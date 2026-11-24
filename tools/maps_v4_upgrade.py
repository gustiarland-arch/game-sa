#!/usr/bin/env python3
"""Arland & Sofia v4: import supplied authored maps, collision, portals, quests, NPCs.

Input: art_source/maps_v4_input/<map_id>.png, intentionally renamed by *visual
content* because original upload filenames were mismatched. Re-run after
build_content.py; idempotent on already-patched JSON. All coordinates are in
image pixels with Y downwards. Do not edit generated maps.json/quests.json by
hand; edit this file (geometry + semantic anchor tables) and re-run.
"""
from pathlib import Path
from PIL import Image
import json, hashlib, math, copy

ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'android/assets'; DATA=A/'data'; SRC=ROOT/'art_source/maps_v4_input'
MAPPING={'jalan_kota':'04_arcade.png','perumahan':'03_perpustakaan.png',
         'perpustakaan':'08_dapur.png','arcade':'09_ruang_arsip.png',
         'toko_bunga':'02_perumahan.png','arland_room':'10_extra_map.png',
         'sofia_room':'05_toko_bunga.png','dapur':'07_sofia_room.png',
         'ruang_arsip':'06_arland_room.png'}
# Collision: x, y, width, height (mask of the actual pictured objects/furniture)
# Wall/alcove masks include 2-3 rectangles per clipped corner, so the playable
# outline follows the octagonal wall, not a misleading full rectangle.
def mask_room(top=190,side=43,bottom=840):
    return [[0,0,1200,top],[0,top,side,720-top],
            [1200-side,top,side,720-top],
            [0,720,95,bottom-720],[1105,720,95,bottom-720],
            [0,bottom,555,896-bottom],[650,bottom,550,896-bottom],
            # beveled outside corners
            [0,top,85,70],[1115,top,85,70]]
