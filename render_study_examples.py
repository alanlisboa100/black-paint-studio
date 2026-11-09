#!/usr/bin/env python3
"""Three deterministic CPU-painted environment studies for Black Paint Studio."""
from __future__ import annotations

import argparse, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from painting_methods import directional_brushstrokes

W,H=900,1350

def mix(a,b,t): return tuple(round(x+(y-x)*t) for x,y in zip(a,b))

def gradient(top,bottom):
    im=Image.new('RGB',(W,H)); d=ImageDraw.Draw(im)
    for y in range(H): d.line((0,y,W,y),fill=mix(top,bottom,y/(H-1)))
    return im.convert('RGBA')

def glow(canvas,xy,radius,color,opacity=150):
    layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer)
    x,y=xy
    for r in range(radius,0,-max(2,radius//28)):
        t=1-r/radius; a=round(opacity*t*t*.55)
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*color,a))
    layer=layer.filter(ImageFilter.GaussianBlur(max(2,radius*.16)))
    return Image.alpha_composite(canvas,layer)

def curve(draw,points,fill,width=3,steps=30):
    p0,p1,p2,p3=points; out=[]
    for i in range(steps+1):
        t=i/steps; u=1-t
        out.append((u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0],u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]))
    draw.line(out,fill=fill,width=width,joint='curve')

def grain(image,seed=1,amount=7):
    rng=random.Random(seed); pix=image.load()
    # Quiet canvas tooth: fine, low-amplitude grain, never large blotches.
    for y in range(0,H,2):
        for x in range(0,W,2):
            if rng.random()<.38:
                r,g,b,a=pix[x,y]; n=rng.randint(-amount,amount)
                col=(max(0,min(255,r+n)),max(0,min(255,g+n)),max(0,min(255,b+n)),a)
                pix[x,y]=col; pix[min(W-1,x+1),y]=col; pix[x,min(H-1,y+1)]=col
    return image

