#!/usr/bin/env python3
"""Five original editable local pixel-icon sources for Chapter5, 192x192 RGBA."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];dst=ROOT/'android/assets/items';dst.mkdir(parents=True,exist_ok=True)
palette={'clock':('#322e52','#f0bf91','#a8c5d1'), 'mirror':('#24435d','#a5d8dc','#ffc4ba'),
         'star':('#2f3655','#fce8aa','#b1beed'),'book':('#443151','#f5c5ba','#b4dce9'),
         'bridge':('#394565','#e3d9c4','#b8c9ef')}
def make(name):
 bg,main,light=palette[name];im=Image.new('RGBA',(48,48));d=ImageDraw.Draw(im)
 d.rounded_rectangle((2,2,45,45),radius=7,fill=bg,outline='#9c9db9',width=2)
 if name=='clock':
  d.ellipse((8,8,40,40),fill='#586077',outline=main,width=3)
  for x,y in [(24,11),(37,24),(24,37),(11,24)]:d.rectangle((x-2,y-2,x+2,y+2),fill=light)
  d.line((24,24,24,13),fill=main,width=3);d.line((24,24,33,30),fill=light,width=3)
 elif name=='mirror':
  d.ellipse((8,7,40,40),fill='#537a90',outline=main,width=3)
  d.arc((11,10,38,38),90,270,fill=light,width=3);d.line((24,11,24,36),fill=light,width=1)
 elif name=='star':
  d.polygon([(24,6),(29,19),(43,20),(32,29),(35,42),(24,34),(13,42),(16,29),(5,20),(19,19)],fill=main,outline=light)
 elif name=='book':
  d.polygon([(6,14),(22,18),(24,38),(7,34)],fill='#d18b9e',outline=main)
  d.polygon([(42,14),(26,18),(24,38),(41,34)],fill=light,outline=main)
  d.line((24,17,24,39),fill='#efdfcd',width=2)
 else:
  d.polygon([(3,34),(13,27),(20,22),(26,22),(36,27),(45,34),(45,43),(3,43)],fill=light,outline=main)
  for x in (9,18,27,36):d.line((x,34,x+3,43),fill=main,width=2)
 d.rectangle((4,44,43,45),fill=main)
 out=dst/('v471_c05_'+name+'.png');im.resize((192,192),Image.Resampling.NEAREST).save(out,optimize=True)
 print('generated',out.name)
for key in palette:make(key)