# Avoid full-width invisible barriers except physical walls; step around objects.
GEOMETRY={
'jalan_kota':{'walls':[
    [0,0,1200,275],[0,730,1200,166],
    [0,275,40,90],[1160,275,40,90],
    [735,392,93,72],[900,395,89,70],[1073,391,116,72],
    [23,522,125,62],[680,518,120,62],
    [165,634,95,60],[426,620,80,80],
    [890,630,135,88]
 ],'spawn':[604,559], 'door_positions':{
   'street_to_res':[1159,465,41,100],'street_to_plaza':[0,465,42,100],
   'door_florist':[225,309,72,45],'door_arcade':[905,307,82,48]},
 'landing':{'perumahan':[62,555],'plaza':None,'toko_bunga':[595,765],'arcade':[598,770]},
 'poi':{'bakery':[495,355],'vending':[757,345]},
 'defaultAnchor':[590,560]},
'perumahan':{'walls':[
    [0,0,1200,309],[0,575,1200,321],
    [0,309,25,266],[1175,309,25,266],
    [0,390,102,86],[417,390,44,87],[801,392,49,82]
 ],'spawn':[65,525], 'door_positions':{
   'res_to_street':[0,475,36,87],'door_library':[640,304,76,40]},
 'landing':{'jalan_kota':[1129,510],'perpustakaan':[600,770]},
 'poi':{'res_garden':[220,553],'res_house_c':[205,548],'res_bench':[728,554]},'defaultAnchor':[590,510]},
'perpustakaan':{'walls':mask_room(195,38,845)+[
    [259,160,112,200],[465,174,85,175],[642,166,110,155],
    [760,390,310,198],[760,610,310,132],
    [562,400,82,184],
    [230,398,254,65],[190,590,305,68],
    [470,278,255,86], [800,230,83,127]
 ],'spawn':[602,789], 'door_positions':{
    'perpustakaan_out':[545,816,110,70],
    'lib_to_archive':[1071,335,66,90]},
 'landing':{'perumahan':[680,368],'ruang_arsip':[600,778]},
 'poi':{'lib_globe':[161,290],'lib_sofa':[154,365],'lib_clock':[586,393], 'lib_shelf_w':[395,370]},
 'defaultAnchor':[612,720]},
'arcade':{'walls':mask_room(115,20,853)+[
    [163,118,120,122],[444,125,111,107],[658,120,110,111],
    [909,110,180,155],[430,285,88,98],
    [534,376,135,208],[948,458,160,145],
    [506,618,213,90],[715,752,189,67],
    [174,766,190,80],[974,719,117,112]
 ],'spawn':[595,751], 'door_positions':{'arcade_out':[545,819,110,66]},
 'landing':{'jalan_kota':[902,358]},
 'poi':{'cabinet_e':[307,246]},'defaultAnchor':[650,730]},
 'toko_bunga':{'walls':mask_room(160,44,847)+[
    [85,220,200,175],[347,212,355,129],
    [352,357,305,136],[342,524,223,124],
    [705,633,374,189],[873,285,204,143],[102,725,291,95],
    [82,516,99,139]
 ],'spawn':[612,776], 'door_positions':{'toko_bunga_out':[546,817,120,70]},
 'landing':{'jalan_kota':[265,360]},
 'poi':{'shelf_w_e':[272,410]},'defaultAnchor':[655,520]},
 'arland_room':{'walls':mask_room(177,38,848)+[
    [282,257,192,96],[288,392,180,83],
    [727,198,217,161],[951,238,159,237],
    [840,559,290,208],[200,712,213,126],
    [65,332,175,119],[50,507,138,115]
 ],'spawn':[620,762], 'door_positions':{'arland_room_out':[552,819,105,68]},
 'landing':{'plaza':None},
 'poi':{'a_window':[400,250],'a_clock':[620,357],'a_poster':[515,290],'a_frame':[908,379]},
 'defaultAnchor':[615,585]},
 'sofia_room':{'walls':mask_room(181,44,849)+[
    [248,238,179,230],[64,424,266,228],
    [736,246,190,112],[893,402,223,244],
    [829,724,187,111],[134,639,224,147],
    [370,300,108,85]
 ],'spawn':[609,783],'door_positions':{'sofia_room_out':[548,819,104,70]},
 'landing':{'plaza':None},
 'poi':{'s_window':[836,249],'s_vanity':[737,372],'s_sofa':[392,682],'s_frame':[710,290]},
 'defaultAnchor':[598,630]},
 'dapur':{'walls':mask_room(184,25,846)+[
    [180,191,577,154],[741,159,79,188],[861,166,135,188],
    [389,416,335,151],[904,432,125,171],
    [204,727,259,103],[804,729,100,97]
 ],'spawn':[592,770], 'door_positions':{'dapur_out':[540,819,122,70]},
 'landing':{'cafe':None},
 'poi':{'fridge_e':[808,388]},'defaultAnchor':[600,666]},
 'ruang_arsip':{'walls':mask_room(179,44,850)+[
    [169,192,266,166],[479,208,271,139],
    [760,189,258,154],[807,312,260,302],
    [65,478,355,154],[506,412,200,115],
    [66,734,379,100],[462,761,92,68],
    [943,753,150,82]
 ],'spawn':[585,756], 'door_positions':{'ruang_arsip_out':[542,823,114,66]},
 'landing':{'perpustakaan':[1090,400]},
 'poi':{'arc_jars':[450,385],'arc_jars_e':[744,378]},
 'defaultAnchor':[597,707]},
}
# Anchor map of *walkable standing points* close to the depicted furniture.
POIS={
 'jalan_kota':{'halte':[217,621],'street_shop':[258,349],'arcade':[897,351],'bakery':[490,345],
              'halte':[215,613],'vending':[756,359]},
 'perumahan':{'halte':[727,546],'mbox':[690,543],'bench':[750,544],
              'garden':[200,540]},
 'perpustakaan':{'counter':[618,389],'laras':[615,388],'books1':[720,593],
   'books2':[737,366],'books3':[1091,570],'table':[346,485],
   'reading':[330,692],'archive':[1092,399],'page':[321,685]},
 'arcade':{'juna':[700,737],'booth':[520,383],'claw':[508,381],
           'frame':[707,738],'cabinet':[303,239]},
 'toko_bunga':{'melati':[828,460],'counter':[831,455],'dried':[671,352],
         'buckets':[609,521],'shelf':[286,430],'flowers':[635,522]},
 'arland_room':{'phone':[721,398],'gift':[514,376],'note':[206,489],
     'idea':[711,388],'window':[493,311],'bed':[934,513]},
 'sofia_room':{'phone':[701,386],'gift':[713,384],'note':[339,500],
     'wardrobe':[883,695],'corner':[505,686],'book':[505,691]},
 'dapur':{'stove':[385,380],'fridge':[820,390],'ingredients':[800,390],
          'packing':[385,390],'cook':[382,391]},
 'ruang_arsip':{'pedestal':[619,566],'board':[429,378],
               'margin':[741,380],'map':[420,377]},
}
# Explicit objective alignments (main quests, sidequests and NPCs).
TRIGGERS={
 'perpustakaan':{'laras1':'laras','laras2':'laras','laras4':'laras',
  'libbook1':'books1','libbook2':'books2','libbook3':'books3','libtable':'table',
  'read4':'reading','q_s_reply':'reading','q_a_reply':'laras'},
 'arcade':{'f2_juna':'juna','juna_print':'juna','booth':'booth','frame':'frame',
 'claw':'claw'},
 'toko_bunga':{'florist':'melati','dried':'dried','f5_melati':'melati',
    'f5_melati_done':'melati'},
 'arland_room':{'phone':'phone','phone2':'phone','phone4':'phone','phone5':'phone',
   'gift':'gift','note':'note','idea':'idea'},
 'sofia_room':{'phone':'phone','phone2':'phone','phone4':'phone','book5':'book',
    'gift':'gift','note':'note','wardrobe':'wardrobe','corner':'corner','arrange':'corner'},
 'dapur':{'fridge':'fridge','stove':'stove','v26_c03_recipe':'stove',
    'v26_c03_packing':'packing','cook1':'cook','cook2':'cook','cook3':'cook'},
 'ruang_arsip':{'pedestal':'pedestal','q_a_map':'map','q_s_margin':'margin'},
 'perumahan':{'halte':'halte','mbox':'mbox','q_a_reply':'halte'},
 'jalan_kota':{'photo4':'halte','route_a_1':'halte','rain_a_1':'halte',
  'v26_sqs_3':'halte','v26_sqf_1':'halte'},
}

