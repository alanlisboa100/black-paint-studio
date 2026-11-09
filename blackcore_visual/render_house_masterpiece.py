#!/usr/bin/env python3
"""
render_house_masterpiece.py - Versão Suprema v4 (Cenário de Fundo Mais Forte e Céu Estrelado Épico)
Mantém a lua perfeita na direita e adiciona um cenário de fundo profundo, imponente e marcante.
"""

import os
import random
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUTPUT_DIR = Path("/storage/emulated/0/Pictures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DIR = Path.home() / "BLACKCORE-Projects" / "black-paint-studio/gallery_house"
LOCAL_DIR.mkdir(parents=True, exist_ok=True)

class EnchantedHouseUltimateEngineV4:
    def __init__(self):
        self.width = 2400
        self.height = 1800

    def paint_house(self) -> Image.Image:
        print("🏡 [BLACKCORE PAINT STUDIO v4] Renderizando Céu Épico e Fundo Forte...")
        img = Image.new("RGB", (self.width, self.height), (2, 4, 12))
        draw = ImageDraw.Draw(img, "RGBA")

        # 1. Céu Noturno Enriquecido com Gradiente Cósmico Profundo
        for y in range(self.height):
            f = y / self.height
            r = int(2 + f * 6)
            g = int(4 + f * 14)
            b = int(12 + f * 42)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # 2. Céu Estrelado Realista (Dezenas de estrelas cintilantes de tamanhos variados)
        for _ in range(120):
            sx = random.randint(50, self.width - 50)
            sy = random.randint(30, 950)
            sr = random.randint(1, 3)
            s_alpha = random.randint(150, 255)
            draw.ellipse([sx-sr, sy-sr, sx+sr, sy+sr], fill=(230, 240, 255, s_alpha))

        # 3. Aurora Boreal Mais Forte e Marcante (Ondas vibrantes em Turquesa, Magenta e Índigo)
        for wave in range(8):
            wy = int(180 + wave * 75)
            for x in range(0, self.width, 12):
                offset = int(math.sin(x * 0.005 + wave * 0.8) * 110)
                cy = wy + offset
                r_col = int(30 + wave * 15)
                g_col = int(140 + wave * 10)
                b_col = int(210 - wave * 12)
                draw.ellipse([x-120, cy-50, x+120, cy+50], fill=(r_col, g_col, b_col, 16))

        # 4. LUA CHEIA PRATEADA MANTIDA BEM BONITA COM HALO DIFUSO
        moon_x, moon_y, moon_r = 1850, 280, 105
        for r_val in range(moon_r + 160, moon_r, -4):
            alpha = int(40 * (1 - (r_val - moon_r) / 160))
            draw.ellipse([moon_x - r_val, moon_y - r_val, moon_x + r_val, moon_y + r_val], fill=(210, 235, 255, alpha))
        draw.ellipse([moon_x - moon_r, moon_y - moon_r, moon_x + moon_r, moon_y + moon_r], fill=(245, 250, 255))
        # Cratera suave na lua
        draw.ellipse([moon_x - 35, moon_y - 25, moon_x - 10, moon_y - 5], fill=(225, 235, 245, 140))

        # 5. Cenário de Fundo Mais Forte: Montanhas Imponentes e Floresta Densa em Múltiplas Camadas
        mountains = [
            [(0, self.height), (200, 1050), (700, 950), (1200, 1020), (1800, 920), (2400, 1080), (2400, self.height)],
            [(0, self.height), (450, 1180), (1050, 1100), (1650, 1150), (2200, 1050), (2400, self.height)]
        ]
        m_colors = [(14, 24, 42), (8, 14, 26)]
        for m, col in zip(mountains, m_colors):
            draw.polygon(m, fill=col)

        # 6. A CASA ENCANTADA PERFEITA (Sem nenhum traço indesejado "---")
        hx, hy, hw, hh = 750, 1000, 900, 520
        
        # Sombra suave da casa no solo
        draw.ellipse([hx - 80, hy + hh - 15, hx + hw + 80, hy + hh + 45], fill=(2, 4, 8, 200))

        # Paredes de Pedra Rústica Aconchegante
        draw.rectangle([hx, hy, hx + hw, hy + hh], fill=(62, 42, 32), outline=(25, 16, 10), width=4)

        for wy in range(hy + 50, hy + hh, 40):
            draw.line([(hx + 5, wy), (hx + hw - 5, wy)], fill=(45, 30, 22), width=1)

        # Telhado Imponente Liso (Perfeitamente limpo)
        roof_poly = [
            (hx - 80, hy),
            (hx + hw // 2, hy - 360),
            (hx + hw + 80, hy)
        ]
        draw.polygon(roof_poly, fill=(38, 28, 25), outline=(18, 12, 10), width=5)
        draw.polygon([
            (hx - 80, hy),
            (hx + hw // 2, hy - 360),
            (hx + hw // 2, hy),
            (hx, hy)
        ], fill=(52, 38, 34))

        # Chaminé com Fumaça Suave
        chimney_x, chimney_y, chimney_w, chimney_h = hx + 140, hy - 280, 65, 190
        draw.rectangle([chimney_x, chimney_y, chimney_x + chimney_w, chimney_y + chimney_h], fill=(85, 52, 40), outline=(22, 14, 10), width=3)
        draw.rectangle([chimney_x - 8, chimney_y - 18, chimney_x + chimney_w + 8, chimney_y], fill=(45, 30, 22))

        fx, fy = chimney_x + chimney_w // 2, chimney_y - 15
        for s in range(7):
            fr = 14 + s * 8
            alpha_smoke = max(10, 100 - s * 14)
            draw.ellipse([fx - fr - s*5, fy - s*40 - fr, fx + fr - s*5, fy - s*40 + fr], fill=(210, 225, 240, alpha_smoke))

        # Janelas com Luz Quente
        draw.rectangle([hx + 120, hy + 90, hx + 280, hy + 300], fill=(255, 195, 80), outline=(25, 16, 10), width=6)
        draw.line([(hx + 200, hy + 90), (hx + 200, hy + 300)], fill=(25, 16, 10), width=4)
        draw.line([(hx + 120, hy + 195), (hx + 280, hy + 195)], fill=(25, 16, 10), width=4)

        draw.rectangle([hx + hw - 280, hy + 90, hx + hw - 120, hy + 300], fill=(255, 195, 80), outline=(25, 16, 10), width=6)
        draw.line([(hx + hw - 200, hy + 90), (hx + hw - 200, hy + 300)], fill=(25, 16, 10), width=4)
        draw.line([(hx + hw - 280, hy + 195), (hx + hw - 120, hy + 195)], fill=(25, 16, 10), width=4)

        # Porta em Arco
        door_w, door_h = 180, 280
        door_x, door_y = hx + hw // 2 - door_w // 2, hy + hh - door_h
        draw.rectangle([door_x, door_y + 40, door_x + door_w, door_y + door_h], fill=(38, 22, 14), outline=(15, 9, 6), width=5)
        draw.pieslice([door_x, door_y, door_x + door_w, door_y + 80], 180, 360, fill=(38, 22, 14), outline=(15, 9, 6))
        draw.ellipse([door_x + 25, door_y + door_h // 2 + 10, door_x + 42, door_y + door_h // 2 + 27], fill=(255, 215, 100))

        # 7. DETALHES EM VOLTA (Jardim Florido, Cerca e Vaga-lumes)
        grass_y = hy + hh
        draw.rectangle([0, grass_y, self.width, self.height], fill=(14, 26, 18))

        flower_colors = [(255, 90, 140), (255, 210, 80), (180, 90, 255), (80, 210, 255)]
        for fx_offset in range(-400, 400, 16):
            fx = hx + hw // 2 + fx_offset
            fy = grass_y + random.randint(-8, 8)
            f_col = random.choice(flower_colors)
            draw.ellipse([fx, fy, fx + 14, fy + 14], fill=f_col)
            draw.line([(fx + 7, fy + 7), (fx + 7, fy + 22)], fill=(30, 100, 30), width=3)

        for cx in range(150, hx - 40, 55):
            draw.rectangle([cx, grass_y - 90, cx + 10, grass_y + 15], fill=(75, 52, 35), outline=(30, 18, 10), width=2)
        draw.line([(130, grass_y - 70), (hx - 20, grass_y - 70)], fill=(75, 52, 35), width=7)

        for cx in range(hx + hw + 40, self.width - 150, 55):
            draw.rectangle([cx, grass_y - 90, cx + 10, grass_y + 15], fill=(75, 52, 35), outline=(30, 18, 10), width=2)
        draw.line([(hx + hw + 20, grass_y - 70), (self.width - 130, grass_y - 70)], fill=(75, 52, 35), width=7)

        for _ in range(45):
            vx = random.randint(80, self.width - 80)
            vy = random.randint(750, self.height - 80)
            vr = random.randint(4, 9)
            draw.ellipse([vx-vr, vy-vr, vx+vr, vy+vr], fill=(255, 255, 140, 220))
            draw.ellipse([vx-vr*2, vy-vr*2, vx+vr*2, vy+vr*2], fill=(255, 255, 140, 60))

        # 8. MASTERIZAÇÃO ÓLEO/IMPASTO FINA
        print("🔄 Aplicando masterização final a óleo (Versão Suprema v4)...")
        img = img.filter(ImageFilter.SMOOTH_MORE)
        img = ImageEnhance.Color(img).enhance(1.35)
        img = ImageEnhance.Contrast(img).enhance(1.15)
        img = ImageEnhance.Sharpness(img).enhance(1.2)

        return img

    def run(self):
        print("==================================================================")
        print("🤖 BLACKCORE // RENDERIZADOR SUPREMO DA CASA ENCANTADA (v4)")
        print("==================================================================")
        
        painting = self.paint_house()
        
        final_path = OUTPUT_DIR / "casa_encantada_chamine_masterpiece.png"
        local_path = LOCAL_DIR / "casa_encantada_chamine_masterpiece.png"
        
        painting.save(final_path, quality=100)
        painting.save(local_path, quality=100)
        
        print(f"💾 Versão Suprema v4 salva com sucesso em: {final_path}")
        return final_path

if __name__ == "__main__":
    engine = EnchantedHouseUltimateEngineV4()
    engine.run()
