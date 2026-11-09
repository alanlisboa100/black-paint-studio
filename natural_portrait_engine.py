#!/usr/bin/env python3
"""Procedural portrait painter: anatomy, soft masked shading and directional locks.

Pillow only. Draws an authored frontal composition; no input pixels, remote image
model or automatic anatomical recognition. Shared primitives support future
hand-authored portraits. The supplied card controls iris/accent colors.
"""
from __future__ import annotations
import math
import random
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from render_neural_plan import to_abs, bezier_samples, color
from portrait_controls import normalize_options

W, H = 900, 1200


def cubic(curve, t):
    u = 1-t
    return tuple(u**3*curve[0][j]+3*u*u*t*curve[1][j]+3*u*t*t*curve[2][j]+t**3*curve[3][j] for j in (0,1))


def mix(a, b, t):
    return tuple(round(x+(y-x)*t) for x,y in zip(a,b))


def path_points(path):
    groups=[]; last=(0,0)
    for command, points in to_abs(path):
        if command == 'M':
            groups.append([points[0]]);last=points[0]
        else:
            sampled=bezier_samples(command,points,last,steps=36)
            groups[-1].extend(sampled);last=sampled[-1]
    return groups


class Painter:
    def __init__(self, width=900, quality='standard', seed=7331, background='paper'):
        if not isinstance(width,int) or not 128<=width<=1080:
            raise ValueError('width deve estar entre 128 e 1080')
        if quality not in ('economy','standard') or background not in ('paper','night'):
            raise ValueError('Qualidade ou fundo inválido')
        self.width=width;self.height=round(width*H/W)
        self.factor=width/W*(2 if quality=='standard' else 1)
        self.size=(round(W*self.factor),round(H*self.factor))
        self.im=Image.new('RGB',self.size,(250,247,248) if background=='paper' else (20,18,27))
        self.rng=random.Random(seed);self.background=background
        self.stages=[];self.fiber_count=0
        self.options=normalize_options()

    def point(self,point):
        return tuple(round(v*self.factor) for v in point)

    def path_mask(self,path):
        mask=Image.new('L',self.size)
        draw=ImageDraw.Draw(mask)
        for points in path_points(path):draw.polygon([self.point(pt) for pt in points],fill=255)
        return mask

    def fill(self,path,rgb,outline=None,line_width=1):
        mask=self.path_mask(path)
        self.im.paste(rgb,(0,0),mask)
        if outline:
            for points in path_points(path):self.line(points+[points[0]],outline,line_width)
        return mask

    def gradient(self,mask,top,bottom):
        bbox=mask.getbbox()
        if not bbox:return
        x0,y0,x1,y1=bbox
        patch=Image.new('RGB',(x1-x0,y1-y0));draw=ImageDraw.Draw(patch)
        for y in range(patch.height):draw.line((0,y,patch.width,y),fill=mix(top,bottom,y/max(1,patch.height-1)))
        self.im.paste(patch,(x0,y0),mask.crop(bbox))

    def line(self,points,rgb,width=1):
        if len(points)>1:
            ImageDraw.Draw(self.im).line([self.point(p) for p in points],fill=rgb,width=max(1,round(width*self.factor)),joint='curve')

    def curve(self,curve,rgb,width=1,taper=True):
        points=[cubic(curve,i/48) for i in range(49)]
        if not taper:self.line(points,rgb,width);return
        for i in range(len(points)-1):
            weight=(.15+.85*math.sin(math.pi*(i+.5)/48)**.5)*width
            self.line(points[i:i+2],rgb,weight)

    def ellipse(self,box,rgb):
        ImageDraw.Draw(self.im).ellipse(tuple(round(v*self.factor) for v in box),fill=rgb)

    def soft(self,box,rgb,opacity=.25,blur=12,clip=None,path=None):
        pad=blur*3+2
        x0=max(0,math.floor((box[0]-pad)*self.factor));y0=max(0,math.floor((box[1]-pad)*self.factor))
        x1=min(self.size[0],math.ceil((box[2]+pad)*self.factor));y1=min(self.size[1],math.ceil((box[3]+pad)*self.factor))
        if x1<=x0 or y1<=y0:return
        mask=Image.new('L',(x1-x0,y1-y0));draw=ImageDraw.Draw(mask)
        alpha=max(0,min(255,round(opacity*255)))
        if path:
            for points in path_points(path):draw.polygon([(self.point(p)[0]-x0,self.point(p)[1]-y0) for p in points],fill=alpha)
        else:
            b=[round(v*self.factor) for v in box]
            draw.ellipse((b[0]-x0,b[1]-y0,b[2]-x0,b[3]-y0),fill=alpha)
        if blur:mask=mask.filter(ImageFilter.GaussianBlur(blur*self.factor))
        if clip:mask=ImageChops.multiply(mask,clip.crop((x0,y0,x1,y1)))
        self.im.paste(rgb,(x0,y0,x1,y1),mask)

    def masked_ellipse(self,box,rgb,clip):
        mask=Image.new('L',self.size);ImageDraw.Draw(mask).ellipse(tuple(round(v*self.factor) for v in box),fill=255)
        self.im.paste(rgb,(0,0),ImageChops.multiply(mask,clip))

    def checkpoint(self,name,folder):
        self.stages.append(name)
        if folder:
            target=Path(folder).expanduser();target.mkdir(parents=True,exist_ok=True)
            self.result().save(target/f'{len(self.stages):02d}_{name}.png','PNG')

    def result(self):
        return self.im.resize((self.width,self.height),Image.Resampling.LANCZOS)

    def lock(self,left,right,top=(35,30,41),bottom=(20,18,26),fibers=170,shine=.55):
        """Bezier ribbon. All fibers interpolate the SAME two boundary curves."""
        shine*=self.options['hair_shine']
        outline=[cubic(left,i/60) for i in range(61)]+[cubic(right,i/60) for i in range(60,-1,-1)]
        mask=Image.new('L',self.size);ImageDraw.Draw(mask).polygon([self.point(p) for p in outline],fill=255)
        self.gradient(mask,top,bottom)
        # Broad lighting is shaped in ribbon coordinates, following the lock
        # rather than painting straight stripes across independently curved hair.
        bbox=mask.getbbox()
        if not bbox:return mask
        x0,y0,x1,y1=bbox
        shade=Image.new('RGB',(x1-x0,y1-y0));draw=ImageDraw.Draw(shade)
        def surface(t,u):
            a,b=cubic(left,t),cubic(right,t)
            x,y=self.point((a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u))
            return x-x0,y-y0
        for row in range(48):
            t=(row+.5)/48
            band=math.exp(-((t-.29)/.14)**2)+.45*math.exp(-((t-.68)/.18)**2)
            for column in range(16):
                u=(column+.5)/16
                volume=math.sin(math.pi*u)**1.8
                base=mix(top,bottom,t)
                tone=mix(base,(106,83,105),min(.45,band*volume*shine*.42))
                draw.polygon([surface(row/48,column/16),surface((row+1)/48,column/16),
                              surface((row+1)/48,(column+1)/16),surface(row/48,(column+1)/16)],fill=tone)
        self.im.paste(shade,(x0,y0),mask.crop(bbox))
        # Soft broad highlights form a volume before fine strands are deposited.
        for center_t,strength in ((.28,.20),(.64,.14)):
            mid=mix(cubic(left,center_t),cubic(right,center_t),.50)
            span=math.dist(cubic(left,center_t),cubic(right,center_t))
            self.soft((mid[0]-span*.43,mid[1]-72,mid[0]+span*.43,mid[1]+72),(113,92,109),strength*shine,20,mask)
        for i in range(fibers):
            u=(i+self.rng.random())/fibers
            begin=self.rng.uniform(0,.14);end=self.rng.uniform(.83,1)
            pts=[];jitter=self.rng.uniform(-1.1,1.1)
            for j in range(65):
                t=begin+(end-begin)*j/64
                a,b=cubic(left,t),cubic(right,t)
                # waviness vanishes at the ribbon edges; fibers never cross the silhouette.
                wave=(math.sin(t*11+u*7)+.22*math.sin(t*24+u*13))*jitter*math.sin(math.pi*u)*self.options['hair_wave']
                pts.append((a[0]+(b[0]-a[0])*u+wave,a[1]+(b[1]-a[1])*u))
            light=math.sin(math.pi*u)**1.7
            rgb=mix((23,21,30),(72,59,74),light*self.rng.uniform(.2,.8))
            self.line(pts,rgb,self.rng.uniform(.35,.78))
            # Distributed short highlights, following the flow instead of random hatch marks.
            if self.rng.random()<.55*shine:
                first=self.rng.randint(9,38);last=min(64,first+self.rng.randint(5,22))
                tint=mix((57,46,62),(129,105,124),light*self.rng.uniform(.28,.80))
                self.line(pts[first:last],tint,self.rng.uniform(.35,.70))
            self.fiber_count+=1
        self.line(outline[:61],(33,28,39),.8)
        self.line(list(reversed(outline[61:])),(18,16,23),.9)
        return mask


