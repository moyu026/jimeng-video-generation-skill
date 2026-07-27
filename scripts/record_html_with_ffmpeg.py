#!/usr/bin/env python3
"""Record a fullscreen HTML diagram on Windows.

The HTML declares its animation length with data-animation-duration. The actual
recording always lasts animation_duration + 1 second.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import pathname2url

DEFAULT_CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
FORMATS = {
    "landscape": (0, 0, 1920, 1080, 1920, 1080),
    "portrait": (497, 0, 926, 1080, 1080, 1260),
}
ANIMATION_DURATION_RE = re.compile(r"data-animation-duration\s*=\s*['\"]([0-9]+(?:\.[0-9]+)?)['\"]", re.I)


def file_url(path: Path, orientation: str) -> str:
    return urljoin("file:", pathname2url(str(path.resolve()))) + f"?record=1&orientation={orientation}"


def animation_duration_from_html(path: Path) -> float | None:
    match = ANIMATION_DURATION_RE.search(path.read_text(encoding="utf-8"))
    return float(match.group(1)) if match else None


def recording_duration(animation_duration: float) -> float:
    if animation_duration <= 0:
        raise ValueError("animation duration must be positive")
    return animation_duration + 1.0

def hide_window() -> subprocess.STARTUPINFO:
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    return startup


def launch_chrome(chrome: str, url: str, profile: str) -> subprocess.Popen:
    return subprocess.Popen([
        chrome,
        f"--user-data-dir={profile}",
        "--new-window",
        "--kiosk",
        f"--app={url}",
        "--disable-extensions",
        "--no-first-run",
        "--no-default-browser-check",
    ])


def send_r_to_chrome() -> None:
    script = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "Add-Type @'\n"
        "using System;\n"
        "using System.Runtime.InteropServices;\n"
        "public class Win32 { [DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr h); }\n"
        "'@;"
        "$w=(Get-Process chrome -ErrorAction SilentlyContinue|Sort-Object StartTime -Descending|Select-Object -First 1).MainWindowHandle;"
        "if($w -and $w -ne 0){[void][Win32]::SetForegroundWindow($w);Start-Sleep -Milliseconds 150;"
        "[System.Windows.Forms.SendKeys]::SendWait('r')}"
    )
    subprocess.run(["powershell.exe", "-NoProfile", "-Command", script], capture_output=True, text=True)


def record_blocking(ffmpeg: str, output: Path, record_duration: float, fps: int, encoder: str, orientation: str) -> int:
    offset_x, offset_y, capture_width, capture_height, output_width, output_height = FORMATS[orientation]
    command = [
        ffmpeg, "-y", "-f", "gdigrab", "-framerate", str(fps),
        "-offset_x", str(offset_x), "-offset_y", str(offset_y),
        "-video_size", f"{capture_width}x{capture_height}",
        "-i", "desktop", "-t", str(record_duration), "-an",
        "-vf", f"scale={output_width}:{output_height},setsar=1",
        "-c:v", encoder, "-pix_fmt", "yuv420p",
    ]
    command += ["-preset", "veryfast", "-global_quality", "18"] if encoder == "h264_qsv" else ["-b:v", "8M"]
    command.append(str(output))
    print("ffmpeg:", " ".join(command))
    process = subprocess.Popen(command, startupinfo=hide_window(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.5)
    send_r_to_chrome()
    _, stderr = process.communicate()
    if process.returncode:
        print(stderr[-800:], file=sys.stderr)
    return process.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Fullscreen-record HTML for animation duration + 1 second.")
    parser.add_argument("html")
    parser.add_argument("-o", "--output")
    parser.add_argument("-d", "--duration", type=float, help="Animation duration in seconds; recording automatically adds 1 second.")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--orientation", choices=FORMATS, default="landscape")
    parser.add_argument("--encoder", default="h264_qsv", choices=["h264_qsv", "h264_mf"])
    parser.add_argument("--chrome", default=DEFAULT_CHROME)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--hold", type=float, default=0.0)
    args = parser.parse_args()

    html = Path(args.html)
    if not html.is_file():
        print(f"ERROR: HTML not found: {html}", file=sys.stderr)
        return 2
    if not args.no_browser and not Path(args.chrome).is_file():
        print(f"ERROR: Chrome not found: {args.chrome}", file=sys.stderr)
        return 2

    animation_duration = args.duration if args.duration is not None else animation_duration_from_html(html)
    if animation_duration is None:
        print("ERROR: set data-animation-duration on .stage or pass --duration.", file=sys.stderr)
        return 2
    try:
        record_duration = recording_duration(animation_duration)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    output = Path(args.output) if args.output else html.parents[1] / "recordings" / f"{html.stem}.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    print(f"animation duration: {animation_duration:.3f}s")
    print(f"recording duration: {record_duration:.3f}s (animation + 1s)")

    browser = None
    try:
        if not args.no_browser:
            profile = str(html.parents[1] / "_chrome_profile")
            url = file_url(html, args.orientation)
            print(f"opening fullscreen: {url}")
            browser = launch_chrome(args.chrome, url, profile)
            time.sleep(2.0)
        if args.hold:
            time.sleep(args.hold)
        result = record_blocking("ffmpeg", output, record_duration, args.fps, args.encoder, args.orientation)
        if result and args.encoder == "h264_qsv":
            print("qsv failed, retrying with h264_mf...")
            result = record_blocking("ffmpeg", output, record_duration, args.fps, "h264_mf", args.orientation)
    finally:
        if browser:
            browser.terminate()

    print("done:", output, output.exists(), output.stat().st_size if output.exists() else 0)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
