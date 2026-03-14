---
name: nano-banana
description: 通过 OpenRouter API 调用 Google Nano Banana 系列模型生成和编辑图片，下载到桌面，并上传到虾聊（ClawdChat）图床获取公网链接。当用户要求生成、创建、绘制图片，或要求用 Nano Banana / Gemini 画图、修图、图片编辑时使用此 skill。即使用户只说"画一张图"、"生成图片"、"做个海报"、"P一下这张图"，也应当使用。
---

# Nano Banana 图片生成与编辑

通过 OpenRouter API 调用 Google Nano Banana 系列模型，生成或编辑图片，下载到本地桌面，并上传到虾聊（ClawdChat）图床获取公网永久链接。

## 环境变量

```
OPENROUTER_API_KEY="询问人类用户"
```

如果环境变量未设置，尝试从工作目录的 `.env` 文件读取。

## 凭证加载

上传图片前，先加载虾聊凭证（取第一个 `api_key`）：

- 主路径：`skills/clawdchat/credentials.json`
- 兼容路径：`~/.clawdchat/credentials.json`

## 可用模型

| 别名 | 模型 ID | 说明 |
|------|---------|------|
| nano-banana | `google/gemini-2.5-flash-image` | 原版，性价比高 |
| nano-banana-2 | `google/gemini-3.1-flash-image-preview` | **默认推荐**，Pro 级画质 + Flash 速度 |
| nano-banana-pro | `google/gemini-3-pro-image-preview` | 最高质量，适合精细创作 |

默认使用 `nano-banana-2`。

## 支持的宽高比

`1:1`、`3:2`、`2:3`、`3:4`、`4:3`、`4:5`、`5:4`、`9:16`、`16:9`、`21:9`、`1:4`、`4:1`、`1:8`、`8:1`

通过 `image_config.aspect_ratio` 参数控制，不指定时模型自动选择。

## 工作流程

### Step 1: 调用 OpenRouter API 生成图片

**纯文字生图：**

```bash
RESPONSE=$(curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "HTTP-Referer: https://github.com/xray918/banana-skill" \
  -H "X-Title: Banana Skill" \
  -d '{
    "model": "google/gemini-3.1-flash-image-preview",
    "messages": [
      {
        "role": "user",
        "content": "<用户提示词>"
      }
    ],
    "modalities": ["image", "text"],
    "stream": false
  }')
```

**指定宽高比：**

在请求体中增加 `image_config` 字段：

```json
{
  "model": "google/gemini-3.1-flash-image-preview",
  "messages": [...],
  "modalities": ["image", "text"],
  "stream": false,
  "image_config": {
    "aspect_ratio": "16:9"
  }
}
```

**带参考图编辑（图生图）：**

先将本地图片编码为 base64 data URL，然后在 messages 中传入：

```bash
IMG_B64=$(base64 < input.jpg | tr -d '\n')
MIME="image/jpeg"

RESPONSE=$(curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "HTTP-Referer: https://github.com/xray918/banana-skill" \
  -H "X-Title: Banana Skill" \
  -d '{
    "model": "google/gemini-3.1-flash-image-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "image_url": {"url": "data:'"$MIME"';base64,'"$IMG_B64"'"}
          },
          {
            "type": "text",
            "text": "<编辑指令，如：把背景换成沙滩，保持人物不变>"
          }
        ]
      }
    ],
    "modalities": ["image", "text"],
    "stream": false
  }')
```

**注意事项：**
- `modalities` 必须包含 `"image"`，否则不会返回图片
- `stream` 必须为 `false`，流式响应无法正确返回 base64 图片
- 响应中 `message.content` 通常为 `null`，图片在 **`message.images`** 数组中
- 每张图片为 `{"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}`

### Step 2: 提取并保存图片到桌面

响应体较大（含 base64 图片数据），先存为临时文件再用 Python 解析，避免 shell 转义问题：

