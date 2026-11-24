#!/usr/bin/env python3
"""Static release gate for the v4.x source; does not replace Android build."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parent.parent
A=R/'android/assets'; n=0

def check(ok, label):
 global n
 n+=1
 if not ok: raise AssertionError('v4 release gate: '+label)

gradle=(R/'build.gradle').read_text()
vn=re.search(r"appVersionName\s*=\s*'([0-9]+\.[0-9]+\.[0-9]+)'",gradle)
vc=re.search(r'appVersionCode\s*=\s*([0-9]+)',gradle)
game=(R/'core/src/main/java/com/arlandsofia/olu/OluGame.java').read_text()
check(vn is not None and vn.group(1).startswith('4.'),'v4 versionName')
check(vc is not None and int(vc.group(1))>=40,'v4 versionCode')
check('VERSION = "'+vn.group(1)+'"' in game,'game version matches gradle')
check('SCHEMA = 8' in (R/'core/src/main/java/com/arlandsofia/olu/logic/Progress.java').read_text(),'save schema')
check('Texture.TextureFilter.Nearest' in (R/'core/src/main/java/com/arlandsofia/olu/Assets.java').read_text(),'nearest pixel filter')
check('maps_v4_upgrade.py' in (R/'tools/build_all.sh').read_text(),'full source rebuild')
check('maps_v4_upgrade.py' in (R/'tools/test_logic.sh').read_text(),'logic rebuild')
check((R/'gradle/wrapper/gradle-wrapper.jar').exists(),'gradle wrapper')
manifest=(R/'android/AndroidManifest.xml').read_text()
check('android.permission.INTERNET' in manifest and 'tools:node="remove"' in manifest,'network permission explicitly removed during manifest merge')
for f in ['MAPS_V4_MAPPING.json','MAPS_V4_COORDINATES.md','MAPS_V4_BASELINE_SHA256.json','MAPS_V4_INTERACTIONS.json']:
 check((R/'docs'/f).is_file(),f+' included')
for workflow in ['build-apk.yml','release-candidate.yml']:
 s=(R/'.github/workflows'/workflow).read_text()
 check('test_maps_v4.py' in s and 'release_audit_v4.py' in s,'workflow '+workflow)
for file in A.rglob('*'):
 if file.is_file():check(not file.name.endswith(('.pyc','.tmp','.DS_Store')) and not file.name.startswith('._'),str(file))
print('V4 RELEASE STATIC AUDIT:',n,'assertions passed. Real Android build still required.')
