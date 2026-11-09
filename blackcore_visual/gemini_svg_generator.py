#!/usr/bin/env python3
"""
gemini_svg_generator.py - Usa a API Gemini (gemini-3.5-flash) para criar a arte vetorizada via IA
"""
import os
import json
import urllib.request
import urllib.error
from pathlib import Path

def get_api_key():
    pool_path = Path.home() / ".blackcore" / "google_key_pool.json"
    if pool_path.exists():
        try:
            data = json.loads(pool_path.read_text())
            keys = data.get("keys", [])
            if keys:
                return keys[0]
        except Exception:
            pass
    return os.environ.get("GEMINI_API_KEY", "")

def main():
    api_key = get_api_key()
    if not api_key:
        print("❌ Chave não encontrada.")
        return

    print("🤖 Consultando a API Gemini 3.5 Flash para projetar a arte vetorial insana...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    
    prompt = (
        "You are an elite master graphic designer and AI artist. "
        "Create a stunning, complete SVG XML string (wrapped in ```xml ... ```) for a Twitter/X header banner (width='3000' height='1000'). "
        "Theme: Misuki and Blackcore cyberpunk gothic art. "
        "Include: A dark obsidian gradient background, cyberpunk cyan and crimson neon glowing elements, "
        "a stylized anime gothic demon-girl silhouette with black horns and glowing red eyes on the left, "
        "and a sleek futuristic tech card on the right with the text 'MISUKI // BLACKCORE' and '@NFTIX2077'. "
        "Make it extremely detailed, insane, beautiful, and visually striking. Output ONLY valid SVG inside an xml markdown block."
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            candidates = res.get("candidates", [])
            if candidates:
                text = candidates[0]["content"]["parts"][0]["text"]
                print("✨ Gemini 3.5 Flash gerou o código da arte com sucesso!")
                
                if "```xml" in text:
                    svg_code = text.split("```xml")[1].split("```")[0].strip()
                elif "```svg" in text:
                    svg_code = text.split("```svg")[1].split("```")[0].strip()
                elif "<svg" in text:
                    start = text.find("<svg")
                    end = text.rfind("</svg>") + 6
                    svg_code = text[start:end]
                else:
                    svg_code = None

                if svg_code:
                    svg_path = Path("BLACKCORE-Projects/black-paint-studio/gallery_misuki/gemini_art.svg")
                    svg_path.write_text(svg_code, encoding="utf-8")
                    print(f"✅ SVG gerado pela API do Gemini salvo em: {svg_path}")
                else:
                    print("⚠️ Resposta do Gemini não continha bloco SVG válido. Salvando texto bruto.")
                    Path("BLACKCORE-Projects/black-paint-studio/gallery_misuki/gemini_raw.txt").write_text(text)
            else:
                print("⚠️ Sem candidatos na resposta do Gemini.")
    except Exception as e:
        print(f"❌ Erro na API do Gemini: {e}")

if __name__ == "__main__":
    main()
