#!/usr/bin/env python3
"""Create a video project from the bundled templates without overwriting files."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


DIRECTORIES = (
    "assets/jimeng",
    "assets/html",
    "assets/recordings",
    "assets/covers",
    "assets/original",
    "subtitles",
    "materials/MP4",
    "materials/MP3",
    "materials/video_output",
    "materials/output",
)

ROOT_TEMPLATES = (
    "video-plan.md",
    "narration.md",
    "shot-list.md",
    "asset-manifest.md",
    "edit-guide.md",
)


def copy_if_missing(source: Path, destination: Path) -> None:
    if not destination.exists():
        shutil.copy2(source, destination)


def scaffold(target: Path) -> None:
    skill_dir = Path(__file__).resolve().parent.parent
    template_dir = skill_dir / "templates"

    for relative in DIRECTORIES:
        (target / relative).mkdir(parents=True, exist_ok=True)

    (target / "article.md").touch(exist_ok=True)
    for name in ROOT_TEMPLATES:
        copy_if_missing(template_dir / name, target / name)
    copy_if_missing(
        template_dir / "html-diagram-template.html",
        target / "assets/html/html-diagram-template.html",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a Jimeng video project without overwriting existing files."
    )
    parser.add_argument("target", type=Path, help="Project directory, for example output/my-video")
    args = parser.parse_args()

    scaffold(args.target)
    print(f"Created Jimeng video project at: {args.target}")
    print("Place user materials:")
    print(f"- documents, images, diagrams, source videos: {args.target / 'assets/original'}")
    print(f"- audio0...audioN and bgm.mp3: {args.target / 'materials/MP3'}")
    print(f"- final outro as SNN.mp4: {args.target / 'materials/MP4'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
