#!/usr/bin/env python3
"""
render_gothic_character.py - Renderizador Artístico de Alta Definição
Pintura Digital da Personagem Gótica Cyberpunk com Iluminação Dramática Preto/Vermelho
"""

import math, os, random, subprocess, sys, time
from pathlib import Path
from termux_compat import scan_media, output_dir
from PIL import Image, ImageDraw, ImageFilter, ImageFont

def render_character(width=1200, height=1200) -> Image.Image:
    # 1. Canvas base em altíssima definição com canal RGBA
    img = Image.new("RGBA", (width, height), (3, 2, 7, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    
    cx = width // 2
    cy = height // 2

    # Layer 1: Fundo Atmosférico Cyber/Dark
    # Gradiente escuro com toque roxo/azul petróleo
    for y in range(height):
        t = y / height
        r = int(2 + t * 12)
        g = int(2 + t * 4)
        b = int(6 + t * 16)
        draw.line([0, y, width, y], fill=(r, g, b, 255))

    # Luzes vermelhas bokeh e arquitetura futurista desfocada ao fundo
    bg_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg_overlay, "RGBA")

    # Silhuetas de colunas/pilares cibernéticos desfocados no fundo
    for pillar_x in [int(width*0.12), int(width*0.28), int(width*0.72), int(width*0.88)]:
        p_w = random.randint(35, 60)
        bg_draw.rectangle([pillar_x, 0, pillar_x + p_w, height], fill=(15, 5, 12, 160))
        # Linha neon discreta na arquitetura
        bg_draw.line([pillar_x, 0, pillar_x, height], fill=(180, 0, 35, 90), width=2)

    # Círculos de luz vermelha bokeh suave no fundo
    for _ in range(12):
        bx = random.randint(int(width*0.1), int(width*0.9))
        by = random.randint(int(height*0.1), int(height*0.75))
        br = random.randint(40, 110)
        bg_draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(220, 10, 40, random.randint(15, 35)))

    # Desfoca o fundo para dar profundidade de campo
    bg_overlay = bg_overlay.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, bg_overlay)
    draw = ImageDraw.Draw(img, "RGBA")

    # Layer 2: Luz Vermelha Traseira Volumétrica (Backlight Rim Glow)
    backlight = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    bl_draw = ImageDraw.Draw(backlight, "RGBA")
    
    # Brilho vermelho vindo de trás do perfil da personagem
    for r in range(int(width * 0.38), 0, -5):
        alpha = int(120 * (1 - r / (width * 0.38))**1.8)
        bl_draw.ellipse([cx - r, cy - r - 40, cx + r, cy + r - 40], fill=(230, 15, 40, alpha))

    backlight = backlight.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, backlight)
    draw = ImageDraw.Draw(img, "RGBA")

    # Layer 3: Cabelo Preto Volumoso (Camada Traseira)
    # Silhueta de cabelo longo volumoso caindo pelas costas
    hair_back = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    hb_draw = ImageDraw.Draw(hair_back, "RGBA")

    # Massa volumosa do cabelo
    hair_points_left = [
        (cx - 80, cy - 220), (cx - 240, cy - 200), (cx - 360, cy - 80),
        (cx - 420, cy + 120), (cx - 380, cy + 380), (cx - 280, cy + 550),
        (cx - 120, cy + 500), (cx - 60, cy + 300)
    ]
    hair_points_right = [
        (cx + 80, cy - 220), (cx + 240, cy - 200), (cx + 360, cy - 80),
        (cx + 420, cy + 120), (cx + 380, cy + 380), (cx + 280, cy + 550),
        (cx + 120, cy + 500), (cx + 60, cy + 300)
    ]
    hb_draw.polygon(hair_points_left, fill=(8, 8, 14, 255))
    hb_draw.polygon(hair_points_right, fill=(8, 8, 14, 255))

    # Mechas volumosas onduladas com reflexos frios
    for i in range(120):
        side = -1 if i % 2 == 0 else 1
        x_start = cx + side * random.randint(40, 260)
        y_start = cy - random.randint(180, 240)
        
        # Curva de mecha
        cp1_x = x_start + side * random.randint(60, 220)
        cp1_y = y_start + random.randint(150, 300)
        cp2_x = x_start + side * random.randint(30, 180)
        cp2_y = y_start + random.randint(350, 550)

        # Desenha fios com gradiente preto/cinza-frio
        strand_w = random.randint(4, 12)
        cold_color = random.choice([
            (10, 10, 16, 255),
            (15, 18, 28, 240),
            (30, 42, 65, 180),  # Reflexo azul frio
            (60, 80, 115, 110)   # Brilho prateado frio
        ])
        hb_draw.line([x_start, y_start, cp1_x, cp1_y, cp2_x, cp2_y], fill=cold_color, width=strand_w)

    img = Image.alpha_composite(img, hair_back)
    draw = ImageDraw.Draw(img, "RGBA")

    # Layer 4: Corpo & Roupa Gótica Elegante
    body = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    body_draw = ImageDraw.Draw(body, "RGBA")

    # Pescoço & Ombros
    neck_w = 90
    shoulder_y = cy + 220
    
    # Ombros
    body_draw.polygon([
        (cx - neck_w, cy + 120), (cx + neck_w, cy + 120),
        (cx + 340, shoulder_y + 240), (cx - 340, shoulder_y + 240)
    ], fill=(12, 12, 18, 255))

    # Vestido/Corset Gótico Preto Elegante
    corset_top = cy + 180
    body_draw.polygon([
        (cx - 110, corset_top), (cx + 110, corset_top),
        (cx + 160, height), (cx - 160, height)
    ], fill=(8, 8, 12, 255))

    # Bordas e Detalhes Vermelhos Discretos na Roupa
    # Costuras e debrum carmesim escuro
    crimson_trim = (180, 10, 35, 220)
    body_draw.line([cx - 110, corset_top, cx, corset_top + 40, cx + 110, corset_top], fill=crimson_trim, width=3)
    body_draw.line([cx - 40, corset_top + 40, cx - 40, height], fill=crimson_trim, width=2)
    body_draw.line([cx + 40, corset_top + 40, cx + 40, height], fill=crimson_trim, width=2)

    # Choker / Gargantilha Gótica Prateada com Pedra Vermelha
    choker_y = cy + 140
    body_draw.rectangle([cx - 50, choker_y, cx + 50, choker_y + 16], fill=(18, 18, 24, 255), outline=(140, 140, 160, 255), width=1)
    # Pingente de Rubi em Gota
    pendant_x, pendant_y = cx, choker_y + 26
    body_draw.ellipse([pendant_x - 8, pendant_y - 8, pendant_x + 8, pendant_y + 8], fill=(220, 10, 40, 255))
    body_draw.ellipse([pendant_x - 3, pendant_y - 3, pendant_x + 3, pendant_y + 3], fill=(255, 200, 220, 255))

    img = Image.alpha_composite(img, body)
    draw = ImageDraw.Draw(img, "RGBA")

    # Layer 5: Pele Clara & Estrutura Facial
    face_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    face_draw = ImageDraw.Draw(face_layer, "RGBA")

    # Tom de pele pálido/clara (porcelana)
    skin_color = (242, 238, 248, 255)
    skin_shadow = (200, 195, 215, 255)

    # Pescoço
    face_draw.polygon([
        (cx - 55, cy + 40), (cx + 55, cy + 40),
        (cx + 65, cy + 150), (cx - 65, cy + 150)
    ], fill=skin_color)
    # Sombra do pescoço abaixo do queixo
    face_draw.polygon([
        (cx - 55, cy + 40), (cx + 55, cy + 40),
        (cx + 45, cy + 85), (cx - 45, cy + 85)
    ], fill=(180, 175, 200, 200))

    # Formato do Rosto (Oval elegante, queixo fino)
    face_poly = [
        (cx - 130, cy - 140), (cx - 145, cy - 40), (cx - 135, cy + 20),
        (cx - 95, cy + 80), (cx - 45, cy + 120), (cx, cy + 130),
        (cx + 45, cy + 120), (cx + 95, cy + 80), (cx + 135, cy + 20),
        (cx + 145, cy - 40), (cx + 130, cy - 140), (cx, cy - 180)
    ]
    face_draw.polygon(face_poly, fill=skin_color)

    # Sombreamento frio nas bochechas e contorno do queixo (iluminação fria frontal)
    face_draw.polygon([
        (cx - 145, cy - 40), (cx - 135, cy + 20), (cx - 95, cy + 80),
        (cx - 110, cy + 20), (cx - 120, cy - 30)
    ], fill=(210, 205, 225, 120))
    face_draw.polygon([
        (cx + 145, cy - 40), (cx + 135, cy + 20), (cx + 95, cy + 80),
        (cx + 110, cy + 20), (cx + 120, cy - 30)
    ], fill=(210, 205, 225, 120))

    # Nariz delicado
    nose_y = cy + 20
    face_draw.line([cx - 4, nose_y + 15, cx, nose_y + 20, cx + 4, nose_y + 15], fill=(160, 150, 180, 220), width=2)
    face_draw.line([cx, cy - 30, cx, nose_y + 18], fill=(210, 205, 230, 90), width=2)

    # Boca (Expressão calma, confiante e levemente intimidadora - sorriso discreto)
    mouth_y = cy + 72
    # Lábios com tom vinho/gótico leve
    face_draw.polygon([
        (cx - 32, mouth_y), (cx - 12, mouth_y - 4), (cx, mouth_y - 2),
        (cx + 12, mouth_y - 4), (cx + 32, mouth_y),
        (cx + 16, mouth_y + 10), (cx, mouth_y + 12), (cx - 16, mouth_y + 10)
    ], fill=(130, 20, 45, 240))
    face_draw.line([cx - 34, mouth_y - 1, cx + 34, mouth_y - 1], fill=(50, 5, 15, 255), width=2)

    img = Image.alpha_composite(img, face_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Layer 6: Chifres Negros Curvados de Obsidiana
    horns = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    horns_draw = ImageDraw.Draw(horns, "RGBA")

    def draw_curved_horn(is_left=True):
        side = -1 if is_left else 1
        base_x = cx + side * 110
        base_y = cy - 140
        
        # Pontos de curva elegante varrendo para fora e subindo
        horn_pts = []
        steps = 60
        for i in range(steps):
            t = i / steps
            # Equação paramétrica de curva estilizada
            hx = base_x + side * (math.sin(t * math.pi * 0.8) * 190 + t * 40)
            hy = base_y - (t * 320 + math.cos(t * math.pi * 0.5) * 40)
            rad = int((1 - t) * 32 + 2)
            horn_pts.append((hx, hy, rad))

        # Renderiza corpo do chifre com gradiente obsidiana
        for hx, hy, rad in horn_pts:
            # Base preta obsidiana
            horns_draw.ellipse([hx - rad, hy - rad, hx + rad, hy + rad], fill=(10, 10, 16, 255))
            # Especular frio (textura mineral polida)
            horns_draw.ellipse([hx - rad*0.5, hy - rad*0.5, hx + rad*0.2, hy + rad*0.2], fill=(80, 95, 120, 60))
            # Luz de recorte vermelha na borda externa (Rim light)
            rim_offset = side * rad * 0.7
            horns_draw.ellipse([hx + rim_offset - 3, hy - 3, hx + rim_offset + 3, hy + 3], fill=(230, 15, 40, 180))

    draw_curved_horn(is_left=True)
    draw_curved_horn(is_left=False)

    img = Image.alpha_composite(img, horns)
    draw = ImageDraw.Draw(img, "RGBA")

    # Layer 7: Olhos Vermelhos Intensos (Ponto Focal Absoluto)
    eyes = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    eyes_draw = ImageDraw.Draw(eyes, "RGBA")

    eye_y = cy - 25
    eye_spacing = 68
    eye_w = 42
    eye_h = 22

    for side in [-1, 1]:
        ex = cx + side * eye_spacing
        
        # Sobrancelhas escuras marcantes e levemente arqueadas (confiantes/intimidadoras)
        brow_y = eye_y - 28
        eyes_draw.polygon([
            (ex - side * 28, brow_y + 4), (ex - side * 10, brow_y - 8),
            (ex + side * 28, brow_y - 2), (ex + side * 20, brow_y - 12),
            (ex - side * 10, brow_y - 14)
        ], fill=(15, 12, 20, 255))

        # Contorno do Olho Gótico (Delineador Preto)
        eyes_draw.ellipse([ex - eye_w, eye_y - eye_h, ex + eye_w, eye_y + eye_h], fill=(15, 15, 22, 255))
        # Esclera clara levemente fria
        eyes_draw.ellipse([ex - eye_w + 3, eye_y - eye_h + 3, ex + eye_w - 3, eye_y + eye_h - 3], fill=(235, 235, 245, 255))

        # Íris Vermelha Intensa com Brilho Radiante
        iris_rad = 16
        # Glow vermelho ao redor do olho (Efeito Ponto Focal)
        for g_r in range(35, iris_rad, -2):
            g_alpha = int(90 * (1 - (g_r - iris_rad) / 20))
            eyes_draw.ellipse([ex - g_r, eye_y - g_r, ex + g_r, eye_y + g_r], fill=(255, 0, 50, g_alpha))

        # Íris Rubi
        eyes_draw.ellipse([ex - iris_rad, eye_y - iris_rad, ex + iris_rad, eye_y + iris_rad], fill=(220, 0, 40, 255))
        eyes_draw.ellipse([ex - iris_rad + 3, eye_y - iris_rad + 3, ex + iris_rad - 3, eye_y + iris_rad - 3], fill=(255, 60, 90, 255))

        # Pupila Fenda/Gato Intimidadora
        eyes_draw.ellipse([ex - 3, eye_y - 12, ex + 3, eye_y + 12], fill=(10, 0, 5, 255))

        # Brilho Especular Intenso no Olho
        eyes_draw.ellipse([ex - 6, eye_y - 8, ex - 1, eye_y - 3], fill=(255, 255, 255, 255))
        eyes_draw.ellipse([ex + 2, eye_y + 2, ex + 5, eye_y + 5], fill=(255, 200, 220, 220))

    img = Image.alpha_composite(img, eyes)
    draw = ImageDraw.Draw(img, "RGBA")

    # Layer 8: Mechas de Cabelo Frontais (Franja & Caimento)
    hair_front = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    hf_draw = ImageDraw.Draw(hair_front, "RGBA")

    # Mechas frontais emoldurando o rosto pálido
    front_strands = [
        # Franja lateral esquerda
        [(cx - 130, cy - 180), (cx - 100, cy - 90), (cx - 125, cy + 40), (cx - 140, cy + 200)],
        [(cx - 110, cy - 170), (cx - 85, cy - 60), (cx - 95, cy + 80), (cx - 110, cy + 320)],
        # Franja lateral direita
        [(cx + 130, cy - 180), (cx + 100, cy - 90), (cx + 125, cy + 40), (cx + 140, cy + 200)],
        [(cx + 110, cy - 170), (cx + 85, cy - 60), (cx + 95, cy + 80), (cx + 110, cy + 320)],
        # Mechas finas no centro da testa
        [(cx - 30, cy - 175), (cx - 15, cy - 120), (cx - 25, cy - 70)],
        [(cx + 30, cy - 175), (cx + 15, cy - 120), (cx + 25, cy - 70)]
    ]

    for pts in front_strands:
        # Passada base preta
        hf_draw.line(pts, fill=(6, 6, 12, 255), width=10)
        # Reflexo azul/prateado frio
        hf_draw.line(pts, fill=(80, 110, 160, 140), width=3)

    img = Image.alpha_composite(img, hair_front)
    draw = ImageDraw.Draw(img, "RGBA")

    # Layer 9: Partículas de Luz e Vinheta Final
    vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette, "RGBA")

    # Partículas carmesim flutuantes (Embers)
    for _ in range(70):
        px = random.randint(0, width)
        py = random.randint(0, height)
        pr = random.randint(1, 4)
        p_alpha = random.randint(60, 220)
        v_draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(255, 20, 60, p_alpha))

    # Vinheta escura nas bordas para focar a atenção no rosto
    for r in range(int(width * 0.72), int(width * 0.45), -10):
        v_alpha = int(180 * (1 - r / (width * 0.72)))
        v_draw.rectangle([0, 0, width, height], outline=(0, 0, 0, v_alpha), width=20)

    img = Image.alpha_composite(img, vignette)

    return img.convert("RGB")

