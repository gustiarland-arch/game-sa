#!/usr/bin/env python3
"""Static package audit to catch accidental loss of legacy assets/features in v2.8."""
from pathlib import Path
import json
import re
r=Path(__file__).resolve().parents[1]
a=r/'android/assets'
checks=0
def ck(ok, msg):
    global checks
    checks+=1
    if not ok:raise AssertionError(msg)
core=r/'core/src/main/java/com/arlandsofia/olu'
settings=(core/'logic/Settings.java').read_text()
model=(core/'logic/TouchInputModel.java').read_text()
control=(core/'game/TouchControls.java').read_text()
screen=(core/'screens/GameScreen.java').read_text()
panel=(core/'ui/SettingsPanel.java').read_text()
ck(int(re.search(r'SCHEMA\s*=\s*(\d+)', (core/'logic/Progress.java').read_text()).group(1)) >= 6,'save schema preserved')
for flag in ('leftHanded','floatingJoystick','joystickSensitivity'):
    ck(flag in settings and flag in screen and flag in panel,'missing setting integration '+flag)
for tag in ('touchDown','touchDragged','touchUp','consumeAction','reset','layout'):
    ck(tag in model,'missing multitouch method '+tag)
for tag in ('propMetrics','visibleActor','propVisible(pr)','drawMarkers.clear()','super.pause()','super.resume()'):
    ck(tag in screen,'missing rendering/lifecycle improvement '+tag)
for category in ('Audio','Tampilan','Kontrol'):
    ck(category in panel,'missing settings category '+category)
import re
m=re.search(r"appVersionName\s*=\s*'(\d+\.\d+\.\d+)'",(r/'build.gradle').read_text())
ck(m is not None,'version declared in gradle')
version=m.group(1)
ck('VERSION = "'+version+'"' in (core/'OluGame.java').read_text(),'app version consistent')
ck('v'+version.rsplit('.',1)[0]+'-debug-apk' in (r/'.github/workflows/build-apk.yml').read_text(),'workflow artifact matches')
ck((r/'docs/ANDROID_CONTROLS_V2.8.md').exists(),'docs')
for kind,expected in (('music',40),('ambience',14),('sfx',32)):
    files=list((a/'audio'/kind).glob('*.*'))
    ck(len(files)==expected,f'{kind}: got {len(files)} expected {expected}')
    for path in files:ck(path.stat().st_size>128,f'empty audio {path}')
ck(len(list((a/'maps').glob('*.png')))==22,'22 maps intact')
ck(len(list((a/'characters').glob('*/poses.png')))==25,'25 characters intact')
q=json.loads((a/'data/quests.json').read_text())
ck(len(q.get('worldEvents',[])) == 14,'14 world events preserved')
print('ANDROID V2.8 SOURCE / ASSET AUDIT OK:',checks,'checks')
