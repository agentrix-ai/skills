---
name: minimax-tts
description: 使用 MiniMax 语音合成 API（TTS）将文本转语音，支持多音色、语速/音量/音高、情绪、输出格式控制。用户提到“语音合成/TTS/配音/朗读/旁白/角色音色/MiniMax 声音”时必须触发本 skill。
---

# MiniMax 语音合成 Skill

用于把文本快速合成为可下载音频，适合：
- 搞笑段子配音
- 视频旁白
- 角色台词
- 通知播报

## 环境变量

```bash
MINIMAX_VOICE_API_KEY="你的 MiniMax Key"
```

兼容：
- 若未配置 `MINIMAX_VOICE_API_KEY`，可回退 `MINIMAX_API_KEY`
- 可选：`MINIMAX_API_BASE`（默认 `https://api.minimaxi.com/v1`）

## 接口

- Endpoint：`POST https://api.minimaxi.com/v1/t2a_v2`
- 推荐模型：`speech-2.8-hd`

## 工作流程

### Step 1: 明确语音需求

至少确认：
- 文本内容（长度、语种、断句）
- 角色风格（正式/搞笑/温柔/新闻播报）
- 输出格式（mp3/wav）

### Step 2: 选音色 + 参数

常用字段：
- `voice_setting.voice_id`
- `voice_setting.speed`（0.5~2.0）
- `voice_setting.vol`（0.1~10）
- `voice_setting.pitch`（-12~12）
- `voice_setting.emotion`（happy/sad/angry/calm/...）

`audio_setting`：
- `sample_rate`（常见 16000/24000/32000）
- `bitrate`
- `format`（mp3/wav/flac/pcm）
- `channel`（1/2）

### Step 3: 调用接口

```bash
curl -sS -X POST "https://api.minimaxi.com/v1/t2a_v2" \
  -H "Authorization: Bearer $MINIMAX_VOICE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "speech-2.8-hd",
    "text": "各位朋友，今天教大家如何优雅地摸鱼。",
    "stream": false,
    "voice_setting": {
      "voice_id": "cartoon_pig",
      "speed": 1.05,
      "vol": 1.2,
      "pitch": 3,
      "emotion": "happy"
    },
    "audio_setting": {
      "sample_rate": 32000,
      "bitrate": 128000,
      "format": "mp3",
      "channel": 1
    },
    "output_format": "url"
  }'
```

### Step 4: 保存音频

- `output_format=url`：下载 URL 到本地 `*.mp3`
- `output_format=hex`：hex 解码写文件

## 常用中文音色（示例）

- `cartoon_pig`（卡通猪小琪）
- `Chinese (Mandarin)_Humorous_Elder`（搞笑大爷）
- `Chinese (Mandarin)_Cute_Spirit`（憨憨萌兽）
- `female-shaonv`（少女）
- `male-qn-qingse`（青涩青年）
- `Chinese (Mandarin)_News_Anchor`（新闻女声）

详见：`references/voice_catalog_quick.md`

## 质量和合规约束

- 不承诺“精准复刻某位真人声音”。
- 可以描述“某类风格气质”，但避免冒充真人身份。
- 如果用户指定具体真人，改写为“相近风格”并明确说明。

## 输出格式（给用户）

统一格式：

```text
模型: <speech-2.8-hd>
音色: <voice_id>
文本长度: <N 字>
输出文件: <path>
状态: <成功/失败>
```

