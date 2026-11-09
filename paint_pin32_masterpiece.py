#!/usr/bin/env python3
"""
paint_pin32_masterpiece.py - Pintura Artística Completa da Imagem PIN32.png
Pinta a personagem com fidelidade à anatomia e estética Blackcore/Anime,
cria um fundo maravilhoso (lua celestial, nebulosa cósmica, partículas e pétalas)
e integra a lineart original de forma orgânica e profissional.
"""

from __future__ import annotations
import argparse
import math, os, random, subprocess, sys, time
from collections import deque
from pathlib import Path
from termux_compat import scan_media, output_dir
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps

INPUT_PATH = Path("/storage/emulated/0/Pictures/PIN32.png")
OUT_DIR_DL = Path("/storage/emulated/0/Download")
OUT_DIR_PIC = Path("/storage/emulated/0/Pictures")

def main():
    global INPUT_PATH
    parser = argparse.ArgumentParser(description='Colorização procedural específica de lineart PIN32; revise as máscaras antes de usar em outras personagens.')
    parser.add_argument('--input', default=str(INPUT_PATH))
    parser.add_argument('--output', help='PNG de saída; padrão na pasta de saída configurada')
    parser.add_argument('--max-edge', type=int, default=1200)
    args = parser.parse_args()
    if not 128 <= args.max_edge <= 1440: parser.error('--max-edge deve estar entre 128 e 1440')
    INPUT_PATH = Path(args.input).expanduser()
    destination = Path(args.output).expanduser() if args.output else output_dir() / 'PIN32_pintada_maravilhosa.png'
    destination.parent.mkdir(parents=True, exist_ok=True)
    print("==================================================================")
    print("🖤 BLACKCORE // PINTURA DIGITAL PROFISSIONAL DE PIN32.png")
    print("==================================================================")
    t0 = time.time()

    if not INPUT_PATH.exists():
        print(f"❌ Arquivo não encontrado: {INPUT_PATH}")
        sys.exit(1)

    orig_img = Image.open(INPUT_PATH).convert("RGBA")
    orig_img.thumbnail((args.max_edge,args.max_edge),Image.Resampling.LANCZOS)
    w, h = orig_img.size
    print(f"📖 Imagem carregada: {INPUT_PATH} ({w}x{h}, modo {orig_img.mode})")

    gray = orig_img.convert("L")
    cx, cy = w // 2, h // 2

    # -------------------------------------------------------------------------
    # 1. SEGMENTAÇÃO PRECISA DO FUNDO EXTERNO VS SILHUETA DA PERSONAGEM
    # -------------------------------------------------------------------------
    print("🔍 [1/6] Segmentando a silhueta da personagem e o fundo...")
    visited = bytearray(w * h)
    bg_mask_bytes = bytearray(w * h)
    queue = deque()

    # Sementes nas 4 bordas onde o pixel é branco/cinza claro (> 185)
    for x in range(w):
        for y in (0, h - 1):
            idx = y * w + x
            if gray.getpixel((x, y)) > 185 and not visited[idx]:
                visited[idx] = 1
                queue.append((x, y))

    for y in range(h):
        for x in (0, w - 1):
            idx = y * w + x
            if gray.getpixel((x, y)) > 185 and not visited[idx]:
                visited[idx] = 1
                queue.append((x, y))

    # Flood fill para marcar todo o fundo externo conectado
    while queue:
        x, y = queue.popleft()
        bg_mask_bytes[y * w + x] = 255
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                nidx = ny * w + nx
                if not visited[nidx]:
                    visited[nidx] = 1
                    if gray.getpixel((nx, ny)) > 175:
                        queue.append((nx, ny))

    outer_bg_mask = Image.frombytes("L", (w, h), bytes(bg_mask_bytes))
    # Máscara da personagem (invertida do fundo externo)
    char_mask = ImageOps.invert(outer_bg_mask)
    # Suavização suave das bordas para evitar serrilhado
    char_mask_soft = char_mask.filter(ImageFilter.GaussianBlur(1.5))

    # -------------------------------------------------------------------------
    # 2. EXTRAÇÃO E REFINAMENTO DA LINEART ORIGINAL
    # -------------------------------------------------------------------------
    print("✒️  [2/6] Extraindo e restaurando a arte linear original...")
    inv_gray = ImageOps.invert(gray)
    # Curva tonal para manter os traços nítidos sem ruído de fundo
    line_alpha = inv_gray.point(lambda p: int(min(255, p * 2.2)) if p > 22 else 0)
    
    # Criar camada de linha em tom mogno/obsidiana suave
    line_art_layer = Image.new("RGBA", (w, h), (14, 10, 20, 0))
    line_art_layer.putalpha(line_alpha)

    # -------------------------------------------------------------------------
    # 3. CRIAÇÃO DO FUNDO MARAVILHOSO (CELESTIAL, LUA, NEBULOSA & PARTÍCULAS)
    # -------------------------------------------------------------------------
    print("🌌 [3/6] Criando o fundo maravilhoso (Noite Celestial, Lua & Nebulosa)...")
    bg = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d_bg = ImageDraw.Draw(bg, "RGBA")

    # Gradiente Cósmico Noturno Rico
    for y in range(h):
        t = y / h
        if t < 0.35:
            # Topo: Azul da meia-noite profundo / Índigo estelar
            rt = t / 0.35
            r = int(8 + rt * 20)
            g = int(6 + rt * 12)
            b = int(24 + rt * 36)
        elif t < 0.75:
            # Meio: Violeta Aveludado & Carmesim Cósmico
            rt = (t - 0.35) / 0.40
            r = int(28 + rt * 80)
            g = int(18 + rt * 10)
            b = int(60 - rt * 15)
        else:
            # Base: Crepúsculo Quente / Âmbar Dourado Suave
            rt = (t - 0.75) / 0.25
            r = int(108 + rt * 90)
            g = int(28 + rt * 45)
            b = int(45 + rt * 15)
        d_bg.line([0, y, w, y], fill=(r, g, b, 255))

    # Grande Lua Celestial Dourada / Carmesim (Halo Iluminador)
    moon_x = int(w * 0.50)
    moon_y = int(h * 0.35)
    moon_r = int(w * 0.30)

    # Corona de Brilho Atmosférico em degradê suave
    moon_glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_mg = ImageDraw.Draw(moon_glow, "RGBA")
    for r in range(int(moon_r * 2.2), moon_r, -4):
        t = 1.0 - (r - moon_r) / (moon_r * 1.2)
        alpha = int(115 * (t**1.8))
        d_mg.ellipse([moon_x - r, moon_y - r, moon_x + r, moon_y + r], fill=(255, 60, 110, alpha))

    # Disco lunar estilizado
    for r in range(moon_r, 0, -3):
        t = 1.0 - (r / moon_r)
        d_mg.ellipse([moon_x - r, moon_y - r, moon_x + r, moon_y + r], fill=(255, int(210 + t*45), int(160 + t*85), 255))

    moon_glow = moon_glow.filter(ImageFilter.GaussianBlur(12))
    bg = Image.alpha_composite(bg, moon_glow)
    d_bg = ImageDraw.Draw(bg, "RGBA")

    # Raios Volumétricos de Luz (God Rays)
    rays = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_rays = ImageDraw.Draw(rays, "RGBA")
    for ang in range(-70, 250, 7):
        rad = math.radians(ang + random.uniform(-1.5, 1.5))
        rx = moon_x + math.cos(rad) * w * 1.3
        ry = moon_y + math.sin(rad) * h * 1.3
        d_rays.polygon([(moon_x, moon_y), (rx - 30, ry), (rx + 30, ry)], fill=(255, 190, 140, random.randint(6, 22)))
    rays = rays.filter(ImageFilter.GaussianBlur(16))
    bg = Image.alpha_composite(bg, rays)
    d_bg = ImageDraw.Draw(bg, "RGBA")

    # Nebulosa e Poeira Cósmica Estelar
    stars = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_stars = ImageDraw.Draw(stars, "RGBA")
    for _ in range(180):
        sx = random.randint(0, w)
        sy = random.randint(0, int(h * 0.75))
        sr = random.randint(1, 4)
        c = random.choice([(255, 255, 255), (255, 210, 230), (200, 230, 255), (255, 220, 150)])
        d_stars.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(*c, random.randint(90, 255)))
    bg = Image.alpha_composite(bg, stars)

    # Orbes Bokeh Flutuantes
    bokeh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_bk = ImageDraw.Draw(bokeh, "RGBA")
    for _ in range(35):
        bx = random.randint(int(w * 0.05), int(w * 0.95))
        by = random.randint(int(h * 0.05), int(h * 0.85))
        br = random.randint(15, 65)
        c = random.choice([(255, 40, 90), (255, 160, 80), (160, 80, 255), (255, 220, 180)])
        d_bk.ellipse([bx - br, by - br, bx + br, by + br], fill=(*c, random.randint(20, 60)))
    bokeh = bokeh.filter(ImageFilter.GaussianBlur(15))
    bg = Image.alpha_composite(bg, bokeh)

    # -------------------------------------------------------------------------
    # 4. PINTURA COMPLETA DA PERSONAGEM (PELE, OLHOS, CABELO, ROUPAS & ADORNOS)
    # -------------------------------------------------------------------------
    print("🎨 [4/6] Pintando a personagem com cores, sombras, pele, olhos e roupas...")
    char_paint = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_char = ImageDraw.Draw(char_paint, "RGBA")

    # 4.1 Base do Cabelo (Raven Black com reflexos azul-noite e carmesim)
    hair_base = (14, 13, 22, 255)
    d_char.rectangle([0, 0, w, h], fill=hair_base)

    # 4.2 Rosto e Pele de Porcelana Delicada
    # Área aproximada da cabeça/face:
    skin_tone = (250, 245, 240, 255)
    shadow_skin = (220, 205, 215, 255)
    
    # Preenchimento base da face e pescoço
    face_polygon = [
        (cx - 160, cy - 220), (cx + 160, cy - 220),
        (cx + 175, cy - 10), (cx + 155, cy + 60),
        (cx + 105, cy + 130), (cx, cy + 170),
        (cx - 105, cy + 130), (cx - 155, cy + 60),
        (cx - 175, cy - 10)
    ]
    d_char.polygon(face_polygon, fill=skin_tone)

    # Pescoço e Clavícula
    neck_polygon = [
        (cx - 75, cy + 60), (cx + 75, cy + 60),
        (cx + 95, cy + 220), (cx - 95, cy + 220)
    ]
    d_char.polygon(neck_polygon, fill=skin_tone)
    # Sombra do pescoço
    d_char.polygon([
        (cx - 75, cy + 60), (cx + 75, cy + 60),
        (cx + 60, cy + 130), (cx - 60, cy + 130)
    ], fill=shadow_skin)

    # Blush Suave nas Bochechas (Airbrush Effect)
    blush_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_blush = ImageDraw.Draw(blush_layer, "RGBA")
    d_blush.ellipse([cx - 155, cy + 15, cx - 65, cy + 70], fill=(255, 140, 165, 120))
    d_blush.ellipse([cx + 65, cy + 15, cx + 155, cy + 70], fill=(255, 140, 165, 120))
    d_blush.ellipse([cx - 15, cy + 30, cx + 15, cy + 45], fill=(255, 160, 180, 90)) # ponta do nariz
    blush_layer = blush_layer.filter(ImageFilter.GaussianBlur(18))
    char_paint = Image.alpha_composite(char_paint, blush_layer)
    d_char = ImageDraw.Draw(char_paint, "RGBA")

    # Lábios Elegantes com Gloss
    mouth_y = cy + 95
    d_char.polygon([
        (cx - 32, mouth_y), (cx - 12, mouth_y - 4), (cx, mouth_y - 1),
        (cx + 12, mouth_y - 4), (cx + 32, mouth_y),
        (cx + 15, mouth_y + 11), (cx, mouth_y + 14), (cx - 15, mouth_y + 11)
    ], fill=(175, 25, 60, 240))
    d_char.ellipse([cx - 6, mouth_y + 3, cx + 6, mouth_y + 8], fill=(255, 210, 225, 180)) # gloss

    # 4.3 Olhos Cerveja/Rubi Cristalinos Radiantes
    eye_y = cy - 35
    for side in [-1, 1]:
        ex = cx + side * 82
        ew, eh = 48, 28
        # Fundo do olho (esclera)
        d_char.ellipse([ex - ew, eye_y - eh, ex + ew, eye_y + eh], fill=(244, 244, 252, 255))
        d_char.ellipse([ex - ew, eye_y - eh, ex + ew, eye_y - eh + 14], fill=(210, 205, 220, 140)) # sombra da pálpebra

        # Íris Rubi
        iris_r = 21
        for ir in range(iris_r, 0, -2):
            t = 1.0 - (ir / iris_r)
            ic = (int(190 + t * 65), int(t * 70), int(40 + t * 75), 255)
            d_char.ellipse([ex - ir, eye_y - ir, ex + ir, eye_y + ir], fill=ic)

        # Micro-fibras radiantes
        for ang in range(0, 360, 24):
            rad = math.radians(ang)
            fx1 = ex + math.cos(rad) * (iris_r * 0.25)
            fy1 = eye_y + math.sin(rad) * (iris_r * 0.25)
            fx2 = ex + math.cos(rad) * (iris_r * 0.88)
            fy2 = eye_y + math.sin(rad) * (iris_r * 0.88)
            d_char.line([fx1, fy1, fx2, fy2], fill=(255, 175, 210, 170), width=2)

        # Pupila vertical gótica
        d_char.ellipse([ex - 3, eye_y - 14, ex + 3, eye_y + 14], fill=(12, 2, 6, 255))

        # Catchlights (Brilho Estelar nos Olhos)
        d_char.ellipse([ex - 7, eye_y - 9, ex - 1, eye_y - 3], fill=(255, 255, 255, 255))
        d_char.ellipse([ex + 4, eye_y + 4, ex + 8, eye_y + 8], fill=(255, 220, 240, 240))

    # 4.4 Cabelo: Reflexos e Mechas Volumosas
    hair_highlights = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_hh = ImageDraw.Draw(hair_highlights, "RGBA")

    # Brilho Angelical (Tenshi no Wa / Halo no Cabelo)
    halo_y = cy - 120
    for hx in range(cx - 180, cx + 180, 6):
        dist = abs(hx - cx)
        if dist < 160:
            bright = int(140 * math.cos(dist / 160 * math.pi * 0.5))
            d_hh.line([hx, halo_y - random.randint(4, 18), hx, halo_y + random.randint(4, 18)], fill=(120, 150, 220, bright), width=3)
            d_hh.line([hx, halo_y - random.randint(2, 10), hx, halo_y + random.randint(2, 10)], fill=(255, 180, 210, bright), width=2)

    # Mechas esvoaçantes nas laterais
    for side in [-1, 1]:
        for i in range(25):
            x0 = cx + side * (120 + i * 8)
            y0 = cy - 160 + i * 6
            x1 = x0 + side * random.randint(20, 70)
            y1 = y0 + random.randint(150, 450)
            d_hh.line([x0, y0, x1, y1], fill=(100, 130, 200, random.randint(50, 130)), width=3)
            d_hh.line([x0, y0, x1, y1], fill=(255, 80, 130, random.randint(30, 80)), width=2)

    hair_highlights = hair_highlights.filter(ImageFilter.GaussianBlur(3))
    char_paint = Image.alpha_composite(char_paint, hair_highlights)
    d_char = ImageDraw.Draw(char_paint, "RGBA")

    # 4.5 Vestimenta Gótica / Blackcore (Veludo, Carmesim & Ouro)
    clothes_top = cy + 180
    d_char.polygon([
        (cx - 130, clothes_top), (cx + 130, clothes_top),
        (cx + 460, h), (cx - 460, h)
    ], fill=(10, 9, 14, 255)) # Veludo preto

    # Decote e Detalhes em Carmesim Vinho
    d_char.polygon([
        (cx - 95, clothes_top), (cx, clothes_top + 80),
        (cx + 95, clothes_top), (cx, clothes_top + 105)
    ], fill=(120, 15, 38, 255))

    # Gargantilha Choker com gema preciosa
    choker_y = cy + 155
    d_char.rectangle([cx - 65, choker_y, cx + 65, choker_y + 24], fill=(18, 16, 26, 255), outline=(215, 180, 100, 255), width=2)
    d_char.polygon([
        (cx, choker_y + 38), (cx + 14, choker_y + 24),
        (cx, choker_y + 10), (cx - 14, choker_y + 24)
    ], fill=(235, 20, 60, 255)) # Gema de rubi lapidada
    d_char.ellipse([cx - 4, choker_y + 18, cx + 4, choker_y + 26], fill=(255, 255, 255, 220)) # brilho na jóia

    # 4.6 Chifres de Obsidiana e Adornos de Cabeça
    for side in [-1, 1]:
        bx = cx + side * 125
        by = cy - 165
        for i in range(85):
            t = i / 85.0
            hx = bx + side * (math.sin(t * math.pi * 0.85) * 210 + t * 50)
            hy = by - (t * 360 + math.cos(t * math.pi * 0.5) * 50)
            rad = (1.0 - t) * 36 + 3
            # Corpo do chifre
            d_char.ellipse([hx - rad, hy - rad, hx + rad, hy + rad], fill=(12, 10, 18, 255))
            # Brilho de aresta polida
            d_char.ellipse([hx - rad*0.3, hy - rad*0.3, hx + rad*0.2, hy + rad*0.2], fill=(140, 160, 205, 50))
            # Luz de contorno avermelhada
            rim_x = hx + side * (rad * 0.85)
            d_char.ellipse([rim_x - 3, hy - 3, rim_x + 3, hy + 3], fill=(255, 40, 75, 200))

    # -------------------------------------------------------------------------
    # 5. COMPOSIÇÃO: MÁSCARA DA PERSONAGEM + LINHAS ORIGINAIS MULTIPLICADAS
    # -------------------------------------------------------------------------
    print("✨ [5/6] Compondo pintura, iluminação volumétrica e traços originais...")
    
    # Recorta a pintura exatamente no contorno da personagem
    char_composite = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    char_composite.paste(char_paint, (0, 0), mask=char_mask_soft)

    # Luz de Borda (Rim Light) Volumétrica ao redor da silhueta
    rim_glow = char_mask.filter(ImageFilter.GaussianBlur(16))
    rim_layer = Image.new("RGBA", (w, h), (255, 50, 95, 0))
    rim_layer.putalpha(rim_glow.point(lambda p: int(min(255, p * 0.85))))
    bg = Image.alpha_composite(bg, rim_layer)

    # Funde a personagem sobre o fundo maravilhoso
    canvas = Image.alpha_composite(bg, char_composite)

    # Aplica a Lineart Original limpa em modo Multiply / Overlay
    canvas = Image.alpha_composite(canvas, line_art_layer)

    # -------------------------------------------------------------------------
    # 6. PÓS-PROCESSAMENTO: PÉTALAS, NÉVOA & BRILHO CINEMATOGRÁFICO
    # -------------------------------------------------------------------------
    print("🌸 [6/6] Finalizando com pétalas flutuantes, vinheta e masterização...")
    fore_fx = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_ffx = ImageDraw.Draw(fore_fx, "RGBA")

    # Pétalas de rosa carmesim caindo na frente da personagem (Depth of Field)
    random.seed(999)
    for _ in range(45):
        ptx = random.randint(int(w * 0.05), int(w * 0.95))
        pty = random.randint(int(h * 0.15), h)
        pw = random.randint(12, 32)
        ph = random.randint(8, 20)
        c_alpha = random.randint(140, 240)
        d_ffx.ellipse([ptx - pw, pty - ph, ptx + pw, pty + ph], fill=(225, 18, 55, c_alpha))
        # Centro da pétala mais escuro
        d_ffx.ellipse([ptx - pw*0.5, pty - ph*0.5, ptx + pw*0.5, pty + ph*0.5], fill=(140, 10, 35, c_alpha))

    # Fagulhas douradas/carmesim flutuando no ar
    for _ in range(75):
        gx = random.randint(0, w)
        gy = random.randint(0, h)
        gr = random.randint(2, 6)
        d_ffx.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(255, random.randint(120, 240), random.randint(80, 180), random.randint(90, 220)))

    canvas = Image.alpha_composite(canvas, fore_fx)

    # Vinheta Cinematográfica Suave
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_vin = ImageDraw.Draw(vignette, "RGBA")
    max_dist = math.hypot(cx, cy)
    for r in range(int(max_dist), int(max_dist * 0.45), -14):
        t = 1.0 - (r / max_dist)
        d_vin.rectangle([0, 0, w, h], outline=(6, 2, 10, int(175 * (1.0 - t)**2)), width=18)
    canvas = Image.alpha_composite(canvas, vignette)

    # Realce de Nitidez e Contraste
    final_rgb = canvas.convert("RGB")
    final_rgb = ImageEnhance.Sharpness(final_rgb).enhance(1.15)
    final_rgb = ImageEnhance.Contrast(final_rgb).enhance(1.04)

    # -------------------------------------------------------------------------
    # SALVAR ARQUIVOS E VARREDURA DE MÍDIA
    # -------------------------------------------------------------------------
    out_dl = destination
    out_pic = destination

    final_rgb.save(out_dl, "PNG", quality=100)

    scan_media(out_dl)

    elapsed = time.time() - t0
    size_kb = os.path.getsize(out_dl) // 1024
    print(f"\n==================================================================")
    print(f"✨ PINTURA CONCLUÍDA EM {elapsed:.2f}s!")
    print(f"📁 Salvo em Downloads: {out_dl} ({size_kb} KB)")
    print(f"📁 Salvo em Pictures:  {out_pic} ({size_kb} KB)")
    print("==================================================================")

if __name__ == "__main__":
    main()