def paint_background(c):
    if c.background=='paper':
        c.soft((160,-60,880,1100),(242,232,242),.30,120)
        c.soft((-220,400,360,1600),(255,255,255),.55,90)
        rgb=(181,163,181)
    else:
        c.soft((140,20,820,1150),(67,48,68),.30,105)
        rgb=(93,75,98)
    for x,y,r in ((118,226,11),(794,247,12),(88,760,10),(803,617,8)):
        c.line([(x-r,y),(x+r,y)],rgb,1);c.line([(x,y-r),(x,y+r)],rgb,1)
    for _ in range(28):
        x=c.rng.uniform(80,825);y=c.rng.uniform(170,1100)
        c.ellipse((x,y,x+1.3,y+1.3),rgb)


def paint_base(c):
    hair='M 450 88 C 292 70 186 172 167 354 C 150 540 121 801 77 1200 L 801 1200 C 752 1010 776 704 746 394 C 743 214 639 92 450 88 Z'
    c.gradient(c.path_mask(hair),(34,29,39),(15,14,21))
    c.lock([(450,88),(281,69),(164,214),(171,590)],[(451,105),(324,126),(308,315),(315,567)],fibers=180,shine=.68)
    c.lock([(450,89),(636,73),(759,244),(749,652)],[(450,107),(588,119),(623,327),(611,581)],fibers=190,shine=.70)
    c.fill('M 383 808 C 318 814 217 850 141 902 L 0 1142 L 0 1200 L 900 1200 L 900 1099 C 793 935 694 857 541 807 Z',(24,23,31))
    c.soft((152,901,773,1390),(53,45,57),.25,65)
    c.fill('M 211 869 C 274 833 326 821 386 811 L 374 875 L 322 970 L 303 1200 L 74 1200 Z',(30,28,37))
    c.fill('M 552 810 C 637 824 720 859 792 929 L 899 1139 L 900 1200 L 681 1200 L 596 973 L 533 877 Z',(28,26,35))
    for curve,width in [([(193,916),(262,905),(344,936),(376,966)],1.3),([(632,891),(652,954),(703,1119),(736,1200)],1),([(563,940),(546,994),(574,1137),(569,1200)],.9),([(353,919),(310,966),(309,1092),(274,1200)],.8)]:
        c.curve(curve,(83,64,84),width)
    c.curve([(374,875),(407,967),(396,1094),(405,1200)],(14,13,20),3)
    c.curve([(532,877),(523,964),(519,1091),(523,1200)],(14,13,20),3)
    # Neck mass and its cast shadow will be partially covered by the jaw.
    neck=c.fill('M 409 687 C 412 749 407 788 386 826 C 421 857 512 862 558 816 C 537 789 523 746 530 680 Z',(239,221,223))
    c.soft((400,708,548,823),(122,97,112),.45,8,neck,path='M 404 708 L 535 700 L 538 747 C 487 779 458 808 420 830 L 404 708 Z')
    c.soft((440,781,557,879),(255,243,241),.38,18,neck)
    return neck


