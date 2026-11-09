#!/usr/bin/env python3
"""render_misuki_linda_v24.py — Misuki "mais linda": melhoria pesada de rosto e cabelo.

Rota neural real (FLUX via endpoint Pollinations, a mesma já usada no telefone).
DNA travado (MISUKI_RUNTIME_MEMORY_V4):
  HC01 dois chifres | HC02 cabelo preto muito longo | HC03 gótico | HC04 adulto (sem chibi)
  HC05 separação tonal | HC06 franja deixa os olhos visíveis | HC07 sem "pente de listras"
  HC08 acessórios góticos preservados
Alvo do pedido: rosto mais bonito, boca e nariz naturais, cabelo reconstruído em massa.
"""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

W, H = 1024, 1536
MODEL = "flux"

HERE = Path(__file__).resolve().parent
OUT_DIRS = [HERE / "gallery_misuki"]
for extra in (Path("/storage/emulated/0/Download"), Path.home() / "Download"):
    try:
        extra.mkdir(parents=True, exist_ok=True)
        if extra not in OUT_DIRS:
            OUT_DIRS.append(extra)
    except OSError:
        pass

FACE = (
    "extremely beautiful adult anime woman, elegant adult proportions, refined tapered jaw, "
    "soft chin, natural small delicate nose with subtle bridge and soft nostril shading, "
    "naturally shaped small lips with a gentle cupid's bow and natural rosy vermilion gradient, "
    "no heavy lipstick, no exaggerated mouth, luminous porcelain skin with soft subsurface glow and light blush, "
    "large expressive almond eyes, glossy dark crimson-red irises with several small catchlights, "
    "defined upper eyelid crease, long lashes, naturally tapered elegant eyebrows"
)

HAIR = (
    "extremely long jet-black silky hair built from a few large flowing lock masses, three to seven major "
    "fringe locks, layered face-framing bangs that leave both eyes fully visible, hair volume at the crown, "
    "glossy individually painted strands with fine ribbon highlights, no comb-like field of parallel stripes, "
    "no roof-shaped or flat hair top"
)

HORNS = (
    "exactly two glossy black keratin horns rooted at the upper-lateral hairline, sweeping outward then curving "
    "upward, thick base tapering to sharp tips, subtle groove texture, catching the rim light"
)

OUTFIT = (
    "elegant black gothic garment with fine lace trim, slender straps and small buckles, a choker with a tiny "
    "pentagram pendant, sparse jewel accents, dark elegant silhouette"
)

STYLE = (
    "cinematic single-direction rim light separating the black hair and horns from the background, moody dark "
    "atmospheric background with soft bokeh and low contrast behind the face, monochrome black-and-white tonal "
    "scheme with red present only in the irises, ultra detailed clean line art, smooth gradient shading, "
    "masterpiece illustration, trending on ArtStation, 8k"
)

NEGATIVE = (
    "no text, no watermark, no logo, no signature, no chibi, no childlike proportions, no blonde hair, "
    "no blue eyes, no candy-stripe hair, no extra fingers, no deformed hands, no distorted face, "
    "no busy high-contrast background behind the face"
)

VARIANTS = [
    {"name": "misuki_linda_v24_a", "seed": 418073, "shot":
        "upper-body front portrait, shoulders open, direct confident gaze into the camera, "
        "a few loose locks crossing one shoulder"},
    {"name": "misuki_linda_v24_b", "seed": 902551, "shot":
        "three-quarter portrait, chin slightly lowered, one large lock sweeping across the shoulder, "
        "soft introspective look"},
    {"name": "misuki_linda_v24_c", "seed": 630148, "shot":
        "close beauty portrait, head slightly tilted, both eyes fully visible through the layered fringe, "
        "intense direct stare"},
]


def build_prompt(shot: str) -> str:
    parts = [
        "breathtaking masterpiece semirealistic anime illustration of Misuki, a demon girl named Misuki",
        shot,
        FACE,
        HAIR,
        HORNS,
        OUTFIT,
        STYLE,
        NEGATIVE,
    ]
    return ", ".join(p.strip().strip(",") for p in parts)


def _fetch_once(prompt: str, seed: int) -> bytes:
    query = urllib.parse.urlencode({
        "width": W, "height": H, "model": MODEL, "nologo": "true",
        "seed": seed, "enhance": "true",
    })
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt) + "?" + query
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Android; Termux; BLACKCORE Paint Studio)",
        "Accept": "image/*,*/*",
    })
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = resp.read()
    if not data or len(data) < 5000:
        raise RuntimeError(f"resposta suspeita do servidor ({len(data)} bytes)")
    return data


def fetch(prompt: str, seed: int, attempts: int = 7, wait: int = 25) -> bytes:
    """A cota gratuita do endpoint é por janela de tempo; insiste com espera."""
    last: Exception | None = None
    for i in range(1, attempts + 1):
        try:
            return _fetch_once(prompt, seed)
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (402, 429) and i < attempts:
                pause = wait * i
                print(f"  cota ocupada (HTTP {exc.code}) tentativa {i}/{attempts}, aguardando {pause}s...")
                time.sleep(pause)
                continue
            raise
        except Exception as exc:  # noqa: BLE001
            last = exc
            if i < attempts:
                time.sleep(wait)
                continue
            raise
    raise last if last else RuntimeError("falha desconhecida")


def finish(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Sharpness(img).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    return img.filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=3))


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
            im.thumbnail((512, 768), Image.Resampling.LANCZOS)
            thumbs.append(im)
        except OSError:
            continue
    if not thumbs:
        return None
    w = sum(t.width for t in thumbs) + 16 * (len(thumbs) + 1)
    h = max(t.height for t in thumbs) + 32
    sheet = Image.new("RGB", (w, h), (10, 10, 12))
    x = 16
    for t in thumbs:
        sheet.paste(t, (x, 16))
        x += t.width + 16
    out = OUT_DIRS[0] / "misuki_linda_v24_COMPARACAO.png"
    sheet.save(out, "PNG", optimize=True)
    return out


def main() -> int:
    OUT_DIRS[0].mkdir(parents=True, exist_ok=True)
    ok = 0
    report = []
    written: list[Path] = []
    for v in VARIANTS:
        t0 = time.time()
        prompt = build_prompt(v["shot"])
        try:
            raw = fetch(prompt, v["seed"])
            img = finish(Image.open(io.BytesIO(raw)).convert("RGB"))
            fname = f"{v['name']}.png"
            saved = save_all(img, fname)
            if saved:
                written.append(Path(saved[0]))
            ok += 1
            report.append({"arquivo": fname, "dim": list(img.size),
                           "kb": round(Path(saved[0]).stat().st_size / 1024, 1) if saved else 0,
                           "segundos": round(time.time() - t0, 1), "salvos": saved})
            print(f"OK {fname} {img.size[0]}x{img.size[1]} em {time.time()-t0:.1f}s -> {saved[0] if saved else '?'}")
        except Exception as exc:  # noqa: BLE001
            report.append({"arquivo": v["name"], "erro": str(exc)[:300]})
            print(f"FALHA {v['name']}: {exc}")

    sheet = contact_sheet(written)
    if sheet:
        report.append({"comparacao": str(sheet)})

    (HERE / "misuki_linda_v24_report.json").write_text(
        json.dumps({"prompt": build_prompt(VARIANTS[0]['shot']), "resultados": report},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())