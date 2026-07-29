#!/usr/bin/env python3
"""Create a branded 1080x1260 video from a background image and a source video."""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = (1080, 1260)
PANEL = (42, 294, 1038, 860)
FONT_REGULAR = Path(r"C:\Windows\Fonts\msyh.ttc")
FONT_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")


def run(command: list[str], capture: bool = False) -> str:
    result = subprocess.run(
        command,
        check=True,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    return result.stdout.strip() if capture else ""


def probe_video(path: Path) -> tuple[int, int, float, bool]:
    raw = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=index,codec_type,width,height,duration:format=duration",
            "-of",
            "json",
            str(path),
        ],
        capture=True,
    )
    data = json.loads(raw)
    streams = data.get("streams", [])
    video = next(stream for stream in streams if stream.get("codec_type") == "video")
    duration = video.get("duration") or data.get("format", {}).get("duration")
    if duration is None:
        raise ValueError(f"Cannot determine video duration: {path}")
    has_audio = any(stream.get("codec_type") == "audio" for stream in streams)
    return int(video["width"]), int(video["height"]), float(duration), has_audio


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.is_file():
        raise FileNotFoundError(f"Missing font: {path}")
    return ImageFont.truetype(str(path), size=size)


def centered_x(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.FreeTypeFont) -> float:
    bounds = draw.textbbox((0, 0), text, font=text_font)
    return (CANVAS_SIZE[0] - (bounds[2] - bounds[0])) / 2 - bounds[0]


def draw_centered(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
) -> None:
    bounds = draw.textbbox((0, 0), text, font=text_font)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    x = box[0] + (box[2] - box[0] - width) / 2 - bounds[0]
    y = box[1] + (box[3] - box[1] - height) / 2 - bounds[1]
    draw.text((x, y), text, font=text_font, fill=fill)


def create_frame(
    background_path: Path,
    logo_path: Path,
    title: str,
    subtitle: str,
    keywords: list[str],
    theme: str,
    output_path: Path,
) -> None:
    canvas = Image.open(background_path).convert("RGBA").resize(
        CANVAS_SIZE, Image.Resampling.LANCZOS
    )
    overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if theme == "light":
        title_color = (42, 49, 60, 255)
        subtitle_color = (88, 101, 119, 255)
        accent_color = (70, 78, 90, 255)
        muted_color = (105, 116, 132, 235)
        shadow = (255, 255, 255, 175)
        keyword_fill = (248, 247, 244, 235)
        keyword_outline = (150, 153, 158, 205)
        divider_color = (132, 136, 143, 155)
        footer_color = (64, 72, 84, 235)
    else:
        title_color = (247, 249, 253, 255)
        subtitle_color = (178, 196, 218, 255)
        accent_color = (232, 224, 205, 255)
        muted_color = (160, 181, 205, 230)
        shadow = (0, 0, 0, 150)
        keyword_fill = (12, 22, 39, 220)
        keyword_outline = (174, 185, 199, 190)
        divider_color = (205, 211, 220, 175)
        footer_color = (219, 227, 238, 235)

    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((62, 62), Image.Resampling.LANCZOS)
    overlay.alpha_composite(logo, (48, 34))

    brand_font = load_font(FONT_BOLD, 31)
    title_font = load_font(FONT_BOLD, 54)
    subtitle_font = load_font(FONT_REGULAR, 27)
    keyword_font = load_font(FONT_REGULAR, 21)
    footer_font = load_font(FONT_REGULAR, 20)
    mark_font = load_font(FONT_BOLD, 22)

    draw.text((124, 49), "openJiuwen", font=brand_font, fill=shadow)
    draw.text((124, 47), "openJiuwen", font=brand_font, fill=title_color)

    title_x = centered_x(draw, title, title_font)
    draw.text((title_x, 116), title, font=title_font, fill=shadow)
    draw.text((title_x, 113), title, font=title_font, fill=title_color)

    subtitle_x = centered_x(draw, subtitle, subtitle_font)
    draw.text((subtitle_x, 182), subtitle, font=subtitle_font, fill=subtitle_color)

    shown_keywords = keywords[:4]
    if shown_keywords:
        top = 226
        area_left = 50
        area_right = 1030
        gap = 18
        box_width = (
            area_right - area_left - gap * (len(shown_keywords) - 1)
        ) / len(shown_keywords)
        for index, keyword in enumerate(shown_keywords):
            x = area_left + index * (box_width + gap)
            box = (int(x), top, int(x + box_width), top + 40)
            draw.rounded_rectangle(
                box,
                radius=20,
                fill=keyword_fill,
                outline=keyword_outline,
                width=1,
            )
            draw_centered(draw, box, keyword, keyword_font, accent_color)

    draw.line((50, 280, 1030, 280), fill=divider_color, width=2)

    footer_y = 1190
    footer = "Human in the Swarm"
    mark = "JiuwenSwarm"
    mark_bounds = draw.textbbox((0, 0), mark, font=mark_font)
    mark_width = mark_bounds[2] - mark_bounds[0]
    draw.text((50, footer_y + 2), footer, font=footer_font, fill=shadow)
    draw.text((50, footer_y), footer, font=footer_font, fill=muted_color)
    draw.text((1030 - mark_width, footer_y), mark, font=mark_font, fill=footer_color)

    canvas.alpha_composite(overlay)
    canvas.convert("RGB").save(output_path, quality=95, optimize=True)


