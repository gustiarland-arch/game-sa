#!/usr/bin/env python3
"""Idempotent sound registration and new world ambience routes."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java'
s=p.read_text()
s=s.replace('"cinema_listen_again_v470"\n    };','"cinema_listen_again_v470", "cinema_clockwork_v471", "cinema_two_sides_v471", "cinema_quiet_reveal_v471"\n    };')
s=s.replace('"v470_paper_note"\n    };','"v470_paper_note", "v471_memory_chime"\n    };')
if 'if ("clockwork_station".equals(area)) return "archive_mystery";' not in s:
 s=s.replace('if ("starfall_village".equals(area)) return "star_village";',
             'if ("starfall_village".equals(area)) return "star_village";\n        if ("clockwork_station".equals(area)) return "archive_mystery";\n        if ("moonlight_lake".equals(area)) return "lake_moon";\n        if ("memory_bridge".equals(area)) return "star_road";')
if 'if ("moonlight_lake".equals(area)) return "lake_water";' not in s:
 s=s.replace('if ("rain_garden".equals(area)) return "rain_outdoor";',
             'if ("rain_garden".equals(area)) return "rain_outdoor";\n        if ("clockwork_station".equals(area) || "memory_bridge".equals(area)) return "magic_chimes";\n        if ("moonlight_lake".equals(area)) return "lake_water";')
s=s.replace('|| "galeri_komunitas".equals(area)) return "step_wood";',
            '|| "galeri_komunitas".equals(area) || "clockwork_station".equals(area)) return "step_wood";')
p.write_text(s)
assert all(v in s for v in ('cinema_clockwork_v471','cinema_two_sides_v471','cinema_quiet_reveal_v471','v471_memory_chime'))
print('PASS: C05 offline audio registration + world ambience')
