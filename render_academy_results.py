#!/usr/bin/env python3
"""Four reproducible CPU/Pillow composition studies for the academy.

Each image is constructed from new shapes and paint marks, without tracing an
input image or asking a remote model to generate the result.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
import math, random, os
W,H=900,1200

def gradient(top,bottom):
    im=Image.new('RGB',(W,H)); p=im.load()
    for y in range(H):
        t=y/(H-1); c=tuple(round(a+(b-a)*t) for a,b in zip(top,bottom))
        for x in range(W): p[x,y]=c
    return im.convert('RGBA')

def glow(im,xy,r,color,alpha=90):
    lay=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(lay)
    for rr in range(r,0,-max(3,r//35)):
        t=1-rr/r; d.ellipse((xy[0]-rr,xy[1]-rr,xy[0]+rr,xy[1]+rr),fill=(*color,round(alpha*t*t)))
    return Image.alpha_composite(im,lay.filter(ImageFilter.GaussianBlur(r*.38)))

def curve_pts(points,steps=70):
    if len(points)!=4:
        out=[]
        for a,b in zip(points,points[1:]):
            out.extend([(a[0]+(b[0]-a[0])*i/steps,a[1]+(b[1]-a[1])*i/steps) for i in range(steps)])
        out.append(tuple(points[-1])); return out
    # cubic
    p0,p1,p2,p3=points; out=[]
    for i in range(steps+1):
        t=i/steps; u=1-t
        out.append((u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0],u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]))
    return out

def stroke(im,points,color,width,alpha=150,seed=1,texture=True):
    rng=random.Random(seed); lay=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(lay,'RGBA'); pts=curve_pts(points)
    for i,(a,b) in enumerate(zip(pts,pts[1:])):
        t=(i+.5)/(len(pts)-1); taper=.36+.64*math.sin(math.pi*t)**.38
        nx,ny=-(b[1]-a[1]),b[0]-a[0]; norm=max(1,math.hypot(nx,ny)); off=rng.uniform(-.18,.18)*width
        ox,oy=nx/norm*off,ny/norm*off; w=max(1,round(width*taper*rng.uniform(.78,1.18)))
        c=(*color,round(alpha*rng.uniform(.78,1.06)))
        p0=(round(a[0]+ox),round(a[1]+oy)); p1=(round(b[0]+ox),round(b[1]+oy))
        d.line((p0,p1),fill=c,width=w)
        if texture and i%7==0 and w>4:
            rr=max(1,w//5); d.ellipse((p0[0]-rr,p0[1]-rr,p0[0]+rr,p0[1]+rr),fill=c)
    return Image.alpha_composite(im,lay)

def dab(im,xy,rx,ry,color,alpha=130,seed=1):
    rng=random.Random(seed); lay=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(lay,'RGBA')
    x,y=xy
    for i in range(7):
        dx=rng.uniform(-rx*.55,rx*.55); dy=rng.uniform(-ry*.55,ry*.55); r=rng.uniform(.3,1)
        d.ellipse((x+dx-rx*r,y+dy-ry*r,x+dx+rx*r,y+dy+ry*r),fill=(*color,round(alpha*rng.uniform(.35,.75))) )
    return Image.alpha_composite(im,lay)

def vignette(im,amount=24):
    im=im.convert('RGB'); overlay=Image.new('L',(W,H)); p=overlay.load()
    for y in range(H):
      for x in range(W):
        dist=math.sqrt(((x-W/2)/(W*.72))**2+((y-H/2)/(H*.78))**2)
        p[x,y]=max(0,min(255,int((dist-.48)*amount*3)))
    return Image.composite(Image.new('RGB',(W,H),(8,9,16)),im,overlay).convert('RGBA')


def house():
    """Single front façade, gabled roof and a garden walk ending at the door."""
    rng=random.Random(47)
    im=gradient((74,91,119),(236,171,126))
    im=glow(im,(739,270),170,(255,207,146),90)
    clouds=Image.new('RGBA',(W,H),(0,0,0,0)); cd=ImageDraw.Draw(clouds,'RGBA')
    for cx,cy in [(218,172),(699,196)]:
        for dx,dy,rx,ry in [(-110,5,115,22),(-40,-13,102,29),(47,-5,110,22),(112,8,79,16)]:
            cd.ellipse((cx+dx-rx,cy+dy-ry,cx+dx+rx,cy+dy+ry),fill=(242,207,188,23))
    im=Image.alpha_composite(im,clouds.filter(ImageFilter.GaussianBlur(32)))
    d=ImageDraw.Draw(im,'RGBA')
    d.polygon([(0,698),(106,580),(220,650),(361,548),(490,634),(647,564),(803,650),(900,575),(900,904),(0,904)],fill=(106,112,106,255))
    d.polygon([(0,760),(140,654),(281,732),(511,624),(702,714),(900,632),(900,1200),(0,1200)],fill=(82,120,83,255))
    d.rectangle((0,804,W,H),fill=(68,108,76,255))
    # Tree silhouettes and clustered foliage: cool shadow underneath, warm light from the right.
    for tx,ty,rx,ry in [(77,586,139,186),(828,573,137,178)]:
        d.ellipse((tx-98,902,tx+54,924),fill=(35,67,54,68))
        d.polygon([(tx-8,ty+12),(tx+10,ty+12),(tx+15,916),(tx-8,916)],fill=(76,66,56,255))
        d.line((tx,ty+134,tx-50,ty+34),fill=(76,66,56,255),width=9)
        d.line((tx,ty+116,tx+55,ty-32),fill=(76,66,56,255),width=8)
        d.ellipse((tx-rx,ty-ry*.67,tx+rx,ty+ry*.69),fill=(34,74,64,255))
        for k in range(145):
            x=tx+rng.gauss(0,rx*.47); y=ty+rng.gauss(-12,ry*.37)
            if ((x-tx)/rx)**2+((y-ty)/(ry*.76))**2>.94: continue
            r=rng.randint(8,24)
            lit=(x-tx)/rx*.45-(y-ty)/ry*.25+.45
            col=(112,151,89,230) if lit>.62 else ((75,118,77,238) if lit>.35 else (42,82,66,246))
            d.ellipse((x-r,y-r*.52,x+r,y+r*.52),fill=col)
        d.arc((tx-rx+28,ty-ry*.59,tx+rx-35,ty+ry*.42),187,314,fill=(162,177,105,56),width=6)
    # Foundation runs unbroken under front wall; a soft oval sets it on the lawn.
    d.ellipse((174,798,757,895),fill=(33,58,51,112))
    d.rectangle((215,501,704,809),fill=(209,164,128,255),outline=(100,73,65,255),width=3)
    d.rectangle((203,800,718,827),fill=(116,91,76,255))
    d.line((225,520,225,794),fill=(240,202,160,133),width=5)
    # The chimney starts behind the roof and its base disappears naturally beneath the slope.
    d.polygon([(320,307),(374,307),(374,431),(320,431)],fill=(157,104,87,255))
    d.polygon([(314,301),(380,301),(386,312),(310,312)],fill=(90,68,69,255))
    for y in range(329,423,17):
        d.line((323,y,371,y),fill=(92,67,67,136),width=2)
        for x in (334+(8 if y%2 else 0),359):
            d.line((x,y-14,x,y),fill=(93,68,67,106),width=2)
    # Gable and eaves share identical base points; no disconnected roof planes.
    roof=[(185,514),(459,313),(735,514),(720,542),(459,359),(201,542)]
    d.polygon(roof,fill=(83,62,67,255),outline=(52,45,54,255),width=3)
    d.polygon([(227,511),(459,342),(695,511)],fill=(113,80,78,255))
    d.polygon([(234,495),(459,350),(681,495)],fill=(195,139,106,255))
    d.polygon([(185,514),(459,313),(735,514),(720,542),(459,359),(201,542)],outline=(54,44,52,255),width=3)
    d.line((459,315,735,516),fill=(159,111,101,255),width=5)
    for t in range(1,7):
        y=353+t*24; x0=459-(y-333)*1.29; x1=459+(y-333)*1.29
        if y<510: d.line((x0,y,x1,y),fill=(91,69,70,95),width=2)
    # Clapboard is aligned on a single front wall, leaving openings untouched.
    for y in range(553,799,22):
        d.line((228,y,692,y),fill=(144,107,91,53),width=2)
    # Attic vent sits on the gable's center axis.
    d.ellipse((435,420,483,466),fill=(66,59,60,255),outline=(231,197,154,255),width=6)
    for x in range(443,477,9): d.line((x,434,x,450),fill=(180,145,113,255),width=3)
    # Front porch is anchored at the foundation and has matching posts.
    d.polygon([(375,616),(546,616),(576,640),(347,640)],fill=(86,63,62,255))
    d.rectangle((363,641,377,804),fill=(235,207,166,255))
    d.rectangle((543,641,557,804),fill=(235,207,166,255))
    d.polygon([(344,800),(576,800),(599,829),(319,829)],fill=(147,124,99,255))
    d.rectangle((401,646,518,805),fill=(84,62,59,255),outline=(238,205,163,255),width=8)
    d.rectangle((412,654,507,801),fill=(126,82,70,255))
    d.line((457,659,457,797),fill=(77,60,58,255),width=3)
    d.ellipse((479,737,488,746),fill=(251,211,139,255))
    for x in [270,591]:
        d.rectangle((x,619,x+74,704),fill=(250,189,116,255),outline=(101,69,62,255),width=7)
        d.line((x+37,623,x+37,701),fill=(116,76,63,255),width=5)
        d.line((x+4,662,x+70,662),fill=(116,76,63,255),width=5)
        d.rectangle((x-10,706,x+84,714),fill=(142,105,84,255))
        d.rectangle((x-14,610,x-4,706),fill=(84,104,81,255));d.rectangle((x+78,610,x+88,706),fill=(84,104,81,255))
    # A winding narrow gravel footpath begins exactly below the porch step.
    walk=[(417,826),(507,826),(535,872),(540,917),(521,964),(475,1021),(438,1081),(447,1144),(481,1200),
          (115,1200),(229,1120),(311,1043),(359,971),(369,916),(386,867)]
    d.polygon(walk,fill=(151,132,105,255))
    d.line((417,826,386,867,369,916,359,971,311,1043,229,1120,115,1200),fill=(105,106,82,255),width=6,joint='curve')
    d.line((507,826,535,872,540,917,521,964,475,1021,438,1081,447,1144,481,1200),fill=(105,106,82,255),width=6,joint='curve')
    for i in range(145):
        x=rng.randint(125,525); y=rng.randint(860,1190)
        if im.getpixel((x,y))[:3] != (68,108,76): continue
        if rng.random()<.13:
            d.line((x,y,x+rng.randrange(-2,3),y-rng.randint(5,15)),fill=(105,151,93,190),width=2)
    # Distinct shrubs flank the doorway, with flowers at varied heights.
    for cx,cy in [(205,817),(285,831),(655,827),(742,818)]:
        for i in range(25):
            x=cx+rng.randint(-48,48); y=cy+rng.randint(-35,28)
            r=rng.randint(8,18)
            d.ellipse((x-r,y-r*.65,x+r,y+r*.65),fill=rng.choice([(46,91,69,230),(70,116,76,230),(104,143,77,225)]))
            if i%7==0:d.ellipse((x-4,y-9,x+4,y-2),fill=(236,169,126,250))
    return vignette(im.filter(ImageFilter.GaussianBlur(.13)))


def still_life():
    rng=random.Random(119); im=gradient((52,44,57),(173,113,85))
    im=glow(im,(680,353),255,(249,193,132),92)
    d=ImageDraw.Draw(im,'RGBA')
    d.polygon([(0,766),(900,704),(900,1200),(0,1200)],fill=(82,58,58,255))
    d.polygon([(0,852),(233,777),(416,837),(653,770),(900,862),(900,1200),(0,1200)],fill=(76,77,99,255))
    # One continuous ceramic vessel: narrow neck grows into shoulders and belly.
    d.ellipse((327,755,620,817),fill=(34,36,47,118))
    left=curve_pts([(396,316),(400,373),(390,390),(364,425)])
    left+=curve_pts([(364,425),(298,550),(326,713),(407,782)])[1:]
    base=curve_pts([(407,782),(439,811),(497,806),(533,777)])[1:]
    right=curve_pts([(533,777),(584,673),(578,520),(525,430)])[1:]
    neck=curve_pts([(525,430),(505,389),(504,352),(510,316)])[1:]
    silhouette=left+base+right+neck+[(396,316)]
    vase_mask=Image.new('L',(W,H),0); ImageDraw.Draw(vase_mask).polygon(silhouette,fill=255)
    d.polygon(silhouette,fill=(166,89,68,255),outline=(77,50,49,255),width=4)
    ceramic=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(ceramic,'RGBA')
    gd.ellipse((452,348,615,805),fill=(76,42,50,142))
    gd.ellipse((335,415,464,709),fill=(245,158,108,89))
    ceramic=ceramic.filter(ImageFilter.GaussianBlur(36))
    ceramic.putalpha(ImageChops.multiply(ceramic.getchannel('A'),vase_mask))
    im=Image.alpha_composite(im,ceramic); d=ImageDraw.Draw(im,'RGBA')
    # Handle connects at the upper shoulder and returns to the middle of the body.
    d.arc((494,369,632,594),275,85,fill=(77,49,51,255),width=24)
    d.arc((503,380,616,578),275,80,fill=(202,125,86,255),width=14)
    d.ellipse((388,296,517,329),fill=(77,47,47,255),outline=(226,157,112,255),width=6)
    d.arc((382,303,520,336),11,170,fill=(249,191,136,159),width=3)
    # Decoration curves around the belly and stops at the shaded side.
    d.arc((351,516,556,616),10,176,fill=(230,160,106,190),width=5)
    d.arc((350,525,557,626),9,176,fill=(87,51,51,135),width=2)
    for x,y in [(403,552),(434,560),(462,563),(491,557)]:
        d.ellipse((x-4,y-5,x+4,y+5),fill=(234,171,120,155))
    d.ellipse((120,773,756,1010),fill=(26,27,37,131))
    d.ellipse((165,744,724,954),fill=(121,77,63,255),outline=(222,159,112,255),width=6)
    d.ellipse((194,761,696,912),fill=(72,46,47,255))
    # No leaves float inside the vase; the fruit remains the focal point.
    fruits=[(291,721,94,105,(215,56,59)),(435,679,94,115,(244,151,54)),(568,734,91,100,(207,56,68)),(379,814,84,87,(222,77,52)),(526,819,79,85,(248,176,66))]
    for idx,(cx,cy,rx,ry,col) in enumerate(fruits):
        rr=random.Random(706+idx)
        # Subtle indent at the stem, uneven lobes and flattened bottom.
        pts=[]
        for j in range(120):
            angle=math.tau*j/120
            swell=1+.025*math.sin(angle*3+idx)+.022*math.sin(angle*5+idx*.6)
            x=cx+rx*math.cos(angle)*swell
            y=cy+ry*math.sin(angle)*swell
            if math.sin(angle)<-.80: y+=11*(1-abs(math.cos(angle)))
            if math.sin(angle)>.80: y-=7
            pts.append((x,y))
        # Paint glazes and short scumbled strokes inside a silhouette mask.
        mask=Image.new('L',(W,H),0); ImageDraw.Draw(mask).polygon(pts,fill=255)
        layer=Image.new('RGBA',(W,H),(0,0,0,0)); fd=ImageDraw.Draw(layer,'RGBA')
        fd.polygon(pts,fill=(*col,255),outline=(102,52,44,255),width=2)
        glaze=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glaze,'RGBA')
        gd.ellipse((cx-rx*.82,cy-ry*.85,cx+rx*.42,cy+ry*.51),fill=(255,222,133,112))
        gd.ellipse((cx+rx*.32,cy-ry*.48,cx+rx*1.15,cy+ry*.96),fill=(98,35,48,72))
        glaze=glaze.filter(ImageFilter.GaussianBlur(21))
        layer=Image.alpha_composite(layer,glaze)
        texture=Image.new('RGBA',(W,H),(0,0,0,0)); td=ImageDraw.Draw(texture,'RGBA')
        for j in range(70):
            x=rr.uniform(cx-rx,cx+rx); y=rr.uniform(cy-ry,cy+ry)
            c=(255,215,153,rr.randint(18,48)) if x<cx else (113,43,44,rr.randint(15,43))
            td.line((x,y,x+rr.randint(4,10),y-rr.randint(0,4)),fill=c,width=rr.randint(1,3))
        layer=Image.alpha_composite(layer,texture)
        layer.putalpha(ImageChops.multiply(layer.getchannel('A'),mask))
        im=Image.alpha_composite(im,layer); d=ImageDraw.Draw(im,'RGBA')
        d.ellipse((cx-14,cy-ry+3,cx+14,cy-ry+13),fill=(104,63,48,160))
        d.line((cx,cy-ry+7,cx+rr.randint(1,9),cy-ry-20),fill=(66,72,46,255),width=5)
        d.ellipse((cx-rx*.46,cy-ry*.55,cx-rx*.28,cy-ry*.38),fill=(255,234,177,205))
    for j in range(18):
        x=rng.randint(80,840); y=rng.randint(1010,1182)
        im=stroke(im,[(x,y),(x+rng.randint(12,55),y-rng.randint(3,12))],rng.choice([(144,114,120),(173,135,117),(53,58,78)]),rng.randint(3,8),rng.randint(19,55),j+900)
    return vignette(im.filter(ImageFilter.GaussianBlur(.18)))

def city():
    """A wet main street with continuous curbs, cross street and side access."""
    rng=random.Random(191); im=gradient((18,24,46),(118,58,71))
    im=glow(im,(448,401),253,(243,134,111),75)
    d=ImageDraw.Draw(im,'RGBA'); horizon=670
    # Sparse stars live only in the visible sky, with a soft cloud bank below.
    for i in range(36):
        x=rng.randrange(21,879); y=rng.randrange(25,211)
        r=1 if i%6 else 2
        d.ellipse((x-r,y-r,x+r,y+r),fill=(232,218,217,rng.randint(95,182)))
    moon_mask=Image.new('L',(W,H),0)
    ImageDraw.Draw(moon_mask).ellipse((346,271,554,476),fill=245)
    moon=Image.new('RGBA',(W,H),(0,0,0,0)); md=ImageDraw.Draw(moon,'RGBA')
    for y in range(271,477):
        t=(y-271)/205
        md.line((346,y,554,y),fill=(round(252-32*t),round(209-67*t),round(184-58*t),255))
    mottling=Image.new('RGBA',(W,H),(0,0,0,0)); mtd=ImageDraw.Draw(mottling,'RGBA')
    for x,y,r in [(397,330,22),(472,309,13),(501,376,28),(432,423,18),(364,392,13),(457,366,8)]:
        mtd.ellipse((x-r,y-r*.8,x+r,y+r*.8),fill=(130,84,91,22))
    mottling=mottling.filter(ImageFilter.GaussianBlur(6))
    moon=Image.alpha_composite(moon,mottling)
    moon.putalpha(ImageChops.multiply(moon.getchannel('A'),moon_mask))
    im=Image.alpha_composite(im,moon); d=ImageDraw.Draw(im,'RGBA')
    # Distant skyline and central end of the avenue.
    d.polygon([(0,669),(0,527),(111,527),(111,583),(216,555),(216,505),(311,505),(311,601),(382,584),(382,670)],fill=(51,53,69,255))
    d.polygon([(520,670),(520,566),(615,566),(615,490),(692,490),(692,548),(786,519),(786,588),(900,588),(900,670)],fill=(51,47,65,255))
    d.rectangle((421,566,479,670),fill=(74,61,72,255))
    d.polygon([(411,575),(450,543),(489,575)],fill=(98,71,77,255))
    # Narrow, receding façades establish an actual street corridor.
    left=[(0,224,254,225),(86,337,309,175),(205,454,352,124),(318,522,400,83)]
    right=[(646,225,900,225),(563,337,814,175),(492,454,695,124),(450,522,582,83)]
    for side,blocks in [('l',left),('r',right)]:
        for i,(x0,y0,x1,depth) in enumerate(blocks):
            # Draw far blocks last near the horizon, but preserve stepped heights.
            if side=='l': a,b=x0,x1
            else: a,b=x0,x1
            facade=rng.choice([(38,39,58,255),(43,37,55,255),(54,41,58,255)])
            d.polygon([(a,y0),(b,y0+21),(b,horizon+depth),(a,horizon+depth+75)],fill=facade)
            d.polygon([(a,y0),(b,y0+21),(b,y0+38),(a,y0+15)],fill=(89,58,71,255))
            spacing=max(15,int((b-a)/5))
            for y in range(y0+62,horizon+depth-19,max(25,round(43-i*5))):
                for x in range(a+13,b-13,spacing):
                    if rng.random()<.28: continue
                    size=max(4,11-i*2)
                    d.rectangle((x,y,x+size,y+size*1.65),fill=rng.choice([(244,171,118,210),(91,191,199,200),(210,102,139,190)]))
            # Each shop gets an entrance, awning and warm lobby near ground.
            if i<3:
                doorx=b-48 if side=='l' else a+22
                yy=horizon+depth-28
                d.rectangle((doorx,yy-78,doorx+33,yy+8),fill=(109,77,75,255),outline=(203,141,108,255),width=2)
                d.polygon([(doorx-13,yy-81),(doorx+45,yy-81),(doorx+38,yy-68),(doorx-7,yy-68)],fill=(129,53,73,255))
                d.line((doorx+17,yy-66,doorx+17,yy+7),fill=(222,159,115,215),width=2)
    # Secondary lanes are dark openings with curb edges between foreground blocks.
    d.polygon([(93,685),(174,661),(284,711),(212,829)],fill=(26,29,44,255))
    d.line((174,661,212,829),fill=(147,110,107,200),width=3)
    d.polygon([(735,667),(821,691),(691,840),(630,712)],fill=(25,29,43,255))
    d.line((735,667,691,840),fill=(145,112,109,200),width=3)
    # Road and two raised sidewalks, all edges converge to the same vanishing zone.
    d.polygon([(421,horizon),(479,horizon),(735,1200),(166,1200)],fill=(29,34,50,255))
    d.polygon([(408,horizon),(421,horizon),(166,1200),(0,1200),(0,850)],fill=(74,71,80,255))
    d.polygon([(479,horizon),(492,horizon),(900,850),(900,1200),(735,1200)],fill=(73,67,78,255))
    d.line((421,horizon,166,1200),fill=(190,155,135,250),width=8)
    d.line((479,horizon,735,1200),fill=(189,153,139,250),width=8)
    d.line((403,678,142,1200),fill=(112,105,112,190),width=3)
    d.line((498,678,759,1200),fill=(112,105,112,190),width=3)
    # Paving seams are confined to sidewalks and widen towards the viewer.
    for k in range(1,9):
        t=k/9; y=round(horizon+(t*t)*530)
        left_edge=421-255*t*t; right_edge=479+256*t*t
        d.line((max(0,left_edge-115*t-25),y,max(0,left_edge-5),y),fill=(139,131,137,110),width=max(1,int(t*3)))
        d.line((min(900,right_edge+5),y,min(900,right_edge+115*t+25),y),fill=(139,131,137,110),width=max(1,int(t*3)))
    # Cross street cuts across the avenue at mid depth; pedestrian crossing reads at a glance.
    d.polygon([(307,819),(389,766),(510,766),(592,819),(684,837),(218,837)],fill=(39,42,57,255))
    for i in range(6):
        yy=857+i*16; spread=(yy-horizon)*.48
        d.polygon([(450-spread+7,yy),(450+spread-7,yy),
                   (450+spread-12,yy+5),(450-spread+12,yy+5)],fill=(172,158,143,105))
    # Street furniture helps measure scale and connects the side routes.
    for x,y,scale in [(200,813,1.05),(320,735,.7),(705,830,1.03),(570,736,.7)]:
        height=round(125*scale)
        d.line((x,y,x,y-height),fill=(24,31,43,255),width=max(3,round(7*scale)))
        direction=1 if x<450 else -1
        d.arc((x-9 if direction==1 else x-43,y-height-15,x+45 if direction==1 else x+10,y-height+28),188 if direction==1 else 260,350 if direction==1 else 62,fill=(24,31,43,255),width=4)
        bx=x+38*direction
        d.ellipse((bx-10,y-height+3,bx+10,y-height+17),fill=(245,179,121,230))
    # Traffic lights control the crossing from both curbs.
    for x,y,side,scale in [(324,817,1,.85),(592,806,-1,.82)]:
        pole_top=round(y-195*scale)
        d.line((x,y,x,pole_top),fill=(38,39,48,255),width=5)
        d.line((x,pole_top,x+side*53,pole_top),fill=(42,41,49,255),width=5)
        sx=x+side*53
        d.rounded_rectangle((sx-9,pole_top-4,sx+9,pole_top+43),radius=3,fill=(25,31,39,255))
        for i,col in enumerate([(234,89,75,240),(190,151,83,125),(75,156,111,98)]):
            yy=pole_top+5+i*13;d.ellipse((sx-5,yy-5,sx+5,yy+5),fill=col)
    # Passersby establish scale; shoes stay strictly on the sidewalks.
    for x,y,height in [(254,878,69),(760,1083,112),(121,1039,96)]:
        head=max(5,height//10); neck=y-height+head*2
        d.ellipse((x-head,y-height,x+head,y-height+head*2),fill=(54,42,49,255))
        d.polygon([(x-head,neck),(x+head,neck),(x+head+5,neck+height*.50),(x-head-5,neck+height*.50)],fill=(43,40,53,255))
        d.line((x-head,neck+8,x-head-12,neck+height*.35),fill=(43,40,53,255),width=5)
        d.line((x+head,neck+8,x+head+9,neck+height*.31),fill=(43,40,53,255),width=5)
        d.line((x-3,neck+height*.49,x-7,y),fill=(31,33,44,255),width=6)
        d.line((x+3,neck+height*.49,x+9,y),fill=(31,33,44,255),width=6)
        d.ellipse((x-10,y-2,x+10,y+3),fill=(18,21,32,160))
    # Reflections are vertical, short, tapered and remain inside the asphalt polygon.
    roadmask=Image.new('L',(W,H),0); ImageDraw.Draw(roadmask).polygon([(421,horizon),(479,horizon),(735,1200),(166,1200)],fill=255)
    reflections=Image.new('RGBA',(W,H),(0,0,0,0)); rd=ImageDraw.Draw(reflections,'RGBA')
    for i in range(115):
        y=rng.randint(738,1180); t=(y-horizon)/(H-horizon)
        x=rng.randint(round(450-255*t),round(450+255*t))
        c=rng.choice([(246,159,119,55),(90,193,203,47),(222,94,143,43),(199,171,157,40)])
        h=rng.randint(9,37); rd.line((x,y,x+rng.randint(-4,4),y+h),fill=c,width=rng.randint(2,6))
    reflections.putalpha(ImageChops.multiply(reflections.getchannel('A'),roadmask))
    im=Image.alpha_composite(im,reflections)
    d=ImageDraw.Draw(im,'RGBA')
    # Cars are placed before and after the crossing, not on its stripes.
    for x,base,width,body in [(453,792,36,(91,111,125,255)),(542,1057,98,(94,43,60,255))]:
        d.ellipse((x-width*.64,base-5,x+width*.64,base+12),fill=(10,18,29,145))
        d.polygon([(x-width*.36,base-width*.48),(x-width*.2,base-width*.78),
                   (x+width*.19,base-width*.78),(x+width*.38,base-width*.48)],fill=(86,86,101,255))
        d.polygon([(x-width*.24,base-width*.71),(x+width*.18,base-width*.71),
                   (x+width*.28,base-width*.49),(x-width*.32,base-width*.49)],fill=(42,52,65,255))
        d.polygon([(x-width*.44,base-width*.49),(x+width*.43,base-width*.49),
                   (x+width*.56,base-4),(x-width*.54,base-4)],fill=body)
        d.line((x-width*.35,base-width*.25,x+width*.33,base-width*.25),fill=(184,115,107,160),width=max(2,round(width*.035)))
        for sign in (-1,1):
            ax=x+sign*width*.38
            d.ellipse((ax-width*.105,base-width*.20,ax+width*.105,base-width*.08),fill=(250,198,139,255))
            d.ellipse((ax-width*.12,base-4,ax+width*.12,base+6),fill=(18,23,34,255))
        d.line((x-width*.36,base-8,x+width*.34,base-8),fill=(36,36,43,255),width=3)
    for x,y,rx in [(424,1033,45),(529,1135,74),(361,980,29)]:
        d.arc((x-rx,y-7,x+rx,y+11),190,352,fill=(108,134,148,96),width=2)
    return vignette(im.filter(ImageFilter.GaussianBlur(.13)))


def render(output_dir):
    from render_painted_character import render as paint_character
    output_dir=Path(output_dir).expanduser().resolve(); output_dir.mkdir(parents=True,exist_ok=True)
    items=[('01_casa_perspectiva.png',house),('02_personagem_pintura.png',paint_character),
           ('03_natureza_morta_oleo.png',still_life),('04_rua_chuvosa_perspectiva.png',city)]
    thumbs=[]
    for name,fn in items:
        image=fn().convert('RGB')
        pending=output_dir/f'.{name}.pending'
        image.save(pending,format='PNG',optimize=False)
        with Image.open(pending) as verify: verify.load()
        pending.replace(output_dir/name)
        thumb=image.copy(); thumb.thumbnail((450,600),Image.Resampling.LANCZOS)
        thumbs.append(thumb)
        print(f'{name}: {image.width}x{image.height}')
    sheet=Image.new('RGB',(920,1240),(23,21,32))
    d=ImageDraw.Draw(sheet)
    labels=['01 · Casa no jardim','02 · Cabelo em massas','03 · Frutas vibrantes','04 · Rua e pedestres']
    for i,img in enumerate(thumbs):
        x=6+(i%2)*460; y=6+(i//2)*620
        sheet.paste(img,(x,y))
        d.rectangle((x,y+570,x+450,y+600),fill=(23,21,32))
        d.text((x+11,y+577),labels[i],fill=(234,222,214))
    pending=output_dir/'.00_contact_sheet.pending'
    sheet.save(pending,format='PNG',optimize=False)
    with Image.open(pending) as verify: verify.load()
    pending.replace(output_dir/'00_contact_sheet.png')
    return output_dir

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Gera quatro estudos da academia usando CPU e Pillow.')
    parser.add_argument('--output-dir',default='academy_results',help='Pasta para quatro PNGs e a folha de contato')
    args=parser.parse_args()
    render(args.output_dir)
