#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import shutil
import sys
from pathlib import Path


def browser_available() -> bool:
    candidates = [
        shutil.which("chrome"),
        shutil.which("msedge"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ]
    return any(item and Path(item).exists() for item in candidates)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Jimeng video workflow environment.")
    parser.add_argument("--require-jimeng", action="store_true", help="Require the dreamina (Jimeng) CLI command.")
    parser.add_argument("--require-browser", action="store_true", help="Require Chrome or Edge for HTML recording.")
    args = parser.parse_args()

    checks = [
        ("Python 3.10+", sys.version_info >= (3, 10), f"current: {sys.version.split()[0]}"),
        ("ffmpeg", shutil.which("ffmpeg") is not None, "install FFmpeg and add its bin directory to PATH"),
        ("ffprobe", shutil.which("ffprobe") is not None, "installed with FFmpeg; add its bin directory to PATH"),
        ("whisper", shutil.which("whisper") is not None, "run: python -m pip install -r requirements.txt"),
        ("Pillow", importlib.util.find_spec("PIL") is not None, "run: python -m pip install -r requirements.txt"),
    ]
    if args.require_jimeng:
        checks.append(("dreamina CLI (Jimeng)", shutil.which("dreamina") is not None, "install/configure the dreamina CLI (Jimeng) and authentication; command name is `dreamina`"))
    if args.require_browser:
        checks.append(("Chrome/Edge", browser_available(), "install Chrome or Edge, or pass an explicit browser path"))

    failed = []
    for name, ok, advice in checks:
        suffix = "" if ok else f" - {advice}"
        print(f"[{'OK' if ok else 'MISSING'}] {name}{suffix}")
        if not ok:
            failed.append(name)

    if failed:
        print("Environment check failed: " + ", ".join(failed), file=sys.stderr)
        return 1
    print("Environment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
