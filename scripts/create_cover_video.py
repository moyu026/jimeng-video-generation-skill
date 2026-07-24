#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "command failed")
    return result.stdout.strip()


def duration(path: Path) -> float:
    value = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)])
    return float(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create S00 by looping a cover image for audio0 duration.")
    parser.add_argument("--image", required=True)
    parser.add_argument("--audio", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--fps", type=int, default=30)
    args = parser.parse_args()

    image, audio, output = Path(args.image), Path(args.audio), Path(args.output)
    for path in (image, audio):
        if not path.is_file():
            print(f"ERROR: missing input: {path}", file=sys.stderr)
            return 2
    try:
        target_duration = duration(audio)
    except Exception as exc:
        print(f"ERROR: cannot read audio duration: {exc}", file=sys.stderr)
        return 2
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(image), "-t", f"{target_duration:.3f}",
        "-vf", f"fps={args.fps},scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
        "-an", "-c:v", "libx264", "-movflags", "+faststart", str(output),
    ]
    try:
        run(command)
    except Exception as exc:
        print(f"ERROR: ffmpeg failed: {exc}", file=sys.stderr)
        return 1
    print(f"Created cover segment: {output} ({target_duration:.3f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
