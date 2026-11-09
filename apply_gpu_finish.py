#!/usr/bin/env python3
"""Passe único equivalente ao botão GPU leve — CPU, para Termux sem WebGL."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageChops
import random


def apply_finish(image: Image.Image, grain: float = 0.03, sharpen: float = 0.24) -> Image.Image:
    rgb = image.convert("RGB")
    detail = ImageEnhance.Sharpness(rgb).enhance(1 + sharpen)
    noise = Image.new("RGB", detail.size)
    pix = noise.load()
    rng = random.Random(19)
    w, h = detail.size
    amp = int(255 * grain)
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            v = rng.randint(-amp, amp)
            for dy in range(2):
                for dx in range(2):
                    if x + dx < w and y + dy < h:
                        pix[x + dx, y + dy] = (v + 128, v + 128, v + 128)
    noise = noise.filter(ImageFilter.GaussianBlur(0.4))
    mixed = ImageChops.add(detail, noise, scale=1.08, offset=-16)
    return mixed


def main():
    parser = argparse.ArgumentParser(description="Acabamento leve (grão + nitidez).")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    src = Path(args.input).expanduser()
    dest = Path(args.output).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    apply_finish(Image.open(src)).save(dest, "PNG", optimize=True)
    print(f"Acabamento salvo em: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
