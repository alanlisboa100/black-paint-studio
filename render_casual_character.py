#!/usr/bin/env python3
"""render_casual_character.py — Personagem completa pintada pelo motor do Black Paint Studio.

Estilo: anime adulto com cel-shading e lineart G-Pen (linguagem Ibis).
Alvo do pedido: extremamente linda, cabelo longo muito bem feito, roupa casual
(suéter de tricô creme), mãos perfeitas — uma segurando o copo de café, a outra
ajeitando a mecha. 100% local (Pillow), sem API de difusão.
"""
from __future__ import annotations

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

W, H = 900, 1200
S = 2

SKIN = (252, 232, 224)
SKIN_SH = (236, 197, 189)
SKIN_SH2 = (244, 212, 204)
HAIR_D = (34, 26, 32)
HAIR_M = (68, 48, 58)
HAIR_G = (152, 120, 132)
LINE = (48, 36, 44)
KNIT = (244, 235, 221)
KNIT_SH = (220, 205, 184)
KNIT_LN = (203, 186, 163)
EYE_A = (210, 138, 58)
EYE_D = (96, 48, 22)
LIP = (205, 116, 118)
BLUSH = (243, 178, 172)


def _p(*xy):
    return [round(v * S) for v in xy]


class Paint:
    def __init__(self):
        self.im = Image.new('RGB', (W * S, H * S), (247, 242, 238))
        self.d = ImageDraw.Draw(self.im, 'RGB')

    def poly(self, pts, fill, outline=None, width=2):
        self.d.polygon([_p(*pt) for pt in pts], fill=fill)
        if outline:
            p = [_p(*pt) for pt in pts] + [_p(*pts[0])]
            self.d.line(p, fill=outline, width=max(1, width * S), joint='curve')

    def ell(self, box, fill=None, outline=None, width=2):
        self.d.ellipse([round(v * S) for v in box], fill=fill, outline=outline,
                       width=max(1, width * S))

    def cubic(self, p0, p1, p2, p3, fill, wmax=3, steps=40, taper=0.35):
        pts = []
        for i in range(steps + 1):
            t = i / steps
            u = 1 - t
            x = u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0]
            y = u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]
            pts.append((x, y))
        for i in range(len(pts) - 1):
            t = (i + .5) / len(pts)
            press = taper + (1 - taper) * (math.sin(math.pi * t) ** .45)
            wd = max(1, round(wmax * press * S))
            a, b = _p(*pts[i]), _p(*pts[i + 1])
            self.d.line([a, b], fill=fill, width=wd)
            r = wd // 2
            if r:
                x, y = a
                self.d.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def bokeh(bg, rng):
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    for _ in range(26):
        x = rng.randint(20, W - 20) * S
        y = rng.randint(20, H - 20) * S
        r = rng.randint(8, 46) * S
        tone = rng.choice([(255, 226, 190), (255, 208, 226), (214, 236, 255)])
        dd.ellipse((x - r, y - r, x + r, y + r), fill=(*tone, rng.randint(22, 58)))
    lay = lay.filter(ImageFilter.GaussianBlur(9 * S))
    return Image.alpha_composite(bg.im.convert('RGBA'), lay).convert('RGB')