def shrine(seed=21):
    rng=random.Random(seed); im=gradient((15,18,45),(185,83,87));
    im=glow(im,(455,354),300,(255,177,123),115); d=ImageDraw.Draw(im,'RGBA')
    # Moon and distant mountain layers
    d.ellipse((315,218,585,488),fill=(255,224,190,238))
    d.polygon([(0,650),(120,488),(225,590),(344,430),(490,615),(655,470),(900,632),(900,890),(0,890)],fill=(44,40,67,255))
    d.polygon([(0,738),(172,578),(302,696),(457,545),(622,704),(760,575),(900,709),(900,964),(0,964)],fill=(25,33,53,255))
    # Water horizon and long quiet reflections
    d.rectangle((0,750,W,H),fill=(15,26,43,255))
    # Warm moon path and cool water sheen are broad, low-opacity glazes.
    glaze=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glaze,'RGBA')
    for j in range(42):
        y=770+j*13; spread=8+int(j*1.35); alpha=max(5,42-j)
        gd.line((455-spread,y,455+spread,y),fill=(255,174,135,alpha),width=1+(j%3))
    glaze=glaze.filter(ImageFilter.GaussianBlur(9)); im=Image.alpha_composite(im,glaze); d=ImageDraw.Draw(im,'RGBA')
    for i in range(70):
        y=rng.randint(775,1270); cx=rng.randint(150,750); length=rng.randint(8,130)
        col=rng.choice([(245,169,131,rng.randint(18,75)),(207,132,154,rng.randint(14,55)),(120,158,181,rng.randint(12,45))])
        d.line((cx-length//2,y,cx+length//2,y+rng.randint(-2,2)),fill=col,width=rng.choice([1,2,3]))
    # A few reed silhouettes give the water foreground a near plane.
    for side in (-1,1):
        base_x=24 if side<0 else W-24
        for j in range(13):
            x=base_x+side*rng.randint(0,115); y=H-rng.randint(0,90)
            curve(d,((x,y),(x+side*8,y-36),(x-side*4,y-72),(x+side*rng.randint(-25,25),y-126)),(24,45,52,220),2)
            d.ellipse((x-3,y-7,x+3,y-1),fill=(232,128,118,190))
    # Torii gate with layered red lacquer and fine warm rim
    red=(116,31,54,255); hi=(207,87,91,255)
    d.polygon([(198,500),(706,500),(754,530),(175,530)],fill=red)
    d.rectangle((230,514,256,832),fill=red); d.rectangle((646,514,672,832),fill=red)
    d.line((231,520,231,820),fill=hi,width=3); d.line((647,520,647,820),fill=hi,width=3)
    d.polygon([(220,573),(683,573),(683,592),(220,592)],fill=(87,28,48,255))
    # Small shrine silhouette and lanterns
    d.polygon([(378,695),(450,637),(522,695),(510,711),(390,711)],fill=(20,24,39,255))
    d.rectangle((398,709,502,785),fill=(18,23,36,255)); d.polygon([(388,710),(512,710),(500,721),(400,721)],fill=(202,101,89,255))
    for x in (142,759):
        im=glow(im,(x,742),70,(255,166,99),65); d=ImageDraw.Draw(im,'RGBA')
        d.rectangle((x-15,716,x+15,776),fill=(102,54,60,255),outline=(236,171,117,230),width=2)
        d.polygon([(x-20,716),(x,700),(x+20,716)],fill=(44,36,51,255)); d.rectangle((x-8,732,x+8,753),fill=(255,201,134,220))
    # Branches and restrained blossoms frame, rather than cover, the scene
    for side in (-1,1):
        ox=0 if side<0 else W
        curve(d,((ox,190),(ox+side*160,240),(ox+side*205,380),(ox+side*275,460)),(27,28,47,255),12)
        for j in range(22):
            x=rng.randint(20,210) if side<0 else rng.randint(690,880); y=rng.randint(220,485)
            r=rng.randint(2,5); d.ellipse((x-r,y-r,x+r,y+r),fill=rng.choice([(246,161,176,220),(255,202,184,210),(213,116,154,210)]))
    # Warm, broken reflections follow the water plane instead of forming a uniform grid.
    im=directional_brushstrokes(im,[
        ([(421,804),(468,808),(492,806)],(255,196,157),12,.18),
        ([(395,894),(445,899),(481,896)],(225,160,167),8,.22),
        ([(365,1018),(431,1022),(496,1017)],(144,184,196),6,.20),
        ([(346,1132),(426,1136),(512,1130)],(255,187,145),5,.17),
    ],seed+11)
    return grain(im,seed)

def city(seed=42):
    """Use the reviewed street composition in the editor and CLI as well."""
    from render_academy_results import city as paint_city
    return paint_city()

def house(seed=42):
    from render_academy_results import house as paint_house
    return paint_house()

def fruit(seed=42):
    from render_academy_results import still_life
    return still_life()

def cathedral(seed=77):
    rng=random.Random(seed); im=gradient((12,11,31),(55,20,46)); im=glow(im,(450,420),360,(205,34,63),105); d=ImageDraw.Draw(im,'RGBA')
    # Blood moon partially framed by distant gothic architecture
    d.ellipse((306,254,594,542),fill=(154,28,52,245),outline=(244,94,95,220),width=5)
    d.ellipse((354,302,546,494),fill=(193,55,67,90))
    # Nave floor and central aisle
    d.rectangle((0,890,W,H),fill=(14,12,24,255))
    d.polygon([(374,900),(526,900),(790,H),(110,H)],fill=(35,18,33,255))
    for i in range(12):
        y=930+i*i*3
        d.line((0,y,W,y),fill=(95,42,54,max(10,80-i*5)),width=2)
    # Repeating pointed arches, layered for depth
    for idx,(cx,base,span,col) in enumerate([(450,1000,660,(31,20,37,255)),(450,890,520,(39,24,43,255)),(450,770,382,(51,29,48,255))]):
        top=base-span*1.16
        d.polygon([(cx-span,base),(cx-span,top+span*.48),(cx,top),(cx+span,top+span*.48),(cx+span,base)],fill=col)
        inner=span*.84; itop=top+span*.16
        d.polygon([(cx-inner,base),(cx-inner,itop+inner*.51),(cx,itop),(cx+inner,itop+inner*.51),(cx+inner,base)],fill=(16,14,30,255))
        d.line((cx-span,base,cx-span,top+span*.48,cx,top,cx+span,top+span*.48,cx+span,base),fill=(126,55,73,220),width=max(2,7-idx*2),joint='curve')
    # Stained glass rose window
    cx,cy=450,652
    for r,col in [(105,(59,31,70,255)),(78,(117,35,64,255)),(49,(218,89,78,255)),(18,(255,186,115,255))]:
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=col,outline=(220,141,124,220),width=3)
    for a in range(0,360,45):
        rad=math.radians(a); d.line((cx,cy,cx+100*math.cos(rad),cy+100*math.sin(rad)),fill=(226,153,141,185),width=3)
    # Candle stands and warm pools of light
    for x,y in [(130,980),(770,980),(265,860),(635,860)]:
        im=glow(im,(x,y-18),65,(255,157,83),65); d=ImageDraw.Draw(im,'RGBA')
        d.rectangle((x-8,y-8,x+8,y+45),fill=(201,179,146,255)); d.ellipse((x-5,y-33,x+5,y-10),fill=(255,206,133,250))
        d.line((x,y-28,x,y-8),fill=(255,243,190,255),width=2)
    # Low pews and stone inlays add scale and a usable foreground perspective.
    for side in (-1,1):
        for j in range(4):
            y=930+j*84; half=130+j*58
            x=450+side*(225+j*18)
            d.polygon([(x-half*.35,y),(x+half*.35,y),(x+half*.48,y+17),(x-half*.48,y+17)],fill=(35,22,35,235))
            d.line((x-half*.35,y,x+half*.35,y),fill=(119,65,73,180),width=2)
    for j in range(17):
        y=1045+j*18; half=15+j*11
        d.line((450-half,y,450+half,y),fill=(113,57,68,max(8,58-j*2)),width=1)
    # Broken vertical highlights reinforce the stone columns and warm focal lights.
    im=directional_brushstrokes(im,[
        ([(235,510),(231,585),(237,656)],(173,102,111),7,.18),
        ([(672,502),(678,576),(671,642)],(182,99,108),7,.16),
        ([(438,914),(442,956),(438,992)],(255,174,103),5,.22),
        ([(472,916),(468,956),(474,990)],(243,141,113),4,.18),
    ],seed+23)
    return grain(im,seed+5)

def main():
    p=argparse.ArgumentParser(description='Gera cinco estudos originais locais em CPU com Pillow.')
    p.add_argument('--output-dir',type=Path,default=Path('gallery')); p.add_argument('--seed',type=int,default=20260924)
    p.add_argument('--study',choices=['all','shrine','city','cathedral','house','fruit'],default='all')
    a=p.parse_args(); a.output_dir.expanduser().mkdir(parents=True,exist_ok=True)
    jobs={'shrine':('01_santuario_da_lua.png',shrine),'city':('02_avenida_neon_chuvosa.png',city),
          'cathedral':('03_catedral_do_eclipse.png',cathedral),
          'house':('04_casa_no_jardim.png',house),'fruit':('05_natureza_morta_frutas.png',fruit)}
    selected=list(jobs.items()) if a.study=='all' else [(a.study,jobs[a.study])]
    for i,(kind,(name,fn)) in enumerate(selected):
        image=fn(a.seed+i*101).convert('RGB'); image=ImageEnhance.Contrast(image).enhance(1.04)
        image.save(a.output_dir.expanduser()/name,'PNG',optimize=False)
        print(a.output_dir.expanduser()/name)

if __name__=='__main__': main()
