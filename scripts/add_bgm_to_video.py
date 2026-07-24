#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "command failed")
    return result.stdout.strip()


def duration(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)]))


def main() -> int:
    parser = argparse.ArgumentParser(description="Mix bgm.mp3 into the narration video.")
    parser.add_argument("--video", default="materials/output/final_voice.mp4")
    parser.add_argument("--bgm", default="materials/MP3/bgm.mp3")
    parser.add_argument("--output", default="materials/output/final_video.mp4")
    parser.add_argument("--bgm-volume", type=float, default=0.18)
    parser.add_argument("--voice-volume", type=float, default=1.0)
    parser.add_argument("--fade", type=float, default=1.5)
    args = parser.parse_args()

    video, bgm, output = Path(args.video), Path(args.bgm), Path(args.output)
    for path in (video, bgm):
        if not path.is_file():
            print(f"ERROR: missing input: {path}", file=sys.stderr)
            return 2
    try:
        length = duration(video)
        fade_out = max(length - args.fade, 0)
        filters = (
            f"[0:a]volume={args.voice_volume}[voice];"
            f"[1:a]volume={args.bgm_volume},afade=t=in:st=0:d={args.fade},"
            f"afade=t=out:st={fade_out:.3f}:d={args.fade}[bgm];"
            "[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        run([
            "ffmpeg", "-y", "-i", str(video), "-stream_loop", "-1", "-i", str(bgm),
            "-filter_complex", filters, "-map", "0:v:0", "-map", "[aout]", "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-t", f"{length:.3f}", "-movflags", "+faststart", str(output),
        ])
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Created final video with BGM: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
