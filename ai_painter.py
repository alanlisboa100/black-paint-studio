#!/usr/bin/env python3
"""Geradores gráficos procedurais locais em Python/Pillow (não é um modelo de IA)."""

from __future__ import annotations
import argparse, json, math, os, random, subprocess, sys, time
from pathlib import Path
from termux_compat import scan_media, output_dir
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Cores Cyberpunk Padrão
PALETTES = {
    "cyberpunk": [(0, 255, 204), (255, 0, 127), (157, 0, 255), (0, 240, 255), (255, 255, 0)],
    "synthwave": [(255, 113, 206), (1, 205, 254), (5, 255, 161), (185, 103, 255), (255, 251, 150)],
    "matrix": [(0, 255, 100), (0, 200, 70), (0, 255, 204), (200, 255, 220), (0, 120, 40)],
    "darkcore": [(0, 255, 204), (255, 51, 0), (20, 20, 35), (240, 240, 250), (100, 100, 150)],
    "sunset": [(255, 75, 75), (255, 150, 50), (255, 220, 50), (120, 40, 140), (40, 10, 60)]
}

def get_output_dir() -> Path:
    """Retorna o diretório oficial de saída (Download do Android ou galeria local)."""
    android_download = Path("/storage/emulated/0/Download")
    if android_download.exists() and os.access(android_download, os.W_OK):
        return android_download
    local_gallery = Path.home() / "BLACKCORE-Projects" / "black-paint-studio" / "gallery"
    local_gallery.mkdir(parents=True, exist_ok=True)
    return local_gallery

def render_terminal_preview(img: Image.Image, width: int = 40, height: int = 20):
    """Renderiza uma prévia TrueColor da imagem direto no terminal do Termux."""
    resized = img.convert("RGB").resize((width, height), Image.Resampling.BILINEAR)
    print("\n\033[1;36m╔" + "═" * (width * 2) + "╗\033[0m")
    print(f"\033[1;36m║ \033[1;37mPRÉVIA DA IMAGEM GERADA ({img.width}x{img.height})\033[1;36m" + " " * (width * 2 - 32) + "║\033[0m")
    print("\033[1;36m╠" + "═" * (width * 2) + "╣\033[0m")
    
    for y in range(height):
        sys.stdout.write("\033[1;36m║\033[0m")
        for x in range(width):
            r, g, b = resized.getpixel((x, y))
            sys.stdout.write(f"\033[48;2;{r};{g};{b}m  \033[0m")
        sys.stdout.write("\033[1;36m║\033[0m\n")
    print("\033[1;36m╚" + "═" * (width * 2) + "╝\033[0m\n")

def draw_neon_glow_line(draw: ImageDraw.ImageDraw, base_img: Image.Image, x0, y0, x1, y1, color, width=4, glow_layers=4):
    """Desenha uma linha com efeito de iluminação neon multicamada."""
    r, g, b = color[:3]
    # Camadas de brilho difuso
    for i in range(glow_layers, 0, -1):
        alpha = int(60 / (i * 1.2))
        draw.line([x0, y0, x1, y1], fill=(r, g, b, alpha), width=width + i * 4)
    # Filamento central brilhante
    draw.line([x0, y0, x1, y1], fill=(255, 255, 255, 255), width=max(1, int(width * 0.4)))

def draw_neon_circle(draw: ImageDraw.ImageDraw, cx, cy, radius, color, width=4, glow_layers=4):
    """Desenha um círculo com anéis de luz neon."""
    r, g, b = color[:3]
    for i in range(glow_layers, 0, -1):
        alpha = int(70 / (i * 1.2))
        draw.ellipse([cx - radius - i*2, cy - radius - i*2, cx + radius + i*2, cy + radius + i*2], 
                     outline=(r, g, b, alpha), width=width + i*3)
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], 
                 outline=(255, 255, 255, 255), width=max(1, int(width * 0.4)))

# ============================================================
# GERADORES DE ESTILOS DE IMAGEM
# ============================================================

