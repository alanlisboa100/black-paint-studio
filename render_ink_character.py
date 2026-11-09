#!/usr/bin/env python3
"""Local gothic anime line-art and color study generator for Termux/Pillow.

This is a deterministic procedural illustration tool, not a diffusion model.
It creates clean layered line art at high resolution without API access.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent
S = 3
W, H = 1024, 1365
INK = (28, 29, 32, 255)
MID = (106, 108, 113, 255)
LIGHT = (190, 192, 196, 255)
PALE = (232, 233, 235, 255)
WHITE = (255, 255, 255, 255)


class InkCanvas:
    def __init__(self):
        self.image = Image.new('RGBA', (W*S, H*S), WHITE)
        self.draw = ImageDraw.Draw(self.image, 'RGBA')

    def point(self, p):
        return (round(p[0]*S), round(p[1]*S))

    def line(self, pts, fill=INK, width=2, joint='curve'):
        if len(pts) < 2: return
        self.draw.line([self.point(p) for p in pts], fill=fill, width=max(1, round(width*S)), joint=joint)

    def polygon(self, pts, fill, outline=INK, width=2):
        points = [self.point(p) for p in pts]
        self.draw.polygon(points, fill=fill)
        if outline:
            self.draw.line(points+[points[0]], fill=outline, width=max(1, round(width*S)), joint='curve')

    def ellipse(self, box, fill=None, outline=INK, width=2):
        b = tuple(round(v*S) for v in box)
        self.draw.ellipse(b, fill=fill, outline=outline, width=max(1, round(width*S)))

    def rect(self, box, fill=None, outline=INK, width=2):
        b = tuple(round(v*S) for v in box)
        self.draw.rectangle(b, fill=fill, outline=outline, width=max(1, round(width*S)))

    def cubic(self, p0, p1, p2, p3, fill=INK, width=2, steps=48):
        points = self.cubic_points(p0,p1,p2,p3,steps)
        # Pressure taper keeps locks, lashes and folds from ending like uniform wires.
        for i in range(len(points) - 1):
            t = (i + .5) / (len(points) - 1)
            pressure = .28 + .72 * (math.sin(math.pi * t) ** .42)
            p0s, p1s = self.point(points[i]), self.point(points[i + 1])
            stroke_width = max(1, round(width * pressure * S))
            self.draw.line([p0s, p1s], fill=fill, width=stroke_width)
            if i % 3 == 0 and stroke_width > 2:
                radius = stroke_width // 2
                x, y = p0s
                self.draw.ellipse((x-radius,y-radius,x+radius,y+radius), fill=fill)

    @staticmethod
    def cubic_points(p0,p1,p2,p3,steps=48):
        points=[]
        for i in range(steps+1):
            t=i/steps; u=1-t
            points.append((u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0],
                           u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]))
        return points

    def curved_shape(self, segments, bottom_points, fill, outline=INK, width=2):
        points=[]
        for segment in segments:
            curve=self.cubic_points(*segment, steps=30)
            points.extend(curve if not points else curve[1:])
        points.extend(bottom_points)
        self.polygon(points,fill,outline,width)

    def charm(self, x, y, size=17):
        self.line([(x,y-size),(x,y+size)], INK, 2)
        self.line([(x-size*.55,y-size*.18),(x+size*.55,y-size*.18)], INK, 3)
        self.polygon([(x,y-size*.18),(x+size*.35,y+size*.30),(x,y+size*.72),(x-size*.35,y+size*.30)], WHITE, INK, 1.5)


def colorize_mask(image: Image.Image, mask: Image.Image, *, dark, mid, light, strength=.55):
    """Tint a mask while retaining drawn light and shadow values."""
    mask = mask.filter(ImageFilter.GaussianBlur(.65))
    luminance = ImageOps.grayscale(image)
    palette = ImageOps.colorize(luminance, black=dark, mid=mid, white=light, midpoint=108)
    alpha = int(max(0, min(1, strength)) * 255)
    mask = ImageChops.multiply(mask, Image.new('L', image.size, alpha))
    return Image.composite(palette, image, mask)


def glaze_mask(image: Image.Image, mask: Image.Image, color, strength=.45):
    mask=mask.filter(ImageFilter.GaussianBlur(.5))
    mask=ImageChops.multiply(mask,Image.new('L',image.size,int(max(0,min(1,strength))*255)))
    return Image.composite(Image.new('RGB',image.size,color),image,mask)


def shape_mask(size, segments, tail=()):
    points=[]
    for segment in segments:
        curve=InkCanvas.cubic_points(*segment, steps=48)
        points.extend(curve if not points else curve[1:])
    points.extend(tail)
    mask=Image.new('L', size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    return mask


def strands_mask(size, curves, width):
    mask=Image.new('L',size,0)
    draw=ImageDraw.Draw(mask)
    for curve in curves:
        points=InkCanvas.cubic_points(*curve,steps=64)
        draw.line(points,fill=255,width=width,joint='curve')
    return mask


def colorize_region(image: Image.Image, points, *, dark, mid, light, strength=.55, subtract=None):
    mask=Image.new('L', image.size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    if subtract:
        cutout=Image.new('L', image.size, 0)
        ImageDraw.Draw(cutout).polygon(subtract, fill=255)
        mask=ImageChops.subtract(mask,cutout)
    return colorize_mask(image,mask,dark=dark,mid=mid,light=light,strength=strength)


def add_character_color(image: Image.Image) -> Image.Image:
    """Apply a restrained gothic palette to the existing line-art regions."""
    face_segments=[((465,286),(520,239),(623,246),(673,315)),((673,315),(720,386),(706,493),(670,561)),
                   ((670,561),(632,624),(580,666),(532,657)),((532,657),(482,648),(440,598),(421,526)),
                   ((421,526),(403,456),(412,353),(465,286))]
    face_mask=shape_mask(image.size,face_segments)
    hair_segments=[((385,293),(365,210),(396,126),(467,82)),((467,82),(518,35),(637,49),(690,98)),
                   ((690,98),(757,155),(751,239),(746,306)),((746,306),(841,438),(890,684),(950,1190))]
    hair_tail=[(826,1218),(771,924),(718,707),(658,542),(391,550),(333,744),(269,1015),(222,1220),(88,1186),(137,802),(224,500)]
    hair_mask=ImageChops.subtract(shape_mask(image.size,hair_segments,hair_tail),face_mask)
    image=colorize_mask(image,hair_mask,dark='#292a35',mid='#b4bdce',light='#fff4e7',strength=.72)

    outfit_segments=[((472,625),(431,684),(405,750),(355,783)),((355,783),(258,805),(155,829),(104,884)),
                     ((104,884),(40,1012),(45,1192),(75,1360)),((75,1360),(333,1380),(435,1355),(512,1360)),
                     ((512,1360),(647,1374),(816,1383),(953,1360)),((953,1360),(982,1180),(970,1023),(892,875)),
                     ((892,875),(794,813),(700,790),(655,757)),((655,757),(637,705),(622,663),(622,625)),
                     ((622,625),(571,657),(520,660),(472,625))]
    image=colorize_mask(image,shape_mask(image.size,outfit_segments,[(472,625)]),dark='#17131d',mid='#502338',light='#b9a5ad',strength=.82)
    # Coat and bodice keep their shadows, now with wine, plum and muted silver tones.
    bodice_segments=[((435,682),(462,699),(493,714),(526,720)),((526,720),(564,714),(593,700),(621,680)),
                     ((621,680),(662,770),(681,821),(691,920)),((691,920),(676,1118),(673,1265),(705,1360)),
                     ((705,1360),(584,1372),(460,1370),(347,1360)),((347,1360),(379,1243),(369,1081),(361,938)),
                     ((361,938),(368,831),(396,750),(435,682))]
    image=colorize_mask(image,shape_mask(image.size,bodice_segments),dark='#20131f',mid='#6b3049',light='#d6b8c3',strength=.88)
    # Put warm skin over the clothes mask at the jaw/neck overlap.
    image = colorize_mask(image, face_mask, dark='#754750', mid='#d99188', light='#ffe6d2', strength=.62)
    image = colorize_region(image, [(393,414),(426,414),(426,482),(393,482)], dark='#754750', mid='#d99188', light='#ffe6d2', strength=.62)
    image = colorize_region(image, [(672,407),(711,407),(711,475),(672,475)], dark='#754750', mid='#d99188', light='#ffe6d2', strength=.62)
    fringe=[((420,267),(402,326),(427,362),(450,385)),((446,204),(424,287),(457,331),(479,367)),
            ((486,149),(462,247),(491,306),(507,358)),((536,112),(517,218),(544,281),(545,355)),
            ((584,108),(594,218),(578,282),(586,354)),((633,131),(662,241),(627,304),(624,360)),
            ((677,183),(718,274),(675,335),(657,378)),((710,241),(744,314),(699,356),(681,390))]
    front_locks=[((412,280),(379,470),(411,661),(378,836)),((431,350),(400,552),(444,690),(416,817)),
                 ((694,280),(742,456),(692,630),(730,822)),((680,356),(724,530),(680,677),(699,830))]
    front_mask=ImageChops.lighter(strands_mask(image.size,fringe,11),strands_mask(image.size,front_locks,16))
    image=glaze_mask(image,front_mask,'#aab5ca',strength=.55)
    # Small ruby irises and cheek warmth give the face a clear focal point.
    for cx,cy,rx,ry in [(489,432,14,18),(617,432,14,18)]:
        iris=[(cx+math.cos(i*math.tau/40)*rx,cy+math.sin(i*math.tau/40)*ry) for i in range(40)]
        image=colorize_region(image,iris,dark='#321923',mid='#bb344e',light='#f18b83',strength=.92)

    # A faint lilac/rose wash is restricted to the connected paper background.
    # Flood isolation keeps the color from becoming a rectangular filter over the figure.
    threshold=ImageOps.grayscale(image).point(lambda p: 255 if p > 250 else 0)
    ImageDraw.floodfill(threshold,(0,0),128,thresh=0)
    background=threshold.point(lambda p: 255 if p == 128 else 0).filter(ImageFilter.GaussianBlur(.55))
    wash=Image.new('RGBA',image.size,(249,247,251,255))
    glow=Image.new('RGBA',image.size,(0,0,0,0))
    gd=ImageDraw.Draw(glow)
    gd.ellipse((185,80,850,800),fill=(187,168,222,78))
    gd.ellipse((95,725,440,1200),fill=(238,177,204,44))
    gd.ellipse((675,680,1010,1180),fill=(183,205,224,48))
    glow=glow.filter(ImageFilter.GaussianBlur(100))
    wash=Image.alpha_composite(wash,glow).convert('RGB')
    image=Image.composite(wash,image,background)
    return image


def horn(c, root, controls, tip, side):
    # Layered tapered curves make each horn read as sculpted, not a straight spike.
    p0=root; p1,p2=controls; p3=tip
    c.cubic(p0,p1,p2,p3,INK,18,64)
    c.cubic((p0[0]-side*4,p0[1]-2),(p1[0]-side*3,p1[1]),(p2[0]-side*2,p2[1]),p3,(84,86,90,255),10,64)
    c.cubic((p0[0]-side*7,p0[1]-4),(p1[0]-side*5,p1[1]-2),(p2[0]-side*4,p2[1]-3),p3,PALE,2,64)
    for i in range(1,7):
        t=i/8
        x=(1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t*t*p2[0]+t**3*p3[0]
        y=(1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t*t*p2[1]+t**3*p3[1]
        c.cubic((x-side*13,y-8),(x-side*9,y-3),(x+side*6,y+1),(x+side*13,y+5),INK,2,12)


def generate(style: str = 'color') -> Image.Image:
    if style == 'oil': style = 'color'  # compatibility with the mislabeled 1.6 option
    if style not in {'ink', 'color'}:
        raise ValueError('style deve ser color ou ink')
    c=InkCanvas()
    # Very light paper tone and a quiet framing line.

    # Rear hair mass, with tapered long locks behind the shoulders.
    c.curved_shape([
        ((385,293),(365,210),(396,126),(467,82)),((467,82),(518,35),(637,49),(690,98)),
        ((690,98),(757,155),(751,239),(746,306)),((746,306),(841,438),(890,684),(950,1190))
    ],[(826,1218),(771,924),(718,707),(658,542),(391,550),(333,744),(269,1015),(222,1220),(88,1186),(137,802),(224,500)],
       (247,247,248,255),INK,3)
    # broad strand shadows give the pale hair shape and depth
    for pts in [
        [(436,190),(348,388),(334,789),(231,1182)],[(476,152),(408,394),(411,721),(346,1158)],
        [(526,119),(497,348),(506,604),(472,1060)],[(601,119),(697,354),(685,593),(757,1137)],
        [(665,160),(775,390),(788,706),(863,1178)],[(376,278),(273,498),(242,742),(159,1118)],
        [(719,260),(839,484),(866,771),(918,1125)]]:
        c.cubic(*pts, (222,223,225,255), 13, 54)
        c.cubic(*pts, (255,255,255,255), 4, 54)

    # Fine, directional locks add layered linework across the pale hair.
    for i in range(15):
        t=i/14
        y0=112+t*174
        c.cubic((423+t*210,y0),(382+t*278,262+t*100),(312+t*405,405+t*45),(154+t*735,1110+t*62),
                (173,175,179,255) if i%3 else (207,208,211,255),1.35 if i%3 else 2.0,48)
    for i in range(10):
        t=i/9
        c.cubic((399,275+t*28),(330,430+t*36),(254,675+t*24),(135+t*56,1100+t*12),(181,183,187,255),1.4,44)
        c.cubic((736,282+t*25),(799,438+t*30),(867,698+t*24),(903-t*38,1110+t*12),(181,183,187,255),1.4,44)

    # Curved horns sit behind the front hair and are deliberately asymmetric.
    horn(c,(390,260),((303,198),(260,112)),(229,45),-1)
    horn(c,(713,255),((799,206),(827,116)),(810,25),1)

    # Neck, shoulders and an ornate gothic bodice.
    c.curved_shape([
        ((472,625),(431,684),(405,750),(355,783)),
        ((355,783),(258,805),(155,829),(104,884)),
        ((104,884),(40,1012),(45,1192),(75,1360)),
        ((75,1360),(333,1380),(435,1355),(512,1360)),
        ((512,1360),(647,1374),(816,1383),(953,1360)),
        ((953,1360),(982,1180),(970,1023),(892,875)),
        ((892,875),(794,813),(700,790),(655,757)),
        ((655,757),(637,705),(622,663),(622,625)),
        ((622,625),(571,657),(520,660),(472,625))
    ],[],(36,37,41,255),(18,19,23,255),3)
    # A sculpted gray bodice sits over the dark jacket, with curved seams for volume.
    c.curved_shape([
        ((435,682),(462,699),(493,714),(526,720)),
        ((526,720),(564,714),(593,700),(621,680)),
        ((621,680),(662,770),(681,821),(691,920)),
        ((691,920),(676,1118),(673,1265),(705,1360)),
        ((705,1360),(584,1372),(460,1370),(347,1360)),
        ((347,1360),(379,1243),(369,1081),(361,938)),
        ((361,938),(368,831),(396,750),(435,682))
    ],[],(69,70,75,255),(18,19,23,255),2.5)
    c.cubic((427,865),(378,1014),(374,1196),(348,1340),LIGHT,1.8)
    c.cubic((622,858),(669,1016),(675,1200),(705,1340),LIGHT,1.8)
    for x in [461,484,507,530,553,576,599]:
        c.ellipse((x-4,1000,x+4,1008), INK, None, 1)
        c.ellipse((x-4,1048,x+4,1056), INK, None, 1)
    for y in range(1015,1051,8):
        c.line([(466,y),(596,1063-y+1015)], MID, 1)
    # high collar, lace edging, seams and buckles
    c.polygon([(435,682),(525,715),(621,680),(648,749),(527,790),(409,747)], (48,49,53,255), INK, 2)
    c.cubic((418,752),(470,775),(578,775),(642,744),LIGHT,3)
    for i in range(13):
        x=429+i*15
        c.ellipse((x,752+(8 if i in (0,12) else 0),x+5,758+(8 if i in (0,12) else 0)), WHITE, INK, 1)
    c.rect((501,800,550,850),(246,246,247,255),INK,2)
    c.charm(526,873,26)
    # Harness straps and small metal fittings across the bodice.
    c.cubic((430,830),(456,910),(474,962),(498,1012),INK,9)
    c.cubic((624,829),(599,904),(579,964),(555,1012),INK,9)
    c.cubic((430,830),(456,910),(474,962),(498,1012),LIGHT,2)
    c.cubic((624,829),(599,904),(579,964),(555,1012),LIGHT,2)
    c.rect((474,947,494,972),(205,206,209,255),INK,2)
    c.rect((559,947,579,972),(205,206,209,255),INK,2)
    for x in [471,497,556,582]:
        c.ellipse((x-3,982,x+3,988),INK,None,1)

    # Face and ears: clear central area, soft jaw rather than a polygon mask.
    # Face silhouette uses tapered cheek/jaw curves and a slight turn; avoids the oval-mask look.
    c.curved_shape([
        ((465,286),(520,239),(623,246),(673,315)),
        ((673,315),(720,386),(706,493),(670,561)),
        ((670,561),(632,624),(580,666),(532,657)),
        ((532,657),(482,648),(440,598),(421,526)),
        ((421,526),(403,456),(412,353),(465,286))
    ],[],(255,255,255,255),INK,2.2)
    c.ellipse((393,414,426,482),(255,255,255,255),INK,1.5)
    c.ellipse((672,407,711,475),(255,255,255,255),INK,1.5)
    # cheek contours and subtle grayscale shadow
    c.cubic((431,476),(437,560),(475,619),(529,644),LIGHT,2)
    c.cubic((682,464),(664,554),(620,619),(548,650),LIGHT,2)
    c.ellipse((432,491,470,518),(241,242,243,255),None,1)
    c.ellipse((635,488,675,515),(241,242,243,255),None,1)

    # Matched eye templates keep the face balanced at this near frontal angle.
    for x, eye_w, eye_h, y in [(489,37,28,430),(617,37,28,430)]:
        c.cubic((x-eye_w,y),(x-eye_w*.65,y-eye_h*.9),(x+eye_w*.65,y-eye_h*1.12),(x+eye_w,y-2),INK,3.5)
        c.cubic((x-eye_w,y),(x-eye_w*.5,y+eye_h*.72),(x+eye_w*.45,y+eye_h*.82),(x+eye_w,y-2),INK,2.4)
        iris_w=14
        c.ellipse((x-iris_w,y-eye_h*.48,x+iris_w,y+eye_h*.68),(194,196,200,255),INK,1.7)
        c.ellipse((x-6,y-eye_h*.35,x+7,y+eye_h*.7),INK,None,1)
        c.ellipse((x-6,y-eye_h*.35,x-1,y-eye_h*.14),WHITE,None,1)
        for j in range(5):
            c.cubic((x-eye_w*.82+j*eye_w*.39,y-1),(x-eye_w*.88+j*eye_w*.39,y-7),(x-eye_w*.95+j*eye_w*.39,y-11),(x-eye_w*.98+j*eye_w*.39,y-13),INK,1.8,12)
        c.cubic((x-eye_w*.95,y-eye_h*.4),(x-eye_w*.5,y-eye_h*.95),(x+eye_w*.45,y-eye_h*1.0),(x+eye_w*.88,y-eye_h*.35),INK,3.2)
    # nose, mouth and chin accents follow the turned face axis.
    c.cubic((558,442),(554,462),(551,480),(563,483),MID,1.7)
    c.cubic((536,536),(550,527),(568,529),(586,536),INK,2.2)
    c.cubic((543,541),(557,546),(572,545),(582,539),LIGHT,1.5)
    c.ellipse((471,474,477,480),LIGHT,None,1); c.ellipse((646,469,652,475),LIGHT,None,1)

    # White layered fringe: locks frame the eyes and stop above the pupils.
    fringe=[
        ((420,267),(402,326),(427,362),(450,385)),((446,204),(424,287),(457,331),(479,367)),
        ((486,149),(462,247),(491,306),(507,358)),((536,112),(517,218),(544,281),(545,355)),
        ((584,108),(594,218),(578,282),(586,354)),((633,131),(662,241),(627,304),(624,360)),
        ((677,183),(718,274),(675,335),(657,378)),((710,241),(744,314),(699,356),(681,390))]
    for p0,p1,p2,p3 in fringe:
        c.cubic(p0,p1,p2,p3,(205,206,209,255),10,42)
        c.cubic(p0,p1,p2,p3,(255,255,255,255),7,42)
        c.cubic((p0[0]+4,p0[1]+5),(p1[0]+4,p1[1]+5),(p2[0]+4,p2[1]+5),(p3[0]+4,p3[1]+5),LIGHT,1,42)
    # Long front locks frame the face but do not run through the eyes.
    for pts in [
        ((412,280),(379,470),(411,661),(378,836)),((431,350),(400,552),(444,690),(416,817)),
        ((694,280),(742,456),(692,630),(730,822)),((680,356),(724,530),(680,677),(699,830))]:
        c.cubic(*pts, (205,206,209,255),15,54)
        c.cubic(*pts, WHITE,10,54)
        c.cubic((pts[0][0]+4,pts[0][1]),(pts[1][0]+4,pts[1][1]),(pts[2][0]+4,pts[2][1]),(pts[3][0]+4,pts[3][1]),LIGHT,1.3,54)

    # Hair ornaments, chains and crosses create the detailed gothic language.
    for x,y in [(350,275),(374,310),(744,287),(765,329),(447,273),(683,275)]:
        c.ellipse((x-7,y-7,x+7,y+7),(230,231,233,255),INK,2)
    for start,end in [((350,275),(386,358)),((744,287),(778,377)),((462,248),(516,193))]:
        x0,y0=start; x1,y1=end
        points=[]
        for i in range(25):
            t=i/24; points.append((x0+(x1-x0)*t,y0+(y1-y0)*t+5*((i%2)*2-1)))
        c.line(points,MID,2)
        for i in range(2,24,3):
            x,y=points[i]; c.ellipse((x-3,y-3,x+3,y+3),WHITE,INK,1)
    c.charm(778,427,22); c.charm(377,401,20); c.charm(608,735,18)

    # Fine folds and lace marks on the sleeves; keep background uncluttered.
    for side in [-1,1]:
        for i in range(7):
            x=526+side*(118+i*19)
            c.cubic((x,820),(x+side*42,924),(x+side*58,1081),(x+side*84,1288),LIGHT,1.4,32)
        c.cubic((526+side*96,910),(526+side*130,940),(526+side*170,948),(526+side*209,931),MID,2)
    for y in range(1110,1320,34):
        c.cubic((397,y),(472,y+12),(580,y+12),(655,y),LIGHT,1)

    result=c.image.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    if style == 'color':
        result=add_character_color(result)
    return result


def main():
    parser=argparse.ArgumentParser(description='Gera um estudo de personagem anime gótica colorido localmente, por CPU.')
    parser.add_argument('--output','-o',default='personagem_ink_anime.png',help='Arquivo PNG de saída')
    parser.add_argument('--style',choices=['ink','color','oil'],default='color',help='Acabamento colorido (oil é um alias legado) ou line art monocromática')
    args=parser.parse_args()
    output=Path(args.output).expanduser()
    if not output.is_absolute(): output=ROOT/output
    output.parent.mkdir(parents=True,exist_ok=True)
    generate(args.style).save(output,'PNG',optimize=False)
    print(f'Ilustração salva em: {output}')


if __name__=='__main__':
    main()
