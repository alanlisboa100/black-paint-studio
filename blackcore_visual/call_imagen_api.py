#!/usr/bin/env python3
"""
call_imagen_api.py - Executa a chamada real à API do Google Imagen / Gemini Generative Language
"""
import os
import json
import base64
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
        print("❌ Erro: Chave de API da Google não encontrada.")
        return

    print("🌐 Disparando requisição para a API do Google AI Studio...")
    
    # Endpoint do Imagen 3 / Generative Language
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
    
    payload = {
        "instances": [
            {
                "prompt": "An insane cyberpunk gothic Twitter X header cover art, Misuki gothic demon-girl with long black hair, curved black horns, glowing crimson anime eyes, neon cyan and magenta matrix grid, dark obsidian atmosphere, masterpiece, 8k"
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "3:1",
            "personGeneration": "ALLOW_ADULT"
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if "predictions" in res_data and len(res_data["predictions"]) > 0:
                b64_img = res_data["predictions"][0].get("bytesBase64Encoded")
                if b64_img:
                    img_bytes = base64.b64decode(b64_img)
                    out_path = Path("/storage/emulated/0/Download/misuki_blackcore_imagen3.png")
                    out_path.write_bytes(img_bytes)
                    print(f"✅ Imagem gerada via Google Imagen 3 com sucesso! Salva em: {out_path}")
                    return
            print("⚠️ Resposta da API recebida, mas sem dados de imagem diretos:", json.dumps(res_data)[:200])
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"⚠️ Erro HTTP da API do Google ({e.code}): {err_body[:300]}")
        print("💡 Nota: Algumas chaves gratuitas do pool padrão são focadas em modelos de texto/chat (Gemini Flash) e podem não ter o endpoint de difusão de imagem ativado na mesma cota.")
    except Exception as e:
        print(f"⚠️ Erro na conexão: {e}")

if __name__ == "__main__":
    main()
