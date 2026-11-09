#!/usr/bin/env python3
"""
render_anime_art.py - Motor de Ilustração Anime de Alta Fidelidade (BLACKCORE KyoAni Engine)
Renderização em 3200x3200 SSAA com cel-shading suave, gradientes de airbrush,
detalhamento de pele, olhos cristalinos, cabelo multicamadas e iluminação volumétrica.
"""

import math, os, random, subprocess, sys, time
from pathlib import Path
from termux_compat import scan_media, output_dir
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

class AnimeStudioEngine:
    def __init__(self, target_w=1600, target_h=1600, ssaa=2):
        self.target_w = target_w
        self.target_h = target_h
        self.ssaa = ssaa
        self.w = target_w * ssaa
        self.h = target_h * ssaa
        self.cx = self.w // 2
        self.cy = self.h // 2

    def create_layer(self) -> tuple[Image.Image, ImageDraw.ImageDraw]:
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        return img, ImageDraw.Draw(img, "RGBA")

    def draw_smooth_bezier(self, draw: ImageDraw.ImageDraw, p0, p1, p2, p3, color, width=3, steps=60):
        """Desenha curvas de Bézier cúbicas suaves para contornos de cabelo e tecidos."""
        points = []
        for i in range(steps + 1):
            t = i / steps
            inv = 1 - t
            x = (inv**3 * p0[0] + 3 * inv**2 * t * p1[0] + 3 * inv * t**2 * p2[0] + t**3 * p3[0])
            y = (inv**3 * p0[1] + 3 * inv**2 * t * p1[1] + 3 * inv * t**2 * p2[1] + t**3 * p3[1])
            points.append((x, y))
        
        for i in range(len(points) - 1):
            t = i / steps
            w_factor = math.sin(t * math.pi) * 0.8 + 0.4
            w = max(1, int(width * w_factor))
            draw.line([points[i], points[i+1]], fill=color, width=w)

    def render_illustration(self) -> Image.Image:
        w, h = self.w, self.h
        cx, cy = self.cx, self.cy

        # ----------------------------------------------------
        # 1. CAMADA DE FUNDO ATMOSFÉRICO (BOKEH & NEON)
        # ----------------------------------------------------
        bg = Image.new("RGBA", (w, h), (8, 6, 16, 255))
        bg_draw = ImageDraw.Draw(bg, "RGBA")

        # Gradiente suave de estúdio
        for y in range(h):
            t = y / h
            r = int(6 + t * 20)
            g = int(4 + t * 8)
            b = int(14 + t * 30)
            bg_draw.line([0, y, w, y], fill=(r, g, b, 255))

        # Arquitetura e luzes bokeh suaves
        bg_fx, bg_fx_draw = self.create_layer()
        for _ in range(25):
            bx = random.randint(int(w*0.05), int(w*0.95))
            by = random.randint(int(h*0.05), int(h*0.85))
            br = random.randint(int(30*self.ssaa), int(140*self.ssaa))
            alpha = random.randint(10, 45)
            c = random.choice([(255, 20, 60), (180, 0, 80), (120, 0, 180), (0, 200, 255)])
            bg_fx_draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(*c, alpha))

        bg_fx = bg_fx.filter(ImageFilter.GaussianBlur(int(25 * self.ssaa)))
        canvas = Image.alpha_composite(bg, bg_fx)

        # Luz Vermelha Volumétrica Traseira (Rim Light)
        rim, rim_draw = self.create_layer()
        r_radius = int(w * 0.42)
        for r in range(r_radius, 0, -int(8 * self.ssaa)):
            t = 1 - (r / r_radius)
            alpha = int(160 * (t**1.8))
            rim_draw.ellipse([cx - r, cy - r - int(40*self.ssaa), cx + r, cy + r - int(40*self.ssaa)], fill=(255, 15, 50, alpha))

        rim = rim.filter(ImageFilter.GaussianBlur(int(40 * self.ssaa)))
        canvas = Image.alpha_composite(canvas, rim)

        # ----------------------------------------------------
        # 2. MASSA DE CABELO TRASEIRA (VOLUME & SOMBRA)
        # ----------------------------------------------------
        hair_bg, hb_draw = self.create_layer()
        
        # Massa sólida escura
        hb_draw.polygon([
            (cx - int(120*self.ssaa), cy - int(280*self.ssaa)),
            (cx - int(380*self.ssaa), cy - int(180*self.ssaa)),
            (cx - int(520*self.ssaa), cy + int(120*self.ssaa)),
            (cx - int(450*self.ssaa), h),
            (cx + int(450*self.ssaa), h),
            (cx + int(520*self.ssaa), cy + int(120*self.ssaa)),
            (cx + int(380*self.ssaa), cy - int(180*self.ssaa)),
            (cx + int(120*self.ssaa), cy - int(280*self.ssaa))
        ], fill=(8, 8, 14, 255))

        # Mechas volumosas em feixes
        for _ in range(350):
            side = -1 if random.random() > 0.49 else 1
            x0 = cx + side * random.randint(int(50*self.ssaa), int(340*self.ssaa))
            y0 = cy - random.randint(int(180*self.ssaa), int(290*self.ssaa))
            
            p1 = (x0 + side * random.randint(int(80*self.ssaa), int(260*self.ssaa)), y0 + random.randint(int(150*self.ssaa), int(380*self.ssaa)))
            p2 = (x0 + side * random.randint(int(30*self.ssaa), int(200*self.ssaa)), y0 + random.randint(int(400*self.ssaa), int(700*self.ssaa)))
            p3 = (x0 + side * random.randint(int(10*self.ssaa), int(150*self.ssaa)), h)

            c_rand = random.random()
            if c_rand > 0.72:
                # Reflexo frio azul/prata
                color = (100, 135, 200, random.randint(90, 170))
                sw = random.randint(int(2*self.ssaa), int(5*self.ssaa))
            elif c_rand > 0.35:
                color = (24, 30, 50, 220)
                sw = random.randint(int(4*self.ssaa), int(10*self.ssaa))
            else:
                color = (7, 7, 12, 255)
                sw = random.randint(int(5*self.ssaa), int(15*self.ssaa))

            self.draw_smooth_bezier(hb_draw, (x0, y0), p1, p2, p3, color, width=sw)

        canvas = Image.alpha_composite(canvas, hair_bg)

        # ----------------------------------------------------
        # 3. CORPO & ROUPA GÓTICA
        # ----------------------------------------------------
        body, b_draw = self.create_layer()
        shoulder_y = cy + int(240 * self.ssaa)
        
        # Vestido e corset
        b_draw.polygon([
            (cx - int(110*self.ssaa), cy + int(130*self.ssaa)),
            (cx + int(110*self.ssaa), cy + int(130*self.ssaa)),
            (cx + int(450*self.ssaa), h),
            (cx - int(450*self.ssaa), h)
        ], fill=(10, 10, 15, 255))

        corset_top = cy + int(200 * self.ssaa)
        b_draw.polygon([
            (cx - int(140*self.ssaa), corset_top),
            (cx + int(140*self.ssaa), corset_top),
            (cx + int(190*self.ssaa), h),
            (cx - int(190*self.ssaa), h)
        ], fill=(6, 6, 10, 255))

        # Detalhes carmesim sutis
        crimson = (210, 15, 45, 240)
        b_draw.line([(cx - int(140*self.ssaa), corset_top), (cx, corset_top + int(48*self.ssaa)), (cx + int(140*self.ssaa), corset_top)], fill=crimson, width=int(4 * self.ssaa))
        
        # Choker e rubi
        choker_y = cy + int(145 * self.ssaa)
        b_draw.rectangle([cx - int(62*self.ssaa), choker_y, cx + int(62*self.ssaa), choker_y + int(20*self.ssaa)], fill=(18, 18, 25, 255), outline=(170, 175, 195, 255), width=int(1.5*self.ssaa))
        gem_y = choker_y + int(32 * self.ssaa)
        b_draw.polygon([(cx, gem_y - int(14*self.ssaa)), (cx + int(11*self.ssaa), gem_y), (cx, gem_y + int(18*self.ssaa)), (cx - int(11*self.ssaa), gem_y)], fill=(240, 10, 45, 255))

        canvas = Image.alpha_composite(canvas, body)

        # ----------------------------------------------------
        # 4. ROSTO ANIME ANATOMIA & PELE PORCELANA
        # ----------------------------------------------------
        face, f_draw = self.create_layer()
        skin_base = (246, 242, 252, 255)

        # Pescoço
        f_draw.polygon([
            (cx - int(68*self.ssaa), cy + int(45*self.ssaa)),
            (cx + int(68*self.ssaa), cy + int(45*self.ssaa)),
            (cx + int(82*self.ssaa), cy + int(165*self.ssaa)),
            (cx - int(82*self.ssaa), cy + int(165*self.ssaa))
        ], fill=skin_base)

        # Sombra suave do pescoço
        f_draw.polygon([
            (cx - int(68*self.ssaa), cy + int(45*self.ssaa)),
            (cx + int(68*self.ssaa), cy + int(45*self.ssaa)),
            (cx + int(58*self.ssaa), cy + int(98*self.ssaa)),
            (cx - int(58*self.ssaa), cy + int(98*self.ssaa))
        ], fill=(200, 195, 218, 200))

        # Estrutura do Rosto Anime (Queixo delicado)
        face_pts = [
            (cx - int(146*self.ssaa), cy - int(150*self.ssaa)),
            (cx - int(162*self.ssaa), cy - int(38*self.ssaa)),
            (cx - int(152*self.ssaa), cy + int(32*self.ssaa)),
            (cx - int(110*self.ssaa), cy + int(96*self.ssaa)),
            (cx - int(55*self.ssaa), cy + int(141*self.ssaa)),
            (cx, cy + int(153*self.ssaa)),
            (cx + int(55*self.ssaa), cy + int(141*self.ssaa)),
            (cx + int(110*self.ssaa), cy + int(96*self.ssaa)),
            (cx + int(152*self.ssaa), cy + int(32*self.ssaa)),
            (cx + int(162*self.ssaa), cy - int(38*self.ssaa)),
            (cx + int(146*self.ssaa), cy - int(150*self.ssaa)),
            (cx, cy - int(202*self.ssaa))
        ]
        f_draw.polygon(face_pts, fill=skin_base)

        # Blush Suave em Degradê (Airbrush Effect)
        blush, bl_draw = self.create_layer()
        bl_draw.ellipse([cx - int(145*self.ssaa), cy + int(5*self.ssaa), cx - int(60*self.ssaa), cy + int(52*self.ssaa)], fill=(245, 175, 200, 100))
        bl_draw.ellipse([cx + int(60*self.ssaa), cy + int(5*self.ssaa), cx + int(145*self.ssaa), cy + int(52*self.ssaa)], fill=(245, 175, 200, 100))
        blush = blush.filter(ImageFilter.GaussianBlur(int(16 * self.ssaa)))
        face = Image.alpha_composite(face, blush)
        f_draw = ImageDraw.Draw(face, "RGBA")

        # Nariz e Boca
        nose_y = cy + int(25 * self.ssaa)
        f_draw.line([cx - int(4*self.ssaa), nose_y + int(18*self.ssaa), cx, nose_y + int(23*self.ssaa), cx + int(5*self.ssaa), nose_y + int(18*self.ssaa)], fill=(160, 150, 178, 220), width=int(2 * self.ssaa))

        mouth_y = cy + int(86 * self.ssaa)
        f_draw.polygon([
            (cx - int(36*self.ssaa), mouth_y),
            (cx - int(15*self.ssaa), mouth_y - int(5*self.ssaa)),
            (cx, mouth_y - int(2*self.ssaa)),
            (cx + int(15*self.ssaa), mouth_y - int(5*self.ssaa)),
            (cx + int(36*self.ssaa), mouth_y),
            (cx + int(18*self.ssaa), mouth_y + int(11*self.ssaa)),
            (cx, mouth_y + int(14*self.ssaa)),
            (cx - int(18*self.ssaa), mouth_y + int(11*self.ssaa))
        ], fill=(155, 18, 50, 240))
        f_draw.line([(cx - int(38*self.ssaa), mouth_y), (cx + int(38*self.ssaa), mouth_y)], fill=(38, 4, 10, 255), width=int(2 * self.ssaa))

        canvas = Image.alpha_composite(canvas, face)

        # ----------------------------------------------------
        # 5. CHIFRES DE OBSIDIANA (POLIDOS COM BRILHO)
        # ----------------------------------------------------
        horns, h_draw = self.create_layer()
        for side in [-1, 1]:
            bx = cx + side * int(122 * self.ssaa)
            by = cy - int(158 * self.ssaa)
            steps = 95
            for i in range(steps):
                t = i / steps
                hx = bx + side * (math.sin(t * math.pi * 0.85) * int(225*self.ssaa) + t * int(52*self.ssaa))
                hy = by - (t * int(390*self.ssaa) + math.cos(t * math.pi * 0.5) * int(52*self.ssaa))
                rad = (1 - t) * int(39 * self.ssaa) + int(2.5 * self.ssaa)
                h_draw.ellipse([hx - rad, hy - rad, hx + rad, hy + rad], fill=(8, 8, 14, 255))
                h_draw.ellipse([hx - rad*0.4, hy - rad*0.4, hx + rad*0.2, hy + rad*0.2], fill=(140, 160, 195, 50))
                rim_x = hx + side * (rad * 0.82)
                h_draw.ellipse([rim_x - int(3*self.ssaa), hy - int(3*self.ssaa), rim_x + int(3*self.ssaa), hy + int(3*self.ssaa)], fill=(255, 20, 55, 210))

        canvas = Image.alpha_composite(canvas, horns)

        # ----------------------------------------------------
        # 6. OLHOS CRISTALINOS VERMELHOS (PONTO FOCAL MAGNÉTICO)
        # ----------------------------------------------------
        eyes, e_draw = self.create_layer()
        eye_y = cy - int(30 * self.ssaa)
        eye_space = int(76 * self.ssaa)
        ew = int(48 * self.ssaa)
        eh = int(26 * self.ssaa)

        for side in [-1, 1]:
            ex = cx + side * eye_space
            brow_y = eye_y - int(35 * self.ssaa)

            # Sobrancelha expressiva
            e_draw.polygon([
                (ex - side * int(35*self.ssaa), brow_y + int(5*self.ssaa)),
                (ex - side * int(12*self.ssaa), brow_y - int(10*self.ssaa)),
                (ex + side * int(35*self.ssaa), brow_y - int(2*self.ssaa)),
                (ex + side * int(24*self.ssaa), brow_y - int(14*self.ssaa)),
                (ex - side * int(12*self.ssaa), brow_y - int(16*self.ssaa))
            ], fill=(16, 12, 22, 255))

            # Contorno e Esclera
            e_draw.ellipse([ex - ew, eye_y - eh, ex + ew, eye_y + eh], fill=(12, 10, 18, 255))
            e_draw.ellipse([ex - ew + int(3.5*self.ssaa), eye_y - eh + int(3.5*self.ssaa), ex + ew - int(3.5*self.ssaa), eye_y + eh - int(3.5*self.ssaa)], fill=(242, 242, 252, 255))

            # Halo de iluminação com intensidade alta
            iris_r = int(20 * self.ssaa)
            for gr in range(int(48 * self.ssaa), iris_r, -int(3 * self.ssaa)):
                t = 1 - (gr - iris_r) / (int(28 * self.ssaa))
                e_draw.ellipse([ex - gr, eye_y - gr, ex + gr, eye_y + gr], fill=(255, 0, 50, int(110 * t)))

            # Íris Rubi
            for ir in range(iris_r, 0, -int(2 * self.ssaa)):
                t = 1 - (ir / iris_r)
                ir_color = (int(185 + t * 70), int(t * 80), int(30 + t * 65), 255)
                e_draw.ellipse([ex - ir, eye_y - ir, ex + ir, eye_y + ir], fill=ir_color)

            # Micro-fibras radiantes
            for f_ang in range(0, 360, 25):
                rad_a = math.radians(f_ang + side * 4)
                fx1 = ex + math.cos(rad_a) * (iris_r * 0.25)
                fy1 = eye_y + math.sin(rad_a) * (iris_r * 0.25)
                fx2 = ex + math.cos(rad_a) * (iris_r * 0.88)
                fy2 = eye_y + math.sin(rad_a) * (iris_r * 0.88)
                e_draw.line([fx1, fy1, fx2, fy2], fill=(255, 140, 170, 160), width=int(1.2 * self.ssaa))

            # Pupila vertical
            e_draw.ellipse([ex - int(3*self.ssaa), eye_y - int(14*self.ssaa), ex + int(3*self.ssaa), eye_y + int(14*self.ssaa)], fill=(10, 0, 4, 255))

            # Múltiplos Catchlights (Brilho Estelar nos Olhos)
            e_draw.ellipse([ex - int(7*self.ssaa), eye_y - int(9*self.ssaa), ex - int(1*self.ssaa), eye_y - int(3*self.ssaa)], fill=(255, 255, 255, 255))
            e_draw.ellipse([ex + int(3*self.ssaa), eye_y + int(3*self.ssaa), ex + int(7*self.ssaa), eye_y + int(7*self.ssaa)], fill=(255, 210, 230, 240))

        canvas = Image.alpha_composite(canvas, eyes)

        # ----------------------------------------------------
        # 7. CABELO FRONTAL & FIOS SOLTOS (STRAY HAIRS)
        # ----------------------------------------------------
        hair_fg, hf_draw = self.create_layer()
        front_strands = [
            [(cx - int(145*self.ssaa), cy - int(200*self.ssaa)), (cx - int(115*self.ssaa), cy - int(100*self.ssaa)), (cx - int(140*self.ssaa), cy + int(50*self.ssaa)), (cx - int(160*self.ssaa), cy + int(240*self.ssaa))],
            [(cx + int(148*self.ssaa), cy - int(198*self.ssaa)), (cx + int(118*self.ssaa), cy - int(98*self.ssaa)), (cx + int(138*self.ssaa), cy + int(52*self.ssaa)), (cx + int(162*self.ssaa), cy + int(242*self.ssaa))],
            [(cx - int(45*self.ssaa), cy - int(195*self.ssaa)), (cx - int(10*self.ssaa), cy - int(110*self.ssaa)), (cx + int(15*self.ssaa), cy - int(55*self.ssaa))],
            [(cx + int(40*self.ssaa), cy - int(190*self.ssaa)), (cx + int(5*self.ssaa), cy - int(105*self.ssaa)), (cx - int(20*self.ssaa), cy - int(50*self.ssaa))]
        ]

        for pts in front_strands:
            p0, p1, p2 = pts[0], pts[1], pts[2]
            p3 = pts[3] if len(pts) > 3 else pts[2]
            self.draw_smooth_bezier(hf_draw, p0, p1, p2, p3, (6, 6, 11, 255), width=int(12*self.ssaa))
            self.draw_smooth_bezier(hf_draw, p0, p1, p2, p3, (95, 130, 190, 150), width=int(3*self.ssaa))

        canvas = Image.alpha_composite(canvas, hair_fg)

        # ----------------------------------------------------
        # 8. PÓS-PROCESSAMENTO & DOWNSAMPLING LANCZOS
        # ----------------------------------------------------
        bloom_layer, bloom_draw = self.create_layer()
        for _ in range(100):
            ex = random.randint(0, w)
            ey = random.randint(0, h)
            er = random.randint(int(1.5*self.ssaa), int(5*self.ssaa))
            bloom_draw.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(255, 20, 55, random.randint(80, 220)))

        bloom_filtered = bloom_layer.filter(ImageFilter.GaussianBlur(int(8 * self.ssaa)))
        canvas = Image.alpha_composite(canvas, bloom_filtered)

        vin, v_draw = self.create_layer()
        max_dist = math.hypot(cx, cy)
        for r in range(int(max_dist), int(max_dist * 0.45), -int(15 * self.ssaa)):
            t = 1 - (r / max_dist)
            v_draw.rectangle([0, 0, w, h], outline=(0, 0, 0, int(190 * (1 - t)**2)), width=int(20 * self.ssaa))
        canvas = Image.alpha_composite(canvas, vin)

        print(f"🔄 Executando Downsampling Lanczos Studio Pro: {self.w}x{self.h} -> {self.target_w}x{self.target_h}...")
        final_img = canvas.convert("RGB").resize((self.target_w, self.target_h), Image.Resampling.LANCZOS)
        
        enhancer = ImageEnhance.Sharpness(final_img)
        final_img = enhancer.enhance(1.15)

        return final_img

