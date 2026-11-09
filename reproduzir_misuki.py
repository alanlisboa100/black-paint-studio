#!/usr/bin/env python3
"""Reproduz o retrato natural, etapas e relatório; não atribui nota artística.

Os arquivos de demonstração nomeados na pasta de saída são substituídos.
"""
import argparse
import json
import platform
import resource
import time
from pathlib import Path
from PIL import Image, ImageDraw
from natural_portrait_engine import render_natural
from portrait_controls import PRESETS, load_settings

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', default='gallery/reproducao_misuki')
    parser.add_argument('--width', type=int, default=900)
    parser.add_argument('--quality', choices=('economy', 'standard'), default='standard')
    parser.add_argument('--seed', type=int, default=7331)
    parser.add_argument('--background', choices=('paper', 'night'), default='paper')
    parser.add_argument('--expression', choices=tuple(PRESETS))
    parser.add_argument('--settings')
    args = parser.parse_args()
    folder = Path(args.output_dir).expanduser()
    card = json.loads((ROOT / 'misuki.json').read_text(encoding='utf-8'))
    start = time.perf_counter()
    image, report = render_natural(card, args.width, args.quality, args.seed,
                                   args.background, folder / 'etapas',load_settings(args.settings),args.expression)
    image.save(folder / 'misuki_natural.png', optimize=True)
    report['seconds_render_checkpoints_and_save'] = round(time.perf_counter() - start, 3)
    report['execution_environment'] = {'system': platform.system(),
                                     'machine': platform.machine(),
                                     'python': platform.python_version()}
    if platform.system() == 'Linux':
        report['peak_process_rss_mib'] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    report['measurement_scope'] = 'Este processo Python; não inclui editor/navegador nem julga qualidade artística.'
    (folder / 'relatorio.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    previous = ROOT / 'exemplos_misuki_v21' / 'misuki_natural.png'
    if previous.is_file():
        with Image.open(previous) as old:
            old = old.convert('RGB').resize(image.size, Image.Resampling.LANCZOS)
        comparison = Image.new('RGB', (image.width * 2, image.height + 32), (250, 247, 248))
        comparison.paste(old, (0, 32)); comparison.paste(image, (image.width, 32))
        draw = ImageDraw.Draw(comparison)
        draw.text((12, 9), '2.1.0 - anterior', fill=(35, 28, 42))
        draw.text((image.width + 12, 9), '2.3.0 - revisao', fill=(35, 28, 42))
        comparison.save(folder / 'comparacao.png', optimize=True)
    print(json.dumps({'output': str(folder.resolve()), 'report': report}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
