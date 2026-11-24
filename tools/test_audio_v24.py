#!/usr/bin/env python3
"""Validate original v2.4 audio, selectors and backward compatibility.
This test does NOT prove that Android audio playback or real-time mixing works on-device.
"""
from pathlib import Path
import hashlib, json, subprocess, sys, tempfile
root=Path(sys.argv[1] if len(sys.argv)>1 else 'android/assets/audio')
base=root.parent
catalog=json.loads((root/'soundscape_v24.json').read_text(encoding='utf-8'))
assert catalog['schema']==1
legacy=['town','memory','cafe','rain','night','star','tender','game']
legacy_sfx=['page','sparkle','soft_wrong']
assert len(catalog['music'])==25 and len(catalog['ambience'])==14 and len(catalog['sfx'])==25
checks=0; hashes=set()
for track in catalog['music']+catalog['ambience']+catalog['sfx']:
    path=base/track['path'];assert path.is_file() and path.stat().st_size>250,(track,path)
    fp=hashlib.sha256(path.read_bytes()).hexdigest();assert fp not in hashes,(track,'duplicate');hashes.add(fp)
    args=['ffprobe','-v','error','-show_entries','stream=codec_name,channels,sample_rate:format=duration','-of','json',str(path)]
    p=subprocess.run(args,capture_output=True,text=True,check=True)
    data=json.loads(p.stdout)
    actual=float(data['format']['duration']); reported=float(track['seconds'])
    assert abs(actual-reported)<0.15,(path,actual,reported)
    assert actual>0.1,(path,actual)
    codec=data['streams'][0]['codec_name'];ext=path.suffix.lower()
    assert codec==('vorbis' if ext=='.ogg' else 'pcm_s16le'),(path,codec)
    checks+=4
for a in legacy:assert (root/'music'/f'{a}_theme.ogg').is_file();checks+=1
for a in legacy_sfx:assert (root/'sfx'/f'{a}.wav').is_file();checks+=1
assert len(list((root/'music').glob('*.ogg')))>=33
assert len(list((root/'ambience').glob('*.ogg')))==14
assert len(list((root/'sfx').glob('*.wav')))>=28
assert len(hashes)==64
print(f'AUDIO v2.4 LEGACY OK: 33 BGM, 14 ambience, 28 SFX = 75 original files preserved; {checks} checks')
