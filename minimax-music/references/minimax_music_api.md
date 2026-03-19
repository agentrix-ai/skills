# MiniMax Music API 快速参考

> 官方文档：<https://platform.minimaxi.com/docs/api-reference/music-generation>

## Endpoint

`POST https://api.minimaxi.com/v1/music_generation`

## 鉴权

`Authorization: Bearer <MINIMAX_MUSIC_API_KEY>`

## 常用请求字段

必填（常见场景）：
- `model`：`music-2.5` 或 `music-2.5+`
- `lyrics`：歌曲模式通常必填

可选：
- `prompt`：风格与编曲描述
- `is_instrumental`：纯音乐模式（常用于 `music-2.5+`）
- `lyrics_optimizer`：自动歌词
- `stream`：流式输出
- `output_format`：`hex` / `url`
- `audio_setting`：
  - `sample_rate`
  - `bitrate`
  - `format`
  - `aigc_watermark`（不同版本位置略有差异，按官方最新文档为准）

## 响应要点

- `data.audio`：hex 音频或 URL
- `data.status`：生成状态（常见 1 处理中，2 完成）
- `extra_info`：时长、码率、采样率等信息
- `base_resp.status_code = 0`：成功

## 实践建议

1. 优先 `music-2.5+`。
2. 输出优先 `url`（下载更直观），调试时可用 `hex`。
3. Prompt 写“动态变化”比平铺标签更稳定（如主歌到副歌能量递进）。
4. 出错先检查：Key、模型名、必填字段、请求体 JSON 合法性。

