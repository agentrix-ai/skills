---
name: uno
description: "Call 134+ MCP Server tools via bash commands — no native tool_use config required. Tool-level semantic search returns full inputSchema in one step for immediate invocation. Covers: Search (DuckDuckGo/Brave/Exa/Tavily/Jina), Dev (GitHub/Context7/Figma/Sentry/Linear/Deepwiki), Docs (Markitdown/Fetch/Firecrawl/Word/Excel/PPT/Notion/arXiv), Visualization (AntV/ECharts), Finance (A-shares/Yahoo/Alpha Vantage/World Bank), Maps (Baidu/Google/Amap), Travel (Flights/Hotels/Weather/Tracking), AI Media (Image Gen/TTS/Vision), Social (Twitter/Discord/Instagram/LinkedIn/Reddit/HN/ClawdChat), Office (Gmail/Outlook/Calendar/GoogleDoc/Drive/Trello/Teams/Canva), Enterprise (Business Registry/Procurement/Risk Scanner), Sandbox (Python/Bash/Node). Use this skill whenever the user wants to call any external tool, API, or service — even if they just say search the web, check the weather, query GitHub, look up stocks, send an email, generate an image, or run a script."
homepage: https://mcpmarket.cn
metadata: {"emoji":"🔧","category":"tools","gateway":"https://uno.mcpmarket.cn/mcp"}
---

# Uno MCP Tools

Use `uno-cli` to access 134+ MCP Servers aggregated by the Uno gateway. Tool-level semantic search delivers complete `inputSchema` in one step — invoke immediately in the next.

## Installation

```bash
uv tool install uno-cli
```

Verify: `uno-cli --help`. If `uv` is unavailable, use `pip3 install uno-cli`.

## Authentication

```bash
uno-cli login --headless
```

**Always copy the terminal output link and device code verbatim to display to the user — never construct or modify the URL yourself.** Token stored at `~/.uno/tokens.json`, valid for 30 days. Check status: `uno-cli status`

## 5 Gateway Tools

| Tool | Responsibility |
|------|----------------|
| `uno_search_servers` | **Search** (main entry) — returns most relevant tools + full inputSchema |
| `uno_discover_servers` | **Connect** — fetch tool definitions by server_names / trigger OAuth auth |
| `uno_call_tool` | **Execute** — invoke a specific tool (format: `server.tool_name`) |
| `uno_execute_script` | **Sandbox** — run Python/Bash/Node scripts |
| `uno_rate_server` | **Rate** — post-call feedback that influences search ranking |

## Two-Step Invocation (Core Flow)

```bash
# Step 1: Search → get tools + inputSchema directly
uno-cli tools call uno_search_servers '{"query": "weather forecast", "mode": "hybrid"}'

# Step 2: Call (use the `tool` field from search result as server.tool_name)
uno-cli tools call uno_call_tool '{"tool_name": "amap-maps.maps_weather", "arguments": {"city": "Beijing"}}'
```

## uno_search_servers Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | **Required** — search keywords (Chinese/English/natural language) |
| `category` | string | Browse by category, e.g. `Search`, `Dev`, `Finance`, `Social` |
| `mode` | string | `keyword` (exact, fast) / `semantic` / `hybrid` (recommended) |
| `limit` | int | Number of tools returned, default 5, max 15 |

Returns:
- `tools`: most relevant tool list, each with `tool` (server.tool_name), `desc`, `inputSchema`
- `uncached`: OAuth servers requiring auth (if any) — prompts you to call `uno_discover_servers`

## uno_discover_servers Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `server_names` | array | List of server names to fetch full tool definitions for |
| `category` | string | Browse servers by category |

Use cases:
- When `uno_search_servers` returns `uncached` servers requiring OAuth
- When you already know the server name and need full tool definitions

## OAuth Flow (Cold Start — Rare)

```bash
# 1. Search discovers an uncached OAuth server
uno-cli tools call uno_search_servers '{"query": "GitHub PR"}'
# → uncached: [{server: "github", auth_required: true, action: "uno_discover_servers(...)"}]

# 2. Discover triggers authentication
uno-cli tools call uno_discover_servers '{"server_names": ["github"]}'
# → auth_url: "https://mcpmarket.cn/oauth/..." (display to user for click-through)

# 3. After user authorizes, discover again
uno-cli tools call uno_discover_servers '{"server_names": ["github"]}'
# → returns full tools (auto-cached to DB — search finds them directly afterwards)

# 4. Call
uno-cli tools call uno_call_tool '{"tool_name": "github.search_repositories", "arguments": {...}}'
```

## Available Categories

| Category | Count | Representative Servers |
|----------|-------|------------------------|
| Search | 66 | exa-search, Jina, Tavily, brave-search |
| Data | 67 | world-bank, Jina, pageindex-mcp |
| Dev | 45 | github, context7, Deepwiki, Linear |
| Social | 31 | clawdchat-mcp, twitter, Discord, Instagram |
| Creative | 30 | powerpoint, zhipu-vision, nano-banana |
| Enterprise | 28 | enterprise-search, enterprise-risk-scanner |
| Productivity | 14 | Gmail, Google Calendar, Trello, Canva |
| Finance | 14 | eastmoney-stock-china, Alpha Vantage, yahoo-finance |
| E-commerce | 8 | Ecommerce, express-tracking-china |

## Usage Examples

### Search and Call (Most Common)

```bash
# Search
uno-cli tools call uno_search_servers '{"query": "Beijing weather", "mode": "hybrid"}'
# Call (use the tool field from results)
uno-cli tools call uno_call_tool '{"tool_name": "amap-maps.maps_weather", "arguments": {"city": "Beijing"}}'
```

### Browse by Category

```bash
uno-cli tools call uno_search_servers '{"category": "Finance", "limit": 10}'
```

### Run a Script in Sandbox

```bash
uno-cli tools call uno_execute_script '{"language": "python", "script": "print(42 * 2)"}'
```

### Rate a Server After Use

```bash
uno-cli tools call uno_rate_server '{"server_name": "amap-maps", "rating": 4.5, "comment": "fast response"}'
```

### JSON Output with jq

```bash
uno-cli --json tools call uno_call_tool '{"tool_name": "time.get_current_time", "arguments": {"timezone": "UTC"}}' | jq '.content[0].text | fromjson'
```

## Workflow Recommendations

1. **Start with `uno_search_servers`** — get tools + schema in one shot, call in two steps total
2. **Use `hybrid` mode for natural language** — semantic search is more accurate
3. **OAuth servers** — search marks them as `uncached`; follow the prompt to call `discover` for auth
4. **Rate after use** — call `uno_rate_server` to improve search ranking for everyone
5. **Unsure about parameters?** — the `inputSchema` from search is the complete parameter definition

## Credential Reference

| Item | Path |
|------|------|
| Token file | `~/.uno/tokens.json` |
| MCP gateway | `https://uno.mcpmarket.cn/mcp` |
| Login | `uno-cli login --headless` |
| Logout | `uno-cli logout` |

## Changelog

### v1.0.0

- Initial release integrating 134+ MCP Server tools via a single aggregation gateway
- 5 gateway commands: search, discover, call, script sandbox, rate
- Tool-level semantic / hybrid / keyword search returning full inputSchema
- Streamlined OAuth flow: auto-detects uncached servers, dedicated discover call triggers auth and caches results
- Comprehensive CLI examples and workflow recommendations for efficient multi-source tool invocation
