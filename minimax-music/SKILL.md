---
name: minimax-music
description: 使用 MiniMax 音乐生成 API（music-2.5 / music-2.5+）创作歌曲、纯音乐和自动歌词作品。用户提到“生成音乐/写歌/BGM/纯音乐/哼唱/歌词自动生成/MiniMax 音乐”时都应使用本 skill，即使用户只说“做一首歌”也应触发。
---

# MiniMax 音乐生成 Skill

用 MiniMax Music API 快速完成三类任务：
- 有歌词歌曲（Standard Song）
- 纯音乐（Instrumental）
- 自动写歌词并生成（Auto Lyrics）

## 环境变量

```bash
MINIMAX_MUSIC_API_KEY="你的 MiniMax Key"
```

兼容：
- 若未配置 `MINIMAX_MUSIC_API_KEY`，可回退使用 `MINIMAX_API_KEY`
- 可选：`MINIMAX_API_HOST`（默认 `https://api.minimaxi.com`）

## 接口与模型

- Endpoint：`POST https://api.minimaxi.com/v1/music_generation`
- 推荐模型：`music-2.5+`
- 兼容模型：`music-2.5`

详细参数参考：`references/minimax_music_api.md`

## 工作流程

### Step 1: 判断模式

1. **Standard Song**（默认）  
   用户提供歌词，或明确要“有人声演唱歌曲”。
2. **Instrumental**  
   用户说“纯音乐/BGM/无人声/instrumental”。
3. **Auto Lyrics**  
   用户希望“你先写歌词再生成”或“自动歌词”。

### Step 2: 组织 Prompt 与歌词

Prompt 采用结构化字段，优先覆盖：
- Genre（风格）
- Mood（情绪）
- BPM / Tempo（节奏）
- Instruments（主乐器）
- Vocals（人声特点）
- Use Case（使用场景）
- Avoid（不希望出现的元素）

建议模板：

```text
Genre: ...
Mood: ...
Tempo: ... BPM
Instruments: ...
Vocals: ...
Use case: ...
Avoid: ...
References: ...
```

歌词建议使用段落标签：

```text
[Intro]
[Verse]
[Pre Chorus]
[Chorus]
[Bridge]
[Outro]
```

### Step 3: 生成

**Standard Song（有歌词）**

```bash
curl -sS -X POST "https://api.minimaxi.com/v1/music_generation" \
  -H "Authorization: Bearer $MINIMAX_MUSIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "music-2.5+",
    "prompt": "Genre: pop, Mood: warm and uplifting, Tempo: 92 BPM, Instruments: piano + strings, Vocals: gentle female",
    "lyrics": "[Verse]\n...\n[Chorus]\n...",
    "output_format": "url",
    "audio_setting": {"sample_rate": 44100, "bitrate": 256000, "format": "mp3"}
  }'
```

**Instrumental（纯音乐）**

```bash
curl -sS -X POST "https://api.minimaxi.com/v1/music_generation" \
  -H "Authorization: Bearer $MINIMAX_MUSIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "music-2.5+",
    "prompt": "coffee shop lofi, relaxing, no vocals",
    "is_instrumental": true,
    "output_format": "url"
  }'
```

**Auto Lyrics（自动歌词）**

```bash
curl -sS -X POST "https://api.minimaxi.com/v1/music_generation" \
  -H "Authorization: Bearer $MINIMAX_MUSIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "music-2.5+",
    "prompt": "summer road trip, upbeat pop, male vocal",
    "lyrics_optimizer": true,
    "output_format": "url"
  }'
```

### Step 4: 保存与返回

- 若 `output_format=url`：下载 URL 到本地文件（URL 通常有时效）。
- 若 `output_format=hex`：按十六进制解码保存音频。
- 输出给用户：文件路径、时长（如接口返回）、主要参数。

## 质量与安全约束

- 不要承诺“精确复刻真人歌手声音”。
- 可使用“风格参考”描述，但避免宣称是官方授权克隆。
- 出现 API 失败时，先重试一次；若仍失败，返回错误摘要与排查建议。

## 输出格式（给用户）

始终用以下格式回复结果：

```text
模式: <song|instrumental|auto-lyrics>
模型: <model>
提示词: <prompt 摘要>
输出文件: <path>
状态: <成功/失败>
```

