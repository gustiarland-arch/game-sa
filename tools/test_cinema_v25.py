#!/usr/bin/env python3
"""Verifikasi v2.5: musik OGG asli, SFX WAV, portrait, minigame, dan perintah cerita.
Ini pengujian aset/data lokal, BUKAN pengganti rendering/build APK Android.
"""
from pathlib import Path
from PIL import Image, ImageChops
import json, subprocess, wave

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'android/assets'
checks = 0

def test(value, label):
    global checks
    checks += 1
    assert value, label

music = ['cinema_first_meet','cinema_memory_portal','cinema_rain_conflict',
         'cinema_reconciliation','cinema_quiet','cinema_lantern_finale','cinema_our_tomorrow']
sfx = ['flower_pick','paper_fold','cinema_heartbeat','cinema_whoosh']
for cue in music:
    path=A/'audio/music'/(cue+'.ogg')
    test(path.exists() and path.stat().st_size>10000, f'missing OGG {cue}')
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries',
                 'stream=codec_name,channels:format=duration','-of','json',str(path)],text=True))
    test(meta['streams'][0]['codec_name']=='vorbis',f'codec {cue}')
    test(24 <= float(meta['format']['duration']) <= 150,f'duration {cue}')
for cue in sfx:
    path=A/'audio/sfx'/(cue+'.wav')
    test(path.exists() and path.stat().st_size>1500,f'missing SFX {cue}')
    with wave.open(str(path),'rb') as sound:
        test(sound.getnchannels()==1 and sound.getsampwidth()==2,f'PCM {cue}')
        test(sound.getnframes()/sound.getframerate()>=.25,f'length {cue}')
test(len(list((A/'audio/music').glob('*.ogg')))>=42,'40 original music cues plus 2 gallery story cues')
test(len(list((A/'audio/ambience').glob('*.ogg')))==14,'ambience total 14')
test(len(list((A/'audio/sfx').glob('*.wav')))>=32,'at least 32 original SFX retained; new story SFX allowed')
for person in ('arland','sofia'):
    for emotion,base in [('jatuh_cinta','malu'),('khawatir','sedih'),('lega','senang')]:
        folder=A/'characters'/person/'portraits'
        new=Image.open(folder/(emotion+'.png')).convert('RGBA')
        original=Image.open(folder/(base+'.png')).convert('RGBA')
        test(new.size==original.size,(person,emotion,'size'))
        test(bool(ImageChops.difference(new,original).getbbox()),(person,emotion,'not changed'))
q=json.loads((A/'data/quests.json').read_text(encoding='utf-8'))
story=json.loads((A/'data/story.json').read_text(encoding='utf-8'))
book=json.loads((A/'data/memory_book.json').read_text(encoding='utf-8'))
games=q['romance']['games']
test(len(games)==6,'six romance minigames')
test({'bouquet','scrapbook'}.issubset(q['minigames']),'two new playable minigames')
unlocks={e['unlock'] for e in book['entries']}
for game in games:
    test(game['minigame'] in q['minigames'],(game['id'],'missing executable game'))
    test('ROM_GAME_'+game['id'].upper()+'_ONCE' in unlocks,(game['id'],'memory missing'))
    for route in ('arland','sofia'):
        scene=story['scenes'].get(game['scene']+'@'+route)
        test(scene is not None and scene['route']==route,(route,game['id']))
        test(len(scene['lines'])>=3,(route,game['id'],'dialogue'))
# Cinematic cues exist in story action definitions; credits cue is specifically triggered by game screen.
content=(ROOT/'tools/build_content.py').read_text(encoding='utf-8')
for cue in music[:-1]:
    test("'"+cue+"'" in content,f'cue unused: {cue}')
test('cinema_our_tomorrow' in (ROOT/'core/src/main/java/com/arlandsofia/olu/screens/GameScreen.java').read_text(), 'finale credits cue missing')
print(f'CINEMATIC ROMANCE & STORY v4.6.5 OK: {checks} checks, 42+ music + 14 ambience + 32+ SFX, 6 games, 6 portraits')
