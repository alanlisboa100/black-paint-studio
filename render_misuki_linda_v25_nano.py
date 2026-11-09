#!/usr/bin/env python3
"""render_misuki_linda_v25_nano.py — Misuki "mais linda" via Google Gemini Image (Nano Banana Pro).

Rota real: generativelanguage.googleapis.com/models/<model>:generateContent
com responseModalities=["IMAGE"], usando o pool de chaves do BLACKCORE (rotação em falha).

DNA travado (MISUKI_RUNTIME_MEMORY_V4):
  HC01 dois chifres | HC02 cabelo preto muito longo | HC03 gótico | HC04 adulto (sem chibi)
  HC05 separação tonal | HC06 franja deixa os olhos visíveis | HC07 sem "pente de listras"
  HC08 acessórios góticos preservados
Foco do pedido: rosto mais bonito, nariz e boca naturais, cabelo reconstruído em massa.
"""
from __future__ import annotations

import base64
import io
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OUT_DIRS = [HERE / "gallery_misuki"]
for extra in (Path("/storage/emulated/0/Download"), Path.home() / "Download"):
    try:
        extra.mkdir(parents=True, exist_ok=True)
        if extra not in OUT_DIRS:
            OUT_DIRS.append(extra)
    except OSError:
        pass

MODEL_CHAIN = ["gemini-3-pro-image", "gemini-3.1-flash-image", "gemini-2.5-flash-image"]
ASPECT = "3:4"

FACE = (
    "extremely beautiful adult anime woman, elegant adult proportions, refined tapered jaw, soft chin, "
    "natural small delicate nose with a subtle bridge and soft nostril shading, naturally shaped small lips "
    "with a gentle cupid's bow and natural rosy vermilion gradient, no heavy lipstick, no exaggerated mouth, "
    "luminous porcelain skin with soft subsurface glow and light blush, large expressive almond eyes, "
    "glossy dark crimson-red irises with several small catchlights, defined upper eyelid crease, long lashes, "
    "naturally tapered elegant eyebrows"
)

HAIR = (
    "extremely long jet-black silky hair built from a few large flowing lock masses, three to seven major "
    "fringe locks, layered face-framing bangs that leave both eyes fully visible, hair volume at the crown, "
    "glossy individually painted strands with fine ribbon highlights, no comb-like field of parallel stripes, "
    "no roof-shaped or flat hair top"
)

HORNS = (
    "exactly two glossy black keratin horns rooted at the upper-lateral hairline, sweeping outward then curving "
    "upward, thick base tapering to sharp tips, subtle groove texture catching the rim light"
)

OUTFIT = (
    "elegant black gothic garment with fine lace trim, slender straps and small buckles, a choker with a tiny "
    "pentagram pendant, sparse jewel accents, dark elegant silhouette"
)

STYLE = (
    "cinematic single-direction rim light separating the black hair and horns from the background, moody dark "
    "atmospheric background with soft bokeh and low contrast behind the face, monochrome black-and-white tonal "
    "scheme with red present only in the irises, ultra detailed clean line art, smooth gradient shading, "
    "masterpiece illustration, 8k"
)

NEGATIVE = (
    "no text, no watermark, no logo, no signature, no chibi, no childlike proportions, no blonde hair, "
    "no blue eyes, no candy-stripe hair, no extra fingers, no deformed hands, no distorted or asymmetrical face, "
    "no busy high-contrast background behind the face"
)

VARIANTS = [
    {"name": "misuki_linda_best_a", "shot":
        "upper-body front portrait, shoulders open, direct confident gaze into the camera, "
        "a few loose locks crossing one shoulder"},
    {"name": "misuki_linda_best_b", "shot":
        "three-quarter portrait, chin slightly lowered, one large lock sweeping across the shoulder, "
        "soft introspective look"},
    {"name": "misuki_linda_best_c", "shot":
        "close beauty portrait, head slightly tilted, both eyes fully visible through the layered fringe, "
        "intense direct stare"},
]


def build_prompt(shot: str) -> str:
    parts = [
        "breathtaking masterpiece semirealistic anime illustration of Misuki, a gothic demon girl named Misuki",
        shot,
        FACE,
        HAIR,
        HORNS,
        OUTFIT,
        STYLE,
        NEGATIVE,
    ]
    return ", ".join(p.strip().strip(",") for p in parts)


