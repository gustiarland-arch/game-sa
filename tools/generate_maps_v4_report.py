#!/usr/bin/env python3
"""Human-readable complete coordinate report and image review gallery."""
from pathlib import Path
import json, math
from PIL import Image,ImageOps,ImageDraw,ImageFont
R=Path(__file__).resolve().parent.parent;A=R/'android/assets';D=A/'data';DOC=R/'docs';PR=DOC/'preview';PR.mkdir(parents=True,exist_ok=True)
M=json.loads((D/'maps.json').read_text())['areas'];Q=json.loads((D/'quests.json').read_text());MD=json.loads((DOC/'MAPS_V4_MAPPING.json').read_text());ids=list(MD['input_original_name_by_area'])
assets=D;out=[]
out+=['# Arland & Sofia v4.0 — Sembilan Map, Collision dan Koordinat', '',
      'Seluruh koordinat dalam **piksel gambar dengan titik (0,0) di kiri atas; X ke kanan, Y ke bawah**.',
      'Semua gambar runtime berukuran **1200 × 896 px**, memakai filter **Nearest** dari `Assets.java`.',
      'Kolom `rect` menggunakan urutan `[x, y, width, height]`. Radius trigger menggunakan piksel.',
      'Untuk data lengkap machine-readable (termasuk seluruh 9 matriks obstacle): `docs/MAPS_V4_MAPPING.json` dan `android/assets/data/maps.json`.',
      '', '## Penting: pemetaan nama gambar unggahan', '',
      'Berkas ZIP pengguna bernama tidak sesuai dengan isi visualnya. Gambar dipetakan berdasarkan isi yang diperiksa, tanpa memakai `01_jalan_kota.png` yang berupa collage perbandingan.',
      '', '| ID map game | Nama asal di ZIP | File runtime |','|---|---|---|']
for area in ids:out.append(f'| `{area}` | `{MD["input_original_name_by_area"][area]}` | `android/assets/maps/{area}.png` |')
out+=['','## Spawn, portal dan interaction zones','','Legenda: `spawnPoint` adalah titik kaki pemain; `arrival` adalah titik kaki setelah pindah map. **Jangan** tempatkan arrival di dalam portal lain.','']
allpoints={}
for id in ids:
 m=M[id]
 out+=[f'### {m["name"]} — `{id}`','',f'- Resolusi: **{m["w"]} × {m["h"]}**',f'- SpawnPoint: **({m["spawn"][0]}, {m["spawn"][1]})**',f'- Collision: **{len(m["walls"])} rectangle/alcove mask**, {len(m["props"])} foreground Y-sort overlay dengan collision terpisah.','', '**Portals**','','| ID portal | Trigger rect | Tujuan map | Arrival (X,Y) |','|---|---|---|---|']
 for d in m['doors']:out.append(f'| `{d["id"]}` | `{d["rect"]}` | `{d["to"]}` | **({d["tx"]}, {d["ty"]})** |')
 out+=['','**Interaction zones — investigasi dan cerita utama**','','| Trigger ID | Pusat (X,Y) | Radius | Keterangan |','|---|---|---|---|']
 points={}
 for e in m['examine']:
  pid='examine:'+e['id'];points[pid]={'x':e['x'],'y':e['y'],'r':e.get('r',56)}
  out.append(f'| `{pid}` | ({e["x"]}, {e["y"]}) | {e.get("r",56)} | {e["label"]} |')
 for step in Q['steps']:
  for it in step.get('interactables',[]):
   if it['area']!=id:continue
   pid=it['id']
   if pid in points:continue
   points[pid]={'x':it['x'],'y':it['y'],'r':it.get('r',64)}
   out.append(f'| `{pid}` | ({it["x"]}, {it["y"]}) | {it.get("r",64)} | `{step["id"]}` — {it["label"]} |')
 out+=['',f'**NPC dan side/event**: {len([n for n in Q["townNpcs"] if n["area"]==id])} NPC lokasi, {len([a for a in Q["side"] if a.get("area")==id])} interaksi opsional. Koordinat lengkapnya ada di `android/assets/data/quests.json`.','']
 allpoints[id]=points
