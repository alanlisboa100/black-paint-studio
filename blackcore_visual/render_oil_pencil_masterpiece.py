#!/usr/bin/env python3
"""
render_oil_pencil_masterpiece.py - Pintura Híbrida Óleo + Lápis Profissional (100% Humano/Orgânico)
Simula traços cruzados de lápis de carvão/grafite (cross-hatching) combinados com pinceladas
espessas de tinta a óleo (impasto) em uma tela de linho texturizada. Sem geradores de IA.
"""

import os
import random
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUTPUT_DIR = Path("/storage/emulated/0/Pictures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DIR = Path.home() / "BLACKCORE-Projects" / "black-paint-studio/gallery_oil_pencil"
LOCAL_DIR.mkdir(parents=True, exist_ok=True)

class OilPencilStudio:
    def __init__(self):
        self.width = 2400
        self.height = 1800

    def render(self) -> Image.Image:
        print("🎨 [BLACKCORE STUDIO] Iniciando Pintura Híbrida: Óleo + Lápis Profissional (100% Orgânico)...")
        
        # 1. Tela de Linho Texturizada (Base de Pintura Artística)
        img = Image.new("RGB", (self.width, self.height), (245, 242, 235))
        draw = ImageDraw.Draw(img, "RGBA")

        # Adicionar micro-textura de grãos de tela de linho
        print("🧵 Aplicando textura de tela de linho e papel de desenho...")
        for x in range(0, self.width, 4):
            for y in range(0, self.height, 4):
                if random.random() < 0.25:
                    shade = random.randint(230, 250)
                    draw.point((x + random.randint(0, 2), y + random.randint(0, 2)), fill=(shade, shade - 2, shade - 5))

        # 2. Esboço com Lápis Profissional (Traços Cruzados / Cross-Hatching Orgânicos)
        print("✏️ Executando esboços e sombreamentos com lápis de carvão/grafite profissional...")
        random.seed(1337)
        
        # Sombra de fundo com hachuras de lápis estruturais
        for _ in range(8000):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            length = random.randint(20, 80)
            angle = random.uniform(-0.8, 0.8)
            x2 = x1 + int(math.cos(angle) * length)
            y2 = y1 + int(math.sin(angle) * length)
            
            # Intensidade baseada na posição (sombreamento dramático nas bordas)
            dist_center = math.hypot(x1 - self.width//2, y1 - self.height//2)
            if dist_center > 600:
                alpha = random.randint(20, 70)
                draw.line([(x1, y1), (x2, y2)], fill=(40, 35, 30, alpha), width=1)

        # 3. Camadas de Tinta a Óleo (Impasto e Pinceladas Orgânicas Visíveis)
        print("🖌️ Aplicando camadas espessas de tinta a óleo com pinceladas expressivas...")
        
        # Paisagem Clássica Expressiva: Árvore Solitária sob Luar Dramático com Montanhas e Lago
        # Fundo: Céu a Óleo (Gradiente de Índigo Profundo, Cobre e Âmbar)
        for y in range(self.height):
            f = y / self.height
            r = int(25 + f * 45)
            g = int(20 + f * 35)
            b = int(40 + f * 70)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # Nuvens a Óleo com Pinceladas Circulares (Estilo Impasto)
        for _ in range(120):
            nx = random.randint(200, self.width - 200)
            ny = random.randint(100, 900)
            nr = random.randint(100, 300)
            cloud_col = random.choice([
                (90, 70, 110, 35),
                (140, 90, 100, 30),
                (60, 80, 120, 40)
            ])
            draw.ellipse([nx - nr, ny - nr//2, nx + nr, ny + nr//2], fill=cloud_col)

        # Lua Poética Brilhante
        mx, my, mr = 1750, 400, 120
        for r_val in range(mr + 150, mr, -3):
            alpha = int(40 * (1 - (r_val - mr) / 150))
            draw.ellipse([mx - r_val, my - r_val, mx + r_val, my + r_val], fill=(255, 230, 180, alpha))
        draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(255, 248, 230))

        # Montanhas Distantes com Hachuras de Lápis sobrepostas a Óleo
        mountain_points = [
            [(0, 1200), (350, 850), (800, 980), (1300, 750), (1800, 920), (2400, 820), (2400, 1800), (0, 1800)]
        ]
        for m in mountain_points:
            draw.polygon(m, fill=(28, 24, 38))

        # Textura de Lápis Profissional nas Montanhas
        for _ in range(4000):
            mx_start = random.randint(0, self.width)
            my_start = random.randint(750, 1200)
            draw.line([(mx_start, my_start), (mx_start + random.randint(-15, 15), my_start + random.randint(20, 50))], fill=(15, 12, 18, 160), width=1)

        # Árvore Solitária Centrada em Primeiro Plano (Tronco e Galhos detalhados à mão)
        tree_x, tree_y = 700, 1350
        # Tronco principal a óleo e lápis
        draw.polygon([
            (tree_x - 40, tree_y + 200),
            (tree_x - 20, tree_y - 250),
            (tree_x + 25, tree_y - 250),
            (tree_x + 45, tree_y + 200)
        ], fill=(35, 25, 20))

        # Galhos expressivos
        branches = [
            (tree_x, tree_y - 180, tree_x - 250, tree_y - 380, 22),
            (tree_x, tree_y - 120, tree_x + 280, tree_y - 350, 20),
            (tree_x - 10, tree_y - 220, tree_x - 120, tree_y - 500, 14),
            (tree_x + 10, tree_y - 200, tree_x + 150, tree_y - 480, 15),
            (tree_x - 80, tree_y - 300, tree_x - 200, tree_y - 420, 10),
            (tree_x + 90, tree_y - 280, tree_x + 210, tree_y - 400, 10)
        ]
        for bx1, by1, bx2, by2, bwidth in branches:
            draw.line([(bx1, by1), (bx2, by2)], fill=(30, 20, 15), width=bwidth)
            # Sombra e hachuras de lápis no tronco e galhos
            for _ in range(15):
                hx = random.randint(min(bx1, bx2), max(bx1, bx2))
                hy = random.randint(min(by1, by2), max(by1, by2))
                draw.line([(hx, hy), (hx + random.randint(-5, 5), hy + random.randint(10, 25))], fill=(10, 8, 5, 200), width=1)

        # Folhagem Expressiva (Mistura de Impasto a Óleo Verde/Dourado/Bronze + Hachuras de Lápis)
        print("🌿 Detalhando folhagem orgânica com pinceladas e hachuras finas...")
        for _ in range(600):
            fx = random.randint(tree_x - 350, tree_x + 380)
            fy = random.randint(tree_y - 600, tree_y - 150)
            fr = random.randint(40, 90)
            leaf_col = random.choice([
                (45, 65, 40, 180),
                (70, 90, 50, 160),
                (120, 100, 50, 170),
                (30, 45, 30, 200)
            ])
            draw.ellipse([fx - fr, fy - fr//2, fx + fr, fy + fr//2], fill=leaf_col)

        # Detalhes finais com lápis afiado (Contornos artísticos e texturas de alta precisão)
        for _ in range(3000):
            px = random.randint(tree_x - 400, tree_x + 400)
            py = random.randint(tree_y - 650, tree_y + 100)
            draw.point((px, py), fill=(20, 15, 10, 220))

        # 4. Lago com Reflexos Lunares Impasto
        lake_y = 1350
        draw.rectangle([0, lake_y, self.width, self.height], fill=(20, 25, 38))
        for x_ref in range(0, self.width, 8):
            ref_col = random.choice([
                (255, 230, 180, 80),
                (140, 110, 150, 70),
                (60, 80, 110, 90)
            ])
            draw.line([(x_ref, lake_y + 10), (x_ref + random.randint(-10, 10), lake_y + random.randint(50, 350))], fill=ref_col, width=random.randint(2, 6))

        # 5. Masterização Final (Protegendo a textura de papel e óleo)
        print("✨ Finalizando masterização artística 100% humana...")
        img = img.filter(ImageFilter.SMOOTH)
        img = ImageEnhance.Color(img).enhance(1.2)
        img = ImageEnhance.Contrast(img).enhance(1.15)
        img = ImageEnhance.Sharpness(img).enhance(1.25)

        return img

    def run(self):
        print("==================================================================")
        print("🖤 BLACKCORE // PINTURA ÓLEO + LÁPIS PROFISSIONAL (100% HUMANO)")
        print("==================================================================")
        
        painting = self.render()
        
        final_path = OUTPUT_DIR / "pintura_oleo_lapis_profissional.png"
        local_path = LOCAL_DIR / "pintura_oleo_lapis_profissional.png"
        
        painting.save(final_path, quality=100)
        painting.save(local_path, quality=100)
        
        print(f"💾 Obra-prima híbrida salva com sucesso em: {final_path}")
        return final_path

if __name__ == "__main__":
    studio = OilPencilStudio()
    studio.run()
