---
name: doubao-music
description: AI music generation using Volcengine Doubao (豆包) Music API — generate vocal songs, instrumental BGM, and lyrics. Use when users want to create music, generate songs, compose BGM/background music, write lyrics, or anything related to AI music creation with Doubao/豆包/火山引擎.
metadata: { "openclaw": { "emoji": "🎵", "requires": { "bins": ["python3"], "env":["VOLC_ACCESSKEY","VOLC_SECRETKEY"]}, "primaryEnv":"VOLC_ACCESSKEY" } }
---

# Doubao Music (豆包音乐生成)

Generate vocal songs, instrumental BGM, and lyrics using Volcengine Doubao Music API. Supports multiple model versions (v4.0/v4.3/v5.0) with rich genre, mood, timbre, and scene controls.

## Prerequisites

1. Activate the **音视频理解与处理** service in [火山引擎控制台](https://console.volcengine.com)
2. Create IAM Access Key: [密钥管理](https://console.volcengine.com/iam/keymanage/)
3. Set environment variables:

```
VOLC_ACCESSKEY=your_access_key
VOLC_SECRETKEY=your_secret_key
```

## Workflow

### Vocal Song / BGM (Async)

1. **Submit Task** — call GenSong or GenBGM → get TaskID
2. **Poll Status** — query every 10s until Status=2 (success) or Status=3 (failed)
3. **Get Audio** — download AudioUrl from result

### Lyrics (Sync)

1. **Call GenLyrics** — returns lyrics immediately in response

## Quick Start

```bash
# Generate a vocal song
python3 scripts/music_gen.py song --prompt "一首温暖的流行歌曲，关于春天和希望"

# Generate instrumental BGM
python3 scripts/music_gen.py bgm --text "轻松的咖啡厅爵士背景音乐" --duration 30

# Generate lyrics
python3 scripts/music_gen.py lyrics --prompt "关于夏天海边的浪漫故事"

# Vocal song with full options (v4.3)
python3 scripts/music_gen.py song \
  --prompt "一首充满活力的摇滚歌曲" \
  --model-version v4.3 \
  --genre Rock --mood "Dynamic/Energetic" \
  --gender Male --timbre Powerful \
  --output rock_song.mp3

# BGM with options (v5.0)
python3 scripts/music_gen.py bgm \
  --text "史诗感的电影配乐" \
  --genre Epic --mood "Shocking/magnificent/epic" \
  --scene "Trailer" --instrument Strings \
  --duration 60 --output epic_bgm.mp3
```

## API Reference

All APIs use HMAC-SHA256 V4 signing against `open.volcengineapi.com`.

| Field | Value |
|-------|-------|
| Host | `open.volcengineapi.com` |
| Service | `imagination` |
| Region | `cn-beijing` |
| Version | `2024-08-12` |

### GenSongV4 / GenSongForTime — 生成人声歌曲

GenSongV4 is prepaid, GenSongForTime is postpaid. Same parameters.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `Prompt` | string | Yes | Song description (5-2000 chars, Chinese recommended) |
| `Lyrics` | string | No | Custom lyrics (leave empty for AI-generated) |
| `ModelVersion` | string | No | `v4.0` / `v4.3` / `v5.0` (default varies) |
| `Genre` | string | No | Music genre (see params reference) |
| `Mood` | string | No | Mood/emotion |
| `Gender` | string | No | `Male` / `Female` |
| `Timbre` | string | No | Voice timbre |
| `Duration` | int | No | Duration in seconds (0 = auto) |
| `Tempo` | string | No | V4.3 only: tempo marking |
| `Kmode` | string | No | V4.3 only: `Major` / `Minor` |
| `Instrument` | string | No | V4.3 only: instrument |
| `Scene` | string | No | V4.3 only: scene/occasion |
| `Lang` | string | No | V4.3+: language |

### GenBGM / GenBGMForTime — 生成纯音乐

GenBGM is prepaid, GenBGMForTime is postpaid. Same parameters.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `Text` | string | Yes | Music description (note: field name is `Text`, not `Prompt`) |
| `ModelVersion` | string | No | `v5.0` recommended |
| `Genre` | []string | No | Genre array, e.g. `["Jazz"]` |
| `Mood` | []string | No | Mood array, e.g. `["Chill"]` |
| `Scene` | []string | No | Scene array |
| `Instrument` | []string | No | Instrument array |
| `Duration` | int | No | Duration in seconds |

**Important**: BGM parameters `Genre`, `Mood`, `Scene`, `Instrument` are **arrays** (not strings). For `ModelVersion v5.0`, you can describe everything in `Text` and omit these fields.

### GenLyrics — 歌词生成

Synchronous — returns lyrics directly.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `Prompt` | string | Yes | Theme/description for lyrics |
| `Genre` | string | No | Genre |
| `Mood` | string | No | Mood |
| `Gender` | string | No | `Male` / `Female` |
| `ModelVersion` | string | No | `v3.0` |

### QuerySong — 查询任务状态

Used to poll vocal song and BGM generation tasks.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `TaskID` | string | Yes | Task ID from GenSong/GenBGM response |

**Status codes:**

| Status | Meaning | Action |
|--------|---------|--------|
| 1 | Processing | Continue polling |
| 2 | Success | Extract AudioUrl from SongDetail |
| 3 | Failed | Check FailureReason |

**Success response fields (Result.SongDetail):**

| Field | Description |
|-------|-------------|
| `AudioUrl` | Download URL for the generated audio |
| `Lyrics` | Generated lyrics (vocal songs) |
| `Duration` | Audio duration in seconds |

## Common Parameter Values (Quick Reference)

### Gender
`Male`, `Female`

### ModelVersion
- Vocal songs: `v4.0`, `v4.3`, `v5.0`
- BGM: `v5.0`
- Lyrics: `v3.0`

### Kmode (V4.3)
`Major`, `Minor`

### Tempo (V4.3)
`Grave`, `Largo`, `Adagio`, `Andante`, `Moderato`, `Allegro`, `Vivace`, `Presto`

### Lang
- V4.3: `Chinese`, `English`, `Instrumental/Non-vocal`
- V5.0: `Chinese`, `Cantonese`, `English`, `Instrumental/Non-vocal`

### Genre (Vocal Song, common)
`Pop`, `Rock`, `Folk`, `Electronic`, `Jazz`, `Hip Hop/Rap`, `R&B/Soul`, `Chinese Style`, `Country`, `Blues`, `Metal`, `Reggae`, `DJ`, `Punk`, `Disco`, `Bossa Nova`, `Pop Rock`, `Alternative/Indie`

### Mood (common)
`Happy`, `Chill`, `Romantic`, `Dynamic/Energetic`, `Sentimental/Melancholic/Lonely`, `Inspirational/Hopeful`, `Nostalgic/Memory`, `Excited`, `Calm/Relaxing`, `Dreamy/Ethereal`, `Groovy/Funky`

### Timbre (Vocal Song, common)
`Warm`, `Bright`, `Husky`, `Powerful`, `Sweet_AUDIO_TIMBRE`, `Sexy/Lazy`, `Gentle`, `Energetic`, `Magnetic`, `Deep`

For the **complete parameter lists** (100+ genres, 30+ moods, 25+ timbres, 80+ instruments, 100+ scenes), read `references/params.md`.

## Polling Strategy

```bash
# Auto-poll with defaults (60 attempts, 10s interval = 10 min timeout)
python3 scripts/music_gen.py song --prompt "你的描述"

# Custom timeout
python3 scripts/music_gen.py song --prompt "你的描述" --max-poll 30 --poll-interval 15
```

Typical generation time: 1-3 minutes for songs, 30s-2min for BGM.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `AccessDenied` | AK/SK invalid or service not activated | Check credentials; activate 音视频理解与处理 service |
| `InvalidRequestParams` | Bad parameter value | Check parameter against allowed values in references/params.md |
| `APINoSource` | Service quota exhausted or not purchased | Purchase/activate the specific feature in console |
| `InternalError` with `missing required parameter` | Wrong field name | BGM uses `Text` (not `Prompt`); Genre/Mood/Instrument/Scene are arrays for BGM |
| `InternalError` with `invalid` | Parameter value not in allowed list | Check the correct ModelVersion's allowed values |
| Status=3 in polling | Generation failed | Check `FailureReason` in response; try simpler prompt |
| Polling timeout | Task still running | Increase `--max-poll`; complex prompts take longer |

## V4 Signing (HMAC-SHA256)

The script handles signing automatically. The signing process:

1. Create canonical request with `POST /`, query params `Action=<action>&Version=2024-08-12`, signed headers `content-type;host;x-date`
2. Build credential scope: `<date>/<region>/<service>/request`
3. Build string to sign: `HMAC-SHA256\n<datetime>\n<scope>\n<hash(canonical)>`
4. Derive signing key: HMAC chain of `SK → date → region → service → "request"`
5. Compute signature and set `Authorization` header

## Architecture Notes

- Vocal song and BGM generation are **asynchronous** — submit task, poll for result
- Lyrics generation is **synchronous** — result returned immediately
- Audio URLs from completed tasks are temporary — download promptly
- Chinese prompts generally produce better results than English
- V5.0 models are the latest; V4.3 offers more fine-grained parameter control
