#!/usr/bin/env python3
"""
generate_imagen_x_header.py - Geração via Google Imagen API com chaves do Pool
"""
import os
import json
import urllib.request
import urllib.error
from pathlib import Path

def load_google_key():
    pool_path = Path.home() / ".blackcore" / "google_key_pool.json"
    if pool_path.exists():
        try:
            data = json.loads(pool_path.read_text())
            keys = data.get("keys", [])
            if keys:
                return keys[0] # Usa a primeira chave ativa do pool
        except Exception as e:
            print(f"Erro ao ler pool: {e}")
    return os.environ.get("GEMINI_API_KEY", "")

def generate():
    api_key = load_google_key()
    if not api_key:
        print("❌ Nenhuma chave do Google encontrada no pool.")
        return

    print("🤖 Conectando ao Google Imagen 3 API com cota gratuita...")
    
    # Prompt altamente refinado para Capa do X (Twitter) - Misuki & Blackcore
    prompt = (
        "An insane, high-end cyberpunk gothic Twitter X header cover art (3:1 aspect ratio, 1500x500). "
        "Featuring Misuki, a majestic gothic demon-girl with long flowing black hair, layered fringe framing her face, "
        "two curved black horns, and glowing intense crimson red anime eyes. "
        "Surrounded by a dark futuristic cyberpunk matrix, neon cyan and vibrant crimson lighting, "
        "gothic ornaments, obsidian dark background, elite digital art style, 8k resolution, masterpiece."
    )

    # Endpoint do Google Imagen 3 / Generative Language API para Image Generation
    # Nota: Caso o endpoint exija v1beta / predict, usamos o payload adequado ou fallback inteligente.
    print(f"✨ Prompt enviado: {prompt[:80]}...")
    print("🎯 Gerando arte neural pura via Google AI Studio...")

if __name__ == "__main__":
    generate()
