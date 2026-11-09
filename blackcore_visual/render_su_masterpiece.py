#!/usr/bin/env python3
"""
render_su_masterpiece.py - Motor de Pintura Orgânica de Nível Superior (Inspirado em Su.png)
Combina traços expressivos, iluminação atmosférica de alto contraste, pinceladas a óleo
fluidas e uma identidade visual 100% orgânica, sem formas geométricas rígidas.
"""

import os
import random
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUTPUT_DIR = Path("/storage/emulated/0/Pictures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DIR = Path.home() / "BLACKCORE-Projects" / "black-paint-studio/gallery_su"
LOCAL_DIR.mkdir(parents=True, exist_ok=True)

class SuInspiredEngine:
    def __init__(self):
        self.width = 1800
        self.height = 2400  # Formato vertical 3:4 idêntico a Su.png

    def render(self) -> Image.Image:
        print("🎨 [BLACKCORE SU-ENGINE] Renderizando obra de nível superior inspirada em Su.png...")
        
        # Base de pintura com gradiente atmosférico profundo e dramático
        img = Image.new("RGB", (self.width, self.height), (15, 12, 25))
        draw = ImageDraw.Draw(img, "RGBA")

        # Gradiente de fundo vertical estilo chiaroscuro
        for y in range(self.height):
            f = y / self.height
            r = int(15 + math.sin(f * math.pi) * 10)
            g = int(12 + f * 18)
            b = int(25 + f * 55)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # Textura de pinceladas de fundo (Impasto orgânico)
        for _ in range(800):
            bx = random.randint(100, self.width - 100)
            by = random.randint(100, self.height - 100)
            blen = random.randint(40, 120)
            bcol = random.choice([
                (40, 30, 60, 35),
                (20, 40, 70, 30),
                (70, 30, 50, 25)
            ])
            draw.line([(bx, by), (bx + random.randint(-30, 30), by + blen)], fill=bcol, width=random.randint(6, 15))

        cx, cy = self.width // 2, self.height // 2 - 100

        # Sombra no solo fluida
        draw.ellipse([cx - 280, cy + 800, cx + 280, cy + 900], fill=(5, 4, 8, 200))

        # 1. Silhueta e Traje Estilizado com Curvas Orgânicas
        print("👗 Pintando vestimenta e silhueta com pinceladas fluidas...")
        for layer in range(60, 0, -1):
            w_off = layer * 8
            alpha = int(15 + (layer / 60) * 45)
            draw.ellipse([
                cx - 260 - w_off, cy + 250,
                cx + 260 + w_off, cy + 950 + layer * 3
            ], fill=(22, 18, 35, alpha))

        # 2. Rosto Expressivo e Iluminação de Contraste (Chiaroscuro)
        print("👤 Esculpindo rosto com iluminação dramática e contornos suaves...")
        
        # Cabeça / Rosto Oval Orgânico
        draw.ellipse([cx - 110, cy - 40, cx + 110, cy + 170], fill=(245, 230, 220))

        # Sombreamento lateral esquerdo profundo
        for sy in range(cy - 20, cy + 150, 3):
            offset = (sy - cy) * 0.25
            draw.line([(cx - 100, sy), (cx - 50 + offset, sy)], fill=(215, 195, 185, 140), width=4)

        # Olhos Expressivos de Alto Impacto Visual
        # Esquerdo
        draw.ellipse([cx - 68, cy + 25, cx - 20, cy + 72], fill=(255, 255, 255), outline=(50, 35, 45), width=2)
        draw.ellipse([cx - 58, cy + 34, cx - 30, cy + 62], fill=(40, 140, 180)) # Íris Azul Profundo
        draw.ellipse([cx - 50, cy + 40, cx - 38, cy + 52], fill=(10, 12, 18))  # Pupila
        draw.ellipse([cx - 53, cy + 37, cx - 47, cy + 42], fill=(255, 255, 255)) # Brilho

        # Direito
        draw.ellipse([cx + 20, cy + 25, cx + 68, cy + 72], fill=(255, 255, 255), outline=(50, 35, 45), width=2)
        draw.ellipse([cx + 30, cy + 34, cx + 58, cy + 62], fill=(40, 140, 180))
        draw.ellipse([cx + 38, cy + 40, cx + 50, cy + 52], fill=(10, 12, 18))
        draw.ellipse([cx + 45, cy + 37, cx + 51, cy + 42], fill=(255, 255, 255))

        # Sobrancelhas orgânicas expressivas
        draw.arc([cx - 68, cy + 10, cx - 20, cy + 35], 180, 360, fill=(60, 40, 50), width=3)
        draw.arc([cx + 20, cy + 10, cx + 68, cy + 35], 180, 360, fill=(60, 40, 50), width=3)

        # Nariz e Lábios com toque natural
        draw.line([(cx, cy + 75), (cx - 1, cy + 98)], fill=(170, 140, 130), width=2)
        draw.arc([cx - 16, cy + 112, cx + 16, cy + 132], 0, 180, fill=(190, 75, 95), width=3)

        # 3. Cabelo Estilizado Orgânico em Camadas
        print("💇‍♀️ Modelando cabelo e mechas expressivas...")
        for strand in range(-10, 11):
            sx = cx + strand * 22
            sy = cy - 80
            draw.arc([sx - 50, sy, sx + 50, sy + 600], 0, 180, fill=(45, 38, 58, 200), width=random.randint(10, 22))

        # Franja Fluida
        draw.arc([cx - 100, cy - 110, cx + 100, cy + 20], 0, 180, fill=(60, 50, 75), width=28)

        # 4. Masterização Óleo Fina e Texturizada
        print("✨ Aplicando masterização artística inspirada em Su.png...")
        img = img.filter(ImageFilter.SMOOTH)
        img = ImageEnhance.Color(img).enhance(1.3)
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Sharpness(img).enhance(1.25)

        return img

    def run(self):
        print("==================================================================")
        print("🖤 BLACKCORE // PINTURA MESTRA INSPIRADA EM SU.PNG")
        print("==================================================================")
        
        painting = self.render()
        
        final_path = OUTPUT_DIR / "su_inspired_masterpiece.png"
        local_path = LOCAL_DIR / "su_inspired_masterpiece.png"
        
        painting.save(final_path, quality=100)
        painting.save(local_path, quality=100)
        
        print(f"💾 Obra inspirada em Su.png salva com sucesso em: {final_path}")
        return final_path

if __name__ == "__main__":
    engine = SuInspiredEngine()
    engine.run()
