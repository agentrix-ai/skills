#!/usr/bin/env python3
"""
Doubao Music Generation CLI — vocal songs, BGM, and lyrics.

Usage:
  python3 music_gen.py song   --prompt "描述" [options]
  python3 music_gen.py bgm    --text "描述" [options]
  python3 music_gen.py lyrics  --prompt "描述" [options]

Requires: VOLC_ACCESSKEY, VOLC_SECRETKEY env vars
"""

import argparse
import datetime
import hashlib
import hmac
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: pip install requests")

HOST = "open.volcengineapi.com"
SERVICE = "imagination"
REGION = "cn-beijing"
VERSION = "2024-08-12"


def _sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def api_call(ak: str, sk: str, action: str, body: dict) -> dict:
    now = datetime.datetime.now(datetime.timezone.utc)
    ds = now.strftime("%Y%m%d")
    dt = now.strftime("%Y%m%dT%H%M%SZ")
    raw = json.dumps(body)

    from urllib.parse import quote
    qs = f"Action={quote(action)}&Version={quote(VERSION)}"
    ch = f"content-type:application/json\nhost:{HOST}\nx-date:{dt}\n"
    sh = "content-type;host;x-date"
    ph = hashlib.sha256(raw.encode()).hexdigest()
    cr = f"POST\n/\n{qs}\n{ch}\n{sh}\n{ph}"
    cs = f"{ds}/{REGION}/{SERVICE}/request"
    sts = f"HMAC-SHA256\n{dt}\n{cs}\n{hashlib.sha256(cr.encode()).hexdigest()}"

    k = _sign(sk.encode(), ds)
    k = _sign(k, REGION)
    k = _sign(k, SERVICE)
    k = _sign(k, "request")
    sig = hmac.new(k, sts.encode(), hashlib.sha256).hexdigest()
    auth = f"HMAC-SHA256 Credential={ak}/{cs}, SignedHeaders={sh}, Signature={sig}"

    resp = requests.post(
        f"https://{HOST}/?{qs}",
        headers={
            "Content-Type": "application/json",
            "Host": HOST,
            "X-Date": dt,
            "Authorization": auth,
        },
        data=raw,
        timeout=30,
    )
    return resp.json()


def check_error(resp: dict) -> bool:
    err = resp.get("ResponseMetadata", {}).get("Error", {})
    if err:
        print(f"[ERROR] {err.get('Code')}: {err.get('Message')}", file=sys.stderr)
        return True
    return False


def poll_task(ak: str, sk: str, task_id: str, max_poll: int, interval: int, output: str):
    print(f"Polling task {task_id} ...")
    for i in range(max_poll):
        time.sleep(interval)
        result = api_call(ak, sk, "QuerySong", {"TaskID": task_id})
        res = result.get("Result") or {}
        status = res.get("Status", -1)
        elapsed = (i + 1) * interval
        print(f"  [{elapsed:>4}s] Status={status}")

        if status == 2:
            song = res.get("SongDetail") or {}
            audio_url = song.get("AudioUrl", "")
            lyrics = song.get("Lyrics", "")
            duration = song.get("Duration", 0)
            print(f"\n  Success! Duration: {duration}s")
            if lyrics:
                print(f"  Lyrics:\n{lyrics[:800]}")
            if audio_url:
                ext = "wav" if "wav" in audio_url else "mp3"
                out = output or f"output.{ext}"
                print(f"  Downloading to {out} ...")
                audio = requests.get(audio_url, timeout=120)
                with open(out, "wb") as f:
                    f.write(audio.content)
                print(f"  Saved: {out} ({len(audio.content) / 1024:.1f} KB)")
            return True

        if status == 3:
            reason = res.get("FailureReason", {})
            print(f"\n  Failed: {json.dumps(reason, ensure_ascii=False)}", file=sys.stderr)
            return False

    print(f"\n  Timeout after {max_poll * interval}s", file=sys.stderr)
    return False


