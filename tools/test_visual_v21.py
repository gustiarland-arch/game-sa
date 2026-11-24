"""Static v2.1 visual asset integrity checks (not an OpenGL/Android runtime test)."""
from PIL import Image, ImageChops
from pathlib import Path
import json, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'android/assets')
checks=0
for asset,wh in [('ui/v21_skyline.png',(1280,720)),('ui/v21_foreground.png',(1280,720)),
 ('ui/v21_dialog_ribbon.png',(512,128)),('ui/v21_bloom.png',(256,256))]:
 im=Image.open(root/asset).convert('RGBA'); assert im.size==wh,(asset,im.size)
 assert im.getbbox() is not None,asset
 checks+=1
for asset in ['panel','panel_dark','button','button_down','button_accent','button_disabled']:
 im=Image.open(root/'ui'/f'{asset}_v21.png').convert('RGBA')
 assert im.size==(48,48),asset
 assert im.getpixel((0,0))[3]==0,asset
 checks+=1
actors=[]
for source in sorted((root/'characters').glob('*/walk.png')):
 im=Image.open(source).convert('RGBA')
 if im.size != (144,288): continue
 plus=Image.open(source.parent/'walk_plus.png').convert('RGBA')
 assert plus.size == (384,288),source
 for row in range(4):
  phases=[plus.crop((f*48,row*72,(f+1)*48,(row+1)*72)) for f in range(8)]
  assert phases[0].getbbox() is not None,source
  assert len({x.tobytes() for x in phases})>=4,(source,row,'insufficient motion phases')
  # Base at phase 0 must reproduce the source's idle/standing frame.
  assert ImageChops.difference(phases[0],im.crop((0,row*72,48,(row+1)*72))).getbbox() is None,(source,row)
  checks+=1
 actors.append(source.parent.name)
assert 'arland' in actors and 'sofia' in actors
assert len(actors)>=20,len(actors)
q=json.loads((root/'data'/'quests.json').read_text())
s=json.loads((root/'data'/'story.json').read_text())
assert len(s['scenes'])>=303
assert len(q['steps'])>=84
# The new cinematic events must remain reachable through the original story quest steps.
for sid, fxkind in [('C06_Q_REVEAL','restore'),('EPI_FEST_LEPAS','lanterns')]:
    step=next(st for st in q['steps'] if st['id']==sid)
    acts=[a for it in step['interactables'] for a in it['actions']]
    assert any(a.get('do')=='cine' and any(c.get('c')=='fx' and c.get('kind')==fxkind
                                      for c in a.get('cmds',[])) for a in acts),(sid,fxkind)
    checks+=1
print(f'VISUAL v2.1 OK: {len(actors)} atlases, 6 ninepatch skins, 4 illustration assets, {checks} integrity checks')
