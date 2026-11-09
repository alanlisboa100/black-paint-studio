#!/usr/bin/env python3
"""Estudo de construção da Misuki — eixos + massas P&B. Não substitui o BlackCore."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 900, 1200
INK = (18, 18, 20, 255)
MID = (68, 68, 72, 255)
PALE = (188, 188, 192, 255)
PAPER = (246, 244, 240, 255)
RED = (139, 16, 24, 255)


def render(pose: str = "front") -> Image.Image:
    im = Image.new("RGBA", (W, H), PAPER)
    d = ImageDraw.Draw(im, "RGBA")
    cx, cy, head = 450, 310, 168
    if pose == "full":
        cy, head = 220, 110
    if pose == "profile":
        cx = 480

    d.ellipse((cx - head, cy - head, cx + head, cy + head), outline=MID, width=3)
    d.line((cx, cy - head, cx, cy + int(head * 1.18)), fill=MID, width=2)
    d.line((cx - head, cy, cx + head, cy), fill=MID, width=2)
    jaw = cy + int(head * 0.78)
    d.arc((cx - int(head * 0.72), cy, cx + int(head * 0.72), jaw + int(head * 0.55)), 10, 170, fill=INK, width=3)

    # Chifres.
    for side in (-1, 1):
        root = (cx + side * int(head * 0.55), cy - int(head * 0.72))
        tip = (cx + side * int(head * 0.95), cy - int(head * 1.35))
        d.polygon([root, (root[0] + side * 18, root[1] - 20), tip, (root[0] + side * 6, root[1] + 8)], fill=INK)

    # Massa de cabelo.
    d.pieslice((cx - int(head * 1.15), cy - int(head * 1.25), cx + int(head * 1.15), cy + int(head * 0.4)), 200, 340, fill=INK)
    d.polygon(
        [
            (cx - int(head * 1.05), cy),
            (cx - int(head * 1.2), cy + 280),
            (cx - int(head * 0.55), cy + 340),
            (cx - int(head * 0.35), cy + 40),
        ],
        fill=INK,
    )
    d.polygon(
        [
            (cx + int(head * 1.05), cy),
            (cx + int(head * 1.22), cy + 300),
            (cx + int(head * 0.5), cy + 350),
            (cx + int(head * 0.32), cy + 40),
        ],
        fill=INK,
    )

    # Olhos no eixo.
    for side in (-1, 1):
        ex = cx + side * int(head * 0.38)
        ey = cy + 8
        d.ellipse((ex - 28, ey - 14, ex + 28, ey + 16), fill=PALE, outline=INK, width=3)
        d.ellipse((ex - 10, ey - 10, ex + 10, ey + 12), fill=RED)
        d.ellipse((ex - 4, ey - 4, ex + 4, ey + 6), fill=INK)
        d.ellipse((ex - 8, ey - 8, ex - 4, ey - 4), fill=(255, 255, 255, 255))

    d.line((cx, cy + 18, cx - 6, cy + 52), fill=MID, width=2)
    d.arc((cx - 22, cy + 64, cx + 22, cy + 88), 20, 160, fill=MID, width=2)

    # Ombros / roupa.
    shoulder_y = cy + int(head * 1.55)
    d.polygon(
        [
            (cx - 220, H - 40),
            (cx - 200, shoulder_y + 40),
            (cx - 80, shoulder_y),
            (cx + 80, shoulder_y),
            (cx + 200, shoulder_y + 40),
            (cx + 220, H - 40),
        ],
        fill=INK,
    )
    d.polygon([(cx - 40, shoulder_y + 8), (cx, shoulder_y + 70), (cx + 40, shoulder_y + 8)], outline=PALE, width=3)

    try:
        font = ImageFont.load_default()
        d.text((24, 24), f"MISUKI  ·  {pose}  ·  estudo local", fill=MID, font=font)
        d.text((24, H - 36), "BLACKCORE Paint  ·  eixos, nao pintura final", fill=MID, font=font)
    except Exception:
        pass
    return im.convert("RGB")


def main():
    parser = argparse.ArgumentParser(description="Estudo de construção da Misuki.")
    parser.add_argument("--pose", default="front")
    parser.add_argument("--output", default="misuki_construct.png")
    args = parser.parse_args()
    dest = Path(args.output).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    render(args.pose).save(dest, "PNG", optimize=True)
    print(f"Estudo Misuki ({args.pose}) salvo em: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
