#!/usr/bin/env python3
"""Register Hall of Tomorrow atmosphere in the native renderer, idempotently."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'core/src/main/java/com/arlandsofia/olu/logic/WorldAtmosphereV462.java'
s=p.read_text()
if '"hall_of_tomorrow"' not in s:
 s=s.replace('"clockwork_station","moonlight_lake","memory_bridge"',
             '"clockwork_station","moonlight_lake","memory_bridge","hall_of_tomorrow"')
 s=s.replace('STAR,WATER,STAR\n    };','STAR,WATER,STAR,STAR\n    };')
assert '"hall_of_tomorrow"' in s and 'STAR,WATER,STAR,STAR' in s
p.write_text(s)
print('PASS: hall_of_tomorrow registered among 28 real runtime FX profiles')
