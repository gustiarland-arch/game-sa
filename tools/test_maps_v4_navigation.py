#!/usr/bin/env python3
"""Verify each v4 map has spawn-rooted access to its own objectives & portals."""
from pathlib import Path
from collections import deque
import math,json
R=Path(__file__).resolve().parent.parent
D=R/'android/assets/data';M=json.loads((D/'maps.json').read_text())['areas'];Q=json.loads((D/'quests.json').read_text());ids=[k for k,m in M.items() if m.get('v4Layout')=='handcrafted_16bit']
STEP=8

def blocked(m,x,y):
 if x-9<0 or x+9>m['w'] or y-6<0 or y+2>m['h']:return True
 return any(x-9<xx+w and x+9>xx and y-6<yy+h and y+2>yy for xx,yy,w,h in m['walls'])

def visit(a):
 m=M[a];sx,sy=m['spawn'];origin=(int(sx//STEP),int(sy//STEP));seen={origin};queue=deque([origin]);gridw=math.ceil(m['w']/STEP);gridh=math.ceil(m['h']/STEP)
 while queue:
  x,y=queue.popleft()
  for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
   nx,ny=x+dx,y+dy
   if nx<0 or ny<0 or nx>=gridw or ny>=gridh or (nx,ny) in seen:continue
   if blocked(m,nx*STEP+4,ny*STEP+4):continue
   seen.add((nx,ny));queue.append((nx,ny))
 return seen

def near(seen,x,y,r):
 lo=int((x-r)//STEP);hi=int((x+r)//STEP);ly=int((y-r)//STEP);hy=int((y+r)//STEP)
 return any((ix,iy) in seen and math.hypot(ix*STEP+4-x,iy*STEP+4-y)<=r for ix in range(lo,hi+1) for iy in range(ly,hy+1))

checks=0;fail=[]
for a in ids:
 m=M[a];seen=visit(a)
 checks+=1
 if len(seen)<600:fail.append((a,'walkable cells disconnected',len(seen)))
 for door in m['doors']:
  x,y,w,h=door['rect']; checks+=1
  if not any(near(seen,x+(k+.5)*w/7,y+(j+.5)*h/5,22) for k in range(7) for j in range(5)):
   fail.append((a,'portal '+door['id'],door['rect']))
 for step in Q['steps']:
  for it in step.get('interactables',[]):
   if it['area']!=a:continue
   checks+=1
   if not near(seen,it['x'],it['y'],min(56,it.get('r',64))):fail.append((a,'quest '+it['id'],(it['x'],it['y'])))
 for obj in Q.get('side',[]):
  if obj['area']!=a:continue
  checks+=1
  if not near(seen,obj['x'],obj['y'],min(56,obj.get('r',64))):fail.append((a,'side '+obj['id'],(obj['x'],obj['y'])))
 for exam in m['examine']:
  checks+=1
  if not near(seen,exam['x'],exam['y'],min(56,exam.get('r',56))):fail.append((a,'examine '+exam['id'],(exam['x'],exam['y'])))
 print(a, 'reachable cells from SPAWN',len(seen),'of approx',math.ceil(m['w']/STEP)*math.ceil(m['h']/STEP))
if fail:
 print('UNREACHABLE:',len(fail));print('\n'.join(str(x) for x in fail[:70]));raise SystemExit(1)
print('V4 SPAWN-ROOTED NAVIGATION OK:',checks,'target / portal / area checks')
