---
name: ai-picture-book
description: 通过百度千帆 API 生成 AI 绘本视频（静态/动态），输入故事文本，异步生成绘本视频并返回下载链接。当用户要求生成绘本、做绘本视频、AI 绘本、百度绘本时使用。
---

# AI 绘本生成

通过百度千帆平台的 AI 绘本官方工具，将故事文本异步生成为绘本视频（静态图片书或动态动画），返回 BOS/CDN 视频下载链接。

## 环境变量

```
BAIDU_API_KEY="询问人类用户"
```

如果环境变量未设置，请向用户索取百度千帆 API Key。

获取方式：登录 [百度千帆控制台](https://console.bce.baidu.com/iam/#/iam/accesslist)，创建 Access Key，格式为 `bce-v3/ALTAK-xxx/xxx`。

## API 端点

```
基础地址: https://qianfan.baidubce.com
Authorization: Bearer $BAIDU_API_KEY
Content-Type: application/json
X-Appbuilder-From: openclaw
```

所有请求都需要携带以上三个 Header。

## 绘本类型

| 类型 | method 值 | 说明 |
|------|-----------|------|
| 静态绘本 | `9` | 静态图片拼接成视频，生成速度快 |
| 动态绘本 | `10` | 带动画效果的绘本视频，画面更生动 |

**默认推荐动态绘本**（method=10），效果更好。如用户未指定，使用动态绘本。

## 任务状态码

| 状态码 | 含义 | 操作 |
|--------|------|------|
| 0 | 排队中 | 继续轮询 |
| 1 | 处理中 | 继续轮询 |
| 3 | 渲染中 | 继续轮询 |
| 2 | **已完成** | 提取视频链接 |
| 其他 | 失败 | 输出错误信息 |

## 工作流程

### Step 1: 创建绘本任务

提交故事文本 + 绘本类型，获取异步任务 ID：

```bash
RESPONSE=$(curl -s -X POST https://qianfan.baidubce.com/v2/tools/ai_picture_book/task_create \
  -H "Authorization: Bearer $BAIDU_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Appbuilder-From: openclaw" \
  -d '{
    "method": 10,
    "input_type": "1",
    "input_content": "<故事文本>"
  }')
```

**参数说明：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `method` | int | 是 | `9` 静态绘本，`10` 动态绘本 |
| `input_type` | string | 是 | 固定传 `"1"`（纯文本输入） |
| `input_content` | string | 是 | 故事文本内容 |

**响应示例：**

```json
{
  "task_id": "1c6a223e-4934-4491-aa07-1ef26fd059a9"
}
```

### Step 2: 解析任务 ID

```bash
TASK_ID=$(echo "$RESPONSE" | python3 -c "
import sys, json
resp = json.load(sys.stdin)
if 'code' in resp:
    print(f'API 错误: {resp.get(\"detail\", resp)}', file=sys.stderr)
    sys.exit(1)
if 'errno' in resp and resp['errno'] != 0:
    print(f'API 错误: {resp.get(\"errmsg\", resp)}', file=sys.stderr)
    sys.exit(1)
print(resp['data']['task_id'])
")

echo "任务已创建: $TASK_ID"
```

### Step 3: 轮询任务状态直到完成

绘本生成通常需要 1-3 分钟。每 5 秒查询一次，最多轮询 60 次（5 分钟）：

```bash
for i in $(seq 1 60); do
  POLL=$(curl -s -X POST https://qianfan.baidubce.com/v2/tools/ai_picture_book/query \
    -H "Authorization: Bearer $BAIDU_API_KEY" \
    -H "Content-Type: application/json" \
    -H "X-Appbuilder-From: openclaw" \
    -d "{\"task_ids\": [\"$TASK_ID\"]}")

  STATUS=$(echo "$POLL" | python3 -c "
import sys, json
resp = json.load(sys.stdin)
data = resp.get('data', [])
if not data:
    print('error')
    sys.exit(0)
task = data[0]
status = task.get('status')
print(status)
if status == 2:
    result = task.get('result', {})
    bos = result.get('video_bos_url', '')
    cdn = result.get('video_cdn_url', '')
    print(bos, file=sys.stderr)
    print(cdn, file=sys.stderr)
")

  if [ "$STATUS" = "2" ]; then
    echo "✓ 绘本生成完成！"
    echo "$POLL" | python3 -c "
import sys, json
resp = json.load(sys.stdin)
task = resp['data'][0]
result = task.get('result', {})
bos = result.get('video_bos_url', '')
cdn = result.get('video_cdn_url', '')
if bos: print(f'BOS 下载链接: {bos}')
if cdn: print(f'CDN 下载链接: {cdn}')
if not bos and not cdn: print(json.dumps(result, ensure_ascii=False, indent=2))
"
    break
  elif [ "$STATUS" = "error" ]; then
    echo "✗ 查询失败"
    echo "$POLL"
    break
  else
    echo "[$i/60] 生成中... (status=$STATUS)"
    sleep 5
  fi
done
```

### Step 4: 下载视频到桌面（可选）

```bash
curl -L -o ~/Desktop/picture_book.mp4 "<BOS 下载链接>"
ls -lh ~/Desktop/picture_book.mp4
```

## 完整一键示例

以下是从创建到获取结果的完整脚本，可直接复制运行：

```bash
python3 -c "
import os, sys, json, time, requests

API_KEY = os.getenv('BAIDU_API_KEY')
if not API_KEY:
    print('错误: 请设置 BAIDU_API_KEY 环境变量')
    sys.exit(1)

BASE = 'https://qianfan.baidubce.com'
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json',
    'X-Appbuilder-From': 'openclaw'
}

STORY = '''<在此粘贴故事文本>'''
METHOD = 10  # 9=静态, 10=动态

# 创建任务
resp = requests.post(f'{BASE}/v2/tools/ai_picture_book/task_create',
    headers=HEADERS,
    json={'method': METHOD, 'input_type': '1', 'input_content': STORY})
resp.raise_for_status()
data = resp.json()
if 'errno' in data and data['errno'] != 0:
    print(f'创建失败: {data}')
    sys.exit(1)
task_id = data['data']['task_id']
print(f'任务已创建: {task_id}')

# 轮询
for i in range(1, 61):
    time.sleep(5)
    resp = requests.post(f'{BASE}/v2/tools/ai_picture_book/query',
        headers=HEADERS,
        json={'task_ids': [task_id]}, timeout=15)
    result = resp.json()
    tasks = result.get('data', [])
    if not tasks:
        print(f'[{i}/60] 无数据...')
        continue
    status = tasks[0].get('status')
    if status == 2:
        video = tasks[0].get('result', {})
        print('\\n' + '='*50)
        print('✓ 绘本生成完成！')
        print('='*50)
        bos = video.get('video_bos_url', '')
        cdn = video.get('video_cdn_url', '')
        if bos: print(f'BOS: {bos}')
        if cdn: print(f'CDN: {cdn}')
        sys.exit(0)
    print(f'[{i}/60] 生成中... (status={status})')

print('\\n超时，任务可能仍在运行，请稍后用 task_id 手动查询')
"
```

## 故事文本技巧

绘本 AI 会自动将故事拆分为多个场景并配图，以下技巧可提升生成质量：

**推荐结构：**
- 故事长度 200-500 字效果最佳
- 包含 3-6 个场景切换（不同地点/时间/情节转折）
- 角色名称保持一致，便于 AI 维持角色形象
- 加入视觉描写（颜色、天气、表情）帮助 AI 生成更精准的画面

**示例故事：**
> 在月光森林里，住着一只怕黑的小刺猬，名叫阿团。每到夜晚，它都把自己缩成一团，不敢出门。一天，森林停电了，萤火虫奶奶邀请阿团一起去点亮夜路。阿团颤抖着跟上队伍，发现每帮助一位迷路的小动物，自己背上的一根小刺就会发出微光。它先送迷路的小兔回家，再帮小松鼠找到丢失的橡果，还陪小鹿跨过小溪。最后，阿团的刺像星星一样亮，整片森林被温柔照亮。

**注意：**
- 中文故事效果优于英文
- 避免过于抽象的描述，具体场景更易生成高质量画面
- 动态绘本（method=10）对动作描写更敏感，适当加入角色动作

## 核心参数速查

### 创建任务 `POST /v2/tools/ai_picture_book/task_create`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `method` | int | 是 | - | `9` 静态绘本，`10` 动态绘本 |
| `input_type` | string | 是 | - | 固定 `"1"`（纯文本） |
| `input_content` | string | 是 | - | 故事文本 |

### 查询任务 `POST /v2/tools/ai_picture_book/query`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_ids` | array | 是 | 任务 ID 数组，支持批量查询 |

### 响应字段

| 字段 | 说明 |
|------|------|
| `status` | 任务状态码（见上方状态码表） |
| `result.video_bos_url` | BOS 视频下载链接（永久有效） |
| `result.video_cdn_url` | CDN 加速链接（带鉴权，有时效） |

## 错误处理

| 错误 | 原因 | 解决 |
|------|------|------|
| 401 Unauthorized | API Key 无效或过期 | 检查 `BAIDU_API_KEY` 格式是否为 `bce-v3/ALTAK-xxx/xxx` |
| `errno != 0` | 请求参数错误 | 检查 `errmsg` 字段获取具体原因 |
| 轮询超时 | 任务耗时过长 | 动态绘本通常 2-3 分钟，可增大轮询次数 |
| `status` 非 0/1/2/3 | 生成失败 | 检查故事文本是否过短或含违规内容 |
| 无 `video_bos_url` | 任务未完成即查询 | 确认 `status=2` 后再提取链接 |
| `code` 字段存在 | 服务端错误 | 查看 `detail` 字段，通常为鉴权或频率问题 |