def paint_face(c):
    shape='M 337 321 C 309 392 308 486 317 549 C 326 635 388 706 451 745 C 469 755 486 741 505 724 C 538 696 561 672 580 644 C 615 591 640 519 635 424 C 630 359 591 325 551 316 C 480 292 387 299 337 321 Z'
    face=c.fill(shape,(244,229,230))
    c.gradient(face,(231,212,221),(249,236,233))
    # Volumes are clipped to skin, keeping all hair/background pixels unchanged.
    c.soft((300,404,391,665),(171,137,158),.27,22,face)
    c.soft((569,385,670,648),(178,140,155),.22,23,face)
    c.soft((326,478,463,591),(214,155,176),.22,24,face)
    c.soft((487,483,610,588),(217,158,176),.19,22,face)
    c.soft((377,555,552,739),(255,250,244),.26,39,face)
    c.soft((331,371,619,465),(152,118,142),.24,21,face)
    c.soft((327,475,425,519),(164,119,147),.26,9,face)
    c.soft((492,470,589,519),(164,118,146),.26,9,face)
    c.soft((432,527,454,599),(178,137,156),.25,4,face,path='M 447 522 C 443 549 439 568 435 581 C 432 592 440 597 450 598 L 444 591 C 438 583 443 558 447 522 Z')
    c.soft((414,498,454,610),(185,143,162),.24,12,face,path='M 443 501 C 439 538 422 570 426 588 C 435 600 446 598 450 596 C 438 573 451 544 443 501 Z')
    c.soft((445,507,475,594),(255,249,243),.32,9,face)
    c.soft((339,527,399,590),(253,235,235),.19,16,face)
    c.soft((519,522,574,578),(255,240,235),.23,15,face)
    c.soft((404,686,506,734),(194,153,169),.13,18,face)
    c.soft((432,687,481,710),(255,249,241),.27,10,face)
    # Natural nose: no heavy continuous outline, only planes of light and the
    # tiny nostril openings. Alar wings get their own soft shadow volumes.
    c.soft((434,584,447,601),(174,136,157),.30,4.5,face)
    c.soft((465,584,479,601),(180,141,161),.26,4.5,face)
    c.soft((439,593,473,606),(193,155,172),.24,4,face)
    c.soft((441,572,470,591),(255,250,245),.34,5,face)
    c.masked_ellipse((448,580,466,592),(255,250,246),face)
    c.curve([(440,592),(444,589),(448,589),(451,592)],(160,120,141),.9)
    c.curve([(462,592),(466,589),(469,589),(472,592)],(176,136,157),.6)
    c.masked_ellipse((442.4,589.6,445.4,591.6),(141,104,125),face)
    c.masked_ellipse((466.6,589.6,469.6,591.6),(150,112,132),face)
    # Jaw contour is light and variable rather than a dark geometric border.
    c.curve([(319,550),(329,637),(390,707),(451,745)],(174,147,158),.65)
    c.curve([(451,745),(469,755),(486,741),(505,724)],(182,153,164),.5)
    c.curve([(505,724),(538,696),(561,672),(580,644)],(182,153,164),.5)
    # An ear visible through the right-side locks.
    c.fill('M 625 435 C 648 428 651 451 642 477 L 629 527 C 618 539 612 526 616 510 Z',(232,209,218))
    c.curve([(634,447),(623,448),(637,470),(624,493)],(170,133,154),.8)
    for center in (368,550):
        for i in range(7):
            x=center-18+i*5+c.rng.uniform(-1,1);y=545+c.rng.uniform(-6,5)
            c.line([(x,y),(x-2,y+4)],(222,182,192),.45)
    return face