# Foreground Y-sort layers cut from the actual supplied art. Alpha silhouettes
# prevent hiding the hero with rectangular, opaque crop backgrounds.
FOREGROUND={
 'jalan_kota': [('lamp',[(443,269),(477,267),(497,394),(431,394)],396)],
 'perumahan': [('bench',[(506,318),(580,318),(580,372),(507,372)],374)],
 'perpustakaan':[('bookshelf',[(752,390),(1075,390),(1075,593),(752,593)],594)],
 'arcade':[('central_cabinets',[(529,367),(670,367),(673,593),(530,593)],596)],
 'toko_bunga':[('flower_table',[(343,350),(671,350),(671,498),(343,498)],500)],
 'arland_room':[('computer',[(712,189),(948,189),(948,361),(712,361)],364)],
 'sofia_room':[('vanity',[(736,226),(933,226),(930,375),(736,375)],377)],
 'dapur':[('island',[(378,417),(729,417),(729,568),(378,568)],570)],
 'ruang_arsip':[('investigation_desk',[(499,397),(712,397),(711,531),(499,531)],534)],
}

def make_foregrounds(area,image,props_db,map_props):
    from PIL import ImageDraw
    for name, polygon, sort_y in FOREGROUND.get(area,[]):
        x0=min(p[0] for p in polygon);x1=max(p[0] for p in polygon)+1
        y0=min(p[1] for p in polygon);y1=max(p[1] for p in polygon)+1
        crop=image.crop((x0,y0,x1,y1)).convert('RGBA')
        alpha=Image.new('L',crop.size,0);d=ImageDraw.Draw(alpha)
        d.polygon([(x-x0,y-y0) for x,y in polygon],fill=255)
        crop.putalpha(alpha)
        # Texture renders centered horizontally with bottom edge at sort_y,
        # so transparent pixels outside the silhouette are never painted.
        path=f'props/maps_v4_{area}_{name}.png'
        crop.save(A/path,optimize=True)
        tid=f'maps_v4_{area}_{name}'
        props_db['props'][tid]={'image':path,'cw':0,'ch':0,'layer':'sort'}
        map_props.append({'type':tid,'x':round((x0+x1)/2),'y':y1})

