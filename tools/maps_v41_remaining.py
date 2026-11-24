#!/usr/bin/env python3
"""v4.1 — scenic art pass for 13 maps not replaced with v4 supplied images.

Uses original/generated pixel-landmark source atlas (art_source/world_v41),
composites editable ground decoration overlays, and selectively substitutes
legacy focal props with better art while retaining their *exact* collision
footprints and anchor coordinates. Keep unchanged the nine authored 1200x896
maps imported by tools/maps_v4_upgrade.py.

Idempotent. Run after maps_v4_upgrade.py (and all legacy visual passes).
"""
from pathlib import Path
import json,random,hashlib,math,shutil,sys,os
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'android/assets'; DATA=A/'data'; SRC=ROOT/'art_source/world_v41'
BASE=SRC/'baseline_maps';LAYERS=SRC/'editable_layers'; PROPS=A/'props'
for d in [BASE,LAYERS,PROPS]:d.mkdir(parents=True,exist_ok=True)
ATLAS=SRC/'pixel_landmarks_atlas.png'
assert ATLAS.is_file(), 'Missing generated atlas (art_source/world_v41/pixel_landmarks_atlas.png)'

# Source artwork crop regions. Names are internal assets, not map data IDs.
BOX={
'fountain':(0,10,265,270), 'gazebo':(502,23,756,249),
'cherry':(130,260,301,452), 'dock':(775,14,1039,266),
'bridge':(1218,12,1535,232), 'rowboat':(1095,241,1270,339),
'willow':(1395,256,1535,455), 'observatory':(17,507,286,746),
'house_blue':(5,768,214,990), 'house_brick':(215,767,411,990),
'memory_tree':(797,517,1055,786), 'arch':(1092,483,1232,659),
'crystal_shrine':(1085,611,1277,763), 'crystal_cluster':(1404,490,1535,647),
'cave':(1306,774,1536,1024), 'waterfall':(780,788,1060,1022),
'starrocks':(500,524,678,644),'telescope':(531,648,620,722),
'flower':(304,274,436,372),'lantern':(664,520,753,666)
}
# Existing map types -> new sprite generated from atlas. Reuse exact old collision.
CHANGE={
'plaza':[('fountain','fountain',1),('bld_arland_house','house_blue',1),('bld_sofia_house','house_brick',1),('tree_cherry','cherry',4),('flowerbed','flower',3)],
'taman_kota':[('gazebo','gazebo',1),('tree_cherry','cherry',5),('flowerbed','flower',3)],
'riverside':[('rowboat_rv','rowboat',1),('tree_cherry','cherry',3),('tree_green','willow',2)],
'cafe':[('counter','cafe_counter',1),('cafe_table','cafe_table',4),('display_case','cafe_display',1)],
'memory_garden':[('arch_flowers','arch',1),('pedestal_book','crystal_shrine',1),('tree_dream','memory_tree',3)],
'lantern_field':[('tree_lantern','cherry',4),('lantern_off','lantern',3)],
'star_path':[('crystal','crystal_cluster',5),('star_stone','starrocks',3)],
'starfall_village':[('bld_star_house0','house_blue',1),('bld_star_house1','house_brick',1),('bld_star_house2','house_blue',1),('tree_dream','memory_tree',2)],
'eternal_garden':[('wishing_tree','memory_tree',1),('arch_flowers_e','arch',1),('arch_flowers_e2','arch',1),('gazebo_e','gazebo',1)],
'dermaga':[('rowboat','rowboat',1),('rowboat_b','rowboat',1),('tree_green','willow',2)],
'hutan_bisik':[('waterfall_hb','waterfall',1),('cave_entrance','cave',1),('tree_dark','willow',3)],
'bukit_bintang':[('observatory','observatory',1),('telescope','telescope',1),('tree_cherry','cherry',3)],
'gua_kristal':[('crystal_big','crystal_cluster',4),('crystal','crystal_cluster',3)]
}
NINE=set('jalan_kota perumahan perpustakaan arcade toko_bunga arland_room sofia_room dapur ruang_arsip'.split())

