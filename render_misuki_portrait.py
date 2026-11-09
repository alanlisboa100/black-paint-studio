#!/usr/bin/env python3
"""Retrato natural procedural da Misuki, com motor vetorial legado opcional.
Não interpreta novas referências nem aprende; a geração aberta usa BlackCore.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from render_neural_plan import render_plan
from portrait_controls import PRESETS, load_settings

ROOT = Path(__file__).resolve().parent

def build_plan():
    plan = json.loads((ROOT / 'neural_plan_S2.json').read_text(encoding='utf-8'))
    card = json.loads((ROOT / 'misuki.json').read_text(encoding='utf-8'))
    palette = card['palette']
    plan['background'] = '#111018'
    plan['title'] = card['name'] + ' — estudo frontal local'
    # Scene values and hair accents follow the character card, instead of pink streaks.
    for index, element in enumerate(plan['elements']):
        if index <= 24:
            if element.get('fill') != 'none': element['fill'] = '#555060'
            if element.get('stroke') != 'none': element['stroke'] = '#797080'
            element['opacity'] = min(element.get('opacity',1), .14)
        if index in (75,78): element['fill'] = '#24232D'
        if index in (76,79): element['fill'] = '#383641'
        if index in (82,83,84,85,88,94): element['fill'] = '#282530'
        if index in (86,87,89,109,110): element['stroke'] = '#47424E'
        if index in (50,51): element['opacity'] = .12
        if index in (63,64): element['fill'] = palette['vermelhoIris']
        if index in (65,66): element['fill'] = palette['vermelhoAcento']
    def path(d,fill,stroke='none',width=1,opacity=1):
        return {'path':d,'fill':fill,'stroke':stroke,'strokeWidth':width,'opacity':opacity,'brush':'flat'}
    horns = [
        path('M 334 165 C 304 128 252 96 261 8 C 275 59 304 84 353 110 C 371 123 367 151 334 165 Z', '#08080B','#39343F',1.8),
        path('M 666 165 C 696 128 748 96 739 8 C 725 59 696 84 647 110 C 629 123 633 151 666 165 Z', '#08080B','#39343F',1.8),
        path('M 268 34 C 278 80 310 101 349 123 C 356 129 351 143 342 149 C 335 120 285 105 268 34 Z','#25212B',opacity=.65),
        path('M 732 34 C 722 80 690 101 651 123 C 644 129 649 143 658 149 C 665 120 715 105 732 34 Z','#25212B',opacity=.65),
        path('M 288 86 L 306 74 M 303 109 L 324 95 M 324 131 L 345 116','none','#403845',1.2,.6),
        path('M 712 86 L 694 74 M 697 109 L 676 95 M 676 131 L 655 116','none','#403845',1.2,.6),
    ]
    plan['elements'].extend(horns)
    return plan

def render(width=900, checkpoint_dir=None, quality='standard', seed=7331, background='paper', engine='natural', options=None, expression=None):
    if engine == 'vector':
        if options or expression:raise ValueError('Ajustes de expressão exigem o motor natural')
        image, _ = render_plan(build_plan(), width, checkpoint_dir)
        return image
    if engine != 'natural': raise ValueError('Motor deve ser natural ou vector')
    from natural_portrait_engine import render_natural
    card = json.loads((ROOT / 'misuki.json').read_text(encoding='utf-8'))
    image, _ = render_natural(card,width,quality,seed,background,checkpoint_dir,options,expression)
    return image

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='misuki_portrait.png')
    parser.add_argument('--width',type=int,default=900)
    parser.add_argument('--checkpoint-dir')
    parser.add_argument('--quality',choices=('economy','standard'),default='standard')
    parser.add_argument('--background',choices=('paper','night'),default='paper')
    parser.add_argument('--engine',choices=('natural','vector'),default='natural')
    parser.add_argument('--seed',type=int,default=7331)
    parser.add_argument('--expression',choices=tuple(PRESETS))
    parser.add_argument('--settings',help='Arquivo JSON de controles validados')
    args=parser.parse_args()
    try:
        image=render(args.width,args.checkpoint_dir,args.quality,args.seed,args.background,args.engine,load_settings(args.settings),args.expression)
    except (ValueError,OSError) as error:parser.error(str(error))
    target=Path(args.output).expanduser();target.parent.mkdir(parents=True,exist_ok=True)
    image.save(target,'PNG',optimize=True)
    print(target)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
