#!/usr/bin/env python3
"""Estudo de personagem natural — motor Black Paint Studio 1.9.4.

Massas, três valores e pinceladas direcionais. Sem modelo de IA.
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

from painting_methods import directional_brushstrokes

W, H = 900, 1200


def bezier(p0, p1, p2, p3, n=52):
    return [
        (
            (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t**3 * p3[0],
            (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t**3 * p3[1],
        )
        for t in (i / n for i in range(n + 1))
    ]


def path(draw, segments, color, width=3):
    pts = []
    for seg in segments:
        pts.extend(bezier(*seg))
    draw.line(pts, fill=color, width=width, joint="curve")


def shape(draw, segments, color):
    pts = []
    for seg in segments:
        pts.extend(bezier(*seg))
    draw.polygon(pts, fill=color)


def shade(im, mask, xy, radius, color, alpha):
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).ellipse(
        (xy[0] - radius, xy[1] - radius, xy[0] + radius, xy[1] + radius),
        fill=(*color, alpha),
    )
    overlay = overlay.filter(ImageFilter.GaussianBlur(max(3, radius * 0.42)))
    overlay.putalpha(ImageChops.multiply(overlay.getchannel("A"), mask))
    return Image.alpha_composite(im, overlay)


def grain(im, amount=11, seed=47):
    rng = random.Random(seed)
    noise = Image.new("L", im.size, 0)
    pix = noise.load()
    step = 2
    for y in range(0, H, step):
        for x in range(0, W, step):
            v = rng.randint(0, amount)
            for dy in range(step):
                for dx in range(step):
                    if x + dx < W and y + dy < H:
                        pix[x + dx, y + dy] = v
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    rgb = im.convert("RGB")
    return ImageChops.add(rgb, Image.merge("RGB", (noise, noise, noise)), scale=1.15, offset=0)


def render():
    im = Image.new("RGBA", (W, H), (214, 198, 172, 255))
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(bg, "RGBA")
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=(int(226 - 34 * t), int(206 - 40 * t), int(176 - 36 * t), 255))

    d.rounded_rectangle((36, 48, 292, 640), radius=10, fill=(168, 188, 178, 255))
    d.rounded_rectangle((50, 62, 278, 626), radius=6, fill=(132, 166, 158, 255))
    d.line((164, 62, 164, 626), fill=(210, 220, 208, 110), width=10)
    d.line((50, 344, 278, 344), fill=(210, 220, 208, 110), width=10)
    d.ellipse((70, 120, 170, 250), fill=(236, 214, 140, 80))
    d.ellipse((150, 200, 270, 340), fill=(200, 222, 188, 55))
    d.ellipse((60, 430, 160, 560), fill=(118, 148, 128, 45))
    im = Image.alpha_composite(im, bg.filter(ImageFilter.GaussianBlur(8)))

    foliage = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(foliage, "RGBA")
    for box, col in (
        ((-90, 500, 170, 880), (78, 112, 72, 170)),
        ((-40, 680, 230, 1080), (56, 90, 58, 150)),
        ((10, 880, 250, 1260), (44, 72, 48, 140)),
        ((690, 820, 990, 1280), (68, 96, 66, 80)),
    ):
        fd.ellipse(box, fill=col)
    im = Image.alpha_composite(im, foliage.filter(ImageFilter.GaussianBlur(11)))
    d = ImageDraw.Draw(im, "RGBA")

    shirt = [
        ((150, 792), (110, 880), (84, 1040), (64, 1200)),
        ((64, 1200), (300, 1200), (450, 1200), (836, 1200)),
        ((836, 1200), (818, 1030), (786, 870), (748, 792)),
        ((748, 792), (628, 754), (450, 742), (270, 754)),
        ((270, 754), (210, 766), (172, 780), (150, 792)),
    ]
    shape(d, shirt, (228, 218, 202, 255))
    shirt_mask = Image.new("L", (W, H), 0)
    shape(ImageDraw.Draw(shirt_mask), shirt, 255)
    im = shade(im, shirt_mask, (250, 980), 300, (164, 146, 124), 88)
    im = shade(im, shirt_mask, (640, 900), 250, (214, 200, 180), 64)
    im = shade(im, shirt_mask, (380, 820), 140, (244, 236, 220), 46)
    d = ImageDraw.Draw(im, "RGBA")
    d.polygon([(388, 748), (450, 846), (512, 748), (500, 748), (450, 820), (400, 748)], fill=(210, 198, 180, 255))
    path(d, [((292, 770), (330, 910), (348, 1050), (328, 1190))], (186, 168, 146, 120), 3)
    path(d, [((608, 770), (568, 910), (552, 1050), (572, 1190))], (186, 168, 146, 100), 3)

    neck = [
        ((396, 618), (400, 692), (390, 746), (376, 772)),
        ((376, 772), (422, 806), (478, 806), (524, 772)),
        ((524, 772), (510, 746), (502, 690), (506, 618)),
        ((506, 618), (470, 640), (430, 640), (396, 618)),
    ]
    shape(d, neck, (210, 160, 134, 255))
    neck_mask = Image.new("L", (W, H), 0)
    shape(ImageDraw.Draw(neck_mask), neck, 255)
    im = shade(im, neck_mask, (428, 724), 92, (160, 104, 90), 84)
    im = shade(im, neck_mask, (488, 658), 68, (232, 190, 162), 48)
    d = ImageDraw.Draw(im, "RGBA")

    hair_back = [
        ((198, 350), (170, 168), (292, 58), (450, 48)),
        ((450, 48), (628, 54), (748, 168), (768, 352)),
        ((768, 352), (798, 560), (818, 830), (842, 1136)),
        ((842, 1136), (708, 1184), (638, 980), (618, 808)),
        ((618, 808), (598, 660), (578, 520), (552, 410)),
        ((348, 410), (318, 540), (286, 730), (238, 920)),
        ((238, 920), (186, 1090), (122, 1170), (64, 1108)),
        ((64, 1108), (118, 820), (168, 540), (198, 350)),
    ]
    shape(d, hair_back, (58, 36, 26, 255))
    hair_mask = Image.new("L", (W, H), 0)
    shape(ImageDraw.Draw(hair_mask), hair_back, 255)
    im = shade(im, hair_mask, (300, 250), 270, (128, 78, 46), 96)
    im = shade(im, hair_mask, (640, 380), 290, (38, 24, 18), 86)
    im = shade(im, hair_mask, (220, 720), 230, (96, 58, 36), 72)
    im = shade(im, hair_mask, (450, 90), 160, (150, 96, 58), 50)
    d = ImageDraw.Draw(im, "RGBA")

    face = [
        ((322, 298), (362, 210), (450, 196), (546, 220)),
        ((546, 220), (614, 278), (628, 392), (606, 504)),
        ((606, 504), (582, 596), (528, 656), (452, 672)),
        ((452, 672), (370, 654), (314, 584), (294, 492)),
        ((294, 492), (278, 398), (286, 328), (322, 298)),
    ]
    face_mask = Image.new("L", (W, H), 0)
    shape(ImageDraw.Draw(face_mask), face, 255)
    shape(d, face, (228, 180, 152, 255))
    im = shade(im, face_mask, (568, 430), 188, (168, 104, 86), 82)
    im = shade(im, face_mask, (338, 352), 156, (248, 214, 186), 90)
    im = shade(im, face_mask, (450, 608), 118, (206, 132, 114), 58)
    im = shade(im, face_mask, (358, 508), 72, (232, 146, 136), 34)
    im = shade(im, face_mask, (528, 508), 72, (206, 122, 112), 26)
    im = shade(im, face_mask, (450, 336), 96, (246, 214, 188), 38)
    d = ImageDraw.Draw(im, "RGBA")

    d.ellipse((266, 428, 314, 514), fill=(218, 164, 138, 255))
    d.ellipse((586, 426, 636, 516), fill=(194, 138, 118, 255))
    d.arc((270, 436, 310, 506), 200, 80, fill=(160, 102, 86, 150), width=3)
    d.arc((590, 436, 632, 506), 100, 340, fill=(146, 92, 80, 150), width=3)

    crown = [
        ((228, 344), (242, 138), (348, 62), (450, 54)),
        ((450, 54), (572, 60), (698, 140), (714, 336)),
        ((714, 336), (668, 372), (604, 348), (546, 286)),
        ((546, 286), (488, 218), (392, 222), (322, 300)),
        ((322, 300), (278, 348), (246, 366), (228, 344)),
    ]
    shape(d, crown, (74, 44, 30, 255))
    shape(d, [((308, 220), (350, 268), (372, 338), (352, 404)), ((352, 404), (322, 428), (300, 392), (296, 328)), ((296, 328), (294, 268), (298, 232), (308, 220))], (98, 58, 38, 255))
    shape(d, [((430, 88), (456, 148), (458, 214), (440, 276)), ((440, 276), (418, 254), (410, 176), (418, 112)), ((418, 112), (422, 94), (426, 88), (430, 88))], (48, 30, 20, 255))
    shape(d, [((512, 208), (574, 234), (612, 304), (598, 380)), ((598, 380), (568, 422), (532, 396), (518, 328)), ((518, 328), (512, 264), (506, 220), (512, 208))], (64, 38, 26, 255))
    path(d, [((428, 70), (436, 148), (438, 214), (426, 262))], (36, 22, 16, 190), 4)
    path(d, [((360, 120), (338, 196), (320, 270), (316, 328))], (138, 86, 52, 80), 7)
    path(d, [((540, 118), (566, 186), (580, 258), (578, 322))], (42, 26, 18, 100), 6)

    for x in (370, 530):
        y = 430
        d.ellipse((x - 36, y - 16, x + 38, y + 22), fill=(244, 220, 206, 255))
        d.ellipse((x - 14, y - 12, x + 15, y + 18), fill=(86, 116, 108, 255))
        d.ellipse((x - 7, y - 7, x + 7, y + 14), fill=(26, 30, 28, 255))
        d.ellipse((x - 12, y - 9, x - 3, y), fill=(252, 244, 228, 220))
        d.arc((x - 38, y - 20, x + 38, y + 8), 192, 352, fill=(60, 40, 32, 230), width=4)
        d.arc((x - 32, y + 2, x + 34, y + 22), 18, 162, fill=(164, 116, 100, 170), width=2)
        path(d, [((x - 34, y - 26), (x - 6, y - 38), (x + 16, y - 36), (x + 34, y - 22))], (70, 44, 34, 210), 4)

    path(d, [((448, 432), (444, 472), (438, 502), (452, 510))], (170, 112, 96, 150), 3)
    d.ellipse((438, 506, 450, 516), fill=(194, 124, 108, 130))
    d.ellipse((452, 506, 466, 516), fill=(182, 114, 100, 130))
    path(d, [((414, 560), (436, 550), (452, 554), (476, 550))], (162, 82, 82, 190), 3)
    path(d, [((416, 562), (438, 574), (454, 572), (474, 558))], (210, 120, 114, 170), 3)
    path(d, [((330, 394), (350, 382), (374, 382), (396, 392))], (76, 46, 34, 200), 4)
    path(d, [((504, 390), (526, 378), (550, 378), (572, 390))], (66, 40, 30, 200), 4)

    shape(d, [((220, 368), (176, 510), (154, 700), (188, 900)), ((188, 900), (248, 952), (296, 820), (302, 650)), ((302, 650), (298, 510), (266, 400), (242, 346)), ((242, 346), (232, 352), (224, 360), (220, 368))], (66, 40, 28, 255))
    shape(d, [((672, 348), (722, 500), (752, 700), (718, 916)), ((718, 916), (654, 968), (612, 820), (608, 640)), ((608, 640), (612, 490), (638, 380), (660, 332)), ((660, 332), (666, 338), (670, 344), (672, 348))], (50, 32, 22, 255))

    strokes = [
        ([(90, 70), (180, 190), (230, 340)], (214, 194, 154), 26, 0.16),
        ([(50, 210), (130, 350), (170, 520)], (170, 192, 176), 34, 0.14),
        ([(730, 70), (810, 220), (850, 430)], (230, 198, 158), 28, 0.12),
        ([(290, 170), (380, 140), (470, 132), (570, 168)], (112, 70, 44), 15, 0.26),
        ([(318, 250), (292, 338), (286, 430)], (92, 54, 36), 13, 0.20),
        ([(552, 230), (598, 318), (610, 412)], (54, 34, 24), 13, 0.20),
        ([(228, 500), (214, 690), (196, 880)], (72, 44, 30), 17, 0.18),
        ([(688, 470), (714, 660), (702, 860)], (48, 30, 20), 17, 0.18),
        ([(332, 350), (372, 418), (392, 500)], (246, 212, 186), 11, 0.14),
        ([(518, 372), (560, 448), (572, 532)], (170, 108, 90), 13, 0.16),
        ([(398, 560), (430, 600), (470, 622)], (210, 136, 118), 9, 0.14),
        ([(190, 820), (320, 862), (450, 882), (610, 848)], (236, 226, 210), 20, 0.16),
        ([(170, 970), (300, 1030), (430, 1090)], (172, 154, 132), 18, 0.14),
        ([(530, 970), (650, 1030), (750, 1110)], (164, 146, 124), 16, 0.12),
        ([(352, 428), (370, 426), (386, 430)], (34, 42, 38), 3, 0.18),
        ([(516, 426), (532, 424), (548, 428)], (34, 42, 38), 3, 0.18),
        ([(416, 558), (452, 552), (474, 548)], (164, 84, 82), 4, 0.20),
        ([(428, 78), (436, 164), (432, 236)], (38, 22, 16), 5, 0.14),
        ([(70, 700), (130, 830), (150, 990)], (68, 98, 70), 24, 0.12),
        ([(30, 910), (90, 1030), (130, 1170)], (46, 76, 50), 28, 0.14),
        ([(340, 348), (362, 366), (392, 380)], (248, 220, 196), 7, 0.09),
        ([(468, 758), (512, 778), (552, 790)], (248, 240, 224), 9, 0.09),
        ([(250, 300), (230, 420), (218, 560)], (120, 74, 46), 8, 0.12),
        ([(640, 290), (670, 430), (686, 580)], (86, 52, 34), 8, 0.10),
    ]
    im = directional_brushstrokes(im, strokes, seed=47)
    rgb = grain(im, amount=11, seed=47)
    rgb = ImageEnhance.Color(rgb).enhance(1.05)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.07)
    return rgb.filter(ImageFilter.SMOOTH)


def main():
    parser = argparse.ArgumentParser(description="Retrato natural pintado no motor Black Paint Studio.")
    parser.add_argument("--output", default="personagem_natural.png")
    args = parser.parse_args()
    dest = Path(args.output).expanduser()
    dest.parent.mkdir(parents=True, exist_ok=True)
    render().save(dest, "PNG", optimize=True)
    print(f"Estudo natural salvo em: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
