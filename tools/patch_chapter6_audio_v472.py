#!/usr/bin/env python3
"""Deterministic idempotent music/SFX registration and hall ambience."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java'
s=p.read_text()
if '"cinema_hall_v472"' not in s:
 s=s.replace('"cinema_quiet_reveal_v471"\n    };','"cinema_quiet_reveal_v471", "cinema_hall_v472", "cinema_unwritten_v472"\n    };')
if '"v472_memory_glint"' not in s:
 s=s.replace('"v471_memory_chime"\n    };','"v471_memory_chime", "v472_memory_glint"\n    };')
if 'if ("hall_of_tomorrow".equals(area)) return "eternal_promise";' not in s:
 s=s.replace('if ("eternal_garden".equals(area)) return "eternal_promise";',
             'if ("eternal_garden".equals(area)) return "eternal_promise";\n        if ("hall_of_tomorrow".equals(area)) return "eternal_promise";')
if 'if ("hall_of_tomorrow".equals(area)) return "magic_chimes";' not in s:
 s=s.replace('if ("rain_garden".equals(area)) return "rain_outdoor";',
             'if ("rain_garden".equals(area)) return "rain_outdoor";\n        if ("hall_of_tomorrow".equals(area)) return "magic_chimes";')
s=s.replace('|| "galeri_komunitas".equals(area) || "clockwork_station".equals(area)) return "step_wood";',
            '|| "galeri_komunitas".equals(area) || "clockwork_station".equals(area) || "hall_of_tomorrow".equals(area)) return "step_wood";')
assert all(x in s for x in ('"cinema_hall_v472"','"cinema_unwritten_v472"','"v472_memory_glint"','if ("hall_of_tomorrow".equals(area)) return "magic_chimes";'))
p.write_text(s)
print('PASS: registered C06 music, FX, soundtrack and ambience')
