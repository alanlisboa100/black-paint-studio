#!/usr/bin/env python3
"""render_casual_character_v2.py — Personagem casual pintada pelo Paint, passe v2.

Melhorias sobre v1 (mesma linguagem: Pillow local, zero difusão):
- supersample 3x (curvas e círculos mais limpos)
- sombreamento suave: luz/penumbra por camadas RGBA com blur local (não só cel duro)
- olhos grandes de anime: íris em gradiente radial, sombra da pálpebra, delineador,
  dois catchlights, cílios externos engrossados
- rosto com queixo em curva bézier (sem cantos de polígono)
- cabelo: massa + mechas + banda de brilho da coroa (halo) + luz de contorno à direita
- suéter: textura de ribana, dobras com sombra suave, punhos
- mãos: unhas e nós dos dedos
- pós: grão leve, aquecimento e nitidez
"""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H = 900, 1200
S = 3

SKIN = (252, 231, 222)
SKIN_SH = (238, 200, 190)
SKIN_DEEP = (224, 168, 160)
HAIR_D = (30, 22, 28)
HAIR_M = (62, 44, 52)
HAIR_H = (138, 104, 116)
HAIR_RIM = (186, 150, 162)
LINE = (46, 34, 42)
KNIT = (245, 236, 222)
KNIT_SH = (219, 203, 181)
KNIT_DEEP = (196, 178, 154)
KNIT_LN = (205, 188, 165)
EYE_TOP = (255, 196, 110)
EYE_BOT = (168, 92, 36)
EYE_D = (86, 40, 18)
LIP = (208, 118, 122)
LIP_SH = (228, 158, 158)
BLUSH = (244, 176, 170)


def _p(*xy):
    return [round(v * S) for v in xy]


def cubic_points(p0, p1, p2, p3, steps=40):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        pts.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    return pts


