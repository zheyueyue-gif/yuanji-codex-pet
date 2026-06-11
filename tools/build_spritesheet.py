from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
PET_DIR = ROOT / "pet"
SOURCE_DIR = ROOT / "source-assets"
GENERATED_DIR = SOURCE_DIR / "generated"
PREVIEW_DIR = ROOT / "preview"

SPRITESHEET = PET_DIR / "spritesheet.webp"
BASE_SPRITESHEET = GENERATED_DIR / "base-spritesheet.webp"
PREVIEW = PREVIEW_DIR / "spritesheet-preview.png"
PET_JSON = PET_DIR / "pet.json"

WIDTH = 1536
HEIGHT = 1872
FRAME_W = 192
FRAME_H = 208
COLS = 8
ROWS = 9


def ensure_dirs() -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    PET_DIR.mkdir(parents=True, exist_ok=True)


def bootstrap_base() -> None:
    if not BASE_SPRITESHEET.exists():
        shutil.copy2(SPRITESHEET, BASE_SPRITESHEET)


def alpha_pixels(image: Image.Image) -> int:
    return sum(1 for value in image.getchannel("A").getdata() if value > 10)


def load_base_frames() -> list[Image.Image]:
    source = Image.open(BASE_SPRITESHEET).convert("RGBA")
    if source.size != (WIDTH, HEIGHT):
        raise ValueError(f"Base spritesheet must be {WIDTH}x{HEIGHT}, got {source.size}")

    frames: list[Image.Image] = []
    for row in range(ROWS):
        row_frames = [
            source.crop((col * FRAME_W, row * FRAME_H, (col + 1) * FRAME_W, (row + 1) * FRAME_H))
            for col in range(COLS)
        ]
        frames.append(max(row_frames, key=alpha_pixels))
    return frames


def crop_content(sprite: Image.Image) -> Image.Image:
    bbox = sprite.getbbox()
    if bbox is None:
        return sprite.copy()
    return sprite.crop(bbox)


def place(sprite: Image.Image, dx: float = 0, dy: float = 0, scale: float = 1, angle: float = 0) -> Image.Image:
    content = crop_content(sprite)
    if scale != 1:
        content = content.resize(
            (max(1, round(content.width * scale)), max(1, round(content.height * scale))),
            Image.Resampling.LANCZOS,
        )
    if angle:
        content = content.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)

    frame = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    frame.alpha_composite(
        content,
        (round((FRAME_W - content.width) / 2 + dx), round((FRAME_H - content.height) / 2 + dy)),
    )
    return frame


def region_warp(frame: Image.Image, box: tuple[int, int, int, int], dx: float = 0, dy: float = 0, angle: float = 0) -> Image.Image:
    region = frame.crop(box)
    if angle:
        region = region.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)

    overlay = frame.copy()
    x = round((box[0] + box[2] - region.width) / 2 + dx)
    y = round((box[1] + box[3] - region.height) / 2 + dy)
    overlay.alpha_composite(region, (x, y))
    return overlay


def squash(frame: Image.Image, sx: float = 1, sy: float = 1, anchor_y: int = 178) -> Image.Image:
    content = crop_content(frame)
    new_size = (max(1, round(content.width * sx)), max(1, round(content.height * sy)))
    content = content.resize(new_size, Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    x = round((FRAME_W - content.width) / 2)
    y = round(anchor_y - content.height)
    out.alpha_composite(content, (x, y))
    return out


def shadow(frame: Image.Image, opacity: int = 55, width: int = 100) -> Image.Image:
    layer = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse(((FRAME_W - width) // 2, FRAME_H - 24, (FRAME_W + width) // 2, FRAME_H - 8), fill=(0, 0, 0, opacity))
    layer = layer.filter(ImageFilter.GaussianBlur(5))
    layer.alpha_composite(frame)
    return layer


def sparkle(draw: ImageDraw.ImageDraw, x: int, y: int, r: int, color: tuple[int, int, int, int]) -> None:
    draw.line((x - r, y, x + r, y), fill=color, width=2)
    draw.line((x, y - r, x, y + r), fill=color, width=2)
    draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(255, 255, 255, 235))


def add_sparkle_trail(frame: Image.Image, phase: int, palette: tuple[int, int, int, int] = (255, 205, 92, 225)) -> Image.Image:
    draw = ImageDraw.Draw(frame)
    path = [(145, 42), (162, 68), (154, 100), (132, 126), (40, 52), (52, 138), (168, 134), (28, 88)]
    for offset in range(4):
        x, y = path[(phase + offset * 2) % len(path)]
        sparkle(draw, x, y, 3 + ((phase + offset) % 3), palette)
    return frame


def add_blink(frame: Image.Image, amount: int = 1) -> Image.Image:
    draw = ImageDraw.Draw(frame)
    color = (92, 72, 62, 155)
    for _ in range(amount):
        draw.arc((78, 78, 92, 86), 10, 170, fill=color, width=2)
        draw.arc((104, 78, 118, 86), 10, 170, fill=color, width=2)
    return frame


def add_lantern_glow(frame: Image.Image, phase: int) -> Image.Image:
    glow = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    cx = 37 + round(math.sin(phase / 7 * math.tau) * 8)
    cy = 143 + round(math.cos(phase / 7 * math.tau) * 2)
    strength = 55 + round(35 * (0.5 + 0.5 * math.sin(phase / 7 * math.tau)))
    for radius in range(35, 4, -4):
        alpha = round(strength * (1 - radius / 36) ** 1.7)
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(255, 201, 92, alpha))
    return Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(5)), frame)


