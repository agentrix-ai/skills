---
name: doubao-tts
description: Text-to-Speech synthesis using Volcengine Doubao (豆包) Speech API with 2.0 voice instruction support
metadata: { "openclaw": { "emoji": "🗣️", "requires": { "bins": ["python3"], "env":["VOLCENGINE_TTS_APPID","VOLCENGINE_TTS_TOKEN"]},"primaryEnv":"VOLCENGINE_TTS_TOKEN" } }
---

# Doubao TTS (豆包语音合成)

Synthesize natural speech from text using Volcengine Doubao Speech API. Supports 2.0 big-model voices with voice instructions, emotion control, context reference, and voice tags.

## Workflow

1. **Prepare text** — plain text, with optional voice instructions `[#指令]` or context `[#上文]`
2. **Run script** — call `tts_synthesize.py` with text + voice + audio params
3. **Get audio** — output file saved to specified path (mp3/wav/pcm/ogg_opus)

## Quick Start

```bash
# Basic synthesis (default: 可爱女生 voice, mp3)
python3 scripts/tts_synthesize.py --text "你好，今天天气真不错！" --output hello.mp3

# With voice instruction (2.0 feature)
python3 scripts/tts_synthesize.py --text "[#用开心兴奋的语气说]太棒了！我们成功了！" --output happy.mp3

# Male voice, slower speed
python3 scripts/tts_synthesize.py --text "这是一段测试语音。" --voice zh_male_vv_young_bigtts --speed 0.8 --output test.mp3
```

## API

### Synthesize

**Endpoint**: `POST https://openspeech.bytedance.com/api/v1/tts`

**Auth**: `Authorization: Bearer;{VOLCENGINE_TTS_TOKEN}`

**Script**: `scripts/tts_synthesize.py`

**Parameters**:

| Param | Flag | Required | Default | Description |
|-------|------|----------|---------|-------------|
| text | `--text` | **Yes** | — | Text to synthesize (max 1024 bytes UTF-8). Supports voice instructions. |
| voice | `--voice` | No | `zh_female_vv_uranus_bigtts` | Voice type ID or built-in name |
| output | `--output` | No | `output.mp3` | Output audio file path |
| encoding | `--encoding` | No | `mp3` | Audio format: `mp3`, `wav`, `pcm`, `ogg_opus` |
| speed | `--speed` | No | `1.0` | Speech rate (0.2–3.0) |
| volume | `--volume` | No | `1.0` | Volume (0.1–3.0) |
| pitch | `--pitch` | No | `1.0` | Pitch (0.1–3.0) |
| emotion | `--emotion` | No | — | Emotion style (e.g. `happy`, `sad`, `angry`) |
| language | `--language` | No | — | Language hint: `zh-cn`, `en`, `ja`, `crosslingual` |
| cluster | `--cluster` | No | `volcano_tts` | API cluster (from env `VOLCENGINE_TTS_CLUSTER`) |

**Examples**:
```bash
# Default voice
python3 scripts/tts_synthesize.py --text "你好世界"

# Specify voice + format + output
python3 scripts/tts_synthesize.py --text "Hello World" --voice zh_female_vv_uranus_bigtts --encoding wav --output hello.wav

# Adjust speed and volume
python3 scripts/tts_synthesize.py --text "慢速大声播报" --speed 0.7 --volume 1.5

# With emotion (for voices that support it)
python3 scripts/tts_synthesize.py --text "这太让人难过了" --emotion sad

# English-only mode
python3 scripts/tts_synthesize.py --text "This is an English test." --language en
```

**Response**: Audio binary saved to `--output` path. Script prints duration and file size.

**Success output**:
```
合成成功 | 音频时长: 3200ms | reqid: uuid-here
音频已保存: output.mp3 (65,280 bytes)
```

## Voice Types

### 2.0 Big-Model Voices (Recommended)

These voices support voice instructions, context reference, and voice tags.

| Name | voice_type | Gender | Features |
|------|-----------|--------|----------|
| 可爱女生 | `zh_female_vv_uranus_bigtts` | Female | Voice instructions, tags |
| 调皮公主 | `zh_female_vv_princess_bigtts` | Female | Voice instructions, tags |
| 爽朗少年 | `zh_male_vv_young_bigtts` | Male | Voice instructions, tags |
| 天才同桌 | `zh_male_vv_genius_bigtts` | Male | Voice instructions, tags |

### Standard Streaming Voices

| Name | voice_type | Gender |
|------|-----------|--------|
| 灿灿 | `BV700_streaming` | Female |
| 梓梓 | `BV406_streaming` | Female |
| 通用女声 | `BV001_streaming` | Female |
| 通用男声 | `BV002_streaming` | Male |
| 电影解说小帅 | `BV411_streaming` | Male |
| 电影解说小美 | `BV412_streaming` | Female |
| 阳光男声 | `BV123_streaming` | Male |
| 知性姐姐 | `BV034_streaming` | Female |

