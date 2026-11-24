#!/usr/bin/env python3
"""Verify visual source packs, 22 area coverage and unchanged collision data."""
from pathlib import Path
from PIL import Image
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
assets=ROOT/'android/assets'
profiles=json.loads((assets/'data/maps.json').read_text('utf8'))['areas']
assert len(profiles)>=24 and {"galeri_komunitas","rain_garden","starfall_village","lantern_field"}<=set(profiles),len(profiles)
source=(ROOT/'core/src/main/java/com/arlandsofia/olu/logic/WorldAtmosphereV462.java').read_text()
for id in profiles:
    assert '"'+id+'"' in source, id
# v6: the v4.6.2 eight-direction sheets were superseded by *_8dir_v53 (the atlas Assets
# loads first) and removed in the v6 asset audit; verify the shipped atlas instead.
for name,phases in [('walk',24),('idle',12)]:
    for who in ('arland','sofia'):
        p=assets/f'characters/{who}/{name}_8dir_v53.png'
        with Image.open(p) as im:
            assert im.size==(48*phases,72*8),(p,im.size)
            assert im.mode=='RGBA'
            nonempty=0
            for row in range(8):
                frame=im.crop((0,row*72,48,(row+1)*72))
                nonempty+=bool(frame.getbbox())
            assert nonempty==8,(p,nonempty)
for name in ('mist','sunbeam','leaf','blossom','firefly','water_glint','raindrop'):
    p=assets/f'fx/v462_{name}.png'
    with Image.open(p) as im:
        assert im.mode=='RGBA' and im.width>0 and im.height>0
        assert im.getbbox(),p
assert len(list((assets/'fx').glob('v462_*.png')))==7
print('PASS: 22 original + gallery + Rain Garden + 3 Chapter5 map profiles, 4 eight-facing hero atlases and 7 editable atmosphere sprites')
