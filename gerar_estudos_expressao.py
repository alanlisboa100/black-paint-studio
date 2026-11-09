#!/usr/bin/env python3
"""Gera seis expressões reais e recortes comparáveis; substitui exemplos nomeados."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from natural_portrait_engine import render_natural
from portrait_controls import PRESETS

ROOT=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',default='gallery/estudos_expressao')
    args=parser.parse_args();folder=Path(args.output_dir).expanduser();folder.mkdir(parents=True,exist_ok=True)
    card=json.loads((ROOT/'misuki.json').read_text(encoding='utf-8'))
    options=json.loads((ROOT/'presets/velvet.json').read_text())
    labels={'neutral':'Neutra','soft':'Sorriso suave','happy':'Alegre','sad':'Triste','angry':'Irritada','surprised':'Surpresa'}
    sheet=Image.new('RGB',(960,760),(250,247,248));draw=ImageDraw.Draw(sheet)
    try:font=ImageFont.truetype('DejaVuSans.ttf',19)
    except OSError:font=ImageFont.load_default()
    reports=[]
    for index,expression in enumerate(PRESETS):
        image,report=render_natural(card,450,'standard',options=options,expression=expression)
        image.save(folder/(expression+'.png'),optimize=True)
        # Identical normalized crop, not a generated substitute for the render.
        crop=image.crop((142,190,322,390)).resize((288,320),Image.Resampling.LANCZOS)
        x=16+(index%3)*320;y=38+(index//3)*380
        sheet.paste(crop,(x,y));draw.text((x,y-27),labels[expression],fill=(42,31,48),font=font)
        reports.append(report)
    sheet.save(folder/'expressoes.png',optimize=True)
    (folder/'controles_aplicados.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(folder.resolve())


if __name__=='__main__':main()
