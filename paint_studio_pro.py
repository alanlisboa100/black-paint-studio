#!/usr/bin/env python3
"""
paint_studio_pro.py - Motor Gráfico v0.4 (BLACKCORE / paint-IA-Studio-Pro)
Suporte Oficial aos 5 Presets do Documento de Referência v0.4:
  - A: Soft Sketch Base
  - B: Paint Retro Interface (com moldura/UI de Paint dos anos 90)
  - C: Soft Render Delicado
  - D: Gothic Pastel Fusion
  - E: Production Polish Light
"""

from __future__ import annotations
import argparse, json, math, os, random, subprocess, sys, time
from pathlib import Path
from termux_compat import scan_media, output_dir
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parent

def load_presets() -> dict:
    preset_file = ROOT / "presets.json"
    if preset_file.exists():
        with open(preset_file, "r", encoding="utf-8") as f:
            return json.load(f).get("presets", {})
    return {}

PRESETS = load_presets()

class ProStudioEngineV04:
    def __init__(self, target_w=1200, target_h=1200, preset_key="gothic_pastel_fusion", ssaa=2, seed=42):
        self.target_w = target_w
        self.target_h = target_h
        self.ssaa = ssaa
        self.w = target_w * ssaa
        self.h = target_h * ssaa
        self.cx = self.w // 2
        self.cy = self.h // 2
        self.seed = seed
        random.seed(seed)
        
        # Mapeia preset
        self.preset_cfg = PRESETS.get(preset_key, PRESETS.get("gothic_pastel_fusion", {}))
        self.preset_name = self.preset_cfg.get("preset_name", preset_key)
        self.ui_frame = self.preset_cfg.get("ui_frame", False)

    def create_layer(self) -> tuple[Image.Image, ImageDraw.ImageDraw]:
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        return img, ImageDraw.Draw(img, "RGBA")

    def draw_hand_drawn_stroke(self, draw: ImageDraw.ImageDraw, p0, p1, p2, p3, color, base_w=3, jitter_amount=0.8, steps=45):
        """Simula a imperfeição e leveza do traço desenhado à mão (microjitter e variação de pressão)."""
        points = []
        for i in range(steps + 1):
            t = i / steps
            inv_t = 1 - t
            # Ponto ideal da curva
            x = (inv_t**3 * p0[0] + 3 * inv_t**2 * t * p1[0] + 3 * inv_t * t**2 * p2[0] + t**3 * p3[0])
            y = (inv_t**3 * p0[1] + 3 * inv_t**2 * t * p1[1] + 3 * inv_t * t**2 * p2[1] + t**3 * p3[1])
            
            # Microtremor / jitter humano
            jx = (random.random() - 0.5) * jitter_amount * self.ssaa
            jy = (random.random() - 0.5) * jitter_amount * self.ssaa
            points.append((x + jx, y + jy))
        
        for i in range(len(points) - 1):
            t = i / steps
            # Variação de pressão (fina nas pontas, encorpada no meio)
            press = math.sin(t * math.pi) * 0.75 + 0.5
            w = max(1, int(base_w * press))
            
            # Interrupções bonitas ocasionais (traço solto)
            if random.random() < 0.02 and i > 5 and i < steps - 5:
                continue
                
            draw.line([points[i], points[i+1]], fill=color, width=w)

    def draw_paint_retro_frame(self, art_img: Image.Image) -> Image.Image:
        """Versão B: Renderiza a arte dentro de uma moldura de Paint Retrô anos 90 completa."""
        w, h = self.w, self.h
        
        # Canvas estendido para a moldura da UI
        frame_img = Image.new("RGBA", (w, h), (192, 192, 192, 255))
        draw = ImageDraw.Draw(frame_img, "RGBA")
        
        top_bar_h = int(60 * self.ssaa)
        tool_bar_w = int(110 * self.ssaa)
        bottom_bar_h = int(70 * self.ssaa)
        
        # 1. Barra de Título (Janela estilo Windows/Paint 95/98)
        title_h = int(32 * self.ssaa)
        draw.rectangle([0, 0, w, title_h], fill=(0, 0, 128, 255)) # Azul clássico
        draw.rectangle([0, 0, w, int(3*self.ssaa)], fill=(255, 255, 255, 255))
        
        # Texto do título da janela
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
            
        draw.text((int(12*self.ssaa), int(8*self.ssaa)), "paint-IA-Studio-Pro v0.4 - [Personagem_Goth.bmp]", fill=(255, 255, 255, 255))
        
        # Botões da janela [ _ ] [ ▢ ] [ X ]
        btn_w = int(22 * self.ssaa)
        for idx, symbol in enumerate(["_", "▢", "X"]):
            bx = w - (3 - idx) * (btn_w + int(4*self.ssaa)) - int(8*self.ssaa)
            by = int(5 * self.ssaa)
            draw.rectangle([bx, by, bx + btn_w, by + int(20*self.ssaa)], fill=(192, 192, 192, 255), outline=(255, 255, 255, 255), width=int(1.5*self.ssaa))
            draw.text((bx + int(6*self.ssaa), by + int(2*self.ssaa)), symbol, fill=(0, 0, 0, 255))

        # 2. Barra de Menus Superior (Arquivo, Editar, Exibir, Imagem, Opções)
        menu_y = title_h + int(2*self.ssaa)
        draw.rectangle([0, menu_y, w, top_bar_h], fill=(192, 192, 192, 255))
        menu_items = ["Arquivo", "Editar", "Exibir", "Imagem", "Cores", "Ajuda"]
        cur_mx = int(12 * self.ssaa)
        for item in menu_items:
            draw.text((cur_mx, menu_y + int(6*self.ssaa)), item, fill=(0, 0, 0, 255))
            cur_mx += int(70 * self.ssaa)

        # 3. Painel de Ferramentas Esquerda (Ícones do Paint)
        draw.rectangle([0, top_bar_h, tool_bar_w, h - bottom_bar_h], fill=(192, 192, 192, 255))
        draw.line([tool_bar_w, top_bar_h, tool_bar_w, h - bottom_bar_h], fill=(128, 128, 128, 255), width=int(2*self.ssaa))
        
        # Ícones de ferramentas
        tools = ["✂️", "🪣", "🖌️", "💨", "🔤", "╱", "▢", "◯"]
        for t_idx, t_icon in enumerate(tools):
            col = t_idx % 2
            row = t_idx // 2
            tx = int(12 * self.ssaa) + col * int(42 * self.ssaa)
            ty = top_bar_h + int(12 * self.ssaa) + row * int(42 * self.ssaa)
            
            # Destaque de ferramenta ativa (Pincel selecionado)
            is_active = (t_icon == "🖌️")
            bg_c = (255, 255, 255, 255) if is_active else (192, 192, 192, 255)
            draw.rectangle([tx, ty, tx + int(36*self.ssaa), ty + int(36*self.ssaa)], fill=bg_c, outline=(0, 0, 0, 255), width=int(1.5*self.ssaa))
            draw.text((tx + int(8*self.ssaa), ty + int(8*self.ssaa)), t_icon, fill=(0, 0, 0, 255))

        # 4. Paleta de Cores Inferior
        draw.rectangle([0, h - bottom_bar_h, w, h], fill=(192, 192, 192, 255))
        draw.line([0, h - bottom_bar_h, w, h - bottom_bar_h], fill=(255, 255, 255, 255), width=int(2*self.ssaa))
        
        # Swatches de cores
        palette_colors = [
            (0, 0, 0), (128, 128, 128), (128, 0, 0), (128, 128, 0), (0, 128, 0), (0, 128, 128), (0, 0, 128), (128, 0, 128),
            (255, 255, 255), (192, 192, 192), (255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255),
            (0, 255, 204), (255, 0, 127), (157, 0, 255) # Adições Cyberpunk
        ]
        
        swatch_w = int(22 * self.ssaa)
        cur_px = int(120 * self.ssaa)
        for c in palette_colors:
            py1 = h - bottom_bar_h + int(10*self.ssaa)
            py2 = h - bottom_bar_h + int(10*self.ssaa) + swatch_w
            draw.rectangle([cur_px, py1, cur_px + swatch_w, py2], fill=(*c, 255), outline=(0, 0, 0, 255), width=int(1.5*self.ssaa))
            cur_px += swatch_w + int(4*self.ssaa)

        # 5. Encaixe do Canvas da Arte na Área Central
        canvas_x0 = tool_bar_w + int(8*self.ssaa)
        canvas_y0 = top_bar_h + int(8*self.ssaa)
        canvas_w = w - canvas_x0 - int(12*self.ssaa)
        canvas_h = h - bottom_bar_h - canvas_y0 - int(12*self.ssaa)
        
        resized_art = art_img.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
        
        # Borda chanfrada de canvas de Paint em volta da arte
        draw.rectangle([canvas_x0 - int(3*self.ssaa), canvas_y0 - int(3*self.ssaa), canvas_x0 + canvas_w + int(3*self.ssaa), canvas_y0 + canvas_h + int(3*self.ssaa)], fill=(128, 128, 128, 255))
        frame_img.paste(resized_art, (canvas_x0, canvas_y0), resized_art.convert("RGBA"))
        
        # Doodles e Estrelinhas ao redor da moldura
        doodle_draw = ImageDraw.Draw(frame_img, "RGBA")
        for _ in range(15):
            dx = random.randint(tool_bar_w + 20, w - 30)
            dy = random.randint(top_bar_h + 10, top_bar_h + 40)
            doodle_draw.text((dx, dy), "★", fill=(255, 255, 0, 200))

        return frame_img

    def render_v04_character(self) -> Image.Image:
        """Renderiza a personagem conforme as diretrizes do preset selecionado (A, B, C, D ou E)."""
        w, h = self.w, self.h
        cx, cy = self.cx, self.cy

        # ----------------------------------------------------
        # DEFINIÇÃO DE CORES E PALETA POR PRESET
        # ----------------------------------------------------
        if self.preset_name == "gothic_pastel_fusion":
            bg_top, bg_bot = (6, 5, 14, 255), (16, 8, 24, 255)
            hair_color = (12, 12, 20, 255)
            hair_highlight = (110, 140, 210, 160) # Azul frio
            skin_base = (246, 242, 252, 255)      # Porcelana
            skin_blush = (240, 180, 200, 90)      # Blush rosado delicado
            eyes_color = (235, 10, 45, 255)       # Vermelho destacado
            outfit_color = (10, 9, 14, 255)
            trim_color = (190, 15, 45, 230)       # Carmesim discreto
            stroke_color = (25, 20, 32, 220)
            stroke_jitter = 0.6
        elif self.preset_name == "soft_sketch_base":
            bg_top, bg_bot = (250, 246, 252, 255), (240, 235, 248, 255)
            hair_color = (40, 35, 55, 255)
            hair_highlight = (180, 170, 210, 140)
            skin_base = (255, 250, 252, 255)
            skin_blush = (255, 200, 215, 110)
            eyes_color = (220, 40, 70, 255)
            outfit_color = (50, 45, 65, 255)
            trim_color = (220, 100, 130, 200)
            stroke_color = (80, 70, 95, 200)
            stroke_jitter = 1.2
        elif self.preset_name == "paint_retro_interface":
            bg_top, bg_bot = (12, 12, 24, 255), (24, 16, 40, 255)
            hair_color = (15, 15, 25, 255)
            hair_highlight = (0, 255, 204, 180)  # Neon Cyber
            skin_base = (248, 242, 250, 255)
            skin_blush = (255, 160, 200, 100)
            eyes_color = (255, 0, 127, 255)
            outfit_color = (15, 12, 22, 255)
            trim_color = (0, 255, 204, 255)
            stroke_color = (20, 20, 35, 240)
            stroke_jitter = 0.9
        else: # soft_render_delicado ou production_polish_light
            bg_top, bg_bot = (10, 8, 20, 255), (22, 14, 34, 255)
            hair_color = (12, 12, 18, 255)
            hair_highlight = (130, 160, 220, 160)
            skin_base = (246, 242, 250, 255)
            skin_blush = (245, 185, 205, 100)
            eyes_color = (230, 15, 45, 255)
            outfit_color = (12, 10, 16, 255)
            trim_color = (210, 20, 50, 240)
            stroke_color = (20, 18, 28, 220)
            stroke_jitter = 0.4

        # ----------------------------------------------------
        # 1. CAMADA DE FUNDO
        # ----------------------------------------------------
        bg = Image.new("RGBA", (w, h), bg_top)
        bg_draw = ImageDraw.Draw(bg, "RGBA")
        for y in range(h):
            t = y / h
            r = int(bg_top[0] + (bg_bot[0] - bg_top[0]) * t)
            g = int(bg_top[1] + (bg_bot[1] - bg_top[1]) * t)
            b = int(bg_top[2] + (bg_bot[2] - bg_top[2]) * t)
            bg_draw.line([0, y, w, y], fill=(r, g, b, 255))

        # 2. CAMADA DE CABELO TRASEIRO (Massa + Mechas Largas)
        hair_bg, hb_draw = self.create_layer()
        hb_draw.polygon([
            (cx - int(100*self.ssaa), cy - int(250*self.ssaa)),
            (cx - int(330*self.ssaa), cy - int(170*self.ssaa)),
            (cx - int(480*self.ssaa), cy + int(110*self.ssaa)),
            (cx - int(420*self.ssaa), cy + int(480*self.ssaa)),
            (cx - int(300*self.ssaa), h),
            (cx + int(290*self.ssaa), h),
            (cx + int(440*self.ssaa), cy + int(470*self.ssaa)),
            (cx + int(460*self.ssaa), cy + int(110*self.ssaa)),
            (cx + int(310*self.ssaa), cy - int(180*self.ssaa)),
            (cx + int(90*self.ssaa), cy - int(250*self.ssaa)),
        ], fill=hair_color)

        # Mechas soltas (Stroke Adaptativo)
        for _ in range(220):
            side = -1 if random.random() > 0.48 else 1
            x0 = cx + side * random.randint(int(40*self.ssaa), int(300*self.ssaa))
            y0 = cy - random.randint(int(170*self.ssaa), int(270*self.ssaa))
            
            p1 = (x0 + side * random.randint(int(70*self.ssaa), int(240*self.ssaa)), y0 + random.randint(int(140*self.ssaa), int(350*self.ssaa)))
            p2 = (x0 + side * random.randint(int(30*self.ssaa), int(180*self.ssaa)), y0 + random.randint(int(380*self.ssaa), int(680*self.ssaa)))
            p3 = (x0 + side * random.randint(int(10*self.ssaa), int(130*self.ssaa)), h)

            c_rand = random.random()
            if c_rand > 0.7:
                cur_color = hair_highlight
                sw = random.randint(int(2*self.ssaa), int(5*self.ssaa))
            else:
                cur_color = hair_color
                sw = random.randint(int(4*self.ssaa), int(12*self.ssaa))

            self.draw_hand_drawn_stroke(hb_draw, (x0, y0), p1, p2, p3, cur_color, base_w=sw, jitter_amount=stroke_jitter)

        base = Image.alpha_composite(bg, hair_bg)

        # 3. CORPO & ROUPA GÓTICA
        body, b_draw = self.create_layer()
        corset_top = cy + int(200 * self.ssaa)
        b_draw.polygon([
            (cx - int(130*self.ssaa), corset_top),
            (cx + int(130*self.ssaa), corset_top),
            (cx + int(180*self.ssaa), h),
            (cx - int(180*self.ssaa), h)
        ], fill=outfit_color)
        
        # Debrum e costura
        b_draw.line([(cx - int(130*self.ssaa), corset_top), (cx, corset_top + int(44*self.ssaa)), (cx + int(130*self.ssaa), corset_top)], fill=trim_color, width=int(4 * self.ssaa))
        
        # Gargantilha
        choker_y = cy + int(145 * self.ssaa)
        b_draw.rectangle([cx - int(58*self.ssaa), choker_y, cx + int(58*self.ssaa), choker_y + int(18*self.ssaa)], fill=(20, 20, 26, 255), outline=(160, 165, 185, 255), width=int(1.5*self.ssaa))
        gem_y = choker_y + int(30 * self.ssaa)
        b_draw.polygon([(cx, gem_y - int(12*self.ssaa)), (cx + int(10*self.ssaa), gem_y), (cx, gem_y + int(16*self.ssaa)), (cx - int(10*self.ssaa), gem_y)], fill=eyes_color)

        base = Image.alpha_composite(base, body)

        # 4. ROSTO DELICADO, BOCHECHAS & BOCA
        face, f_draw = self.create_layer()
        # Pescoço
        f_draw.polygon([(cx - int(65*self.ssaa), cy + int(45*self.ssaa)), (cx + int(65*self.ssaa), cy + int(45*self.ssaa)), (cx + int(80*self.ssaa), cy + int(165*self.ssaa)), (cx - int(80*self.ssaa), cy + int(165*self.ssaa))], fill=skin_base)

        # Rosto com pequena assimetria
        face_pts = [
            (cx - int(144*self.ssaa), cy - int(150*self.ssaa)),
            (cx - int(160*self.ssaa), cy - int(38*self.ssaa)),
            (cx - int(150*self.ssaa), cy + int(32*self.ssaa)),
            (cx - int(108*self.ssaa), cy + int(96*self.ssaa)),
            (cx - int(54*self.ssaa), cy + int(141*self.ssaa)),
            (cx + int(2*self.ssaa), cy + int(152*self.ssaa)),
            (cx + int(55*self.ssaa), cy + int(139*self.ssaa)),
            (cx + int(110*self.ssaa), cy + int(94*self.ssaa)),
            (cx + int(148*self.ssaa), cy + int(28*self.ssaa)),
            (cx + int(158*self.ssaa), cy - int(42*self.ssaa)),
            (cx + int(145*self.ssaa), cy - int(150*self.ssaa)),
            (cx, cy - int(200*self.ssaa))
        ]
        f_draw.polygon(face_pts, fill=skin_base)

        # Blush suave nas bochechas
        blush_layer, bl_draw = self.create_layer()
        bl_draw.ellipse([cx - int(140*self.ssaa), cy + int(5*self.ssaa), cx - int(60*self.ssaa), cy + int(50*self.ssaa)], fill=skin_blush)
        bl_draw.ellipse([cx + int(60*self.ssaa), cy + int(5*self.ssaa), cx + int(140*self.ssaa), cy + int(50*self.ssaa)], fill=skin_blush)
        blush_layer = blush_layer.filter(ImageFilter.GaussianBlur(int(14 * self.ssaa)))
        face = Image.alpha_composite(face, blush_layer)
        f_draw = ImageDraw.Draw(face, "RGBA")

        # Nariz mínimo sugerido
        nose_y = cy + int(25 * self.ssaa)
        f_draw.line([cx - int(4*self.ssaa), nose_y + int(18*self.ssaa), cx, nose_y + int(23*self.ssaa), cx + int(5*self.ssaa), nose_y + int(18*self.ssaa)], fill=(160, 150, 175, 200), width=int(2 * self.ssaa))

        # Boca pequena e sutil com leve assimetria
        mouth_y = cy + int(86 * self.ssaa)
        f_draw.polygon([
            (cx - int(36*self.ssaa), mouth_y),
            (cx - int(15*self.ssaa), mouth_y - int(5*self.ssaa)),
            (cx + int(1*self.ssaa), mouth_y - int(2*self.ssaa)),
            (cx + int(14*self.ssaa), mouth_y - int(4*self.ssaa)),
            (cx + int(36*self.ssaa), mouth_y),
            (cx + int(18*self.ssaa), mouth_y + int(11*self.ssaa)),
            (cx, mouth_y + int(13*self.ssaa)),
            (cx - int(20*self.ssaa), mouth_y + int(10*self.ssaa))
        ], fill=(150, 20, 50, 240))

        base = Image.alpha_composite(base, face)

        # 5. CHIFRES NEGROS CURVADOS DE OBSIDIANA
        horns, h_draw = self.create_layer()
        for side in [-1, 1]:
            bx = cx + side * int(120 * self.ssaa)
            by = cy - int(155 * self.ssaa)
            for i in range(85):
                t = i / 85
                hx = bx + side * (math.sin(t * math.pi * 0.85) * int(220*self.ssaa) + t * int(50*self.ssaa))
                hy = by - (t * int(380*self.ssaa) + math.cos(t * math.pi * 0.5) * int(50*self.ssaa))
                rad = (1 - t) * int(38 * self.ssaa) + int(2.5 * self.ssaa)
                h_draw.ellipse([hx - rad, hy - rad, hx + rad, hy + rad], fill=(8, 8, 14, 255))
                h_draw.ellipse([hx - rad*0.4, hy - rad*0.4, hx + rad*0.2, hy + rad*0.2], fill=(130, 150, 185, 45))
                rim_x = hx + side * (rad * 0.8)
                h_draw.ellipse([rim_x - int(3*self.ssaa), hy - int(3*self.ssaa), rim_x + int(3*self.ssaa), hy + int(3*self.ssaa)], fill=trim_color)

        base = Image.alpha_composite(base, horns)

        # 6. OLHOS EXPRESSIVOS E DETALHADOS
        eyes, e_draw = self.create_layer()
        eye_y = cy - int(30 * self.ssaa)
        eye_space = int(75 * self.ssaa)
        ew = int(46 * self.ssaa)
        eh = int(25 * self.ssaa)

        for side in [-1, 1]:
            ex = cx + side * eye_space
            brow_y = eye_y - int(34 * self.ssaa)
            e_draw.polygon([
                (ex - side * int(34*self.ssaa), brow_y + int(5*self.ssaa)),
                (ex - side * int(12*self.ssaa), brow_y - int(10*self.ssaa)),
                (ex + side * int(34*self.ssaa), brow_y - int(2*self.ssaa)),
                (ex + side * int(24*self.ssaa), brow_y - int(14*self.ssaa)),
                (ex - side * int(12*self.ssaa), brow_y - int(16*self.ssaa))
            ], fill=stroke_color)

            e_draw.ellipse([ex - ew, eye_y - eh, ex + ew, eye_y + eh], fill=(12, 10, 18, 255))
            e_draw.ellipse([ex - ew + int(3.5*self.ssaa), eye_y - eh + int(3.5*self.ssaa), ex + ew - int(3.5*self.ssaa), eye_y + eh - int(3.5*self.ssaa)], fill=(240, 240, 248, 255))

            # Íris Rubi
            iris_r = int(19 * self.ssaa)
            for ir in range(iris_r, 0, -int(2 * self.ssaa)):
                t = 1 - (ir / iris_r)
                ir_color = (int(180 + t * 75), int(t * 70), int(20 + t * 60), 255) if self.preset_name != "paint_retro_interface" else eyes_color
                e_draw.ellipse([ex - ir, eye_y - ir, ex + ir, eye_y + ir], fill=ir_color)

            e_draw.ellipse([ex - int(3*self.ssaa), eye_y - int(14*self.ssaa), ex + int(3*self.ssaa), eye_y + int(14*self.ssaa)], fill=(10, 0, 4, 255))
            e_draw.ellipse([ex - int(6*self.ssaa), eye_y - int(8*self.ssaa), ex - int(1*self.ssaa), eye_y - int(3*self.ssaa)], fill=(255, 255, 255, 255))

        base = Image.alpha_composite(base, eyes)

        # 7. CABELO FRONTAL COM FIOS CRUZADOS (STRAY HAIRS)
        hair_fg, hf_draw = self.create_layer()
        front_strands = [
            [(cx - int(145*self.ssaa), cy - int(200*self.ssaa)), (cx - int(115*self.ssaa), cy - int(100*self.ssaa)), (cx - int(140*self.ssaa), cy + int(50*self.ssaa)), (cx - int(160*self.ssaa), cy + int(240*self.ssaa))],
            [(cx + int(148*self.ssaa), cy - int(198*self.ssaa)), (cx + int(118*self.ssaa), cy - int(98*self.ssaa)), (cx + int(138*self.ssaa), cy + int(52*self.ssaa)), (cx + int(162*self.ssaa), cy + int(242*self.ssaa))],
            # Fios soltos perdidos cruzando a testa
            [(cx - int(45*self.ssaa), cy - int(195*self.ssaa)), (cx - int(10*self.ssaa), cy - int(110*self.ssaa)), (cx + int(15*self.ssaa), cy - int(55*self.ssaa))],
            [(cx + int(40*self.ssaa), cy - int(190*self.ssaa)), (cx + int(5*self.ssaa), cy - int(105*self.ssaa)), (cx - int(20*self.ssaa), cy - int(50*self.ssaa))]
        ]

        for pts in front_strands:
            p0, p1, p2 = pts[0], pts[1], pts[2]
            p3 = pts[3] if len(pts) > 3 else pts[2]
            self.draw_hand_drawn_stroke(hf_draw, p0, p1, p2, p3, stroke_color, base_w=int(10*self.ssaa), jitter_amount=stroke_jitter)
            self.draw_hand_drawn_stroke(hf_draw, p0, p1, p2, p3, hair_highlight, base_w=int(3*self.ssaa), jitter_amount=stroke_jitter)

        base = Image.alpha_composite(base, hair_fg)

        # 8. DOWNSAMPLING LANCZOS & TEXTURA
        final_art = base.convert("RGB").resize((self.target_w, self.target_h), Image.Resampling.LANCZOS)

        # Se for o Preset B (Paint Retro Interface), aplica a moldura/UI de Paint
        if self.ui_frame or self.preset_name == "paint_retro_interface":
            print("🎨 Aplicando Moldura de Interface Paint Retrô (Preset B)...")
            final_art = self.draw_paint_retro_frame(final_art)

        return final_art