Full list: https://www.volcengine.com/docs/6561/1257544

**Note**: Standard voices (BV*) require `volc.tts.default` resource. Big-model voices (*_bigtts) require `volc.megatts.default` resource. Use the cluster and voices that match your account's activated service.

## 2.0 Features

### Voice Instructions (语音指令)

Prepend `[#instruction]` to control emotion, dialect, tone, speed, pitch:

```bash
# Angry tone
python3 scripts/tts_synthesize.py --text "[#你得跟我互怼！用吵架的语气]你也不是什么好东西！"

# Whisper / ASMR
python3 scripts/tts_synthesize.py --text "[#用asmr悄悄话的语气]每次听到你的声音，我都觉得心里暖暖的。"

# Complex emotion
python3 scripts/tts_synthesize.py --text "[#用低沉沙哑、带着沧桑与绝望的语气说]我多想再回到从前啊。"

# Dialect
python3 scripts/tts_synthesize.py --text "[#用四川话说]巴适得板！"
```

### Context Reference (引用上文)

Provide preceding context that the model understands but doesn't synthesize:

```bash
# Q&A context — model understands the question and speaks the answer naturally
python3 scripts/tts_synthesize.py --text "[#你怎么评价北京？]北京嘛，因为我来这是第二次了。"

# Emotional context
python3 scripts/tts_synthesize.py --text "[#是你吗？好像没怎么变啊？]你头发长了，十年了，你还好吗？"
```

### Voice Tags (语音标签)

For 2.0 voices (可爱女生, 调皮公主, 爽朗少年, 天才同桌), add expression/action/mood tags inline:

```bash
python3 scripts/tts_synthesize.py --text "【旁白，语调惊恐】他的手触碰到对方身体时，却感觉一阵冰冷僵硬。"

python3 scripts/tts_synthesize.py --text "【怒目圆睁，大声怒吼】放肆！我是龙族的女王！"
```

## Audio Parameters

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| `encoding` | `mp3`, `wav`, `pcm`, `ogg_opus` | `mp3` | `wav` does not support streaming |
| `speed_ratio` | 0.2 – 3.0 | 1.0 | Speech rate |
| `volume_ratio` | 0.1 – 3.0 | 1.0 | Volume level |
| `pitch_ratio` | 0.1 – 3.0 | 1.0 | Pitch (standard voices only; big-model voices don't support pitch) |
| `rate` | 8000, 16000, 24000 | 24000 | Sample rate in Hz |
| `emotion` | `happy`, `sad`, `angry`, `fear`, `hate`, `surprise`, `neutral` | — | Only for voices with multi-emotion support |
| `language` | `zh-cn`, `en`, `ja`, `crosslingual`, etc. | auto | Explicit language hint |
| `loudness_ratio` | 0.5 – 2.0 | 1.0 | Alternative volume control for big-model voices |

## Error Handling

| Code | Description | Action |
|------|-------------|--------|
| 3000 | Success | Normal |
| 3001 | Invalid request | Check parameters (voice_type, cluster, auth) |
| 3003 | Concurrency limit | Retry later |
| 3005 | Server busy | Retry later |
| 3010 | Text too long | Reduce to ≤1024 bytes UTF-8 |
| 3011 | Invalid text | Check text content (not empty, matches language) |
| 3030 | Timeout | Retry or shorten text |

Common error messages:
- `"requested resource not granted"` → Voice not activated in console. Buy/order the voice pack (some are free at ¥0).
- `"authenticate request: load grant: requested grant not found"` → Check AppID + Token.
- `"illegal input text!"` → Text is empty or contains only punctuation/emoji.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VOLCENGINE_TTS_APPID` | **Yes** | Application ID from Volcengine console |
| `VOLCENGINE_TTS_TOKEN` | **Yes** | Access Token (Bearer token) |
| `VOLCENGINE_TTS_CLUSTER` | No | Cluster name (default: `volcano_tts`) |

Get credentials: https://console.volcengine.com → 豆包语音 → [FAQ Q1](https://www.volcengine.com/docs/6561/196768)

## References

- [豆包语音合成 2.0 能力介绍](https://www.volcengine.com/docs/6561/1871062)
- [HTTP 接口参数说明](https://www.volcengine.com/docs/6561/79823)
- [大模型音色列表](https://www.volcengine.com/docs/6561/1257544)
- [大模型 V1 HTTP 接口文档](https://www.volcengine.com/docs/6561/1257584)
- [SSML 标记语言](https://www.volcengine.com/docs/6561/1330194)