def hand_with_cup(c, hx, hy, flip=-1):
    """Mão esquerda do observador segurando copo de café take-away."""
    # copo primeiro, atrás dos dedos
    c.poly([(hx - 34, hy - 96), (hx + 34, hy - 96), (hx + 27, hy + 26), (hx - 27, hy + 26)],
           (250, 249, 252), LINE, 2)
    c.poly([(hx - 30, hy - 74), (hx + 30, hy - 74), (hx + 26, hy - 30), (hx - 26, hy - 30)],
           (150, 102, 66))  # luva de papelão
    c.poly([(hx - 37, hy - 104), (hx + 37, hy - 104), (hx + 34, hy - 92), (hx - 34, hy - 92)],
           (214, 88, 80), LINE, 2)  # tampa
    for i in range(3):  # canudo/vapor decorativo
        x = hx - 8 + i * 8
        c.cubic((x, hy - 104), (x - 4, hy - 128), (x + 5, hy - 146), (x, hy - 170),
                (255, 255, 255), 2.2, 24, 0.5)
    # palma por trás do copo
    c.poly([(hx - 40, hy - 8), (hx + 46, hy - 8), (hx + 52, hy + 60), (hx - 32, hy + 66)],
           SKIN, LINE, 2)
    # quatro dedos envolvendo a frente do copo
    for i in range(4):
        y = hy - 52 + i * 22
        c.poly([(hx - 34, y), (hx + 30, y - 4), (hx + 34, y + 9), (hx - 30, y + 15)],
               SKIN, LINE, 2)
        c.ell((hx + 22, y - 2, hx + 36, y + 10), SKIN_SH2, LINE, 1)  # pontas
    # polegar por cima
    c.cubic((hx + 40, hy + 12), (hx + 46, hy - 22), (hx + 30, hy - 46), (hx + 6, hy - 52),
            SKIN, 15, 22, 0.55)
    c.ell((hx - 2, hy - 60, hx + 16, hy - 44), SKIN, LINE, 2)
    # punho/tricô
    c.poly([(hx - 44, hy + 44), (hx + 52, hy + 40), (hx + 66, hy + 96), (hx - 30, hy + 100)],
           KNIT, KNIT_LN, 2)
    for i in range(5):
        x = hx - 34 + i * 20
        c.cubic((x, hy + 44), (x + 2, hy + 66), (x - 2, hy + 78), (x, hy + 98),
                KNIT_SH, 2.4, 12, 0.6)


def hand_tucking_hair(c, hx, hy):
    """Mão direita do observador levantada perto da bochecha, dedos longos puxando a mecha."""
    # antebraço (manga) entrando pela lateral
    c.poly([(hx + 96, hy + 250), (hx + 140, hy + 96), (hx + 104, hy + 66), (hx + 58, hy + 210)],
           KNIT, KNIT_LN, 2)
    for i in range(4):
        x = hx + 62 + i * 18
        c.cubic((x + 8, hy + 218), (x + 16, hy + 168), (x + 12, hy + 122), (x + 4, hy + 76),
                KNIT_SH, 2.2, 12, 0.6)
    # palma
    c.poly([(hx - 14, hy + 60), (hx + 44, hy + 66), (hx + 52, hy + 12), (hx - 8, hy + 4)],
           SKIN, LINE, 2)
    # quatro dedos longos apontando para cima entre a franja e o rosto
    for i in range(4):
        x = hx - 4 + i * 15
        lean = (i - 1.5) * 5
        c.cubic((x, hy + 8), (x + lean * .3, hy - 34), (x + lean * .7, hy - 66),
                (x + lean, hy - 96 - i * 4), SKIN, 13, 22, 0.42)
        c.ell((x + lean - 6, hy - 104 - i * 4, x + lean + 6, hy - 92 - i * 4),
              SKIN_SH2, LINE, 1)
    # polegar
    c.cubic((hx - 10, hy + 34), (hx - 26, hy + 10), (hx - 30, hy - 16), (hx - 18, hy - 38),
            SKIN, 12, 16, 0.5)