class Paint:
    def __init__(self):
        self.im = Image.new('RGB', (W * S, H * S), (247, 242, 238))

    def draw(self):
        return ImageDraw.Draw(self.im, 'RGB')

    # ---------- primitivas duras ----------
    def poly(self, pts, fill, outline=None, width=2):
        d = self.draw()
        d.polygon([_p(*pt) for pt in pts], fill=fill)
        if outline:
            p = [_p(*pt) for pt in pts] + [_p(*pts[0])]
            d.line(p, fill=outline, width=max(1, width * S), joint='curve')

    def curve_shape(self, beziers, fill, outline=None, width=2, steps=14):
        """Polígono de contorno suave a partir de cubics encadeadas."""
        pts = []
        for seg in beziers:
            pts += cubic_points(*seg, steps)[: (len(pts) and steps + 1) or steps + 1]
        self.poly(pts, fill, outline, width)
        return pts

    def ell(self, box, fill=None, outline=None, width=2):
        self.draw().ellipse([round(v * S) for v in box], fill=fill, outline=outline,
                            width=max(1, width * S))

    def tapered(self, p0, p1, p2, p3, fill, wmax=3.0, steps=28, taper=0.35):
        d = self.draw()
        pts = cubic_points(p0, p1, p2, p3, steps)
        for i in range(len(pts) - 1):
            t = (i + .5) / len(pts)
            press = taper + (1 - taper) * (math.sin(math.pi * t) ** .45)
            wd = max(1, round(wmax * press * S))
            a, b = _p(*pts[i]), _p(*pts[i + 1])
            d.line([a, b], fill=fill, width=wd)
            r = wd // 2
            if r:
                x, y = a
                d.ellipse((x - r, y - r, x + r, y + r), fill=fill)

    # ---------- sombreamento suave (local, barato) ----------
    def soft_ell(self, box, color, alpha=60, radius=8):
        x0, y0, x1, y1 = (round(v * S) for v in box)
        pad = radius * S * 2
        lay = Image.new('RGBA', (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
        ImageDraw.Draw(lay).ellipse((pad, pad, lay.width - pad, lay.height - pad),
                                    fill=(*color, alpha))
        lay = lay.filter(ImageFilter.GaussianBlur(radius * S))
        self.im.paste(lay, (x0 - pad, y0 - pad), lay)

    def soft_poly(self, pts, color, alpha=70, radius=6, feather=True):
        xs = [v[0] for v in pts]
        ys = [v[1] for v in pts]
        x0, y0 = round(min(xs) * S), round(min(ys) * S)
        x1, y1 = round(max(xs) * S), round(max(ys) * S)
        pad = radius * S * 2
        lay = Image.new('RGBA', (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
        ImageDraw.Draw(lay).polygon([(_p(*pt)[0] - x0 + pad, _p(*pt)[1] - y0 + pad)
                                     for pt in pts], fill=(*color, alpha))
        if feather:
            lay = lay.filter(ImageFilter.GaussianBlur(radius * S))
        self.im.paste(lay, (x0 - pad, y0 - pad), lay)

    def soft_path(self, pts, color, alpha=60, width=6, radius=5):
        xs = [v[0] for v in pts]
        ys = [v[1] for v in pts]
        x0 = round(min(xs) * S) - radius * S * 2 - width * S
        y0 = round(min(ys) * S) - radius * S * 2 - width * S
        x1 = round(max(xs) * S) + radius * S * 2 + width * S
        y1 = round(max(ys) * S) + radius * S * 2 + width * S
        lay = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        shifted = [(_p(*pt)[0] - x0, _p(*pt)[1] - y0) for pt in pts]
        d.line(shifted, fill=(*color, alpha), width=max(1, round(width * S)), joint='curve')
        lay = lay.filter(ImageFilter.GaussianBlur(radius * S))
        self.im.paste(lay, (x0, y0), lay)

    def radial_gradient(self, box, stops, steps=None):
        """Íris com gradiente vertical aproximado por anéis."""
        x0, y0, x1, y1 = (round(v * S) for v in box)
        w, h = x1 - x0, y1 - y0
        lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        n = 22
        for i in range(n, 0, -1):
            t = (i - 1) / (n - 1)
            col = tuple(round(a + (b - a) * t) for a, b in zip(stops[0], stops[1]))
            m = int((w * i / n) / 2)
            d.ellipse((w // 2 - m, h // 2 - m * h // w, w // 2 + m, h // 2 + m * h // w),
                      fill=(*col, 255))
        self.im.paste(lay, (x0, y0), lay)


def background(c, rng):
    # fundo neutro quente com bokeh suave
    for _ in range(30):
        x = rng.randint(20, W - 20)
        y = rng.randint(20, H - 60)
        r = rng.randint(10, 52)
        tone = rng.choice([(255, 224, 188), (255, 206, 224), (208, 232, 255)])
        c.soft_ell((x - r, y - r, x + r, y + r), tone, alpha=rng.randint(20, 46), radius=10)


def draw_face(c, cx):
    # contorno do rosto em bézier: têmpora -> bochecha -> queixo pontudo
    left = cubic_points((cx - 152, 330), (cx - 166, 470), (cx - 132, 590), (cx - 8, 682), 30)
    right = [(cx + (cx - p[0]), p[1]) for p in left][::-1]
    c.poly([(cx - 152, 322)] + left + right + [(cx + 152, 322)], SKIN)
    # sombra lateral esquerda + queixo
    c.soft_poly([(cx - 152, 400), (cx - 138, 570), (cx - 70, 660), (cx - 58, 600),
                 (cx - 104, 500), (cx - 120, 400)], SKIN_SH, alpha=90, radius=9)
    c.soft_ell((cx - 120, 596, cx + 120, 700), SKIN_SH, alpha=70, radius=12)
    # orelhas
    for side in (-1, 1):
        ex = cx + side * 158
        c.ell((ex - 16, 452, ex + 16, 542), SKIN, LINE, 2)
        c.tapered((ex - 6, 470), (ex + 4, 490), (ex + 2, 510), (ex - 4, 524), SKIN_SH, 2, 10, .6)
    return cx


def draw_eyes(c, cx):
    for side in (-1, 1):
        ex, ey = cx + side * 80, 502
        rx, ry = 52, 40
        # branco do olho
        c.poly([(ex - rx, ey), (ex - rx * .55, ey - ry * .78), (ex + rx * .5, ey - ry * .8),
                (ex + rx, ey - ry * .1), (ex + rx * .5, ey + ry * .82), (ex - rx * .5, ey + ry * .8)],
               (253, 251, 251), LINE, 2)
        # íris em gradiente (topo claro -> base escura)
        c.radial_gradient((ex - 30, ey - 26, ex + 30, ey + 30), (EYE_TOP, EYE_BOT))
        c.ell((ex - 13, ey - 11, ex + 13, ey + 15), EYE_D)
        # sombra da pálpebra por cima da íris
        c.soft_poly([(ex - 32, ey - 26), (ex + 32, ey - 26), (ex + 20, ey - 4), (ex - 18, ey - 6)],
                    (120, 70, 40), alpha=88, radius=4)
        # catchlights
        c.ell((ex - 22, ey - 22, ex - 2, ey - 2), (255, 255, 255))
        c.ell((ex + 10, ey + 6, ex + 20, ey + 16), (255, 244, 214))
        # cílios superiores grossos, mais pesados no canto externo
        c.tapered((ex - rx - 2, ey - 6), (ex - rx * .4, ey - ry - 8), (ex + rx * .3, ey - ry - 10),
                  (ex + rx + 6, ey - 4), LINE, 8.5, 22, .25)
        c.tapered((ex + rx, ey - 8), (ex + rx + 14, ey - 14), (ex + rx + 20, ey - 22),
                  (ex + rx + 24, ey - 34), LINE, 5, 10, .3)  # cílio externo
        # delineador fino inferior
        c.tapered((ex - rx * .6, ey + ry * .8), (ex, ey + ry * .95), (ex + rx * .5, ey + ry * .85),
                  (ex + rx * .9, ey + ry * .45), LINE, 2.6, 14, .4)
        # sobrancelha delicada
        c.tapered((ex - rx, ey - ry - 34), (ex - 10, ey - ry - 52), (ex + 18, ey - ry - 52),
                  (ex + rx - 4, ey - ry - 30), HAIR_M, 5, 16, .3)


def draw_nose_mouth(c, cx):
    c.tapered((cx - 3, 548), (cx - 9, 560), (cx - 5, 570), (cx + 4, 572), SKIN_DEEP, 2.6, 8, .5)
    # boca sorrindo: arco superior + lábio inferior + gloss
    c.tapered((cx - 36, 596), (cx - 14, 612), (cx + 14, 612), (cx + 38, 592), LIP, 5.5, 16, .25)
    c.tapered((cx - 30, 604), (cx - 8, 624), (cx + 12, 624), (cx + 30, 601), LIP, 4.5, 14, .3)
    c.soft_ell((cx - 18, 610, cx + 18, 622), (255, 255, 255), alpha=60, radius=3)
    c.tapered((cx - 36, 596), (cx - 30, 590), (cx - 26, 588), (cx - 22, 590), LINE, 3, 6, .4)
    # blush
    c.soft_ell((cx - 142, 528, cx - 52, 574), BLUSH, alpha=64, radius=12)
    c.soft_ell((cx + 52, 528, cx + 142, 574), BLUSH, alpha=64, radius=12)


def draw_back_hair(c, cx, rng):
    c.poly([(cx - 268, 350), (cx - 344, 780), (cx - 312, 1196), (cx + 312, 1196),
            (cx + 344, 780), (cx + 268, 350)], HAIR_D)
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        for sx in (-1, 1):
            x = cx + sx * (240 + t * 90)
            c.tapered((x - sx * 20, 360), (x + sx * 30, 700), (x + sx * 36, 980),
                      (x + sx * 20, 1196), HAIR_M, 10, 24, .4)
    for i in range(46):
        t = i / 45
        x0 = cx - 262 + t * 524
        sway = math.sin(t * math.pi * 3 + 1.1) * 38
        tone = [HAIR_M, HAIR_D, HAIR_H][i % 3]
        c.tapered((x0, 296 + t * 70), (x0 - 46 + sway, 660), (x0 - 74 + sway, 960),
                  (x0 - 96 + sway * 1.4, 1196), tone, 2.3 + (i % 3), 30, .3)


def draw_front_hair(c, cx):
    # coroa + franja em tufos
    crown = cubic_points((cx - 176, 470), (cx - 212, 288), (cx - 40, 176), (cx + 140, 196), 24) \
        + cubic_points((cx + 140, 196), (cx + 252, 226), (cx + 232, 420), (cx + 188, 488), 24)
    fringe = [(cx + 186, 484), (cx + 152, 402), (cx + 100, 368), (cx + 34, 412),
              (cx - 32, 356), (cx - 106, 398), (cx - 158, 404)]
    c.poly([(cx - 176, 470)] + crown + fringe, HAIR_D)
    tufts = [((cx - 186, 320), (cx - 156, 480), (cx - 176, 566), (cx - 206, 656)),
             ((cx - 124, 268), (cx - 98, 382), (cx - 124, 476), (cx - 156, 552)),
             ((cx - 32, 224), (cx - 10, 336), (cx - 54, 404), (cx - 90, 434)),
             ((cx + 62, 214), (cx + 88, 330), (cx + 54, 406), (cx + 24, 438)),
             ((cx + 152, 292), (cx + 140, 428), (cx + 162, 524), (cx + 186, 616)),
             ((cx + 198, 376), (cx + 190, 470), (cx + 208, 562), (cx + 220, 668))]
    for pts in tufts:
        c.tapered(*pts, HAIR_D, 17, 26, .35)
        c.tapered(*[(x + 4, y - 8) for x, y in pts], HAIR_M, 4.5, 26, .35)
    # halo de brilho da coroa
    c.soft_path(cubic_points((cx - 132, 286), (cx - 40, 238), (cx + 60, 236), (cx + 148, 276), 20),
                HAIR_H, alpha=120, width=13, radius=7)
    c.soft_path(cubic_points((cx - 116, 300), (cx - 30, 258), (cx + 52, 256), (cx + 130, 292), 20),
                HAIR_RIM, alpha=90, width=5, radius=4)
    # fios finos
    for i in range(34):
        t = i / 33
        x0 = cx - 178 + t * 356
        c.tapered((x0, 226 + abs(x0 - cx) * .55), (x0 - 18, 334), (x0 - 30, 398),
                  (x0 - 40 - t * 22, 456 + (i * 53 % 70)),
                  HAIR_H if i % 4 == 0 else HAIR_M, 1.5, 22)
    # luz de contorno no lado direito do cabelo
    c.soft_path([(cx + 262, 380), (cx + 320, 640), (cx + 330, 900), (cx + 306, 1150)],
                HAIR_RIM, alpha=80, width=10, radius=8)


def draw_body(c, rng):
    c.poly([(110, 1196), (146, 856), (252, 742), (372, 700), (528, 700), (648, 742),
            (754, 856), (790, 1196)], KNIT, KNIT_LN, 2)
    # gola relaxada com sombra interna
    c.poly([(296, 742), (450, 796), (604, 742), (646, 872), (450, 936), (254, 872)], KNIT_SH)
    c.soft_path([(312, 754), (450, 810), (588, 754)], KNIT_DEEP, alpha=110, width=8, radius=6)
    c.tapered((262, 762), (356, 818), (544, 818), (638, 762), KNIT_LN, 3.4, 20, .4)
    # pescoço com sombra sob o queixo
    c.poly([(406, 598), (494, 598), (514, 716), (386, 716)], SKIN)
    c.soft_ell((398, 600, 502, 664), SKIN_DEEP, alpha=90, radius=8)
    # ribana do tricô
    for i in range(17):
        x = 162 + i * 36
        top = 792 + abs(x - 450) * .30
        c.tapered((x, top), (x + 5, top + 150), (x - 5, top + 260), (x + 2, 1196),
                  KNIT_SH, 2.4, 16, .5)
        c.tapered((x + 18, top + 8), (x + 22, top + 170), (x + 14, top + 280), (x + 19, 1196),
                  KNIT_LN, 1.1, 16, .5)
    # dobras macias
    for pts in [((210, 850), (260, 950), (240, 1040), (214, 1150)),
                ((690, 850), (640, 960), (662, 1060), (692, 1150)),
                ((450, 940), (440, 1020), (462, 1100), (452, 1196))]:
        c.soft_path([tuple(p) for p in pts], KNIT_DEEP, alpha=80, width=9, radius=8)
    # luz vinda da direita no suéter
    c.soft_path([(722, 768), (760, 900), (782, 1080), (786, 1196)], (255, 250, 235),
                alpha=70, width=12, radius=10)
    # bainha
    c.tapered((124, 1140), (300, 1156), (600, 1156), (776, 1140), KNIT_LN, 3.6, 22, .4)


def hand_cup(c, hx, hy):
    # copo take-away
    c.poly([(hx - 34, hy - 98), (hx + 34, hy - 98), (hx + 27, hy + 28), (hx - 27, hy + 28)],
           (252, 250, 253), LINE, 2)
    c.poly([(hx - 31, hy - 74), (hx + 31, hy - 74), (hx + 26, hy - 28), (hx - 26, hy - 28)],
           (152, 104, 68))
    c.soft_ell((hx - 26, hy - 70, hx - 4, hy - 32), (110, 70, 40), alpha=70, radius=4)
    c.poly([(hx - 38, hy - 106), (hx + 38, hy - 106), (hx + 34, hy - 92), (hx - 34, hy - 92)],
           (212, 86, 78), LINE, 2)
    for i in range(3):
        x = hx - 8 + i * 9
        c.tapered((x, hy - 106), (x - 5, hy - 132), (x + 6, hy - 150), (x, hy - 174),
                  (255, 255, 255), 2.2, 16, .5)
    # palma atrás
    c.poly([(hx - 40, hy - 6), (hx + 48, hy - 8), (hx + 54, hy + 62), (hx - 30, hy + 66)],
           SKIN, LINE, 2)
    # dedos à frente com unhas
    for i in range(4):
        y = hy - 52 + i * 21
        c.poly([(hx - 34, y), (hx + 30, y - 4), (hx + 35, y + 9), (hx - 30, y + 16)], SKIN, LINE, 2)
        c.ell((hx + 22, y - 1, hx + 34, y + 10), SKIN_SH, LINE, 1)
        c.ell((hx + 24, y + 1, hx + 32, y + 8), (255, 224, 216), None, 0)  # unha
    # polegar por cima
    c.tapered((hx + 42, hy + 14), (hx + 48, hy - 22), (hx + 32, hy - 48), (hx + 6, hy - 54),
              SKIN, 15, 20, .5)
    c.ell((hx - 2, hy - 62, hx + 16, hy - 46), SKIN, LINE, 2)
    c.ell((hx - 2, hy - 60, hx + 8, hy - 50), (255, 224, 216), None, 0)
    # punho de tricô
    c.poly([(hx - 46, hy + 46), (hx + 54, hy + 42), (hx + 68, hy + 98), (hx - 32, hy + 102)],
           KNIT, KNIT_LN, 2)
    c.soft_path([(hx - 40, hy + 60), (hx + 20, hy + 56), (hx + 60, hy + 72)], KNIT_DEEP,
                alpha=80, width=6, radius=4)


def hand_hair(c, hx, hy):
    # manga subindo
    c.poly([(hx + 96, hy + 258), (hx + 142, hy + 96), (hx + 106, hy + 62), (hx + 58, hy + 216)],
           KNIT, KNIT_LN, 2)
    for i in range(4):
        x = hx + 62 + i * 20
        c.tapered((x + 8, hy + 224), (x + 18, hy + 164), (x + 14, hy + 120), (x + 4, hy + 72),
                  KNIT_SH, 2.4, 12, .5)
    # punho
    c.poly([(hx + 58, hy + 86), (hx + 110, hy + 66), (hx + 96, hy + 36), (hx + 48, hy + 54)],
           KNIT_SH, KNIT_LN, 2)
    # palma
    c.poly([(hx - 14, hy + 62), (hx + 44, hy + 68), (hx + 52, hy + 12), (hx - 8, hy + 4)],
           SKIN, LINE, 2)
    # quatro dedos longos puxando a mecha, com unhas
    for i in range(4):
        x = hx - 4 + i * 15
        lean = (i - 1.5) * 6
        c.tapered((x, hy + 8), (x + lean * .3, hy - 36), (x + lean * .7, hy - 68),
                  (x + lean, hy - 100 - i * 5), SKIN, 13, 22, .42)
        c.ell((x + lean - 6, hy - 110 - i * 5, x + lean + 6, hy - 96 - i * 5),
              SKIN_SH, LINE, 1)
        c.ell((x + lean - 4, hy - 108 - i * 5, x + lean + 4, hy - 98 - i * 5),
              (255, 224, 216), None, 0)
    # polegar
    c.tapered((hx - 10, hy + 36), (hx - 28, hy + 10), (hx - 32, hy - 18), (hx - 20, hy - 42),
              SKIN, 12, 16, .5)
    # mecha que os dedos puxam (fica por cima)
    c.tapered((hx + 12, hy - 96), (hx + 4, hy - 130), (hx - 6, hy - 160), (hx - 2, hy - 200),
              HAIR_D, 8, 16, .35)
    c.tapered((hx + 14, hy - 96), (hx + 8, hy - 128), (hx + 0, hy - 156), (hx + 4, hy - 190),
              HAIR_M, 3, 16, .35)


def post(c):
    img = c.im.resize((W, H), Image.LANCZOS)
    img = ImageEnhance.Color(img).enhance(1.05)
    img = ImageEnhance.Contrast(img).enhance(1.04)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=85, threshold=2))
    # vinheta leve com piso: nunca esmaga sombra em preto puro
    vig = Image.new('L', (W, H), 0)
    dv = ImageDraw.Draw(vig)
    dv.ellipse((-40, -60, W + 40, H + 60), fill=24)
    vig = vig.filter(ImageFilter.GaussianBlur(50))
    vig = vig.point(lambda v: min(255, v + 220))
    black = Image.new('RGB', (W, H), (14, 12, 16))
    img = Image.composite(img, black, vig)
    return img


def render() -> Image.Image:
    rng = random.Random(20260926)
    c = Paint()
    cx = 450
    background(c, rng)
    draw_back_hair(c, cx, rng)
    draw_body(c, rng)
    draw_face(c, cx)
    draw_eyes(c, cx)
    draw_nose_mouth(c, cx)
    draw_front_hair(c, cx)
    hand_cup(c, 322, 918)
    hand_hair(c, 560, 560)
    return post(c)


def main():
    ap = argparse.ArgumentParser(description="Personagem casual — Paint v2.")
    ap.add_argument("--output", default="personagem_casual_v2.png")
    args = ap.parse_args()
    dest = Path(args.output).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    render().save(dest, "PNG", optimize=True)
    print(f"Personagem casual v2 salva em: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
