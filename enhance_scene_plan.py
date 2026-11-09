#!/usr/bin/env python3
"""enhance_scene_plan.py — Aplica o GUIA MISUKI (Instruções.png) no plano neural.

Corrige a estrutura do plano S antes de rasterizar, item a item do guia:
 [4] traço limpo com variação de espessura (língua de cílio afilada)
 [6] cabelo: mechas grandes -> cinzas de volume -> brilho -> mechas soltas
 [7] olhos: pupila definida, sombra na pálpebra, simetria, íRIS VERMELHA
 [8] chifres: sombra interna + textura, separação da massa de cabelo
 [9] roupa: camadas, alças, fivelas, corrente, símbolo BLACKCORE vermelho
 [10] sombras/luz: névoa, vinheta, lua, estrelas PB sem poluir
 [+] boca: sorriso leve com dentes

FIX 4-OLHOS (causa raiz comprovada por amostragem de pixel):
 - elems 37/38: lentes pretas GROSSAS sobrepostas à esclera -> cílios afilados
 - elem 46: franja-cortina que descia a y=440 SOBRE os olhos -> recolhida
 - elem 47: mechinha central a y=435 na ponte -> sobe a y=402

Arquitetura segura: TODAS as edições por índice acontecem no índice ORIGINAL;
inserções são aplicadas em ordem DECRESCENTE de k para nenhum índice deslocar.

Uso:
    python enhance_scene_plan.py --in neural_plan_S.json --out neural_plan_S2.json
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path


def el(path, fill='none', stroke='none', sw=0, op=1.0):
    return {'path': path, 'fill': fill, 'stroke': stroke,
            'strokeWidth': sw, 'opacity': op}


def mirror(p):
    """Espelha path em x=500 por comando. Pares (x,y) viram (1000-x,y).
    H vira coordenada espelhada; Z preservado; A trata flags e inverte sweep."""
    npts = {'M': 2, 'L': 2, 'C': 6, 'Q': 4, 'T': 2, 'S': 4}
    out = []
    for mo in re.finditer(r'([MmLlHhVvCcSsQqTtZzAa])((?:[^MmLlHhVvCcSsQqTtZzAa])*)', p):
        c = mo.group(1)
        cmd = c.upper()
        nums = [float(n) for n in re.findall(r'[-+]?\d*\.?\d+', mo.group(2))]
        rep = c.islower()
        if cmd == 'Z':
            out.append(c)
            continue
        if cmd == 'A':
            vals = []
            for blk in range(0, len(nums) - 6, 7):
                rx, ry, rot, la, sw, x, y = nums[blk:blk + 7]
                if rep:
                    vals += [rx, ry, rot, la, 1 - sw, -x, y]
                else:
                    vals += [rx, ry, rot, la, 1 - sw, 1000 - x, y]
            out.append(c + ' ' + ' '.join(f'{v:g}' for v in vals))
            continue
        if cmd in npts:
            n = npts[cmd]
            vals = []
            for blk in range(0, len(nums) - n + 1, n):
                for i in range(n):
                    v = nums[blk + i]
                    if rep:
                        vals.append(-v if i % 2 == 0 else v)
                    else:
                        vals.append(1000 - v if i % 2 == 0 else v)
            out.append(c + ' ' + ' '.join(f'{v:g}' for v in vals))
            continue
        out.append(c + ' ' + ' '.join(f'{v:g}' for v in nums))  # H/V: mantém
    return ' '.join(out)


def transform(plan):
    p = copy.deepcopy(plan)
    els = p['elements']

    # ===== EDIÇÕES POR ÍNDICE ORIGINAL (antes de QUALQUER inserção) =====
    # (a) 37/38: lente preta grossa -> cílio afilado colado na linha real da pálpebra
    lash_E = ('M 380 425 C 398 404 446 400 476 418 '
              'C 478 421 474 421 470 419 '
              'C 444 406 402 410 384 427 Z')
    els[37] = el(lash_E, fill='#1A0A20', op=1.0)
    els[38] = el(mirror(lash_E), fill='#1A0A20', op=1.0)

    # (b) 46: franja-cortina sobre os olhos -> abre a janela orbital
    els[46]['path'] = ('M 320 200 C 380 130 620 130 680 200 C 680 280 640 372 622 392 '
                       'C 580 352 545 392 500 398 C 455 392 420 352 378 392 '
                       'C 360 372 320 280 320 200 Z')
    # (c) 47: mechinha central termina na ponte, não sobre a íris
    els[47]['path'] = ('M 480 170 C 470 258 462 352 474 402 '
                       'C 488 392 512 322 508 224 Z')
    # (d) íris VERMELHA (guia: "olhos vermelhos"; DNA Misuki), pupila definida
    els[29]['fill'] = '#5C1628'
    els[30]['fill'] = '#5C1628'
    els[31]['fill'] = '#A0344E'
    els[32]['fill'] = '#A0344E'
    els[33]['fill'] = '#120419'
    els[34]['fill'] = '#120419'
    # (e) catchlights: bolha branca 22x18 sobre a pupila -> brilho no canto
    els[35]['path'] = ('M 419 416 A 7 5.5 -18 1 1 418.9 415 Z '
                       'M 437 431 A 2.2 2.2 0 1 1 436.9 430 Z')
    els[36]['path'] = mirror(els[35]['path'])
    # (f) boca viva
    els[22]['fill'] = '#C4516E'
    els[24]['fill'] = '#B34563'
    # (g) chifres 48/49: sombra da base -> chifre sólido puxado
    els[48]['fill'] = '#7A2E50'
    els[49]['fill'] = '#7A2E50'

    # ===== ACÚMULOS A INSERIR =====
    hair_add = [
        el('M 360 372 C 420 344 580 344 640 372 C 620 392 560 366 500 366 '
           'C 440 366 380 392 360 372 Z', fill='#241432', op=0.5),
        el('M 344 320 C 372 240 420 200 470 190 C 430 224 398 286 382 372 '
           'C 368 356 352 340 344 320 Z', fill='#241A31', op=0.9),
        el(mirror('M 344 320 C 372 240 420 200 470 190 C 430 224 398 286 382 372 '
                  'C 368 356 352 340 344 320 Z'), fill='#241A31', op=0.9),
        el('M 300 322 C 380 258 620 258 700 322 C 620 288 380 288 300 322 Z',
           fill='#3B2A52', op=0.5),
        el('M 312 342 C 386 286 614 286 688 342 C 614 312 386 312 312 342 Z',
           fill='#7E3A6E', op=0.32),
        el('M 128 560 C 112 520 118 480 138 452', stroke='#1D1228', sw=3, op=0.7),
        el('M 872 560 C 888 520 882 480 862 452', stroke='#1D1228', sw=3, op=0.7),
        el('M 396 196 C 390 268 398 330 390 390', stroke='#241631', sw=2, op=0.55),
        el('M 604 196 C 610 268 602 330 610 390', stroke='#241631', sw=2, op=0.55),
        el('M 494 188 C 492 238 500 280 496 318', stroke='#2A1A38', sw=2, op=0.5),
    ]

    horn_add = [
        el('M 402 376 C 408 320 418 262 429 224 C 424 274 416 330 412 378 Z',
           fill='#5F2E47', op=0.55),
        el('M 598 376 C 592 320 582 262 571 224 C 576 274 584 330 588 378 Z',
           fill='#5F2E47', op=0.55),
        el('M 404 300 C 412 296 424 296 430 300', stroke='#8A4268', sw=1.5, op=0.5),
        el('M 570 300 C 582 296 594 296 598 300', stroke='#8A4268', sw=1.5, op=0.5),
    ]

    mouth_add = [
        el('M 478 571 C 492 575 510 575 522 571 C 512 580 488 580 478 571 Z',
           fill='#FCF7F7', op=0.92),
        el('M 478 571 C 492 575 510 575 522 571', stroke='#7E2740', sw=1.5, op=0.6),
    ]

    outfit = [
        el('M 440 745 C 448 726 460 716 500 714 C 540 716 552 726 560 745 '
           'L 556 850 C 528 866 472 866 444 850 Z', fill='#20162B', op=1.0),
        el('M 452 736 C 470 726 486 723 500 723', stroke='#4E3A5E', sw=2, op=0.55),
        el('M 452 718 L 470 692 L 480 696 L 462 724 Z', fill='#171021'),
        el('M 548 718 L 530 692 L 520 696 L 538 724 Z', fill='#171021'),
        el('M 446 762 L 466 758 L 468 774 L 448 778 Z', fill='#8E8698'),
        el('M 450 764 L 463 761 L 464 771 L 452 774 Z', fill='#C9C3D2'),
        el('M 554 762 L 534 758 L 532 774 L 552 778 Z', fill='#8E8698'),
        el('M 550 764 L 537 761 L 536 771 L 548 774 Z', fill='#C9C3D2'),
        el('M 468 790 C 488 802 512 802 532 790', stroke='#9A93A6', sw=2.5, op=0.85),
        el('M 472 794 C 490 804 510 804 528 794', stroke='#D9D3E2', sw=1, op=0.6),
        el('M 448 650 C 472 660 528 660 552 650 L 552 668 C 528 678 472 678 448 668 Z',
           fill='#120B18'),
        el('M 480 655 L 486 665 L 494 651 L 500 668 L 506 651 L 514 665 L 520 655 '
           'L 514 660 L 507 654 L 500 662 L 493 654 L 486 660 Z',
           fill='#D0243F', op=0.95),
    ]

    bg_add = [
        el('M 0 130 C 300 70 700 70 1000 130 C 700 150 300 150 0 130 Z',
           fill='#E3DBEC', op=0.35),
        el('M 0 980 C 250 950 750 950 1000 980 L 1000 1097 L 0 1097 Z',
           fill='#E8E2F0', op=0.4),
        el('M 790 130 A 90 90 0 1 1 789.9 129.9 Z', fill='#F4EFF7', op=0.9),
        el('M 764 116 A 26 26 0 1 1 763.9 115.9 Z', fill='#E3D9E8', op=0.55),
        el('M 818 162 A 14 14 0 1 1 817.9 161.9 Z', fill='#E3D9E8', op=0.45),
    ]
    stars = []
    for (x, y, r, o) in [(170, 300, 2.4, .9), (240, 150, 2.0, .8), (75, 520, 2.2, .8),
                         (925, 480, 2.2, .85), (830, 300, 2.6, .9), (940, 700, 2.0, .7),
                         (60, 780, 1.8, .6), (905, 620, 2.0, .75), (300, 120, 1.8, .7),
                         (700, 430, 1.8, .6), (122, 432, 2.2, .8), (500, 60, 2.0, .8)]:
        stars.append(el(f'M {x} {y} A {r} {r} 0 1 1 {x - 0.1:.1f} {y} Z',
                        fill='#F7F4FA', op=o))
    for (x, y, s) in [(860, 380, 16), (150, 130, 14), (930, 760, 12)]:
        stars.append(el(f'M {x} {y - s} L {x} {y + s} M {x - s} {y} L {x + s} {y} '
                        f'M {x - s * .6:.1f} {y - s * .6:.1f} L {x + s * .6:.1f} {y + s * .6:.1f} '
                        f'M {x - s * .6:.1f} {y + s * .6:.1f} L {x + s * .6:.1f} {y - s * .6:.1f}',
                        stroke='#F2EDF7', sw=1.5, op=0.85))

    # ===== INSERÇÕES EM ORDEM DECRESCENTE -> índices originais estáveis =====
    new = list(els)
    for k, add in ((51, hair_add), (49, horn_add), (23, mouth_add),
                   (13, outfit), (4, bg_add + stars)):
        new = new[:k + 1] + add + new[k + 1:]
    p['elements'] = new
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    plan = json.load(open(args.inp, encoding='utf-8'))
    new = transform(plan)
    assert 1 <= len(new['elements']) <= 240, \
        f'elementos demais: {len(new["elements"])}'
    Path(args.out).write_text(json.dumps(new, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'in': args.inp, 'out': args.out,
                      'antes': len(plan['elements']),
                      'depois': len(new['elements'])}, ensure_ascii=False))


if __name__ == '__main__':
    main()