def hdrgb(c):return tuple(c[:3])
def scene_layer(name,w,h,seed):
    """Subtle location-specific hand-authored shapes over original walkable ground.
    Everything is transparent walkable decoration; props are Y-sorted separately.
    No new solid geometry is invented on a navigable path.
    """
    rng=random.Random(seed)
    im=Image.new('RGBA',(w,h),(0,0,0,0)); dr=ImageDraw.Draw(im,'RGBA')
    def line(seq,col,width=2):dr.line(seq,fill=col,width=width,joint='curve')
    def ring(x,y,rx,ry,col,width=3):dr.ellipse((x-rx,y-ry,x+rx,y+ry),outline=col,width=width)
    def petals(n, colors, zone=None, scale=1):
        x0,y0,x1,y1=zone or (40,40,w-40,h-40)
        for _ in range(n):
            x=rng.randrange(int(x0),int(x1));y=rng.randrange(int(y0),int(y1));r=rng.choice([2,3,4,6])*scale
            dr.ellipse((x-r,y-r//2,x+r,y+r//2),fill=rng.choice(colors))
    if name in ('plaza','taman_kota','riverside','dermaga'):
        # Water glints and urban masonry accents; surface detail only, no new objects.
        if name=='plaza':
            for rad in [230,247,263]:ring(w//2,780,rad,int(rad*.54),(255,233,166,70),2)
            for a in range(24):
                theta=a*2*math.pi/24;x=w//2+int(258*math.cos(theta));y=778+int(144*math.sin(theta));
                dr.ellipse((x-5,y-4,x+5,y+4),fill=(235,188,92,95))
            petals(430,[(252,157,185,75),(255,225,134,55)],scale=1)
        elif name=='taman_kota':
            petals(500,[(255,190,209,98),(242,229,138,85),(253,252,221,72)])
            for i in range(40):
                x=rng.randrange(260,1100);y=rng.randrange(700,1070)
                dr.arc((x-16,y-4,x+16,y+8),190,345,fill=(175,229,248,110),width=2)
        elif name=='riverside':
            petals(240,[(252,173,201,75),(250,221,143,50)],zone=(60,60,w-60,720))
            for i in range(340):
                x=rng.randrange(60,w-80);y=rng.randrange(840,h-30)
                line([(x,y),(x+rng.randrange(6,24),y)],(188,243,248,rng.randrange(60,155)),rng.randrange(2,4))
        else:
            for i in range(410):
                x=rng.randrange(40,w-40);y=rng.randrange(690,h-20)
                line([(x,y),(x+rng.randrange(6,33),y)],(179,237,241,rng.randrange(55,155)),2)
            petals(150,[(231,172,192,80),(238,212,160,70)],zone=(40,30,w-40,620))
    if name=='cafe':
        # Warm brick, window muntins and parquet wear; counters remain proper Y-sort props.
        for x in range(28,w-12,58):
            line([(x,170),(x+42,170)],(110,65,41,60),2)
        for y in range(256,h-20,56):
            for x in range(40+(28 if (y//56)%2 else 0),w-20,90):
                line([(x,y),(x+55,y)],(255,218,142,42),3)
        for cx in (155,500,825):
            dr.rounded_rectangle((cx-35,80,cx+35,180),radius=5,outline=(143,80,42,120),width=5)
            line([(cx,82),(cx,180)],(248,211,142,100),2)
        for i in range(150):
            x=rng.randrange(32,w-30);y=rng.randrange(244,h-8)
            line([(x,y),(x+8,y)],(247,220,174,65),2)
    if name in ('memory_garden','eternal_garden','lantern_field'):
        colors={'memory_garden':[(222,163,255,100),(246,219,255,100)],
                'eternal_garden':[(252,198,230,95),(249,228,166,90)],
                'lantern_field':[(255,198,105,90),(244,158,172,90)]}[name]
        petals(700,colors)
        cx,cy=(800,600) if name=='memory_garden' else ((960,1040) if name=='eternal_garden' else (960,660))
        for radius in [150,170,188]:ring(cx,cy,radius,int(radius*.66),(233,196,255,90),2)
        for i in range(100):
            x=rng.randrange(60,w-60);y=rng.randrange(60,h-60)
            dr.ellipse((x-2,y-2,x+2,y+2),fill=(255,246,202,rng.randrange(90,190)))
    if name in ('star_path','starfall_village','bukit_bintang'):
        for i in range(170):
            x=rng.randrange(35,w-35);y=rng.randrange(35,h-35);r=rng.choice([2,3,4])
            dr.ellipse((x-r,y-r,x+r,y+r),fill=(247,219,159,rng.randrange(55,155)))
            if i%9==0:
                line([(x-10,y),(x+10,y)],(229,209,250,110),2)
                line([(x,y-10),(x,y+10)],(229,209,250,110),2)
        if name=='starfall_village':
            for (cx,cy) in ((420,690),(960,680),(1500,685)):
                ring(cx,cy,160,92,(235,202,160,85),3)
        if name=='bukit_bintang':
            ring(1100,560,320,185,(249,227,167,52),2)
    if name=='hutan_bisik':
        petals(1200,[(155,228,169,56),(198,232,129,48),(235,201,155,62)])
        for _ in range(95):
            x=rng.randrange(60,w-60);y=rng.randrange(75,h-75)
            line([(x-5,y),(x+5,y)],(149,232,227,77),2)
    if name=='gua_kristal':
        for i in range(230):
            x=rng.randrange(48,w-48);y=rng.randrange(48,h-48)
            c=rng.choice([(146,222,255,105),(199,137,255,125),(249,139,242,75)])
            line([(x,y+8),(x+rng.randint(3,12),y-10)],c,2)
        for cx,cy in [(420,300),(860,300),(1000,520),(520,760)]:
            for r in [44,68,95]:ring(cx,cy,r,int(r*.6),(138,206,253,65),2)
    return im

def image_from_atlas(atlas,kind,target_size):
    if kind.startswith('cafe_'):return None
    c=atlas.crop(BOX[kind]);
    # Generation comes as RGBA with translucent light checker/background.
    # Separate by opacity; avoid burning the near-white background into prop textures.
    a=c.getchannel('A').point(lambda v:0 if v<181 else min(255,round((v-181)*3.6)))
    c.putalpha(a)
    # Trim empty borders at this cut, keep original artwork's palette (no blurring).
    bb=a.getbbox()
    if bb:c=c.crop(bb)
    return c.resize(target_size,Image.Resampling.NEAREST)

def cafe_custom(old,kind):
    img=old.copy().convert('RGBA');dr=ImageDraw.Draw(img,'RGBA');w,h=img.size
    # Keep silhouette and original alpha to preserve collision and sorting.
    if kind=='cafe_table':
        y=int(h*.46);x=w//2
        dr.ellipse((x-14,y-5,x+11,y+5),fill=(241,231,215,190),outline=(91,54,49,160),width=2)
        dr.ellipse((x-6,y-10,x+5,y+1),fill=(126,74,40,230),outline=(249,222,186,215),width=2)
        dr.line((x+13,y-1,x+18,y-7),fill=(249,227,192,210),width=2)
    elif kind=='cafe_counter':
        dr.rectangle((12,int(h*.36),w-12,int(h*.39)),fill=(252,206,140,105))
        for x in range(28,w-20,26):
            dr.line((x,int(h*.43),x,int(h*.9)),fill=(103,54,39,75),width=3)
        for x in (int(w*.28),int(w*.65)):
            dr.ellipse((x-10,int(h*.18),x+10,int(h*.29)),fill=(233,221,188,200))
            dr.ellipse((x-6,int(h*.20),x+6,int(h*.24)),fill=(143,79,47,245))
    elif kind=='cafe_display':
        for x in range(12,w-10,18):
            dr.ellipse((x,int(h*.3),x+9,int(h*.3)+8),fill=(255,200,116,160))
    # alpha must not expand beyond original where transparent.
    oldmask=old.getchannel('A');img.putalpha(oldmask);return img

def main():
    from PIL import Image
    data=json.loads((DATA/'maps.json').read_text(encoding='utf8'))
    prop_data=json.loads((DATA/'props.json').read_text(encoding='utf8'))
    fast='--metadata-only' in sys.argv
    areas=data['areas'];defs=prop_data['props'];atlas=None if fast else Image.open(ATLAS).convert('RGBA')
    # After v4.2, 13 world PNGs are intentionally painted over v4.1.
    # Metadata-only tests must verify the ACTIVE art version, never demand the
    # older v4.1 pixels and never repaint/overwrite them during logic tests.
    v42=ROOT/'docs/V42_WORLD_MANIFEST.json'
    expected=(json.loads(v42.read_text())['sha256'] if v42.is_file() else json.loads((ROOT/'docs/V41_RUNTIME_SHA256.json').read_text())) if fast else {}
    active_v43=ROOT/'docs/V43_WORLD_MANIFEST.json'
    if fast and active_v43.is_file():
        expected.update(json.loads(active_v43.read_text())['areas'])  # exact hash, not permissive bypass
    active_v44=ROOT/'docs/V44_WORLD_MANIFEST.json'
    if fast and active_v44.is_file():
        expected.update(json.loads(active_v44.read_text())['maps'])  # precise new map hashes
    assert set(CHANGE)==set(areas)-NINE,(set(CHANGE),set(areas)-NINE)
    summary={};replaced=0
    for area_id,spec in CHANGE.items():
        m=areas[area_id];mp=A/m['image'];before=BASE/(area_id+'.png')
        if fast:
            assert area_id in expected and mp.is_file(),('source asset missing',area_id)
            assert hashlib.sha256(mp.read_bytes()).hexdigest()==expected[area_id],('runtime map differs; rebuild full assets first',area_id)
            assert before.is_file() and (LAYERS/(area_id+'_atmosphere.png')).is_file()
        else:
            if not before.exists():shutil.copy2(mp,before)
            baseline=Image.open(before).convert('RGBA')
            assert baseline.size==(m['w'],m['h']),(area_id,baseline.size,m['w'],m['h'])
            overlay=scene_layer(area_id,m['w'],m['h'],int(hashlib.sha256(area_id.encode()).hexdigest()[:8],16))
            lay=LAYERS/(area_id+'_atmosphere.png');laytmp=LAYERS/(area_id+'_atmosphere.png.tmp')
            overlay.save(laytmp,format='PNG',compress_level=3);os.replace(laytmp,lay)
            runtime=Image.alpha_composite(baseline,overlay)
            tmp=mp.with_suffix('.png.tmp')
            runtime.save(tmp,format='PNG',optimize=False,compress_level=3)
            os.replace(tmp,mp)  # Never leave a half-written active map on interruption.
        if 'v41PropReplacementIndex' not in m:
            changes={};taken=set()
            for old,kind,count in spec:
                found=[i for i,p in enumerate(m['props']) if i not in taken and p['type']==old]
                assert len(found)>=count,(area_id,old,len(found),count)
                for i in found[:count]:
                    changes[str(i)]={'was':old,'art':kind};taken.add(i)
            m['v41PropReplacementIndex']=changes
        changes=m['v41PropReplacementIndex']
        # Backwards-compatible generator extension: add newly requested styles
        # without reselecting different existing props on the second run.
        taken={int(k) for k in changes}
        for old,kind,count in spec:
            done=sum(ref['was']==old and ref['art']==kind for ref in changes.values())
            for i,p in enumerate(m['props']):
                if done>=count:break
                if i not in taken and p['type']==old:
                    changes[str(i)]={'was':old,'art':kind};taken.add(i);done+=1
            assert done==count,(area_id,old,kind,count)
        for index,ref in changes.items():
            p=m['props'][int(index)];old=ref['was'];kind=ref['art']
            assert p['type'] in (old,'v41_'+old+'_'+kind),(area_id,index,p['type'])
            new='v41_'+old+'_'+kind; src=defs[old]['image']
            newpath=PROPS/(new+'.png')
            if not newpath.exists():
                assert not fast, ('missing runtime prop art in metadata-only mode',new)
                original=Image.open(A/src).convert('RGBA')
                output=(cafe_custom(original,kind) if kind.startswith('cafe_') else image_from_atlas(atlas,kind,original.size))
                output.save(newpath,optimize=False,compress_level=6)
            assert Image.open(newpath).getbbox() is not None
            defs[new]={'image':'props/'+new+'.png','cw':defs[old]['cw'],'ch':defs[old]['ch'],'layer':defs[old]['layer']}
            p['type']=new;replaced+=1
        m['visualStyle']='v4.1_romantic_scenery';m['visualUpdate']='13_legacy_worlds_landmarks_atmosphere'
        summary[area_id]={'size':[m['w'],m['h']],'legacyPropsReplaced':len(changes),'originalCollisionPreserved':True,'originalSpawn':m['spawn'],'existingPortals':[d['id'] for d in m['doors']]}
    data['_maps_v41']={'id':'v4.1','count':13,'info':'13 prior background maps improved by scenic layers and focal landmark props; geometry unchanged'}
    (DATA/'maps.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
    (DATA/'props.json').write_text(json.dumps(prop_data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
    report={'areas':summary,'newPropReplacements':replaced,'atlasSource':str(ATLAS.relative_to(ROOT)),'transparentLayers':13,
            'nine_v4_authored_maps_untouched':sorted(NINE)}
    (ROOT/'docs'/'MAPS_V41_MANIFEST.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if not fast:
        (ROOT/'docs/V41_RUNTIME_SHA256.json').write_text(json.dumps({k:hashlib.sha256((A/areas[k]['image']).read_bytes()).hexdigest() for k in CHANGE},indent=2)+'\n')
    print('v4.1 scenic maps generated:',len(summary),'areas,',replaced,'prop instances,',len(set(p['type'] for a in areas.values() for p in a['props'] if p['type'].startswith('v41_'))),'new prop types')
if __name__=='__main__':main()