def generate_cyberpunk_city(w=1024, h=1024, palette_name="cyberpunk") -> Image.Image:
    """Gera uma pintura de cidade cyberpunk com horizonte synthwave e sol neon."""
    img = Image.new("RGBA", (w, h), (4, 4, 10, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    palette = PALETTES.get(palette_name, PALETTES["cyberpunk"])
    
    # 1. Gradiente de céu profundo
    for y in range(int(h * 0.75)):
        ratio = y / (h * 0.75)
        r = int(5 + ratio * 25)
        g = int(4 + ratio * 5)
        b = int(12 + ratio * 45)
        draw.line([0, y, w, y], fill=(r, g, b, 255))

    # 2. Sol Synthwave
    horizon = int(h * 0.72)
    sun_radius = int(w * 0.22)
    sun_cx = int(w * 0.5)
    sun_cy = horizon - int(sun_radius * 0.6)
    
    for r_cur in range(sun_radius, 0, -1):
        t = 1 - (r_cur / sun_radius)
        c_r = int(255)
        c_g = int(255 * (1 - t * 0.8))
        c_b = int(120 * t)
        draw.ellipse([sun_cx - r_cur, sun_cy - r_cur, sun_cx + r_cur, sun_cy + r_cur], fill=(c_r, c_g, c_b, 255))

    # Cortes horizontais no sol (estilo anos 80)
    for cut_y in range(sun_cy - int(sun_radius*0.2), horizon, 14):
        cut_h = max(2, int(3 + max(0, cut_y - sun_cy) * 0.15))
        draw.rectangle([sun_cx - sun_radius, cut_y, sun_cx + sun_radius, cut_y + cut_h], fill=(12, 6, 28, 255))

    # 3. Grade de perspectiva no chão (Synthwave Grid)
    for x in range(-w, w * 2, 45):
        draw.line([sun_cx + (x - sun_cx) * 0.1, horizon, x, h], fill=(255, 0, 127, 80), width=2)
    
    for y in range(horizon, h, 20):
        alpha = int(120 * ((y - horizon) / (h - horizon)))
        draw.line([0, y, w, y], fill=(0, 255, 204, alpha), width=2)

    # 4. Prédios / Skyline Futurista
    cur_x = 0
    while cur_x < w:
        b_w = random.randint(40, 90)
        b_h = random.randint(int(h * 0.2), int(h * 0.55))
        b_y = horizon - b_h
        
        # Sombra do prédio
        draw.rectangle([cur_x, b_y, cur_x + b_w, horizon + 20], fill=(6, 7, 18, 255), outline=(15, 15, 35, 255))
        
        # Borda neon no topo
        neon_c = random.choice(palette)
        draw.line([cur_x, b_y, cur_x + b_w, b_y], fill=(*neon_c, 255), width=3)
        
        # Antena ou pináculo
        if random.random() > 0.5:
            ant_h = random.randint(20, 60)
            draw.line([cur_x + b_w//2, b_y - ant_h, cur_x + b_w//2, b_y], fill=(*neon_c, 200), width=2)
            draw.ellipse([cur_x + b_w//2 - 3, b_y - ant_h - 3, cur_x + b_w//2 + 3, b_y - ant_h + 3], fill=(255, 255, 255, 255))
        
        # Janelas acesas
        for wy in range(b_y + 12, horizon - 10, 16):
            for wx in range(cur_x + 6, cur_x + b_w - 6, 12):
                if random.random() > 0.4:
                    win_c = random.choice([(0, 255, 204), (255, 255, 0), (255, 0, 127)])
                    draw.rectangle([wx, wy, wx + 4, wy + 7], fill=(*win_c, 220))
        cur_x += b_w + random.randint(2, 8)

    return img

def generate_neon_logo(text: str = "BLACKCORE", subtitle: str = "AUTONOMOUS AGENT", w=1024, h=1024) -> Image.Image:
    """Gera um logotipo e emblema futurista com anéis neon e tipografia geométrica."""
    img = Image.new("RGBA", (w, h), (5, 5, 12, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    cx, cy = w // 2, h // 2
    
    # 1. Grade de fundo sutil
    for x in range(0, w, 40):
        draw.line([x, 0, x, h], fill=(20, 20, 40, 40), width=1)
    for y in range(0, h, 40):
        draw.line([0, y, w, y], fill=(20, 20, 40, 40), width=1)

    # 2. Anéis e Escudo Neon
    draw_neon_circle(draw, cx, cy, int(w * 0.38), (0, 255, 204), width=4, glow_layers=5)
    draw_neon_circle(draw, cx, cy, int(w * 0.35), (255, 0, 127), width=3, glow_layers=4)
    
    # Hexágono Central
    hex_radius = int(w * 0.28)
    points = []
    for i in range(6):
        ang = math.pi / 3 * i - math.pi / 6
        points.append((cx + hex_radius * math.cos(ang), cy + hex_radius * math.sin(ang)))
    
    for i in range(6):
        p1 = points[i]
        p2 = points[(i + 1) % 6]
        draw_neon_glow_line(draw, img, p1[0], p1[1], p2[0], p2[1], (157, 0, 255), width=3, glow_layers=4)

    # 3. Desenho de Ícone Central (Símbolo Cyber / Chip)
    chip_s = int(w * 0.12)
    draw.rectangle([cx - chip_s, cy - chip_s, cx + chip_s, cy + chip_s], 
                   fill=(10, 12, 28, 240), outline=(0, 255, 204, 255), width=3)
    
    # Circuitos do chip
    for off in [-chip_s + 15, 0, chip_s - 15]:
        draw.line([cx + off, cy - chip_s, cx + off, cy - chip_s - 30], fill=(0, 255, 204, 255), width=2)
        draw.line([cx + off, cy + chip_s, cx + off, cy + chip_s + 30], fill=(0, 255, 204, 255), width=2)
        draw.line([cx - chip_s, cy + off, cx - chip_s - 30, cy + off], fill=(255, 0, 127, 255), width=2)
        draw.line([cx + chip_s, cy + off, cx + chip_s + 30, cy + off], fill=(255, 0, 127, 255), width=2)

    # 4. Texto Estilizado
    try:
        # Tenta carregar fonte padrão ou desenha em blocos
        font_main = ImageFont.load_default()
    except Exception:
        font_main = None

    # Desenha texto com efeito de banner
    banner_w, banner_h = int(w * 0.7), 60
    draw.rectangle([cx - banner_w//2, cy + int(h * 0.28), cx + banner_w//2, cy + int(h * 0.28) + banner_h], 
                   fill=(0, 0, 0, 220), outline=(0, 255, 204, 255), width=2)
    
    draw.text((cx, cy + int(h * 0.28) + 20), text, fill=(0, 255, 204, 255), anchor="mm")
    draw.text((cx, cy + int(h * 0.28) + 45), subtitle, fill=(255, 0, 127, 255), anchor="mm")

    return img

def generate_neural_cosmos(w=1024, h=1024) -> Image.Image:
    """Gera uma rede neural cósmica com constelações, sinapses e esferas de energia."""
    img = Image.new("RGBA", (w, h), (3, 3, 8, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    
    # 1. Fundo com poeira estelar
    for _ in range(350):
        sx, sy = random.randint(0, w), random.randint(0, h)
        s_alpha = random.randint(50, 255)
        s_size = random.choice([1, 1, 1, 2, 3])
        s_color = random.choice([(255, 255, 255), (0, 255, 204), (255, 0, 127), (0, 240, 255)])
        draw.ellipse([sx, sy, sx + s_size, sy + s_size], fill=(*s_color, s_alpha))

    # 2. Nós da Rede Neural
    node_count = 45
    nodes = []
    for _ in range(node_count):
        nodes.append({
            "x": random.randint(int(w * 0.1), int(w * 0.9)),
            "y": random.randint(int(h * 0.1), int(h * 0.9)),
            "rad": random.randint(6, 18),
            "color": random.choice([(0, 255, 204), (255, 0, 127), (157, 0, 255), (0, 240, 255), (255, 255, 0)])
        })

    # 3. Conexões Sinápticas
    for i in range(node_count):
        for j in range(i + 1, node_count):
            dist = math.hypot(nodes[i]["x"] - nodes[j]["x"], nodes[i]["y"] - nodes[j]["y"])
            if dist < w * 0.25:
                alpha = int(220 * (1 - dist / (w * 0.25)))
                c = nodes[i]["color"]
                draw.line([nodes[i]["x"], nodes[i]["y"], nodes[j]["x"], nodes[j]["y"]], fill=(*c, alpha), width=2)

    # 4. Desenha os nós brilhantes
    for n in nodes:
        draw_neon_circle(draw, n["x"], n["y"], n["rad"], n["color"], width=3, glow_layers=4)
        draw.ellipse([n["x"] - n["rad"]//2, n["y"] - n["rad"]//2, n["x"] + n["rad"]//2, n["y"] + n["rad"]//2], 
                     fill=(255, 255, 255, 255))

    return img

def generate_pixel_art(matrix_data: list, pixel_scale: int = 24) -> Image.Image:
    """Gera pixel art de alta definição a partir de uma matriz numérica ou de cores."""
    h = len(matrix_data)
    w = len(matrix_data[0]) if h > 0 else 0
    img = Image.new("RGBA", (w * pixel_scale, h * pixel_scale), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    
    for y in range(h):
        for x in range(w):
            val = matrix_data[y][x]
            if isinstance(val, (list, tuple)) and len(val) >= 3:
                color = tuple(val[:4])
            elif isinstance(val, str) and val.startswith('#'):
                r = int(val[1:3], 16)
                g = int(val[3:5], 16)
                b = int(val[5:7], 16)
                color = (r, g, b, 255)
            elif isinstance(val, (int, float)):
                # Mapeia 0-255 ou 0-1 para tom neon
                v = int(val * 255) if isinstance(val, float) else int(val)
                color = (0, v, int(v * 0.8), 255)
            else:
                color = (0, 0, 0, 0)
                
            px = x * pixel_scale
            py = y * pixel_scale
            draw.rectangle([px, py, px + pixel_scale - 1, py + pixel_scale - 1], fill=color)
            
    return img

# ============================================================
# SALVAR E SINCRONIZAR NO ANDROID
# ============================================================

def save_and_publish_image(img: Image.Image, filename: str = None) -> str:
    """Salva a imagem no armazenamento do telefone e dispara o scanner de mídia."""
    out_dir = get_output_dir()
    if not filename:
        filename = f"black_ai_paint_{int(time.time())}.png"
    if not filename.lower().endswith(".png"):
        filename += ".png"
        
    out_path = out_dir / filename
    img.save(out_path, "PNG")
    
    # Notifica o Android para aparecer imediatamente na Galeria e WhatsApp
    try:
        scan_media(out_path)
    except Exception:
        pass
        
    return str(out_path)

# ============================================================
# CLI PRINCIPAL
# ============================================================

def main():
    parser = argparse.ArgumentParser(prog="ai_painter", description="Geradores procedurais locais do Black Paint Studio (sem modelo de IA)")
    parser.add_argument("--type", "-t", choices=["city", "logo", "neural"], default="city", help="Tipo de arte procedural")
    parser.add_argument("--text", default="BLACKCORE", help="Texto principal (para logos/banners)")
    parser.add_argument("--subtext", default="CÉREBRO 2.0", help="Subtexto")
    parser.add_argument("--palette", default="cyberpunk", choices=list(PALETTES.keys()), help="Paleta de cores")
    parser.add_argument("--width", "-W", type=int, default=1024, help="Largura da imagem")
    parser.add_argument("--height", "-H", type=int, default=1024, help="Altura da imagem")
    parser.add_argument("--output", "-o", help="Nome do arquivo de saída")
    parser.add_argument("--no-preview", action="store_true", help="Não exibir prévia no terminal")
    parser.add_argument("--seed", type=int, default=2026, help="Semente para repetir a composição")
    
    args = parser.parse_args()
    if not (64 <= args.width <= 2048 and 64 <= args.height <= 2048):
        parser.error("largura e altura devem ficar entre 64 e 2048 pixels")
    random.seed(args.seed)
    print(f"\033[1;36m🎨 BLACK PAINT // Gerador procedural CPU ({args.type.upper()})...\033[0m")
    
    if args.type == "city":
        img = generate_cyberpunk_city(args.width, args.height, args.palette)
    elif args.type == "logo":
        img = generate_neon_logo(args.text, args.subtext, args.width, args.height)
    elif args.type == "neural":
        img = generate_neural_cosmos(args.width, args.height)
    else:
        img = generate_cyberpunk_city(args.width, args.height, args.palette)
        
    # Renderiza prévia TrueColor no terminal
    if not args.no_preview:
        render_terminal_preview(img, width=38, height=18)
        
    # Salva imagem e notifica Android
    final_path = save_and_publish_image(img, args.output)
    print(f"\033[1;32m✅ Imagem gerada e salva com sucesso no celular:\033[0m")
    print(f"\033[1;37m👉 {final_path}\033[0m\n")

if __name__ == "__main__":
    main()
