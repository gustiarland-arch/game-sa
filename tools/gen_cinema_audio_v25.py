#!/usr/bin/env python3
"""Seven original, self-generated cinematic audio cues, no samples. Does not regenerate old files."""
from pathlib import Path
import importlib.util, sys
ROOT = Path(__file__).resolve().parents[1]
sys.argv = ['gen_soundscape_v24.py', str(ROOT/'android/assets/audio')]
spec=importlib.util.spec_from_file_location('sound_v24', ROOT/'tools/gen_soundscape_v24.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
CUES=[
 ('cinema_first_meet',71,0,0,510,'C4'),
 ('cinema_memory_portal',86,5,1,511,'D3'),
 ('cinema_rain_conflict',64,4,1,512,'E3'),
 ('cinema_reconciliation',73,1,0,513,'F3'),
 ('cinema_quiet',68,4,1,514,'A3'),
 ('cinema_lantern_finale',102,5,0,515,'G3'),
 ('cinema_our_tomorrow',80,0,0,516,'C3'),
]
if __name__=='__main__':
 for cue in CUES:
  duration=module.make_song(*cue)
  print(cue[0],round(duration,1),'sec',flush=True)
