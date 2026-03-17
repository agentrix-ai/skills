#!/usr/bin/env python3
"""
Doubao ASR — Transcribe audio files using Big-Model ASR 2.0.

Usage:
    python3 asr_transcribe.py --audio recording.mp3
    python3 asr_transcribe.py --url "https://example.com/audio.wav"
    python3 asr_transcribe.py --audio meeting.mp3 --speakers --output transcript.txt
"""

import os
import sys
import json
import uuid
import base64
import time
import argparse
import requests

SUBMIT_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit"
QUERY_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query"


def transcribe(
    appid: str,
    token: str,
    audio_path: str = "",
    audio_url: str = "",
    audio_format: str = "",
    enable_speakers: bool = False,
    enable_channels: bool = False,
    max_wait: int = 120,
) -> dict:
    task_id = str(uuid.uuid4())

    headers = {
        "X-Api-App-Key": appid,
        "X-Api-Access-Key": token,
        "X-Api-Resource-Id": "volc.bigasr.auc",
        "X-Api-Request-Id": task_id,
        "X-Api-Sequence": "-1",
        "Content-Type": "application/json",
    }

    audio_section = {}
    if audio_path:
        with open(audio_path, "rb") as f:
            audio_section["data"] = base64.b64encode(f.read()).decode("utf-8")
        if not audio_format:
            ext = os.path.splitext(audio_path)[1].lstrip(".").lower()
            audio_format = ext if ext else "wav"
    elif audio_url:
        audio_section["url"] = audio_url
        if not audio_format:
            for ext in ["mp3", "wav", "ogg", "m4a", "flac", "aac"]:
                if ext in audio_url.lower():
                    audio_format = ext
                    break
            else:
                audio_format = "wav"

    audio_section["format"] = audio_format
    audio_section["codec"] = "raw"

    request_params = {
        "model_name": "bigmodel",
        "model_version": "400",
        "enable_itn": True,
        "enable_punc": True,
        "enable_ddc": True,
        "show_utterances": True,
    }
    if enable_speakers:
        request_params["enable_speaker_info"] = True
    if enable_channels:
        request_params["enable_channel_split"] = True

    body = {
        "user": {"uid": "asr_skill"},
        "audio": audio_section,
        "request": request_params,
    }

    resp = requests.post(SUBMIT_URL, json=body, headers=headers, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Submit failed HTTP {resp.status_code}: {resp.text[:200]}")

    query_headers = {
        "X-Api-App-Key": appid,
        "X-Api-Access-Key": token,
        "X-Api-Resource-Id": "volc.bigasr.auc",
        "X-Api-Request-Id": task_id,
        "Content-Type": "application/json",
    }

    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            raise RuntimeError(f"Timeout after {max_wait}s. Task ID: {task_id}")

        time.sleep(min(3, max_wait - elapsed))

        resp2 = requests.post(QUERY_URL, json={}, headers=query_headers, timeout=30)
        result = resp2.json()

        resp_section = result.get("resp", {})
        code = resp_section.get("code")

        if code == 20000001 or code == 20000002:
            continue

        if code == 20000000:
            return {
                "task_id": task_id,
                "audio_info": result.get("audio_info", {}),
                "result": resp_section.get("result", {}),
            }

        if "result" in result and result["result"].get("text"):
            return {
                "task_id": task_id,
                "audio_info": result.get("audio_info", {}),
                "result": result["result"],
            }

        if code is not None:
            raise RuntimeError(f"ASR failed [{code}]: {resp_section.get('message', '')}")

        return {
            "task_id": task_id,
            "audio_info": result.get("audio_info", {}),
            "result": result.get("result", {}),
        }


def main():
    parser = argparse.ArgumentParser(description="Doubao ASR — Transcribe Audio")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--audio", help="Path to local audio file")
    group.add_argument("--url", help="URL to audio file")
    parser.add_argument("--output", help="Save transcript to text file")
    parser.add_argument("--format", default="", help="Audio format (auto-detected if omitted)")
    parser.add_argument("--speakers", action="store_true", help="Enable speaker diarization")
    parser.add_argument("--channels", action="store_true", help="Enable channel splitting")
    parser.add_argument("--words", action="store_true", help="Show word-level timestamps")
    parser.add_argument("--max-wait", type=int, default=120, help="Max wait seconds for async tasks")

    args = parser.parse_args()

    appid = os.getenv("VOLCENGINE_TTS_APPID", "")
    token = os.getenv("VOLCENGINE_TTS_TOKEN", "")

    if not appid or not token:
        print(json.dumps({"error": "VOLCENGINE_TTS_APPID and VOLCENGINE_TTS_TOKEN must be set"}, indent=2))
        sys.exit(1)

    if args.audio and not os.path.isfile(args.audio):
        print(json.dumps({"error": f"File not found: {args.audio}"}, indent=2))
        sys.exit(1)

    source = args.audio or args.url
    print(f"音频来源: {source}")

    try:
        result = transcribe(
            appid=appid, token=token,
            audio_path=args.audio or "", audio_url=args.url or "",
            audio_format=args.format,
            enable_speakers=args.speakers, enable_channels=args.channels,
            max_wait=args.max_wait,
        )

        duration = result["audio_info"].get("duration", 0)
        text = result["result"].get("text", "")
        utterances = result["result"].get("utterances", [])

        print(f"音频时长: {duration}ms")
        print(f"识别结果: {text}")

        if utterances and len(utterances) > 1:
            print(f"\n分句 ({len(utterances)} 句):")
            for i, u in enumerate(utterances):
                start = u.get("start_time", 0)
                end = u.get("end_time", 0)
                spk = u.get("speaker", "")
                prefix = f"[说话人{spk}] " if spk else ""
                print(f"  {prefix}[{start/1000:.1f}s-{end/1000:.1f}s] {u.get('text', '')}")

        if args.words and utterances:
            print(f"\n逐字时间戳:")
            for u in utterances:
                for w in u.get("words", []):
                    s = w.get("start_time", 0)
                    e = w.get("end_time", 0)
                    print(f"  [{s/1000:.2f}s-{e/1000:.2f}s] {w.get('text', '')}")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text + "\n")
                if utterances and len(utterances) > 1:
                    f.write("\n--- 分句明细 ---\n")
                    for u in utterances:
                        start = u.get("start_time", 0)
                        end = u.get("end_time", 0)
                        f.write(f"[{start/1000:.1f}s-{end/1000:.1f}s] {u.get('text', '')}\n")
            print(f"\n已保存: {args.output}")

    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