def load_keys() -> list[str]:
    p = Path.home() / ".blackcore" / "google_key_pool.json"
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            keys = [k for k in data.get("keys", []) if isinstance(k, str) and k.strip()]
            if keys:
                return keys
        except (OSError, ValueError):
            pass
    import os
    env = os.environ.get("GEMINI_API_KEY", "").strip()
    return [env] if env else []


def generate(model: str, key: str, prompt: str, timeout: int = 180) -> tuple[bytes, str]:
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model}:generateContent")
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": ASPECT},
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"]), inline.get("mimeType", "image/png")
    raise RuntimeError("resposta sem imagem: " + json.dumps(data)[:300])


def save_all(img: Image.Image, fname: str) -> list[str]:
    saved: list[str] = []
    for d in OUT_DIRS:
        try:
            p = d / fname
            img.save(p, "PNG", optimize=True)
            saved.append(str(p))
        except OSError:
            continue
    for p in saved:
        if shutil.which("termux-media-scan"):
            subprocess.run(["termux-media-scan", p], check=False, capture_output=True)
    return saved


def contact_sheet(paths: list[Path]) -> Path | None:
    if len(paths) < 2:
        return None
    thumbs = []
    for p in paths:
        try:
            im = Image.open(p).convert("RGB")
            im.thumbnail((640, 900), Image.Resampling.LANCZOS)
            thumbs.append(im)
        except OSError:
            continue
    if not thumbs:
        return None
    w = sum(t.width for t in thumbs) + 16 * (len(thumbs) + 1)
    h = max(t.height for t in thumbs) + 32
    sheet = Image.new("RGB", (w, h), (8, 8, 10))
    x = 16
    for t in thumbs:
        sheet.paste(t, (x, 16))
        x += t.width + 16
    out = OUT_DIRS[0] / "MISUKI_LINDA_ESCOLHA.png"
    sheet.save(out, "PNG", optimize=True)
    return out


def main() -> int:
    OUT_DIRS[0].mkdir(parents=True, exist_ok=True)
    keys = load_keys()
    if not keys:
        print("SEM_CHAVE")
        return 2
    print(f"chaves no pool: {len(keys)} | modelos: {' > '.join(MODEL_CHAIN)} | aspecto {ASPECT}")

    report, written, ok = [], [], 0
    for idx, v in enumerate(VARIANTS):
        prompt = build_prompt(v["shot"])
        done = False
        for model in MODEL_CHAIN:
            if done:
                break
            for ki in range(len(keys)):
                key = keys[(idx + ki) % len(keys)]
                t0 = time.time()
                try:
                    raw, mime = generate(model, key, prompt)
                    img = Image.open(io.BytesIO(raw)).convert("RGB")
                    fname = f"{v['name']}.png"
                    saved = save_all(img, fname)
                    written.append(Path(saved[0]))
                    ok += 1
                    done = True
                    entry = {"arquivo": fname, "modelo": model, "slot": (idx + ki) % len(keys) + 1,
                             "dim": list(img.size), "kb": round(Path(saved[0]).stat().st_size / 1024, 1),
                             "segundos": round(time.time() - t0, 1), "salvos": saved}
                    report.append(entry)
                    print(f"OK {fname} [{model} slot{(idx+ki)%len(keys)+1}] "
                          f"{img.size[0]}x{img.size[1]} {time.time()-t0:.1f}s -> {saved[0]}")
                    break
                except urllib.error.HTTPError as e:
                    detail = e.read().decode("utf-8", "ignore")[:160].replace("\n", " ")
                    report.append({"arquivo": v["name"], "modelo": model,
                                   "slot": (idx + ki) % len(keys) + 1, "erro": f"HTTP {e.code} {detail}"})
                    print(f"  falha {model} slot{(idx+ki)%len(keys)+1}: HTTP {e.code}")
                except Exception as exc:  # noqa: BLE001
                    report.append({"arquivo": v["name"], "modelo": model,
                                   "slot": (idx + ki) % len(keys) + 1, "erro": str(exc)[:200]})
                    print(f"  falha {model} slot{(idx+ki)%len(keys)+1}: {str(exc)[:140]}")

    sheet = contact_sheet(written)
    if sheet:
        report.append({"comparacao": str(sheet)})
        print(f"COMPARACAO -> {sheet}")

    (HERE / "misuki_linda_v25_report.json").write_text(
        json.dumps({"prompt": build_prompt(VARIANTS[0]["shot"]), "aspecto": ASPECT,
                    "modelos": MODEL_CHAIN, "resultados": report},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps([r for r in report if "erro" not in r], ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())