"""Small optional Termux integrations shared by the local renderers."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def scan_media(image_path: str | Path) -> bool:
    """Ask Android's media indexer to notice a saved image when available."""
    scanner = shutil.which('termux-media-scan')
    if not scanner:
        return False
    try:
        result = subprocess.run([scanner, str(image_path)], capture_output=True, check=False, timeout=10)
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def output_dir() -> Path:
    """Writable destination, including phones without storage permission."""
    configured = os.environ.get('PAINT_OUTPUT_DIR')
    choices = [Path(configured).expanduser()] if configured else [Path('/storage/emulated/0/Download'), Path(__file__).resolve().parent / 'gallery']
    for folder in choices:
        try:
            folder.mkdir(parents=True, exist_ok=True)
            if os.access(folder, os.W_OK):
                return folder
        except OSError:
            pass
    raise OSError('Pasta de saída sem permissão de escrita.')
