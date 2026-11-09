#!/usr/bin/env python3
"""generate_personagem_ia.py — Retrato neural de personagem completa (Flux/Pollinations).

Rota neural real (a mesma já usada com sucesso neste telefone em generate_real_ai_art.py).
Alvo do pedido: personagem extremamente linda, completa, cabelo muito bem feito,
roupa casual elegante e mãos perfeitas e bonitas.
"""
import io
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from termux_compat import output_dir

from PIL import Image, ImageEnhance, ImageFilter

OUT_DIRS = [output_dir()]

BASE = (
    "Breathtakingly beautiful young adult woman, full upper-body portrait, "
    "stunning detailed long flowing dark hair with glossy individually painted strands, "
    "soft face-framing layers, luminous healthy hair highlights; "
    "elegant casual outfit: cozy oversized cream knit sweater with soft wool texture, "
    "high-waist denim jeans; perfect graceful hands with slim well-proportioned fingers, "
    "one hand gently holding a paper coffee cup, the other lightly tucking a strand of hair, "
    "anatomically flawless hands, five fingers each, natural nails; "
    "warm confident gentle smile, expressive detailed eyes with catchlights, "
    "golden-hour city street bokeh background, cinematic soft rim light, "
    "modern anime semi-realistic illustration style, masterwork lineart, cel shading, "
    "8k detail, trending on ArtStation, high quality, no text, no watermark, no logo"
)

VARIANTS = [
    {"name": "personagem_ia_linda_01", "seed": 770231},
    {"name": "personagem_ia_linda_02", "seed": 195502},
]

W, H = 1024, 1536


def fetch(prompt: str, seed: int) -> bytes:
    url = (
        "https://image.pollinations.ai/prompt/"
        + urllib.parse.quote(prompt)
        + f"?width={W}&height={H}&model=flux&nologo=true&seed={seed}&enhance=true"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Android; Termux; BLACKCORE)"})
    with urllib.request.urlopen(req, timeout=150) as resp:
        return resp.read()


def main() -> int:
    ok = 0
    report = []
    for v in VARIANTS:
        t0 = time.time()
        try:
            raw = fetch(BASE, v["seed"])
            img = Image.open(io.BytesIO(raw)).convert("RGB")
            img = ImageEnhance.Sharpness(img).enhance(1.15)
            img = ImageEnhance.Contrast(img).enhance(1.06)
            img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=90, threshold=3))
            fname = f"{v['name']}.png"
            saved = []
            for d in OUT_DIRS:
                try:
                    p = d / fname
                    img.save(p, "PNG", optimize=True)
                    saved.append(str(p))
                except OSError:
                    continue
            import subprocess
            for p in saved:
                subprocess.run(["termux-media-scan", p], check=False)
            ok += 1
            report.append({"arquivo": fname, "dim": list(img.size), "salvos": saved,
                           "segundos": round(time.time() - t0, 1)})
            print(f"✅ {fname} gerada ({img.size[0]}x{img.size[1]}) em {time.time()-t0:.1f}s → {saved[0]}")
        except Exception as exc:  # noqa: BLE001
            report.append({"arquivo": v["name"], "erro": str(exc)[:300]})
            print(f"❌ {v['name']}: {exc}")
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
