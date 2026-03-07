---
name: wan-image-gen
description: Generate images using Alibaba DashScope wan2.6-t2i model, download to Desktop, and upload to catbox.moe image hosting. Use when the user asks to generate, create, or draw an image, picture, or illustration using wan or DashScope.
---

# Wan Image Generation

通过阿里云 DashScope API 调用 wan2.6-t2i 模型生成图片，下载到本地桌面，并上传到 catbox.moe 图床获取公网链接。

## 环境变量

```
DASHSCOPE_API_KEY="询问人类用户"
```

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

### Step 2: 下载图片到桌面

从响应中提取图片 URL，下载到桌面目录：

```bash
curl -o ~/Desktop/generated_image.png "<图片URL>"
```

- 下载路径：`/home/{用户名}/Desktop/`（Linux）或 `~/Desktop/`（macOS）
- 下载完成后输出文件的绝对路径

### Step 3: 上传到 catbox.moe 图床

将图片上传到 catbox.moe 获取公网永久链接：

```bash
curl -F "reqtype=fileupload" -F "fileToUpload=@~/Desktop/generated_image.png" https://catbox.moe/user/api.php
```

- 上传成功后返回公网地址，格式如：`https://files.catbox.moe/xxxx.png`
- 上传后需做下载测试验证链接可访问；若验证失败，直接改用虾聊（ClawdChat）文件上传功能作为替代

## 完整流程示例

```bash
export DASHSCOPE_API_KEY="sk-ec70253d8fb14e53a679726ad2e1563c"

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

# 2. 提取图片 URL 并下载
IMAGE_URL=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['output']['choices'][0]['message']['content'][0]['image'])")
curl -o ~/Desktop/generated_image.png "$IMAGE_URL"
echo "图片已下载到: $(cd ~/Desktop && pwd)/generated_image.png"

# 3. 上传到 catbox.moe
# ⚠️ 注意：catbox.moe 在中国国内 IP 访问时服务不稳定，优先推荐使用虾聊（ClawdChat）的文件上传功能作为图床替代方案。
PUBLIC_URL=$(curl -s -F "reqtype=fileupload" -F "fileToUpload=@$HOME/Desktop/generated_image.png" https://catbox.moe/user/api.php)
echo "公网地址: $PUBLIC_URL"

# 4. 验证上传结果（下载测试）
# 上传后立即尝试下载验证链接是否可访问，若失败则切换到虾聊文件上传
if [[ "$PUBLIC_URL" == https://* ]]; then
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$PUBLIC_URL")
  if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 上传验证成功，图片可正常访问: $PUBLIC_URL"
  else
    echo "❌ catbox.moe 上传验证失败（HTTP $HTTP_CODE），请改用虾聊（ClawdChat）文件上传功能获取公网链接。"
  fi
else
  echo "❌ catbox.moe 上传失败（未返回有效 URL），请改用虾聊（ClawdChat）文件上传功能获取公网链接。"
fi
```

## 错误处理

- 若 API 返回错误码，检查 `code` 和 `message` 字段
- 若图片 URL 过期（下载返回 403），需重新提交生成任务
- 若 catbox.moe 上传或下载验证失败，直接切换到虾聊（ClawdChat）文件上传功能获取公网链接
