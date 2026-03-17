#!/usr/bin/env python3
"""
Doubao Voice Clone — Check training status of a cloned voice.

Usage:
    python3 voice_clone_status.py --speaker-id S_my_voice
"""

import os
import sys
import json
import argparse
import requests

API_URL = "https://openspeech.bytedance.com/api/v1/mega_tts/status"

STATUS_MAP = {0: "未开始", 1: "训练中", 2: "训练成功", 3: "训练失败"}


def check_status(appid: str, token: str, speaker_id: str, resource_id: str = "seed-icl-1.0") -> dict:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer;{token}",
        "Resource-Id": resource_id,
    }
    body = {"appid": appid, "speaker_id": speaker_id}

    resp = requests.post(API_URL, json=body, headers=headers, timeout=30)

    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")

    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Doubao Voice Clone — Check Status")
    parser.add_argument("--speaker-id", required=True, help="Speaker ID to check")
    parser.add_argument("--resource-id", default="seed-icl-1.0",
                        help="seed-icl-1.0 or seed-icl-2.0")

    args = parser.parse_args()

    appid = os.getenv("VOLCENGINE_TTS_APPID", "")
    token = os.getenv("VOLCENGINE_TTS_TOKEN", "")

    if not appid or not token:
        print(json.dumps({"error": "VOLCENGINE_TTS_APPID and VOLCENGINE_TTS_TOKEN must be set"}, indent=2))
        sys.exit(1)

    try:
        result = check_status(appid, token, args.speaker_id, args.resource_id)
        base_resp = result.get("BaseResp", {})
        code = base_resp.get("StatusCode", -1)

        if code != 0:
            print(f"Error [{code}]: {base_resp.get('StatusMessage', '')}")
            sys.exit(1)

        status = result.get("status", -1)
        demo_audio = result.get("demo_audio", "")
        status_text = STATUS_MAP.get(status, f"未知({status})")

        print(f"Speaker ID: {args.speaker_id}")
        print(f"训练状态: {status_text} (code={status})")
        if demo_audio:
            print(f"试听音频: {demo_audio}")

    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
