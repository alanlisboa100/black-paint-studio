#!/usr/bin/env python3
"""Retrato plano em fiapos — linguagem do estudo tipo GPT, no Paint local."""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

W, H = 900, 1200


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c0, c1, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c0, c1))


def strand(draw, rng, x0, y0, x1, y1, color, width=1, bend=8):
    steps = max(8, int(abs(y1 - y0) / 18))
    pts = []
    wave = rng.uniform(0.6, 1.6)
    amp = rng.uniform(-bend, bend)
    for i in range(steps + 1):
        t = i / steps
        pts.append((lerp(x0, x1, t) + math.sin(t * math.pi * wave) * amp, lerp(y0, y1, t)))
    draw.line(pts, fill=color, width=max(1, width), joint="curve")


def pluses(draw, rng, color):
    for _ in range(14):
        x, y = rng.randint(36, W - 36), rng.randint(24, H - 24)
        if 200 < x < 700 and 140 < y < 1000:
            continue
        s = rng.choice((4, 5, 6))
        draw.line((x - s, y, x + s, y), fill=color, width=1)
        draw.line((x, y - s, x, y + s), fill=color, width=1)
    for _ in range(28):
        x, y = rng.randint(20, W - 20), rng.randint(16, H - 16)
        if 220 < x < 680 and 160 < y < 980:
            continue
        draw.point((x, y), fill=color)


