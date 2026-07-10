#!/usr/bin/env python3
"""Record an approved HTML diagram with Chrome/Edge + ffmpeg on Windows.

This script intentionally stays semi-automatic:
1. It opens the HTML in browser recording mode (?record=1).
2. The human checks the fullscreen/window state.
3. After Enter, ffmpeg records the desktop for a fixed duration.
4. The human presses R immediately after recording starts to replay animation.

Why semi-automatic: Windows window capture, DPI scaling, browser focus, and animation
restart are more reliable with one human checkpoint than with brittle UI automation.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import pathname2url


def file_url(path: Path, record: bool = True) -> str:
    url = urljoin("file:", pathname2url(str(path.resolve())))
    return url + ("?record=1" if record else "")


def find_browser(explicit: str | None = None) -> str | None:
    candidates = []
    if explicit:
        candidates.append(explicit)
    candidates.extend(
        [
            shutil.which("chrome"),
            shutil.which("msedge"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
    )
    for item in candidates:
        if item and Path(item).exists():
            return item
    return None


def find_ffmpeg(explicit: str | None = None) -> str | None:
    candidates = []
    if explicit:
        candidates.append(explicit)
    candidates.extend([shutil.which("ffmpeg"), r"D:\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"])
    for item in candidates:
        if item and Path(item).exists():
            return item
    return None


def open_browser(browser: str | None, url: str, app_mode: bool) -> subprocess.Popen | None:
    if browser:
        args = [browser]
        if app_mode:
            args.extend([f"--app={url}"])
        else:
            args.append(url)
        return subprocess.Popen(args)
    webbrowser.open(url)
    return None


def build_ffmpeg_cmd(ffmpeg: str, output: Path, duration: float, fps: int, offset_x: int | None, offset_y: int | None, width: int | None, height: int | None) -> list[str]:
    input_name = "desktop"
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "gdigrab",
        "-framerate",
        str(fps),
    ]
    if offset_x is not None:
        cmd.extend(["-offset_x", str(offset_x)])
    if offset_y is not None:
        cmd.extend(["-offset_y", str(offset_y)])
    if width is not None and height is not None:
        cmd.extend(["-video_size", f"{width}x{height}"])
    cmd.extend(
        [
            "-i",
            input_name,
            "-t",
            str(duration),
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            str(output),
        ]
    )
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(description="Record HTML diagram via browser + ffmpeg gdigrab on Windows.")
    parser.add_argument("html", help="Path to assets/html/<diagram-id>.html")
    parser.add_argument("-o", "--output", help="Output mp4 path. Default: assets/recordings/<diagram-id>.mp4")
    parser.add_argument("-d", "--duration", type=float, default=8.0, help="Recording duration in seconds. Default: 8")
    parser.add_argument("--fps", type=int, default=30, help="Recording fps. Default: 30")
    parser.add_argument("--browser", help="Browser executable path. Auto-detect Chrome/Edge by default.")
    parser.add_argument("--ffmpeg", help="ffmpeg executable path. Auto-detect by default.")
    parser.add_argument("--no-app", action="store_true", help="Open normal browser tab instead of app window.")
    parser.add_argument("--offset-x", type=int, help="gdigrab crop offset x")
    parser.add_argument("--offset-y", type=int, help="gdigrab crop offset y")
    parser.add_argument("--width", type=int, help="gdigrab crop width, e.g. 1920")
    parser.add_argument("--height", type=int, help="gdigrab crop height, e.g. 1080")
    parser.add_argument("--skip-browser", action="store_true", help="Do not open browser; only record current screen after confirmation.")
    args = parser.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        print(f"ERROR: HTML not found: {html_path}", file=sys.stderr)
        return 2

    output = Path(args.output) if args.output else html_path.parents[1] / "recordings" / f"{html_path.stem}.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg = find_ffmpeg(args.ffmpeg)
    if not ffmpeg:
        print("ERROR: ffmpeg not found. Install ffmpeg or pass --ffmpeg <path>.", file=sys.stderr)
        return 2

    browser = find_browser(args.browser)
    if not browser and not args.skip_browser:
        print("WARN: Chrome/Edge not found, falling back to default browser.")

    url = file_url(html_path, record=True)
    if not args.skip_browser:
        print(f"Opening browser: {browser or 'default'}")
        print(f"URL: {url}")
        open_browser(browser, url, app_mode=not args.no_app)
        time.sleep(1.0)

    print("\nBefore recording:")
    print("1. Make the browser/window fullscreen or ensure the target area is visible.")
    print("2. Confirm the HTML has passed human review: HTML Review: approved.")
    print("3. After pressing Enter here, ffmpeg starts recording.")
    print("4. Immediately press R in the browser to replay the animation from the beginning.\n")
    input("Press Enter to start ffmpeg recording...")

    cmd = build_ffmpeg_cmd(
        ffmpeg=ffmpeg,
        output=output,
        duration=args.duration,
        fps=args.fps,
        offset_x=args.offset_x,
        offset_y=args.offset_y,
        width=args.width,
        height=args.height,
    )

    print("Running:")
    print(" ".join(f'"{c}"' if " " in c else c for c in cmd))
    print("\nRecording now. Press R in the browser if you have not already.\n")
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        print("ERROR: ffmpeg recording failed.", file=sys.stderr)
        return proc.returncode

    print(f"Done: {output}")
    print("Next: replay the mp4 and update asset-manifest.md with path, duration, resolution, and status.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