def add_prompt_bubble(frame: Image.Image, phase: int) -> Image.Image:
    draw = ImageDraw.Draw(frame)
    x = 146 + round(math.sin(phase / 8 * math.tau) * 4)
    y = 42 + round(math.cos(phase / 8 * math.tau) * 2)
    draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(248, 255, 254, 220), outline=(95, 153, 157, 190), width=2)
    draw.text((x - 3, y - 9), "?", fill=(62, 121, 128, 235))
    return frame


def add_failed_bubbles(frame: Image.Image, phase: int) -> Image.Image:
    draw = ImageDraw.Draw(frame)
    base_x = 142 + round(math.sin(phase / 8 * math.tau) * 5)
    base_y = 55 + round(math.cos(phase / 8 * math.tau) * 2)
    for i, r in enumerate((5, 7, 4)):
        x = base_x + i * 13
        y = base_y - i * 13
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(235, 248, 250, 205), outline=(100, 147, 153, 165), width=2)
    draw.line((166, 22, 174, 30), fill=(195, 91, 91, 210), width=3)
    draw.line((174, 22, 166, 30), fill=(195, 91, 91, 210), width=3)
    return frame


def add_review_card(frame: Image.Image, phase: int) -> Image.Image:
    draw = ImageDraw.Draw(frame)
    x = 126 + round(math.sin(phase / 8 * math.tau) * 3)
    y = 42 + round(math.cos(phase / 8 * math.tau) * 2)
    draw.rounded_rectangle((x, y, x + 42, y + 25), radius=6, fill=(255, 255, 243, 230), outline=(91, 151, 127, 200), width=2)
    draw.line((x + 8, y + 14, x + 17, y + 20, x + 32, y + 8), fill=(65, 145, 106, 235), width=3)
    if phase in (1, 2, 3, 6):
        sparkle(draw, x - 8, y + 6, 4, (255, 213, 96, 220))
    return frame


def add_petals(frame: Image.Image, phase: int) -> Image.Image:
    draw = ImageDraw.Draw(frame)
    petals = [(42, 55), (54, 78), (33, 86), (62, 112)]
    for idx, (x, y) in enumerate(petals):
        px = x + round(math.sin((phase + idx) / 8 * math.tau) * 7)
        py = y + phase * 2 - idx * 5
        draw.ellipse((px - 3, py - 2, px + 5, py + 4), fill=(248, 142, 126, 190))
    return frame


def save_generated_overlays() -> None:
    overlay = Image.new("RGBA", (FRAME_W * 3, FRAME_H), (0, 0, 0, 0))
    for idx, name in enumerate(("waiting-prompt", "failed-bubbles", "review-card")):
        frame = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
        if name == "waiting-prompt":
            frame = add_prompt_bubble(frame, 2)
        elif name == "failed-bubbles":
            frame = add_failed_bubbles(frame, 2)
        else:
            frame = add_review_card(frame, 2)
        overlay.alpha_composite(frame, (idx * FRAME_W, 0))
        frame.save(GENERATED_DIR / f"{name}.png")
    overlay.save(GENERATED_DIR / "overlay-reference.png")