(DOC/'MAPS_V4_INTERACTIONS.json').write_text(json.dumps(allpoints,ensure_ascii=False,indent=2)+'\n')
out+=['## Kompatibilitas dan batasan','',
 '- Seluruh ID `door`, `quest`, `step`, `scene`, dan item dipertahankan.',
 '- Objek furniture sudah tergambar di PNG; sprite prop lama disembunyikan pada sembilan area agar tidak menumpuk. Foreground object tertentu digunakan kembali sebagai overlay Y-sort tanpa hitbox ganda.',
 '- Obstacle adalah matriks geometri yang ditentukan berdasarkan objek pada gambar, menggunakan rectangle majemuk untuk lekukan/alcove. Ini bukan collider pixel-perfect per piksel.',
 '- Titik quest umum yang berada dalam obstacle dipindahkan ke posisi berdiri terdekat. Titik utama (buku, meja, komputer, kasir, dapur, papan investigasi) diberi anchor manual.',
 '- Save schema 8 menambah `mapLayoutVersion=4` untuk migrasi posisi dari v3.x. Item, cerita, dan pilihan tetap tersimpan; posisi pada obstacle disnap ke titik legal saat resume.',
 '- Build Android aktual dan visual runtime perlu diuji di perangkat. Tes headless tidak menguji kualitas perspektif, clipping pixel art, maupun gesture sentuh sebenarnya.',
 '', '## Cara mengedit dan membangun ulang','',
 '1. Edit `art_source/maps_v4_input/<id>.png` untuk artwork (1200×896). Baseline v3.7 tersedia di `art_source/maps_v37_baseline/`.',
 '2. Edit `GEOMETRY`, `POIS`, `TRIGGERS`, dan `FOREGROUND` dalam `tools/maps_v4_upgrade.py`.',
 '3. Untuk regenerasi penuh jalankan `bash tools/build_all.sh`; script memasang layout v4 setelah generator map & konten lama selesai.',
 '4. Jalankan `python3 tools/check_layout.py android/assets`, `python3 tools/test_maps_v4.py`, `bash tools/test_maps_v4_save.sh`, dan `bash tools/test_logic.sh`.',
 '5. Build APK melalui Gradle/Android SDK pada mesin dengan dependensi tersedia. Jangan mengklaim APK lulus berdasarkan tes headless.','']
(DOC/'MAPS_V4_COORDINATES.md').write_text('\n'.join(out),encoding='utf8')
font=ImageFont.load_default()
def resize(im,w,h):
 return ImageOps.contain(im,(w,h),Image.Resampling.LANCZOS)
# Gallery of all nine exact supplied maps (not AI rendered or emulator screenshot)
W,H=480,360;pad=18;head=44;rows=3;cols=3
for mode in ('gallery','collision'):
 dst=Image.new('RGB',(cols*(W+pad)+pad,rows*(H+head+pad)+pad),(25,27,36));d=ImageDraw.Draw(dst)
 for i,id in enumerate(ids):
  mp=M[id];im=Image.open(A/mp['image']).convert('RGBA')
  if mode=='collision':
   ov=Image.new('RGBA',im.size,(0,0,0,0));draw=ImageDraw.Draw(ov)
   for x,y,w,h in mp['walls']:draw.rectangle((x,y,x+w,y+h),fill=(231,48,62,65),outline=(234,60,76,130),width=2)
   for door in mp['doors']:
    x,y,w,h=door['rect'];draw.rectangle((x,y,x+w,y+h),fill=(44,127,239,170),outline=(200,220,255,255),width=3)
   x,y=mp['spawn'];draw.ellipse((x-14,y-14,x+14,y+14),fill=(40,255,140,245))
   for pt in allpoints[id].values():
    x,y=pt['x'],pt['y'];draw.ellipse((x-7,y-7,x+7,y+7),fill=(255,204,65,255))
   im.alpha_composite(ov)
  scaled=resize(im.convert('RGB'),W,H)
  x0=(i%cols)*(W+pad)+pad;y0=(i//cols)*(H+head+pad)+pad
  d.rounded_rectangle((x0-1,y0-1,x0+W+1,y0+H+head+1),radius=6,fill=(41,45,57))
  dst.paste(scaled,(x0+(W-scaled.width)//2,y0+head+(H-scaled.height)//2))
  d.text((x0+12,y0+14),f'{i+1:02d}  {mp["name"]} / {id}',fill=(250,247,240),font=font)
 dst.save(PR/('v40_nine_maps_'+mode+'.jpg'),quality=88)
print('Coordinate docs and 2 asset previews created', len(out),'lines')