def paint_iris(c, cx, cy, radius, iris_rgb, clip, pupil_size=.25):
    # Small, local patch: avoids allocating a whole portrait per iris ring.
    x0,y0=c.point((cx-radius-1,cy-radius*1.07-1));x1,y1=c.point((cx+radius+1,cy+radius*1.07+1))
    patch=Image.new('RGB',(x1-x0,y1-y0));alpha=Image.new('L',patch.size)
    pixels=patch.load();opacity=alpha.load()
    local_clip=clip.crop((x0,y0,x1,y1));mask_pixels=local_clip.load()
    for y in range(patch.height):
        for x in range(patch.width):
            dx=((x+x0)/c.factor-cx)/radius
            dy=((y+y0)/c.factor-cy)/(radius*1.06)
            rho=math.hypot(dx,dy)
            if rho>1 or not mask_pixels[x,y]:continue
            angle=math.atan2(dy,dx)
            light=.53+.25*dy+.13*math.sin(angle*49+rho*22)+.07*math.cos(angle*93-rho*17)
            tone=mix((38,17,33),mix(iris_rgb,(224,143,160),.36),max(0,min(1,light)))
            if .35<rho<.58:tone=mix(tone,(183,112,135),.17*(1-abs(rho-.465)/.115))
            if rho>.83:tone=mix(tone,(31,18,32),min(1,(rho-.83)/.17))
            if rho<pupil_size+.08:tone=mix((23,15,27),tone,max(0,(rho-pupil_size)/.08))
            if dy<-.22:tone=mix(tone,(25,17,29),min(.72,(-dy-.22)*.95))
            pixels[x,y]=tone;opacity[x,y]=mask_pixels[x,y]
    c.im.paste(patch,(x0,y0),alpha)


