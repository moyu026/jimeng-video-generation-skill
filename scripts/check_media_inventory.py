#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from check_narration_consistency import extract_section, extract_table_rows

SHOT_RE = re.compile(r"^S(\d+)$", re.I)
AUDIO_RE = re.compile(r"^audio(\d+)$", re.I)
VIDEO_EXTS = {".mp4", ".mov", ".mkv"}


def collect(folder: Path, pattern: re.Pattern[str], extensions: set[str]) -> dict[int, Path]:
    result: dict[int, Path] = {}
    if not folder.is_dir():
        return result
    for path in folder.iterdir():
        if path.suffix.lower() not in extensions:
            continue
        match = pattern.fullmatch(path.stem)
        if not match:
            continue
        number = int(match.group(1))
        if number in result:
            raise ValueError(f"duplicate number {number}: {result[number]} and {path}")
        result[number] = path
    return result


def shot_rows(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    return extract_table_rows(extract_section(text, "分镜总表"))


def continuous(numbers: set[int]) -> bool:
    return bool(numbers) and numbers == set(range(max(numbers) + 1))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SNN/audioN pairing, cover, outro, and BGM.")
    parser.add_argument("--shot-list", default="shot-list.md")
    parser.add_argument("--video-dir", default="materials/MP4")
    parser.add_argument("--audio-dir", default="materials/MP3")
    args = parser.parse_args()

    errors: list[str] = []
    try:
        rows = shot_rows(Path(args.shot_list))
        shot_ids = [row.get("Shot ID", "").strip() for row in rows]
        shot_numbers = [int(match.group(1)) for sid in shot_ids if (match := SHOT_RE.fullmatch(sid))]
        if len(shot_numbers) != len(rows):
            errors.append("shot-list contains an invalid or missing Shot ID")
        if len(set(shot_numbers)) != len(shot_numbers):
            errors.append("shot-list contains duplicate Shot IDs")
        if shot_numbers and shot_numbers != list(range(max(shot_numbers) + 1)):
            errors.append("shot-list Shot IDs must be ordered and continuous from S00")
        if rows and rows[0].get("素材类型", "").strip() != "cover-still":
            errors.append("S00 must use material type cover-still")
        if rows and rows[-1].get("素材类型", "").strip() != "user-provided-outro":
            errors.append("the last shot must use material type user-provided-outro")
    except Exception as exc:
        errors.append(f"cannot parse shot-list: {exc}")
        shot_numbers = []

    try:
        videos = collect(Path(args.video_dir), SHOT_RE, VIDEO_EXTS)
        audios = collect(Path(args.audio_dir), AUDIO_RE, {".mp3"})
    except ValueError as exc:
        errors.append(str(exc))
        videos, audios = {}, {}

    video_numbers = set(videos)
    audio_numbers = set(audios)
    planned_numbers = set(shot_numbers)
    if not continuous(video_numbers):
        errors.append("video files must be continuous from S00")
    if not continuous(audio_numbers):
        errors.append("audio files must be continuous from audio0")
    if video_numbers != audio_numbers:
        errors.append(f"video/audio number mismatch: videos={sorted(video_numbers)}, audios={sorted(audio_numbers)}")
    if planned_numbers and video_numbers != planned_numbers:
        errors.append(f"media files do not match shot-list: planned={sorted(planned_numbers)}, videos={sorted(video_numbers)}")
    if not (Path(args.audio_dir) / "bgm.mp3").is_file():
        errors.append("missing materials/MP3/bgm.mp3")

    if errors:
        print("Media inventory check FAILED:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    print(f"Media inventory check passed: {len(video_numbers)} paired segments (S00-S{max(video_numbers):02d}) + bgm.mp3.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
