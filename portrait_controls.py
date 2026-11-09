"""Validated controls for a frontal portrait; no free-form prompt interpreter."""
import math
import json
from pathlib import Path

PRESETS = {
    'neutral': {},
    'soft': {'eye_open': .87, 'mouth_curve': .42, 'brow_tilt': .08},
    'happy': {'eye_open': .76, 'mouth_curve': .85, 'mouth_open': .18, 'brow_tilt': .12},
    'sad': {'eye_open': .85, 'mouth_curve': -.65, 'brow_tilt': -.75},
    'angry': {'eye_open': .68, 'eye_tilt': .32, 'mouth_curve': -.25, 'brow_tilt': .9},
    'surprised': {'eye_open': 1.3, 'iris_size': .86, 'mouth_width': .78, 'mouth_open': .85, 'brow_tilt': -.15},
}
LIMITS = {
    'eye_open': (.5, 1.4, 1), 'eye_width': (.8, 1.15, 1),
    'eye_tilt': (-.6, .6, 0), 'iris_size': (.75, 1.15, 1),
    'pupil_size': (.18, .36, .25), 'gaze_x': (-1, 1, 0), 'gaze_y': (-1, 1, 0),
    'mouth_width': (.7, 1.4, 1), 'mouth_curve': (-1, 1, 0),
    'mouth_open': (0, 1, 0), 'lip_fullness': (.6, 1.4, 1),
    'brow_tilt': (-1, 1, 0), 'hair_shine': (.3, 1.3, 1),
    'hair_wave': (0, 2, 1), 'cloth_fold': (.4, 1.5, 1),
}


def normalize_options(options=None, expression=None):
    if options is None: options = {}
    if not isinstance(options, dict): raise ValueError('Ajustes devem ser um objeto JSON')
    unknown = set(options) - set(LIMITS) - {'expression', 'cloth_material'}
    if unknown: raise ValueError('Ajustes desconhecidos: ' + ', '.join(sorted(unknown)))
    expression = expression if expression is not None else options.get('expression', 'neutral')
    if not isinstance(expression, str) or expression not in PRESETS:
        raise ValueError('Expressão inválida')
    result = {name: bounds[2] for name, bounds in LIMITS.items()}
    result.update(PRESETS[expression])
    result.update({key: value for key, value in options.items() if key in LIMITS})
    for key, (low, high, _) in LIMITS.items():
        value = result[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f'{key} deve estar entre {low} e {high}')
    material = options.get('cloth_material', 'velvet')
    if material not in ('velvet', 'satin'): raise ValueError('Tecido deve ser velvet ou satin')
    result.update(expression=expression, cloth_material=material)
    return result


def load_settings(path):
    if not path:return None
    target=Path(path).expanduser()
    if target.stat().st_size>32768:raise ValueError('Arquivo de ajustes excede 32 KiB')
    options=json.loads(target.read_text(encoding='utf-8'))
    normalize_options(options)
    return options