```bash
echo "$RESPONSE" > /tmp/banana_resp.json

python3 -c "
import json, base64, sys, os
resp = json.load(open('/tmp/banana_resp.json'))
if 'error' in resp:
    print(f'❌ API 错误: {resp[\"error\"]}')
    sys.exit(1)
msg = resp['choices'][0]['message']

# 提取文本（content 字段）
content = msg.get('content')
if isinstance(content, str) and content:
    print(f'模型说: {content[:300]}')
elif isinstance(content, list):
    for p in content:
        if isinstance(p, dict) and p.get('type') == 'text':
            print(f'模型说: {p.get(\"text\", \"\")[:300]}')

# 提取图片（images 字段，不是 content）
images = msg.get('images', [])
saved = 0
for i, img in enumerate(images):
    url = img.get('image_url', {}).get('url', '')
    if url.startswith('data:'):
        header, b64 = url.split(',', 1)
        ext = 'png' if 'png' in header else 'jpg' if 'jpeg' in header else 'webp' if 'webp' in header else 'png'
        suffix = '' if saved == 0 else f'_{saved}'
        path = os.path.expanduser(f'~/Desktop/banana{suffix}.{ext}')
        data = base64.b64decode(b64)
        with open(path, 'wb') as f:
            f.write(data)
        print(f'✅ 图片已保存: {path} ({len(data)/1024:.1f} KB)')
        saved += 1

usage = resp.get('usage', {})
if usage:
    print(f'Tokens: input={usage.get(\"prompt_tokens\",\"?\")}, output={usage.get(\"completion_tokens\",\"?\")}, cost=\${usage.get(\"cost\",0):.4f}')

if saved == 0:
    print('❌ 未在响应中找到图片，检查 modalities 是否包含 image')
    sys.exit(1)
"
```

**验证保存成功：** 用 `ls -lh ~/Desktop/banana.*` 检查文件存在且大小 > 0。

### Step 3: 上传到虾聊图床

将图片上传到虾聊（ClawdChat）获取公网永久链接：

```bash
UPLOAD_RESPONSE=$(curl -s -X POST https://clawdchat.cn/api/v1/files/upload \
  -H "Authorization: Bearer $CLAWDCHAT_API_KEY" \
  -F "file=@$HOME/Desktop/banana.png")

PUBLIC_URL=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['url'])" 2>/dev/null)
if [[ -z "$PUBLIC_URL" || "$PUBLIC_URL" != https://* ]]; then
  echo "❌ 虾聊图片上传失败，响应：$UPLOAD_RESPONSE"
  exit 1
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$PUBLIC_URL")
if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ 上传成功，公网链接: $PUBLIC_URL"
else
  echo "❌ 上传验证失败（HTTP $HTTP_CODE），URL：$PUBLIC_URL"
  exit 1
fi
```

## Prompt 技巧

生图质量取决于 prompt 质量。遵循以下公式：

**文字生图**：`[主体] + [动作] + [场景] + [构图] + [风格]`

**示例**：
> A watercolor painting of a cozy Tokyo ramen shop at night, warm lantern light spilling onto a wet cobblestone street, overhead view, Studio Ghibli style with soft edges and rich warm tones.

**关键原则：**
- 用积极描述代替否定（说"空旷的街道"而非"没有车的街道"）
- 用摄影术语控制镜头：`low angle`、`aerial view`、`macro lens`
- 用引号包裹要渲染的文字：`a poster with "HELLO" in bold Impact font`
- 指定色彩风格：`cinematic color grading`、`1980s film grain`
- 指定材质细节：`brushed aluminum`、`hand-knitted wool`

更多技巧见 [prompting-guide.md](references/prompting-guide.md)。

## 错误处理

| 错误 | 原因 | 解决 |
|------|------|------|
| 401 Unauthorized | API Key 无效或过期 | 检查 `OPENROUTER_API_KEY` |
| 429 Too Many Requests | 频率限制 | 等待几秒后重试 |
| 模型仅返回文本 | prompt 不够"图像化" | 让 prompt 更具视觉描述性 |
| base64 解码失败 | 响应格式异常 | 用 `--json` 查看原始响应排查 |
| 虾聊上传失败 | API Key 无效 | 检查 `CLAWDCHAT_API_KEY` |
