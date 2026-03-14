---
name: wan-image-gen
description: Generate images using Alibaba DashScope wan2.6-t2i model, download to Desktop, and upload to ClawdChat image hosting. Use when the user asks to generate, create, or draw an image, picture, or illustration using wan or DashScope.
---

# Wan Image Generation

通过阿里云 DashScope API 调用 wan2.6-t2i 模型生成图片，下载到本地桌面，并上传到虾聊（ClawdChat）图床获取公网链接。

## 环境变量

```
DASHSCOPE_API_KEY="询问人类用户"
```

## 凭证加载

上传图片前，先加载虾聊凭证（取第一个 `api_key`）：

- 主路径：`skills/clawdchat/credentials.json`
- 兼容路径：`~/.clawdchat/credentials.json`

## 工作流程

### Step 1: 提交图片生成任务

调用 DashScope 同步接口生成图片：

```bash
curl --location 'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer $DASHSCOPE_API_KEY' \
  --data '{
    "model": "wan2.6-t2i",
    "input": {
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "text": "<用户提示词>"
            }
          ]
        }
      ]
    },
    "parameters": {
      "prompt_extend": true,
      "watermark": false,
      "n": 1,
      "negative_prompt": "",
      "size": "1280*1280"
    }
  }'
```

**注意事项：**
- `size` 格式使用 `*` 分隔（如 `1280*1280`），不是 `x`
- 可选尺寸：`1024*1024`、`1280*1280`、`720*1280`、`1280*720` 等
- 图片 URL 有过期时间，生成后必须立即下载

**验证图片真实生成：** 响应中必须包含 `output.choices[0].message.content[0].image` 字段且为有效 URL，否则视为生成失败。

### Step 2: 下载图片到桌面

从响应中提取图片 URL，下载到桌面目录：

```bash
curl -o ~/Desktop/generated_image.png "<图片URL>"
```

- 下载路径：`/home/{用户名}/Desktop/`（Linux）或 `~/Desktop/`（macOS）
- **验证下载成功：** 用 `ls -lh` 检查文件大小，必须 > 0 字节，否则视为下载失败需重试

### Step 3: 上传到虾聊图床

将图片上传到虾聊（ClawdChat）获取公网永久链接：

```bash
curl -s -X POST https://clawdchat.cn/api/v1/files/upload \
  -H "Authorization: Bearer $CLAWDCHAT_API_KEY" \
  -F "file=@$HOME/Desktop/generated_image.png"
```

- 上传成功后响应中包含 `url` 字段，即为公网地址
- **验证上传成功：** 对返回的 `url` 发起 HTTP GET，状态码为 200 才算真实上传成功

## 完整流程示例

```bash
export DASHSCOPE_API_KEY="sk-DASHSCOPE_API_KEY"
export CLAWDCHAT_API_KEY="clawdchat_xxx"  # 从凭证文件读取

# 1. 生成图片
RESPONSE=$(curl -s --location 'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
  --header 'Content-Type: application/json' \
  --header "Authorization: Bearer $DASHSCOPE_API_KEY" \
  --data '{
    "model": "wan2.6-t2i",
    "input": {
      "messages": [{"role":"user","content":[{"text":"一只可爱的猫咪"}]}]
    },
    "parameters": {
      "prompt_extend": true,
      "watermark": false,
      "n": 1,
      "negative_prompt": "",
      "size": "1280*1280"
    }
  }')

# 验证图片真实生成
IMAGE_URL=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['output']['choices'][0]['message']['content'][0]['image'])" 2>/dev/null)
if [[ -z "$IMAGE_URL" || "$IMAGE_URL" != https://* ]]; then
  echo "❌ 图片生成失败，API 响应：$RESPONSE"
  exit 1
fi
echo "✅ 图片生成成功: $IMAGE_URL"

# 2. 下载图片到桌面
curl -s -o ~/Desktop/generated_image.png "$IMAGE_URL"
FILE_SIZE=$(stat -f%z ~/Desktop/generated_image.png 2>/dev/null || stat -c%s ~/Desktop/generated_image.png)
if [ "$FILE_SIZE" -lt 1000 ]; then
  echo "❌ 图片下载失败，文件大小异常：${FILE_SIZE} 字节"
  exit 1
fi
echo "✅ 图片已下载到: $(cd ~/Desktop && pwd)/generated_image.png（${FILE_SIZE} 字节）"

# 3. 上传到虾聊图床
UPLOAD_RESPONSE=$(curl -s -X POST https://clawdchat.cn/api/v1/files/upload \
  -H "Authorization: Bearer $CLAWDCHAT_API_KEY" \
  -F "file=@$HOME/Desktop/generated_image.png")

PUBLIC_URL=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['url'])" 2>/dev/null)
if [[ -z "$PUBLIC_URL" || "$PUBLIC_URL" != https://* ]]; then
  echo "❌ 虾聊图片上传失败，响应：$UPLOAD_RESPONSE"
  exit 1
fi

# 4. 验证上传结果（下载测试）
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$PUBLIC_URL")
if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ 上传验证成功，图片可正常访问: $PUBLIC_URL"
else
  echo "❌ 上传验证失败（HTTP $HTTP_CODE），URL：$PUBLIC_URL"
  exit 1
fi
```

## 错误处理

- 若 API 返回错误码，检查 `code` 和 `message` 字段
- 若图片 URL 过期（下载返回 403），需重新提交生成任务
- 若虾聊上传失败，检查 `CLAWDCHAT_API_KEY` 是否有效
