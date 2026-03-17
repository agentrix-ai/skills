---
name: doubao-asr
description: Transcribe audio files to text using Volcengine Doubao (豆包) Big-Model ASR 2.0 with word-level timestamps
metadata: { "openclaw": { "emoji": "👂", "requires": { "bins": ["python3"], "env":["VOLCENGINE_TTS_APPID","VOLCENGINE_TTS_TOKEN"]},"primaryEnv":"VOLCENGINE_TTS_TOKEN" } }
---

# Doubao ASR (豆包录音文件识别 2.0)

Transcribe audio files to text using Volcengine Doubao Big-Model ASR. Supports word-level timestamps, punctuation, ITN (inverse text normalization), speaker diarization, and channel splitting.

## Workflow

1. **Submit** — Upload audio (file or URL) to start transcription
2. **Query** — Poll for results (small files return instantly; large files are async)
3. **Get Results** — Full text + word-level timestamps + optional speaker info

## Quick Start

```bash
# Transcribe a local audio file
python3 scripts/asr_transcribe.py --audio recording.mp3

# Transcribe from URL
python3 scripts/asr_transcribe.py --url "https://example.com/audio.wav"

# Save transcription to file
python3 scripts/asr_transcribe.py --audio meeting.mp3 --output transcript.txt

# With speaker diarization
python3 scripts/asr_transcribe.py --audio meeting.mp3 --speakers
```

## API

### Transcribe

**Submit**: `POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit`
**Query**: `POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/query`

**Script**: `scripts/asr_transcribe.py`

**Parameters**:

| Param | Flag | Required | Default | Description |
|-------|------|----------|---------|-------------|
| audio | `--audio` | Yes* | — | Path to local audio file |
| url | `--url` | Yes* | — | URL to audio file |
| output | `--output` | No | — | Save transcript to text file |
| format | `--format` | No | auto-detect | Audio format: `mp3`, `wav`, `ogg`, `m4a`, `flac`, `aac`, `amr` |
| speakers | `--speakers` | No | false | Enable speaker diarization |
| channels | `--channels` | No | false | Enable channel splitting |
| words | `--words` | No | false | Show word-level timestamps |
| max-wait | `--max-wait` | No | `120` | Max seconds to wait for async tasks |

*One of `--audio` or `--url` is required.

**Examples**:
```bash
# Basic transcription
python3 scripts/asr_transcribe.py --audio podcast.mp3

# Show word-level timestamps
python3 scripts/asr_transcribe.py --audio speech.wav --words

# Multi-speaker meeting with output file
python3 scripts/asr_transcribe.py --audio meeting.mp3 --speakers --output meeting.txt

# From URL with channel splitting
python3 scripts/asr_transcribe.py --url "https://example.com/call.wav" --channels

# Custom audio format
python3 scripts/asr_transcribe.py --audio recording.raw --format pcm
```

**Success output**:
```
音频时长: 5496ms
识别结果: 你好，我是豆包语音合成，今天天气真不错，一起出去走走吧。
```

With `--words`:
```
音频时长: 5496ms
识别结果: 你好，我是豆包语音合成，今天天气真不错，一起出去走走吧。

逐字时间戳:
  [0.19s-0.35s] 你
  [0.35s-0.71s] 好
  [0.71s-0.99s] 我
  ...
```

## Request Parameters (Advanced)

These can be set in the `request` object when calling the API directly:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | string | `bigmodel` | Model name |
| `model_version` | string | `400` | Model version |
| `enable_itn` | bool | `true` | Inverse text normalization (numbers → digits) |
| `enable_punc` | bool | `true` | Automatic punctuation |
| `enable_ddc` | bool | `true` | Spoken language normalization |
| `show_utterances` | bool | `true` | Return sentence-level segments |
| `enable_channel_split` | bool | `false` | Split audio channels (for stereo) |
| `enable_speaker_info` | bool | `false` | Speaker diarization |

## Auth Headers

The ASR API uses header-based auth (different from TTS Bearer token):

| Header | Value |
|--------|-------|
| `X-Api-App-Key` | AppID |
| `X-Api-Access-Key` | Access Token |
| `X-Api-Resource-Id` | `volc.bigasr.auc` |
| `X-Api-Request-Id` | Unique task UUID |
| `X-Api-Sequence` | `-1` (single request) |

## Response Status Codes

| Code | Status | Action |
|------|--------|--------|
| `20000000` | Completed | Results available |
| `20000001` | Queued | Wait and re-query |
| `20000002` | Processing | Wait and re-query |
| Other | Failed | Check error message |

## Supported Audio Formats

mp3, wav, ogg, m4a, flac, aac, amr, pcm (16kHz 16bit mono)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VOLCENGINE_TTS_APPID` | **Yes** | Application ID |
| `VOLCENGINE_TTS_TOKEN` | **Yes** | Access Token |

## References

- [大模型录音文件识别标准版 API](https://www.volcengine.com/docs/6561/1354868)
- [大模型录音文件识别极速版 API](https://www.volcengine.com/docs/6561/1631584)
- [豆包语音产品文档](https://www.volcengine.com/docs/6561/163032)
