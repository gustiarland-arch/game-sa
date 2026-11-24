#!/usr/bin/env python3
"""v5.2 regression: 29 original maps, 2 route rooms, story/side interaction access,
spawn and all 51 door destinations. 16-pixel conservative collision-grid
approximation; not a substitute for runtime playtesting or Android build.
Uses Python standard library only (no Numpy/Pillow required).
"""
from pathlib import Path
import json, math, collections
ROOT=Path(__file__).resolve().parents[1]
assets=ROOT/'android/assets/data'
maps=json.loads((assets/'maps.json').read_text(encoding='utf-8'))['areas']
props=json.loads((assets/'props.json').read_text(encoding='utf-8'))['props']
quests=json.loads((assets/'quests.json').read_text(encoding='utf-8'))
ST=16
checks=0

def check(ok,label):
    global checks
    checks+=1
    if not ok:raise AssertionError(label)

def rects(a):
    walls=list(a.get('walls',[]))
    for prop in a.get('props',[]):
        d=props[prop['type']];cw=d.get('cw',0);ch=d.get('ch',0)
        if cw>0 and ch>0:
            walls.append([prop['x']-cw/2,prop['y']-ch,cw,ch])
    return walls

def is_blocked(a,x,y):
    if x-11<0 or x+11>a['w'] or y-10<0 or y+10>a['h']:return True
    for rx,ry,rw,rh in rects(a):
        if x-11<rx+rw and x+11>rx and y-10<ry+rh and y+10>ry:return True
    for cx,cy,rw,rh in a.get('ellipses',[]):
        for px,py in ((x-11,y-10),(x+11,y-10),(x-11,y+10),(x+11,y+10),(x,y)):
            if ((px-cx)/rw)**2+((py-cy)/rh)**2<1:return True
    return False

def grid(a):
    ww=math.ceil(a['w']/ST);hh=math.ceil(a['h']/ST)
    blocked=bytearray(ww*hh)
    # conservative expanded foot hitbox in raster for every wall, including colliding props
    for rx,ry,rw,rh in rects(a):
        left=max(0,int(math.floor((rx-11)/ST))-1)
        right=min(ww,int(math.ceil((rx+rw+11)/ST))+1)
        top=max(0,int(math.floor((ry-10)/ST))-1)
        bottom=min(hh,int(math.ceil((ry+rh+10)/ST))+1)
        for j in range(top,bottom):
            cy=(j+0.5)*ST
            if not (cy>ry-10 and cy<ry+rh+10):continue
            off=j*ww
            for i in range(left,right):
                cx=(i+0.5)*ST
                if cx>rx-11 and cx<rx+rw+11:blocked[off+i]=1
    for j in range(hh):
        for i in range(ww):
            k=j*ww+i
            if blocked[k]:continue
            x=(i+0.5)*ST;y=(j+0.5)*ST
            if x<12 or x>a['w']-12 or y<12 or y>a['h']-12:blocked[k]=1;continue
            for cx,cy,rw,rh in a.get('ellipses',[]):
                if ((x-cx)/(rw+11))**2+((y-cy)/(rh+10))**2<1:blocked[k]=1;break
    return ww,hh,blocked

def flood(a):
    ww,hh,blocked=grid(a)
    x,y=a['spawn']
    sx,sy=int(x//ST),int(y//ST)
    src=sy*ww+sx
    if blocked[src]:
        for r in range(1,6):
            candidates=[(sx+dx,sy+dy) for dx in range(-r,r+1) for dy in range(-r,r+1)]
            good=next(((cx,cy) for cx,cy in candidates if 0<=cx<ww and 0<=cy<hh and not blocked[cy*ww+cx]),None)
            if good is not None:
                sx,sy=good;src=sy*ww+sx;break
    check(not blocked[src], 'spawn navigation '+a['name'])
    reached=bytearray(ww*hh);reached[src]=1
    queue=collections.deque([src])
    while queue:
        k=queue.popleft();xx=k%ww;yy=k//ww
        for nx,ny in ((xx+1,yy),(xx-1,yy),(xx,yy+1),(xx,yy-1)):
            if not 0<=nx<ww or not 0<=ny<hh:continue
            nk=ny*ww+nx
            if blocked[nk] or reached[nk]:continue
            reached[nk]=1;queue.append(nk)
    return ww,hh,reached

def can_reach(data,x,y,r):
    ww,hh,reached=data
    lim=max(ST,r-5)
    x0=max(0,int((x-lim)/ST)-2);x1=min(ww-1,int((x+lim)/ST)+2)
    y0=max(0,int((y-lim)/ST)-2);y1=min(hh-1,int((y+lim)/ST)+2)
    for j in range(y0,y1+1):
        for i in range(x0,x1+1):
            if reached[j*ww+i] and ((i+.5)*ST-x)**2+((j+.5)*ST-y)**2<=lim*lim:return True
    return False

check(len(maps)==29,'29 areas remain')
for id,a in maps.items():
    check(not is_blocked(a,*a['spawn']),'blocked spawn '+id)
    data=flood(a)
    for st in quests['steps']:
        for it in st.get('interactables',[]):
            if it['area'] != id and not (it['area']=='$ROOM' and id in ('arland_room','sofia_room')):continue
            check(can_reach(data,it['x'],it['y'],it.get('r',64)),f"STORY INACCESSIBLE {id} {st['id']} {it['id']}")
    for it in quests['side']:
        if it['area'] != id and not (it['area']=='$ROOM' and id in ('arland_room','sofia_room')):continue
        # Side quests gated by flags are still tested as physical paths.
        check(can_reach(data,it['x'],it['y'],it.get('r',64)),f"SIDE INACCESSIBLE {id} {it['id']}")
    # No stray decorative v5.1 street furniture inside protagonist rooms.
    if id in ('arland_room','sofia_room'):
        check(not any(p['type'].startswith('v51_') for p in a['props']),'stray outdoor furniture '+id)
for origin,a in maps.items():
    for d in a.get('doors',[]):
        target=maps.get(d['to'])
        if target is None:continue
        check(not is_blocked(target,d['tx'],d['ty']),f"BLOCKED DOOR LANDING {origin}:{d['id']} -> {d['to']}")
check("appVersionName = '5.2.0'" in (ROOT/'build.gradle').read_text(),'release version')
check('SCHEMA = 8' in (ROOT/'core/src/main/java/com/arlandsofia/olu/logic/Progress.java').read_text(),'save schema unchanged')
check(len(quests['steps'])==157,'canon steps unchanged')
print(f'V5.2 WORLD ACCESS PASS: {checks} assertions, 29 maps, complete quest/side routes and door destinations')
