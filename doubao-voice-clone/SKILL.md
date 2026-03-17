---
name: doubao-voice-clone
description: Clone voices using Volcengine Doubao (豆包) Voice Cloning API — upload audio, train, check status, then synthesize with cloned voice
metadata: { "openclaw": { "emoji": "🎙️", "requires": { "bins": ["python3"], "env":["VOLCENGINE_TTS_APPID","VOLCENGINE_TTS_TOKEN"]},"primaryEnv":"VOLCENGINE_TTS_TOKEN" } }
---

# Doubao Voice Clone (豆包声音复刻)

Clone any voice from an audio sample using Volcengine Doubao Voice Cloning API. After training, use the cloned voice for text-to-speech synthesis.

## Prerequisites

1. Activate the **声音复刻** service in [豆包语音控制台](https://console.volcengine.com/speech/service/8)
2. **Order a speaker_id**: Go to console → 声音复刻 → 下单 to get a `speaker_id` (format: `S_xxxxxxx`)
3. Set environment variables: `VOLCENGINE_TTS_APPID`, `VOLCENGINE_TTS_TOKEN`

## Workflow

1. **Upload Audio** → Train a voice clone from an audio sample
2. **Check Status** → Poll until training completes
3. **Synthesize** → Use the cloned `speaker_id` as `voice_type` in TTS

## APIs

### 1. Upload & Train

**Endpoint**: `POST https://openspeech.bytedance.com/api/v1/mega_tts/audio/upload`

**Script**: `scripts/voice_clone_upload.py`

**Parameters**:

| Param | Flag | Required | Default | Description |
|-------|------|----------|---------|-------------|
| audio | `--audio` | **Yes** | — | Path to audio file (wav/mp3/ogg/m4a/aac, max 10MB) |
| speaker_id | `--speaker-id` | **Yes** | — | Speaker ID from console (format: `S_xxxxxxx`) |
| model_type | `--model-type` | No | `1` | Clone model: `1`=ICL1.0, `2`=DiT standard, `3`=DiT restore, `4`=ICL2.0 |
| language | `--language` | No | `0` | `0`=Chinese, `1`=English, `2`=Japanese, `3`=Spanish, `4`=Indonesian, `5`=Portuguese |
| denoise | `--denoise` | No | — | Enable audio denoising |
| resource_id | `--resource-id` | No | `seed-icl-1.0` | `seed-icl-1.0` for ICL1.0, `seed-icl-2.0` for ICL2.0 |

**Examples**:
```bash
# Upload audio to train voice clone (ICL 1.0)
python3 scripts/voice_clone_upload.py --audio sample.wav --speaker-id S_my_voice_01

# ICL 2.0 model
python3 scripts/voice_clone_upload.py --audio sample.mp3 --speaker-id S_my_voice_02 --model-type 4 --resource-id seed-icl-2.0

# English voice with denoising
python3 scripts/voice_clone_upload.py --audio english.wav --speaker-id S_en_voice --language 1 --denoise

# DiT restore model (preserves accent and speaking style)
python3 scripts/voice_clone_upload.py --audio sample.wav --speaker-id S_dit_voice --model-type 3
```

**Success output**:
```
上传成功 | speaker_id: S_my_voice_01
```

### 2. Check Training Status

**Endpoint**: `POST https://openspeech.bytedance.com/api/v1/mega_tts/status`

**Script**: `scripts/voice_clone_status.py`

**Parameters**:

| Param | Flag | Required | Description |
|-------|------|----------|-------------|
| speaker_id | `--speaker-id` | **Yes** | Speaker ID to check |
| resource_id | `--resource-id` | No | `seed-icl-1.0` (default) or `seed-icl-2.0` |

**Example**:
```bash
python3 scripts/voice_clone_status.py --speaker-id S_my_voice_01
```

**Status Codes**:

| Code | Status | Action |
|------|--------|--------|
| 0 | Not started | Upload audio first |
| 1 | Training | Wait and re-check |
| 2 | Success | Ready for synthesis |
| 3 | Failed | Check error and retry |

### 3. Synthesize with Cloned Voice

After training completes (status=2), use the `speaker_id` as `voice_type` in the TTS API:

```bash
# Using the doubao-tts skill's script:
python3 ../doubao-tts/scripts/tts_synthesize.py --text "你好" --voice S_my_voice_01 --cluster volcano_icl

# Or directly with this skill's synthesize script:
python3 scripts/voice_clone_synthesize.py --text "你好世界" --speaker-id S_my_voice_01 --output cloned.mp3
```

**Important cluster mapping for cloned voices**:

| model_type | Cluster (字符版) | Cluster (并发版) |
|-----------|-----------------|-----------------|
| 1, 2, 3 (ICL 1.0) | `volcano_icl` | `volcano_icl_concurr` |
| 4 (ICL 2.0) | `volcano_icl` | `volcano_icl_concurr` |

## Model Types

| model_type | Name | Description |
|-----------|------|-------------|
| `1` | ICL 1.0 | Standard voice cloning, good quality |
| `2` | DiT Standard | Tone only, doesn't preserve speaking style |
| `3` | DiT Restore | Preserves accent, speed, and speaking style |
| `4` | ICL 2.0 | Latest model, best quality |

## Audio Requirements

- **Formats**: wav, mp3, ogg, m4a, aac, pcm (pcm must be 24kHz mono)
- **Max size**: 10MB per file
- **Best practice**: 10-30 seconds of clear speech, minimal background noise
- **Upload limit**: 10 uploads per speaker_id

## Error Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1001 | Bad request parameters |
| 1101 | Audio upload failed |
| 1102 | ASR transcription failed |
| 1103 | Voiceprint detection failed |
| 1104 | Voiceprint too similar to celebrity |
| 1106 | Speaker ID already exists |
| 1107 | Speaker ID not found |
| 1108 | Audio transcoding failed |
| 1109 | Audio-text mismatch too large |
| 1111 | No speech detected in audio |
| 1112 | Signal-to-noise ratio too low |
| 1122 | No human voice detected |
| 1123 | Upload limit reached (max 10 per speaker) |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VOLCENGINE_TTS_APPID` | **Yes** | Application ID |
| `VOLCENGINE_TTS_TOKEN` | **Yes** | Access Token |
| `VOLCENGINE_TTS_CLUSTER` | No | Default cluster (default: `volcano_icl`) |

## References

- [声音复刻 API-V1 文档](https://www.volcengine.com/docs/6561/1305191)
- [声音复刻 API-V3 文档 (推荐)](https://www.volcengine.com/docs/6561/2227958)
- [声音复刻下单指南](https://www.volcengine.com/docs/6561/1167802)
- [声音复刻最佳实践](https://www.volcengine.com/docs/6561/1204182)
- [音色管理 API](https://www.volcengine.com/docs/6561/2235883)
