#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

VIDEO_RE = re.compile(r"^S(\d+)$", re.I)
AUDIO_RE = re.compile(r"^audio(\d+)$", re.I)


def run(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "command failed")
    return result.stdout.strip()


def collect(folder: Path, pattern: re.Pattern[str], extensions: set[str]) -> dict[int, Path]:
    result: dict[int, Path] = {}
    for path in folder.iterdir() if folder.is_dir() else []:
        match = pattern.fullmatch(path.stem)
        if path.suffix.lower() not in extensions or not match:
            continue
        number = int(match.group(1))
        if number in result:
            raise ValueError(f"duplicate segment number {number}")
        result[number] = path
    return result


def video_size(path: Path) -> tuple[int, int]:
    data = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", str(path)]))
    stream = data.get("streams", [])[0]
    return int(stream["width"]), int(stream["height"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Combine SNN videos with audioN and concatenate them.")
    parser.add_argument("--video-dir", default="materials/video_output")
    parser.add_argument("--audio-dir", default="materials/MP3")
    parser.add_argument("--output", default="materials/output/final_voice.mp4")
    parser.add_argument("--fps", type=int, default=30)
    args = parser.parse_args()

    try:
        videos = collect(Path(args.video_dir), VIDEO_RE, {".mp4", ".mov", ".mkv"})
        audios = collect(Path(args.audio_dir), AUDIO_RE, {".mp3", ".wav", ".m4a", ".aac"})
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

    output = Path(args.output)
    temp_dir = output.parent / "temp_segments"
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    segments: list[Path] = []
    try:
        width, height = video_size(videos[0])
        for number in numbers:
            segment = temp_dir / f"segment{number:03d}.mp4"
            vf = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={args.fps},format=yuv420p"
            run([
                "ffmpeg", "-y", "-i", str(videos[number]), "-i", str(audios[number]),
                "-vf", vf, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-crf", "18",
                "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k", "-shortest", str(segment),
            ])
            segments.append(segment)
        concat_list = temp_dir / "concat_list.txt"
        concat_list.write_text("\n".join(f"file '{path.name}'" for path in segments), encoding="utf-8")
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", "-movflags", "+faststart", str(output)])
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Created voice video: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