def paint_eye(c,left,iris_rgb):
    o=c.options
    if left:
        upper=[(331,486),(354,465),(393,463),(422,482)]
        lower=[(331,486),(355,503),(394,501),(422,482)]
        cx,cy=379,483
    else:
        upper=[(496,481),(524,461),(562,461),(586,480)]
        lower=[(496,481),(526,502),(563,500),(586,480)]
        cx,cy=538,480
    orientation=1 if left else -1
    def transform(p):
        return (cx+(p[0]-cx)*o['eye_width'],
                cy+(p[1]-cy)*o['eye_open']+orientation*(p[0]-cx)*o['eye_tilt']*.18)
    upper=[transform(p) for p in upper];lower=[transform(p) for p in lower]
    points=[cubic(upper,i/48) for i in range(49)]+[cubic(lower,i/48) for i in range(48,-1,-1)]
    clip=Image.new('L',c.size);ImageDraw.Draw(clip).polygon([c.point(p) for p in points],fill=255)
    c.gradient(clip,(200,181,201),(248,237,239))
    bounds=(min(p[0] for p in points)-8,min(p[1] for p in points)-8,
            max(p[0] for p in points)+8,max(p[1] for p in points)+8)
    c.soft(bounds,(158,115,143),.10,8,clip)
    ix=cx+o['gaze_x']*8;iy=cy+o['gaze_y']*5
    radius=20*o['iris_size']
    paint_iris(c,ix,iy,radius,iris_rgb,clip,o['pupil_size'])
    c.soft((ix-11,iy-10,ix-3,iy-4),(255,245,251),.60,1.7,clip)
    c.masked_ellipse((ix-9,iy-9,ix-5,iy-6),(255,246,250),clip)
    c.masked_ellipse((ix+7,iy+8,ix+9,iy+9.5),(227,177,191),clip)
    # Shadow shares the transformed upper lid; never use stale fixed coordinates.
    shadow=Image.new('L',c.size);draw=ImageDraw.Draw(shadow)
    band=[cubic(upper,i/48) for i in range(49)]
    draw.polygon([c.point(p) for p in band]+[c.point((x,y+5)) for x,y in reversed(band)],fill=110)
    shadow=ImageChops.multiply(shadow.filter(ImageFilter.GaussianBlur(c.factor)),clip)
    c.im.paste((45,27,44),(0,0),shadow)
    c.curve(upper,(37,27,41),3.7)
    c.curve(lower,(124,87,110),.75)
    c.curve([(x,y-8) for x,y in upper],(174,124,151),.8)
    for i in range(10):
        p=cubic(lower,.1+i*.078)
        c.curve([p,(p[0]+.4,p[1]+2),(p[0]+1.8,p[1]+4),(p[0]+2,p[1]+5)],(135,92,116),.5)
    for i in range(5):
        p=cubic(upper,(.05+i*.10) if left else (.95-i*.10));sgn=-1 if left else 1
        c.curve([p,(p[0]+sgn*4,p[1]-2),(p[0]+sgn*7,p[1]-4),(p[0]+sgn*9,p[1]-7)],(40,29,44),1.3)
    brow=[(335,443),(359,428),(392,431),(417,444)] if left else [(499,441),(527,425),(559,427),(582,440)]
    brow=[(x,y+orientation*(x-cx)*o['brow_tilt']*.24-(o['eye_open']-1)*10) for x,y in brow]
    c.curve(brow,(76,59,76),2)
    for i in range(15):
        p=cubic(brow,(i+.3)/15);c.line([p,(p[0]+3,p[1]-1.7)],(67,51,68),.5)


def ribbon_points(points, steps=18):
    """Catmull-Rom style smoothing so any authored control list becomes a soft outline."""
    if len(points) < 2: return list(points)
    out = []
    n = len(points)
    for i in range(n-1):
        p0 = points[i-1] if i > 0 else points[i]
        p1, p2 = points[i], points[i+1]
        p3 = points[i+2] if i+2 < n else points[i+1]
        c1 = (p1[0]+(p2[0]-p0[0])/6, p1[1]+(p2[1]-p0[1])/6)
        c2 = (p2[0]-(p3[0]-p1[0])/6, p2[1]-(p3[1]-p1[1])/6)
        for j in range(steps):
            out.append(cubic((p1, c1, c2, p2), j/steps))
    out.append(points[-1])
    return out


