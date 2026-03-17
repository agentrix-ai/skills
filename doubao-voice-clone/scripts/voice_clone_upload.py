#!/usr/bin/env python3
"""
Doubao Voice Clone — Upload audio to train a cloned voice.

Usage:
    python3 voice_clone_upload.py --audio sample.wav --speaker-id S_my_voice
    python3 voice_clone_upload.py --audio sample.mp3 --speaker-id S_my_voice --model-type 4 --resource-id seed-icl-2.0
"""

import os
import sys
import json
import base64
import argparse
import requests

API_URL = "https://openspeech.bytedance.com/api/v1/mega_tts/audio/upload"


def upload_audio(
    appid: str,
    token: str,
    audio_path: str,
    speaker_id: str,
    model_type: int = 1,
    language: int = 0,
    resource_id: str = "seed-icl-1.0",
    denoise: bool = False,
) -> dict:
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    ext = os.path.splitext(audio_path)[1].lstrip(".").lower()
    if ext in ("m4a", "pcm"):
        audio_format = ext
    else:
        audio_format = ext if ext else "wav"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer;{token}",
        "Resource-Id": resource_id,
    }

    extra = {}
    if denoise:
        extra["enable_audio_denoise"] = True

    body = {
        "appid": appid,
        "speaker_id": speaker_id,
        "audios": [{"audio_bytes": audio_b64, "audio_format": audio_format}],
        "source": 2,
        "language": language,
        "model_type": model_type,
    }
    if extra:
        body["extra_params"] = json.dumps(extra)

    resp = requests.post(API_URL, json=body, headers=headers, timeout=120)

    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")

    result = resp.json()
    base_resp = result.get("BaseResp", {})
    code = base_resp.get("StatusCode", -1)

    if code != 0:
        raise RuntimeError(
            json.dumps({"code": code, "message": base_resp.get("StatusMessage", "")}, ensure_ascii=False)
        )

    return result


def main():
    parser = argparse.ArgumentParser(description="Doubao Voice Clone — Upload Audio")
    parser.add_argument("--audio", required=True, help="Path to audio file (wav/mp3/ogg/m4a/aac)")
    parser.add_argument("--speaker-id", required=True, help="Speaker ID from console (S_xxxxxxx)")
    parser.add_argument("--model-type", type=int, default=1, choices=[1, 2, 3, 4],
                        help="1=ICL1.0, 2=DiT standard, 3=DiT restore, 4=ICL2.0")
    parser.add_argument("--language", type=int, default=0,
                        help="0=Chinese, 1=English, 2=Japanese, 3=Spanish, 4=Indonesian, 5=Portuguese")
    parser.add_argument("--resource-id", default="seed-icl-1.0",
                        help="seed-icl-1.0 (ICL1.0) or seed-icl-2.0 (ICL2.0)")
    parser.add_argument("--denoise", action="store_true", help="Enable audio denoising")

    args = parser.parse_args()

    appid = os.getenv("VOLCENGINE_TTS_APPID", "")
    token = os.getenv("VOLCENGINE_TTS_TOKEN", "")

    if not appid or not token:
        print(json.dumps({"error": "VOLCENGINE_TTS_APPID and VOLCENGINE_TTS_TOKEN must be set"}, indent=2))
        sys.exit(1)

    if not os.path.isfile(args.audio):
        print(json.dumps({"error": f"Audio file not found: {args.audio}"}, indent=2))
        sys.exit(1)

    file_size = os.path.getsize(args.audio)
    print(f"音频文件: {args.audio} ({file_size:,} bytes)")
    print(f"Speaker ID: {args.speaker_id}")
    print(f"Model: type={args.model_type} | Language: {args.language} | Resource: {args.resource_id}")

    try:
        result = upload_audio(
            appid=appid, token=token, audio_path=args.audio,
            speaker_id=args.speaker_id, model_type=args.model_type,
            language=args.language, resource_id=args.resource_id,
            denoise=args.denoise,
        )
        print(f"上传成功 | speaker_id: {result.get('speaker_id', args.speaker_id)}")
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
