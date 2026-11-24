#!/usr/bin/env python3
"""Remove pale matte/background leakage from v4.1 sprite atlas crops.

Original legacy PNG files stay available under art_source/world_v42/baseline_props.
Collision footprints and filenames are unchanged; reproducible, idempotent.
"""
from pathlib import Path
import hashlib, shutil, argparse
from collections import deque
import numpy as np
# Only Pillow + numpy required; do not add SciPy dependency to project builds.
def dilate(a,n=1):
 for _ in range(n):
  b=a.copy()
  b[1:,:] |= a[:-1,:];b[:-1,:] |= a[1:,:]
  b[:,1:] |= a[:,:-1];b[:,:-1] |= a[:,1:]
  a=b
 return a

def edge_flood(pale):
 h,w=pale.shape;seen=np.zeros((h,w),dtype=bool);q=deque()
 for x in range(w):
  if pale[0,x] and not seen[0,x]:seen[0,x]=True;q.append((0,x))
  if pale[h-1,x] and not seen[h-1,x]:seen[h-1,x]=True;q.append((h-1,x))
 for y in range(h):
  if pale[y,0] and not seen[y,0]:seen[y,0]=True;q.append((y,0))
  if pale[y,w-1] and not seen[y,w-1]:seen[y,w-1]=True;q.append((y,w-1))
 while q:
  y,x=q.popleft()
  for ny,nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
   if 0<=ny<h and 0<=nx<w and pale[ny,nx] and not seen[ny,nx]:
    seen[ny,nx]=True;q.append((ny,nx))
 return seen
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
SRCD=ROOT/'android/assets/props'; BASE=ROOT/'art_source/world_v42/baseline_props'
BASE.mkdir(parents=True,exist_ok=True)

def clean(src):
 rgba=np.array(src.convert('RGBA'))
 rgb=rgba[:,:,:3].astype(np.int16);r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
 mx=np.max(rgb,axis=2);mn=np.min(rgb,axis=2)
 # Pale gray / ivory / lilac sheet background differs from colored pixel art.
 pale=(mn>=204)&((mx-mn)<=39)&(rgba[:,:,3]>0)
 # Segmented pale background from outer edge first; retain bright highlights
 # within detailed sprite silhouettes.
 borders=np.zeros(pale.shape,bool);borders[:3,:]=True;borders[-3:,:]=True;borders[:,:3]=True;borders[:,-3:]=True
 connected=edge_flood(pale)
 # near-white speckles are a product of the original matte, not useful art.
 verypale=(mn>=236)&((mx-mn)<=22)
 erase=connected | verypale
 # antialias colors similar to white background gently fade.
 alpha=rgba[:,:,3].astype('float32')
 alpha[erase]=0
 fringe=dilate(erase,1) & ~erase
 fringe2=dilate(erase,2) & ~erase
 alpha[fringe]*=.65
 alpha[fringe2&~fringe]*=.87
 rgba[:,:,3]=np.clip(alpha,0,255).astype(np.uint8)
 return Image.fromarray(rgba,'RGBA')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--verify',action='store_true'); args=ap.parse_args()
 files=sorted(SRCD.glob('v41_*.png'))
 fixed=0
 for p in files:
  src=BASE/p.name
  if not src.exists() and not args.verify:shutil.copy2(p,src)
  if not src.is_file():raise RuntimeError('missing baseline '+str(src))
  with Image.open(src) as original:
   base=original.convert('RGBA'); output=clean(base)
  with Image.open(p) as active:
   if args.verify:
    assert active.size==base.size
    assert np.array_equal(np.asarray(active.convert('RGBA')),np.asarray(output)),p
    fixed+=1;continue
  output.save(p,compress_level=5)
  fixed+=1
 print('V4.2 MATTE', 'VERIFIED' if args.verify else 'CLEANED',fixed,'v41 prop sprites')
if __name__=='__main__':main()