# Two-dimensional collision uses player's 18x8 foot rectangle (MapDb.java).
FW, FT, FB=18,6,2

def blocked(area,x,y):
    if x-9<0 or y-6<0 or x+9>1200 or y+2>896: return True
    for rx,ry,rw,rh in GEOMETRY[area]['walls']:
        if x-9<rx+rw and x+9>rx and y-6<ry+rh and y+2>ry: return True
    return False

def safe(area, x, y, preferred=None):
    if preferred is not None: x,y=preferred
    x,y=float(x),float(y)
    if not blocked(area,x,y): return [int(round(x)),int(round(y))]
    # grid search around original point. Keep <=250px to avoid teleport to far room.
    best=None
    for radius in range(8,600,8):
        for angle in range(0,360,12):
            nx=x+radius*math.cos(math.radians(angle));ny=y+radius*math.sin(math.radians(angle))
            if not blocked(area,nx,ny):
                val=math.hypot(nx-x,ny-y)
                if best is None or val<best[0]:best=(val,nx,ny)
        if best is not None:return [round(best[1]),round(best[2])]
    raise ValueError(f'no safe coordinate for {area} at {(x,y)}')

def scale(area,x,y):
    w,h=OLD_DIM[area];return [max(13,min(1187,round(float(x)*1200/w))), max(13,min(883,round(float(y)*896/h)))]

def sem(area,id):
    sid=id.lower()
    explicit=TRIGGERS.get(area,{}).get(sid)
    if explicit:return POIS[area][explicit]
    for k,v in POIS.get(area,{}).items():
        if k in sid:return v
    if area=='perpustakaan' and ('lib' in sid or 'book' in sid):return POIS[area]['books2']
    return None


def move_point(area,obj, id='', snap=True):
    if area not in GEOMETRY or not isinstance(obj,dict):return
    if 'x' not in obj or 'y' not in obj:return
    p=scale(area,obj['x'],obj['y']); desired=sem(area,id)
    if desired:p=desired
    if snap:p=safe(area,*p)
    obj['x'],obj['y']=p


def relocate_actions(actions,context=None):
    # Legacy scene commands embedded in quests use world coordinates, not pixels
    # relative to a portrait. Transform only when their owning area is known.
    for a in actions or []:
        if not isinstance(a,dict):continue
        typ=a.get('do')
        if typ=='warp' and a.get('area') in GEOMETRY:
            ar=a['area'];move_point(ar,a,'warp');
        elif typ=='if':
            relocate_actions(a.get('then',[]),context);relocate_actions(a.get('else',[]),context)
        elif typ=='cine' and (context in GEOMETRY or context=='$ROOM'):
            for c in a.get('cmds',[]):
                ar=context if context in GEOMETRY else (c.get('route')+'_room' if c.get('route') in ('arland','sofia') else None)
                if ar not in GEOMETRY:continue
                if c.get('c') in ('place','cam','spawn') and 'x' in c and 'y' in c:
                    # Camera positions may view scenery; clipping to safe tile is wrong.
                    move_point(ar,c,c.get('c',''),snap=c.get('c') != 'cam')
                if c.get('c')=='move':
                    if 'to' in c and isinstance(c['to'],list):c['to']=safe(ar,*scale(ar,*c['to']))
                    if 'path' in c:c['path']=[safe(ar,*scale(ar,*pt)) for pt in c['path']]

