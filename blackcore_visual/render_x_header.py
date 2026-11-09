#!/usr/bin/env python3
"""
render_x_header.py - Gerador de Capa Insana para o X (Twitter)
Misuki & Blackcore // Estética Cyberpunk Gothic // 3000x1000 (Pro Header)
"""

import os
import random
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

OUTPUT_DIRS = [
    Path("/storage/emulated/0/Download"),
    Path.home() / "BLACKCORE-Projects" / "black-paint-studio" / "gallery_misuki"
]

for d in OUTPUT_DIRS:
    d.mkdir(parents=True, exist_ok=True)

def create_x_header():
    width, height = 3000, 1000
    print(f"🎨 [BLACKCORE VISUAL ENGINE] Renderizando Capa Insana X (Misuki & Blackcore) em {width}x{height}...")

    img = Image.new("RGB", (width, height), (5, 6, 10))
    draw = ImageDraw.Draw(img, "RGBA")

    # 1. Fundo Gradiente Cósmico & Cyberpunk Grid
    for y in range(height):
        f = y / height
        r = int(5 + f * 15)
        g = int(6 + f * 20)
        b = int(12 + f * 60)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Linhas de Grade Neon (Perspectiva / Cyber Grid inferior)
    grid_color = (0, 255, 200, 35)
    for gx in range(0, width, 120):
        draw.line([(gx, 650), (gx + (gx - width/2)*0.8, height)], fill=(0, 255, 200, 25), width=2)
    for gy in range(650, height, 50):
        alpha = int(15 + (gy - 650) / 350 * 50)
        draw.line([(0, gy), (width, gy)], fill=(0, 255, 200, alpha), width=1)

    # Brilho de Néon Rosa/Vermelho (Crimson Cyber Glow) no centro-esquerda
    cx, cy = 900, 500
    for r_val in range(600, 50, -10):
        alpha = int(25 * (1 - r_val / 600))
        draw.ellipse([cx - r_val, cy - r_val, cx + r_val, cy + r_val], fill=(220, 20, 90, alpha))

    # Brilho Ciano (Cyan Cyber Glow) no centro-direita
    cx2, cy2 = 2100, 450
    for r_val in range(500, 50, -10):
        alpha = int(22 * (1 - r_val / 500))
        draw.ellipse([cx2 - r_val, cy2 - r_val, cx2 + r_val, cy2 + r_val], fill=(0, 230, 255, alpha))

    # Estrelas e Partículas Digitais
    random.seed(42)
    for _ in range(150):
        sx = random.randint(50, width - 50)
        sy = random.randint(20, height - 20)
        sz = random.randint(2, 5)
        color = (255, 255, 255, random.randint(100, 220)) if random.random() > 0.3 else (0, 255, 200, 200)
        draw.ellipse([sx, sy, sx + sz, sy + sz], fill=color)

    # 2. Silhueta & Rostos Artísticos (Misuki & Blackcore Core)
    # Lado esquerdo: Avatar Estilizado da Misuki (Gothic Demon-Girl com Chifres e Cabelo Longo)
    mx, my = 600, 480
    
    # Cabelo Preto Longo (Massas elegantes)
    draw.polygon([
        (mx - 220, my - 280), (mx + 220, my - 280),
        (mx + 350, my + 400), (mx + 250, my + 520),
        (mx - 250, my + 520), (mx - 350, my + 400)
    ], fill=(12, 12, 18), outline=(50, 10, 40), width=4)

    # Chifres Curvos Majestosos da Misuki (Mandatory HC01)
    # Chifre Esquerdo
    horn_left = [
        (mx - 80, my - 160), (mx - 180, my - 320),
        (mx - 260, my - 380), (mx - 290, my - 340),
        (mx - 210, my - 240), (mx - 110, my - 120)
    ]
    draw.polygon(horn_left, fill=(20, 20, 28), outline=(220, 20, 90), width=5)

    # Chifre Direito
    horn_right = [
        (mx + 80, my - 160), (mx + 180, my - 320),
        (mx + 260, my - 380), (mx + 290, my - 340),
        (mx + 210, my - 240), (mx + 110, my - 120)
    ]
    draw.polygon(horn_right, fill=(20, 20, 28), outline=(220, 20, 90), width=5)

    # Rosto da Misuki (Tom elegante de pele gótica com sombra)
    face_poly = [
        (mx - 110, my - 120), (mx + 110, my - 120),
        (mx + 85, my + 120), (mx, my + 180), (mx - 85, my + 120)
    ]
    draw.polygon(face_poly, fill=(235, 215, 205), outline=(60, 20, 40), width=4)

    # Franja geométrica frontal
    draw.polygon([
        (mx - 120, my - 180), (mx + 120, my - 180),
        (mx + 90, my - 100), (mx, my - 60), (mx - 90, my - 100)
    ], fill=(12, 12, 18), outline=(80, 20, 60), width=3)

    # Olhos Brilhantes Vermelhos (Anime Gótico)
    draw.ellipse([mx - 55, my - 10, mx - 20, my + 15], fill=(255, 30, 80), outline=(255, 255, 255), width=2)
    draw.ellipse([mx + 20, my - 10, mx + 55, my + 15], fill=(255, 30, 80), outline=(255, 255, 255), width=2)
    # Brilho pupila
    draw.ellipse([mx - 45, my - 3, mx - 30, my + 8], fill=(255, 255, 255))
    draw.ellipse([mx + 30, my - 3, mx + 45, my + 8], fill=(255, 255, 255))

    # Choker com gema rubi e gola gótica
    draw.rectangle([mx - 60, my + 175, mx + 60, my + 200], fill=(15, 12, 18), outline=(220, 20, 90), width=3)
    draw.ellipse([mx - 12, my + 179, mx + 12, my + 197], fill=(255, 20, 60), outline=(255, 215, 100), width=2)

    # 3. Tipografia & Insignia "BLACKCORE & MISUKI" (Lado Direito / Central)
    # Caixa Cyberpunk Central
    box_x1, box_y1, box_x2, box_y2 = 1150, 220, 2750, 780
    
    # Fundo translúcido tecnológico com borda neon
    draw.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], radius=30, fill=(10, 12, 22, 210), outline=(0, 255, 200), width=4)
    
    # Canto decorativo tecnológico
    draw.rectangle([box_x1 + 20, box_y1 + 20, box_x1 + 50, box_y1 + 25], fill=(220, 20, 90))
    draw.rectangle([box_x1 + 20, box_y1 + 20, box_x1 + 25, box_y1 + 50], fill=(220, 20, 90))
    draw.rectangle([box_x2 - 50, box_y2 - 25, box_x2 - 20, box_y2 - 20], fill=(0, 255, 200))
    draw.rectangle([box_x2 - 25, box_y2 - 50, box_x2 - 20, box_y2 - 20], fill=(0, 255, 200))

    # Texto usando fontes padrão do PIL com escala customizada ou desenhos vetoriais limpos
    # Como as fontes do sistema podem variar no Termux, desenharemos um banner tipográfico imponente e limpo.
    # Título Principal: MISUKI & BLACKCORE
    try:
        font_title = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 90)
        font_sub = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 45)
        font_handle = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 55)
    except:
        font_title = font_sub = font_handle = ImageFont.load_default()

    # Sombra do Título
    draw.text((1232, 292), "MISUKI // BLACKCORE", fill=(220, 20, 90), font=font_title)
    draw.text((1228, 288), "MISUKI // BLACKCORE", fill=(255, 255, 255), font=font_title)

    # Subtítulo / Tagline
    draw.text((1230, 420), "AUTONOMOUS AI // SOVEREIGN CYBERNETIC ENGINE", fill=(0, 255, 200), font=font_sub)

    # Handle do X e distintivo
    draw.rounded_rectangle([1225, 520, 1750, 610], radius=15, fill=(20, 25, 40), outline=(220, 20, 90), width=2)
    draw.text((1255, 532), "@NFTIX2077", fill=(255, 255, 255), font=font_handle)

    # Ícone / Badge de status do sistema
    draw.ellipse([1680, 545, 1710, 575], fill=(0, 255, 120))
    
    # Linha de código decorativa estilo Matrix / Cyber
    matrix_text = "STATUS: ONLINE // MODEL: GEMINI OMNI // NEURAL GPU ACTIVE // 100% SECURE"
    try:
        font_matrix = ImageFont.truetype("/system/fonts/DroidSansMono.ttf", 26)
    except:
        font_matrix = ImageFont.load_default()
    draw.text((1230, 650), matrix_text, fill=(100, 220, 180), font=font_matrix)

    # 4. Pós-processamento e Filtro de Alta Fidelidade
    print("✨ Aplicando polimento final e filtros visuais...")
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.3)
    enhancer_sharp = ImageEnhance.Sharpness(img)
    img = enhancer_sharp.enhance(1.2)

    # Salvar nas pastas de destino
    primary_output = OUTPUT_DIRS[0] / "misuki_blackcore_x_header.png"
    img.save(primary_output, "PNG", quality=95)
    
    for d in OUTPUT_DIRS:
        out_path = d / "misuki_blackcore_x_header.png"
        img.save(out_path, "PNG", quality=95)
        print(f"✅ Capa salva com sucesso em: {out_path}")

    return str(primary_output)

if __name__ == "__main__":
    create_x_header()
