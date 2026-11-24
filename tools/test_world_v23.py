"""Static v2.3 world-art checks. No LibGDX renderer or Android build is executed.

Optional `--baseline /path/to/v2.2.zip` measures which map PNG pixels have actually
changed against the previous release. No baseline is needed for CI within the ZIP.
"""
from pathlib import Path
from PIL import Image, ImageChops
import hashlib, json, sys, zipfile, io

ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'android'/'assets'
base=json.loads((ROOT/'tools'/'build'/'maps_base.json').read_text(encoding='utf-8'))
game=json.loads((A/'data'/'maps.json').read_text(encoding='utf-8'))['areas']
assert set(base)==set(game) and len(base)==22, 'Map ids must be preserved exactly'
archive = None
if '--baseline' in sys.argv:
    archive = zipfile.ZipFile(sys.argv[sys.argv.index('--baseline')+1])
checks=0; changed=0
for mid,info in base.items():
    p=A/info['image']; im=Image.open(p)
    if game[mid].get('v4Layout') == 'handcrafted_16bit':
        assert im.size == (1200,896) and (game[mid]['w'],game[mid]['h'])==(1200,896)
    else:
        assert im.size == (info['w'],info['h'])
    # Newer stages intentionally replace PNG metadata, not the v2.3 artwork.
    # Require the exact known later-stage art-pass tag instead of the removed v2.3 tag.
    art_stage={
       **dict.fromkeys(('plaza','taman_kota','cafe'),'v3.3-stage1'),
       **dict.fromkeys(('riverside','dermaga','bukit_bintang','memory_garden','eternal_garden'),'v3.4-stage2'),
       **dict.fromkeys(('starfall_village','star_path','gua_kristal','lantern_field','hutan_bisik'),'v3.5-stage3'),
       **dict.fromkeys(('jalan_kota','perumahan','perpustakaan','arcade','toko_bunga','arland_room','sofia_room','dapur','ruang_arsip'),'v3.6-stage4'),
    }
    if game[mid].get('v4Layout') == 'handcrafted_16bit':
        assert im.size == (1200,896) and im.mode in ('RGB','RGBA')
    elif mid in art_stage and im.info.get('world_art_pass'):
        assert im.info.get('world_art_pass')==art_stage[mid], ('unexpected art pass',mid)
    else:
        assert im.info.get('world_polish_v23')=='1'
        assert im.info.get('world_polish_area')==mid
    assert p.stat().st_size>3000,mid
    if game[mid].get('v4Layout') != 'handcrafted_16bit':assert game[mid]['spawn']==info['spawn'],mid
    assert len(game[mid]['doors'])==len(info['doors']),mid
    checks+=6
    if archive is not None:
        old=Image.open(io.BytesIO(archive.read('ArlandSofia/'+info['image'].replace('maps/','android/assets/maps/')))).convert('RGB')
        diff=ImageChops.difference(old,im.convert('RGB'))
        assert diff.getbbox() is not None,f'{mid}: unchanged map despite polish'
        changed+=1
        checks+=1
pose_names=['sit','wave','give','reach','bow','hold_l','hold_r','cheer','hug','lean','photo','highfive','dance','read','water','sweep']
actors=[]
for p in sorted((A/'characters').glob('*/poses.png')):
    im=Image.open(p).convert('RGBA')
    assert im.size==(384,72*len(pose_names)),p
    for idx in range(13,16):
        for direction in range(4):
            x=direction*96; y=idx*72
            a=im.crop((x,y,x+48,y+72)); b=im.crop((x+48,y,x+96,y+72))
            assert a.getbbox() and b.getbbox() and ImageChops.difference(a,b).getbbox(),(p,idx,direction)
            checks+=1
    actors.append(p.parent.name)
    checks+=1
assert len(actors)>=25 and 'arland' in actors and 'sofia' in actors
code=(ROOT/'core/src/main/java/com/arlandsofia/olu/screens/GameScreen.java').read_text()
assert 'animatedTreeRegions' in code and 'propVisible(pr)' in code and 'drawSceneAtmosphere' in code
assert 'return "read";' in code and 'return "water";' in code and 'return "sweep";' in code
checks+=6
print(f'WORLD v2.3 OK: {len(base)} peta dipoles, {len(actors)} sprite pose 16 baris, {checks} cek statis'+
      (f', {changed} peta berubah vs v2.2' if archive else ''))