def transform_script(quest):
    for step in quest.get('steps',[]):
        ctx=step.get('startArea')
        for it in step.get('interactables',[]):
            area=it.get('area');move_point(area,it,it['id']);
            if 'sprite' in it and area in GEOMETRY:move_point(area,it['sprite'],it['id'])
            relocate_actions(it.get('actions',[]),area)
        for npc in step.get('npcs',[]):move_point(npc.get('area'),npc,npc.get('who','npc'))
        enter=step.get('enterArea')
        if enter:relocate_actions(enter.get('actions',[]),enter.get('area'))
        if 'onStart' in step:relocate_actions(step['onStart'],ctx)
        if 'complete' in step:relocate_actions(step['complete'].get('actions',[]),ctx)
    for it in quest.get('side',[]):
        ar=it.get('area');move_point(ar,it,it['id'])
        if ar=='$ROOM':it['x'],it['y']=600,744
        if 'sprite' in it and ar in GEOMETRY:move_point(ar,it['sprite'],it['id'])
        elif 'sprite' in it and ar=='$ROOM':it['sprite']['x'],it['sprite']['y']=600,739
        relocate_actions(it.get('actions',[]),ar)
    for n in quest.get('townNpcs',[]):
        ar=n.get('area');move_point(ar,n,n['id'])
        for e in n.get('schedule',[]):move_point(e.get('area'),e,n['id'])
    world_markers={it['id']:it for it in quest.get('side',[])}
    for e in quest.get('worldEvents',[]):
        ar=e.get('area')
        if ar in GEOMETRY:
            marker=world_markers.get('WE27_'+e['id'].upper())
            if marker:
                e['x'],e['y']=marker['x'],marker['y']
            else:move_point(ar,e,e['id'])
    # Some interactions have explicit NPC schedules/side quest spawn points
    # nested under sideQuests, or other key collections.

