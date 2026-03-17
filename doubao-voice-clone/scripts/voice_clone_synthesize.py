#!/usr/bin/env python3
"""
Doubao Voice Clone — Synthesize speech using a cloned voice.

Usage:
    python3 voice_clone_synthesize.py --text "你好" --speaker-id S_my_voice --output cloned.mp3
"""

import os
import sys
import json
import uuid
import base64
import argparse
import requests

API_URL = "https://openspeech.bytedance.com/api/v1/tts"


def synthesize(appid: str, token: str, text: str, speaker_id: str,
               encoding: str = "mp3", speed_ratio: float = 1.0,
               cluster: str = "volcano_icl") -> dict:
    payload = {
        "app": {
            "appid": appid,
            "token": "access_token",
            "cluster": cluster,
        },
        "user": {"uid": "voice_clone_skill"},
        "audio": {
            "voice_type": speaker_id,
            "encoding": encoding,
            "speed_ratio": speed_ratio,
        },
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

    if result.get("code") != 3000:
        raise RuntimeError(
            json.dumps({"code": result.get("code"), "message": result.get("message")}, ensure_ascii=False)
        )

    audio_data = base64.b64decode(result["data"])
    return {
        "audio": audio_data,
        "duration_ms": result.get("addition", {}).get("duration", "0"),
        "reqid": result.get("reqid", ""),
    }


def main():
    parser = argparse.ArgumentParser(description="Doubao Voice Clone — Synthesize")
    parser.add_argument("--text", required=True, help="Text to synthesize")
    parser.add_argument("--speaker-id", required=True, help="Cloned speaker ID")
    parser.add_argument("--output", default="cloned_output.mp3", help="Output file path")
    parser.add_argument("--encoding", default="mp3", choices=["mp3", "wav", "pcm", "ogg_opus"])
    parser.add_argument("--speed", type=float, default=1.0, help="Speed ratio (0.2-3.0)")
    parser.add_argument("--cluster", default="volcano_icl",
                        help="volcano_icl (字符版) or volcano_icl_concurr (并发版)")

    args = parser.parse_args()

    appid = os.getenv("VOLCENGINE_TTS_APPID", "")
    token = os.getenv("VOLCENGINE_TTS_TOKEN", "")

    if not appid or not token:
        print(json.dumps({"error": "VOLCENGINE_TTS_APPID and VOLCENGINE_TTS_TOKEN must be set"}, indent=2))
        sys.exit(1)

    try:
        result = synthesize(appid, token, args.text, args.speaker_id,
                            args.encoding, args.speed, args.cluster)
        with open(args.output, "wb") as f:
            f.write(result["audio"])
        print(f"合成成功 | 时长: {result['duration_ms']}ms | reqid: {result['reqid']}")
        print(f"音频已保存: {args.output} ({len(result['audio']):,} bytes)")
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
