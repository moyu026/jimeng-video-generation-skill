#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SIZE_16X9 = (1920, 1080)
SIZE_1080X608 = (1080, 608)
SIZE_1080X1260 = (1080, 1260)

THEMES = {
    "dark": {
        "title": (245, 249, 255, 255),
        "subtitle": (174, 198, 222, 255),
        "muted": (105, 150, 185, 235),
        "accent": (61, 218, 255, 255),
        "badge_fill": (12, 39, 67, 225),
        "badge_outline": (54, 190, 238, 230),
        "panel": (0, 8, 20, 120),
        "shadow": (0, 0, 0, 160),
    },
    "light": {
        "title": (34, 61, 210, 255),
        "subtitle": (44, 72, 150, 245),
        "muted": (92, 116, 170, 230),
        "accent": (23, 196, 228, 255),
        "badge_fill": (236, 244, 255, 230),
        "badge_outline": (58, 128, 255, 220),
        "panel": (255, 255, 255, 130),
        "shadow": (255, 255, 255, 120),
    },
}

FONT_CANDIDATES = {
    "regular": [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\arial.ttf", "/System/Library/Fonts/PingFang.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "bold": [r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\arialbd.ttf", "/System/Library/Fonts/PingFang.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
}


def find_font(kind: str, explicit: str | None = None) -> str | None:
    candidates = []
    if explicit:
        candidates.append(explicit)
    candidates.extend(FONT_CANDIDATES[kind])
    for item in candidates:
        if item and Path(item).exists():
            return item
    return None


def load_font(kind: str, size: int, explicit: str | None = None) -> ImageFont.ImageFont:
    font_path = find_font(kind, explicit)
    if font_path:
        return ImageFont.truetype(font_path, size=size)
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    if not text:
        return 0, 0
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def fit_cover(image: Image.Image, size: tuple[int, int], focus_x: float = 0.5, focus_y: float = 0.5) -> Image.Image:
    image = image.convert("RGBA")
    src_w, src_h = image.size
    dst_w, dst_h = size
    scale = max(dst_w / src_w, dst_h / src_h)
    new_w, new_h = int(math.ceil(src_w * scale)), int(math.ceil(src_h * scale))
    resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    max_left = max(0, new_w - dst_w)
    max_top = max(0, new_h - dst_h)
    left = int(max_left * min(max(focus_x, 0.0), 1.0))
    top = int(max_top * min(max(focus_y, 0.0), 1.0))
    return resized.crop((left, top, left + dst_w, top + dst_h))


def draw_text_with_shadow(draw, xy, text, font, fill, shadow, shadow_offset=(0, 4)) -> None:
    if not text:
        return
    x, y = xy
    ox, oy = shadow_offset
    draw.text((x + ox, y + oy), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


def centered_text(draw, box, text, font, fill) -> None:
    left, top, right, bottom = box
    bounds = draw.textbbox((0, 0), text, font=font)
    tw, th = bounds[2] - bounds[0], bounds[3] - bounds[1]
    x = left + (right - left - tw) / 2 - bounds[0]
    y = top + (bottom - top - th) / 2 - bounds[1]
    draw.text((x, y), text, font=font, fill=fill)


def wrap_text(draw, text: str, font, max_width: int) -> list[str]:
    if not text:
        return []
    raw_lines = [part.strip() for part in text.replace("\n", "\n").split("\n") if part.strip()]
    lines: list[str] = []
    for raw in raw_lines:
        current = ""
        for ch in raw:
            candidate = current + ch
            if text_size(draw, candidate, font)[0] <= max_width or not current:
                current = candidate
            else:
                lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines


def add_gradient_panel(base: Image.Image, box, color, blur: int = 40) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(box, radius=36, fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def paste_logo(base: Image.Image, logo_path: Path | None, pos, max_size) -> tuple[int, int, int, int] | None:
    if not logo_path:
        return None
    if not logo_path.exists():
        raise FileNotFoundError(f"Logo not found: {logo_path}")
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail(max_size, Image.Resampling.LANCZOS)
    base.alpha_composite(logo, pos)
    x, y = pos
    return (x, y, x + logo.size[0], y + logo.size[1])


def draw_badge(draw, xy, text: str, font, theme, pad_x: int, pad_y: int):
    if not text:
        return None
    x, y = xy
    tw, th = text_size(draw, text, font)
    box = (x, y, x + tw + pad_x * 2, y + th + pad_y * 2)
    radius = max(14, (box[3] - box[1]) // 2)
    draw.rounded_rectangle(box, radius=radius, fill=theme["badge_fill"], outline=theme["badge_outline"], width=2)
    centered_text(draw, box, text, font, theme["accent"])
    return box


def draw_horizontal_cover(background: Image.Image, size, args, theme, output: Path, variant: str) -> None:
    w, h = size
    canvas = fit_cover(background, size, focus_x=args.focus_x, focus_y=args.focus_y)
    add_gradient_panel(canvas, (0, 0, int(w * 0.55), h), theme["panel"], blur=max(28, w // 45))
    draw = ImageDraw.Draw(canvas)

    margin_x = int(w * 0.058)
    top = int(h * 0.09)
    brand_font = load_font("bold", max(21, int(h * 0.036)), args.font_bold)
    badge_font = load_font("bold", max(17, int(h * 0.025)), args.font_bold)
    title_font = load_font("bold", max(46, int(h * (0.112 if variant == "16x9" else 0.108))), args.font_bold)
    title2_font = load_font("bold", max(50, int(h * (0.132 if variant == "16x9" else 0.126))), args.font_bold)
    subtitle_font = load_font("regular", max(21, int(h * 0.036)), args.font_regular)
    footer_font = load_font("regular", max(15, int(h * 0.025)), args.font_regular)

    logo_box = paste_logo(canvas, Path(args.logo) if args.logo else None, (margin_x, top), (int(h * 0.085), int(h * 0.085)))
    brand_x = margin_x if not logo_box else logo_box[2] + int(w * 0.018)
    if args.brand:
        draw_text_with_shadow(draw, (brand_x, top + int(h * 0.01)), args.brand, brand_font, theme["title"], theme["shadow"], (0, 2))
    badge_x = brand_x + (text_size(draw, args.brand, brand_font)[0] if args.brand else 0) + int(w * 0.035)
    if args.badge:
        draw_badge(draw, (badge_x, top + int(h * 0.005)), args.badge, badge_font, theme, int(w * 0.014), int(h * 0.012))

    title_y = int(h * 0.265)
    max_text_width = int(w * 0.47)
    if args.title_line1:
        draw_text_with_shadow(draw, (margin_x, title_y), args.title_line1, title_font, theme["title"], theme["shadow"])
    if args.title_line2:
        draw_text_with_shadow(draw, (margin_x, title_y + int(h * 0.12)), args.title_line2, title2_font, theme["title"], theme["shadow"])

    sub_y = int(h * 0.60)
    subtitle_lines: list[str] = []
    if args.subtitle:
        subtitle_lines.extend(wrap_text(draw, args.subtitle, subtitle_font, max_text_width))
    if args.subtitle2:
        subtitle_lines.extend(wrap_text(draw, args.subtitle2, subtitle_font, max_text_width))
    for idx, line in enumerate(subtitle_lines[:3]):
        draw_text_with_shadow(draw, (margin_x, sub_y + idx * int(h * 0.058)), line, subtitle_font, theme["subtitle"], theme["shadow"], (0, 2))
    if args.footer:
        draw.text((margin_x, int(h * 0.885)), args.footer, font=footer_font, fill=theme["muted"])

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, quality=96, optimize=True)


def draw_portrait_cover(background: Image.Image, args, theme, output: Path) -> None:
    w, h = SIZE_1080X1260
    canvas = fit_cover(background, SIZE_1080X1260, focus_x=args.portrait_focus_x, focus_y=args.portrait_focus_y)
    add_gradient_panel(canvas, (0, 0, w, int(h * 0.55)), theme["panel"], blur=34)
    draw = ImageDraw.Draw(canvas)

    margin_x = 70
    top = 72
    brand_font = load_font("bold", 34, args.font_bold)
    badge_font = load_font("bold", 24, args.font_bold)
    title_font = load_font("bold", 78, args.font_bold)
    title2_font = load_font("bold", 94, args.font_bold)
    subtitle_font = load_font("regular", 34, args.font_regular)
    footer_font = load_font("regular", 24, args.font_regular)

    logo_box = paste_logo(canvas, Path(args.logo) if args.logo else None, (margin_x, top), (76, 76))
    brand_x = margin_x if not logo_box else logo_box[2] + 24
    if args.brand:
        draw_text_with_shadow(draw, (brand_x, top + 13), args.brand, brand_font, theme["title"], theme["shadow"], (0, 2))
    if args.badge:
        draw_badge(draw, (margin_x, top + 104), args.badge, badge_font, theme, 25, 14)

    title_y = 270
    title1_lines = wrap_text(draw, args.title_line1, title_font, w - margin_x * 2)
    for idx, line in enumerate(title1_lines[:2]):
        draw_text_with_shadow(draw, (margin_x, title_y + idx * 90), line, title_font, theme["title"], theme["shadow"])
    if args.title_line2:
        y2 = title_y + (90 if len(title1_lines) <= 1 else 175)
        for idx, line in enumerate(wrap_text(draw, args.title_line2, title2_font, w - margin_x * 2)[:2]):
            draw_text_with_shadow(draw, (margin_x, y2 + idx * 106), line, title2_font, theme["title"], theme["shadow"])

    sub_y = 760
    subtitle_lines: list[str] = []
    if args.subtitle:
        subtitle_lines.extend(wrap_text(draw, args.subtitle, subtitle_font, w - margin_x * 2))
    if args.subtitle2:
        subtitle_lines.extend(wrap_text(draw, args.subtitle2, subtitle_font, w - margin_x * 2))
    for idx, line in enumerate(subtitle_lines[:4]):
        draw_text_with_shadow(draw, (margin_x, sub_y + idx * 52), line, subtitle_font, theme["subtitle"], theme["shadow"], (0, 2))
    if args.footer:
        draw.text((margin_x, h - 92), args.footer, font=footer_font, fill=theme["muted"])

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, quality=96, optimize=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Overlay exact cover text/logo and export 16:9 + video-account variants.")
    parser.add_argument("--background", required=True, help="No-text 16:9 background image, e.g. assets/covers/cover-bg-16x9.png")
    parser.add_argument("--logo", help="Official/self-owned logo path. Pasted as image; never redrawn.")
    parser.add_argument("--brand", default="", help="Brand text near logo, e.g. openJiuwen")
    parser.add_argument("--badge", default="", help="Small pill label, e.g. AUTO-GENETIC MEMORY")
    parser.add_argument("--title-line1", required=True, help="Main title first line")
    parser.add_argument("--title-line2", default="", help="Main title second line")
    parser.add_argument("--subtitle", default="", help="Subtitle line(s). Use \n for explicit line break.")
    parser.add_argument("--subtitle2", default="", help="Optional second subtitle")
    parser.add_argument("--footer", default="", help="Footer text")
    parser.add_argument("--out-dir", default="assets/covers", help="Output directory")
    parser.add_argument("--theme", choices=sorted(THEMES.keys()), default="dark")
    parser.add_argument("--font-regular", help="Regular font path")
    parser.add_argument("--font-bold", help="Bold font path")
    parser.add_argument("--focus-x", type=float, default=0.55, help="Horizontal crop focus for landscape outputs, 0-1")
    parser.add_argument("--focus-y", type=float, default=0.5, help="Vertical crop focus for landscape outputs, 0-1")
    parser.add_argument("--portrait-focus-x", type=float, default=0.58, help="Horizontal crop focus for portrait output, 0-1")
    parser.add_argument("--portrait-focus-y", type=float, default=0.5, help="Vertical crop focus for portrait output, 0-1")
    parser.add_argument("--only", choices=["all", "16x9", "1080x608", "1080x1260"], default="all", help="Export only one variant")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    background_path = Path(args.background)
    if not background_path.exists():
        print(f"ERROR: background not found: {background_path}", file=sys.stderr)
        return 2

    background = Image.open(background_path).convert("RGBA")
    out_dir = Path(args.out_dir)
    theme = THEMES[args.theme]

    outputs: list[Path] = []
    if args.only in {"all", "16x9"}:
        output = out_dir / "cover-16x9.png"
        draw_horizontal_cover(background, SIZE_16X9, args, theme, output, "16x9")
        outputs.append(output)
    if args.only in {"all", "1080x608"}:
        output = out_dir / "cover-video-account-1080x608.png"
        draw_horizontal_cover(background, SIZE_1080X608, args, theme, output, "1080x608")
        outputs.append(output)
    if args.only in {"all", "1080x1260"}:
        output = out_dir / "cover-video-account-1080x1260.png"
        draw_portrait_cover(background, args, theme, output)
        outputs.append(output)

    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