def paint_lips(c,clip=None):
    """Natural small mouth: cupid's bow, soft vermilion gradient, thin seam."""
    o=c.options;cx=455;cy=650
    half=27*o['mouth_width'];smile=o['mouth_curve']*7
    fullness=o['lip_fullness'];opening=o['mouth_open']*16
    left=(cx-half,cy-smile);right=(cx+half,cy-smile)
    bow=cx-half*.06
    # Upper lip rises to the cupid's bow and dips at the philtrum.
    upper=[left,(cx-half*.62,cy-3.2*fullness),(bow-.6,cy-6.2*fullness),
           (bow,cy-7.4*fullness),(bow+.9,cy-5.9*fullness),
           (cx+half*.58,cy-2.8*fullness),right]
    seam=[left,(cx-half*.42,cy+smile*.30),(cx+half*.42,cy+smile*.30),right]
    lower=[left,(cx-half*.62,cy+5.4*fullness+opening),(cx+half*.60,cy+9.4*fullness+opening),right]
    def ribbon(a,b,rgb):
        points=ribbon_points(a)+list(reversed(ribbon_points(b)))
        mask=Image.new('L',c.size);ImageDraw.Draw(mask).polygon([c.point(p) for p in points],fill=255)
        if clip is not None:mask=ImageChops.multiply(mask,clip)
        c.im.paste(rgb,(0,0),mask)
        return mask
    # Soft natural vermilion halo before the lips are laid in, so edges blend.
    c.soft((cx-half-7,cy-11,cx+half+7,cy+14+opening),(196,146,164),.13,9,clip)
    upper_mask=ribbon(upper,seam,(203,157,175))
    lip=ribbon(seam,lower,(233,190,201))
    # Volume inside each lip instead of flat fill.
    c.soft((cx-half*.75,cy-6*fullness,cx+half*.75,cy+2),(176,124,146),.26,5,upper_mask)
    c.soft((cx-half*.60,cy+1,cx+half*.60,cy+11*fullness+opening),(246,214,218),.30,6,lip)
    if opening>.5:
        inner=[left,(cx-half*.40,cy+opening),(cx+half*.40,cy+opening),right]
        cavity=ribbon(seam,inner,(74,33,53))
        if o['mouth_curve']>.4:
            c.soft((cx-half*.6,cy+1,cx+half*.6,cy+4),(247,227,223),.75,1,cavity)
        c.soft((cx-half*.45,cy+opening*.55,cx+half*.45,cy+opening),(175,86,115),.42,2,cavity)
    # Seam is thin and interrupted, never a hard continuous line.
    c.curve([left,(cx-half*.42,cy+smile*.30),(cx+half*.42,cy+smile*.30),right],(150,108,130),.7)
    c.soft((cx-half*.9,cy+smile*.30-1,cx+half*.9,cy+smile*.30+1),(198,150,167),.30,2,clip)
    # Small specular on the lower lip plus a soft philtrum shadow.
    c.soft((cx-11,cy+5+opening,cx+12,cy+9+opening),(255,240,238),.42,2.2,lip)
    c.masked_ellipse((cx-3.4,cy+4.4+opening,cx+.6,cy+6.2+opening),(255,247,244),lip)
    c.soft((cx-6,cy-11*fullness,cx+7,cy-3),(206,168,183),.16,4,clip)
    c.soft((cx-19,cy+23+opening,cx+22,cy+29+opening),(204,170,181),.12,4,clip)