def cmd_song(args, ak, sk):
    body = {"Prompt": args.prompt}
    if args.lyrics:
        body["Lyrics"] = args.lyrics
    if args.model_version:
        body["ModelVersion"] = args.model_version
    if args.genre:
        body["Genre"] = args.genre
    if args.mood:
        body["Mood"] = args.mood
    if args.gender:
        body["Gender"] = args.gender
    if args.timbre:
        body["Timbre"] = args.timbre
    if args.tempo:
        body["Tempo"] = args.tempo
    if args.kmode:
        body["Kmode"] = args.kmode
    if args.instrument:
        body["Instrument"] = args.instrument
    if args.scene:
        body["Scene"] = args.scene
    if args.lang:
        body["Lang"] = args.lang
    if args.duration:
        body["Duration"] = args.duration

    action = "GenSongV4" if args.prepaid else "GenSongForTime"
    print(f"Submitting {action} ...")
    print(f"  Prompt: {args.prompt}")
    resp = api_call(ak, sk, action, body)
    if check_error(resp):
        sys.exit(1)
    task_id = (resp.get("Result") or {}).get("TaskID", "")
    if not task_id:
        print(f"No TaskID in response: {json.dumps(resp, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)
    print(f"  TaskID: {task_id}")
    poll_task(ak, sk, task_id, args.max_poll, args.poll_interval, args.output)


def cmd_bgm(args, ak, sk):
    body = {"Text": args.text}
    if args.model_version:
        body["ModelVersion"] = args.model_version
    if args.duration:
        body["Duration"] = args.duration
    if args.genre:
        body["Genre"] = [args.genre] if isinstance(args.genre, str) else args.genre
    if args.mood:
        body["Mood"] = [args.mood] if isinstance(args.mood, str) else args.mood
    if args.scene:
        body["Scene"] = [args.scene] if isinstance(args.scene, str) else args.scene
    if args.instrument:
        body["Instrument"] = [args.instrument] if isinstance(args.instrument, str) else args.instrument

    action = "GenBGM" if args.prepaid else "GenBGMForTime"
    print(f"Submitting {action} ...")
    print(f"  Text: {args.text}")
    resp = api_call(ak, sk, action, body)
    if check_error(resp):
        sys.exit(1)
    task_id = (resp.get("Result") or {}).get("TaskID", "")
    if not task_id:
        print(f"No TaskID in response: {json.dumps(resp, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)
    print(f"  TaskID: {task_id}")
    poll_task(ak, sk, task_id, args.max_poll, args.poll_interval, args.output)


def cmd_lyrics(args, ak, sk):
    body = {"Prompt": args.prompt}
    if args.genre:
        body["Genre"] = args.genre
    if args.mood:
        body["Mood"] = args.mood
    if args.gender:
        body["Gender"] = args.gender
    if args.model_version:
        body["ModelVersion"] = args.model_version

    print(f"Generating lyrics (GenLyrics) ...")
    print(f"  Prompt: {args.prompt}")
    resp = api_call(ak, sk, "GenLyrics", body)
    if check_error(resp):
        sys.exit(1)
    res = resp.get("Result") or {}
    lyrics = res.get("Lyrics", "")
    if lyrics:
        print(f"\nGenerated lyrics:\n{'─' * 40}")
        print(lyrics)
        print(f"{'─' * 40}")
        out = args.output or "output_lyrics.txt"
        with open(out, "w", encoding="utf-8") as f:
            f.write(lyrics)
        print(f"Saved: {out}")
    else:
        print(f"Response: {json.dumps(resp, ensure_ascii=False, indent=2)}")


def main():
    parser = argparse.ArgumentParser(description="Doubao Music Generation CLI")
    sub = parser.add_subparsers(dest="mode", required=True)

    # --- song ---
    p_song = sub.add_parser("song", help="Generate vocal song")
    p_song.add_argument("--prompt", required=True, help="Song description")
    p_song.add_argument("--lyrics", help="Custom lyrics (empty = AI generated)")
    p_song.add_argument("--model-version", help="v4.0 / v4.3 / v5.0")
    p_song.add_argument("--genre", help="Genre (e.g. Pop, Rock)")
    p_song.add_argument("--mood", help="Mood (e.g. Happy, Chill)")
    p_song.add_argument("--gender", help="Male / Female")
    p_song.add_argument("--timbre", help="Voice timbre (e.g. Warm, Powerful)")
    p_song.add_argument("--tempo", help="V4.3: Grave/Largo/Adagio/Andante/Moderato/Allegro/Vivace/Presto")
    p_song.add_argument("--kmode", help="V4.3: Major / Minor")
    p_song.add_argument("--instrument", help="V4.3: instrument (e.g. Acoustic_Piano)")
    p_song.add_argument("--scene", help="V4.3: scene (e.g. Coffee Shop)")
    p_song.add_argument("--lang", help="V4.3+: Chinese/English/Cantonese/Instrumental")
    p_song.add_argument("--duration", type=int, default=0, help="Duration in seconds (0=auto)")
    p_song.add_argument("--prepaid", action="store_true", help="Use prepaid API (GenSongV4)")
    p_song.add_argument("--output", "-o", help="Output file path")
    p_song.add_argument("--max-poll", type=int, default=60, help="Max polling attempts")
    p_song.add_argument("--poll-interval", type=int, default=10, help="Poll interval in seconds")

    # --- bgm ---
    p_bgm = sub.add_parser("bgm", help="Generate instrumental BGM")
    p_bgm.add_argument("--text", required=True, help="BGM description")
    p_bgm.add_argument("--model-version", default="v5.0", help="Model version (default: v5.0)")
    p_bgm.add_argument("--genre", help="Genre (wrapped as array)")
    p_bgm.add_argument("--mood", help="Mood (wrapped as array)")
    p_bgm.add_argument("--scene", help="Scene (wrapped as array)")
    p_bgm.add_argument("--instrument", help="Instrument (wrapped as array)")
    p_bgm.add_argument("--duration", type=int, default=30, help="Duration in seconds (default: 30)")
    p_bgm.add_argument("--prepaid", action="store_true", help="Use prepaid API (GenBGM)")
    p_bgm.add_argument("--output", "-o", help="Output file path")
    p_bgm.add_argument("--max-poll", type=int, default=60, help="Max polling attempts")
    p_bgm.add_argument("--poll-interval", type=int, default=10, help="Poll interval in seconds")

    # --- lyrics ---
    p_lyrics = sub.add_parser("lyrics", help="Generate lyrics")
    p_lyrics.add_argument("--prompt", required=True, help="Lyrics theme/description")
    p_lyrics.add_argument("--genre", help="Genre")
    p_lyrics.add_argument("--mood", help="Mood")
    p_lyrics.add_argument("--gender", help="Male / Female")
    p_lyrics.add_argument("--model-version", default="v3.0", help="Model version (default: v3.0)")
    p_lyrics.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    ak = os.getenv("VOLC_ACCESSKEY", "")
    sk = os.getenv("VOLC_SECRETKEY", "")
    if not ak or not sk:
        sys.exit("Error: set VOLC_ACCESSKEY and VOLC_SECRETKEY environment variables")

    if args.mode == "song":
        cmd_song(args, ak, sk)
    elif args.mode == "bgm":
        cmd_bgm(args, ak, sk)
    elif args.mode == "lyrics":
        cmd_lyrics(args, ak, sk)


if __name__ == "__main__":
    main()