def fit_size(source_width: int, source_height: int) -> tuple[int, int]:
    left, top, right, bottom = PANEL
    max_width = right - left
    max_height = bottom - top
    scale = min(max_width / source_width, max_height / source_height)
    width = max(2, int(source_width * scale) // 2 * 2)
    height = max(2, int(source_height * scale) // 2 * 2)
    return width, height


def create_rounded_mask(width: int, height: int, radius: int, output_path: Path) -> None:
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, width - 1, height - 1),
        radius=radius,
        fill=255,
    )
    mask.save(output_path)


def compose_video(
    frame_path: Path,
    video_path: Path,
    mask_path: Path,
    output_path: Path,
    fps: int,
    crf: int,
    preset: str,
    radius: int,
) -> None:
    source_width, source_height, duration, has_audio = probe_video(video_path)
    width, height = fit_size(source_width, source_height)
    left, top, right, bottom = PANEL
    x = left + ((right - left) - width) // 2
    y = top + ((bottom - top) - height) // 2
    create_rounded_mask(width, height, radius, mask_path)

    filters = (
        f"[1:v]scale={width}:{height}:flags=lanczos,format=rgba[shot];"
        "[2:v]format=gray[mask];"
        "[shot][mask]alphamerge[rounded];"
        f"[0:v][rounded]overlay={x}:{y}:format=auto[v]"
    )

    command = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(frame_path),
        "-i",
        str(video_path),
        "-loop",
        "1",
        "-i",
        str(mask_path),
        "-filter_complex",
        filters,
        "-map",
        "[v]",
    ]
    if has_audio:
        command.extend(["-map", "1:a:0", "-c:a", "aac", "-b:a", "192k"])
    command.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(fps),
            "-t",
            f"{duration:.6f}",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    )
    run(command)
    print(f"Embedded video: {width}x{height} at ({x},{y})")
    print(f"Duration: {duration:.6f}s; audio: {'kept' if has_audio else 'none'}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add branded background text and embed a rounded source video."
    )
    parser.add_argument("--background", required=True, help="Background image path")
    parser.add_argument("--logo", required=True, help="Logo image path")
    parser.add_argument("--video", required=True, help="Source video path")
    parser.add_argument("--output", required=True, help="Output MP4 path")
    parser.add_argument("--title", required=True, help="Main title")
    parser.add_argument("--subtitle", required=True, help="Subtitle")
    parser.add_argument(
        "--keywords",
        nargs="+",
        required=True,
        help="Up to four keyword labels",
    )
    parser.add_argument("--theme", choices=["light", "dark"], default="light")
    parser.add_argument("--radius", type=int, default=30, help="Video corner radius")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--crf", type=int, default=18)
    parser.add_argument("--preset", default="medium")
    parser.add_argument(
        "--keep-assets",
        action="store_true",
        help="Save generated frame and mask beside the output video",
    )
    args = parser.parse_args()

    background = Path(args.background).resolve()
    logo = Path(args.logo).resolve()
    video = Path(args.video).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    for path in (background, logo, video):
        if not path.is_file():
            parser.error(f"Input does not exist: {path}")
    if output == video:
        parser.error("Output must not overwrite the source video directly")

    if args.keep_assets:
        frame_path = output.with_name(f"{output.stem}-frame.png")
        mask_path = output.with_name(f"{output.stem}-mask.png")
        create_frame(
            background,
            logo,
            args.title,
            args.subtitle,
            args.keywords,
            args.theme,
            frame_path,
        )
        compose_video(
            frame_path,
            video,
            mask_path,
            output,
            args.fps,
            args.crf,
            args.preset,
            args.radius,
        )
    else:
        with tempfile.TemporaryDirectory(prefix="branded-video-") as temp:
            temp_dir = Path(temp)
            frame_path = temp_dir / "frame.png"
            mask_path = temp_dir / "mask.png"
            create_frame(
                background,
                logo,
                args.title,
                args.subtitle,
                args.keywords,
                args.theme,
                frame_path,
            )
            compose_video(
                frame_path,
                video,
                mask_path,
                output,
                args.fps,
                args.crf,
                args.preset,
                args.radius,
            )

    print(f"Created: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