def paint_clothing(c):
    o=c.options;satin=o['cloth_material']=='satin';fold=o['cloth_fold']
    garment=c.path_mask('M 211 869 C 274 833 326 821 386 811 L 552 810 C 637 824 720 859 792 929 L 899 1139 L 900 1200 L 74 1200 Z')
    c.soft((295,888,586,1250),(66,51,70),.20,42,garment)
    # Creases start at seams and tension points. Satin has narrower highlights;
    # velvet has broad diffuse volume with a subtle directional nap.
    for shape,box in [
        ('M 356 878 C 330 938 321 1030 316 1157 L 302 1199 C 298 1061 313 950 344 883 Z',(285,871,368,1200)),
        ('M 577 887 C 604 963 604 1087 640 1200 L 657 1200 C 630 1061 615 961 587 880 Z',(562,874,669,1240)),
        ('M 404 928 C 450 953 491 954 537 928 L 515 953 C 473 974 435 966 412 945 Z',(399,920,545,982))]:
        c.soft(box,(96,74,103) if satin else (70,55,76),(.33 if satin else .20)*fold,5 if satin else 13,garment,path=shape)
    for curve in [[(353,889),(328,963),(321,1064),(306,1200)],[(581,887),(619,996),(618,1100),(650,1200)]]:
        c.curve(curve,(12,12,20),2.5*fold)
        c.curve([(x+4,y) for x,y in curve],(76,60,82) if satin else (49,40,58),.9)
    for _ in range(190):
        x=c.rng.uniform(290,657);y=c.rng.uniform(900,1198);px,py=c.point((x,y))
        if garment.getpixel((px,py)):
            old=c.im.getpixel((px,py))
            c.line([(x,y),(x+1,y+3)],mix(old,(96,78,105),.10 if satin else .14),.3)
    # Separate collar mask keeps texture from entering the neck.
    collar=c.fill('M 385 815 C 420 833 517 838 558 814 L 555 870 C 511 889 421 887 380 867 Z',(24,22,31))
    c.gradient(collar,(34,28,39),(18,17,25))
    for y in range(825,875,4):c.curve([(388,y),(433,y+8),(513,y+11),(553,y-2)],(55,46,63),.55)
    c.soft((403,824,456,878),(113,90,118),.18,13,collar)
    # Metal receives a dark rim and a small light-facing bevel.
    c.ellipse((456,861,473,878),(67,60,79));c.ellipse((458,863,471,876),(133,121,146))
    c.ellipse((460,865,469,874),(23,21,30))
    c.curve([(460,864),(461,862),(466,862),(469,864)],(192,181,201),.6)
    c.curve([(389,883),(434,906),(499,910),(554,884)],(57,46,64),.9)
    for y in range(967,1190,24):
        x1=424+(y-967)*.025;x2=504-(y-967)*.018
        for x in (x1,x2):
            c.ellipse((x-2,y-2,x+2,y+2),(81,67,90));c.ellipse((x-1,y-1,x+1,y+1),(19,17,27))
        c.line([(x1,y),(x2,y+18)],(19,16,25),2)
        c.line([(x1,y-1),(x2,y+17)],(70,53,76),.65)
        c.line([(x2,y),(x1,y+18)],(61,46,68),.65)


def paint_hair(c):
    # Crowning mass first: hair grows from a soft dome, never a roof/pentagon top.
    crown=c.fill('M 300 292 C 318 214 370 150 451 143 C 533 137 590 196 612 268 '
                 'C 625 312 633 356 636 402 C 596 336 549 300 470 293 '
                 'C 390 286 331 306 300 292 Z',(32,27,39))
    c.gradient(crown,(38,31,45),(26,22,32))
    c.soft((330,166,570,300),(83,66,89),.22,34,crown)
    c.soft((352,196,470,282),(126,101,122),.15,20,crown)
    # Underlying fringe connects the crown to fine tapered locks; skin gaps
    # begin on curved edges, avoiding exposed rectangular tops of the face.
    fringe=c.fill('M 302 300 C 342 216 566 226 641 312 L 616 437 C 589 451 574 445 553 428 '
                  'C 533 413 509 405 492 419 C 476 435 463 433 444 409 '
                  'C 426 383 416 383 402 409 C 386 438 353 461 324 476 Z',(34,28,40))
    c.gradient(fringe,(36,29,42),(27,23,33))
    c.soft((330,232,570,330),(92,73,98),.16,26,fringe)
    # Side locks fall in front of the shoulders; each owns its mask and curvature.
    c.lock([(434,99),(175,96),(177,565),(104,1200)],[(458,121),(298,185),(303,600),(219,1200)],fibers=300,shine=.75)
    c.lock([(431,106),(192,165),(126,804),(77,1200)],[(440,126),(312,352),(267,957),(207,1200)],top=(27,24,33),fibers=200,shine=.62)
    c.lock([(464,99),(683,88),(724,454),(796,1200)],[(450,114),(600,178),(616,536),(669,1200)],fibers=310,shine=.70)
    c.lock([(465,108),(678,166),(669,959),(714,1200)],[(479,129),(756,245),(774,970),(820,1200)],top=(29,25,35),fibers=180,shine=.54)
    # Asymmetric fringe: separates into curved locks, revealing most of both eyes.
    c.lock([(426,106),(319,137),(298,348),(324,473)],[(443,123),(400,229),(422,373),(380,436)],top=(36,30,41),fibers=125,shine=.65)
    c.lock([(440,110),(390,174),(470,326),(414,488)],[(474,126),(524,230),(514,393),(414,488)],top=(34,28,40),fibers=155,shine=.72)
    c.lock([(470,114),(543,177),(549,363),(482,438)],[(487,124),(613,180),(629,364),(573,451)],top=(36,30,43),fibers=140,shine=.65)
    c.lock([(474,125),(635,162),(681,321),(600,453)],[(498,112),(698,168),(712,323),(624,439)],top=(31,27,37),fibers=120,shine=.55)
    # Continuous ribbon highlight bands along each major lock: the shine follows
    # the flow as one sweep instead of scattered hatch marks.
    for curve in [
        ([(438,116),(356,150),(300,300),(318,470)],(104,84,105),1.0),
        ([(466,114),(566,168),(600,318),(560,436)],(112,90,112),1.1),
        ([(178,220),(172,470),(146,760),(112,1050)],(96,77,99),.9),
        ([(700,250),(716,500),(742,780),(778,1030)],(99,79,101),.9),
        ([(402,180),(452,300),(452,410),(430,486)],(90,72,94),.7),
    ]:
        c.curve(curve[0],curve[1],curve[2])
        c.soft((curve[0][1][0]-46,curve[0][1][1]-46,curve[0][2][0]+46,curve[0][2][1]+46),
               curve[1],.10,34,crown if curve[0][0][1]<140 else None)
    # A few isolated flyaways establish an organic silhouette.
    for curve in [([(447,90),(413,52),(259,98),(211,241)],.7),([(691,272),(760,450),(757,572),(789,638)],.65),([(196,312),(151,424),(164,567),(142,691)],.7),([(166,669),(129,852),(111,954),(42,1045)],.65),([(723,689),(756,790),(767,852),(843,917)],.6)]:
        c.curve(curve[0],(48,39,54),curve[1])
    c.curve([(427,100),(491,83),(550,117),(580,148)],(75,61,82),.6)
    c.curve([(427,197),(465,310),(450,439),(400,516)],(46,36,50),.7)
    c.curve([(431,205),(471,325),(450,450),(410,502)],(84,62,80),.4)
    c.curve([(329,245),(300,340),(341,406),(317,504)],(51,39,55),.55)


