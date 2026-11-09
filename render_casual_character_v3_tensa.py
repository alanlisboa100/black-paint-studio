#!/usr/bin/env python3
"""render_casual_character_v3.py — Misuki casual TENSA: pintura local do Paint, v3.

Identidade canônica (runtime memory V2): dois chifres pretos curvos (HC01),
cabelo preto muito longo (HC02), olhos vermelhos (HC-identidade), proporções
adultas, estética gótica elegante (HC03/HC04) — mas em ROUPA CASUAL dark:
tee preta + jaqueta jeans larga, mãos perfeitas segurando caséu de chá gelado.
Com calma: sombreamento suave, halo de brilho no cabelo, vinheta noir.
"""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H = 900, 1200
S = 3

SKIN = (250, 229, 224)
SKIN_SH = (233, 194, 188)
SKIN_DEEP = (215, 162, 156)
HAIR_D = (15, 12, 17)
HAIR_M = (43, 38, 48)
HAIR_H = (94, 84, 102)
HAIR_RIM = (148, 136, 158)
HORN = (26, 23, 28)
HORN_HI = (88, 82, 94)
LINE = (30, 24, 32)
TEE = (26, 25, 30)
TEE_SH = (16, 15, 19)
TEE_HL = (54, 53, 62)
DENIM = (48, 56, 74)
DENIM_SH = (34, 40, 54)
DENIM_ST = (166, 176, 190)
EYE_TOP = (255, 96, 108)
EYE_BOT = (138, 10, 28)
EYE_D = (62, 4, 14)
LIP = (198, 96, 108)
LIP_SH = (226, 150, 156)
BLUSH = (240, 168, 164)


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
        self.im = Image.new('RGB', (W * S, H * S), (18, 15, 22))

    def draw(self):
        return ImageDraw.Draw(self.im, 'RGB')

    def poly(self, pts, fill, outline=None, width=2):
        d = self.draw()
        d.polygon([_p(*pt) for pt in pts], fill=fill)
        if outline:
            p = [_p(*pt) for pt in pts] + [_p(*pts[0])]
            d.line(p, fill=outline, width=max(1, width * S), joint='curve')

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

    def radial_gradient(self, box, stops):
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
    # neon bokeh frio + um magenta (clima tenso de rua à noite)
    for _ in range(24):
        x = rng.randint(30, W - 30)
        y = rng.randint(40, H - 120)
        r = rng.randint(9, 44)
        tone = rng.choice([(60, 220, 230), (180, 60, 220), (255, 70, 96)])
        c.soft_ell((x - r, y - r, x + r, y + r), tone, alpha=rng.randint(14, 30), radius=11)
    # cruzes de luz (star filter)
    d = c.draw()
    for _ in range(5):
        x, y = rng.randint(60, W - 60), rng.randint(80, H - 200)
        ln = rng.randint(14, 26) * S
        col = (120, 220, 235, 120)
        lay = Image.new('RGBA', (ln * 2, ln * 2), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        dd.line([(ln, 0), (ln, ln * 2)], fill=col, width=2)
        dd.line([(0, ln), (ln * 2, ln)], fill=col, width=2)
        c.im.paste(lay, (x * S - ln, y * S - ln), lay)


def horns(c, cx):
    # HC01: dois chifres curvos assimétricos, com anéis e highlight
    for side in (-1, 1):
        base = (cx + side * 118, 258)
        mid1 = (cx + side * 152, 176)
        mid2 = (cx + side * 176, 104)
        tip = (cx + side * 150, 34)
        outer = cubic_points((base[0], base[1] + 18), (mid1[0] + side * 16, mid1[1]),
                             (mid2[0] + side * 18, mid2[1]), (tip[0] + side * 8, tip[1]), 20)
        inner = cubic_points((base[0], base[1] - 14), (mid1[0] - side * 8, mid1[1]),
                             (mid2[0] - side * 8, mid2[1]), tip, 20)[::-1]
        c.poly([base] + outer[1:] + inner[:-1], HORN, LINE, 2)
        c.tapered(*[p for p in (base, mid1, mid2, tip)], HORN_HI, 3.4, 20, .5)
        for i in range(4):
            t = .25 + i * .16
            px = base[0] + (tip[0] - base[0]) * t + side * 12 * math.sin(t * math.pi)
            py = base[1] + (tip[1] - base[1]) * t
            c.tapered((px - 10, py - 3), (px, py - 7), (px + 8, py - 7), (px + 14, py - 2),
                      HORN_HI, 2.2, 8, .5)


def draw_back_hair(c, cx, rng):
    c.poly([(cx - 268, 340), (cx - 356, 800), (cx - 330, 1196), (cx + 330, 1196),
            (cx + 356, 800), (cx + 268, 340)], HAIR_D)
    for i in range(52):
        t = i / 51
        x0 = cx - 266 + t * 532
        sway = math.sin(t * math.pi * 3 + 1.1) * 42
        tone = [HAIR_M, HAIR_D, HAIR_H][i % 3]
        c.tapered((x0, 292 + t * 74), (x0 - 50 + sway, 680), (x0 - 80 + sway, 980),
                  (x0 - 104 + sway * 1.4, 1196), tone, 2.2 + (i % 3), 30, .3)
    c.soft_path([(cx + 268, 372), (cx + 334, 660), (cx + 344, 940), (cx + 322, 1160)],
                HAIR_RIM, alpha=70, width=10, radius=9)
    c.soft_path([(cx - 268, 372), (cx - 334, 660), (cx - 344, 940), (cx - 322, 1160)],
                (70, 120, 190), alpha=40, width=8, radius=9)


def draw_face(c, cx):
    left = cubic_points((cx - 150, 322), (cx - 166, 466), (cx - 130, 588), (cx - 6, 680), 30)
    right = [(cx + (cx - p[0]), p[1]) for p in left][::-1]
    c.poly([(cx - 150, 314)] + left + right + [(cx + 150, 314)], SKIN)
    c.soft_poly([(cx - 150, 396), (cx - 136, 566), (cx - 66, 658), (cx - 54, 596),
                 (cx - 100, 496), (cx - 118, 396)], SKIN_SH, alpha=88, radius=9)
    c.soft_ell((cx - 118, 594, cx + 118, 698), SKIN_SH, alpha=66, radius=12)
    for side in (-1, 1):
        ex = cx + side * 156
        c.ell((ex - 16, 448, ex + 16, 538), SKIN, LINE, 2)


def draw_eyes(c, cx):
    for side in (-1, 1):
        ex, ey = cx + side * 80, 500
        rx, ry = 53, 41
        c.poly([(ex - rx, ey), (ex - rx * .55, ey - ry * .78), (ex + rx * .5, ey - ry * .8),
                (ex + rx, ey - ry * .1), (ex + rx * .5, ey + ry * .82), (ex - rx * .5, ey + ry * .8)],
               (253, 250, 251), LINE, 2)
        c.radial_gradient((ex - 31, ey - 27, ex + 31, ey + 31), (EYE_TOP, EYE_BOT))
        c.ell((ex - 13, ey - 11, ex + 13, ey + 15), EYE_D)
        # anel escuro externo da íris + linhas radiais
        d = c.draw()
        ring = [_p(ex - 31, ey - 27), _p(ex + 31, ey + 31)]
        d.ellipse((ring[0][0], ring[0][1], ring[1][0], ring[1][1]), outline=(50, 4, 12, 255)[:3],
                  width=2 * S)
        for i in range(9):
            a = math.pi * (i / 8)
            x1 = ex + math.cos(a) * 24
            y1 = ey + math.sin(a) * 26
            x2 = ex + math.cos(a) * 12
            y2 = ey + math.sin(a) * 13
            d.line([_p(x1, y1), _p(x2, y2)], fill=(255, 150, 160), width=1 * S)
        c.soft_poly([(ex - 33, ey - 27), (ex + 33, ey - 27), (ex + 21, ey - 4), (ex - 19, ey - 6)],
                    (90, 20, 30), alpha=90, radius=4)
        c.ell((ex - 23, ey - 23, ex - 3, ey - 3), (255, 255, 255))
        c.ell((ex + 9, ey + 7, ex + 19, ey + 17), (255, 210, 214))
        # glow vermelho sutil do olho no clima dark
        c.soft_ell((ex - 34, ey - 30, ex + 34, ey + 34), (255, 60, 80), alpha=26, radius=12)
        c.tapered((ex - rx - 2, ey - 6), (ex - rx * .4, ey - ry - 8), (ex + rx * .3, ey - ry - 10),
                  (ex + rx + 6, ey - 4), LINE, 8.5, 22, .25)
        c.tapered((ex + rx, ey - 8), (ex + rx + 14, ey - 14), (ex + rx + 20, ey - 22),
                  (ex + rx + 24, ey - 34), LINE, 5, 10, .3)
        c.tapered((ex - rx * .6, ey + ry * .8), (ex, ey + ry * .95), (ex + rx * .5, ey + ry * .85),
                  (ex + rx * .9, ey + ry * .45), LINE, 2.6, 14, .4)
        c.tapered((ex - rx, ey - ry - 36), (ex - 10, ey - ry - 54), (ex + 18, ey - ry - 54),
                  (ex + rx - 4, ey - ry - 32), HAIR_M, 5, 16, .3)


def draw_nose_mouth(c, cx):
    c.tapered((cx - 3, 546), (cx - 9, 558), (cx - 5, 568), (cx + 4, 570), SKIN_DEEP, 2.6, 8, .5)
    c.tapered((cx - 34, 596), (cx - 12, 614), (cx + 12, 614), (cx + 36, 594), LIP, 5.5, 16, .25)
    c.tapered((cx - 28, 604), (cx - 8, 622), (cx + 10, 622), (cx + 28, 602), LIP, 4.5, 14, .3)
    c.soft_ell((cx - 16, 610, cx + 16, 620), (255, 255, 255), alpha=52, radius=3)
    c.soft_ell((cx - 138, 528, cx - 50, 572), BLUSH, alpha=52, radius=12)
    c.soft_ell((cx + 50, 528, cx + 138, 572), BLUSH, alpha=52, radius=12)


def draw_front_hair(c, cx):
    crown = cubic_points((cx - 176, 462), (cx - 216, 278), (cx - 40, 168), (cx + 142, 190), 24) \
        + cubic_points((cx + 142, 190), (cx + 258, 222), (cx + 236, 414), (cx + 192, 484), 24)
    fringe = [(cx + 190, 480), (cx + 154, 400), (cx + 102, 366), (cx + 36, 410),
              (cx - 30, 354), (cx - 104, 396), (cx - 156, 402)]
    c.poly([(cx - 176, 462)] + crown + fringe, HAIR_D)
    tufts = [((cx - 188, 312), (cx - 158, 480), (cx - 178, 566), (cx - 208, 656)),
             ((cx - 126, 260), (cx - 100, 380), (cx - 126, 476), (cx - 158, 552)),
             ((cx - 34, 216), (cx - 12, 334), (cx - 56, 402), (cx - 92, 432)),
             ((cx + 64, 208), (cx + 90, 328), (cx + 56, 404), (cx + 26, 436)),
             ((cx + 154, 284), (cx + 142, 426), (cx + 164, 524), (cx + 188, 616)),
             ((cx + 200, 368), (cx + 192, 468), (cx + 210, 562), (cx + 222, 668))]
    for pts in tufts:
        c.tapered(*pts, HAIR_D, 17, 26, .35)
        c.tapered(*[(x + 4, y - 8) for x, y in pts], HAIR_M, 4.5, 26, .35)
    c.soft_path(cubic_points((cx - 132, 280), (cx - 40, 232), (cx + 60, 230), (cx + 148, 270), 20),
                HAIR_H, alpha=110, width=13, radius=7)
    c.soft_path(cubic_points((cx - 116, 294), (cx - 30, 252), (cx + 52, 250), (cx + 130, 286), 20),
                HAIR_RIM, alpha=80, width=5, radius=4)
    for i in range(36):
        t = i / 35
        x0 = cx - 178 + t * 356
        c.tapered((x0, 220 + abs(x0 - cx) * .55), (x0 - 18, 330), (x0 - 30, 394),
                  (x0 - 40 - t * 22, 452 + (i * 53 % 70)),
                  HAIR_H if i % 4 == 0 else HAIR_M, 1.5, 22)


def choker(c, cx):
    # HC08: choker gótico preservado mesmo na roupa casual
    c.poly([(cx - 62, 700), (cx + 62, 700), (cx + 66, 728), (cx - 66, 728)], (18, 16, 22), LINE, 2)
    for i in range(5):
        x = cx - 44 + i * 22
        c.ell((x - 3, 706, x + 3, 712), (190, 184, 200), None, 0)
    c.ell((cx - 10, 724, cx + 10, 744), (210, 60, 80), (40, 10, 16), 2)  # pingente vermelho
    c.ell((cx - 6, 728, cx - 1, 733), (255, 200, 210), None, 0)


def draw_body(c, rng):
    # tee casual preta + jaqueta jeans larga por cima (casual TENSA)
    c.poly([(196, 1196), (214, 840), (330, 748), (570, 748), (686, 840), (704, 1196)], TEE, LINE, 2)
    c.poly([(252, 748), (450, 806), (648, 748), (688, 880), (450, 950), (212, 880)], TEE_SH)
    c.soft_path([(300, 758), (450, 818), (600, 758)], TEE_HL, alpha=60, width=6, radius=5)
    # decote da tee
    c.tapered((378, 748), (414, 776), (486, 776), (522, 748), TEE_HL, 3, 16, .4)
    # jaqueta jeans: painéis abertos
    for sx, x0, x1, x2, x3 in [(-1, 110, 150, 214, 196), (1, 790, 750, 686, 704)]:
        c.poly([(x0, 1196), (x1, 800), (x2, 730), (x3, 748), (x0 + sx * 6, 1196)],
               DENIM, LINE, 2)
    c.poly([(196, 748), (240, 730), (300, 748), (252, 880), (196, 1196), (150, 1196),
            (168, 880)], DENIM)
    c.poly([(704, 748), (660, 730), (600, 748), (648, 880), (704, 1196), (750, 1196),
            (732, 880)], DENIM)
    # gola da jaqueta + costuras
    c.poly([(240, 730), (330, 748), (300, 792), (222, 774)], DENIM_SH, LINE, 2)
    c.poly([(660, 730), (570, 748), (600, 792), (678, 774)], DENIM_SH, LINE, 2)
    for pts in [((182, 820), (176, 950), (182, 1080), (176, 1196)),
                ((718, 820), (724, 950), (718, 1080), (724, 1196))]:
        c.tapered(*pts, DENIM_ST, 1.8, 22, .5)
    c.soft_path([(230, 760), (260, 900), (240, 1050), (252, 1196)], DENIM_SH,
                alpha=90, width=10, radius=8)
    c.soft_path([(670, 760), (640, 900), (660, 1050), (648, 1196)], DENIM_SH,
                alpha=90, width=10, radius=8)
    # dobras suaves da tee
    for pts in [((420, 850), (408, 960), (426, 1060), (414, 1196)),
                ((480, 850), (492, 960), (476, 1060), (486, 1196))]:
        c.soft_path(list(pts), TEE_SH, alpha=120, width=9, radius=9)
    # rim light fria à direita
    c.soft_path([(700, 780), (744, 900), (762, 1060), (770, 1196)], (120, 190, 230),
                alpha=60, width=9, radius=8)
    # pescoço
    c.poly([(406, 598), (494, 598), (514, 716), (386, 716)], SKIN)
    c.soft_ell((398, 600, 502, 662), SKIN_DEEP, alpha=88, radius=8)


def cup_cold_tea(c, hx, hy):
    c.poly([(hx - 32, hy - 104), (hx + 32, hy - 104), (hx + 25, hy + 26), (hx - 25, hy + 26)],
           (238, 236, 240, 120)[:3], LINE, 2)
    c.poly([(hx - 30, hy - 58), (hx + 30, hy - 58), (hx + 25, hy + 24), (hx - 25, hy + 24)],
           (124, 62, 28))  # chá
    c.poly([(hx - 30, hy - 58), (hx + 30, hy - 58), (hx + 28, hy - 44), (hx - 28, hy - 44)],
           (148, 80, 40))
    c.poly([(hx - 35, hy - 112), (hx + 35, hy - 112), (hx + 31, hy - 100), (hx - 31, hy - 100)],
           (24, 22, 28), LINE, 2)  # tampa preta
    c.tapered((hx + 6, hy - 112), (hx + 10, hy - 138), (hx + 4, hy - 160), (hx + 12, hy - 186),
              (240, 60, 88), 6, 14, .5)  # canudo vermelho
    c.ell((hx - 12, hy - 30, hx + 2, hy - 6), (255, 255, 255, 200)[:3], None, 0)  # gelo
    c.ell((hx - 4, hy - 14, hx + 12, hy + 10), (255, 255, 255), None, 0)
    # gotas de condensação
    for _ in range(6):
        gx = hx + rng_g.randrange(-24, 24)
        gy = hy + rng_g.randrange(-46, 18)
        c.ell((gx, gy, gx + 4, gy + 6), (255, 255, 255), None, 0)


rng_g = random.Random(9)


def hand_cup(c, hx, hy):
    c.poly([(hx - 40, hy - 4), (hx + 48, hy - 6), (hx + 54, hy + 62), (hx - 30, hy + 66)],
           SKIN, LINE, 2)
    for i in range(4):
        y = hy - 50 + i * 20
        c.poly([(hx - 33, y), (hx + 29, y - 4), (hx + 34, y + 8), (hx - 29, y + 15)], SKIN, LINE, 2)
        c.ell((hx + 21, y - 1, hx + 33, y + 9), SKIN_SH, LINE, 1)
        c.ell((hx + 23, y + 1, hx + 31, y + 7), (255, 220, 214), None, 0)  # unha
        c.tapered((hx - 30, y + 4), (hx - 10, y + 2), (hx + 6, y + 2), (hx + 24, y + 4),
                  SKIN_SH, 1.6, 10, .4)  # nó do dedo
    c.tapered((hx + 42, hy + 12), (hx + 47, hy - 20), (hx + 32, hy - 44), (hx + 6, hy - 50),
              SKIN, 14, 20, .5)
    c.ell((hx - 2, hy - 58, hx + 15, hy - 43), SKIN, LINE, 2)
    c.ell((hx - 1, hy - 56, hx + 8, hy - 47), (255, 220, 214), None, 0)


def hand_hair(c, hx, hy):
    c.poly([(hx - 14, hy + 62), (hx + 44, hy + 68), (hx + 52, hy + 12), (hx - 8, hy + 4)],
           SKIN, LINE, 2)
    for i in range(4):
        x = hx - 4 + i * 15
        lean = (i - 1.5) * 6
        c.tapered((x, hy + 8), (x + lean * .3, hy - 36), (x + lean * .7, hy - 68),
                  (x + lean, hy - 100 - i * 5), SKIN, 13, 22, .42)
        c.ell((x + lean - 6, hy - 110 - i * 5, x + lean + 6, hy - 96 - i * 5), SKIN_SH, LINE, 1)
        c.ell((x + lean - 4, hy - 108 - i * 5, x + lean + 4, hy - 98 - i * 5),
              (255, 220, 214), None, 0)
    c.tapered((hx - 10, hy + 36), (hx - 28, hy + 10), (hx - 32, hy - 18), (hx - 20, hy - 42),
              SKIN, 12, 16, .5)
    c.tapered((hx + 12, hy - 96), (hx + 4, hy - 130), (hx - 6, hy - 160), (hx - 2, hy - 200),
              HAIR_D, 8, 16, .35)
    c.tapered((hx + 14, hy - 96), (hx + 8, hy - 128), (hx + 0, hy - 156), (hx + 4, hy - 190),
              HAIR_M, 3, 16, .35)
    # manga da jaqueta saindo do quadro
    c.poly([(hx + 96, hy + 258), (hx + 142, hy + 96), (hx + 106, hy + 62), (hx + 58, hy + 216)],
           DENIM, LINE, 2)
    c.poly([(hx + 58, hy + 86), (hx + 110, hy + 66), (hx + 96, hy + 36), (hx + 48, hy + 54)],
           DENIM_SH, LINE, 2)


def post(c):
    img = c.im.resize((W, H), Image.LANCZOS)
    img = ImageEnhance.Color(img).enhance(1.08)
    img = ImageEnhance.Contrast(img).enhance(1.10)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=95, threshold=2))
    vig = Image.new('L', (W, H), 0)
    dv = ImageDraw.Draw(vig)
    dv.ellipse((-30, -50, W + 30, H + 50), fill=30)
    vig = vig.filter(ImageFilter.GaussianBlur(60))
    vig = vig.point(lambda v: min(255, v + 176))  # piso: pretos profundos, não zero puro
    black = Image.new('RGB', (W, H), (6, 5, 9))
    return Image.composite(img, black, vig)


def render() -> Image.Image:
    rng = random.Random(20260927)
    c = Paint()
    cx = 450
    background(c, rng)
    draw_back_hair(c, cx, rng)
    horns(c, cx)
    draw_body(c, rng)
    choker(c, cx)
    draw_face(c, cx)
    draw_eyes(c, cx)
    draw_nose_mouth(c, cx)
    draw_front_hair(c, cx)
    cup_cold_tea(c, 322, 918)
    hand_cup(c, 322, 918)
    hand_hair(c, 560, 560)
    return post(c)


def main():
    ap = argparse.ArgumentParser(description="Misuki casual tensa — Paint v3.")
    ap.add_argument("--output", default="misuki_casual_tensa.png")
    args = ap.parse_args()
    dest = Path(args.output).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    render().save(dest, "PNG", optimize=True)
    print(f"Misuki casual tensa salva em: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