def build_frame(row: int, col: int, base: Image.Image) -> Image.Image:
    wave = math.sin(col / COLS * math.tau)
    bounce = [0, -1, -2, -1, 0, 1, 0, -1][col]

    if row == 0:
        frame = place(base, dy=bounce * 0.7, scale=1 + 0.006 * math.sin((col + 1) / COLS * math.tau))
        frame = region_warp(frame, (42, 22, 151, 122), dx=wave * 1.6, dy=-abs(wave) * 0.5, angle=wave * 0.8)
        frame = region_warp(frame, (38, 108, 154, 178), dx=-wave * 1.2, angle=-wave * 0.5)
        if col in (2, 6):
            frame = add_blink(frame)
        return shadow(frame, 42, 86)

    if row == 1:
        frame = place(base, dx=[-9, -6, -2, 3, 7, 9, 5, 0][col], dy=[4, 2, 0, 1, 3, 2, 1, 3][col], scale=0.94, angle=[-3, -2, -1, 1, 3, 2, 1, -1][col])
        frame = squash(frame, sx=1.01 + 0.025 * abs(wave), sy=0.995 - 0.01 * abs(wave), anchor_y=188)
        frame = add_sparkle_trail(shadow(frame, 54, 122), col)
        return frame

    if row == 2:
        frame = place(base, dx=[9, 6, 2, -3, -7, -9, -5, 0][col], dy=[4, 2, 0, 1, 3, 2, 1, 3][col], scale=0.94, angle=[3, 2, 1, -1, -3, -2, -1, 1][col])
        frame = squash(frame, sx=1.01 + 0.025 * abs(wave), sy=0.995 - 0.01 * abs(wave), anchor_y=188)
        frame = add_sparkle_trail(shadow(frame, 54, 122), col + 3)
        return frame

    if row == 3:
        frame = place(base, dx=[0, 1, 2, 1, 0, -1, 0, 1][col], dy=[1, -1, -2, -1, 0, 1, 0, -1][col], angle=[0, -1.5, -3, -1.5, 0, 1, 0, -1][col])
        frame = region_warp(frame, (28, 56, 90, 140), dx=wave * 3, dy=-abs(wave) * 3, angle=-wave * 3.5)
        frame = add_petals(shadow(frame, 43, 86), col)
        return frame

    if row == 4:
        dy = [8, 2, -5, -11, -12, -5, 5, 9][col]
        frame = place(base, dy=dy, scale=[0.985, 1.005, 1.035, 1.045, 1.04, 1.025, 0.99, 0.975][col])
        if col in (0, 7):
            frame = squash(frame, sx=1.04, sy=0.965, anchor_y=185)
        frame = add_sparkle_trail(shadow(frame, 35 if dy < -6 else 58, 82), col + 1)
        return frame

    if row == 5:
        frame = place(base, dy=[1, 2, 2, 1, 0, 1, 2, 1][col], scale=1 + 0.004 * wave)
        frame = region_warp(frame, (54, 72, 142, 154), dy=abs(wave) * 1.5)
        frame = add_failed_bubbles(shadow(frame, 38, 120), col)
        return frame

    if row == 6:
        frame = place(base, dx=round(wave * 2), dy=bounce)
        frame = region_warp(frame, (18, 98, 70, 172), dx=wave * 7, dy=abs(wave) * 2, angle=wave * 4)
        frame = add_lantern_glow(frame, col)
        frame = add_prompt_bubble(shadow(frame, 45, 82), col)
        return frame

    if row == 7:
        frame = place(base, dx=round(math.sin((col + 1) / COLS * math.tau) * 2), dy=bounce)
        frame = region_warp(frame, (58, 72, 134, 122), dx=wave * 1.5, dy=-abs(wave), angle=wave * 0.8)
        frame = region_warp(frame, (46, 112, 138, 174), dx=-wave * 1.3, angle=-wave)
        frame = add_sparkle_trail(shadow(frame, 48, 86), col, (99, 190, 191, 220))
        if col in (3, 7):
            frame = add_blink(frame)
        return frame

    frame = place(base, dy=[0, -1, -3, -2, 0, 1, 0, -1][col], scale=1 + 0.006 * math.sin((col + 2) / COLS * math.tau))
    frame = region_warp(frame, (50, 84, 138, 176), dx=-wave * 1.5, angle=-wave * 0.8)
    frame = add_review_card(shadow(frame, 44, 84), col)
    return frame


def build_sheet() -> Image.Image:
    bases = load_base_frames()
    sheet = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    for row, base in enumerate(bases):
        for col in range(COLS):
            sheet.alpha_composite(build_frame(row, col, base), (col * FRAME_W, row * FRAME_H))
    return sheet


def build_preview(sheet: Image.Image) -> Image.Image:
    preview = Image.new("RGBA", (WIDTH, HEIGHT), (22, 22, 22, 255))
    draw = ImageDraw.Draw(preview)
    for y in range(0, HEIGHT, 16):
        for x in range(0, WIDTH, 16):
            if (x // 16 + y // 16) % 2 == 0:
                draw.rectangle((x, y, x + 15, y + 15), fill=(33, 33, 33, 255))
    preview.alpha_composite(sheet)
    for col in range(COLS + 1):
        x = col * FRAME_W
        draw.line((x, 0, x, HEIGHT), fill=(255, 255, 255, 60))
    for row in range(ROWS + 1):
        y = row * FRAME_H
        draw.line((0, y, WIDTH, y), fill=(255, 255, 255, 60))
    return preview


def write_pet_json() -> None:
    PET_JSON.write_text(
        json.dumps(
            {
                "displayName": "\u521d\u89c1",
                "description": "A lively chibi companion for focused Codex work.",
                "spritesheetPath": "spritesheet.webp",
            },
            ensure_ascii=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dirs()
    bootstrap_base()
    save_generated_overlays()
    sheet = build_sheet()
    sheet.save(SPRITESHEET, "WEBP", lossless=True, method=6)
    build_preview(sheet).save(PREVIEW, "PNG")
    write_pet_json()


if __name__ == "__main__":
    main()
