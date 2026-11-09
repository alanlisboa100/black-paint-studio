#!/usr/bin/env python3
"""enhance_eyes_neural.py — Cirurgia de olhos anime sobre PNG do plano neural.

Lê o plano JSON, localiza os pares espelhados de íris (fill escuro-saturado,
bbox 28..70), e aplica na região de cada olho:
  1. limbal ring (anel escuro na borda da íris)
  2. sombra da pálpebra no topo da íris
  3. lower iris light (meia-lua clara na base)
  4. streaks radiais sutis
  5. cílios superiores (3 fios em cada canto externo) + linha de cílio inferior
  6. catchlight secundário + pontinho de brilho na pupila
Antialiased via supersample 3x. Determinístico: mesma base+plano -> mesmo PNG.

Uso:
    python enhance_eyes_neural.py --base pintura.png --plan plano.json \
        --output olhos.png [--iris-color #4A1B5C]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from render_neural_plan import to_abs, color


def path_pts(d: str):
    return [p for c, pts in to_abs(d) for p in pts]


def bbox_of(d: str):
    xs = [p[0] for p in path_pts(d)]
    ys = [p[1] for p in path_pts(d)]
    return min(xs), min(ys), max(xs), max(ys)


def mirror(d: str):
    """Espelha um path SVG no eixo x=500 (coordenadas absolutas, par M/C/L/Q)."""
    def mm(cmd, pts):
        return (cmd, [(1000 - x, y) for x, y in pts])
    cmds = to_abs(d)
    out = []
    for cmd, pts in cmds:
        out.append(mm(cmd, pts))
    return out


def cmds_to_d(cmds) -> str:
    parts = []
    for cmd, pts in cmds:
        nums = ' '.join(f'{x:.1f} {y:.1f}' for x, y in pts)
        parts.append(f'{cmd} {nums}')
    return ' '.join(parts)


def find_iris_pairs(plan, want):
    """Retorna [(iris_left, iris_right)] detectados por cor de fill + simetria."""
    els = plan['elements']
    cands = []
    for k, el in enumerate(els):
        f = color(el.get('fill', 'none'))
        if not f:
            continue
        d = el.get('path', '')
        if not d:
            continue
        x0, y0, x1, y1 = bbox_of(d)
        w, h = x1 - x0, y1 - y0
        if 28 <= w <= 70 and 20 <= h <= 60 and y1 < 600:
            cands.append((k, f, (x0, y0, x1, y1)))
    pairs = []
    target = color(want) if want else None
    used = set()
    for i, (k, f, b) in enumerate(cands):
        if k in used:
            continue
        cx = (b[0] + b[2]) / 2
        if cx > 500:
            continue
        for j in range(i + 1, len(cands)):
            k2, f2, b2 = cands[j]
            if k2 in used or f != f2:
                continue
            cx2 = (b2[0] + b2[2]) / 2
            if abs((1000 - cx) - cx2) <= 6 and abs(b[1] - b2[1]) <= 6:
                if target is None or _close(f, target, 24):
                    pairs.append((k, k2))
                    used.update((k, k2))
                break
    return pairs


def _close(a, b, tol):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--plan', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--iris-color', default=None)
    args = ap.parse_args()

    plan = json.load(open(args.plan, encoding='utf-8'))
    base = Image.open(args.base).convert('RGB')
    W, H = base.size
    VH = int(plan.get('viewBoxHeight') or 1200)
    SS = 3
    sx, sy = W * SS / 1000, H * SS / VH  # escala viewBox -> pixels SS

    def P(x, y):
        return (x * sx, y * sy)

    # camada de tinta em SS para traços nítidos antialiased
    ink = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
    idr = ImageDraw.Draw(ink)

    els = plan['elements']
    iris_pairs = find_iris_pairs(plan, args.iris_color)
    if not iris_pairs:
        raise SystemExit('[ERRO] nenhuma pair de íris detectada; passe --iris-color')

    def mask_poly(d_cmds):
        m = Image.new('L', (W * SS, H * SS), 0)
        dd = ImageDraw.Draw(m)
        for cmd, pts in d_cmds:
            if cmd == 'M':
                poly = [P(*p) for p in pts]
            else:
                poly.extend(P(*p) for p in pts)
        if len(poly) > 2:
            dd.polygon(poly, fill=255)
        return m

    report = []
    for kl, kr in iris_pairs:
        for k, side in ((kl, 'E'), (kr, 'D')):
            d = els[k]['path']
            x0, y0, x1, y1 = bbox_of(d)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
            cmds = to_abs(d)
            m = mask_poly(cmds)
            m_np = np.asarray(m, dtype=np.float32) / 255.0

            # 1) limbal ring: stroke do próprio contorno da íris
            outline = [(P(*p)) for cmd, pts in cmds for p in pts]
            idr.line(outline + [outline[0]], fill=(16, 4, 24, 235), width=max(2, round(2.2 * SS / 2)), joint='curve')

            # 2-4) tons anime da íris calculados em 1x com máscara suavizada
            m1 = m.resize((W, H), Image.LANCZOS)
            m_np = np.asarray(m1, dtype=np.float32)[..., None] / 255.0
            yy = np.arange(H, dtype=np.float32)[None, :, None].transpose(1, 0, 2)
            # coordenadas viewBox -> px
            gx, gy = W / 1000.0, H / VH
            cyp, ryp = cy * gy, ry * gy
            exp = np.clip(m_np, 0, 1)
            # sombra da pálpebra: faixa estreita no topo da íris, quase preta
            top_w = np.clip((cyp - yy) / (ryp * 0.55), 0, 1) ** 2 * 0.55
            dark = np.array([26, 3, 12], dtype=np.float32)
            arr = np.asarray(base, dtype=np.float32)
            mix = top_w * exp
            arr = arr * (1 - mix) + dark * mix
            # crescente na base da íris: cor viva, falloff quadrático
            bot_w = np.clip((yy - (cyp + ryp * 0.22)) / (ryp * 0.62), 0, 1) ** 2 * 0.50
            cres = np.array([216, 62, 74], dtype=np.float32)
            mix = bot_w * exp
            arr = arr * (1 - mix) + cres * mix
            # boost de saturação na íris preservando luminância
            lum = (0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2])[..., None]
            boosted = lum + (arr - lum) * 1.32
            mix = exp * 0.9
            arr = np.where(exp > 0.02, arr * (1 - mix) + boosted * mix, arr)
            base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')
            report.append((side, round(float(top_w.max()), 2), round(float(bot_w.max()), 2)))

        # 5) cílios: âncora = canto externo da esclera mais externa (bbox par)
        dl = els[kl]['path']
        bbl = bbox_of(dl)
        outer_x = bbl[0]  # olho E: extremo esquerdo
        base_y = bbl[1] + (bbl[3] - bbl[1]) * 0.1
        for i, (dxl, dyl) in enumerate(((-14, -12), (-9, -15), (-4, -15))):
            x1c, y1c = outer_x + dxl, base_y + dyl - 6
            idr.line([P(outer_x + 6 + i * 5, base_y - 2),
                      P(outer_x + (dxl + 6) / 2 + i * 4, base_y + dyl / 2),
                      P(x1c, y1c)], fill=(16, 6, 24, 230), width=max(2, SS), joint='curve')

        # 6) catchlight secundário + brilho na parte inferior da íris
        cx_l = (bbl[0] + bbl[2]) / 2
        cy_l = (bbl[1] + bbl[3]) / 2
        px_l = Image.new('L', (W * SS, H * SS), 0)
        ImageDraw.Draw(px_l).ellipse(
            [P(cx_l - 9, cy_l + 5), P(cx_l + 7, cy_l + 13)], fill=210)
        px_r = Image.new('L', (W * SS, H * SS), 0)
        ImageDraw.Draw(px_r).ellipse(
            [P(1000 - cx_l - 7, cy_l + 5), P(1000 - cx_l + 9, cy_l + 13)], fill=210)
        for pxx in (px_l, px_r):
            pxx = pxx.filter(ImageFilter.GaussianBlur(1.6 * SS)).resize((W, H), Image.LANCZOS)
            pnp = np.asarray(pxx, dtype=np.float32)[..., None] / 255.0
            arr = np.asarray(base, dtype=np.float32)
            arr = arr * (1 - pnp * 0.8) + 255.0 * pnp * 0.8
            base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')

    # composto final da tinta (cílios/streaks/limbal) com downscale AA
    ink_small = ink.resize((W, H), Image.LANCZOS)
    out = Image.alpha_composite(base.convert('RGBA'), ink_small).convert('RGB')
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.save(args.output)
    print(json.dumps({
        'saida': args.output,
        'dim': list(out.size),
        'pares_iris': len(iris_pairs),
        'tons_aplicados': report,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
