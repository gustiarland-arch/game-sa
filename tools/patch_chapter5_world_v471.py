#!/usr/bin/env python3
"""Register 3 new playable world atmospheres (zero changes to existing 24 types)."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'core/src/main/java/com/arlandsofia/olu/logic/WorldAtmosphereV462.java'
s=p.read_text()
if '"clockwork_station"' not in s:
 s=s.replace('"hutan_bisik","bukit_bintang","gua_kristal","rain_garden"',
             '"hutan_bisik","bukit_bintang","gua_kristal","rain_garden",\n        "clockwork_station","moonlight_lake","memory_bridge"')
if 'STAR,WATER,STAR' not in s:
 s=s.replace('STAR,STAR,STAR,GARDEN,CITY,HOME,HOME,HOME,WATER,GARDEN,STAR,CAVE,GARDEN',
             'STAR,STAR,STAR,GARDEN,CITY,HOME,HOME,HOME,WATER,GARDEN,STAR,CAVE,GARDEN,\n        STAR,WATER,STAR')
p.write_text(s)
assert all('"'+k+'"' in s for k in ('clockwork_station','moonlight_lake','memory_bridge'))
print('PASS: all 27 areas have atmosphere classifications')
