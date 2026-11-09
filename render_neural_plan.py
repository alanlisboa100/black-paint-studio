#!/usr/bin/env python3
"""render_neural_plan.py — Rasterizador local do plano de pintura gerado pela IA.

A rota vision do estúdio (POST /api/vision/paint) pede ao BlackCore Google um
plano JSON com paths SVG (comandos M L H V C S Q T Z, cores #RRGGBB). O navegador
renderiza via <img src=blob:svg>. Este módulo faz o mesmo passe fora do navegador:
valida cada forma, converte curvas em amostras e pinta fundo → massas → lineart
na ordem do plano, supersampling 2x. Determinístico: o mesmo plano gera o mesmo PNG.

Uso:
    python render_neural_plan.py --plan plano.json --output pintura.png [--width 900]
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw

MAX_PATH_CHARS = 7000
NUM = r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'
CMD = re.compile(r'([MmLlHhVvCcSsQqTtZzAa])((?:[^MmLlHhVvCcSsQqTtZzAa])*)')
NRE = re.compile(NUM)
COLOR_RE = re.compile(r'#[0-9a-fA-F]{6}')


def arc_points(p0, rx, ry, rot_deg, large, sweep, p1, steps=14):
    """Elliptical arc SVG (endpoint params) -> center params -> amostras."""
    import math
    if rx == 0 or ry == 0:
        return [p1]
    rx, ry = abs(rx), abs(ry)
    phi = math.radians(rot_deg) % (2 * math.pi)
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = (x0 - x1) / 2, (y0 - y1) / 2
    x0r = math.cos(phi) * dx + math.sin(phi) * dy
    y0r = -math.sin(phi) * dx + math.cos(phi) * dy
    lam = (x0r / rx) ** 2 + (y0r / ry) ** 2
    if lam > 1:  # raios insuficientes: escala como manda a spec
        s = math.sqrt(lam)
        rx *= s
        ry *= s
    num = rx**2 * ry**2 - rx**2 * y0r**2 - ry**2 * x0r**2
    den = rx**2 * y0r**2 + ry**2 * x0r**2
    co = 0.0 if den == 0 else math.sqrt(max(0.0, num / den))
    if large == sweep:
        co = -co
    cxr = co * rx * y0r / ry
    cyr = -co * ry * x0r / rx
    cx = math.cos(phi) * cxr - math.sin(phi) * cyr + (x0 + x1) / 2
    cy = math.sin(phi) * cxr + math.cos(phi) * cyr + (y0 + y1) / 2

    def ang(ux, uy):
        return math.atan2(uy, ux)

    th0 = ang((x0r - cxr) / rx, (y0r - cyr) / ry)
    dth = ang((-x0r - cxr) / rx, (-y0r - cyr) / ry) - th0
    if sweep == 0 and dth > 0:
        dth -= 2 * math.pi
    elif sweep == 1 and dth < 0:
        dth += 2 * math.pi
    out = []
    for i in range(1, steps + 1):
        t = th0 + dth * i / steps
        px = math.cos(phi) * rx * math.cos(t) - math.sin(phi) * ry * math.sin(t) + cx
        py = math.sin(phi) * rx * math.cos(t) + math.cos(phi) * ry * math.sin(t) + cy
        out.append((px, py))
    return out


def to_abs(d: str):
    """Converte o 'd' do path SVG em comandos absolutos (M/L/C/Q com pontos)."""
    if not isinstance(d, str) or len(d) > MAX_PATH_CHARS or not re.fullmatch(r'[MmLlHhVvCcSsQqTtZzAa0-9eE+.,\-\s]+', d) or not re.match(r'\s*[Mm]', d):
        raise ValueError('Path SVG inválido')
    x = y = sx = sy = cx = cy = qx = qy = 0.0
    previous = '' 
    out = []
    for cmd, nums in CMD.findall(d):
        vals = [float(v) for v in NRE.findall(nums)]
        if any(not math.isfinite(v) or abs(v) > 5000 for v in vals): raise ValueError('Coordenadas inválidas')
        rep = cmd.islower()
        C = cmd.upper()
        i = 0

        def take(n):
            nonlocal i
            g = vals[i:i + n]
            i += n
            if len(g) != n: raise ValueError("Comando SVG incompleto")
            return g

        first = True
        while i < len(vals) or C == 'Z' or first:
            first = False
            if C == 'Z':
                out.append(('L', [(sx, sy)]))
                x, y = sx, sy
                break
            if i >= len(vals):
                break
            if C == 'M':
                dx, dy = take(2)
                x = x + dx if rep else dx
                y = y + dy if rep else dy
                sx, sy = x, y
                out.append(('M', [(x, y)]))
                C = 'L'
            elif C == 'L':
                dx, dy = take(2)
                x = x + dx if rep else dx
                y = y + dy if rep else dy
                out.append(('L', [(x, y)]))
            elif C == 'H':
                dx, = take(1)
                x = x + dx if rep else dx
                out.append(('L', [(x, y)]))
            elif C == 'V':
                dy, = take(1)
                y = y + dy if rep else dy
                out.append(('L', [(x, y)]))
            elif C == 'C':
                a, b, c2, d2, e, f = take(6)
                x1 = x + a if rep else a
                y1 = y + b if rep else b
                x2 = x + c2 if rep else c2
                y2 = y + d2 if rep else d2
                x = x + e if rep else e
                y = y + f if rep else f
                cx, cy = x2, y2
                out.append(('C', [(x1, y1), (x2, y2), (x, y)]))
            elif C == 'S':
                a, b, e, f = take(4)
                x1, y1 = (2 * x - cx, 2 * y - cy) if previous in ('C', 'S') else (x, y)
                x2 = x + a if rep else a
                y2 = y + b if rep else b
                x = x + e if rep else e
                y = y + f if rep else f
                cx, cy = x2, y2
                out.append(('C', [(x1, y1), (x2, y2), (x, y)]))
            elif C == 'Q':
                a, b, e, f = take(4)
                x1 = x + a if rep else a
                y1 = y + b if rep else b
                x = x + e if rep else e
                y = y + f if rep else f
                qx, qy = x1, y1
                out.append(('Q', [(x1, y1), (x, y)]))
            elif C == 'T':
                e, f = take(2)
                x1, y1 = (2 * x - qx, 2 * y - qy) if previous in ('Q', 'T') else (x, y)
                x = x + e if rep else e
                y = y + f if rep else f
                qx, qy = x1, y1
                out.append(('Q', [(x1, y1), (x, y)]))
            elif C == 'A':
                rx, ry, rot, la, sw, e, f = take(7)
                nx = x + e if rep else e
                ny = y + f if rep else f
                pts = arc_points((x, y), rx, ry, rot, int(la), int(sw), (nx, ny))
                x, y = nx, ny
                if pts:
                    out.append(('L', pts))
            else:
                break
            previous = C
    return out


def bezier_samples(c, pts, last, steps=10):
    """Amostra curvas C/Q em segmentos; L passa direto."""
    if c == 'L':
        return pts
    if c == 'C':
        p0 = last
        p1, p2, p3 = pts
        out = []
        for i in range(1, steps + 1):
            t = i / steps
            u = 1 - t
            out.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                        u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
        return out
    if c == 'Q':
        p0 = last
        p1, p2 = pts
        out = []
        for i in range(1, steps + 1):
            t = i / steps
            u = 1 - t
            out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                        u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
        return out
    return [pts[0]]


def color(s):
    if not s or s == 'none':
        return None
    s = str(s).strip()
    if COLOR_RE.fullmatch(s):
        return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))
    return None


def valid_plan(plan) -> bool:
    return (isinstance(plan, dict) and color(plan.get('background')) is not None
            and isinstance(plan.get('elements'), list)
            and 1 <= len(plan['elements']) <= 240)


def composite_mark(image, points, rgb, opacity, stroke_width=0):
    """Allocate only the painted region instead of a full canvas for every mark."""
    margin = stroke_width + 2
    left = max(0, min(x for x, _ in points) - margin)
    top = max(0, min(y for _, y in points) - margin)
    right = min(image.width, max(x for x, _ in points) + margin + 1)
    bottom = min(image.height, max(y for _, y in points) + margin + 1)
    if right <= left or bottom <= top or opacity <= 0: return
    patch = Image.new('RGBA', (right-left,bottom-top))
    draw = ImageDraw.Draw(patch)
    translated = [(x-left,y-top) for x,y in points]
    if stroke_width:
        draw.line(translated,fill=(*rgb,round(opacity*255)),width=stroke_width,joint='curve')
    else:
        draw.polygon(translated,fill=(*rgb,round(opacity*255)))
    image.paste(patch,(left,top),patch)


def render_plan(plan: dict, width: int = 900, checkpoint_dir=None) -> tuple:
    if not valid_plan(plan): raise ValueError("Plano inválido")
    W = int(width)
    VH = int(plan.get('viewBoxHeight') or 1200)
    H = round(W * VH / 1000)
    if not 128 <= W <= 1440 or not 350 <= VH <= 2200 or W * H > 2_000_000:
        raise ValueError("Resolução acima do limite do celular (128–1440 px, até 2 MP)")
    SS = 2
    img = Image.new('RGB', (W * SS, H * SS), color(plan['background']))
    stats = {'ok': 0, 'skip': 0}

    folder = Path(checkpoint_dir).expanduser() if checkpoint_dir else None
    if folder: folder.mkdir(parents=True, exist_ok=True)
    milestones = {max(1, math.ceil(len(plan['elements']) * n / 5)): n for n in range(1, 6)}
    for element_index, el in enumerate(plan['elements'], 1):
        try:
            d = el.get('path') or ''
            if len(d) > MAX_PATH_CHARS or not re.fullmatch(r'[MmLlHhVvCcSsQqTtZzAa0-9eE+.,\-\s]+', d):
                stats['skip'] += 1
                continue
            cmds = to_abs(d)
            if not cmds:
                stats['skip'] += 1
                continue
            # agrupa em subpaths (cada M abre um novo): suporta anéis concêntricos,
            # cruzes/faíscas e paths de múltiplos lápis sem distorcer
            subs = []
            last = (0.0, 0.0)
            for c, pts in cmds:
                if c == 'M':
                    subs.append([[pts[0]], pts[0]])
                    last = pts[0]
                else:
                    if not subs:
                        subs.append([[(0.0, 0.0)], (0.0, 0.0)])
                    samp = bezier_samples(c, pts, last)
                    subs[-1][0].extend(samp)
                    last = samp[-1]
            fill = color(el.get('fill', 'none'))
            stroke = color(el.get('stroke', 'none'))
            w = max(0.0, float(el.get('strokeWidth') or 0))
            op = max(0.0, min(1.0, float(el.get('opacity', 1))))
            drew = False
            for poly, _start in subs:
                pts_px = [(round(x / 1000 * W * SS), round(y / VH * H * SS))
                          for x, y in poly]
                if fill and len(pts_px) >= 3:
                    composite_mark(img, pts_px, fill, op)
                    drew = True
                if stroke and w > 0 and len(pts_px) >= 2:
                    composite_mark(img, pts_px, stroke, op, max(1, round(w * W / 1000 * SS)))
                    drew = True
            stats['ok' if drew else 'skip'] += 1
        except (ValueError, TypeError, KeyError, OverflowError):
            stats['skip'] += 1
        if folder and element_index in milestones:
            number = milestones[element_index]
            img.resize((W,H),Image.Resampling.LANCZOS).save(folder / f'etapa_{number:02d}.png','PNG')

    return img.resize((W, H), Image.LANCZOS), stats


def main() -> int:
    ap = argparse.ArgumentParser(description="Rasteriza um plano SVG da IA (rota vision) em PNG local.")
    ap.add_argument('--plan', required=True, help='JSON do plano (background, elements, viewBoxHeight)')
    ap.add_argument('--output', default='pintura_neural.png')
    ap.add_argument('--width', type=int, default=900)
    ap.add_argument('--checkpoint-dir', help='Salva até cinco etapas visuais da ordem de pintura')
    args = ap.parse_args()
    plan = json.loads(Path(args.plan).expanduser().read_text())
    if not valid_plan(plan):
        print('Plano inválido ou incompleto (fundo/elements). Nada foi pintado.', flush=True)
        return 1
    try:
        img, stats = render_plan(plan, args.width, args.checkpoint_dir)
    except ValueError as error:
        ap.error(str(error))
    dest = Path(args.output).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, 'PNG', optimize=True)
    print(json.dumps({'saida': str(dest), 'dim': list(img.size), **{'elementos_pintados': stats['ok'], 'pulados': stats['skip']}},
                     ensure_ascii=False))
    return 0 if stats['ok'] > 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
