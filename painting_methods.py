"""CPU painting primitives inspired by the Black Paint Academy exercises."""
from __future__ import annotations

import math
import random
from PIL import Image, ImageDraw


def directional_brushstrokes(image: Image.Image, strokes, seed: int = 1) -> Image.Image:
    """Add restrained, tapered pigment marks that follow a form's direction.

    Each stroke is (points, RGB color, width, opacity). Uses Pillow/CPU only.
    The image stays intact underneath; marks are alpha-composited as a new pass.
    """
    base=image.convert('RGBA')
    layer=Image.new('RGBA',base.size,(0,0,0,0))
    draw=ImageDraw.Draw(layer,'RGBA')
    rng=random.Random(seed)
    for points,color,width,opacity in strokes:
        if len(points)<2 or width<=0 or opacity<=0: continue
        segments=[]
        for a,b in zip(points,points[1:]):
            length=math.hypot(b[0]-a[0],b[1]-a[1])
            count=max(2,min(24,math.ceil(length/max(4,width*.7))))
            for n in range(count):
                t=n/count
                segments.append((a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t))
        segments.append(tuple(points[-1]))
        total=max(1,len(segments)-1)
        rgba=tuple(color[:3])+(round(max(0,min(1,opacity))*255),)
        for i,(a,b) in enumerate(zip(segments,segments[1:])):
            t=(i+.5)/total
            taper=.24+.76*(math.sin(math.pi*t)**.38)
            jitter=rng.uniform(-.42,.42)*width
            nx,ny=-(b[1]-a[1]),b[0]-a[0]
            norm=max(1,math.hypot(nx,ny)); ox,oy=nx/norm*jitter,ny/norm*jitter
            p0=(round(a[0]+ox,1),round(a[1]+oy,1)); p1=(round(b[0]+ox,1),round(b[1]+oy,1))
            pen=max(1,round(width*taper))
            draw.line((p0,p1),fill=rgba,width=pen)
            radius=pen/2
            draw.ellipse((p0[0]-radius,p0[1]-radius,p0[0]+radius,p0[1]+radius),fill=rgba)
    return Image.alpha_composite(base,layer)
