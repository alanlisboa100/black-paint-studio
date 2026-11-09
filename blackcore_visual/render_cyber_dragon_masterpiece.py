#!/usr/bin/env python3
"""
render_cyber_dragon_masterpiece.py - Neo-Tokyo Cyber-Gótica: O Templo do Dragão Mecânico
Renderiza um cenário cyberpunk absurdo, com torres gótico-futuristas, letreiros neon,
chuva fina e um colossal dragão cibernético bioluminescente no topo do templo.
"""

import os
import random
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUTPUT_DIR = Path("/storage/emulated/0/Pictures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DIR = Path.home() / "BLACKCORE-Projects" / "black-paint-studio/gallery_cyber"
LOCAL_DIR.mkdir(parents=True, exist_ok=True)

class CyberDragonEngine:
    def __init__(self):
        self.width = 2400
        self.height = 1800

    def paint_scene(self) -> Image.Image:
        print("⚡ [BLACKCORE CYBER STUDIO] Renderizando Neo-Tokyo Cyber-Gótica (Conceito 3)...")
        img = Image.new("RGB", (self.width, self.height), (3, 5, 12))
        draw = ImageDraw.Draw(img, "RGBA")

        # 1. Céu Noturno de Tempestade Urbanóide (Gradiente Sombrio)
        for y in range(self.height):
            f = y / self.height
            r = int(3 + f * 10)
            g = int(5 + f * 15)
            b = int(12 + f * 35)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # 2. Nuvens Ácidas de Tempestade ao Fundo com Glow Eletrizante (Magenta e Ciano)
        for _ in range(18):
            nx = random.randint(100, self.width - 100)
            ny = random.randint(50, 900)
            nr = random.randint(250, 600)
            glow_col = random.choice([(120, 20, 100, 22), (20, 100, 140, 22), (80, 20, 140, 20)])
            draw.ellipse([nx - nr, ny - nr//2, nx + nr, ny + nr//2], fill=glow_col)

        # 3. Mega Arranha-Céus e Templos Tradicionais Fundidos (Arquitetura Cyber-Gótica)
        # Formato de silhuetas verticais complexas
        towers = [
            (50, 150, 200, 1350, (10, 14, 25)),
            (230, 80, 240, 1420, (14, 20, 35)),
            (460, 200, 180, 1300, (8, 12, 22)),
            (630, 40, 280, 1460, (18, 25, 42)),  # O Templo Principal Central
            (900, 120, 210, 1380, (12, 17, 30)),
            (1100, 90, 250, 1410, (15, 22, 38)),
            (1340, 170, 190, 1330, (9, 13, 24)),
            (1520, 60, 260, 1440, (16, 23, 40)),
            (1770, 130, 210, 1370, (11, 16, 28)),
            (1970, 100, 230, 1400, (14, 20, 35)),
            (2190, 160, 180, 1340, (9, 13, 23))
        ]

        for tx, ty, tw, th, tcol in towers:
            # Estrutura principal
            draw.rectangle([tx, ty, tx + tw, self.height - 400], fill=tcol, outline=(35, 50, 75), width=2)
            
            # Telhados curvados tradicionais combinados com antenas futuristas
            if tw > 220:
                # Topo em estilo Pagode Futurista
                draw.polygon([
                    (tx - 30, ty + 40),
                    (tx + tw // 2, ty - 80),
                    (tx + tw + 30, ty + 40)
                ], fill=(25, 35, 55), outline=(0, 220, 255), width=2)
            
            # Janelas de Neon e Painéis Holográficos verticais
            num_cols = random.randint(5, 8)
            col_w = tw // num_cols
            for c in range(num_cols):
                for wy in range(ty + 60, self.height - 420, 50):
                    if random.random() < 0.35: continue
                    ww = random.choice([6, 10, 14])
                    wh = random.choice([20, 35, 50])
                    wx = tx + c * col_w + random.randint(2, max(2, col_w - ww - 2))
                    neon_col = random.choice([
                        (0, 230, 255),   # Ciano Neon
                        (255, 40, 140),  # Magenta Neon
                        (255, 180, 50),  # Amarelo Âmbar
                        (160, 50, 255)   # Roxo Eletrizante
                    ])
                    draw.rectangle([wx, wy, wx + ww, wy + wh], fill=neon_col)

        # 4. O COLOSSAL DRAGÃO MECÂNICO NO TOPO DO TEMPLO CENTRAL
        # Posicionado no topo da torre central (X: 630..910, Y: 40)
        dx, dy = 770, 80
        # Corpo serpentino mecano-biológico enrolado na agulha central
        dragon_segments = [
            (dx, dy + 200, 70),
            (dx - 60, dy + 120, 60),
            (dx + 50, dy + 50, 50),
            (dx - 30, dy - 20, 40),
            (dx + 20, dy - 90, 35) # Cabeça com chifres cyber
        ]
        for ds_x, ds_y, ds_r in dragon_segments:
            # Escamas de titânio escuro com bioluminescência ciano/magenta
            draw.ellipse([ds_x - ds_r, ds_y - ds_r, ds_x + ds_r, ds_y + ds_r], fill=(15, 22, 35), outline=(0, 255, 200), width=3)
            # Núcleo de energia nas costas do dragão
            draw.ellipse([ds_x - ds_r//2, ds_y - ds_r//2, ds_x + ds_r//2, ds_y + ds_r//2], fill=(255, 0, 128))

        # Olhos laser do dragão (Brilho intenso)
        draw.ellipse([dx + 5, dy - 95, dx + 15, dy - 85], fill=(0, 255, 255))
        draw.ellipse([dx - 5, dy - 95, dx + 5, dy - 85], fill=(0, 255, 255))

        # Vapor saindo das narinas do dragão mecânico
        for v in range(5):
            vr = 8 + v * 6
            v_alpha = max(10, 100 - v * 18)
            draw.ellipse([dx - 15 - v*12 - vr, dy - 110 - v*15 - vr, dx - 15 - v*12 + vr, dy - 110 - v*15 + vr], fill=(200, 230, 255, v_alpha))

        # 5. LETREIRO HOLOGRÁFICO GIGANTE EM NEON (Kanji / Cyber Script no Horizonte)
        # Painel flutuante cyberpunk
        board_x, board_y, board_w, board_h = 950, 450, 500, 120
        draw.rectangle([board_x, board_y, board_x + board_w, board_y + board_h], fill=(10, 10, 18, 200), outline=(0, 240, 255), width=4)
        # Brilho de fundo do painel
        draw.rectangle([board_x - 10, board_y - 10, board_x + board_w + 10, board_y + board_h + 10], fill=(255, 0, 128, 40))

        # 6. ASFALTO MOLHADO COM REFLEXOS GIGANTES DE NEON E CHUVA FINA
        road_y = 1380
        draw.rectangle([0, road_y, self.width, self.height], fill=(5, 8, 14))

        # Reflexos espelhados no asfalto molhado
        for x_ref in range(0, self.width, 8):
            ref_col = random.choice([
                (0, 230, 255, 85),
                (255, 40, 140, 85),
                (255, 180, 50, 75),
                (160, 50, 255, 80)
            ])
            wave_len = random.randint(120, 350)
            start_y = road_y + random.randint(5, 40)
            draw.line([(x_ref, start_y), (x_ref + random.randint(-15, 15), start_y + wave_len)], fill=ref_col, width=random.randint(4, 7))

        # Chuva fina cinematográfica em alta densidade
        for _ in range(800):
            rx = random.randint(0, self.width)
            ry = random.randint(0, self.height - 150)
            rlen = random.randint(20, 45)
            draw.line([(rx, ry), (rx - 8, ry + rlen)], fill=(180, 220, 255, 60), width=1)

        # 7. MASTERIZAÇÃO ÓLEO/IMPASTO FINA (Estilo Concept Art AAA)
        print("🔄 Aplicando masterização final Cyberpunk a óleo...")
        img = img.filter(ImageFilter.SMOOTH_MORE)
        img = ImageEnhance.Color(img).enhance(1.4)
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Sharpness(img).enhance(1.3)

        return img

    def run(self):
        print("==================================================================")
        print("🤖 BLACKCORE // RENDERIZADOR NEO-TOKYO CYBER-GÓTICA")
        print("==================================================================")
        
        painting = self.paint_scene()
        
        final_path = OUTPUT_DIR / "neo_tokyo_cyber_dragon_masterpiece.png"
        local_path = LOCAL_DIR / "neo_tokyo_cyber_dragon_masterpiece.png"
        
        painting.save(final_path, quality=100)
        painting.save(local_path, quality=100)
        
        print(f"💾 Obra-prima Cyberpunk salva com sucesso em: {final_path}")
        return final_path

if __name__ == "__main__":
    engine = CyberDragonEngine()
    engine.run()
