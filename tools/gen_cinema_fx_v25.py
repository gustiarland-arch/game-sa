#!/usr/bin/env python3
"""Original v2.5 SFX & portrait accents, derived ONLY from the project's own supplied assets."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np, math, wave
ROOT=Path(__file__).resolve().parents[1]
SR=22050
for i,(name,freq,duration) in enumerate([('flower_pick',860,.33),('paper_fold',370,.30),('cinema_heartbeat',110,.65),('cinema_whoosh',275,.76)]):
 t=np.arange(int(SR*duration),dtype=np.float32)/SR
 rng=np.random.default_rng(2510+i)
 noise=rng.normal(0,.8,len(t)).astype(np.float32)
 if name=='cinema_heartbeat':
  sig=.25*np.sin(2*np.pi*(freq-40*t)*t)*(np.exp(-t*21)+.85*np.exp(-np.maximum(0,t-.28)*22)*(t>.28))
 elif name=='cinema_whoosh':
  sig=(np.sin(2*np.pi*(freq+380*t)*t)*.2+noise*.055)*np.sin(np.pi*t/duration)**2
 elif name=='paper_fold':
  sig=(noise*.13+np.sin(2*np.pi*freq*t)*.11)*np.exp(-t*17)
 else:
  sig=(np.sin(2*np.pi*(freq+250*t)*t)+.2*np.sin(2*np.pi*freq*1.5*t))*.18*np.exp(-t*12)
 sig=np.clip(sig,-.9,.9)
 dest=ROOT/'android/assets/audio/sfx'/f'{name}.wav'
 with wave.open(str(dest),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((sig*32767).astype('<i2').tobytes())
 print('SFX',name)

def heart(d,x,y,scale=3,color=(244,110,155,245)):
 # chunky pixel hearts, not sharp vector art
 u=scale
 pix=['0110110','1111111','1111111','0111110','0011100','0001000']
 for j,row in enumerate(pix):
  for k,v in enumerate(row):
   if v=='1':d.rectangle((x+k*u,y+j*u,x+k*u+u-1,y+j*u+u-1), fill=color)
for who in ('arland','sofia'):
 dr=ROOT/'android/assets/characters'/who/'portraits'
 for label,base in [('jatuh_cinta','malu'),('khawatir','sedih'),('lega','senang')]:
  img=Image.open(dr/(base+'.png')).convert('RGBA'); d=ImageDraw.Draw(img,'RGBA')
  if label=='jatuh_cinta':
   heart(d,141,24,3);heart(d,13,58,2,(255,143,174,190))
   d.ellipse((110,122,119,127),fill=(245,109,139,70))
  elif label=='khawatir':
   d.polygon([(143,36),(137,52),(144,57),(149,52)],fill=(120,178,217,200))
   d.line([(141,45),(140,51)],fill=(224,248,255,190),width=2)
  else:
   d.ellipse((142,27,151,36),fill=(255,245,195,175))
   d.line([(140,33),(153,33)],fill=(255,241,191,155),width=2)
  img.save(dr/(label+'.png'))
  print('Portrait',who,label)
