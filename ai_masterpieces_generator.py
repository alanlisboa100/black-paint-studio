#!/usr/bin/env python3
"""Geração de imagens usando um endpoint externo Pollinations; requer internet.

Este script não é local, não usa um Flux instalado no aparelho e não é chamado
pelo editor web. A resposta do serviço remoto é ampliada e ajustada por Pillow.
"""

import io, json, math, os, random, subprocess, sys, time
import urllib.parse, urllib.request
from pathlib import Path
from termux_compat import scan_media, output_dir
from PIL import Image, ImageEnhance, ImageFilter

TARGET_DIR = output_dir()
if not TARGET_DIR.exists():
    TARGET_DIR = Path.home() / "BLACKCORE-Projects" / "black-paint-studio" / "gallery"
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

MASTERPIECES = [
    {
        "id": "p1",
        "title": "O Dragão Celestial de Jade nas Nuvens Cósmicas",
        "filename": "ia_arte_01_dragao_celestial_jade.png",
        "seed": 771234,
        "prompt": (
            "An epic breathtaking cinematic digital painting of a colossal celestial ancient oriental dragon "
            "coiling around majestic floating limestone karst mountain peaks shrouded in glowing morning mist. "
            "The dragon scales are carved from translucent imperial emerald jade and shimmering quartz crystal, "
            "radiating a subtle turquoise bioluminescence. Cascading waterfalls plunging into clouds, ancient golden-roofed "
            "pagoda temples balanced on steep cliffs. Golden hour volumetric sunbeams piercing through magenta and indigo clouds, "
            "floating glowing lanterns, hyper-detailed fantasy art, masterpiece, trending on ArtStation, Makoto Shinkai meets "
            "James Gurney lighting, 8k resolution, photorealistic depth of field, sublime and awe-inspiring atmosphere."
        )
    },
    {
        "id": "p2",
        "title": "A Catedral Cyber-Bioluminescente de Neo-Verdia",
        "filename": "ia_arte_02_catedral_cyber_bioluminescente.png",
        "seed": 993421,
        "prompt": (
            "A breathtaking interior of a massive ruined neo-gothic sci-fi cathedral overgrown with alien bioluminescent jungle flora. "
            "Colossal dark titanium rib arches and broken stained glass ceiling revealing a vivid swirling galaxy nebula. "
            "In the center stands a gigantic ancient cybernetic tree of life with roots made of glowing fiber-optic cables "
            "and canopy of prismatic glowing crystal leaves emitting pulses of cyan, ultraviolet and amber light. "
            "Reflections on a dark mirror-like shallow water floor, floating glowing spores, solitary hooded traveler in high-tech "
            "exploration suit standing in wonder. Volumetric cinematic god rays, Octane Render, unreal engine 5, Syd Mead meets "
            "Moebius aesthetic, intricate architectural details, majestic surrealism."
        )
    },
    {
        "id": "p3",
        "title": "O Santuário Abissal de Atlântida e o Leviatã Cósmico",
        "filename": "ia_arte_03_santuario_atlantida_leviata.png",
        "seed": 445892,
        "prompt": (
            "An awe-inspiring mystical deep underwater kingdom of ancient sunken Atlantis, colossal marble temples and golden spires "
            "surrounded by towering bioluminescent coral reefs glowing in electric cyan, violet and gold. A majestic giant cosmic "
            "whale leviathan gliding gracefully overhead with glowing celestial constellations and nebula stars shimmering on its deep sapphire skin, "
            "accompanied by schools of translucent glowing manta rays. Beams of sunlight refracting through crystal-clear turquoise ocean depths "
            "creating intricate animated caustic light patterns on ancient statues and seabeds. Dreamy ethereal fantasy masterpiece, "
            "cinematic wide-angle view, vibrant color harmony, ultra-detailed textures, breathtaking beauty."
        )
    }
]

def fetch_and_master_image(item: dict) -> Path:
    print(f"\n🎨 Gerando Obra: '{item['title']}'...")
    print(f"🌱 Seed: {item['seed']}")
    
    encoded_prompt = urllib.parse.quote(item["prompt"])
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true&seed={item['seed']}"
    
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (BLACKCORE Neural Studio/1.0)"})
    
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=90) as resp:
        raw_data = resp.read()
    
    fetch_time = time.time() - t0
    print(f"⚡ Serviço remoto respondeu em {fetch_time:.2f}s ({len(raw_data)//1024} KB recebidos).")
    
    # Processamento e Masterização com Pillow
    img = Image.open(io.BytesIO(raw_data)).convert("RGB")
    orig_w, orig_h = img.size
    
    target_w, target_h = 1536, 1536
    print(f"🔄 Executando Upscaling de Masterização Lanczos ({orig_w}x{orig_h} -> {target_w}x{target_h})...")
    mastered_img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Realce sutil de nitidez e contraste para tela de smartphone
    mastered_img = ImageEnhance.Sharpness(mastered_img).enhance(1.15)
    mastered_img = ImageEnhance.Contrast(mastered_img).enhance(1.04)
    
    out_path = TARGET_DIR / item["filename"]
    mastered_img.save(out_path, "PNG", quality=100)
    
    # Varredura do Android MediaStore
    scan_media(out_path)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"✅ Obra-prima salva com sucesso: {out_path} ({size_kb} KB)")
    
    return out_path

def main():
    print("==================================================================")
    print("🌐 BLACK PAINT // GERADOR REMOTO (POLLINATIONS)")
    print("==================================================================")
    
    total_t0 = time.time()
    results = []
    
    for item in MASTERPIECES:
        try:
            out_file = fetch_and_master_image(item)
            results.append((item, out_file, True))
        except Exception as e:
            print(f"❌ Erro ao gerar {item['title']}: {e}")
            results.append((item, None, False))
            
    total_time = time.time() - total_t0
    print("\n==================================================================")
    print(f"✨ Pipeline remoto concluído em {total_time:.2f}s.")
    for item, out_file, ok in results:
        if ok:
            print(f"  • {item['title']}: {out_file}")
    print("==================================================================")

if __name__ == "__main__":
    main()
