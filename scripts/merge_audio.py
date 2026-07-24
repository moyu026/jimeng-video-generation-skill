#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

AUDIO_RE = re.compile(r"^audio(\d+)\.mp3$", re.I)


def main() -> int:
    parser = argparse.ArgumentParser(description="Concatenate audio0.mp3...audioN.mp3; exclude bgm.mp3.")
    parser.add_argument("--audio-dir", default="materials/MP3")
    parser.add_argument("--output", default="materials/output/narration.mp3")
    args = parser.parse_args()

    audio_dir = Path(args.audio_dir)
    numbered = []
    for path in audio_dir.iterdir() if audio_dir.is_dir() else []:
        match = AUDIO_RE.fullmatch(path.name)
        if match:
            numbered.append((int(match.group(1)), path.resolve()))
    numbered.sort()
    numbers = [number for number, _ in numbered]
    if not numbers or numbers != list(range(numbers[-1] + 1)):
        print(f"ERROR: audio files must be continuous from audio0; found {numbers}", file=sys.stderr)
        return 2

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    list_file = output.parent / "audio_list.txt"
    list_file.write_text("\n".join(f"file '{str(path).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'" for _, path in numbered), encoding="utf-8")
    result = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-vn", "-c:a", "libmp3lame", "-q:a", "2", str(output),
    ])
    if result.returncode:
        return result.returncode
    print(f"Created narration audio: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
