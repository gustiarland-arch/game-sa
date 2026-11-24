#!/usr/bin/env python3
"""Static release gate: verifies bundled assets, metadata, permissions and source references.
Does NOT compile Android, certify OpenGL, test native 16 KB binaries, or prove store acceptance.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'android/assets'
SOURCE = ROOT / 'core/src/main/java/com/arlandsofia/olu'
CHECKS = 0

def check(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise AssertionError(f'RELEASE GATE FAIL: {message}')

build = (ROOT/'build.gradle').read_text()
android = (ROOT/'android/build.gradle').read_text()
entry = (SOURCE/'OluGame.java').read_text()
version = re.search(r"appVersionName\s*=\s*'([^']+)'", build).group(1)
check(version in ('3.2.0','3.3.0','3.4.0','3.5.0','3.6.0','3.7.0'), 'supported v3.x metadata')
check('VERSION = "'+version+'"' in entry, 'runtime version')
check(f'appVersionCode = {30+int(version.split(".")[1])}' in build, 'versionCode')
check('compileSdk 36' in android and 'targetSdk 36' in android, 'API 36 baseline')
check("version '8.10.0'" in build, 'AGP version')
check("gdxVersion = '1.14.2'" in build, 'LibGDX version')
check('OLU_RELEASE_KEYSTORE' in android and 'OLU_RELEASE_STORE_PASSWORD' in android, 'release signing external-only')
check('buildTypes' in android and 'minifyEnabled false' in android, 'release variant exists')
check((ROOT/'gradle/wrapper/gradle-wrapper.jar').is_file(), 'gradle wrapper bundled')
check((ROOT/'gradlew').is_file() and (ROOT/'gradlew.bat').is_file(), 'both Gradle launchers')

manifest = ET.parse(ROOT/'android/AndroidManifest.xml').getroot()
ANDROID = '{http://schemas.android.com/apk/res/android}'
TOOLS = '{http://schemas.android.com/tools}'
for perm in manifest.findall('uses-permission'):
    if perm.get(ANDROID+'name') in ('android.permission.INTERNET', 'android.permission.ACCESS_WIFI_STATE', 'android.permission.ACCESS_NETWORK_STATE'):
        check(perm.get(TOOLS+'node') == 'remove', 'network permissions removed')
app = manifest.find('application')
check(app.get(ANDROID+'allowBackup') == 'false', 'app private backup policy')
check(app.get(ANDROID+'usesCleartextTraffic') == 'false', 'cleartext disabled')
check(app.find('activity').get(ANDROID+'screenOrientation') == 'sensorLandscape', 'landscape orientation')

for filename in ('data/quests.json','data/maps.json','data/story.json','data/memory_book.json','data/props.json'):
    check((ASSETS/filename).is_file(), filename)
    json.loads((ASSETS/filename).read_text(encoding='utf8'))

maps = list((ASSETS/'maps').glob('*.png'))
check(len(maps)==22,'22 world maps')
check(len(list((ASSETS/'characters').glob('*/poses.png')))==25,'25 pose sheets')
check(len(list((ASSETS/'characters').glob('*/walk_plus.png')))==25,'25 walk atlases')

# Every soundtrack ID in Java must have its expected local audio asset.
plan = (SOURCE/'logic/SoundscapePlan.java').read_text()
def ids(identifier):
    match = re.search(r'public static final String\[\]\s+'+identifier+r'\s*=\s*\{(.*?)\};',plan,re.S)
    check(match is not None, 'audio catalog '+identifier)
    return re.findall(r'"([^"]+)"',match.group(1))
old, music, cinema, ambients, sfx = (ids(k) for k in ('LEGACY','MUSIC','CINEMATIC','AMBIENTS','SFX'))
check(len(old)+len(music)+len(cinema)==40, '40 tracks')
check(len(ambients)==14,'14 ambience')
check(len(sfx)==32,'32 sfx')
for name in old: check((ASSETS/'audio/music'/f'{name}_theme.ogg').is_file(), 'classic music '+name)
for name in music+cinema: check((ASSETS/'audio/music'/f'{name}.ogg').is_file(), 'music '+name)
for name in ambients: check((ASSETS/'audio/ambience'/f'{name}.ogg').is_file(), 'ambience '+name)
for name in sfx: check((ASSETS/'audio/sfx'/f'{name}.wav').is_file(), 'sfx '+name)
actual_audio = list((ASSETS/'audio/music').glob('*.ogg'))+list((ASSETS/'audio/ambience').glob('*.ogg'))+list((ASSETS/'audio/sfx').glob('*.wav'))
check(len(actual_audio)==86, '86 audio in one source folder')
for audio in actual_audio:
    raw = audio.read_bytes()
    check(audio.stat().st_size >= 300, 'nontrivial audio '+str(audio))
    check(raw[:4] == (b'RIFF' if audio.suffix=='.wav' else b'OggS'), 'audio magic '+str(audio))

images = list(ASSETS.rglob('*.png'))
for picture in images:
    with Image.open(picture) as im:
        im.verify()
    check(picture.stat().st_size > 0, 'image nonempty '+str(picture))

check((SOURCE/'logic/Achievements.java').is_file(), 'achievement engine present')
check('achievements' in (SOURCE/'logic/GlobalProgress.java').read_text(), 'achievements saved globally')
check('tabAchievements' in (SOURCE/'game/MemoryBookOverlay.java').read_text(), 'achievements integrated in UI')
check('INCOMPATIBLE' in (SOURCE/'logic/SaveStore.java').read_text(), 'future schema guard')
check('.bak2' in (SOURCE/'logic/SaveStore.java').read_text(), 'double backup recovery')
check('warmArea(a)' in (SOURCE/'screens/GameScreen.java').read_text(), 'lazy prop warmup integration')
check((ROOT/'tools/test_release_v29.sh').exists(), 'release resilience tests')
check((ROOT/'.github/workflows/release-candidate.yml').exists(), 'signed release pipeline')

# Ship a reproducible source-assets hash manifest for detecting any missing/corrupt upload.
manifest_data = {
    'game': 'Arland & Sofia: Our Little Universe',
    'version': version,
    'format': 1,
    'note': 'Source asset hashes v3.2, excludes generated binaries and private saves',
    'files': {str(file.relative_to(ASSETS)).replace('\\','/'): hashlib.sha256(file.read_bytes()).hexdigest()
              for file in sorted(ASSETS.rglob('*')) if file.is_file()}
}
baseline = json.loads((ROOT/'docs/ASSET_SHA256_V3.0.json').read_text(encoding='utf8'))['files']
check(set(baseline).issubset(set(manifest_data['files'])), 'all v3.0 source assets still exist')
changed = []
allowed = ('maps/', 'props/', 'characters/arland/portraits/', 'characters/sofia/portraits/')
for asset, old_hash in baseline.items():
    if manifest_data['files'][asset] != old_hash:
        check(asset.startswith(allowed), 'unexpected legacy file mutation: ' + asset)
        changed.append(asset)
check(len(changed) >= 22 + 190 + 15, 'visual assets not substantively updated')
check(len(list((ASSETS/'ui/v32_cinema').glob('*.png')))==12,'12 integrated cinema illustrations')
check(len(list((ASSETS/'characters').glob('*/walk_v32.png')))==25,'25 upgraded walking sheets')
check(len(list((ASSETS/'characters').glob('*/idle_v32.png')))==25,'25 new idle sheets')
check((ROOT/'tools/visual_overhaul_v32.py').exists(),'reproducible visual generator')
check((ROOT/'art_source/visual_v32_base/maps/plaza.png').exists(),'original map source preserved')
check('walk_v32.png' in (SOURCE/'Assets.java').read_text(),'v3.2 walking atlas in renderer')
check('v32_menu_far.png' in (SOURCE/'screens/TitleScreen.java').read_text(),'new panorama in title screen')
check('v32_cinema/' in (SOURCE/'game/CutscenePlayer.java').read_text(),'12 cinema stills wired')
manifest_data['note'] = 'v3.2 full source assets incl original art in art_source/visual_v32_base; intentional visual changes audited'
if version == '3.2.0':
    (ROOT/'docs/ASSET_SHA256_V3.2.json').write_text(json.dumps(manifest_data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
check((SOURCE/'logic/DialogueHistory.java').exists() and 'dialogueHistory' in (SOURCE/'logic/Progress.java').read_text(), 'dialogue log persistence')
check((SOURCE/'logic/QuestCompass.java').exists(), 'quest compass exists')
check('tabExplore' in (SOURCE/'game/MemoryBookOverlay.java').read_text(), 'exploration tab integrated')
check('autosaveAcc >= 90f' in (SOURCE/'screens/GameScreen.java').read_text(), 'safe timed autosave')
check('schema >= 7' in (SOURCE/'logic/Progress.java').read_text(), 'schema7 migration')
check(f'appVersionCode = {30+int(version.split(".")[1])}' in build, 'versionCode matches versionName')
print(f'RELEASE STATIC AUDIT {version} OK: {CHECKS} assertions | {len(images)} PNG | 86 audio | 22 maps | API36 | source assets {len(manifest_data["files"])} files')
print('BLOCKERS: Android SDK/Gradle build, actual device QA, native 16 KB alignment, signing/Play Console NOT verified here.')
