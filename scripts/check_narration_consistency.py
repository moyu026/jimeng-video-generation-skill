#!/usr/bin/env python3
"""Check narration consistency between narration.md and shot-list.md.

Rules enforced:
1. The concatenation of narration.md shot mapping voiceover text, in Shot ID order,
   must equal 配音总稿 after removing whitespace.
2. shot-list.md 配音文案 for each Shot ID must equal narration.md mapping text.

This script is intentionally lightweight and markdown-table based. It is a helper
for the Skill workflow; it does not replace human review.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SHOT_ID_RE = re.compile(r"^S\d+", re.I)


def normalize_text(text: str) -> str:
    """Normalize only layout whitespace, not wording."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"\s+", "", text)
    return text


def strip_cell(cell: str) -> str:
    return cell.strip().replace("<br>", "").replace("<br/>", "").replace("<br />", "")


def split_md_row(line: str) -> list[str]:
    line = line.strip()
    if not (line.startswith("|") and line.endswith("|")):
        return []
    # Lightweight parser: expected generated files should not use literal pipes in cells.
    return [strip_cell(c) for c in line.strip("|").split("|")]


def extract_section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.M)
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Missing section: ## {heading}")
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.M)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def extract_table_rows(section: str) -> list[dict[str, str]]:
    lines = [line for line in section.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return []
    header = split_md_row(lines[0])
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = split_md_row(line)
        if not cells or len(cells) < len(header):
            continue
        row = dict(zip(header, cells))
        if row.get("Shot ID") or row.get("配音文案"):
            rows.append(row)
    return rows


def load_narration(path: Path) -> tuple[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    total = extract_section(text, "配音总稿")
    mapping_section = extract_section(text, "分镜配音映射")
    rows = extract_table_rows(mapping_section)
    mapping: dict[str, str] = {}
    for row in rows:
        sid = row.get("Shot ID", "").strip()
        voice = row.get("配音文案", "").strip()
        if not sid or not SHOT_ID_RE.match(sid):
            continue
        if voice == "无配音":
            continue
        mapping[sid] = voice
    return total, mapping


def load_shot_list(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    section = extract_section(text, "分镜总表")
    rows = extract_table_rows(section)
    mapping: dict[str, str] = {}
    for row in rows:
        sid = row.get("Shot ID", "").strip()
        voice = row.get("配音文案", "").strip()
        if not sid or not SHOT_ID_RE.match(sid):
            continue
        if voice == "无配音":
            continue
        mapping[sid] = voice
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser(description="Check narration total/mapping/shot-list voiceover consistency.")
    parser.add_argument("--narration", default="narration.md", help="Path to narration.md")
    parser.add_argument("--shot-list", default="shot-list.md", help="Path to shot-list.md")
    args = parser.parse_args()

    narration_path = Path(args.narration)
    shot_list_path = Path(args.shot_list)

    errors: list[str] = []
    try:
        total, narration_map = load_narration(narration_path)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse {narration_path}: {exc}", file=sys.stderr)
        return 2

    try:
        shot_map = load_shot_list(shot_list_path)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot parse {shot_list_path}: {exc}", file=sys.stderr)
        return 2

    joined = "".join(narration_map[sid] for sid in narration_map.keys())
    if normalize_text(joined) != normalize_text(total):
        errors.append(
            "narration.md mismatch: concatenated shot mapping does not equal 配音总稿 after whitespace normalization."
        )

    for sid, voice in narration_map.items():
        if sid not in shot_map:
            errors.append(f"shot-list.md missing Shot ID from narration mapping: {sid}")
            continue
        if normalize_text(shot_map[sid]) != normalize_text(voice):
            errors.append(f"shot-list.md voiceover mismatch for {sid}")

    for sid in shot_map.keys():
        if sid not in narration_map:
            errors.append(f"shot-list.md has voiceover but narration.md mapping is missing: {sid}")

    if errors:
        print("Narration consistency check FAILED:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Narration consistency check passed.")
    print(f"Checked {len(narration_map)} voiced shots.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
