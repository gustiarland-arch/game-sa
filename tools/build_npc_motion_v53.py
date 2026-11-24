#!/usr/bin/env python3
"""v5.3 reproducible pixel-art animation upgrade. Source v5.2 atlases remain untouched.
Produces 24-frame walking / 12-frame idle motion sheets, 8-direction for playable leads,
22 individualized NPC style sheets and pose sheets. All at 48x72 per frame.
No sprite/background upscaling or changes to collision footprint.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import json, math, hashlib

BASE=Path(__file__).resolve().parent.parent
DIR=BASE/"android/assets/characters"
FW,FH=48,72
STYLE={
 "raka":("apron",(190,99,67),(253,218,148)),
 "rini":("satchel",(158,112,219),(245,203,111)),
 "sari":("cane",(190,160,110),(235,210,150)),
 "melati":("flower",(234,119,145),(250,211,116)),
 "tigor":("cap",(84,149,128),(255,203,92)),
 "laras":("glasses",(131,190,198),(244,205,116)),
 "dito":("child_cap",(228,101,84),(255,223,112)),
 "wulan":("scarf",(221,165,104),(249,223,183)),
 "juna":("backpack",(93,154,223),(251,159,101)),
 "bimo":("school",(112,119,219),(248,199,104)),
 "tika":("bow",(229,130,178),(252,204,221)),
 "darto":("guard",(76,114,158),(244,209,113)),
 "harun":("gardener",(122,151,81),(244,203,111)),
 "ujang":("courier",(235,173,70),(255,229,155)),
 "ina":("chef",(164,121,172),(255,224,167)),
 "pos":("mail",(219,132,71),(251,220,154)),
 "nara":("star",(119,134,210),(231,215,126)),
 "bayu":("headphone",(101,177,205),(250,187,104)),
 "eko":("toolbelt",(209,118,90),(235,183,114)),
 "darmo":("scholar",(153,157,164),(255,232,181)),
 "rara":("ribbon",(131,167,237),(255,193,151)),
 "udin":("leaf",(124,175,102),(245,210,128))
}
def ink(c):return (43,37,55,255)
def c4(c):return tuple(c)+(255,)
def outline_rect(d, rect, fill, edge=(43,37,55)):
 d.rectangle(rect,fill=c4(fill),outline=c4(edge))
def adorn(tile,role,primary,accent,direction,phase,idle=False):
 """Place visible signature items on each native-resolution directional frame.
 Facial accessories are frontal only; torso accessories follow all directions.
 Body coordinates are stable for all existing NPC atlases and poses.
 """
 d=ImageDraw.Draw(tile)
 dark=(46,38,55)
 if role in ("apron","chef","gardener"):
  outline_rect(d,(19,39,29,54),primary)
  d.line((20,42,28,42), fill=c4(accent),width=1)
  if role=="apron":
   d.ellipse((22,45,26,49),fill=c4(accent),outline=c4(dark))
  elif role=="chef":
   d.rectangle((22,45,26,49),fill=c4(accent))
  else:
   d.line((22,44,27,48),fill=c4(accent),width=2)
 if role in ("satchel","mail","courier","school","backpack"):
  d.line((18,36,32,49), fill=c4(dark),width=3)
  d.line((19,36,31,48), fill=c4(accent),width=1)
  outline_rect(d,(30,48,36,54),primary)
  if role in ("mail","courier"):d.line((31,50,35,50),fill=c4(accent))
 if role in ("scarf","scholar"):
  d.line((17,35,31,35),fill=c4(dark),width=4)
  d.line((18,35,30,35),fill=c4(primary),width=2)
  d.line((29,36,27,43),fill=c4(accent),width=2)
 if role in ("cap","child_cap","guard","courier","gardener","leaf"):
  top=8 if role!="child_cap" else 13
  outline_rect(d,(15,top,32,top+4),primary)
  d.line((17,top+1,29,top+1),fill=c4(accent))
  if direction==0:d.line((21,top+5,36,top+5),fill=c4(primary),width=2)
  if role=="leaf":d.ellipse((25,top-3,30,top+1), fill=c4(accent),outline=c4(dark))
 if role in ("flower","ribbon","bow","star"):
  x,y=34,(17 if role!="flower" else 23)
  d.rectangle((x-1,y-1,x+1,y+1),fill=c4(primary))
  d.point((x-2,y),fill=c4(accent));d.point((x+2,y),fill=c4(accent))
  d.point((x,y-2),fill=c4(accent));d.point((x,y+2),fill=c4(accent))
  if role=="flower":
   d.line((33,25,30,30),fill=c4((97,158,99)))
  if role=="star":
   d.point((x-3,y-3),fill=c4(accent))
 if role in ("glasses","scholar","cane"):
  if direction == 0:
   for left in [15,25]:
    d.rectangle((left,26,left+7,30),outline=c4(primary))
   d.line((23,27,25,27),fill=c4(primary))
  if role=="cane":
   d.line((39,47,39,65),fill=c4(dark),width=3)
   d.line((38,47,38,65),fill=c4(primary),width=1)
 if role in ("headphone",):
  d.arc((14,11,34,31),185,352,fill=c4(primary),width=3)
  d.rectangle((13,20,15,27),fill=c4(accent))
  d.rectangle((32,20,34,27),fill=c4(accent))
 if role in ("toolbelt","guard"):
  d.rectangle((17,47,31,49),fill=c4(primary))
  for x in (19,26):d.rectangle((x,48,x+2,51),fill=c4(accent))
  if role=="guard":d.rectangle((25,42,29,45),fill=c4(accent),outline=c4(dark))
 if role in ("child_cap",):
  d.ellipse((14,15,17,18),fill=c4(accent))
 if role in ("school",):d.line((23,38,26,43),fill=c4(primary),width=2)
 if role in ("leaf",):d.ellipse((33,42,36,46),fill=c4(accent))
 if role in ("gardener",):d.line((35,45,39,50),fill=c4(primary),width=2)
 if role in ("apron","chef","gardener","school","guard","toolbelt"):
  # Small palette highlight defines individual occupation even from rear view.
  d.point((21,42),fill=c4(accent))
 if idle:
  # Cloth breathing: a subtle one-pixel crease actually changes phase,
  # without modifying feet or the sprite's silhouette.
  if phase%3==1:d.line((20,42,25,42),fill=c4(accent))
  elif phase%3==2:d.line((22,43,27,43),fill=c4(accent))
 return tile

def make_atlas(name, source, phases, which, directions, role=None, colors=None):
 src=Image.open(source).convert('RGBA')
 assert src.height==directions*FH and src.width%FW==0,(source,src.size)
 old=src.width//FW
 target=Image.new("RGBA",(phases*FW,directions*FH))
 for direction in range(directions):
  for phase in range(phases):
   # Frames are authored from original art; sample with consistent gait period.
   old_frame=(phase*old//phases)%old
   im=src.crop((old_frame*FW,direction*FH,(old_frame+1)*FW,(direction+1)*FH))
   if which=="walk":
    # one-pixel, nearest-pixel animation in-tween for limb rhythm; never alter feet collision coordinates.
    shift = (1 if phase%6==2 else -1 if phase%6==5 else 0)
    if shift:
     moving=Image.new("RGBA",(FW,FH))
     moving.alpha_composite(im,(shift,0))
     im=moving
   else:
    dx=(1 if phase in (1,7) else -1 if phase in (4,10) else 0)
    dy=-1 if phase in (3,9) else 0
    if dx or dy:
     moving=Image.new("RGBA",(FW,FH));moving.alpha_composite(im,(dx,dy));im=moving
   if role:
    im=adorn(im,role,colors[0],colors[1],direction%4,phase,which=="idle")
   target.alpha_composite(im,(phase*FW,direction*FH))
 target.save(DIR/name/("idle_v53.png" if which=="idle" else "walk_v53.png")
             if directions==4 else DIR/name/("idle_8dir_v53.png" if which=="idle" else "walk_8dir_v53.png"),optimize=True)
 return target

def make_pose(name,role,palette):
 original=DIR/name/"poses.png"
 im=Image.open(original).convert("RGBA")
 assert im.size==(384,1152),im.size
 out=Image.new("RGBA",im.size)
 for row in range(im.height//FH):
  for col in range(8):
   tile=im.crop((col*FW,row*FH,(col+1)*FW,(row+1)*FH))
   tile=adorn(tile,role,palette[0],palette[1],col//2,col%2)
   out.alpha_composite(tile,(col*FW,row*FH))
 out.save(DIR/name/"poses_v53.png",optimize=True)

def main():
 manifest={"version":"5.3.0","frame_size":[48,72],"walk_frames":24,"idle_frames":12,
           "styles":{},"sprites":[],"source":"Legacy v5.2 sprite atlases remain unchanged"}
 for name in sorted(d.name for d in DIR.iterdir() if d.is_dir()):
  npc=name in STYLE
  role,p,a = STYLE[name] if npc else (None,None,None)
  walk=make_atlas(name,DIR/name/"walk_v37.png",24,"walk",4,role,(p,a) if npc else None)
  idle=make_atlas(name,DIR/name/"idle_v37.png",12,"idle",4,role,(p,a) if npc else None)
  if npc:
   make_pose(name,role,(p,a))
   manifest["styles"][name]={"role":role,"primary":p,"accent":a}
  if name in ("arland","sofia"):
   make_atlas(name,DIR/name/"walk_8dir_v462.png",24,"walk",8)
   make_atlas(name,DIR/name/"idle_8dir_v462.png",12,"idle",8)
  manifest["sprites"].append(name)
 assert len(manifest["sprites"])==25 and len(manifest["styles"])==22
 destination=BASE/"docs"/"MOTION_NPC_V53_ASSET_MANIFEST.json"
 destination.parent.mkdir(parents=True,exist_ok=True)
 destination.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("v5.3 animation:",len(manifest["sprites"]),"characters,",len(manifest["styles"]),"individual NPC designs")
if __name__=="__main__":main()