def render() -> Image.Image:
    rng = random.Random(20260926)
    c = Paint()
    cx = 450

    # ===== CABELO TRASEIRO: massa longa e cheia =====
    c.poly([(cx - 260, 360), (cx - 330, 760), (cx - 300, 1196), (cx + 300, 1196),
            (cx + 330, 760), (cx + 260, 360)], HAIR_D)
    c.poly([(cx - 300, 620), (cx - 336, 900), (cx - 306, 1196), (cx - 240, 1196),
            (cx - 250, 860)], HAIR_M)
    c.poly([(cx + 300, 620), (cx + 336, 900), (cx + 306, 1196), (cx + 240, 1196),
            (cx + 250, 860)], HAIR_M)
    for i in range(34):  # mechas longas com caimento
        t = i / 33
        x0 = cx - 250 + t * 500
        sway = math.sin(t * math.pi * 3 + 1.2) * 34
        c.cubic((x0, 300 + t * 60), (x0 - 40 + sway, 640), (x0 - 70 + sway, 940),
                (x0 - 88 + sway * 1.4, 1196), HAIR_M if i % 3 else HAIR_D, 2.6, 30)
    for i in range(9):  # brilho alto da coroa (cintilô)
        x0 = cx - 150 + i * 38
        c.cubic((x0, 268), (x0 + 18, 330), (x0 + 30, 392), (x0 + 20, 452), HAIR_G, 1.9, 16, .5)

    # ===== CORPO: suéter de tricô creme =====
    c.poly([(120, 1196), (150, 860), (250, 748), (370, 706), (530, 706), (650, 748),
            (750, 860), (780, 1196)], KNIT, KNIT_LN, 2)
    c.poly([(300, 748), (450, 800), (600, 748), (640, 880), (450, 940), (260, 880)],
           KNIT_SH)  # dobra da gola relaxada
    c.cubic((258, 760), (350, 820), (550, 820), (642, 760), KNIT_LN, 3, 22, .5)
    for i in range(16):  # costelas do tricô
        x = 168 + i * 38
        c.cubic((x, 800 + abs(x - 450) * .28), (x + 4, 940), (x - 4, 1060), (x, 1196),
                KNIT_SH, 2.2, 18, .55)
    # bainha
    c.cubic((132, 1140), (300, 1156), (600, 1156), (768, 1140), KNIT_LN, 3.4, 24, .5)

    # ===== PESCOÇO E ROSTO =====
    c.poly([(406, 604), (494, 604), (512, 712), (388, 712)], SKIN)
    c.poly([(406, 604), (494, 604), (500, 650), (400, 650)], SKIN_SH)  # sombra do queixo
    c.ell((cx - 150, 306, cx + 150, 668), SKIN)  # rosto
    c.poly([(cx - 150, 470), (cx - 118, 600), (cx, 672), (cx + 118, 600),
            (cx + 150, 470), (cx + 150, 330), (cx - 150, 330)], SKIN)
    c.poly([(cx - 150, 460), (cx - 128, 600), (cx - 46, 664), (cx - 46, 460)], SKIN_SH)
    # orelhas discretas
    c.ell((cx - 166, 452, cx - 134, 540), SKIN, LINE, 2)
    c.ell((cx + 134, 452, cx + 166, 540), SKIN, LINE, 2)

    # ===== OLHOS grandes e luminosos =====
    for side in (-1, 1):
        ex, ey = cx + side * 76, 500
        c.poly([(ex - 44, ey - 6), (ex - 22, ey - 22), (ex + 24, ey - 20), (ex + 44, ey + 2),
                (ex + 20, ey + 26), (ex - 22, ey + 24)], (252, 250, 250))
        c.ell((ex - 24, ey - 18, ex + 26, ey + 26), EYE_A, LINE, 3)
        c.ell((ex - 12, ey - 6, ex + 14, ey + 22), EYE_D)
        c.ell((ex - 10, ey - 22, ex + 8, ey - 4), (255, 255, 255))  # catchlight alto
        c.ell((ex + 10, ey + 8, ex + 20, ey + 18), (255, 236, 208, 255)[:3])  # catchlight sob
        # cílios superiores grossos (G-Pen) + sobrancelha fina
        c.cubic((ex - 46, ey - 2), (ex - 24, ey - 28), (ex + 22, ey - 28), (ex + 48, ey - 8),
                LINE, 7, 18, .3)
        c.cubic((ex + 34, ey - 16), (ex + 46, ey - 22), (ex + 54, ey - 28), (ex + 58, ey - 36),
                LINE, 4, 8, .4)
        c.cubic((ex - 50, ey - 44), (ex - 20, ey - 58), (ex + 18, ey - 58), (ex + 46, ey - 46),
                HAIR_M, 5, 14, .35)
        for k in range(3):  # cílios inferiores
            x = ex - 20 + k * 20
            c.cubic((x, ey + 26), (x + 4, ey + 30), (x + 6, ey + 32), (x + 8, ey + 36),
                    LINE, 2.2, 6, .5)

    # nariz + boca sorridente
    c.cubic((cx - 2, 540), (cx - 8, 556), (cx - 4, 564), (cx + 4, 566), SKIN_SH, 3, 8, .5)
    c.cubic((cx - 34, 596), (cx - 10, 616), (cx + 14, 616), (cx + 36, 594), LIP, 5, 14, .3)
    c.cubic((cx - 26, 604), (cx - 6, 622), (cx + 12, 622), (cx + 28, 602),
            (226, 150, 150), 3.2, 12, .4)
    # blush chapado
    blush = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blush)
    bd.ellipse([round(v * S) for v in (cx - 138, 532, cx - 52, 578)], fill=(*BLUSH, 70))
    bd.ellipse([round(v * S) for v in (cx + 52, 532, cx + 138, 578)], fill=(*BLUSH, 70))
    blush = blush.filter(ImageFilter.GaussianBlur(6 * S))
    c.im = Image.alpha_composite(c.im.convert('RGBA'), blush).convert('RGB')
    c.d = ImageDraw.Draw(c.im, 'RGB')

    # ===== CABELO FRONTAL: franja em camadas moldando o rosto =====
    c.poly([(cx - 176, 470), (cx - 190, 300), (cx - 60, 210), (cx + 130, 214),
            (cx + 196, 320), (cx + 182, 480), (cx + 150, 400), (cx + 96, 366),
            (cx + 30, 408), (cx - 36, 356), (cx - 104, 396), (cx - 156, 402)], HAIR_D)
    tufts = [((cx - 180, 320), (cx - 150, 470), (cx - 168, 560), (cx - 196, 640)),
             ((cx - 120, 280), (cx - 96, 380), (cx - 120, 470), (cx - 150, 540)),
             ((cx - 30, 240), (cx - 10, 340), (cx - 52, 400), (cx - 86, 430)),
             ((cx + 60, 232), (cx + 86, 330), (cx + 52, 402), (cx + 22, 436)),
             ((cx + 150, 300), (cx + 136, 430), (cx + 158, 520), (cx + 180, 610)),
             ((cx + 196, 380), (cx + 188, 470), (cx + 204, 560), (cx + 216, 660))]
    for pts in tufts:
        c.cubic(*pts, HAIR_D, 16, 24, .4)
        c.cubic(*[(x + 3, y - 6) for x, y in pts], HAIR_M, 4, 24, .4)
    for i in range(26):  # fios finos sobre a franja
        t = i / 25
        x0 = cx - 170 + t * 340
        c.cubic((x0, 236 + abs(x0 - cx) * .5), (x0 - 16, 330), (x0 - 26, 396),
                (x0 - 34 - t * 20, 460 + rng.uniform(-30, 60)), HAIR_M, 1.6, 20)

    # ===== MÃOS =====
    hand_with_cup(c, 322, 918)
    hand_tucking_hair(c, 560, 560)
    # dedos sobrepondo a mecha (reforço de profundidade)
    for i in range(4):
        x = 556 - 4 + i * 15
        c.cubic((x + 15, 520), (x + 18, 498), (x + 16, 480), (x + 12, 462),
                HAIR_D, 7, 10, .45)

    # bokeh quente por cima de tudo
    c.im = bokeh(c, rng)
    return c.im.resize((W, H), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser(description="Personagem casual completa — pintura local do Paint.")
    ap.add_argument("--output", default="personagem_casual.png")
    args = ap.parse_args()
    dest = Path(args.output).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    render().save(dest, "PNG", optimize=True)
    print(f"Personagem casual pintada pelo Paint salva em: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
