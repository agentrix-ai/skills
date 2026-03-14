---
name: seedream
description: 通过火山引擎方舟 API 调用豆包 Seedream 系列模型生成高清图片（2K/3K/4K），支持文生图、图生图、多图融合、组图生成、联网搜索生图，下载到桌面并上传虾聊图床。当用户要求生成图片、AI绘图、用 Seedream/豆包/火山引擎 画图时使用。
---

# Seedream 图片生成

通过火山引擎方舟 API 调用豆包 Seedream 系列模型，生成高清图片，下载到本地桌面，并上传到虾聊（ClawdChat）图床获取公网永久链接。

## 环境变量

```
ARK_API_KEY="询问人类用户"
```

如果环境变量未设置，尝试从工作目录的 `.env` 文件读取。

## 凭证加载

上传图片前，先加载虾聊凭证（取第一个 `api_key`）：

- 主路径：`skills/clawdchat/credentials.json`
- 兼容路径：`~/.clawdchat/credentials.json`

## 可用模型

| 别名 | 模型 ID | 说明 |
|------|---------|------|
| seedream-5 | `doubao-seedream-5-0-260128` | **默认推荐**，最新旗舰，支持联网搜索 |
| seedream-4.5 | `doubao-seedream-4-5-251128` | 高质量，稳定 |
| seedream-4 | `doubao-seedream-4-0-250828` | 经济实惠 |

默认使用 `seedream-5`（doubao-seedream-5-0-260128）。

## API 端点

```
POST https://ark.cn-beijing.volces.com/api/v3/images/generations
Authorization: Bearer $ARK_API_KEY
Content-Type: application/json
```

## 支持的尺寸

**方式 1：分辨率关键词**（推荐，模型根据 prompt 自动判断宽高比）

| 关键词 | 说明 | 支持模型 |
|--------|------|----------|
| `2K` | 约 2048×2048 | 全部 |
| `3K` | 约 3072×3072 | 仅 5.0 lite |
| `1K` | 约 1024×1024 | 仅 4.0 |
| `4K` | 约 4096×4096 | 4.0、4.5 |

**方式 2：精确像素值**（如 `2048x2048`、`2848x1600`）

常用 2K 推荐组合：

| 宽高比 | 尺寸 |
|--------|------|
| 1:1 | 2048×2048 |
| 4:3 | 2304×1728 |
| 3:2 | 2496×1664 |
| 16:9 | 2848×1600 |
| 9:16 | 1600×2848 |
| 21:9 | 3136×1344 |

## 工作流程

### Step 1: 调用方舟 API 生成图片

**文生图（默认）：**

```bash
RESPONSE=$(curl -s https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-5-0-260128",
    "prompt": "<用户提示词>",
    "size": "2K",
    "output_format": "png",
    "response_format": "url",
    "watermark": false
  }')
```

**指定精确尺寸（如 16:9 横幅）：**

```bash
RESPONSE=$(curl -s https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-5-0-260128",
    "prompt": "<用户提示词>",
    "size": "2848x1600",
    "output_format": "png",
    "response_format": "url",
    "watermark": false
  }')
```

**图生图（单图编辑）：**

参考图支持 URL 或 Base64 编码（带 `data:image/jpeg;base64,...` 前缀）。

```bash
RESPONSE=$(curl -s https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-5-0-260128",
    "prompt": "<编辑指令，如：把背景换成海滩>",
    "image": "https://example.com/reference.png",
    "size": "2K",
    "output_format": "png",
    "response_format": "url",
    "watermark": false
  }')
```

本地图片需先编码为 Base64：

```bash
IMG_B64=$(base64 < input.jpg | tr -d '\n')
```

然后 `"image": "data:image/jpeg;base64,'"$IMG_B64"'"`。

**多图融合（最多 10 张）：**

```bash
RESPONSE=$(curl -s https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-5-0-260128",
    "prompt": "将图1的人物穿上图2的服装",
    "image": ["https://example.com/person.png", "https://example.com/outfit.png"],
    "size": "2K",
    "output_format": "png",
    "response_format": "url",
    "watermark": false
  }')
```

**组图生成（多张关联图）：**

```bash
RESPONSE=$(curl -s https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-5-0-260128",
    "prompt": "生成一组4张连贯插画，展现四季庭院变迁",
    "size": "2K",
    "sequential_image_generation": "auto",
    "sequential_image_generation_options": {"max_images": 4},
    "output_format": "png",
    "response_format": "url",
    "watermark": false
  }')
```

**联网搜索生图（仅 5.0 lite）：**

```bash
RESPONSE=$(curl -s https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-5-0-260128",
    "prompt": "制作一张上海未来5日天气预报图，扁平化插画风格",
    "size": "2048x2048",
    "tools": [{"type": "web_search"}],
    "output_format": "png",
    "response_format": "url",
    "watermark": false
  }')
```