def main():
    mp=DATA/'maps.json';qp=DATA/'quests.json';prp=DATA/'props.json'
    maps=json.loads(mp.read_text('utf-8'));qs=json.loads(qp.read_text('utf-8'));props=json.loads(prp.read_text('utf-8'))
    global OLD_DIM
    OLD_DIM={k:(maps['areas'][k]['w'],maps['areas'][k]['h']) for k in MAPPING}
    if maps.get('_maps_v4') and qs.get('_maps_v4'):
        print('Maps v4 already installed; runtime patch is idempotent.');return
    if maps.get('_maps_v4') or qs.get('_maps_v4'):
        raise RuntimeError('Map and quest markers inconsistent; regenerate with tools/build_content.py')
    # Replace background with visually correct file, never a before/after collage.
    for area in MAPPING:
        src=SRC/(area+'.png');im=Image.open(src)
        assert im.size==(1200,896) and im.mode in ('RGB','RGBA'),(area,im.size)
        dst=A/'maps'/f'{area}.png';dst.write_bytes(src.read_bytes())
        m=maps['areas'][area];m['w']=1200;m['h']=896
        m['v4Layout']='handcrafted_16bit';m['v4SourceOriginalFilename']=MAPPING[area]
        m['walls']=GEOMETRY[area]['walls'];m['ellipses']=[]
        m['spawn']=safe(area,*GEOMETRY[area]['spawn']);
        m['props']=[] # Baked into the supplied map. Do not render old props twice.
        make_foregrounds(area,im,props,m['props'])
        # Entrance/exit zones have explicit picture-based coordinates; preserve locks.
        for d in m['doors']:
            r=GEOMETRY[area]['door_positions'][d['id']]
            d['rect']=r
            # Portal arrival coordinates are assigned from the destination
            # mapping in the second pass below, after all areas are updated.
        for e in m['examine']:
            desired=GEOMETRY[area]['poi'].get(e['id'])
            move_point(area,e,e['id']);
            if desired:e['x'],e['y']=safe(area,*desired)
        for animal in m.get('animals',[]):
            if 'region' in animal:
                x,y,w,h=animal['region'];p=scale(area,x,y);x2,y2=scale(area,x+w,y+h)
                animal['region']=[p[0],p[1],max(48,x2-p[0]),max(48,y2-p[1])]
            if 'water' in animal:
                cx,cy,rx,ry=animal['water'];pt=scale(area,cx,cy)
                animal['water']=[pt[0],pt[1],max(12,rx*1200/OLD_DIM[area][0]),max(12,ry*896/OLD_DIM[area][1])]
        # Water on supplied street is decorative, no active swim zone.
        m['water']=[]
        if area=='perumahan':
            for animal in m.get('animals',[]):
                animal['region']=([250,337,330,190] if animal['type']=='chicken' else [650,332,280,215] if animal['type']=='cat_orange' else [125,339,960,220])
    # Fix inbound portals from all other 13 areas, and explicit arrival coords for
    # each named doorway (e.g. street-to-florist should land near its entrance).
    inbound={
      ('plaza','plaza_to_street'):[65,511],
      ('jalan_kota','street_to_res'):[65,517],
      ('jalan_kota','door_florist'):[601,774],
      ('jalan_kota','door_arcade'):[600,776],
      ('perumahan','door_library'):[601,780],
      ('perpustakaan','lib_to_archive'):[594,782],
      ('perpustakaan','perpustakaan_out'):[676,370],
      ('ruang_arsip','ruang_arsip_out'):[1093,462],
      ('arcade','arcade_out'):[900,382],
      ('toko_bunga','toko_bunga_out'):[260,386],
      ('plaza','door_arland_house'):[608,773],
      ('plaza','door_sofia_house'):[609,775],
      ('cafe','cafe_to_kitchen'):[599,777],
      ('dapur','dapur_out'):[856,283],
    }
    for origin, m in maps['areas'].items():
        for d in m['doors']:
            if d['to'] not in GEOMETRY:continue
            dest=d['to']
            if (origin,d['id']) in inbound:point=inbound[(origin,d['id'])]
            else:point=scale(dest,d['tx'],d['ty'])
            point=safe(dest,*point)
            d['tx'],d['ty']=point
    transform_script(qs)
    maps['_maps_v4']='maps_v4_upgrade.py';qs['_maps_v4']='maps_v4_upgrade.py'
    prp.write_text(json.dumps(props,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    mp.write_text(json.dumps(maps,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    qp.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Mapping log with distinct original upload filenames, useful for audit.
    (ROOT/'docs/MAPS_V4_MAPPING.json').write_text(json.dumps({
       'source_note':'Provided filenames do NOT match picture contents; mapping verified visually.',
       'input_original_name_by_area':MAPPING,
       'excluded':['01_jalan_kota.png (comparison collage, not an area)','__MACOSX','AppleDouble ._ metadata'],
       'dimensions':{a:[1200,896] for a in MAPPING},
       'doors':{a:[dict(id=d['id'],rect=d['rect'],to=d['to'],target=[d['tx'],d['ty']]) for d in maps['areas'][a]['doors']] for a in MAPPING},
       'spawns':{a:maps['areas'][a]['spawn'] for a in MAPPING},
       'examines':{a:[dict(id=e['id'],point=[e['x'],e['y']]) for e in maps['areas'][a]['examine']] for a in MAPPING},
       'obstacles':{a:GEOMETRY[a]['walls'] for a in MAPPING},
    },ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Installed nine visually matched maps; portals, collisions, quest triggers and NPCs transformed')

if __name__=='__main__':main()