def main():
    print("\033[1;36m🎨 Renderizando Pintura Digital da Personagem Gótica Cyberpunk (1200x1200)...\033[0m")
    t0 = time.time()
    
    img = render_character(1200, 1200)
    
    # Salva na pasta de Downloads do Android
    out_dir = output_dir()
    if not out_dir.exists():
        out_dir = Path.home() / "BLACKCORE-Projects" / "black-paint-studio" / "gallery"
        out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / "personagem_goth_cyber.png"
    img.save(out_file, "PNG", quality=100)

    # Executa scanner de mídia do Android
    scan_media(out_file)
    
    duration = time.time() - t0
    print(f"\033[1;32m✅ Pintura concluída em {duration:.2f}s!\033[0m")
    print(f"\033[1;37m👉 Arquivo salvo: {out_file}\033[0m\n")

    # Importa módulo de visão para exibir prévia TrueColor no terminal
    try:
        sys.path.insert(0, str(Path.home() / ".blackcore" / "modules" / "black_numbers"))
        from bn_vision import scan_pixels, render_terminal_ansi
        scan_data = scan_pixels(out_file, width=42, height=22)
        render_terminal_ansi(scan_data, colored=True)
    except Exception as e:
        print(f"Prévia no terminal: {e}")

if __name__ == "__main__":
    main()
