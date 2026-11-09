#!/usr/bin/env python3
"""render_ibis_anime.py — Retrato anime em cel-shading estilo Ibis Paint X.

Aplicação local determinística (Pillow, sem difusão): lineart de G-Pen limpa,
cores planas em chapado, sombra em cel-shading dura, acentos de brilho (screen)
e a identidade da Misuki (cabelo preto longo, franja, dois chifres, olhos
vermelhos, vestido gótico com choker). Baixa superfície plana de 3x por estilo
Ibis: linha grossa + base chapada + sombra dura + glow opcional.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

W, H = 900, 1200
S = 3


class CelCanvas:
    """Canvas multi-camadas interpretando chapado + sombra + lineart separatista."""

    def __init__(self):
        self.w, self.h = W * S, H * S
        self.base = Image.new('RGBA', (self.w, self.h), (255, 255, 255, 0))
        self.shade = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))   # camada de sombra
        self.glow = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))    # camada de luz/glow
        self.line_img = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))    # lineart G-Pen

    @staticmethod
    def _pt(x, y):
        return (round(x * S), round(y * S))

    def fill(self, pts, color, canvas=None):
        c = canvas or self.base
        d = ImageDraw.Draw(c)
        d.polygon([self._pt(x, y) for x, y in pts], fill=color)

    def stroke(self, pts, color, width=2, canvas=None, cap='round'):
        c = canvas or self.line_img
        d = ImageDraw.Draw(c)
        pts = [self._pt(x, y) for x, y in pts]
        d.line(pts, fill=color, width=max(1, round(width * S)), joint='curve')

    def ellipse(self, box, fill=None, outline=None, width=2, canvas=None):
        c = canvas or self.line_img
        d = ImageDraw.Draw(c)
        b = (round(box[0] * S), round(box[1] * S), round(box[2] * S), round(box[3] * S))
        d.ellipse(b, fill=fill, outline=outline, width=max(1, round(width * S)))

    def polygon(self, pts, fill=None, outline=None, width=2, canvas=None):
        c = canvas or self.line_img
        d = ImageDraw.Draw(c)
        p = [self._pt(x, y) for x, y in pts]
        d.polygon(p, fill=fill)
        if outline:
            d.line(p + [p[0]], fill=outline, width=max(1, round(width * S)), joint='curve')

    def blend_all(self) -> Image.Image:
        # fundo transparente real: chapado na base, sombra multiplicada (cel),
        # glow em "screen" e a lineart por cima.
        layers = [
            self.base,
            self.shade,
            self.glow,
            self.line_img,
        ]
        out = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        for layer in layers:
            out.alpha_composite(layer)
        return out

    def composite(self, backdrop=(30, 28, 34, 255)):
        """Devolve imagem achatada (chapado) com fundo de estúdio dark."""
        flat = self.blend_all()
        bg = Image.new('RGBA', (self.w, self.h), backdrop)
        bg.alpha_composite(flat)
        return bg.convert('RGB')


def render(style: str = 'ibis') -> Image.Image:
    return render_cel().resize((W, H), Image.LANCZOS)


def render_cel() -> Image.Image:
    c = CelCanvas()
    skin = (247, 232, 229, 255)
    skin_shade = (225, 188, 186, 255)
    hair_d = (18, 14, 22, 255)
    hair_m = (58, 52, 66, 255)
    hair_glow = (140, 130, 160, 255)
    red = (198, 36, 62, 255)
    dark = (24, 20, 30, 255)
    cloth = (36, 32, 44, 255)
    cloth_shade = (20, 18, 26, 255)
    line_col = (34, 30, 40, 255)
    paper = (242, 240, 244, 255)

    cx = 450

    # ---- fundo chapado (estúdio) ----
    c.fill([(0, 0), (W, 0), (W, H), (0, H)], paper)

    # ---- cabelo de trás: quedas longas fechadas ----
    back_hair = [
        [(cx - 40, 300), (cx - 260, 320), (cx - 300, 700), (cx - 250, 1180), (cx - 60, 1195), (cx - 30, 800), (cx - 20, 500)],
        [(cx + 40, 300), (cx + 260, 320), (cx + 300, 700), (cx + 250, 1180), (cx + 60, 1195), (cx + 30, 800), (cx + 20, 500)],
    ]
    for poly in back_hair:
        c.polygon(poly, hair_d, None, 0)
    # sombra cel na queda esquerda (luz da direita)
    c.fill([(cx - 260, 420), (cx - 280, 760), (cx - 220, 1140), (cx - 150, 700)], (10, 8, 14, 255))

    # ---- pescoço e corpo: vestido gótico ----
    c.polygon([(402, 640), (498, 640), (520, 780), (380, 780)], skin, None, 0)
    c.polygon([(410, 660), (490, 660), (505, 700), (395, 700)], skin_shade, None, 0)
    # vestido: base + sombra cel dura
    c.polygon([(150, 780), (300, 720), (600, 720), (750, 780), (770, 1195), (130, 1195)], cloth, None, 0)
    c.polygon([(300, 720), (600, 720), (660, 880), (520, 1195), (240, 1195), (330, 880)], cloth_shade, None, 0)
    # decote/gola alta
    c.polygon([(320, 720), (580, 720), (620, 800), (560, 850), (340, 850), (280, 800)], (44, 40, 54, 255), None, 0)
    c.stroke([(340, 720), (560, 720)], (225, 228, 235, 255), 3)
    c.stroke([(420, 720), (420, 850)], line_col, 2)
    c.stroke([(480, 720), (480, 850)], line_col, 2)

    # ---- rosto ----
    c.polygon([(330, 300), (570, 300), (600, 430), (570, 560), (520, 660), (380, 660), (330, 560), (300, 430)], skin, None, 0)
    c.polygon([(330, 470), (305, 560), (340, 640), (420, 660), (420, 470)], skin_shade, None, 0)
    # bochecha blush chapado (cel)
    c.ellipse((330, 500, 420, 550), (240, 190, 196, 110), None, 0)
    c.ellipse((480, 500, 570, 550), (240, 190, 196, 110), None, 0)
    # nariz e boca
    c.stroke([(450, 500), (442, 526), (450, 532)], line_col, 2)
    c.stroke([(420, 600), (450, 614), (480, 600)], (150, 90, 100, 255), 3)

    # ---- olhos vermelhos expressivos com brilho ----
    for side in (-1, 1):
        ex = cx + side * 82
        c.ellipse((ex - 46, 428, ex + 6, 492), (255, 255, 255, 255), line_col, 4)  # branco
        c.ellipse((ex - 30, 440, ex + 24, 496), red, line_col, 3)                  # íris
        c.ellipse((ex - 18, 452, ex + 12, 488), (120, 8, 26, 255), None, 0)        # pupila
        c.ellipse((ex - 22, 452, ex - 8, 466), (255, 210, 220, 255), None, 0)      # brilho + topo
        c.ellipse((ex + 10, 470, ex + 18, 478), (255, 255, 255, 255), None, 0)     # brilho
        # cílios grossos G-Pen
        c.polygon([(ex - 46, 436), (ex + 6, 428), (ex - 24, 412), (ex - 52, 420)], hair_d, None, 0)
        c.stroke([(ex + 6, 430), (ex + 16, 424)], line_col, 3)

    # ---- sobrancelhas ----
    c.stroke([(cx - 130, 400), (cx - 52, 412)], line_col, 5)
    c.stroke([(cx + 52, 412), (cx + 130, 400)], line_col, 5)

    # ---- franja e cabelo frontal: massas chapadas com mechas ----
    c.polygon([(cx - 250, 200), (cx + 250, 200), (cx + 210, 430), (cx + 70, 400), (cx, 450), (cx - 70, 400), (cx - 210, 430)], hair_d, None, 0)
    # fiapos frontais
    for i in range(14):
        x = cx - 210 + i * 32
        pts = [(x, 220), (x - 18 + (i % 3) * 6, 400 + (i % 4) * 18), (x + 10, 330)]
        c.stroke(pts, hair_m, 2)
    # mecha clara para dar dimensão
    c.polygon([(cx - 60, 220), (cx + 20, 215), (cx + 40, 390), (cx - 30, 380)], (58, 52, 66, 255), None, 0)

    # ---- dois chifres curvos (góticos, simétricos mas orgânicos) ----
    for side in (-1, 1):
        pts = [
            (cx + side * 120, 220),
            (cx + side * 150, 120),
            (cx + side * 130, 70),
            (cx + side * 92, 150),
            (cx + side * 80, 205),
        ]
        c.polygon(pts, hair_d, (80, 76, 92, 255), 4)
        c.stroke([(cx + side * 100, 200), (cx + side * 128, 120)], (240, 240, 246, 255), 3)

    # ---- choker e acessórios ----
    c.polygon([(385, 690), (515, 690), (520, 730), (380, 730)], (18, 14, 22, 255), line_col, 4)
    c.ellipse((438, 688, 462, 736), (200, 208, 220, 255), None, 0)  # pingente
    c.stroke([(330, 720), (260, 840)], (200, 208, 220, 255), 3)      # corrente do ombro
    c.stroke([(570, 720), (640, 840)], (200, 208, 220, 255), 3)

    # ---- glow sutil nos olhos (camada screen) ----
    for side in (-1, 1):
        ex = cx + side * 82
        c.ellipse((ex - 30, 440, ex + 24, 496), (255, 90, 120, 70), None, 0, canvas=c.glow)

    return c.composite((242, 240, 244, 255))


def main():
    parser = argparse.ArgumentParser(description="Retrato anime cel-shading estilo Ibis Paint X.")
    parser.add_argument("--output", default="ibis_anime.png")
    args = parser.parse_args()
    dest = Path(args.output).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    render('ibis').save(dest, "PNG", optimize=True)
    print(f"Retrato anime Ibis salvo em: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())