#!/usr/bin/env python3
"""CPU portrait study painted in overlapping masses, not exposed contour lines."""
from __future__ import annotations
import argparse, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops
W,H=900,1200

def bezier(p0,p1,p2,p3,n=50):
    return [((1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t*t*p2[0]+t**3*p3[0],
             (1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t*t*p2[1]+t**3*p3[1]) for t in (i/n for i in range(n+1))]

def path(draw,segments,color,width=3):
    pts=[]
    for seg in segments: pts.extend(bezier(*seg))
    draw.line(pts,fill=color,width=width,joint='curve')

def shape(draw,segments,color):
    pts=[]
    for seg in segments: pts.extend(bezier(*seg))
    draw.polygon(pts,fill=color)

def shade(im,mask,xy,radius,color,alpha):
    overlay=Image.new('RGBA',im.size,(0,0,0,0))
    ImageDraw.Draw(overlay).ellipse((xy[0]-radius,xy[1]-radius,xy[0]+radius,xy[1]+radius),fill=(*color,alpha))
    overlay=overlay.filter(ImageFilter.GaussianBlur(radius*.35))
    overlay.putalpha(ImageChops.multiply(overlay.getchannel('A'),mask))
    return Image.alpha_composite(im,overlay)

def render():
    rng=random.Random(83)
    im=Image.new('RGBA',(W,H),(36,29,40,255))
    bg=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(bg,'RGBA')
    for y in range(H):
        t=y/H; d.line((0,y,W,y),fill=(int(37+36*t),int(28+22*t),int(42+32*t),255))
    im=Image.alpha_composite(im,bg); d=ImageDraw.Draw(im,'RGBA')
    d.arc((95,-174,805,782),10,170,fill=(141,77,89,98),width=12)
    d.arc((146,-113,752,665),8,171,fill=(99,62,83,120),width=4)
    for cx,cy in [(96,740),(815,740)]:
        d.line((cx,0,cx,1060),fill=(52,37,51,160),width=15)
        d.ellipse((cx-13,cy-15,cx+13,cy+15),fill=(235,145,103,220))
    # Two dark back masses share the same scalp; layered locks retain volume.
    hair=[((253,316),(237,132),(339,102),(433,92)),((433,92),(592,82),(702,172),(699,333)),
          ((699,333),(723,584),(778,832),(834,1132)),((834,1132),(686,1189),(627,1067),(592,909)),
          ((592,909),(504,859),(393,850),(291,930)),((291,930),(253,1107),(175,1174),(78,1128)),
          ((78,1128),(133,752),(216,494),(253,316))]
    shape(d,hair,(18,19,31,255))
    hair_mask=Image.new('L',(W,H),0);shape(ImageDraw.Draw(hair_mask),hair,255)
    im=shade(im,hair_mask,(354,318),335,(105,61,79),94)
    im=shade(im,hair_mask,(677,703),363,(77,62,99),70)
    d=ImageDraw.Draw(im,'RGBA')
    # Bodice and sleeves are broad shaded masses with narrow trim.
    shape(d,[((337,778),(225,795),(120,856),(78,1200)),((78,1200),(307,1210),(440,1195),(468,1199)),
             ((468,1199),(607,1198),(748,1215),(827,1200)),((827,1200),(773,848),(657,789),(558,777)),
             ((558,777),(494,790),(394,790),(337,778))],(32,25,37,255))
    d.polygon([(351,816),(450,930),(553,816),(652,1200),(250,1200)],fill=(74,36,52,255))
    d.polygon([(369,832),(450,915),(533,832),(493,932),(450,974),(412,931)],fill=(33,26,40,255))
    for side in [-1,1]:
        x=450+side*148
        path(d,[((x,900),(x+side*25,1003),(x+side*87,1080),(x+side*109,1192))],(128,77,87,160),5)
        path(d,[((x,927),(x+side*46,984),(x+side*57,1054),(x+side*90,1133))],(212,126,111,75),3)
    # Neck starts behind the jaw. Its shadow anchors the head to the collar.
    shape(d,[((377,633),(389,716),(365,790),(347,809)),((347,809),(421,847),(483,861),(556,807)),
             ((556,807),(526,758),(523,653),(514,625)),((514,625),(460,653),(411,648),(377,633))],(197,137,132,255))
    d.polygon([(367,779),(449,813),(536,779),(554,832),(450,885),(344,832)],fill=(39,31,42,255))
    d.arc((350,777,550,866),14,163,fill=(201,139,126,165),width=4)
    # Face silhouette, shaded within its own mask to preserve a clean jaw.
    face=[((350,297),(407,232),(529,246),(586,312)),((586,312),(631,367),(639,475),(605,560)),
          ((605,560),(582,652),(527,719),(456,740)),((456,740),(371,729),(322,651),(297,550)),
          ((297,550),(269,445),(289,354),(350,297))]
    m=Image.new('L',(W,H),0); shape(ImageDraw.Draw(m),face,255)
    shape(d,face,(235,184,172,255))
    im=shade(im,m,(605,508),205,(108,65,82),85)
    im=shade(im,m,(348,428),160,(255,224,198),92)
    im=shade(im,m,(477,682),126,(205,126,129),53)
    im=shade(im,m,(363,533),91,(242,124,130),36)
    im=shade(im,m,(548,534),93,(207,109,135),31)
    im=shade(im,m,(457,396),145,(255,221,198),42)
    d=ImageDraw.Draw(im,'RGBA')
    d.ellipse((286,484,319,545),fill=(222,165,160,255))
    d.ellipse((612,484,643,542),fill=(176,114,122,255))
    d.arc((290,500,324,548),220,85,fill=(99,60,72,150),width=3)
    d.arc((610,500,641,546),90,335,fill=(92,56,69,150),width=3)
    # Connected root shadow and dark crown wrap the forehead rather than floating.
    shape(d,[((264,344),(271,181),(368,115),(454,118)),((454,118),(567,113),(659,192),(650,347)),
             ((650,347),(616,381),(592,390),(576,357)),((576,357),(476,316),(376,349),(312,417)),
             ((312,417),(290,391),(264,365),(264,344))],(23,20,30,255))
    shape(d,[((301,329),(363,239),(414,188),(468,216)),((468,216),(451,284),(417,353),(368,405)),
             ((368,405),(364,360),(331,336),(301,329))],(36,28,41,255))
    shape(d,[((450,190),(505,171),(586,227),(617,298)),((617,298),(570,350),(551,408),(515,430)),
             ((515,430),(507,358),(474,295),(450,190))],(31,25,37,255))
    # Tapered overlapping locks start at the part and cast a shadow onto the forehead.
    shape(d,[((434,185),(459,221),(472,255),(480,287)),((480,287),(467,321),(452,352),(442,361)),
             ((442,361),(433,327),(426,262),(434,185))],(59,37,53,255))
    shape(d,[((486,180),(541,196),(584,251),(594,290)),((594,290),(571,325),(545,352),(523,376)),
             ((523,376),(538,307),(517,235),(486,180))],(45,31,47,255))
    # Crown-to-side connection: thick locks pass around eyes and attach to scalp.
    shape(d,[((301,343),(283,457),(258,606),(236,758)),((236,758),(215,939),(181,1075),(144,1159)),
             ((144,1159),(256,1208),(321,1041),(337,855)),((337,855),(329,644),(349,468),(368,405)),
             ((368,405),(351,365),(318,341),(301,343))],(26,22,34,255))
    shape(d,[((596,314),(638,371),(669,514),(673,633)),((673,633),(694,856),(735,1030),(799,1155)),
             ((799,1155),(686,1196),(625,1039),(597,884)),((597,884),(604,647),(561,462),(515,430)),
             ((515,430),(549,406),(575,340),(596,314))],(24,22,35,255))
    # Hair part and root-driven locks cast real shadows over the upper face.
    for seg in [((378,183),(381,254),(353,318),(343,448)),
                ((430,168),(417,252),(422,326),(404,391)),
                ((475,158),(473,231),(509,311),(515,430)),
                ((544,185),(581,265),(588,349),(568,407))]:
        path(d,[seg],(121,77,92,108),rng.randint(4,9))
    path(d,[((348,313),(385,275),(413,225),(425,181))],(159,95,108,91),7)
    path(d,[((520,196),(579,259),(582,318),(543,378))],(149,79,100,98),8)
    # Full paired eyes on the same tilted facial axis; dark upper lashes.
    for x in (370,542):
        y=494
        d.ellipse((x-39,y-21,x+41,y+29),fill=(247,222,209,255))
        d.ellipse((x-20,y-18,x+20,y+29),fill=(137,40,58,255))
        d.ellipse((x-11,y-12,x+12,y+26),fill=(79,24,40,255))
        d.ellipse((x-17,y-13,x-5,y-1),fill=(255,238,214,245))
        d.ellipse((x+8,y+5,x+12,y+9),fill=(245,163,154,160))
        d.arc((x-43,y-29,x+43,y+25),180,357,fill=(39,28,40,255),width=7)
        d.arc((x-38,y-6,x+40,y+34),5,160,fill=(84,54,66,210),width=2)
        path(d,[((x-40,y-43),(x-9,y-60),(x+24,y-57),(x+39,y-42))],(67,39,49,205),5)
        for i in range(3):
            lx=x+32+i*5
            path(d,[((lx,y-21),(lx+6,y-27),(lx+7,y-31),(lx+7,y-34))],(45,30,44,225),2)
    path(d,[((455,520),(451,551),(443,579),(459,582))],(115,67,77,110),2)
    d.ellipse((453,584,465,589),fill=(143,80,86,111))
    path(d,[((418,632),(435,621),(470,627),(493,630))],(139,64,73,196),3)
    path(d,[((423,646),(446,659),(471,653),(488,635))],(215,112,110,158),2)
    d.ellipse((439,629,468,638),fill=(247,178,163,74))
    # A curved dark cap shares the crown's exact width; horn roots disappear under it.
    d.polygon([(300,236),(350,159),(408,143),(452,160),(537,138),(594,159),(642,236),(650,265),(300,265)],fill=(25,23,31,255))
    d.ellipse((308,218,646,298),fill=(31,28,36,255),outline=(90,55,67,255),width=3)
    d.arc((324,224,630,288),190,346,fill=(152,81,93,148),width=3)
    path(d,[((343,209),(399,171),(511,177),(586,207))],(143,83,93,84),3)
    for side in (-1,1):
        root=(450+side*145,207); tip=(450+side*165,55)
        path(d,[(root,(root[0]+side*83,150),(tip[0]+side*43,86),tip)],(14,16,24,255),22)
        path(d,[(root,(root[0]+side*75,150),(tip[0]+side*37,85),tip)],(132,83,94,175),5)
        for band in (110,151):
            bx=root[0]+side*(36+(151-band)*.3)
            d.line((bx-side*9,band,bx+side*11,band-5),fill=(145,99,102,161),width=2)
    # Detached locks no longer hide the eyes; restrained specular strokes.
    for seg in [((302,426),(274,624),(286,814),(207,1113)),
                ((335,434),(329,637),(307,811),(268,1051)),
                ((592,416),(641,625),(623,804),(714,1093)),
                ((630,405),(689,621),(689,835),(764,1079))]:
        path(d,[seg],(148,91,104,88),5)
    for side in (-1,1):
        for x0,y0,x1,y1,ex,ey in [(139,343,163,533,187,746),(174,402,181,561,213,671),
                                   (118,497,149,670,211,891)]:
            path(d,[((450+side*x0,y0),(450+side*x1,y1),
                     (450+side*(x1+19),ey-89),(450+side*ex,ey))],
                 (148,87,108,57),3)
        earx=450+side*162
        d.ellipse((earx-5,567,earx+5,577),fill=(197,164,151,255),outline=(86,65,76,255),width=2)
        d.line((earx,576,earx,613),fill=(200,152,135,210),width=2)
        d.line((earx-9,593,earx+9,593),fill=(200,152,135,210),width=2)
        d.polygon([(earx,607),(earx+4,615),(earx,625),(earx-4,615)],fill=(115,40,58,245))
    d.polygon([(437,276),(452,289),(466,275),(452,250)],fill=(109,37,59,255))
    # Layered collar, lace and three small fasteners break up the flat torso.
    d.polygon([(361,806),(450,846),(535,806),(548,840),(451,888),(349,840)],fill=(31,26,37,255))
    path(d,[((360,814),(400,837),(430,866),(450,863))],(169,104,115,144),3)
    path(d,[((450,863),(481,862),(503,826),(538,811))],(169,104,115,144),3)
    for yy in (949,1002,1055):
        d.ellipse((445,yy-5,456,yy+6),fill=(202,144,116,255))
        d.ellipse((449,yy-2,453,yy+2),fill=(252,205,154,255))
    for side in (-1,1):
        path(d,[((450+side*80,891),(450+side*92,1002),(450+side*88,1128),(450+side*109,1200))],(163,98,112,115),3)
    d.ellipse((446,933,457,945),fill=(209,149,114,255))
    path(d,[((451,945),(452,972),(447,998),(452,1021))],(216,158,122,200),3)
    return im.convert('RGB')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Retrato pintado por massas em CPU.')
    parser.add_argument('--output',default='personagem_pintado.png')
    args=parser.parse_args()
    dest=Path(args.output).expanduser(); dest.parent.mkdir(parents=True,exist_ok=True)
    render().save(dest,'PNG',optimize=True)
    print(dest)
