#!/usr/bin/env python3
"""
Doubao TTS — Synthesize speech from text using Volcengine Doubao Speech API.
Supports 2.0 big-model voices, voice instructions, emotion, and more.

Usage:
    python3 tts_synthesize.py --text "你好" --output hello.mp3
    python3 tts_synthesize.py --text "[#用开心的语气]太棒了！" --voice zh_female_vv_uranus_bigtts
    python3 tts_synthesize.py --text "Hello" --encoding wav --speed 0.8 --output hello.wav

Env vars:
    VOLCENGINE_TTS_APPID   — App ID (required)
    VOLCENGINE_TTS_TOKEN   — Access Token (required)
    VOLCENGINE_TTS_CLUSTER — Cluster (default: volcano_tts)
"""

import os
import sys
import json
import uuid
import base64
import argparse
import requests

API_URL = "https://openspeech.bytedance.com/api/v1/tts"

VOICE_ALIASES = {
    "可爱女生": "zh_female_vv_uranus_bigtts",
    "调皮公主": "zh_female_vv_princess_bigtts",
    "爽朗少年": "zh_male_vv_young_bigtts",
    "天才同桌": "zh_male_vv_genius_bigtts",
    "灿灿": "BV700_streaming",
    "梓梓": "BV406_streaming",
    "通用女声": "BV001_streaming",
    "通用男声": "BV002_streaming",
}


def synthesize(
    appid: str,
    token: str,
    text: str,
    voice_type: str = "zh_female_vv_uranus_bigtts",
    encoding: str = "mp3",
    speed_ratio: float = 1.0,
    volume_ratio: float = 1.0,
    pitch_ratio: float = 1.0,
    emotion: str = "",
    language: str = "",
    cluster: str = "volcano_tts",
) -> dict:
    """Call Doubao TTS API. Returns dict with 'audio' (bytes), 'duration_ms', 'reqid'."""

    audio_params = {
        "voice_type": voice_type,
        "encoding": encoding,
        "speed_ratio": speed_ratio,
        "volume_ratio": volume_ratio,
        "pitch_ratio": pitch_ratio,
    }
    if emotion:
        audio_params["emotion"] = emotion
        audio_params["enable_emotion"] = True
    if language:
        audio_params["explicit_language"] = language

    payload = {
        "app": {
            "appid": appid,
            "token": "access_token",
            "cluster": cluster,
        },
        "user": {"uid": "doubao_tts_skill"},
        "audio": audio_params,
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "text_type": "plain",
            "operation": "query",
        },
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer;{token}",
    }

    resp = requests.post(API_URL, json=payload, headers=headers, timeout=60)
    result = resp.json()

    code = result.get("code")
    if code != 3000:
        raise RuntimeError(
            json.dumps({"code": code, "message": result.get("message")}, ensure_ascii=False)
        )

    audio_data = base64.b64decode(result["data"])
    duration_ms = result.get("addition", {}).get("duration", "0")
    reqid = result.get("reqid", "")

    return {"audio": audio_data, "duration_ms": duration_ms, "reqid": reqid}


def main():
    parser = argparse.ArgumentParser(description="Doubao TTS Synthesize")
    parser.add_argument("--text", required=True, help="Text to synthesize (supports [#指令] prefix)")
    parser.add_argument("--voice", default="zh_female_vv_uranus_bigtts", help="Voice type ID or name")
    parser.add_argument("--output", default="output.mp3", help="Output audio file path")
    parser.add_argument("--encoding", default="mp3", choices=["mp3", "wav", "pcm", "ogg_opus"])
    parser.add_argument("--speed", type=float, default=1.0, help="Speed ratio (0.2-3.0)")
    parser.add_argument("--volume", type=float, default=1.0, help="Volume ratio (0.1-3.0)")
    parser.add_argument("--pitch", type=float, default=1.0, help="Pitch ratio (0.1-3.0)")
    parser.add_argument("--emotion", default="", help="Emotion: happy, sad, angry, etc.")
    parser.add_argument("--language", default="", help="Language hint: zh-cn, en, ja, crosslingual")
    parser.add_argument("--cluster", default="", help="API cluster override")

    args = parser.parse_args()

    appid = os.getenv("VOLCENGINE_TTS_APPID", "")
    token = os.getenv("VOLCENGINE_TTS_TOKEN", "")
    cluster = args.cluster or os.getenv("VOLCENGINE_TTS_CLUSTER", "volcano_tts")

    if not appid or not token:
        print(json.dumps({
            "error": "VOLCENGINE_TTS_APPID and VOLCENGINE_TTS_TOKEN must be set"
        }, indent=2))
        sys.exit(1)

    voice_type = VOICE_ALIASES.get(args.voice, args.voice)

    try:
        result = synthesize(
            appid=appid,
            token=token,
            text=args.text,
            voice_type=voice_type,
            encoding=args.encoding,
            speed_ratio=args.speed,
            volume_ratio=args.volume,
            pitch_ratio=args.pitch,
            emotion=args.emotion,
            language=args.language,
            cluster=cluster,
        )

        with open(args.output, "wb") as f:
            f.write(result["audio"])

        print(f"合成成功 | 音频时长: {result['duration_ms']}ms | reqid: {result['reqid']}")
        print(f"音频已保存: {args.output} ({len(result['audio']):,} bytes)")

    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
