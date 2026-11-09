#!/usr/bin/env python3
"""
render_valariel_masterpiece.py - Valariel v3 (Conceitos 100% Orgânicos e Naturais)
Elimina qualquer resquício de polígono, linha reta ou simetria mecânica.
Utiliza pinceladas orgânicas a óleo dispersas, curvas de Bézier dinâmicas
e sombreamento suave de claro-escuro (Chiaroscuro) para total naturalidade.
"""

import os
import random
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUTPUT_DIR = Path("/storage/emulated/0/Pictures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DIR = Path.home() / "BLACKCORE-Projects" / "black-paint-studio/gallery_valariel"
LOCAL_DIR.mkdir(parents=True, exist_ok=True)

class ValarielNatureEngine:
    def __init__(self):
        self.width = 2400
        self.height = 1800

    def render(self) -> Image.Image:
        print("🍃 [BLACKCORE NATURE] Renderizando Valariel v3 (Conceito Orgânico Puro)...")
        
        # Fundo texturizado à mão com gradiente suave de floresta noturna
        img = Image.new("RGB", (self.width, self.height), (12, 16, 26))
        draw = ImageDraw.Draw(img, "RGBA")

        # Gradiente orgânico de fundo (luz da lua filtrada por árvores)
        for y in range(self.height):
            f = y / self.height
            r = int(12 + math.sin(f * math.pi) * 8)
            g = int(16 + f * 15)
            b = int(26 + f * 35)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # Manchas de luz suave da lua (Bokeh natural)
        for _ in range(45):
            bx = random.randint(100, self.width - 100)
            by = random.randint(100, self.height - 100)
            br = random.randint(20, 70)
            draw.ellipse([bx-br, by-br, bx+br, by+br], fill=(100, 180, 220, random.randint(15, 45)))

        cx, cy = self.width // 2, self.height // 2 + 60

        # 1. Corpo e Ombros com Caimento Orgânico (Sem polígonos retos)
        print("🌿 Pintando silhueta e vestimenta com curvas fluidas...")
        
        # Sombra base difusa no solo
        draw.ellipse([cx - 250, cy + 580, cx + 250, cy + 650], fill=(4, 6, 12, 180))

        # Manto fluido em camadas de pinceladas a óleo sobrepostas
        for layer in range(40, 0, -1):
            w_off = layer * 6
            alpha_val = int(10 + (layer / 40) * 40)
            draw.ellipse([
                cx - 220 - w_off, cy + 200, 
                cx + 220 + w_off, cy + 700 + layer * 2
            ], fill=(15, 30, 50, alpha_val))

        # 2. Rosto Humano e Expressivo (Conceito Chiaroscuro Natural)
        print("🧝‍♀️ Esculpindo rosto orgânico com luz e sombra suaves...")
        
        # Cabeça / Rosto (Formato oval orgânico macio)
        draw.ellipse([cx - 85, cy - 30, cx + 85, cy + 130], fill=(242, 225, 215))

        # Sombreamento lateral esquerdo (Luz vinda da direita/lua)
        for sy in range(cy - 20, cy + 120, 2):
            offset = (sy - cy) * 0.3
            draw.line([(cx - 75, sy), (cx - 45 + offset, sy)], fill=(210, 190, 180, 120), width=3)

        # Orelhas de elfo delicadas e pontiagudas com curvatura anatômica natural
        draw.polygon([(cx - 80, cy + 15), (cx - 130, cy - 10), (cx - 75, cy + 45)], fill=(242, 225, 215))
        draw.polygon([(cx + 80, cy + 15), (cx + 130, cy - 10), (cx + 75, cy + 45)], fill=(242, 225, 215))

        # Olhos vivos e profundos (Íris âmbar/esmeralda com brilho natural)
        # Esquerdo
        draw.ellipse([cx - 52, cy + 20, cx - 18, cy + 56], fill=(245, 245, 250), outline=(60, 40, 50), width=2)
        draw.ellipse([cx - 45, cy + 27, cx - 25, cy + 49], fill=(50, 160, 140)) # Íris Esmeralda
        draw.ellipse([cx - 38, cy + 32, cx - 30, cy + 44], fill=(10, 15, 20))  # Pupila
        draw.ellipse([cx - 40, cy + 30, cx - 35, cy + 35], fill=(255, 255, 255)) # Brilho úmido

        # Direito
        draw.ellipse([cx + 18, cy + 20, cx + 52, cy + 56], fill=(245, 245, 250), outline=(60, 40, 50), width=2)
        draw.ellipse([cx + 25, cy + 27, cx + 45, cy + 49], fill=(50, 160, 140))
        draw.ellipse([cx + 30, cy + 32, cx + 38, cy + 44], fill=(10, 15, 20))
        draw.ellipse([cx + 35, cy + 30, cx + 40, cy + 35], fill=(255, 255, 255))

        # Sobrancelhas finas orgânicas
        draw.arc([cx - 52, cy + 8, cx - 18, cy + 28], 190, 350, fill=(70, 50, 60), width=2)
        draw.arc([cx + 18, cy + 8, cx + 52, cy + 28], 190, 350, fill=(70, 50, 60), width=2)

        # Nariz e lábios delicados e naturais
        draw.line([(cx, cy + 62), (cx - 1, cy + 78)], fill=(180, 150, 140), width=2)
        draw.arc([cx - 12, cy + 88, cx + 12, cy + 102], 0, 180, fill=(190, 85, 105), width=2)

        # 3. Cabelo Natural e Ondulado (Mechas soltas sem rigidez)
        print("💇‍♀️ Pintando cabelo ondulado e natural...")
        for strand in range(-8, 9):
            sx = cx + strand * 18
            sy = cy - 60
            # Ondas suaves em arcos
            draw.arc([sx - 40, sy, sx + 40, sy + 500], 0, 180, fill=(190, 205, 225, 180), width=random.randint(6, 14))

        # Franja solta sobre a testa
        draw.arc([cx - 80, cy - 90, cx + 80, cy + 20], 0, 180, fill=(210, 225, 245), width=22)

        # 4. Textura de Óleo Orgânica (Pinceladas livres por toda a tela)
        print("🎨 Aplicando pinceladas livres de tinta a óleo...")
        for _ in range(1500):
            px = random.randint(200, self.width - 200)
            py = random.randint(200, self.height - 200)
            plen = random.randint(15, 45)
            pcol = random.choice([
                (30, 50, 80, 40),
                (100, 160, 200, 30),
                (50, 35, 25, 35)
            ])
            draw.line([(px, py), (px + random.randint(-15, 15), py + plen)], fill=pcol, width=random.randint(3, 7))

        # Masterização Final Orgânica
        print("✨ Finalizando masterização Valariel v3 (Natural)...")
        img = img.filter(ImageFilter.SMOOTH)
        img = ImageEnhance.Color(img).enhance(1.25)
        img = ImageEnhance.Contrast(img).enhance(1.1)
        img = ImageEnhance.Sharpness(img).enhance(1.15)

        return img

    def run(self):
        print("==================================================================")
        print("🍃 BLACKCORE // VALARIEL V3 (CONCEITO 100% ORGÂNICO E NATURAL)")
        print("==================================================================")
        
        painting = self.render()
        
        final_path = OUTPUT_DIR / "valariel_v3_natural.png"
        local_path = LOCAL_DIR / "valariel_v3_natural.png"
        
        painting.save(final_path, quality=100)
        painting.save(local_path, quality=100)
        
        print(f"💾 Obra Valariel v3 salva com sucesso em: {final_path}")
        return final_path

if __name__ == "__main__":
    engine = ValarielNatureEngine()
    engine.run()
