#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

VIDEO_RE = re.compile(r"^S(\d+)$", re.I)
AUDIO_RE = re.compile(r"^audio(\d+)$", re.I)
VIDEO_EXTS = {".mp4", ".mov", ".mkv"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac"}


def run(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "command failed")
    return result.stdout.strip()


def duration(path: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)]))


def collect(folder: Path, pattern: re.Pattern[str], extensions: set[str]) -> dict[int, Path]:
    result: dict[int, Path] = {}
    for path in folder.iterdir() if folder.is_dir() else []:
        match = pattern.fullmatch(path.stem)
        if path.suffix.lower() not in extensions or not match:
            continue
        number = int(match.group(1))
        if number in result:
            raise ValueError(f"duplicate number {number}: {result[number]} and {path}")
        result[number] = path
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Match SNN video durations to audioN durations.")
    parser.add_argument("--video-dir", default="materials/MP4")
    parser.add_argument("--audio-dir", default="materials/MP3")
    parser.add_argument("--output-dir", default="materials/video_output")
    args = parser.parse_args()

    try:
        videos = collect(Path(args.video_dir), VIDEO_RE, VIDEO_EXTS)
        audios = collect(Path(args.audio_dir), AUDIO_RE, AUDIO_EXTS)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not videos or set(videos) != set(audios):
        print(f"ERROR: SNN/audioN mismatch: videos={sorted(videos)}, audios={sorted(audios)}", file=sys.stderr)
        return 2
    numbers = sorted(videos)
    if numbers != list(range(numbers[-1] + 1)):
        print("ERROR: segment numbers must be continuous from 0", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        run(["ffmpeg", "-version"])
        run(["ffprobe", "-version"])
        for number in numbers:
            video_duration = duration(videos[number])
            audio_duration = duration(audios[number])
            if min(video_duration, audio_duration) <= 0:
                raise ValueError(f"invalid duration for segment {number}")
            factor = audio_duration / video_duration
            if factor < 0.5 or factor > 2.0:
                print(f"WARNING: S{number:02d} speed factor is {factor:.3f}; review the result.")
            output = output_dir / f"S{number:02d}.mp4"
            run([
                "ffmpeg", "-y", "-i", str(videos[number]),
                "-vf", f"setpts={factor:.8f}*PTS", "-t", f"{audio_duration:.3f}", "-an",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", str(output),
            ])
            print(f"S{number:02d}: {video_duration:.3f}s -> {audio_duration:.3f}s ({output})")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
