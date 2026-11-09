#!/usr/bin/env python3
"""
paint_studio_v06_pro.py - Motor Gráfico v0.6 Professional (BLACKCORE Studio)
Sintetizador e Estúdio de Pintura 100% Local (Zero API Externa).

Recursos de Nível Profissional:
  - Physical Oil & Watercolor Brushes (Física de Cerdas & Glazing de Tinta)
  - Canvas Texture & Impasto Grain (Rugosidade e Textura de Tela a Óleo)
  - Procedural Fractal Noise Landscape Generator (Atmosfera, Montanhas, Lagos e Ray Scatter)
  - High-Definition SSAA Render Pipeline com Downsampling Lanczos
"""

from __future__ import annotations
import argparse, json, math, os, random, subprocess, sys, time
from pathlib import Path
from termux_compat import scan_media, output_dir
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parent
TARGET_DIR = output_dir()
if not TARGET_DIR.exists():
    TARGET_DIR = ROOT / "gallery"
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

def load_presets() -> dict:
    preset_file = ROOT / "presets.json"
    if preset_file.exists():
        with open(preset_file, "r", encoding="utf-8") as f:
            return json.load(f).get("presets", {})
    return {}

PRESETS = load_presets()

class OrganicStudioEngineV06:
    def __init__(self, target_w=1600, target_h=1600, ssaa=2, seed=2026):
        self.target_w = target_w
        self.target_h = target_h
        self.ssaa = ssaa
        self.w = target_w * ssaa
        self.h = target_h * ssaa
        self.cx = self.w // 2
        self.cy = self.h // 2
        self.seed = seed
        random.seed(seed)

    def layer(self) -> tuple[Image.Image, ImageDraw.ImageDraw]:
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        return img, ImageDraw.Draw(img, "RGBA")

    def apply_canvas_grain(self, img: Image.Image, roughness=0.08) -> Image.Image:
        """Aplica textura de tela de pintura a óleo com grão de linho e rugosidade natural."""
        grain, d_grain = self.layer()
        for y in range(0, self.h, int(4 * self.ssaa)):
            d_grain.line([0, y, self.w, y], fill=(255, 255, 255, int(18 * roughness * 255)), width=int(1.5*self.ssaa))
        for x in range(0, self.w, int(4 * self.ssaa)):
            d_grain.line([x, 0, x, self.h], fill=(0, 0, 0, int(18 * roughness * 255)), width=int(1.5*self.ssaa))
        
        grain = grain.filter(ImageFilter.GaussianBlur(int(1.2 * self.ssaa)))
        return Image.alpha_composite(img, grain)

    def draw_bristle_oil_stroke(self, draw: ImageDraw.ImageDraw, p0, p1, p2, p3, base_color, width=12, bristles=14, steps=60):
        """Simula a física de cerdas paralelas de pincel a óleo com esgotamento de tinta."""
        r, g, b = base_color[:3]
        base_a = base_color[3] if len(base_color) > 3 else 255

        # Pontos da curva de Bézier
        curve_pts = []
        for i in range(steps + 1):
            t = i / steps
            inv = 1.0 - t
            x = (inv**3 * p0[0] + 3 * inv**2 * t * p1[0] + 3 * inv * t**2 * p2[0] + t**3 * p3[0])
            y = (inv**3 * p0[1] + 3 * inv**2 * t * p1[1] + 3 * inv * t**2 * p2[1] + t**3 * p3[1])
            curve_pts.append((x, y))

        # Desenha cada cerda do pincel com micro-deslocamento e variação de tonalidade
        for br in range(bristles):
            offset_factor = (br / max(1, bristles - 1) - 0.5) * width
            b_r = max(0, min(255, r + random.randint(-18, 18)))
            b_g = max(0, min(255, g + random.randint(-18, 18)))
            b_b = max(0, min(255, b + random.randint(-18, 18)))

            bristle_pts = []
            for i, (cx, cy) in enumerate(curve_pts):
                t = i / steps
                # Tangente para perpendicularidade
                if i < len(curve_pts) - 1:
                    dx = curve_pts[i+1][0] - cx
                    dy = curve_pts[i+1][1] - cy
                else:
                    dx = cx - curve_pts[i-1][0]
                    dy = cy - curve_pts[i-1][1]
                
                length = math.hypot(dx, dy) or 1.0
                nx = -dy / length
                ny = dx / length

                bx = cx + nx * offset_factor
                by = cy + ny * offset_factor
                bristle_pts.append((bx, by))

            for i in range(len(bristle_pts) - 1):
                t = i / steps
                # Esgotamento de tinta e variação de pressão
                pressure = math.sin(t * math.pi) * 0.8 + 0.35
                alpha = int(base_a * pressure * (1.0 - t * 0.15))
                w = max(1, int(2.5 * self.ssaa * pressure))
                draw.line([bristle_pts[i], bristle_pts[i+1]], fill=(b_r, b_g, b_b, alpha), width=w)

    def fractal_noise_val(self, x: float, y: float, octaves=5) -> float:
        """Sintetizador de Ruído Fractal Procedural (Perlin-like via Seno/Cosseno Multiescala)."""
        val = 0.0
        amp = 1.0
        freq = 1.0
        max_amp = 0.0
        for _ in range(octaves):
            val += math.sin(x * freq * 0.005 + y * freq * 0.003) * math.cos(y * freq * 0.006 - x * freq * 0.002) * amp
            max_amp += amp
            amp *= 0.5
            freq *= 2.1
        return (val / max_amp + 1.0) * 0.5

    def generate_procedural_masterpiece_landscape(self) -> Image.Image:
        """Gera 100% via Código Local uma Paisagem Épica de Montanhas, Lago, Aurora e Floresta."""
        w, h, cx, cy = self.w, self.h, self.cx, self.cy
        print("🎨 [BLACKCORE v0.6 Engine] Sintetizando Paisagem Épica 100% Procedural e Local...")

        canvas, d_canvas = self.layer()

        # 1. Céu Crepuscular Pôr do Sol e Aurora (Gradiente Óptico)
        for y in range(int(h * 0.65)):
            t = y / (h * 0.65)
            if t < 0.3:
                # Topo Zenith Púrpura Profundo
                rt = t / 0.3
                r = int(18 + rt * 30)
                g = int(8 + rt * 20)
                b = int(45 + rt * 60)
            elif t < 0.7:
                # Meio Carmesim / Magenta
                rt = (t - 0.3) / 0.4
                r = int(48 + rt * 180)
                g = int(28 + rt * 40)
                b = int(105 - rt * 45)
            else:
                # Horizonte Dourado / Laranja Vivo
                rt = (t - 0.7) / 0.3
                r = int(228 + rt * 27)
                g = int(68 + rt * 90)
                b = int(60 - rt * 50)
            
            d_canvas.line([0, y, w, y], fill=(r, g, b, 255))

        # Sol Dourado Volumétrico no Horizonte
        sun_x = int(w * 0.52)
        sun_y = int(h * 0.48)
        sun_r = int(140 * self.ssaa)
        
        sun_layer, d_sun = self.layer()
        for r in range(int(sun_r * 2.5), 0, -int(4 * self.ssaa)):
            t = 1.0 - (r / (sun_r * 2.5))
            alpha = int(180 * (t**2))
            d_sun.ellipse([sun_x - r, sun_y - r, sun_x + r, sun_y + r], fill=(255, int(180 + t*70), int(100*t), alpha))
        
        sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(int(22 * self.ssaa)))
        canvas = Image.alpha_composite(canvas, sun_layer)
        d_canvas = ImageDraw.Draw(canvas, "RGBA")

        # Raios Dourados Volumétricos (God Rays)
        rays, d_rays = self.layer()
        for ang in range(-60, 240, 8):
            rad = math.radians(ang + random.uniform(-2, 2))
            rx = sun_x + math.cos(rad) * w * 1.2
            ry = sun_y + math.sin(rad) * h * 1.2
            d_rays.polygon([(sun_x, sun_y), (rx - 40*self.ssaa, ry), (rx + 40*self.ssaa, ry)], fill=(255, 210, 130, random.randint(8, 25)))
        
        rays = rays.filter(ImageFilter.GaussianBlur(int(15 * self.ssaa)))
        canvas = Image.alpha_composite(canvas, rays)
        d_canvas = ImageDraw.Draw(canvas, "RGBA")

        # 2. Cordilheira de Montanhas Distantes (Nível 1 - Névoa Roxa)
        m1, d_m1 = self.layer()
        pts_m1 = [(0, h)]
        for x in range(0, w + 1, int(10 * self.ssaa)):
            n = self.fractal_noise_val(x * 0.8, 100, octaves=4)
            my = int(h * 0.38 + n * h * 0.18)
            pts_m1.append((x, my))
        pts_m1.append((w, h))
        d_m1.polygon(pts_m1, fill=(65, 30, 75, 240))
        canvas = Image.alpha_composite(canvas, m1)
        d_canvas = ImageDraw.Draw(canvas, "RGBA")

        # Cordilheira de Montanhas Médias com Picos de Neve e Pinceladas (Nível 2)
        m2, d_m2 = self.layer()
        pts_m2 = [(0, h)]
        peak_pts = []
        for x in range(0, w + 1, int(8 * self.ssaa)):
            n = self.fractal_noise_val(x * 1.5, 300, octaves=5)
            my = int(h * 0.42 + n * h * 0.22)
            pts_m2.append((x, my))
            peak_pts.append((x, my))
        pts_m2.append((w, h))
        d_m2.polygon(pts_m2, fill=(35, 18, 48, 255))

        # Pinceladas de Neve Dourada e Sombra nos Picos
        for i in range(0, len(peak_pts) - 1, 3):
            px, py = peak_pts[i]
            if py < h * 0.55:
                # Luz de fundo nas arestas
                p0 = (px, py)
                p1 = (px + int(20*self.ssaa), py + int(30*self.ssaa))
                p2 = (px + int(40*self.ssaa), py + int(70*self.ssaa))
                p3 = (px + int(60*self.ssaa), py + int(110*self.ssaa))
                self.draw_bristle_oil_stroke(d_m2, p0, p1, p2, p3, (255, 180, 140, 210), width=int(8*self.ssaa), bristles=8)

        canvas = Image.alpha_composite(canvas, m2)
        d_canvas = ImageDraw.Draw(canvas, "RGBA")

        # 3. Lago de Montanha Espelhado (Reflexo e Ondulação Senoidal)
        water, d_water = self.layer()
        water_top = int(h * 0.58)
        
        for y in range(water_top, h):
            t = (y - water_top) / (h - water_top)
            r = int(45 - t * 35)
            g = int(22 - t * 15)
            b = int(60 - t * 40)
            d_water.line([0, y, w, y], fill=(r, g, b, 255))

        # Ocorrência de reflexo cintilante do Pôr do Sol e Montanhas na Água
        for y in range(water_top, h, int(3 * self.ssaa)):
            t = (y - water_top) / (h - water_top)
            wave_off = math.sin(y * 0.08) * int(15 * self.ssaa * (t + 0.1))
            alpha = int(160 * (1.0 - t**0.8))
            ref_color = (255, int(140 + t*80), int(60*t), alpha)
            d_water.line([sun_x - int(120*self.ssaa) + wave_off, y, sun_x + int(120*self.ssaa) + wave_off, y], fill=ref_color, width=int(2*self.ssaa))

        canvas = Image.alpha_composite(canvas, water)
        d_canvas = ImageDraw.Draw(canvas, "RGBA")

        # 4. Floresta de Pinheiros e Colinas em Camadas Promontório (Primeiro Plano)
        fore, d_fore = self.layer()
        
        # Margens e Colinas
        d_fore.polygon([(0, int(h*0.72)), (int(w*0.45), int(h*0.78)), (0, h)], fill=(12, 12, 22, 255))
        d_fore.polygon([(w, int(h*0.68)), (int(w*0.52), int(h*0.75)), (w, h)], fill=(10, 10, 18, 255))

        # Desenha Pinheiros com Cerdas de Pincel
        def draw_pine_tree(draw: ImageDraw.ImageDraw, x: int, base_y: int, height: int):
            trunk_w = max(2, int(height * 0.08))
            draw.line([x, base_y, x, base_y - height], fill=(6, 6, 10, 255), width=trunk_w)
            
            branches = 18
            for i in range(branches):
                t = i / branches
                by = base_y - height * (0.2 + t * 0.8)
                bw = (1.0 - t) * (height * 0.38)
                p0 = (x - bw, by + int(10*self.ssaa))
                p1 = (x, by)
                p2 = (x + bw, by + int(10*self.ssaa))
                draw.polygon([(x - bw, by + int(12*self.ssaa)), (x, by), (x + bw, by + int(12*self.ssaa))], fill=(14, 18, 28, 240))
                # Reflexo dourado nas pontas das galhos
                draw.line([(x - bw, by + int(12*self.ssaa)), (x - bw*0.4, by)], fill=(220, 120, 80, 180), width=int(2*self.ssaa))

        # Povoar pinheiros à esquerda e direita
        for px in range(0, int(w * 0.38), int(35 * self.ssaa)):
            tree_h = random.randint(int(140*self.ssaa), int(320*self.ssaa))
            tree_y = int(h * 0.74 + (px/w)*h*0.12)
            draw_pine_tree(d_fore, px, tree_y, tree_h)

        for px in range(int(w * 0.62), w + 1, int(35 * self.ssaa)):
            tree_h = random.randint(int(150*self.ssaa), int(340*self.ssaa))
            tree_y = int(h * 0.70 + ((w-px)/w)*h*0.15)
            draw_pine_tree(d_fore, px, tree_y, tree_h)

        canvas = Image.alpha_composite(canvas, fore)

        # 5. Névoa Matinal Atmosférica e Fagulhas Bioluminescentes
        fog, d_fog = self.layer()
        for _ in range(60):
            fx = random.randint(0, w)
            fy = random.randint(int(h * 0.52), int(h * 0.80))
            fr_x = random.randint(int(80*self.ssaa), int(260*self.ssaa))
            fr_y = random.randint(int(15*self.ssaa), int(45*self.ssaa))
            d_fog.ellipse([fx - fr_x, fy - fr_y, fx + fr_x, fy + fr_y], fill=(255, 190, 160, random.randint(10, 35)))

        fog = fog.filter(ImageFilter.GaussianBlur(int(20 * self.ssaa)))
        canvas = Image.alpha_composite(canvas, fog)

        # 6. Aplicação da Textura de Tela de Pintura a Óleo
        canvas = self.apply_canvas_grain(canvas, roughness=0.10)

        # Finalização e Downsampling Lanczos
        print(f"🔄 Downsampling Lanczos Studio Pro ({self.w}x{self.h} -> {self.target_w}x{self.target_h})...")
        final_img = canvas.convert("RGB").resize((self.target_w, self.target_h), Image.Resampling.LANCZOS)
        
        # Realce de Nitidez
        enhancer = ImageEnhance.Sharpness(final_img)
        final_img = enhancer.enhance(1.20)

        out_path = TARGET_DIR / "paisagem_local_v06_insana.png"
        final_img.save(out_path, "PNG", quality=100)
        scan_media(out_path)

        size_kb = os.path.getsize(out_path) // 1024
        print(f"✅ Paisagem Épica 100% Procedural Gerada: {out_path} ({size_kb} KB)")
        return out_path

def main():
    parser = argparse.ArgumentParser(description="BLACKCORE v0.6 Organic Studio Engine")
    parser.add_argument("--generate-landscape", action="store_true", help="Gera a Paisagem Épica 100% Procedural e Local")
    args = parser.parse_args()

    engine = OrganicStudioEngineV06(target_w=1600, target_h=1600, ssaa=2, seed=2026)

    if args.generate_landscape or len(sys.argv) == 1:
        out = engine.generate_procedural_masterpiece_landscape()
        print(f"✨ Sucesso! Arte local disponível em: {out}")

if __name__ == "__main__":
    main()