### Step 2: 解析响应并下载图片到桌面

响应格式为标准 JSON，`data` 数组中每项包含 `url`（图片下载链接）：

```bash
echo "$RESPONSE" > /tmp/seedream_resp.json

python3 -c "
import json, urllib.request, sys, os

resp = json.load(open('/tmp/seedream_resp.json'))
if 'error' in resp:
    print(f'API 错误: {resp[\"error\"]}')
    sys.exit(1)

data = resp.get('data', [])
if not data:
    print('未返回图片数据')
    sys.exit(1)

saved = 0
for i, item in enumerate(data):
    url = item.get('url', '')
    b64 = item.get('b64_json', '')
    suffix = '' if i == 0 else f'_{i}'
    path = os.path.expanduser(f'~/Desktop/seedream{suffix}.png')

    if url:
        urllib.request.urlretrieve(url, path)
        size_kb = os.path.getsize(path) / 1024
        print(f'图片已保存: {path} ({size_kb:.1f} KB)')
        saved += 1
    elif b64:
        import base64
        with open(path, 'wb') as f:
            f.write(base64.b64decode(b64))
        size_kb = os.path.getsize(path) / 1024
        print(f'图片已保存: {path} ({size_kb:.1f} KB)')
        saved += 1

usage = resp.get('usage', {})
if usage:
    count = usage.get('image_count', saved)
    print(f'生成图片数: {count}')

if saved == 0:
    print('未能保存任何图片')
    sys.exit(1)
"
```

**验证保存成功：** 用 `ls -lh ~/Desktop/seedream*` 检查文件存在且大小 > 0。

### Step 3: 上传到虾聊图床

将图片上传到虾聊（ClawdChat）获取公网永久链接：

```bash
UPLOAD_RESPONSE=$(curl -s -X POST https://clawdchat.cn/api/v1/files/upload \
  -H "Authorization: Bearer $CLAWDCHAT_API_KEY" \
  -F "file=@$HOME/Desktop/seedream.png")

PUBLIC_URL=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['url'])" 2>/dev/null)
if [[ -z "$PUBLIC_URL" || "$PUBLIC_URL" != https://* ]]; then
  echo "虾聊图片上传失败，响应：$UPLOAD_RESPONSE"
  exit 1
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$PUBLIC_URL")
if [ "$HTTP_CODE" = "200" ]; then
  echo "上传成功，公网链接: $PUBLIC_URL"
else
  echo "上传验证失败（HTTP $HTTP_CODE），URL：$PUBLIC_URL"
  exit 1
fi
```

## Prompt 技巧

Seedream 支持中英文 prompt。遵循以下公式：

**文字生图**：`[主体] + [动作/行为] + [场景/环境] + [构图] + [风格/光影]`

**示例**：
> 充满活力的特写编辑肖像，模特眼神犀利，头戴雕塑感帽子，色彩拼接丰富，具有 Vogue 杂志封面的美学风格，中画幅拍摄，工作室灯光强烈。

**关键原则：**
- 中英文均可，建议不超过 300 个汉字或 600 个英文单词
- 用积极描述代替否定（说"空旷的街道"而非"没有车的街道"）
- 可在 prompt 中直接指定宽高比（如"竖版海报""横版壁纸"）
- 用引号包裹要渲染的文字：`写着"新年快乐"的大红灯笼`
- 指定色彩风格：`电影调色`、`胶片质感`、`赛博朋克霓虹`

更多技巧见 [seedream-prompting-guide.md](references/seedream-prompting-guide.md)。

## 核心参数速查

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | string | - | 模型 ID（必填） |
| `prompt` | string | - | 提示词（必填） |
| `image` | string/array | - | 参考图 URL 或 Base64（图生图用） |
| `size` | string | `2048x2048` | `2K`/`3K` 或精确像素如 `2848x1600` |
| `output_format` | string | `png` | `png` 或 `jpeg` |
| `response_format` | string | `url` | `url`（下载链接）或 `b64_json` |
| `watermark` | boolean | `true` | 是否添加"AI生成"水印 |
| `sequential_image_generation` | string | `disabled` | `auto` 开启组图 |
| `tools` | array | - | `[{"type":"web_search"}]` 联网搜索（仅 5.0 lite） |

## 错误处理

| 错误 | 原因 | 解决 |
|------|------|------|
| 401 Unauthorized | API Key 无效或过期 | 检查 `ARK_API_KEY` |
| 429 Too Many Requests | 频率限制 | 等待几秒后重试 |
| Invalid parameter | 参数格式错误 | 检查 size 像素范围、宽高比 |
| 图片下载失败 | URL 过期（通常 24h 有效） | 尽快下载，或改用 `b64_json` |
| 虾聊上传失败 | API Key 无效 | 检查 `CLAWDCHAT_API_KEY` |