def main():
    print("\033[1;36m🎨 BLACKCORE ANIME STUDIO // Renderizando Ilustração em Alta Definição (1600x1600)...\033[0m")
    t0 = time.time()
    
    engine = AnimeStudioEngine(target_w=1600, target_h=1600, ssaa=2)
    img = engine.render_illustration()
    
    out_dir = output_dir()
    if not out_dir.exists():
        out_dir = Path.home() / "BLACKCORE-Projects" / "black-paint-studio" / "gallery"
        out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / "personagem_anime_kyoani.png"
    img.save(out_file, "PNG", quality=100)

    scan_media(out_file)
    
    elapsed = time.time() - t0
    print(f"\033[1;32m✅ Renderização de Ilustração concluída em {elapsed:.2f}s!\033[0m")
    print(f"\033[1;37m👉 Arquivo em altíssima qualidade: {out_file}\033[0m\n")

    try:
        sys.path.insert(0, str(Path.home() / ".blackcore" / "modules" / "black_numbers"))
        from bn_vision import scan_pixels, render_terminal_ansi
        scan_data = scan_pixels(out_file, width=42, height=22)
        render_terminal_ansi(scan_data, colored=True)
    except Exception as e:
        print(f"Prévia: {e}")

if __name__ == "__main__":
    main()
