#!/usr/bin/env python3
"""Position optional v4.9 interactions on legal terrain near their landmarks.
Does not alter original props/collision/maps or any pre-v4.9 events.
"""
import math, json
from pathlib import Path
assets=Path(__file__).resolve().parents[1]/'android/assets/data'
mp=json.loads((assets/'maps.json').read_text('utf-8'))['areas']
props=json.loads((assets/'props.json').read_text('utf-8'))['props']
qp=assets/'quests.json'; q=json.loads(qp.read_text('utf-8'))

def blocked(a,x,y):
  x0,x1=x-9,x+9;y0,y1=y-6,y+2
  if x0<0 or y0<0 or x1>a['w'] or y1>a['h']:return True
  walls=a.get('walls',[])[:]
  for p in a.get('props',[]):
    d=props.get(p['type'],{})
    cw,ch=d.get('cw',0),d.get('ch',0)
    if cw>0 and ch>0:walls.append([p['x']-cw/2,p['y']-ch,cw,ch])
  for w in walls:
    if len(w)>=4 and x0<w[0]+w[2] and x1>w[0] and y0<w[1]+w[3] and y1>w[1]:return True
  for g in a.get('gates',[]):
    # conservative: treat all gates as solid, even gates opened by main-story flags
    r=g['rect']
    if x0<r[0]+r[2] and x1>r[0] and y0<r[1]+r[3] and y1>r[1]:return True
  for e in a.get('ellipses',[]):
    if len(e)<4:continue
    for xx,yy in [(x0,y0),(x1,y0),(x0,y1),(x1,y1),(x,y)]:
      if ((xx-e[0])/e[2])**2+((yy-e[1])/e[3])**2<1:return True
  return False

def find_legal(a,x,y):
  if not blocked(a,x,y):return x,y
  for r in range(12,241,12):
    candidates=[]
    for k in range(32):
      ang=k*2*math.pi/32
      xx=round(x+math.cos(ang)*r); yy=round(y+math.sin(ang)*r)
      if not blocked(a,xx,yy):candidates.append((xx,yy))
    if candidates:
      # pick closest to player's typical corridor if necessary
      return min(candidates,key=lambda p:(p[0]-x)**2+(p[1]-y)**2)
  # fallback map-spawn must already be traversable
  sx,sy=a['spawn']; assert not blocked(a,sx,sy), (a['name'],sx,sy)
  return sx,sy

shifts=[]
for item in q['side']:
  if not item['id'].startswith(('V49_DISC_','V49_WE_')):continue
  a=mp[item['area']]; x,y=item['x'],item['y']
  nx,ny=find_legal(a,x,y)
  if (nx,ny)!=(x,y):
    shifts.append((item['id'],item['area'],(x,y),(nx,ny)))
    item['x']=nx;item['y']=ny
    if item['id'].startswith('V49_WE_'):
      ev_id='v49_'+item['id'][len('V49_WE_'):].lower()
      ev=next(e for e in q['worldEvents'] if e['id']==ev_id)
      ev['x'],ev['y']=nx,ny
for item in q['side']:
  if item['id'].startswith(('V49_DISC_','V49_WE_')):
    assert not blocked(mp[item['area']],item['x'],item['y']),item['id']
qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('position corrections:',len(shifts))
for row in shifts:print(' ',row)
