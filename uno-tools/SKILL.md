---
name: uno
description: "Call 1300+ tools (from 134+ MCP Servers) via curl — zero install. Tool-level semantic search returns full inputSchema in one step for immediate invocation. Covers: Search, Dev, Docs, Finance, Maps, Travel, AI Media, Social, Office, Enterprise, and more. Use this skill whenever the user wants to call any external tool, API, or service — even if they just say search the web, check the weather, query GitHub, look up stocks, send an email, generate an image, or run a script."
homepage: https://mcpmarket.cn
source: https://github.com/xray918/uno-mcp-cli
license: MIT
metadata: {"emoji":"🔧","category":"tools"}
---

# Uno MCP Tools

Call MCPMarket REST APIs directly via `curl` to search and invoke 1300+ tools from 134+ MCP Servers. No package installation required.

## Prerequisites

- `curl` (pre-installed on all systems)

## Authentication

```bash
# 1. Request a device code
curl -s -X POST https://mcpmarket.cn/oauth/device/code \
  -d "client_id=skill-agent&scope=mcp:*"
```

**Always copy the `verification_uri` and `user_code` from terminal output verbatim to display to the user — never construct or modify the URL yourself.**

```bash
# 2. Poll for token after user authorizes (retry every 5s until access_token is returned)
curl -s -X POST https://mcpmarket.cn/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code=DEVICE_CODE&client_id=skill-agent"

# 3. Store the token securely
mkdir -p ~/.uno && chmod 700 ~/.uno
echo "ACCESS_TOKEN_VALUE" > ~/.uno/token && chmod 600 ~/.uno/token
```

Verify login:
```bash
curl -s https://mcpmarket.cn/api/uno/verify-token \
  -H "Authorization: Bearer $(cat ~/.uno/token)"
```

## Two-Step Invocation (Core Flow)

```bash
# Step 1: Search tools — get tool_name and inputSchema
curl -s "https://mcpmarket.cn/api/uno/search-tools?q=weather&mode=hybrid&limit=5" \
  -H "Authorization: Bearer $(cat ~/.uno/token)"

# Step 2: Call the tool
curl -s -X POST https://mcpmarket.cn/api/uno/call-tool \
  -H "Authorization: Bearer $(cat ~/.uno/token)" \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"tonghu-weather.weatherArea","arguments":{"area":"Beijing"}}'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/uno/search-tools` | GET | Search tools (main entry) — returns tools + full inputSchema |
| `/api/uno/search-servers` | GET | Search servers |
| `/api/uno/call-tool` | POST | Call a tool (format: `server_name.tool_name`) |
| `/api/uno/categories` | GET | List all categories with counts |
| `/api/uno/rate-server` | POST | Rate after use — influences search ranking |

All endpoints use base URL `https://mcpmarket.cn` and require an `Authorization: Bearer <token>` header.

## search-tools Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search keywords |
| `category` | string | Browse by category, e.g. `Search`, `Dev`, `Finance`, `Social` |
| `mode` | string | `keyword` (exact) / `semantic` / `hybrid` (recommended) |
| `limit` | int | Number of results, default 5, max 15 |

Returns: `tools[]` (with `tool`, `desc`, `inputSchema`), `uncached` (servers requiring connection first)

**Search keyword tips:** The vector database indexes tool functional descriptions. Search terms should match **tool capabilities**, not specific query intents.
- Good: `weather` — matches weather tool descriptions
- Bad: `Shanghai weather tomorrow` — reads like a query intent, less likely to match tools

## call-tool Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `tool_name` | string | **Required** — format `server_name.tool_name` (from the `tool` field of search-tools) |
| `arguments` | object | **Required** — construct according to inputSchema |

**Response structure:**
```json
{"content": [{"type": "text", "text": "<JSON string>"}], "isError": false}
```
> `content[0].text` is itself a JSON string that needs secondary parsing. On error, `isError` is `true` and the `error` field contains the error message.

**Downstream OAuth:** When calling certain services (e.g. GitHub, Notion) for the first time, the response will be:
```json
{"auth_required": true, "auth_url": "https://...", "state_id": "..."}
```
Open `auth_url` to complete authorization, then **simply retry the call** — the platform links everything server-side automatically.

## Parameter Construction Rules (Must Read)

**Always read inputSchema before calling — never guess parameters.** Checklist:

| Check | Why | Lesson Learned |
|-------|-----|----------------|
| `required` fields | Must provide every one | Missing fields cause errors |
| `minLength: 1` | Cannot pass empty string `""` | Notion search with empty query returns nothing |
| Copy field names from schema verbatim | Don't write from memory | `filter` vs `filters` — one letter causes failure |
| `enum` constraints | Only pass values within the enum | Wrong values cause silent failure |
| `description` | Read when field meaning is unclear | Prevents format errors |

**Standard two-step flow (never skip step 1):**

```bash
# Step 1: search-tools, read inputSchema (mandatory every time)
curl -s "https://mcpmarket.cn/api/uno/search-tools?q=<capability_keyword>&mode=hybrid&limit=5" \
  -H "Authorization: Bearer $(cat ~/.uno/token)"
# → Carefully check required / minLength / field names / enum

# Step 2: Construct correct parameters from schema and call
curl -s -X POST https://mcpmarket.cn/api/uno/call-tool \
  -H "Authorization: Bearer $(cat ~/.uno/token)" \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"<tool>","arguments":{<fill per schema>}}'
```

## Workflow Recommendations

1. **Always search-tools first, read inputSchema before calling** — this is the most important step, never skip it
2. **Search terms should match tool capabilities, not query intents** — `weather` is good, `Shanghai weather tomorrow` is bad
3. **Copy parameter names from schema verbatim** — don't guess; `filters` is not `filter`
4. **No results?** — try English keywords, or switch to `mode=semantic`

## Credential Reference

| Item | Value |
|------|-------|
| Token file | `~/.uno/token` (permissions 0600) |
| API Base URL | `https://mcpmarket.cn` |
| Logout | `rm ~/.uno/token` |