def paint_horns(c):
    for side in (-1,1):
        def mapped(path):
            # Coordinates are authored in a small horn-centered frame.
            points=path_points(path)[0]
            return [(450+side*x,y) for x,y in points]
        pts=mapped('M 142 193 C 158 152 191 129 191 48 C 216 98 207 153 169 207 C 160 216 148 209 142 193 Z')
        mask=Image.new('L',c.size);ImageDraw.Draw(mask).polygon([c.point(p) for p in pts],fill=255)
        c.gradient(mask,(26,23,31),(14,13,19));c.line(pts+[pts[0]],(57,48,66),.9)
        c.curve([(450+side*154,191),(450+side*183,144),(450+side*205,97),(450+side*191,48)],(67,55,76),1.3)
        for i in range(5):
            y=97+i*20;x=450+side*(196-(y-97)*.32)
            c.curve([(x-side*7,y),(x,y+1),(x+side*11,y+7),(x+side*15,y+10)],(48,40,57),.7)


def render_natural(card, width=900, quality='standard', seed=7331, background='paper', checkpoint_dir=None, options=None, expression=None):
    iris=color(card.get('palette',{}).get('vermelhoIris'))
    if iris is None:raise ValueError('Ficha visual sem vermelhoIris #RRGGBB válido')
    c=Painter(width,quality,seed,background)
    c.options=normalize_options(options,expression)
    paint_background(c);paint_base(c);c.checkpoint('base_e_silhueta',checkpoint_dir)
    face=paint_face(c);c.checkpoint('rosto_e_volume',checkpoint_dir)
    paint_eye(c,True,iris);paint_eye(c,False,iris);paint_lips(c,face);c.checkpoint('olhos_e_expressao',checkpoint_dir)
    paint_clothing(c);paint_hair(c);c.checkpoint('mechas_e_roupa',checkpoint_dir)
    paint_horns(c)
    # Skin pores/paper-like marks are subtle and restricted to the face.
    for _ in range(150):
        x=c.rng.uniform(329,605);y=c.rng.uniform(450,703);px,py=c.point((x,y))
        if face.getpixel((px,py)):
            original=c.im.getpixel((px,py));c.ellipse((x,y,x+.28,y+.28),mix(original,(167,126,147),.05))
    c.checkpoint('acabamento',checkpoint_dir)
    report={'engine':'procedural-natural-portrait','engine_version':'2.3.0','dimensions':[c.width,c.height], 'seed':seed,
            'quality':quality,'background':background,'hair_fibers':c.fiber_count,'stages':c.stages,
            'reference_pixels_used':False,'pose':'front','controls':c.options,'semantic_fidelity_score':None}
    return c.result(),report
