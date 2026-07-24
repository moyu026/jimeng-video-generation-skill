#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

from check_narration_consistency import load_narration

OUTRO = "openJiuwen开源社区致力于打造精准、易用、高效的生产级AI Agent。欢迎大家持续关注公众号后台回复开源加入开发交流群，解锁更多实用的智能体案例与前沿技术干货."
TIMECODE_RE = re.compile(r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2}),(\d{3})$")


def normalize(text: str) -> str:
    return "".join(char.lower() for char in text if char.isalnum())


def srt_text(path: Path) -> tuple[str, list[str]]:
    blocks = re.split(r"\r?\n\s*\r?\n", path.read_text(encoding="utf-8-sig").strip())
    cues: list[str] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if lines[0].isdigit():
            lines = lines[1:]
        if lines and TIMECODE_RE.fullmatch(lines[0]):
            lines = lines[1:]
        if lines:
            cues.append("".join(lines))
    return "".join(cues), cues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SRT text against narration and fixed outro.")
    parser.add_argument("--narration", default="narration.md")
    parser.add_argument("--srt", default="subtitles/subtitles.srt")
    parser.add_argument("--threshold", type=float, default=0.98)
    args = parser.parse_args()

    try:
        _, mapping = load_narration(Path(args.narration))
        expected = "".join(mapping[sid] for sid in sorted(mapping, key=lambda value: int(value[1:])))
        actual, cues = srt_text(Path(args.srt))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    expected_normalized = normalize(expected)
    actual_normalized = normalize(actual)
    ratio = SequenceMatcher(None, expected_normalized, actual_normalized).ratio()
    errors = []
    if ratio < args.threshold:
        errors.append(f"text similarity {ratio:.3f} is below {args.threshold:.3f}")
    if not re.sub(r"\s+", "", actual).endswith(re.sub(r"\s+", "", OUTRO)):
        errors.append("SRT does not end with the fixed outro text")
    if not re.sub(r"\s+", "", expected).endswith(re.sub(r"\s+", "", OUTRO)):
        errors.append("narration does not end with the fixed outro text")
    if not cues:
        errors.append("SRT has no subtitle cues")

    if errors:
        print("Subtitle validation FAILED:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    print(f"Subtitle validation passed: similarity={ratio:.3f}, cues={len(cues)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
