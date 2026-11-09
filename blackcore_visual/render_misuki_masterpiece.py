#!/usr/bin/env python3
"""
render_misuki_masterpiece.py - Misuki Mestra v2 (Nota 10/10)
Evolução extrema: rica em detalhes de luz, ornamentos góticos, colares de choker,
franja perfeitamente enquadrada, chifres texturizados e hachuras profissionais.
"""

import os
import random
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUTPUT_DIR = Path("/storage/emulated/0/Pictures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DIR = Path.home() / "BLACKCORE-Projects" / "black-paint-studio/gallery_misuki"
LOCAL_DIR.mkdir(parents=True, exist_ok=True)

class MisukiMasterpieceV2Engine:
    def __init__(self):
        self.width = 2400
        self.height = 1800

    def render(self) -> Image.Image:
        print("👑 [BLACKCORE MASTERCLASS v2] Elevando a Misuki para o nível 10/10...")
        
        img = Image.new("RGB", (self.width, self.height), (10, 12, 20))
        draw = ImageDraw.Draw(img, "RGBA")

        # 1. Fundo Atmosférico Gótico Profundo com Gradiente Estrelado
        for y in range(self.height):
            f = y / self.height
            r = int(10 + f * 8)
            g = int(12 + f * 14)
            b = int(20 + f * 45)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # Estrelas finas de fundo
        for _ in range(80):
            sx = random.randint(50, self.width - 50)
            sy = random.randint(50, 900)
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(220, 240, 255, 200))

        # Lua gótica centralizada atrás da personagem com halo prismático
        mx, my, mr = 1200, 380, 180
        for r_val in range(mr + 180, mr, -4):
            alpha = int(30 * (1 - (r_val - mr) / 180))
            draw.ellipse([mx - r_val, my - r_val, mx + r_val, my + r_val], fill=(140, 190, 255, alpha))
        draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(230, 242, 255))
        draw.ellipse([mx - 50, my - 40, mx - 10, my], fill=(210, 225, 240, 160))

        cx, cy = self.width // 2, self.height // 2 + 100

        # Sombra no solo
        draw.ellipse([cx - 220, cy + 620, cx + 220, cy + 680], fill=(4, 6, 12, 230))

        # 2. VESTIDO E CORSET GÓTICO DETALHADO (Textura de Couro / Renda)
        print("👗 Desenhando traje gótico com alta complexidade...")
        draw.polygon([
            (cx - 160, cy + 180),
            (cx + 160, cy + 180),
            (cx + 260, cy + 650),
            (cx - 260, cy + 650)
        ], fill=(14, 12, 20), outline=(8, 6, 12), width=4)

        draw.polygon([
            (cx - 130, cy + 185),
            (cx + 130, cy + 185),
            (cx + 145, cy + 400),
            (cx - 145, cy + 400)
        ], fill=(22, 17, 30), outline=(140, 60, 200), width=3)

        for fy in range(cy + 220, cy + 380, 45):
            draw.rectangle([cx - 12, fy, cx + 12, fy + 15], fill=(255, 215, 100), outline=(180, 140, 50), width=2)

        draw.polygon([
            (cx - 140, cy + 185),
            (cx, cy + 250),
            (cx + 140, cy + 185),
            (cx, cy + 175)
        ], fill=(245, 248, 255), outline=(210, 220, 235), width=2)

        # Choker de Couro com Gema Vermelha
        draw.rectangle([cx - 38, cy + 175, cx + 38, cy + 195], fill=(15, 12, 18), outline=(255, 215, 100), width=2)
        draw.ellipse([cx - 8, cy + 178, cx + 8, cy + 192], fill=(220, 20, 60), outline=(255, 215, 100), width=2)

        # Pescoço
        draw.rectangle([cx - 35, cy + 105, cx + 35, cy + 180], fill=(230, 210, 200))
        draw.polygon([(cx - 35, cy + 120), (cx, cy + 140), (cx + 35, cy + 120)], fill=(160, 135, 125))

        # 3. ROSTO E OLHOS EXPRESSIVOS (Anime Gótico de Elite)
        print("👁️ Refinando rosto, olhos e franja da Misuki...")
        face_poly = [
            (cx - 82, cy - 25),
            (cx + 82, cy - 25),
            (cx + 62, cy + 105),
            (cx, cy + 130),
            (cx - 62, cy + 105)
        ]
        draw.polygon(face_poly, fill=(240, 220, 210), outline=(70, 40, 50), width=3)

        # Olhos Detalhados
        draw.ellipse([cx - 55, cy + 15, cx - 15, cy + 55], fill=(255, 255, 255), outline=(40, 20, 30), width=2)
        draw.ellipse([cx - 50, cy + 20, cx - 20, cy + 50], fill=(0, 220, 255))
        draw.ellipse([cx - 42, cy + 28, cx - 28, cy + 42], fill=(120, 30, 200))
        draw.ellipse([cx - 38, cy + 32, cx - 32, cy + 38], fill=(10, 10, 20))
        draw.ellipse([cx - 43, cy + 27, cx - 38, cy + 32], fill=(255, 255, 255))

        draw.ellipse([cx + 15, cy + 15, cx + 55, cy + 55], fill=(255, 255, 255), outline=(40, 20, 30), width=2)
        draw.ellipse([cx + 20, cy + 20, cx + 50, cy + 50], fill=(0, 220, 255))
        draw.ellipse([cx + 28, cy + 28, cx + 42, cy + 42], fill=(120, 30, 200))
        draw.ellipse([cx + 32, cy + 32, cx + 38, cy + 38], fill=(10, 10, 20))
        draw.ellipse([cx + 37, cy + 27, cx + 42, cy + 32], fill=(255, 255, 255))

        draw.line([(cx - 55, cy + 5), (cx - 15, cy + 10)], fill=(40, 20, 30), width=3)
        draw.line([(cx + 15, cy + 10), (cx + 55, cy + 5)], fill=(40, 20, 30), width=3)

        draw.line([(cx, cy + 60), (cx - 2, cy + 78)], fill=(170, 130, 120), width=2)
        draw.arc([cx - 14, cy + 86, cx + 14, cy + 104], 0, 180, fill=(190, 60, 85), width=3)

        # 4. CABELO LONGO E FRANJA
        print("💇‍♀️ Construindo mechas e franja detalhadas...")
        draw.polygon([(cx - 150, cy - 70), (cx - 250, cy + 450), (cx - 90, cy + 200)], fill=(20, 16, 28))
        draw.polygon([(cx + 150, cy - 70), (cx + 250, cy + 450), (cx + 90, cy + 200)], fill=(20, 16, 28))

        draw.polygon([
            (cx - 95, cy - 85),
            (cx, cy - 120),
            (cx + 95, cy - 85),
            (cx + 105, cy + 25),
            (cx - 105, cy + 25)
        ], fill=(30, 24, 42), outline=(10, 8, 15), width=3)

        draw.polygon([(cx - 95, cy - 20), (cx - 80, cy + 140), (cx - 58, cy + 130)], fill=(45, 36, 62))
        draw.polygon([(cx + 95, cy - 20), (cx + 80, cy + 140), (cx + 58, cy + 130)], fill=(45, 36, 62))

        # 5. OS 2 CHIFRES GÓTICOS
        print("🐉 Adicionando os chifres góticos texturizados...")
        draw.polygon([
            (cx - 75, cy - 90),
            (cx - 180, cy - 240),
            (cx - 115, cy - 100)
        ], fill=(15, 12, 22), outline=(0, 240, 255), width=3)
        draw.line([(cx - 100, cy - 120), (cx - 125, cy - 150)], fill=(0, 240, 255), width=2)
        draw.line([(cx - 120, cy - 150), (cx - 145, cy - 180)], fill=(0, 240, 255), width=2)

        draw.polygon([
            (cx + 75, cy - 90),
            (cx + 180, cy - 240),
            (cx + 115, cy - 100)
        ], fill=(15, 12, 22), outline=(0, 240, 255), width=3)
        draw.line([(cx + 100, cy - 120), (cx + 125, cy - 150)], fill=(0, 240, 255), width=2)
        draw.line([(cx + 120, cy - 150), (cx + 145, cy - 180)], fill=(0, 240, 255), width=2)

        # 6. RIM LIGHT E HACHURAS
        print("💡 Aplicando Rim Light e hachuras profissionais...")
        for i in range(20):
            draw.arc([cx - 120 - i, cy - 130 - i, cx + 120 + i, cy + 130 + i], 180, 360, fill=(0, 230, 255, 40), width=2)

        for _ in range(4500):
            hx = random.randint(cx - 220, cx + 220)
            hy = random.randint(cy + 180, cy + 620)
            draw.line([(hx, hy), (hx + random.randint(-5, 5), hy + random.randint(12, 35))], fill=(3, 2, 5, 160), width=1)

        # 7. Masterização Final
        print("✨ Finalizando masterização da Misuki Mestra v2...")
        img = img.filter(ImageFilter.SMOOTH)
        img = ImageEnhance.Color(img).enhance(1.4)
        img = ImageEnhance.Contrast(img).enhance(1.25)
        img = ImageEnhance.Sharpness(img).enhance(1.35)

        return img

    def run(self):
        print("==================================================================")
        print("🖤 BLACKCORE // MISUKI MESTRA V2 (NOTA 10/10)")
        print("==================================================================")
        
        painting = self.render()
        
        final_path = OUTPUT_DIR / "misuki_pintura_mestra_v2.png"
        local_path = LOCAL_DIR / "misuki_pintura_mestra_v2.png"
        
        painting.save(final_path, quality=100)
        painting.save(local_path, quality=100)
        
        print(f"💾 Obra Misuki Mestra v2 salva com sucesso em: {final_path}")
        return final_path

if __name__ == "__main__":
    engine = MisukiMasterpieceV2Engine()
    engine.run()