def main():
    parser = argparse.ArgumentParser(prog="paint_studio_pro", description="Motor Gráfico v0.4 BLACKCORE / paint-IA-Studio-Pro")
    parser.add_argument("--preset", "-p", choices=["A", "B", "C", "D", "E", "soft_sketch_base", "paint_retro_interface", "soft_render_delicado", "gothic_pastel_fusion", "production_polish_light"], default="D", help="Preset de estilo")
    parser.add_argument("--output", "-o", help="Nome do arquivo de saída")
    args = parser.parse_args()

    # Mapeamento de letra para nome de preset
    preset_map = {
        "A": "soft_sketch_base",
        "B": "paint_retro_interface",
        "C": "soft_render_delicado",
        "D": "gothic_pastel_fusion",
        "E": "production_polish_light"
    }
    selected_preset = preset_map.get(args.preset, args.preset)

    print(f"\033[1;36m🎨 BLACKCORE STUDIO PRO v0.4 // Preset: {selected_preset.upper()}...\033[0m")
    t0 = time.time()
    
    engine = ProStudioEngineV04(target_w=1200, target_h=1200, preset_key=selected_preset, ssaa=2)
    img = engine.render_v04_character()
    
    out_dir = output_dir()
    if not out_dir.exists():
        out_dir = Path.home() / "BLACKCORE-Projects" / "black-paint-studio" / "gallery"
        out_dir.mkdir(parents=True, exist_ok=True)

    out_name = args.output or f"personagem_{selected_preset}_v04.png"
    out_file = out_dir / out_name
    img.save(out_file, "PNG", quality=100)

    scan_media(out_file)
    
    elapsed = time.time() - t0
    print(f"\033[1;32m✅ Renderização v0.4 [{selected_preset}] concluída em {elapsed:.2f}s!\033[0m")
    print(f"\033[1;37m👉 Arquivo salvo na galeria: {out_file}\033[0m\n")

    try:
        sys.path.insert(0, str(Path.home() / ".blackcore" / "modules" / "black_numbers"))
        from bn_vision import scan_pixels, render_terminal_ansi
        scan_data = scan_pixels(out_file, width=42, height=22)
        render_terminal_ansi(scan_data, colored=True)
    except Exception as e:
        print(f"Prévia: {e}")

if __name__ == "__main__":
    main()
