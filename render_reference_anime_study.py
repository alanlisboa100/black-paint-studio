#!/usr/bin/env python3
"""render_reference_anime_study.py — Estude a referência no estilo do Paint (local, sem API).

Rota 100% Pillow: usa a imagem REAL como fonte de informação (composição, cores,
contornos) e a reconstrói em linguagem de ilustração:
  1) aplainamento pintado (median passes) -> massas de cor chapadas
  2) paleta extraída DA referência (median cut) -> cel-shading nas cores dela
  3) lineart por detecção de borda + dilatação -> traço escuro sobre as formas
  4) realce de cor, grão e vinheta
Nada de visão computacional semântica: nenhuma roupa/rosto/objeto é "reconhecido";
os contornos são matemáticos e as cores vêm do arquivo original.
"""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

WORK = Path(__file__).resolve().parent


def flatten_paint(img: Image.Image, strength: int) -> Image.Image:
    """Suaviza textura preservando bordas — base para massas chapadas."""
    out = img
    for _ in range(strength):
        out = out.filter(ImageFilter.MedianFilter(5))
        out = out.filter(ImageFilter.SMOOTH_MORE)
    return out


def lineart(img: Image.Image, edge_threshold: int, weight: int) -> Image.Image:
    """Traço escuro a partir das bordas reais da referência."""
    g = ImageOps.grayscale(img)
    g = g.filter(ImageFilter.SMOOTH)
    edges = g.filter(ImageFilter.FIND_EDGES)
    ink = edges.point(lambda v: 0 if v > edge_threshold else 255)
    for _ in range(weight):
        ink = ink.filter(ImageFilter.MinFilter(3))
    return ink.convert('L')


def posterize_cel(img: Image.Image, colors: int) -> Image.Image:
    """Quantiza para a paleta da própria referência (massas chapadas)."""
    pal = img.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    return pal.convert('RGB')


def grain(img: Image.Image, amount: int, seed: int) -> Image.Image:
    rng = random.Random(seed)
    w, h = img.size
    noise = Image.new('L', (max(1, w // 3), max(1, h // 3)))
    px = noise.load()
    for y in range(noise.height):
        for x in range(noise.width):
            px[x, y] = rng.randint(128 - amount, 128 + amount)
    noise = noise.resize((w, h))
    return Image.blend(img, Image.merge('RGB', (noise, noise, noise)).convert('RGB'), 0.05)


def vignette(img: Image.Image, floor: int = 190) -> Image.Image:
    w, h = img.size
    vig = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(vig)
    d.ellipse((-int(w * .06), -int(h * .06), int(w * 1.06), int(h * 1.06)), fill=26)
    vig = vig.filter(ImageFilter.GaussianBlur(int(min(w, h) / 12)))
    vig = vig.point(lambda v: min(255, v + floor))
    bg = Image.new('RGB', (w, h), (10, 9, 13))
    return Image.composite(img, bg, vig)


def study(src: Path, dst: Path, colors=64, flatten=2, edge=26, weight=1,
          saturation=1.22, max_side=1080) -> dict:
    im = Image.open(src).convert('RGB')
    im.thumbnail((max_side, max_side), Image.LANCZOS)

    base = flatten_paint(im, flatten)
    cel = posterize_cel(base, colors)
    ink = lineart(im, edge, weight)

    # tinta sobre as massas chapadas: multiply integra a lineart à cor real
    # (branco = transparente, preto = linha). Nada de inversão máscara/base.
    study_img = ImageChops.multiply(cel, Image.merge('RGB', (ink, ink, ink)))

    study_img = ImageEnhance.Color(study_img).enhance(saturation)
    study_img = ImageEnhance.Contrast(study_img).enhance(1.06)
    study_img = study_img.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=3))
    study_img = grain(study_img, 12, 20260927)
    study_img = vignette(study_img)

    dst.parent.mkdir(parents=True, exist_ok=True)
    study_img.save(dst, 'PNG', optimize=True)

    # medições honestas para o portão de qualidade
    before = set(im.getdata())
    after = set(study_img.getdata())
    ink_px = sum(1 for p in ink.getdata() if p < 128)
    return {
        'saida': str(dst),
        'dim_entrada': list(im.size),
        'dim_saida': list(study_img.size),
        'cores_referencia': len(before),
        'cores_estudo': len(after),
        'cobertura_lineart_pct': round(100 * ink_px / (ink.width * ink.height), 1),
        'paleta_preservada': round(100 * min(len(after), colors) / max(1, colors), 1),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Estudo anime da referência (local, sem API).")
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', default='reference_anime_study.png')
    ap.add_argument('--colors', type=int, default=64)
    ap.add_argument('--edge', type=int, default=26)
    ap.add_argument('--flatten', type=int, default=2)
    ap.add_argument('--saturation', type=float, default=1.22)
    args = ap.parse_args()
    import json
    report = study(Path(args.input), Path(args.output).expanduser(),
                   colors=args.colors, flatten=args.flatten, edge=args.edge,
                   saturation=args.saturation)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