def render(variant: str = "misuki") -> Image.Image:
    rng = random.Random(7 if variant == "misuki" else 3)
    paper = (250, 247, 244)
    mark = (216, 210, 216)
    im = Image.new("RGB", (W, H), paper)
    draw = ImageDraw.Draw(im)
    pluses(draw, rng, mark)

    cx = 450
    if variant == "misuki":
        skin, blush = (236, 226, 228), (214, 176, 186)
        hair_d, hair_m, hair_l = (16, 14, 18), (64, 62, 70), (186, 184, 190)
        eye_w, iris, pupil = (248, 240, 242), (140, 32, 38), (24, 8, 10)
        lip, cloth, line = (170, 128, 134), (24, 24, 30), (70, 68, 78)
    else:
        skin, blush = (238, 214, 206), (236, 170, 170)
        hair_d, hair_m, hair_l = (40, 30, 48), (86, 64, 92), (204, 176, 196)
        eye_w, iris, pupil = (250, 236, 232), (90, 74, 96), (30, 24, 32)
        lip, cloth, line = (198, 146, 148), (30, 34, 50), (56, 60, 78)

    # Ombros.
    draw.polygon([(70, H), (130, 792), (300, 736), (600, 736), (770, 792), (830, H)], fill=cloth)

    if variant == "misuki":
        draw.rounded_rectangle((338, 698, 562, 746), radius=10, fill=(12, 12, 14))
        for i in range(10):
            draw.ellipse((352 + i * 20, 712, 362 + i * 20, 722), fill=paper)
        draw.polygon([(390, 746), (510, 746), (500, 1020), (400, 1020)], fill=(18, 18, 22))
        for i in range(6):
            y = 768 + i * 26
            draw.line((428, y, 472, y + 12), fill=line, width=2)
            draw.line((472, y, 428, y + 12), fill=line, width=2)
        for bx, by in ((318, 830), (582, 830), (318, 930), (582, 930)):
            draw.rectangle((bx - 14, by - 9, bx + 14, by + 9), outline=line, width=2)
    else:
        draw.rounded_rectangle((338, 700, 562, 768), radius=3, fill=(22, 26, 40))
        for y in range(706, 764, 3):
            draw.line((344, y, 556, y), fill=(38, 42, 58), width=1)

    # Pescoço + rosto.
    draw.polygon([(402, 610), (498, 610), (528, 742), (372, 742)], fill=skin)
    draw.ellipse((cx - 158, 286, cx + 158, 678), fill=skin)
    blush_l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blush_l)
    bd.ellipse((cx - 148, 508, cx - 38, 592), fill=(*blush, 72))
    bd.ellipse((cx + 38, 508, cx + 148, 592), fill=(*blush, 72))
    im = Image.alpha_composite(im.convert("RGBA"), blush_l.filter(ImageFilter.GaussianBlur(7))).convert("RGB")
    draw = ImageDraw.Draw(im)
    for side in (-1, 1):
        for i in range(4):
            x = cx + side * (74 + i * 7)
            draw.line((x, 552 + i % 2 * 5, x + side * 9, 554 + i % 2 * 5), fill=mix(skin, blush, 0.4), width=1)
    draw.ellipse((cx - 186, 468, cx - 146, 556), fill=skin)
    draw.ellipse((cx + 146, 468, cx + 186, 556), fill=skin)

    # Cabelo de fundo: coroa + duas quedas arredondadas (sem caixa).
    draw.pieslice((cx - 250, 132, cx + 250, 560), 180, 360, fill=hair_d)
    draw.ellipse((cx - 250, 200, cx + 250, 430), fill=hair_d)
    draw.polygon([(cx - 150, 330), (cx - 248, 280), (cx - 268, 970), (cx - 176, 1036), (cx - 72, 650), (cx - 96, 430)], fill=hair_d)
    draw.polygon([(cx + 150, 330), (cx + 248, 280), (cx + 268, 980), (cx + 176, 1044), (cx + 72, 650), (cx + 96, 430)], fill=hair_d)
    draw.polygon(
        [
            (cx - 168, 292),
            (cx - 138, 206),
            (cx, 188),
            (cx + 138, 206),
            (cx + 168, 292),
            (cx + 150, 418),
            (cx + 56, 392),
            (cx - 8, 428),
            (cx - 70, 390),
            (cx - 148, 422),
        ],
        fill=hair_d,
    )

    # Fiapos escuros em grupos (não uma cortina única).
    groups = []
    for i in range(48):
        x = cx - 120 + i * 5
        groups.append((x, 210, x + rng.uniform(-14, 14), 360 + rng.uniform(0, 40), hair_d, 2))
    for i in range(26):
        x = cx - 236 + i * 4
        groups.append((x, 250, x - rng.uniform(8, 22), 980 + rng.uniform(-30, 20), hair_d, 2))
    for i in range(26):
        x = cx + 140 + i * 4
        groups.append((x, 250, x + rng.uniform(8, 22), 1000 + rng.uniform(-40, 10), hair_d, 2))
    # Mecha clara à esquerda, como no GPT.
    for i in range(22):
        x = cx - 210 + i * 3.2
        groups.append((x, 300, x - 10, 900 + rng.uniform(-20, 20), hair_l, 1))
    for i in range(14):
        x = cx - 40 + i * 4
        groups.append((x, 220, x + rng.uniform(-6, 6), 370, hair_m, 1))
    for x0, y0, x1, y1, color, width in groups:
        strand(draw, rng, x0, y0, x1, y1, color, width=width, bend=7)

    # Olhos por cima da franja (GPT deixa os dois visíveis).
    for side in (-1, 1):
        ex, ey = cx + side * 58, 478
        draw.ellipse((ex - 36, ey - 14, ex + 32, ey + 20), fill=eye_w)
        draw.ellipse((ex - 14, ey - 10, ex + 16, ey + 16), fill=iris)
        draw.ellipse((ex - 6, ey - 4, ex + 7, ey + 10), fill=pupil)
        draw.ellipse((ex - 3, ey - 7, ex + 2, ey - 2), fill=(255, 255, 255))
        draw.arc((ex - 38, ey - 18, ex + 34, ey + 6), 200, 345, fill=hair_d, width=3)
        for k in range(4):
            lx = ex - 20 + k * 12
            draw.line((lx, ey - 12, lx + side, ey - 20), fill=hair_d, width=1)

    draw.line((cx, 520, cx - 6, 556), fill=mix(skin, (110, 80, 80), 0.28), width=2)
    draw.ellipse((cx - 10, 550, cx - 5, 555), fill=mix(skin, blush, 0.45))
    draw.ellipse((cx + 3, 550, cx + 8, 555), fill=mix(skin, blush, 0.45))
    draw.arc((cx - 20, 598, cx + 20, 616), 15, 165, fill=lip, width=2)
    draw.ellipse((cx + 16, 630, cx + 20, 634), fill=mix(skin, blush, 0.5))

    if variant == "misuki":
        for side in (-1, 1):
            draw.polygon(
                [
                    (cx + side * 96, 196),
                    (cx + side * 122, 188),
                    (cx + side * 168, 96),
                    (cx + side * 186, 58),
                    (cx + side * 152, 108),
                    (cx + side * 108, 176),
                ],
                fill=hair_d,
            )
            draw.line(
                [(cx + side * 110, 188), (cx + side * 150, 110), (cx + side * 180, 62)],
                fill=hair_m,
                width=2,
            )
        draw.line((cx + 148, 528, cx + 148, 552), fill=hair_m, width=1)
        draw.line((cx + 136, 540, cx + 160, 540), fill=hair_m, width=1)

    return im


def main():
    parser = argparse.ArgumentParser(description="Retrato plano em fiapos.")
    parser.add_argument("--variant", choices=("misuki", "natural"), default="misuki")
    parser.add_argument("--output", default="stroke_portrait.png")
    args = parser.parse_args()
    dest = Path(args.output).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    render(args.variant).save(dest, "PNG", optimize=True)
    print(f"Retrato {args.variant} salvo em: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
