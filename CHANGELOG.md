## 5.4.0 — Cuaca & Air (25 November 2026)

- **Air mengalir:** arus permukaan di Tepi Danau (14 px/s) dan Dermaga Danau (7 px/s), sungai
  Hutan Bisik mengikuti alur yang dilukis di peta (`waterFlow` di `maps.json`, `WorldFx.drawFlowV54`/
  `drawRiverV54`). Air mancur plaza dan air terjun hutan kini bergerak: tetesan jatuh dengan
  gravitasi, kilau yang mengalir, percikan di kolam dan kabut di kaki air terjun.
- **Petir:** saat hujan di luar ruangan, kilat lembut tiap 9–22 detik dan guntur menyusul 0,35–2,25
  detik kemudian (makin dekat makin keras). Maksimal dua denyut per sambaran dan alpha 0,24, jadi
  tidak pernah lebih dari tiga kilatan per detik (WCAG 2.3.1). Tidak ada petir di dalam ruangan,
  Memory Realm, Taman Hujan, atau saat kamera cutscene aktif.
- **Genangan:** 3–16 genangan per map luar ruangan, tidak pernah di collider, air, teras, atau tangga.
  Muncul bertahap saat hujan (±45 detik) dan mengering pelan (±2 menit), ada riak hujan dan pantulan
  kilat. Melangkah di genangan memunculkan percikan dan suara `v54_step_puddle`.
- Aset baru dibuat offline oleh `tools/gen_weather_fx_v54.py`: 3 tekstur genangan, `v54_thunder.wav`,
  `v54_step_puddle.wav`.
- Uji baru `tools/test_v54_weather.sh` (36.571 pemeriksaan): keamanan kilat, waktu guntur, genangan
  di semua 21 map luar ruangan, data arus air, dan aset. Smoke `test_visual_fx.sh` memanggil semua
  method baru.
- `AudioManager.tap` (null di game) untuk rekaman/QA otomatis. Harness rekaman desktop di
  `tools/capture_v54/`.
- Save schema 8, dua route, canon ending, quest, collision, dan 29 map tidak diubah.

## 5.4.0 — Interior scale rebalance (24 November 2026)

- Empat interior handcrafted v4 (kamar Arland, kamar Sofia, dapur, ruang arsip) dilukis
  ±2x lebih besar dari skala karakter: kursi bar setinggi orang, lemari 3x tinggi badan.
  Seluruh ruang dunia keempat area diperkecil 0.5x secara seragam (`tools/room_scale_v54.py`):
  gambar map, sprite furnitur khusus ruangan, tembok, pintu, prop, titik examine, interaksi quest,
  posisi NPC, warp, kamera/gerak cutscene, dan pintu yang menuju ruangan tersebut.
- Karakter, hitbox kaki, dan semua map lain tidak berubah. Radius interaksi diskalakan dengan
  batas bawah 40 px. Delapan titik berdiri yang bergeser ke dalam furnitur karena hitbox kaki
  tidak ikut mengecil digeser beberapa piksel ke titik legal terdekat.
- Posisi kasur kini dibaca dari data map (`bed`), bukan konstanta di `GameScreen`.
- Save lama: `mapLayoutVersion` 5 + `MapLayoutV54` memindahkan posisi pemain di keempat ruangan;
  save schema 8, item, quest, dan pilihan tidak berubah.
- Gambar asli disimpan di `art_source/v54_room_scale/`. Pratinjau statis sebelum/sesudah:
  `docs/v54/room_scale_before_after/`.

## 5.4.0 — World Reborn, Fase 1–2 (24 November 2026)

- **Tangga & elevasi (P0):** `ElevationV50.canStep` kini menerima seluruh lebar tangga yang
  dianggap walkable oleh `stairs()`. Sebelumnya hanya pita tengah (lebar−12 px) yang boleh
  melewati bibir platform, sehingga pemain/pasangan/NPC di dekat pegangan tangga tersangkut
  saat naik atau tidak bisa turun. Ditambah pengaman lompatan frame (maks satu panjang tangga).
- **arcade:** platform digeser 17 px ke atas; kaki tangga sebelumnya berakhir di mesin arcade.
- **dermaga:** pohon di sudut tangga digeser 14 px; collider batangnya menghalangi mulut tangga.
- **Skala karakter:** `Actor.SCALE` 0.85 → 1.0 dan ukuran sprite dibulatkan ke piksel utuh.
  Arland/Sofia ±18% lebih besar terhadap furniture, dan sprite tidak lagi di-resample pada
  grid non-integer (piksel tidak rata/berkilau saat berjalan). Hitbox kaki tidak berubah.
- Uji baru `tools/test_v54_stairs.sh`: 7.948 pemeriksaan pada 21 tangga (naik, turun, berhenti
  di tengah, berbalik, pegangan, tepi tebing, input diagonal, 4 variasi frame delta, A* naik/turun,
  kontinuitas lift).
- Audit skala `tools/scale_audit_v54.py` (372 prop) dan pratinjau statis before/after
  `tools/scale_preview_v54.py` di `docs/v54/`.
- CI: perbaikan langkah Android SDK yang gagal (`setup-android` memasang paket `tools` yang
  sudah dihapus), action dinaikkan ke v5, uji v5.4 dijalankan di CI, nama artefak APK v5.4.
- Tiga uji lama yang mengunci string versi 5.x tertentu dibuat menerima versi 5.x berikutnya.
- **Pixel-perfect (Fase 4):** kamera eksplorasi memilih zoom terdekat dengan jumlah piksel layar
  utuh per texel dan mengunci posisi ke grid piksel layar (`PixelPerfectV54`). Texel tidak lagi
  tampil 2/3 px bergantian dan tidak "berkilau" saat kamera bergerak. Cutscene tidak berubah.
  Setelan `pixelPerfect` (default aktif) disimpan di settings tanpa mengubah schema.
- **Tangga (Fase 5):** pemain, pasangan, dan NPC berjalan dengan 82% kecepatan normal di anak tangga
  (`ElevationV50.speedFactor`), sehingga naik-turun terasa berbobot dan suara langkah tangga
  tidak terlalu rapat.
- Save schema 8, dua route, canon ending, quest, dan 29 map tidak diubah.

## 5.3.0 — Character Motion & NPC Identity

- 25 karakter mendapat atlas walk 24-frame dan idle 12-frame 4 arah; 8 arah untuk Arland/Sofia.
- 22 NPC menggunakan aksesori dan pakaian profesi yang berbeda (barista, florist, pustakawan,
  petugas pos, kurir, anak sekolah, penjaga, dan lainnya), berikut pose yang konsisten.
- MotionPersonalityV53: cadence/sway/bounce/idle-pose/timing dan kecepatan NPC berbeda.
- Actor: visual easing saat mulai/berhenti, turn lean ringan, variasi napas dan visual scale.
- Pengaturan collision, koordinat fisik, quest, dialog, dunia, dan save schema 8 tidak diubah.
- `tools/build_npc_motion_v53.py` menghasilkan atlas PNG baru; atlas lama tetap ada.
- Pengujian kepalaless untuk kualitas sprite dan 25 motion profile ditambahkan.
- Android APK/build perangkat nyata belum teruji; jangan anggap kompilasi statis sebagai APK release.

## 5.2.0 — 23 November 2026

- Wide exploration camera with configurable view distance (separate from cutscene zoom).
- Obstacle-aware A* quest directions, avoiding walls and decoration collisions.
- Safe spawn/door/NPC placement, swept player/companion/NPC collision checks.
- 7 formerly inaccessible interactions repositioned, blocked gallery-to-cafe landing repaired.
- Indoor/out-of-biome decorative props curated (all original assets kept editable).
- 29-map / all-quest static accessibility audit, with dedicated reproducible Java/Python tests.
- Two independent routes and canonical ending unchanged; save schema 8 preserved.
- No Android APK/device validation was possible in this environment.

---

# 5.1.0 — Natural Environment Remaster (23 November 2026)

- Ganti 21 posisi tangga v5.0 berdasarkan landmark peta asli; setiap posisi diuji jalur atas hingga kaki tangga dengan collision existing sebelum ditulis.
- Tambah 21 tekstur teras baru, 21 foreground parapet, dan 21 approach path; pertahankan semua 42 PNG aset v5.0 sebagai arsip.
- Tambah 33 tipe dekorasi PNG orisinal (bangku, pagar, ramp kayu, jembatan, dinding penahan, tanaman, lampu, penunjuk arah, batu, kolom, fountain, dll.) yang ditempatkan di 29 area.
- Pindahkan 21 penanda panorama v5.0 ke atas pelataran baru. Dua route, 157 quest steps, 874 scene, musik dan save schema 8 tidak diganti.
- Perbaiki bentrokan penempatan dekorasi dengan NPC terjadwal (contoh Bu Laras di perpustakaan) dan bebatuan di jalur tangga Star Path.
- Audit QA: validasi aset/editor, headless traversability, jalur NPC/quest, story/save dan UI tablet; status Android APK dan device terpisah.

---
# Arland & Sofia: Our Little Universe v5.0.0 — Cinematic Vertical World Overhaul

- 21 area bertangga dengan collision elevasi dan 42 RGBA editable, 21 panorama playable, 42 scene POV, 11 peningkatan cutscene utama, 19 adegan lama yang diperluas (38 dialog), 4 VFX baru, 5 lagu OGG, 2 ambience OGG, 5 SFX WAV.
- Seluruh route, main story, game offline, dan save schema v4.9 dipertahankan. Pengujian headless ada di `tools/test_v50_release.sh`; belum build APK Android nyata.

---

# Arland & Sofia: Our Little Universe v4.9.0 — Living World & Gameplay Expansion

**Full source Android Studio / LibGDX, bukan APK.** Turunan langsung dari v4.8.0; 29 area, dua route dengan satu canon ending, seluruh aset lama, dan format save schema 8 tetap dipertahankan.

**Update yang benar-benar diintegrasikan:** 29 interaksi penemuan sekali per save (satu per area); 14 minigame Memory Echo baru dengan pola berbeda untuk Arland/Sofia, masing-masing 3 tahap; 18 event harian baru dengan syarat jam/area/companion; 58 adegan discovery + 36 adegan event berdasarkan POV + 2 adegan bonus Atlas Kenangan Kecil; entri Memory Book dan tab Jelajah menunjukkan progres penemuan. Total kini 832 adegan, 335 entri Memory Book, 32 event dunia, dan 36 konfigurasi minigame.

**Validasi source:** `bash tools/test_logic.sh` lulus 32.147 pemeriksaan headless (dua route, story, quest, event, save, collision, anti-farming, Memory Echo). `bash tools/test_v30_ui_compile.sh` lulus. Kelas minigame dikompilasi dengan stub sementara, bukan engine Android yang sesungguhnya. **APK build, FPS, sentuh pada HP/tablet, dan game lengkap di perangkat fisik belum diuji.** Tetap jalankan Gradle Sync dan test perangkat Android Studio sebelum distribusi.

**Penting:** Game data JSON lengkap dalam `android/assets/data/` adalah runtime source v4.9. Script generator lama `tools/build_all.sh` ditujukan untuk versi-versi historis dan tidak boleh digunakan untuk meregenerasi JSON v4.9 tanpa mengintegrasikan penambahan v4.9 terlebih dahulu. Seluruh file Java, JSON, sprite dan audio dapat diedit. Petunjuk lebih lanjut ada dalam `RELEASE_STATUS_V490.md`.

---

# v4.8.0 — Story World & Cinematic Polish (23 November 2026)
- Tujuh peta eksklusif cerita diremaster melalui layer RGBA editable, komposit di PNG runtime.
- Lima original score baru OGG Vorbis stereo 44.1 kHz (durasi 75–88 detik), diregistrasi dan dipicu di enam momen utama.
- Cutscene kursi kosong dari Arland/Sofia, Rain Garden, The Quiet, future hall, dan lakeside epilog mendapatkan shot/tint/fx baru.
- Memperbaiki softlock pada Chapter 2 route Sofia saat menolak kencan (galeri hanya terbuka saat quest sketsa mandiri).
- Pertahankan 29 area, 736 scene, 157 quest step, 287 Memory Book entries, 2 route, 1 canon ending, schema save.
- Menambah uji artefak v4.8.0 dan menyinkronkan pipeline regenerasi; belum diverifikasi sebagai APK release.

---

## v4.7.4 — FULL SOURCE STORY OVERHAUL, Prologue Narrative Lock (23 November 2026)

- Prolog dua route kini memiliki pilihan pesan dan pengerjaan hadiah dalam dua tahap, pilihan simbol/pita dan catatan, tiga shards dua perspektif, cutscene, original OGG musik dan empat PNG pixel-art.
- Semua keputusan Prolog diberi callback adegan di Plaza atau Epilog, tidak berhenti pada flag tanpa tindak lanjut. Referensi yang cocok hadir di Chapter 1 dan Memory Book.
- Semua chapter telah diintegrasikan, termasuk 29 area, konflik The Empty Seat, akhir yang mengingat keputusan; tetap satu canon ending.
- Dua stage baru mengunci pintu kamar secara aman; langkah quest Prolog lama tetap kompatibel dengan save lama.
- Generator Prolog dapat dijalankan ulang tanpa menduplikasi data, adegan, atau reward; tes khusus 96 rute / 12.465 check plus 438 pemeriksaan media lulus.
- Semua 1.980 source file baseline v4.6.6 ada dan 807 aset media Android lama SHA-identik. Full source versionName dan UI diubah menjadi v4.7.4.
- **Tidak ada APK build atau playtest fisik.** Gradle distribution tidak tersedia dan unduhan eksternal terhalang. Jangan mengklaim sempurna 100% atau durasi main sudah terukur.
- Laporan lengkap: `docs/STORY_OVERHAUL_V474_FULL_RELEASE_AUDIT.md`.

## Story Overhaul 3.0 — Epilogue v4.7.3 (PRIVATE DRAFT)

- Moved Epilogue's emotional closure from instant festival dialogue to an actual **playable memory walk**: Plaza, Café, Gallery, Riverside; old canon ending and all earlier letter/future callbacks still run at the lake.
- 29 original Epilogue scenes and 7 interactive steps, exclusive Arland/Sofia POV, 3 two-way choice moments and save-backed consequences; post-credit memory visits stay available.
- Added **The Other Side of the Page** playable mini-chapter, guarded by GlobalProgress for both C06-completed routes; new pixel-art *Ruang Dua Surat* (29th area), 5 editable icons, 2 original OGG Vorbis instrumental cues and 1 original WAV, all registered in the native runtime.
- Fixed return-portal bounce from the bonus room and made all 7 stages physically accessible from map spawns. Full two-route logic regression: **28,695 checks**, Epilogue **36 paths / 3,376 checks**, navigation **43**, asset references **186**. Earlier Chapter1–6, cutscenes, audio, tablet, touches, romance and living-world suites passed. All 1980 baseline files and 1616 legacy media preserved (CRC identical).
- Repeatable generation produces byte-identical JSON/Java with no duplicate scenes/steps. **No ZIP and no GitHub upload.** Prologue chapter audit and Android APK/device playtest still pending.
- Audit: `docs/STORY_EPILOGUE_OVERHAUL_V473_AUDIT.md`.

## Story Overhaul 3.0 — Chapter 6 v4.7.2 (PRIVATE DRAFT)

- Audit and playable Chapter 6 overhaul: 55 emotional scenes, 6 real sequential quests, the original editable Hall of Tomorrow map (28th area), three futures with route-specific decisions, four chapters of memory alignment, 12 branch-specific climax callbacks, six epilogue callbacks and one canon ending.
- Five editable pixel-art memory icons, two original OGG instrumentals and a WAV glint registered in the game runtime; Hall world FX/ambience/footsteps registered.
- Chapter 1–5 flags survive and trigger real Chapter 6 dialogue. Original C06 / Epilogue quest and save identifiers preserved. No original asset deleted, no GitHub updates or ZIP export.
- QA: 576 playable branch walkthroughs / 101,154 ActionRunner assertions, 52 collision-grid assertions, 203 asset checks; full headless source test 28,277 assertions, regression Chapter1–5 and tablet/audio/cutscenes pass. Physical Android gameplay and build APK are not yet verified.

## v4.7.1 — PRIVATE DRAFT, Chapter 5 / Across the Stars (23 November 2026)

- Completed the Chapter 5 interactive narrative pass: added Clockwork Station, Moonlight Lake and Memory Bridge as three independent 1920×1280 maps, making 27 world areas in total.
- Added 15 playable quest stages with independent Arland/Sofia time-and-memory paths, 5 constellation fragments, 4-stage memory alignment, choice-aware The Quiet reveal and earned bridge restoration.
- All new native minigames can be cancelled/retried without consuming progression; existing `C05_Q_ECHO` saves are routed safely into newly required content.
- Added new two-route dialogue and cross-chapter callbacks from C01, C02, C03 and C04, registered three original OGG cinematic scores, original WAV chime, five pixel-art Memory Book items, updated atmosphere/audio for new maps.
- QA: 108 complete C05 variants / 21,234 engine assertions, 139 portal/navigation checks, 1,036 art/story/audio checks, 27,674 full-story headless checks; all earlier chapter/finale tests passed. Entire legacy v4.6.6 source present and 1,616 old audio/image assets byte-identical. Repeatable generation idempotent.
- **NOT yet APK-tested**; Prologue, C06 and Epilogue still await separate full narrative audit. NO ZIP sent and GitHub untouched. See `docs/STORY_CHAPTER5_OVERHAUL_V471_AUDIT.md`.

## v4.7.0 — PRIVATE DRAFT, Chapter 4 / The Empty Seat & Rain Garden

- Implemented Chapter 4 full two-route conflict: 3 playable projector paths, 3 Sofia exhibition openings, unique follow-up scenes, five context lanterns, delayed reconciliation quests and cross-chapter callbacks.
- Added original pixel-art Rain Garden as 24th distinct world area, with 5 lantern positions, collision-safe portals, and a temporary escape doorway for players resuming older Chapter-4 saves inside Lantern Field.
- Added 5 original memory icons, 3 soundtrack cues and original paper SFX, registered and integrated in quest actions.
- Source tests: 324 branch runs, 69,947 assertions, 104 physical navigation/lock checks, 756 media references, and two-route full logic regression passing 26,943 assertions.
- Source regeneration is idempotent. Original v4.6.6 asset library and source are retained. Android-device and APK end-to-end testing is still pending.
- DO NOT distribute draft or push to GitHub before remaining chapter audits and user approval.

## Draft v4.6.8 — Chapter 2: A Little Date (23 November 2026)

- Full source retained; no ZIP delivered and no GitHub push.
- Three genuine Sofia schedule branches: accept now, postpone to the next calendar day, or decline then later independently reinvite after solo drawing at Galeri Komunitas.
- New Arland invitation POV, native bouquet minigame and real two-stage photobooth machine repair; native photo minigame, three pose choices, original phantom lantern cinematic and SFX.
- C01 choice-reactive gazebo dialogue, emotional pier reflections, route-guarded item exchange and gallery invitation foreshadow.
- 17 editable Memory Book entries, 3 new original pixel icons, 27.6s original emotional music and 1.1s original FX.
- 486 full route combinations / 78,314 Java assertions, 2,439 static story/media assertions, 27 map reachability checks, 26,060 full logic regression checks; repeatable JSON generation byte-identical.
- Android APK / phone/tablet GPU and actual playtime remain unverified. Documentation: `docs/STORY_CHAPTER2_OVERHAUL_V468_AUDIT.md`.

## 4.6.6 — Story Overhaul 3.2 · Letters of Tomorrow

- Mengembangkan 12 scene baru: dua surat personal Chapter 6, enam epilog berdasarkan pilihan, satu refleksi bersama, fallback old save, dan dua sesi galeri postgame.
- Mengaktifkan pilihan akhir Arland/Sofia yang terekam per route, kemudian diperlihatkan kembali di epilog, tetap menuju satu canon ending.
- Menambahkan kunjungan Galeri Komunitas pascakredit, tiga entri Memory Book dan tiga ikon pixel-art editable.
- Menghasilkan cue orisinal `cinema_letter_tomorrow.ogg` (28.8 detik); registrasi audio engine diperbaiki.
- Tes khusus: percabangan route, anti-repeat, epilog fallback, save roundtrip, referensi aset, dan idempotensi patch.
- Mempertahankan sistem save dan keseluruhan cerita v4.6.5; tidak ada perubahan di GitHub.
- Build APK Android/tes perangkat nyata belum diverifikasi.

## 4.6.5 — Story Overhaul 3.1: Complete Emotional Arc (23 November 2026)

- Major conflict **The Empty Seat** integrated into 23-map offline game, with replayable route-specific perspectives and original gallery map/music/icons.
- Added playable after-rain reflection for both routes, a second conversation with three choices, and two required cooperation actions in C05.
- Decisions are persisted to flags and pay off in C06/Epilogue; older saves without flags receive a safe narrative fallback; one canon ending.
- Expanded to 445 scenes, 103 quest steps, 136 memory entries; 22 original maps stay untouched, 23 areas total.
- Original 793 Android audio/image assets SHA-identical to v4.6.3; core save, route and game engine Java files unchanged.
- Fixed automated generation order and outdated 22-map/40-music assumptions in active QA.
- Verified 25,304 full logic assertions plus 457 story branches, 493 completion, 11 reachability and 5,885 story/asset reference checks.
- **APK compile and physical Android playtests remain unverified.** See docs/V465_STORY_OVERHAUL_COMPLETE.md.

## 4.6.3 — Cinematic Cutscene 2.0 & Premium UI/UX 2.0 (23 November 2026)

- Renderer cutscene: camera shot berbasis posisi aktor/pasangan, zoom preset yang konsisten, tween smoothstep, fade easing, batas durasi/speed/FX serta pemulihan kamera yang lebih stabil pada variasi FPS.
- Lima command pada scene yang sudah ada dipoles tanpa menambah/mengubah dialog atau canon ending. Patch data bersifat idempotent dan dipanggil kembali oleh pipeline generator.
- Dialog/UI: pilihan adaptif layar HP/tablet, keyboard/d-pad, multi-pointer input guard, tombol lebih mudah dibaca, transisi menu ringan, perbaikan overlap keterangan save di TitleScreen.
- 7 runtime camera checks, 859 layout/motion checks, 51 romance, 390 tablet, 750 touch, 395 story, 131 navigation, 93 cinematic/audio, 38 save migration.
- Semua original graphics/audio/map/save dipertahankan; APK perangkat belum diuji.

## 4.6.2 — Character Animation Overhaul & World Graphics 4.0 (23 November 2026)

- Empat atlas 8-facing baru untuk Arland dan Sofia: walk 16×8, idle 8×8. Arah diagonal disintesis secara pixel-preserving dari sumber 4 arah, fallback tetap aman.
- Character Actor: facing8 tanpa mengubah schema save lama; motion blending berbasis delta time; gestur `shy`, `excited`, `ponder` dan reaksi companion yang dibatasi.
- World Graphics: 22 kategori area dikaitkan dengan 6 mood visual dan efek cuaca/waktu; fog, sunbeam, blossom, foliage, fireflies, water glints, dan rain droplets via tujuh PNG baru yang bisa diedit.
- Renderer hanya menambah pass visual, tidak mengganti map PNG/collision/quest/save; Low preset mematikan efek tambahan.
- Tambah generator `tools/gen_visual_v462.py`, Java headless tests, audit aset, panduan edit, dan perbandingan source asli.
- Belum mengklaim build APK, animasi GPU 60 FPS pada device, atau sprite diagonal hand-drawn.

## 4.6.1 — Save, Living World, UI & Packaging Stability (23 November 2026)

- Jam romance tidak dapat mundur ketika pemain memuat ulang save utama yang lebih lama; tidak bisa mengulang hadiah kencan/dialog di hari yang sama.
- Jadwal waypoint NPC divariasikan berdasarkan penghitung keputusan lokal dengan pemilihan deterministik dan collision checking, tanpa teleportasi melewati objek.
- Gerakan swipe di layar Romance Simulation membedakan pointer multitouch dan membatalkan gesture pada touch-cancel.
- Penghapusan/penimpaan slot romance menangani kegagalan storage dengan pemberitahuan yang jelas, bukan crash tanpa pesan.
- Manifest hash data/props.json diperbaiki berdasarkan verifikasi byte-identik dengan source asli v4.4; aset world tidak diubah.
- JDK 11 syntax/type checks, 51 romance assertions, 12 NPC assertions, 390 tablet checks, 38 save migrations, 2.197 world checks, 956 audio checks, dan 24.686 full logic checks pada salinan QA.
- ZIP source penuh dibangun ulang dan diuji CRC/integritas; APK Android nyata belum diuji.

## 4.6.0 — Living World 3.0 + Romance Integration (23 November 2026)

- Menggabungkan semua source, map, visual, audio, dan cerita v4.4 dengan modul romance v4.5.
- Perbaikan NPC saat bergerak, pemilihan waypoint, cuaca, dan jam dunia.
- Menu Romance Simulation 3.0 mengacu pada route/slot game, tanpa merusak save lama.
- Pengujian engine NPC, romance, dan layout tablet; build APK belum terverifikasi.

## 4.4.0 — Romantic Environment & Tablet UI Polish (23 November 2026)

- Art pass deterministik pada Dermaga, Bukit Bintang, Memory Garden, dan Eternal Garden: material, lingkaran observasi/kenangan, riak air, kelopak, dan pencahayaan. Empat latar runtime baru dan 16 layer transparan editable.
- Dua puluh lima varian sprite prop memanfaatkan footprint dan alpha lama; total 147 penempatan diperbarui tanpa memindahkan collision, portal, spawn, atau objek quest.
- Layout menu utama 3×2 pada layar lebar dan 2×3 pada tablet; grid slot 3×2 pada ponsel landscape dan 2×3 pada tablet; panel Pengaturan menghormati safe inset.
- Tes geometri tablet v4.4, audit gambar/collision/audio, dan generator metadata-only ditambahkan pada pipeline.
- Source lengkap; belum diklaim APK yang teruji karena distribusi Gradle/Android SDK tidak tersedia atau tidak dapat diunduh di lingkungan ini.

## v4.3.0 — Tablet Android & Four-Area World Art Pass

- Panorama layar utama dan route select tidak lagi stretch pada tablet 16:10 / 4:3.
- Route card, pause menu, joystick, dan tombol sentuh memakai metrik safe-screen responsif.
- Aktivitas multitasking tablet diizinkan (resizeable activity, landscape preferred).
- Empat latar map dan 20 jenis prop diperbarui; 59 anchor prop dipertahankan.
- Baseline editable 4 area + 16 layer visual dan generator baru.
- Test layout lintas enam profil screen; status Android GPU build masih belum teruji.

# Update v4.2.0 — Artistic World Pass & Landmark Cleanup (23 November 2026)

- 13 map v4.1 memperoleh 3 layer ilustrasi editable per area (39 RGBA), terkomposit ke background runtime.
- 33 landmark sprites `v41_*.png` diperbaiki transparansi matte putihnya; footprint collision dan ID tetap.
- 9 map handcrafted v4.0, 86 aset audio, semua quest, save schema 8, dan portal dipertahankan.
- Generator dibuat deterministik dan menulis file atomik; pipeline build/test terbaru menjalankan audit v4.2.
- Fokus: konsistensi ilustrasi dan artefak; belum full manual redraw 13 area, belum build APK terverifikasi.
- Panduan: `docs/WORLD_ART_PASS_V4.2.md`, audit `docs/V42_ASSET_DIFF.json`.

## 4.1.0 — Remaining 13 Map Art Pass (23 November 2026)

- Update background runtime 13 area di luar 9 map v4.0. Tambahkan layer suasana bertema masing-masing area dan atlas landmark pixel-art source yang dapat diedit.
- Ganti 81 penempatan prop menggunakan 33 tipe sprite baru tanpa mengubah x/y, `cw/ch`, sort layer, world dimensions, spawn, collision, doors, atau quest triggers.
- Pertahankan kesembilan map handcrafted v4.0 dan 86 audio identik. Simpan baseline PNG / metadata v4.0 untuk regenerasi.
- Tambahkan pratinjau komposit 13 map dan perbandingan 6 area, tes geometry+assets+audio 5247 pemeriksaan, dan koordinat detail per map.
- Source telah diuji secara headless; APK Android, Y-sort nyata, dan performa perangkat belum diverifikasi.

## 4.0.0 — Nine Handcrafted Map Upgrade (23 November 2026)

- Install real supplied artwork in 9 maps. Images are matched by visual content, since uploaded filenames did not correspond to their subjects; comparison-collage image omitted.
- 1200×896 world bounds for nine scenes and Nearest texture filtering.
- Replace old collision geometry with custom wall/alcove masks and furniture hitboxes; preserve portal IDs and quest IDs while updating all arrival coordinates, step interactions, NPC schedules and world event markers.
- Add alpha-cut foreground props for Y-sorting without double drawing old baked furniture; save schema 8 converts v3.x local coordinates.
- Add 9-map image + collision previews, full coordinate inventory, 302 integrity checks, spawn-rooted navigation BFS, and 38 save migration checks.
- Retain 13 other map images, all 86 audio items, visual generator assets, story, and old map baselines.
- APK compiling and physical Android playtesting remain unresolved; not a public release claim.

# v3.7.0 — Character Motion & Visual Depth

- Tambah 50 atlas sprite (`walk_v37.png`, `idle_v37.png`) untuk 25 karakter, dengan animasi 16/8 fase per arah dan fallback aset lama.
- Perbaiki bug idle head double-draw dan sampling cadence untuk walk/sprint.
- Bayangan kontak dinamis untuk prop dan karakter; tidak memengaruhi collision atau save.
- Pindahkan efek air ke layer lantai agar tidak menutupi aktor.
- Audit dan tes: cek atlas, test renderer headless, regresi kedua route/22 peta/86 audio, cleanup aman.
- **Batasan:** belum build APK sungguhan maupun verifikasi FPS/GL. Atlas baru merupakan turunan pixel-level dari aset existing, belum redraw manual.

---

# v3.6.0 — Final Nine-Map Art Pass + Safe Source Cleanup

- 9 runtime map backgrounds dipoles secara khusus: jalan_kota, perumahan, perpustakaan, arcade, toko_bunga, arland_room, sofia_room, dapur, ruang_arsip. Semua 22 area kini telah mendapat art pass tersendiri (tahap 1–4).
- 57 prop runtime diberi detail baru tanpa perubahan ukuran/alpha silhouette. 36 layer editor dan 66 baseline gambar persis v3.5 untuk regenerasi deterministik.
- Aset lama, cerita, save schema 7, collision, dan 86 audio dipertahankan.
- Pembersihan yang dibatasi ke dokumen/pratinjau usang tanpa referensi dan cache Python (9 file / 5.293.387 byte). Laporan: `docs/CLEANUP_AUDIT_V3.6.json`.
- Tool baru: `world_redesign_stage4.py`, `test_world_redesign_stage4.py`, `preview_world_stage4.py`, `clean_project_v36.py` (dry-run default). QA tahap 1–3 direvisi agar tetap memverifikasi aset masing-masing, sambil mengizinkan perubahan yang tercatat dari tahap 4.
- Integrasi build_all dan GitHub Actions, metadata runtime dan Gradle menjadi 3.6.0.
- **Build APK / QA Android sebenarnya belum terbukti berhasil.**

---

# v3.5.0 — World Redesign Tahap 3: Fantasy Village, Stars, Crystal & Forest

- **Lanjutan sumber v3.4**, bukan peta baru atau pengganti engine. Lima PNG runtime diperbarui: `starfall_village`, `star_path`, `gua_kristal`, `lantern_field`, `hutan_bisik`.
- Arah seni dibedakan per area: mosaik desa berbintang, konstelasi Star Path, urat mineral dan kolam Gua Kristal, ukiran festival lentera, serta dedaunan/penanda jalur Hutan Bisik.
- **36 tipe prop aktif** mengalami detailing warna/jendela/atap, kristal, lentera, dedaunan, atau elemen hutan. Siluet alpha dan ukuran setiap prop tetap sama, sehingga tidak mengubah footprint collision atau depth.
- **25 layer RGBA editable**, baseline PNG v3.4 (5 peta + 36 prop), generator deterministik, preview komposit sebelum–sesudah, dan manifest SHA-256 per aset. Ini peningkatan gambar/prosedural, bukan penggambaran manual ulang gaya Sea of Stars.
- Stage 1 (3 map) dan Stage 2 (5 map) tetap identik dengan v3.4. Cakupan map yang telah mendapatkan art pass khusus dari v3.3–v3.5 menjadi **13 dari 22**; **9 map tersisa** untuk tahap berikutnya.
- File data peta/quest/cerita/save serta **86 audio runtime** tidak berubah. `tools/build_all.sh`, tes CI, metadata 3.5.0 / versionCode 35 diperbarui. Status: **source headless**, APK/performa HP belum terverifikasi.

---

# v3.4.0 — World Redesign Tahap 2 / Romantic & Fantasy Environment

- Memodifikasi 5 PNG map runtime (Riverside, Dermaga, Bukit Bintang, Memory Garden, Eternal Garden), terintegrasi memakai path yang sama dengan data map; tidak membuat area dummy.
- Memodifikasi 30 prop aktif pada kelima area (jembatan, perahu, fasilitas dermaga, observatorium, teleskop, pohon dan gerbang fantasi) dengan alpha dan resolusi semula.
- Menambah 20 RGBA editable layer + baseline 5 map/30 prop dari v3.3, generator dan preview before-after berbasis aset runtime.
- Menambah pengujian hash v3.3 yang melindungi 656 file aset dan 86 audio, serta validasi visual, collision, cerita dan kontrol. Tahap 1 (3 peta) tetap utuh.
- Menaikkan metadata game ke v3.4.0 / versionCode 34 dan memperbarui workflow build.
- **Status: source diuji headless, APK Android asli/FPS/OpenGL dan kualitas artistik komersial belum terverifikasi.**

---

# v3.3.0 — World Redesign Tahap 1

- 3 peta benchmark (Plaza Kota, Taman Kota, Kafe Senja) mendapat palet material, detail visual dan pola dekorasi baru pada PNG runtime.
- 29 prop digunakan pada area benchmark dipoles (termasuk bangunan kafe, air mancur, gazebo, jembatan, flora, dan interior); alpha/ukuran asli dipertahankan.
- 4 layer PNG editable per map (12 master), 3 backup map serta 29 backup prop v3.2, generator deterministik dan preview komposit source sebelum/sesudah.
- Tidak ada cerita, quest, collision, save, atau audio yang diubah. 19 map sisanya masih v3.2 untuk tahap berikutnya.
- Menambahkan uji khusus berbasis hash terhadap manifest v3.2 dan melindungi mural prop dari efek samping pengujian generator konten.
- Metadata Android 3.3.0 / versionCode 33; workflow mengeksekusi uji baru. APK tetap belum dapat diverifikasi di lingkungan tanpa SDK/Gradle.

---

## v3.2.0 — Ultimate Visual Overhaul (source, belum APK)

- **22 peta** memiliki penyegaran tekstur/cahaya bertema berbeda, disertai dekorasi floor pixel art tambahan tanpa mengubah ukuran peta, collision, door, atau titik quest.
- **256 prop** dipoles di dalam PNG asli; ukuran serta siluet alpha dipertahankan. Baseline asli disimpan di `art_source/visual_v32_base/`.
- **25 karakter** memiliki atlas berjalan 12 frame × 4 arah dan idle 6 frame × 4 arah. Atlas sebelumnya tidak dihapus dan dipakai sebagai fallback.
- **21 portrait ekspresi** diberi finishing, ditambah skin UI ninepatch 64×64, 2 panorama menu baru, ribbon/bloom/ornamen dialog dan 12 stills cutscene dari area canon.
- Renderer benar-benar memakai atlas, UI, menu dan stills baru. 86 audio tetap utuh; save schema 7 tidak berubah.
- Generator, audit statis aset dan dokumentasi editing disertakan. **APK Android tetap belum dikompilasi/diuji pada HP**; belum layak disebut rilis final.

## v3.0.0 — 23 November 2026 — Expanded Systems & Release Candidate SOURCE

- Tambah **riwayat dialog per slot** 72 baris, UI baca ulang, tombol H, dan paginasi. Simpan di schema 7, migrasi schema1–6.
- Tambah **Kompas Misi** marker utama lokal, dan tab **Jelajah** untuk 22 area yang pernah dikunjungi.
- Tambah autosave aman tiap 90 detik gameplay bebas; tidak menyimpan state setengah cutscene.
- SaveStore tidak menimpa save versi lebih baru, tidak memutar file utama semantik rusak menjadi backup, dan menolak penulisan progres tanpa step.
- Audit hash 583 aset v2.9 tetap identik; 86 aset audio tetap dalam ZIP utama; 12 achievement dan semua sistem lama tetap ada.
- Workflow debug / signed AAB diperbarui, plus native 16KB ELF check (butuh APK nyata untuk lolos).
- 25.024 tes gameplay logic, 63 tes save+history, 6 tes UI overlay, 1.374 pemeriksaan audit statis lulus; **tidak ada APK hasil build karena Gradle tidak dapat diunduh di lingkungan ini**.
- **Bukan rilis publik.** QA perangkat, signed AAB dan store compliance masih blocker.

## v2.9.0 — 23 November 2026 — Release Readiness, QA & Achievements

- 12 achievements offline di tab **Prestasi** Memory Book dengan penyimpanan lintas route/slot (GlobalProgress schema 2 dan migrasi schema 1).
- Safe-save: CRC32 tetap kompatibel, cadangan `.bak` + `.bak2`, `.tmp` recovery, validasi semantik route/slot/schema, proteksi save versi lebih baru, deteksi baca gagal, dan gagal backup/rename tidak merusak save lama.
- Tombol Simpan sekarang tidak memberi toast sukses saat gagal; mulai New Game berhenti bila save pertama gagal; global progress hanya di-update setelah save slot sukses.
- Menu Pause > Cara bermain dan teks panduan pada penyelamatan data.
- Warm prop hanya untuk area aktif, bukan preload semua prop 22 area saat boot; performa nyata belum diukur.
- Upgrade baseline Android API 36, AGP 8.10.0, Gradle 8.11.1, libGDX 1.14.2. **Belum lolos build Android asli.**
- Added external signing configuration (no secrets embedded), signed AAB workflow candidate, asset SHA256 manifest, static release QA, 39 targeted resilience assertions.
- Seluruh asset sprite/peta/audio v2.8 dipertahankan. Tidak mengubah alur cerita atau save schema 6.

# CHANGELOG — Arland & Sofia: Our Little Universe

## v2.8.0 — Android Controls, Landscape UI & Rendering Optimization (2026-11-23)

- **Lanjutan langsung v2.7 (bukan rewrite)**: 22 peta, 398 scene, 1.991 dialog, kedua route, 14 world events, canon ending, dan 86 aset audio dipertahankan.
- Pengaturan dibagi menjadi 3 tab Audio/Tampilan/Kontrol; tambah 3 setting tersimpan: tangan kanan/kidal, joystick melayang/tetap, sensitivitas joystick 70–150%. `settings.json` menjadi schema 3 tetapi membaca schema 1/2. **Save progres tetap schema 6**.
- Model `TouchInputModel` pure Java menerima multi-pointer eksklusif (gerak, aksi, lari bersamaan), safe inset landscape, deadzone dan sensitivitas. Sprite UI lama dipakai tanpa duplikasi file audio/gambar.
- `GameScreen`: preculling prop floor, NPC, hewan, sprite quest dan cutscene; cache dimensi normal/alternatif prop per area; reuse daftar marker render. Perbaikan `pause()/resume()` untuk menghentikan dan mengembalikan audio background.
- Tes `tools/test_controls_v28.sh`: input multi-pointer, layout landscape dan kontrol kidal + menu tiga tab; suite regresi logika, audio, visual, dan world events dipertahankan dalam workflow GitHub Actions. Dokumentasi `docs/ANDROID_CONTROLS_V2.8.md`.
- **Batasan**: Java syntax dan tes headless lulus tetapi kompilasi Android asli tetap terhalang DNS `services.gradle.org`, Android SDK lokal belum tersedia. Efisiensi FPS, mixing audio, dan perilaku HP belum diverifikasi secara runtime.

## v2.7.0 — Living World & Daily Events (2026-11-23)

- Source dilanjutkan dari v2.6, **bukan rewrite**. Semua 22 peta, 25 NPC, 60 hewan, 25 side quest katalog, kedua POV, satu canon ending, 8 couple actions, 6 romance minigames, 86 file audio lama, aset visual dan UI dipertahankan.
- **14 event dunia** (12 shared, satu Arland-only dan satu Sofia-only), **26 scene route-authored**, **156 baris dialog**, **14 penanda interaksi**, **14 Memory Book entries**. Kegiatan pagi, sore, malam dan hujan terbuka berdasar konteks, bukan hanya selalu muncul setelah cerita selesai.
- Engine event data-driven: `QuestDb.WorldEvent`, `QuestEngine.worldEventBlock/completeWorldEvent`, kondisi `worldEventReady`, perintah ActionRunner `worldEvent`; integrasi langsung ke side interactables, prompt dan HUD pada GameScreen. Tidak ada duplikasi engine quest atau menu baru yang memutus input lama.
- NPC idle berbasis waktu/cuaca menggunakan atlas pose bawaan. `Progress.SCHEMA=6` dengan `worldEventDays/worldEventCounts`, migrasi otomatis schema 1–5, hari baru dapat mengulang event tanpa menggandakan kenangan dan tanpa reward berulang hari yang sama.
- Generator dan dialog editable di `tools/content/world_events_v27.py` serta `tools/content/naskah_world_v27.txt`; docs `docs/LIVING_WORLD_EVENTS_V2.7.md` dan tes `tools/test_world_events_v27.py` ditambahkan ke GitHub Actions.
- Total output: **398 scene, 1.991 baris dialog, 93 step, 149 side interaction, 129 Memory Book entries, 86 file audio**.
- `bash tools/test_logic.sh`: **25.024 pemeriksaan lulus**, `tools/test_world_events_v27.py`: **315 pemeriksaan lulus**, tes aset/regresi v2.1–2.6 lulus. Syntax parse Java 11 (48 file) lulus; **bukan kompilasi Android**.
- Percobaan `./gradlew :android:assembleDebug --offline` **gagal sebelum kompilasi** karena DNS `services.gradle.org`; APK/FPS/audio runtime pada Android belum teruji. Output satu ZIP **source** final, bukan APK.

## v2.6.0 — Dual-Route Story Expansion (2026-11-23)

- **Berasal langsung dari v2.5.0**, bukan rewrite: mempertahankan dua POV, 22 map, canon ending, 25 NPC, 60 hewan, 86 file musik/ambience/SFX, enam romance game, interaksi berdua dan save schema 5.
- **41 adegan baru / 226 baris dialog baru**, **9 langkah main quest** menyentuh Chapter 3, 4, dan 5: bekal setelah memasak, komitmen pascahujan, penyelidikan di Starfall Village dengan urutan/puzzle berbeda untuk Arland dan Sofia. Kedua jalur kembali bergabung sebelum The Quiet.
- **Empat side quest baru** (Arland-only `SQ_V26_MAP_A`, Sofia-only `SQ_V26_CARDS_S`, shared `SQ_V26_LISTEN`, shared `SQ_V26_LAMPS`): 20 interaksi, empat hadiah baru dan empat Memory Book entries. Total 25 side quest dalam katalog; masing-masing route dapat menyelesaikan 22.
- Dua puzzle (`v26_night_compass` code-lock dan `v26_night_pages` page sort) diregistrasikan di `Games.create`; musik cutscene menggunakan trek **yang sudah ada** (`cinema_reconciliation`, `star_road`) sehingga seluruh audio tetap satu ZIP lengkap.
- **Regresi:** `bash tools/test_logic.sh` lulus 24.095 pemeriksaan untuk kedua route, termasuk flag scene/puzzle baru, side quest, migrasi save, ekonomi dan romansa. Validasi tambahan `tools/test_story_v26.py` lulus; asset tests versi terdahulu tetap diperlukan.
- Metadata: appVersionName `2.6.0`, versionCode `26`, workflow GitHub Actions artifact `ArlandSofia-v2.6-debug-apk` dan uji konten v2.6. Dokumentasi `docs/STORY_EXPANSION_V2.6.md`.
- **Batasan:** estimasi simulator sekitar 3j39m–3j41m / route (bukan uji waktu permainan nyata); target enam jam/route belum tercapai. Build dan FPS pada Android belum diverifikasi hingga Gradle dan dependensi dapat diperoleh.


## v2.5.0 — Cinematic Romance & Immersive Gameplay (2026-11-23)

- Dari source v2.4, seluruh progres canon, dua route, peta, collision, karakter, UI lama, toko, save schema 5, dan 75 audio sebelumnya tetap dipertahankan.
- Tab kelima **Main Bareng** dengan enam permainan berdua (empat mekanik minigame yang sudah ada dan dua baru: `bouquet`/`scrapbook`), 12 adegan berbeda antar route, score/best harian tersimpan, enam kenangan di Memory Book, anti-farming bonus tanpa menghalangi replay.
- Tujuh komposisi sinematik original di `audio/music/cinema_*.ogg`, empat SFX baru serta enam potret ekspresi (`jatuh_cinta`, `khawatir`, `lega` untuk Arland/Sofia). Total audio sekarang **40 musik + 14 ambience + 32 SFX = 86** dalam satu source ZIP.
- Perintah musik baru pada cutscene utama/credits melalui engine soundtrack v2.4. `tools/build_all.sh`, `tools/test_cinema_v25.py`, test UI/audio, dan workflow GitHub Actions diperbarui. **331 scene, 1.609 dialog, 106 entri Memory Book**.
- Metadata `appVersionName=2.5.0`, `versionCode=25`, `OluGame.VERSION=2.5.0`, artifact `ArlandSofia-v2.5-debug-apk`.
- Simulasi headless dan verifikasi konten bukan uji FPS/codec nyata pada Android; kompilasi Gradle asli masih memerlukan verifikasi pada lingkungan yang bisa mengunduh Gradle/dependensi.


## v2.4.0 — Music & Soundscape Expansion (2026-11-22)

**Lanjutan dari ZIP source v2.3.0; bukan rewrite.** Semua 22 map, dua route, 319 scene, 21 side quest, sistem pasangan, visual v2.3, dan save schema 5 tetap dipertahankan.

- **64 audio baru:** 25 original procedural BGM OGG (menu + tema area/waktu/cuaca), 14 ambience loop OGG, 25 efek WAV. Delapan BGM dan tiga SFX lama tetap ada sehingga total **75 aset audio lokal**. Generator deterministik `tools/gen_soundscape_v24.py`; manifest metadata `android/assets/audio/soundscape_v24.json`.
- **Soundtrack kontekstual:** `logic/SoundscapePlan.java` memilih track untuk 22 area, siang/malam, hujan, dan override musik quest. Mode musik klasik mempertahankan perilaku v2.3. Peta/story/gameplay tidak diganti.
- **Engine audio:** `AudioManager` memakai dua bus streaming BGM dan ambience dengan crossfade, ducking dialog, pause/resume Android, cache SFX lazy, cleanup stream, kontrol volume musik/ambience/efek. `SettingsPanel` kini 11 baris termasuk toggle musik beragam dan langkah; migrasi **schema settings 1 ke 2** aman, **schema save progres tetap 5**.
- **Trigger audio:** langkah terukur, pintu, elus hewan, pembelian/koin, interaksi pasangan, inspect, klik menu, quest selesai, efek Festival Lentera/The Quiet. Aset yang belum ditautkan ke event tetap tersedia sebagai library untuk update berikutnya.
- **Test:** `test_audio_v24.py` verifikasi 75 file (codec/durasi/hash), `test_soundscape_plan.sh` lintas map/cuaca/waktu/override, `test_audio_manager.sh` headless crossfade/ducking/pause/cleanup, `test_settings_ui_v24.sh` layout/tombol, ditambah seluruh regression test sebelumnya. Dokumen `docs/AUDIO_SOUNDTRACK_V2.4.md`.
- **Belum dibuktikan:** build APK asli, kualitas mixing dan FPS/audio perangkat Android. Tidak ada klaim APK instalasi teruji dalam ZIP ini.

---

## v2.3.0 — Living World, Pixel-Art Environment & NPC Activity (2026-11-22)

**Ruang lingkup:** upgrade visual atas ZIP source v2.2.0, bukan rewrite; 319 scene canon, 22 map, 21 side quest, 25 NPC, 60 hewan, 8 couple action dan save schema 5 **tidak dihapus**.

- `tools/polish_world_v23.py`: **8.471 microdetail pixel art** ditambahkan ke **22 gambar `maps/*.png`**, berdasarkan gaya tiap area. PNG diberi marker idempotensi; generator `build_all.sh` menjalankannya **sesudah** generator map utama. Pintu, anchors, collision, metadata maps, dan dimensi tidak diubah.
- `GameScreen`: kanopi pohon lembut bergoyang ketika mode Sinematik, cache split `TextureRegion` untuk menghindari alokasi frame; filter prop offscreen sebelum depth-sorting.
- `WorldFx.drawSceneAtmosphere`: variasi percikan cahaya, motes, dan kilau pada cave/library/realm/garden, menyesuaikan tiga preset. Menggunakan tekstur yang sudah ada, tanpa asset pihak ketiga atau API internet.
- `tools/gen_poses.py` + `Assets.POSES` + `Actor`: 3 aktivitas NPC baru `read`, `water`, `sweep` dengan dua frame per arah pada **25 sheet poses.png** yang kini berukuran 384×1152 (16 baris). Dialog dan pose berdua sebelumnya tidak diubah. NPC idle menggunakan aktivitas berdasarkan peran.
- `docs/preview/v23_world_asset_preview.png`: pratinjau komposit 6 area dari PNG aktual peta + props, **bukan screenshot APK**. `tools/preview_world_v23.py` dapat membuat ulang.
- **Verifikasi:** `bash tools/test_logic.sh` lulus **23.201 pemeriksaan**, 22 peta teruji beda dari v2.2, `tools/test_world_v23.py` lulus **463 cek** (atau **485** dengan opsi pembanding ZIP v2.2), `tools/test_couple_v22.py` lulus 528 cek, test visual v2.1 dan smoke visual FX lulus, input romansa lulus; parser Java 11 lulus 47 file.
- **Belum dibuktikan:** build APK asli dan pengujian sentuh/FPS GPU/Android. Wrapper `./gradlew --offline :android:assembleDebug` gagal sebelum source compile karena `UnknownHostException: services.gradle.org`. Jangan menganggap v2.3 ini APK siap pakai sebelum pipeline/perangkat menjalankannya.
- **Durasi:** main story sekitar 82–83 menit/route; lengkap sekitar 189–191 menit/route di estimator (bukan playtest). **6 jam per route belum tercapai.**

---

## v2.2.0 — Living Romance & Synchronized Characters (2026-11-22)

**Upgrade langsung atas ZIP source v2.1.0; tidak menghapus peta, quest, cerita canon atau aset lama.**

- **Gameplay pasangan:** tab baru `Aksi Berdua` di `RomanceOverlay` dengan 8 aksi kontekstual, lengkap dengan syarat lokasi, waktu, cuaca dan affection, serta 16 scene khusus route Arland/Sofia dari `tools/content/naskah_couple_v22.txt`. Semua dipanggil lewat `QuestEngine.coupleActionActions` dan cutscene `pair` sinkron.
- **Gerak bersama:** mode gandengan saat eksplorasi dengan orientasi sprite dan perpindahan companion paralel, cek collision, kontrol sprint, dan fallback saat koridor sempit. Hug, lean, selfie, highfive, dance, serta momen senja/bintang memakai pose serempak dan framing kamera cutscene. Ini animasi 2D data-driven di scene, bukan simulasi fisika/IK penuh.
- **Aset karakter:** generator `tools/gen_poses.py` menambah `hug`, `lean`, `photo`, `highfive`, `dance` ke delapan pose lama; 25 sheet `poses.png` menjadi 384×936 (13 row × 72 px). Dua frame berbeda per pose/arah; sheet `walk.png` dan `walk_plus.png` tidak dimodifikasi. Pose sprite baru merupakan turunan/prosedural, bukan gambar tangan lengkap dari artis.
- **Dunia hidup:** idle activity sederhana pada NPC terpilih, reaksi bob saat hewan dielus, tanpa mengubah jadwal atau quest. **Perbaikan data v2.0:** memori `m_rain_a` ganda dipisahkan menjadi `m_rain_sketch_a` supaya hadiah side quest tidak tertimpa oleh kenangan cerita utama.
- **Save schema 5:** histori per aksi/slot/route, mode gandengan tersimpan. Migrasi schema 1–4 mempertahankan progres lama, ekonomi, romansa, dan snapshot. Bonus masing-masing aksi dibatasi satu kali per hari; gandengan boleh on/off berkali-kali tanpa farming.
- **Jumlah konten:** 319 scene, 1.573 dialog, 84 step utama, 115 side interaction, 25 NPC, 71 item, 21 side quest katalog (19 per route), 100 kenangan.
- **Tes nyata sesi ini:** `bash tools/test_logic.sh` **23.201 pemeriksaan lulus**, kedua route hingga epilog + 19 side quest per route + delapan aksi / route + save migration; `bash tools/test_romance_ui.sh` **lulus** delapan callback termasuk toggle dan halaman 2; `python3 tools/test_couple_v22.py` **528 checks**, `python3 tools/test_visual_v21.py` 112 checks, `bash tools/test_visual_fx.sh` lulus parse Java dan WorldFx stub; layout OK.
- **Belum dibuktikan:** build APK Android asli, touch/performa/render OpenGL. Percobaan `./gradlew --offline :android:assembleDebug` gagal **sebelum kompilasi** karena `UnknownHostException: services.gradle.org` saat mengambil Gradle 8.11.1. Source ini kandidat pengembangan, belum APK rilis.

---

## v2.1.0 — Ultimate Pixel Art, Character Animation & UI (2026-11-22)

**Jenis upgrade:** visual dan sinematik atas source v2.0.0, **bukan rewrite**. Semua data, 22 area, kedua route, ending canon, interaksi ekonomi/romansa, dan schema save 4 dipertahankan.

- **Panorama baru**: dua ilustrasi procedural `v21_skyline.png` + `v21_foreground.png`, paralaks ringan di menu utama dan route select dengan banner asli tetap digunakan. Ada komposit pratinjau `docs/preview/v21_menu_asset_preview.png`, **bukan hasil screenshot runtime**.
- **Animasi karakter**: 25 sheet `walk_plus.png` dengan 8 fase/4 arah, dihasilkan dari sheet `walk.png` 3 frame lama yang tetap utuh; engine membaca sheet baru dengan fallback otomatis. Fase tambahan merupakan turunan sprite lama (belum animasi artis manual 8 pose independen).
- **UI**: 6 skin nine-patch baru di seluruh aplikasi; dialog dengan panel portrait, animasi masuk, indikator progres teks dan pilihan jawaban; cutscene dengan ribbon/caption/letterbox beraksen. FX tambahan pada Plaza, Memory Garden, Perpustakaan, surat Sofia, The Quiet, Festival Lentera.
- **Generator / testing**: `tools/gen_visual_v21.py` (build otomatis), `tools/test_visual_v21.py`. Hasil **112 verifikasi aset lulus**, **22.803 pemeriksaan logika lulus**, parse-only 47 file Java dan smoke WorldFx + RomanceOverlay lulus.
- **Konten tidak ditambah**: 303 adegan, 1.493 baris dialog, 84 step, 115 side interaction, 21 side quest unik (19 relevan per route), 25 NPC, 71 item, 92 Memory Book. 6 jam per route masih belum dicapai (±3,1 jam/route termasuk aktivitas simulasi).
- **Versi**: `appVersionName=2.1.0`, `versionCode=21`, `OluGame.VERSION=2.1.0`, GitHub Actions `ArlandSofia-v2.1-debug-apk`. Save schema tetap 4.
- **Batas verifikasi**: `./gradlew --offline :android:assembleDebug` gagal **sebelum mengompilasi source**, karena distribusi Gradle 8.11.1 masih perlu diunduh dari `services.gradle.org`. Tidak ada klaim APK sudah berjalan atau visual/FPS sudah diverifikasi di HP Android.

---

## v2.0.0 — Cinematic Atmosphere, Smooth Camera & Performance (2026-11-22)

**Ruang lingkup:** lanjutan langsung v1.9.0. Source native Java/LibGDX, 22 peta, cerita canon, ekonomi, hubungan, dan schema save 4 tetap dipertahankan.

- **Kamera**: helper `CameraRig` pure-Java dengan smoothing eksponensial framerate-independent, snap saat ganti area atau cutscene camera aktif, dan look-ahead kecil saat pemain berjalan. Opsi kamera halus disimpan di pengaturan.
- **Pengaturan visual 3 mode**: `Hemat` / `Seimbang` / `Sinematik` mengendalikan jumlah hujan, kelopak, partikel, kilau air, glow, dan vignette; `Settings` default kompatibel dengan file pengaturan lama.
- **Efek runtime**: kelas `WorldFx` dengan fixed pool 48 partikel untuk jejak kaki/debu, cipratan ketika hujan, dan hati lembut di dekat companion saat affection tinggi; visual foreground kelopak, riak air, vignette transparan. Aset PNG orisinal dihasilkan oleh `tools/gen_visual_fx.py` dan dimuat lokal tanpa internet.
- **Optimasi**: depth sort memakai pool `DrawItem` reusable; prop di luar batas viewport tidak dirender. Menu route tidak membuat objek `Color` baru setiap frame, menu dan dialog mengikuti preset kualitas.
- **Cerita route**: 6 scene opsional baru (3 Arland C04 dan 3 Sofia C05), 6 interaksi baru, 2 item, 2 Memory Book entry. Dua side quest baru; jurnal dan simulasi menyaring side quest berdasarkan route sehingga 19 dari 21 quest relevan per route.
- **Data**: **303 scene, 1.493 dialog, 84 step, 115 side interaction, 25 NPC, 71 item, 92 entri Memory Book, 21 side quest total**. `versionCode=20`, `versionName=2.0.0`, artifact `ArlandSofia-v2.0-debug-apk`.
- **Uji**: `bash tools/test_logic.sh` lulus **22.764 pemeriksaan**, termasuk save/migrasi, route hingga epilog, NPC, ekonomi, romansa, visual settings dan CameraRig. `bash tools/test_visual_fx.sh`: 47 file Java berhasil diparse sebagai Java 11 dan smoke test WorldFx berjalan dengan stub render. `bash tools/test_romance_ui.sh`: uji tombol romansa lulus. Estimasi main story **81–83 menit/route** dan lengkap kedua route **±6,2 jam** (estimator otomatis; belum playtest).
- **Belum teruji**: APK asli dan FPS/memori GPU di Android, karena `./gradlew --offline :android:assembleDebug` tetap mencoba unduhan Gradle 8.11.1 dan gagal `UnknownHostException: services.gradle.org`. Syntax parse dan stub **bukan pengganti kompilasi Android maupun uji sentuh/perangkat**.

---

## v1.9.0 — Visual Overhaul, HUD Polish & Route Enrichment (2026-11-22)

- **Visual / rendering:** Title screen dan route select sekarang memakai layer warna lebih kaya, glow lembut, partikel dekoratif, dan suasana yang lebih hidup. `GameScreen` ditingkatkan dengan halo siang/malam, glow untuk lampu/lentera/kristal, vignette tipis, dan HUD kiri atas yang lebih rapi dengan ikon koin. Animasi sprite `Actor` dipoles dengan idle breathing, walk bob, dan sedikit squash/lean saat bergerak.
- **Konten cerita tambahan:** dua side quest route-eksklusif baru di Chapter 3 — `SQ_ROUTE_A` (Rute Lentera Arland bersama Kak Bayu) dan `SQ_ROUTE_S` (Catatan Tamu Sofia bersama Bu Laras). Keduanya menambah 4 scene baru (`tools/content/naskah_visual_v19.txt`), 2 item (`peta_lentera`, `catatan_lentera`), dan 2 Memory Book entry (`m_route_a`, `m_route_s`).
- **Aset/UI:** `tools/gen_art.py` menambah `ui/icon_coin.png` dan `ui/soft_glow.png`; aset diregenerasi ke `android/assets` dan `android/res`.
- **Data/versi:** hasil generator sekarang **297 scene, 1.455 baris dialog, 84 step, 109 side interaction, 25 NPC, 69 item, 90 entri Memory Book**. `appVersionName=1.9.0`, `versionCode=19`, `OluGame.VERSION=1.9.0`, artifact Actions `ArlandSofia-v1.9-debug-apk`.
- **Pengujian:** `python3 tools/gen_art.py android/assets android/res`, `python3 -I tools/build_content.py`, `python3 -I tools/check_layout.py android/assets`, `bash tools/test_logic.sh`, dan `bash tools/test_romance_ui.sh` **lulus**. `test_logic` melaporkan **22.649 pemeriksaan lulus** dan estimasi lengkap kedua route **±6,1 jam**.
- **Keterbatasan:** build APK Android asli masih belum dijalankan di lingkungan ini karena wrapper Gradle memerlukan akses internet ke `services.gradle.org`. Jadi peningkatan visual v1.9 sudah lolos uji data/logika, tetapi belum diverifikasi di device Android nyata dari sesi ini.

---

## v1.8.0 — The Quiet, Two Perspectives & Sari Closure (2026-11-22)

**Ruang lingkup:** melanjutkan ZIP source v1.7.0, bukan rewrite. Misteri *The Quiet* akhirnya terungkap dan kisah Pak Wira/Nenek Sari mendapat penutup yang dapat dimainkan. Kedua route tetap bertemu pada canon yang sama, tetapi petunjuk, respons, urutan interaksi, serta minigame investigasi berbeda.

- **Chapter 1:** setelah menemukan catatan Pak Wira, Arland meneliti denah di stoples barat; Sofia membaca kalimat pudar di stoples timur. Keduanya memicu scene dan flag khusus route sebelum kembali ke Bu Laras.
- **Chapter 4:** seusai surat Wira/Sari, Arland merefleksikan keheningan di halte; Sofia menulis respons di meja perpustakaan. Tidak mengubah konflik hujan atau Lantern Field canon.
- **Chapter 5:** satu langkah petunjuk baru setelah peta bintang, dengan dialog berbeda route.
- **Chapter 6:** tiga jejak per route, **kunci kode bunga–buku–bintang** untuk Arland, **susun empat halaman** untuk Sofia, dilanjutkan pengungkapan *The Quiet* dan dua pilihan respons yang tidak mengganti ending canon. Puzzle menggunakan `Games.CodeLock` dan `Games.Pages` yang sudah ada; ditambah dua konfigurasi data-driven (`quiet_cipher`, `quiet_pages`).
- **Epilog:** pemain menemui Nenek Sari dalam langkah utama Festival Lentera untuk menyerahkan halaman Pak Wira; Sari bercerita tentang rindu dan memilih mengingat. Cerita dan hadiah route-specific. Festival asli dilanjutkan utuh.
- **Data/versi:** `tools/content/naskah_quiet_v18.txt` dengan total 20 scene mentah menjadi **22 adegan runtime** karena dua adegan `me/partner` dipecah per route. Total **293 scene, 1.432 dialog, 84 step, 103 side-interaction, 25 NPC, 67 item, 88 entri Memory Book**. `appVersionName=1.8.0`, `versionCode=18`, `OluGame.VERSION=1.8.0`, artifact Actions `ArlandSofia-v1.8-debug-apk`.
- **Save:** tetap schema 4. Flag route, progress tiga jejak, pilihan, item halaman/pembatas memakai save generik. Tidak ada reset ekonomi, relasi, quest, dunia, atau save. Adegan baru yang sudah dilewati pada file v1.7 memerlukan replay chapter.

### Pengujian yang benar-benar dijalankan

| Perintah | Hasil | Batasan |
|---|---|---|
| `python3 -I tools/build_content.py` | **Lulus**: 293 scene, 1.432 baris, 84 step, 103 side, 25 NPC, 67 item, 88 kenangan | Generator data, bukan engine Android |
| `python3 -I tools/check_layout.py android/assets` | **Layout OK, tanpa error** | Memvalidasi data/peta, bukan tampilan renderer |
| `bash tools/test_logic.sh` | **Lulus 22.547 pemeriksaan**: kedua route sampai festival, semua 17 side quest, 3 jejak per route, seluruh scene The Quiet dan minigame route terpanggil, pilihan tersimpan, item ditukar pada Sari, save ulang petunjuk, regresi toko/pekerjaan/romansa/NPC | Menggunakan Java 11 + stub grafis; tidak menjalankan APK/LibGDX asli |
| `bash tools/test_romance_ui.sh` | **Lulus**: hadiah, kencan, momen gratis serta batasan harian di callback | Uji input stub, bukan uji UI runtime Android; puzzle baru diuji lewat simulasi aksi, bukan sentuhan perangkat |
| `./gradlew --offline :android:assembleDebug` | **Gagal sebelum kompilasi**: `UnknownHostException: services.gradle.org` ketika mengambil Gradle 8.11.1 | APK dan performa perangkat belum dapat diverifikasi; jangan dianggap sudah built |

**Durasi hasil simulasi:** Arland cerita utama ±81 menit, lengkap ±177 menit; Sofia cerita utama ±83 menit, lengkap ±181 menit. Seluruh dua route lengkap ±6,0 jam secara estimator, **bukan** 6 jam per route. Pengujian pemain nyata belum dilakukan; target masih perlu perluasan lanjutan. 22/23 percakapan opsional berhasil dijalankan pada simulator tiap route.

---

## v1.7.0 — Everyday Moments & Relationship Depth (2026-11-22)

**Ruang lingkup:** melanjutkan langsung source v1.6, bukan rewrite. Katalog v1.5 (3 toko/3 kerja) dan hadiah/kencan v1.6 tidak dihapus. Dua route, ending bersama, 22 peta, 17 side quest, 25 NPC, 60 hewan, dan seluruh sistem cerita tetap dipertahankan.

- **8 momen berdua** berbasis data (`ROMANCE['moments']`), dengan validasi lokasi, jam, cuaca dan hati. Gratis; satu momen per hari game; kedekatan bertambah +3 s.d. +8; tidak memotong koin atau kuota hadiah/kencan. Dialog tidak mengubah ending canon.
- **18 adegan tambahan** (16 sudut pandang unik untuk 8 momen dan 2 versi milestone 80), total **271 adegan/1.243 baris dialog naskah**. Tambahan **9 Memory Book** dari momen pertama dan milestone 80; total **79 entri**.
- **UI** `RomanceOverlay`: tab Momen Harian, keterangan kenapa kegiatan terkunci, 3 item/halaman dan tombol sentuh. Callback yang sudah dipakai `GameScreen` menyimpan state dan menjalankan adegan.
- **Save schema 4**: histori `momentCounts` & `lastMomentDay`, migrasi schema 1/2/3, validasi angka untuk mencegah data negatif/overflow. Sistem replay tidak menambah kedekatan.
- **Pengujian ditambah** `testMoments()` dan `playMoments()` pada `LogicSelfTest`, serta uji klik tab ketiga pada `RomanceOverlaySmoke`. Kedua route menjalani 8 momen sungguhan melalui ActionRunner.
- **Dokumentasi/versi**: README, `docs/MOMENTS_V1.7.md`, `versionName=1.7.0`, `versionCode=17`, nama artifact Actions `ArlandSofia-v1.7-debug-apk`.

### Pengujian yang benar-benar dijalankan

| Perintah | Hasil | Batasan |
|---|---|---|
| `bash tools/test_logic.sh` | **Lulus**: generator `scene 271`, `baris dialog 1243`, `step 73`, `side 103`, `npc 25`, `item 65`, `entri 79`; `Layout OK`; `SEMUA LULUS: 22069 pemeriksaan` | Kompilasi Java logika memakai stub grafis, bukan library Android/LibGDX asli |
| `bash tools/test_romance_ui.sh` | **Lulus**: hadiah dikonsumsi, kencan dibayar, momen gratis, batas harian dan hari baru; callback 4 kali | Simulasi tombol berbasis stub, bukan render atau input di Android |
| `./gradlew :core:test :android:assembleDebug --stacktrace` | **Gagal sebelum kompilasi**: `java.net.UnknownHostException: services.gradle.org` ketika wrapper mengunduh `gradle-8.11.1-bin.zip` | APK dan performa Android **belum** diuji |

**Keterbatasan diketahui:** durasi terukur ±72/73 menit cerita utama per route, ±2,8 jam/route dengan side & eksplorasi. Target 6 jam/route belum tercapai. 22 dari 23 percakapan opsional dapat diputar dalam simulator per route. Distribusi ZIP berisi source, bukan APK siap instal. Build Gradle dengan internet pada mesin developer atau melalui GitHub Actions, lalu jalankan QA perangkat nyata. Validasi `INTERNET` tetap dipaksakan pada pipeline.

---

## v1.6.0 — Romance & Economy Integration (2026-11-22)

### Hubungan pasangan & gameplay
- Saat Arland/Sofia menjadi companion (C02+), dekati pasangan untuk membuka panel **♥ Waktu Berdua**, setelah percakapan opsional area tersebut selesai. Percakapan lama tidak dihapus.
- **9 hadiah** memakai barang dari 3 toko v1.5: hadiah menghabiskan satu item di Tas, bisa dibeli ulang, dan menambah +3–10 kedekatan. Maksimal **1 hadiah per hari**.
- **3 kencan** (Taman Kota, Kafe Senja, Bukit Bintang), memerlukan jam dan lokasi yang cocok, companion aktif, serta koin cukup; biaya **8/12/18 koin**, bonus **+10/+12/+16** kedekatan. Maksimal **1 kencan per hari** meskipun pindah lokasi.
- **Kedekatan 0–100** tersimpan dan ditampilkan di HUD/panel. Ambang 20/50 membuka dua kenangan dan dialog yang dimainkan sekali. Hadiah pertama dan 3 kencan juga membuka kenangan baru, total **6 entri Memory Book** tambahan.
- **16 adegan dialog baru**: 3 adegan hadiah yang dipecah per route, 6 adegan kencan khusus route, serta 2 adegan milestone yang dipecah per route. Sebagian dialog dan pose menggunakan cutscene data-driven dan sistem emote lama; cerita utama, route, 17 side quest, 22 peta, 25 NPC, 60 hewan tetap dipertahankan. Total **253 adegan / 1.152 baris dialog**, 73 step, 103 interaksi sampingan, 65 item, 70 entri Memory Book.
- **Save schema 3**: migrasi dari schema 1/v1.4 dan schema 2/v1.5 tanpa menghapus saldo, jobDays, inventory, progress route/slot, atau chapter snapshot. State baru: `affection`, `lastGiftDay`, `lastDateDay`, `dateCounts`.
- Katalog dan dialog: `tools/content/romance.py` dan `tools/content/naskah_romance.txt`. JSON runtime dibuat lewat generator, tidak diedit manual. UI baru: `RomanceOverlay.java`; validasi ekonomi di `QuestEngine.java`.
- VersionName `1.6.0`, versionCode `16`, `OluGame.VERSION`, README, dan nama artifact GitHub Actions diperbarui. Referensi pemeliharaan lengkap di `docs/ROMANCE_V1.6.md`.

### Pengujian yang benar-benar dijalankan
| Pengujian | Hasil |
|---|---|
| `python3 -I tools/build_content.py` | Lulus: 253 adegan, 1.152 baris dialog, 103 side, 65 item, 70 memori |
| `python3 -I tools/check_layout.py android/assets` | `Layout OK, tanpa error.` |
| `bash tools/test_logic.sh` (`javac --release 11` dengan stub minimal) | **21.678 pemeriksaan lulus**, mencakup kedua route sampai epilog, 17 side quest, 3 pekerjaan, 9 hadiah, 3 kencan, 2 milestone, nilai kedekatan, migrasi save v1.4/v1.5, dan dunia hidup |
| UI `RomanceOverlay` memakai stub `Ui`/`Assets` + uji klik | Lulus: tombol hadiah menghabiskan item, tombol kencan memotong saldo, kencan berulang ditolak, callback aksi dialog dipanggil; **bukan render UI asli** |
| `./gradlew --offline :android:assembleDebug` | **Gagal sebelum kompilasi source Android:** distribusi Gradle 8.11.1 tidak tersedia; `UnknownHostException: services.gradle.org` |
| APK nyata, touch HP, visual, cutscene dan performa di perangkat | **Belum terverifikasi** |

**Batasan:** ini ZIP **source v1.6.0**, bukan APK teruji. Estimasi main story ±72–73 menit/route; total lama ±2,75 jam/route dengan side + eksplorasi, kegiatan romantis berulang tidak dihitung sebagai durasi cerita. Target 6 jam/route belum tercapai. Tidak ada klaim kompatibilitas perangkat sebelum build/QA Android.

## v1.5.0 — Economy & Jobs (2026-11-22)

### Ekonomi dan profesi (tidak mengubah engine, route, atau alur canon)
- Menambahkan dompet **12 koin awal**, saldo di HUD, serta save schema **2**. Save schema 1 dari v1.4 tetap dapat dibaca/migrasi; progress per route/slot tidak bercampur.
- **3 toko dengan layar katalog native LibGDX:** Kafe Senja, Toko Bunga Melati, dan Kios Bu Rini, masing-masing 3 produk (total **9 barang belanja**). Harga tersedia di `tools/content/economy.py`. Barang dibeli satu kali per jenis, harus punya saldo cukup, dan muncul di Memory Book → Tas.
- **Shift barista**: minigame lama `pour` (tuang teh), upah 20 koin; **merangkai bunga**: varian data-driven minigame `cooking` 8 tahap, upah 22 koin. Hasil minigame divalidasi dan dibayar sekali per hari kerja.
- **Kurir Pak Pos**: mulai di halte Perumahan, antar surat ke 3 titik (Plaza/Jalan Kota/Tepi Danau), bonus 28 koin tepat saat alamat terakhir diselesaikan. Label objek dan HUD melacak status, surat tidak dapat dikirim dua kali pada hari yang sama, serta gugur bila tidur sebelum selesai.
- 3 entri Memory Book untuk pekerjaan pertama; jumlah **103 interaksi sampingan**, **65 item**, **64 entri Memory Book**. Cerita tetap 237 scene/1.080 baris, 73 step, 17 side quest, 25 NPC, dan 60 hewan.
- `tools/content/economy.py` menjadi sumber toko/pekerjaan/objek baru. JSON di `android/assets/data/` dihasilkan dengan `build_content.py`, tidak ditulis tangan. Dokumen dan nama artifact CI dinaikkan ke v1.5.
- Reproduksi uji logika: `bash tools/test_logic.sh` menggunakan shim minimal pada `tools/stubs/logic/` untuk menguji *logic* Java dan kelas Animal, **bukan build grafis LibGDX**.

### Pengujian yang benar-benar dijalankan
| Pengujian | Hasil |
|---|---|
| `python3 -I tools/build_content.py` | Lulus: 123 jadwal NPC, 22 NPC berjadwal, 60 hewan, 237 scene, 103 side, 65 item, 64 memori |
| `python3 -I tools/check_layout.py android/assets` | `Layout OK, tanpa error.` |
| `javac --release 11` kelas `logic/` + `Animal.java` + `LogicSelfTest` dengan shim grafis minimal | Lulus (bukan build LibGDX/Android asli) |
| `LogicSelfTest` dua route, 17 side quest, simulasi ekonomi, pembelian, save/migrasi, upah harian dan reset hari | Lulus, **21.409 pemeriksaan** |
| `./gradlew --offline :android:assembleDebug` | **Terhalang**: Gradle 8.11.1 tidak tersedia lokal; download `services.gradle.org` gagal `UnknownHostException` |
| Uji input `ShopOverlay` dengan stub UI minimal (beli, blokir duplikat, tutup) | Lulus (bukan render LibGDX asli) |
| Build APK nyata dan pengujian UI toko/performa di emulator/HP | **Belum dilakukan** — wajib diuji di lingkungan ber-Android SDK dan jaringan build |

### Batasan
- Durasi cerita ±2,75 jam/route lengkap (tidak memasukkan pengulangan kerja). Target 6 jam/route masih belum tercapai.
- NPC berpindah area instan; representasi NPC belum sepenuhnya berbeda. Permasalahan lama belum diubah.
- Ketergantungan Gradle/LibGDX tidak dapat diuji pada runtime lingkungan ini. **Status rilis: source v1.5.0 siap untuk build dan QA lanjutan, belum dinyatakan APK siap produksi.**

## v1.4.0 — Living World Update (2026-11-22)

Fondasi simulasi kehidupan di atas cerita. Cerita, misi utama, dan side quest lama tetap berjalan seperti sebelumnya.

### Waktu & hari
- **Jam dunia**: hari berjalan 06:00–02:00, 1 detik nyata = 1 menit game. Jam hanya berjalan saat bebas bermain (berhenti saat dialog, cutscene, menu, minigame, dan di dunia kenangan).
- **Siang–malam bertahap**: fajar jingga → siang terang → jam emas → senja → malam biru → larut lebih gelap. Lampu jalan berpendar saat malam. Musik kota berganti ke musik malam otomatis.
- **Tidur**: dekati kasur di kamarmu → "Tidur" → pagi berikutnya jam 07:00, progres tersimpan otomatis. Bila tetap di luar sampai 02:00, karakter ketiduran dan bangun di kamar.
- **HUD**: nama hari, hari ke-berapa, jam, dan cuaca.
- **Selaras dengan cerita**: step bersuasana senja/malam memajukan jam (hanya maju) supaya langit, HUD, dan NPC cocok.

### Cuaca harian
- Cerah, berawan (langit lebih redup), berangin (daun & kelopak terbawa angin), hujan (partikel hujan + musik hujan). Deterministik per hari, jadi sama untuk save yang sama. Hari 1–2 selalu cerah. Hujan sekitar 16% hari (diuji 140 hari).
- Hujan cerita (Chapter 4) tetap menimpa cuaca harian.

### Warga yang hidup (13 → 25 NPC, 22 berjadwal, 123 titik jadwal)
- **Jadwal harian** per warga, dengan versi khusus hujan. Contoh: Kak Raka lari pagi di Tepi Danau → buka kafe → istirahat di plaza → pulang jam 22:00. Pak Udin memancing di dermaga subuh, ngopi di kafe sore, dan berteduh di kafe saat hujan. Dito & Tika sekolah pagi, main di taman siang, dan pindah ke arcade bila hujan.
- **Berjalan-jalan**: warga berjalan ke titik jadwal berikutnya bila masih di area yang sama, lalu mondar-mandir di radius masing-masing. Mereka berhenti saat diajak bicara dan tidak menabrak pemain.
- **Dialog sesuai jam & cuaca** untuk semua warga lama (mis. Raka saat lari pagi, Melati saat makan siang, Udin saat hujan).
- **12 warga baru**: Bu Rini (penjual kue), Pak Harun (penjaga taman), Tika, Mas Eko (pelari), Bu Wulan, Kakek Darmo (dermaga), Pak Darto (satpam ronda malam), Rara & Bimo (pelajar), Pak Ujang (penjual balon), Oma Ina, Bang Tigor (ojek pangkalan).
- **Pengaman cerita**: warga yang dibutuhkan step aktif (interaksi di dekat posisinya, NPC step, atau dialog bersyarat step) tetap di posisi rumahnya, sehingga cerita tidak buntu karena jadwal.

### Hewan (60 hewan di 8 area)
- Kucing (oranye, abu, hitam, belang tiga), anjing, bebek, burung, ayam, kelinci, dan tupai. Semua pixel art baru (`tools/gen_animals.py`).
- Perilaku: berjalan, duduk, dan meringkuk (kucing/anjing/ayam); berenang di kolam & danau (bebek, tetap keluar saat hujan); terbang menjauh bila didekati (burung); kabur bila dikejar (kelinci/tupai).
- Siang dan malam berbeda: burung, kelinci, dan anjing pulang malam hari; kucing malam keluar mulai 19:30.
- **Elus**: kucing, anjing, bebek, ayam, kelinci. Muncul hati, dan pasangan ikut senang.

### Side quest baru (15 → 17)
- **Kue untuk Kakek Darmo** (Bu Rini → Kakek Darmo → Bu Rini), memanfaatkan jadwal: Kakek di dermaga pagi dan pindah ke Tepi Danau siang.
- **Teman Berbulu** (Pak Harun): elus kucing, anjing, dan bebek.
- 2 entri Memory Book dan 3 item baru.

### Alat
- `tools/world_preview.py`: time-lapse satu hari dari data game (jadwal, hewan, cahaya, cuaca). Ini alat desain, bukan rekaman APK.
- `check_layout.py` memvalidasi setiap titik jadwal dan region hewan. `build_content.py` men-snap titik jadwal ke sel terjangkau terdekat.

### Pengujian yang benar-benar dijalankan
| Uji | Hasil |
|---|---|
| `javac --release 11` vs stub API | Lulus |
| LogicSelfTest: kedua route + 17 side quest + uji dunia (jam, cuaca 140 hari, 22 jadwal × 7 hari × tiap 15 menit, hewan tidak menembus tembok, save hari/jam) | Lulus, 21.257 pemeriksaan |
| `check_layout.py` (123 titik jadwal, 30 region hewan) | Lulus |
| Estimasi | Cerita utama 2,4 jam, lengkap 5,5 jam (kedua route). Waktu bebas bermain di dunia hidup tidak dihitung. |
| **Belum:** build Gradle, APK di HP, playtest, performa 25 NPC + hewan di HP kelas bawah | — |

### Yang belum ada (sengaja ditunda ke tahap berikutnya)
Uang & toko, pekerjaan sampingan, poin pertemanan NPC, hadiah untuk NPC, berkebun, kalender event musiman, interior rumah warga, dan NPC yang pindah antar area sambil terlihat berjalan (sekarang warga muncul di area tujuan).

## v1.3.0 — Explorer & Detail Update (2026-11-22)

### Kepadatan pixel & grafik (semua 22 peta dibangun ulang)
- **Rumput** berlapis: 3 nada dengan dither Bayer (tidak lagi bercak lembut), rumpun bervolume (tepi atas terang, bawah gelap), helai halus, semanggi, kerikil.
- **Jalan tanah**: 3 nada dither, kerikil bersorot, tepi bertingkat, rumput menjuntai. Persimpangan jalan tidak lagi meninggalkan garis tepi di tengah jalan.
- **Medan baru**: tebing dataran tinggi berlapis batu dengan bayangan di kakinya, tangga batu, sungai kecil, batu pijakan, lantai hutan berdaun gugur, lantai gua dengan retakan dan kilau mineral, dan tepi gua yang tidak beraturan.
- **18 props baru**: pohon ek besar, pohon hutan gelap, semak beri, peti (tertutup/terbuka), mulut gua, observatorium berkubah, lentera batu, jembatan rusak/utuh, batu berukir (4 simbol), cincin jamur, api unggun, tenda, bangku kayu gelondong, stalagmit, kristal besar bercahaya, air terjun.
- Tiang lampu di plaza tidak lagi menutupi bangku.

### Eksplorasi (19 → 22 area)
- **Hutan Bisik** (2560×1920 px, peta terbesar): 8 cabang jalan, dua dataran tinggi bertangga, sungai dengan air terjun, kuil tua dengan lentera batu, perkemahan, cincin jamur, celah sempit menuju lembah rahasia, dan mulut gua. Pintunya dari utara Taman Kota (terbuka mulai Chapter 2).
- **Bukit Bintang**: observatorium, dek pandang dengan teropong, padang bunga, tebing pemandangan kota, dan NPC baru Kak Nara.
- **Gua Kristal**: area gelap dengan lingkar cahaya di sekitar pemain, kristal berpendar, kolam bawah tanah, dan ukiran misterius "W + S".
- **Gerbang dinamis** di engine: jembatan rusak benar-benar menghalangi (sudah diuji, sisi timur tidak bisa dicapai sebelum jembatan diperbaiki).

### Aktivitas eksplorasi baru
- **Kepingan Bintang**: 30 kepingan tersembunyi di 10 area. Hadiah dari Kak Nara di 10, 20, dan 30 kepingan, dan yang ke-30 membuka "peta langit" (benih jalan bintang untuk Chapter 5).
- **Jembatan Hutan**: cari 3 papan, lalu perbaiki jembatan lewat cutscene.
- **4 peti harta**, salah satunya **peti kata sandi** (minigame kunci simbol baru). Petunjuknya terukir di batu kuil, perkemahan, dan gua.
- **Teropong observatorium** (minigame peta bintang dengan urutan baru).
- Komentar companion di 3 area baru. Lore tentang Pak Wira dan Nenek Sari (lukisan "W. untuk S.", ukiran di gua) menyambung ke cerita Chapter 1 dan 4.
- Total: 237 adegan, 1.080 baris naskah, 94 interaksi sampingan, 15 side quest, 13 NPC, 53 item, 59 entri Memory Book.

### Pengujian yang benar-benar dijalankan
| Uji | Hasil |
|---|---|
| `javac --release 11` vs stub API | Lulus |
| LogicSelfTest (kedua route, 15 side quest termasuk 30 bintang & peti kata sandi) | Lulus, 7.458 pemeriksaan |
| `check_layout.py` 22 peta (semua bintang, peti, papan terjangkau) | Lulus |
| Uji gerbang: jembatan tertutup memblok sisi timur, papan tetap terjangkau | Lulus |
| Estimasi | Cerita utama 2,4 jam, lengkap 5,3 jam (kedua route) |
| **Belum:** build Gradle, APK di HP, playtest | — |

## v1.2.0 — World & Story Expansion (2026-11-22)

### Lokasi baru (15 → 19 area), semuanya punya cerita dan aktivitas
- **Distrik Perumahan**: jalan dua jalur, perpustakaan, 4 rumah warga, kebun, halte, dan kotak surat tua. Pintu masuknya ada di ujung timur Jalan Kota, yang dulu ditutup.
- **Perpustakaan Kota**: rak-rak tinggi, meja baca, bola dunia, dan sofa baca. Ada NPC baru, Bu Laras, dan puzzle "Rak yang Sunyi" (cari 3 buku catatan Pak Wira, letakkan di meja baca, lalu rak rahasia bergeser terbuka).
- **Ruang Arsip Rahasia (Arsip No. 7)**: stoples-stoples cahaya kenangan dan tiang batu bercahaya. Di sini benih misteri The Quiet mulai ditanam.
- **Dermaga Danau**: dermaga panjang berbentuk T, perahu, pondok sewa perahu, dan NPC baru Kak Bayu. Ada spot memancing ketiga dan momen senja di Chapter 1.
- 17 props pixel art baru (rak tinggi, rak rahasia buka/tutup, meja baca, bola dunia, meja informasi, tumpukan buku, lilin, rak stoples bercahaya, tiang arsip, perahu, tiang dermaga, pondok, kotak surat tua, kebun, pagar tanaman, genangan, teleskop). Sebagian juga dipasang di peta lama.

### Cerita
- **Chapter 1 diperluas**: cap "Arsip No. 7" di surat kafe membawa pemain ke perpustakaan. Di sana pemain bertemu Bu Laras, mendengar kisah Pak Wira (suami Nenek Sari), memecahkan puzzle rak, lalu menemukan arsip kenangan dan catatan pertama tentang "sunyi". Chapter ditutup dengan cutscene senja di ujung dermaga: duduk berdua, langit berubah dari jingga ke ungu, lalu bintang muncul.
- **Chapter 4, dua surat lama**: di route Arland, ia menemukan surat permintaan maaf Pak Wira untuk Sari di kotak surat halte. Di route Sofia, Bu Laras memberinya surat balasan Nenek Sari yang tidak pernah terkirim. Dua sisi dari satu pertengkaran lama yang mencerminkan Arland dan Sofia, sesuai tema canon "dua sisi, satu tempat pulang".
- Nenek Sari bereaksi setelah pemain menemukan arsip dan surat-surat itu. Komentar companion juga ada di 4 area baru.
- Total: 220 adegan (31 baru), 1.030 baris naskah, 73 step, 12 NPC, 46 item, 53 entri Memory Book.

### Musik (2 → 8 lagu orisinal, OGG)
- `gen_music2.py`: synth electric piano FM, pluck, pad detune, flute, bell, piano, bass, drum lembut, reverb Schroeder, dan loop yang menyambung mulus.
- Lagu: Kota (pagi), Kafe Senja (lo-fi jazz), Hujan (piano minor), Malam Festival, Memory Garden, Across the Stars, Our Tomorrow (balada piano), Minigame.
- Musik dipilih otomatis per area dan suasana: kota berganti musik saat hujan dan saat malam, step bisa menimpa musik (mis. senja di dermaga memakai balada). Stream lama dilepas setelah crossfade.

### Pengujian yang benar-benar dijalankan
| Uji | Hasil |
|---|---|
| `javac --release 11` vs stub API | Lulus |
| LogicSelfTest (kedua route sampai Epilog, termasuk puzzle perpustakaan dan dua surat) | Lulus, 6.289 pemeriksaan |
| `check_layout.py` 19 peta + posisi akhir semua cutscene | Lulus |
| Pratinjau cutscene baru dicek frame demi frame | 3 perbaikan: posisi sofa, halte, duduk di dermaga |
| Musik: RMS, clipping, sambungan loop (dicek numerik, tidak didengar) | Tanpa clipping |
| Estimasi | Cerita utama 2,4 jam, lengkap 4,6 jam (kedua route) |
| **Belum:** build Gradle, APK di HP, playtest | — |

## v1.1.0 — Cinematic Foundation (2026-11-22)

Fase 1 dari Master Prompt v2.0 (cutscene + animasi + companion). Peta baru dan Chapter 1–6 sinematik belum dikerjakan.

### Sistem cutscene (baru)
- `CutscenePlayer`: kamera pan/zoom halus, aktor berjalan/berlari mengikuti jalur, menghadap, pose dan gestur, emote, letterbox, fade berwarna, flash, tint, getaran kamera, caption lokasi/waktu, aktor sementara, dan 10 jenis efek partikel (portal, buku bercahaya, hati, kelopak, lentera, sinar, gelombang pemulihan, dan lain-lain).
- Dialog bisa dipotong per baris (`say` dengan `from`/`n`), jadi gestur bisa disisipkan di antara kalimat.
- Step bisa memicu cutscene saat dimulai (`onStart`), termasuk saat New Game.
- Tahan layar untuk mempercepat cutscene x3. HUD disembunyikan selama cutscene.
- Validasi: LogicSelfTest memeriksa setiap perintah, aktor, pose, dan adegan; `check_layout.py` memeriksa posisi akhir pemain/pasangan setelah cutscene.

### Animasi karakter (baru)
- Lembar pose untuk semua 10 karakter (`tools/gen_poses.py`, dibuat dari sprite asli tanpa mengganti desain): duduk, melambai (2 frame), memberi hadiah, meraih/menerima, menunduk, bergandengan kiri/kanan, bersorak (2 frame).
- Gestur prosedural: tertawa, kaget (lompat), mengangguk, menggeleng, lompat gembira.
- Napas idle (kepala/bahu naik 1px dengan ritme acak per karakter), sedikit condong saat berlari.

### Prolog sinematik (kedua route)
- Bangun tidur di kamar (duduk di kasur, caption "Sabtu pagi", berjalan ke ponsel). Versi Sofia ada sisa cahaya mimpi dan peregangan.
- Menyiapkan hadiah (pose memegang hadiah).
- Tiba di plaza: kamera menyapu plaza, lalu fokus ke pasangan yang menunggu (aktivitas berbeda per route).
- Pertemuan: melambai, berjalan mendekat, saling memberi dan menerima hadiah di sela dialog, efek hati, lalu kamera pindah ke buku yang berpendar.
- Buku dan portal: buku terangkat bercahaya, getaran, portal berputar, kamera zoom, bergandengan tangan, flash putih.
- Tiba di Memory Garden: fade dari putih, caption, kamera turun, karakter melihat sekeliling. Keping cahaya menyatu dengan gelombang pemulihan dan gerbang pulang menyala.

### Dunia lebih hidup
- Companion: menoleh ke target interaksi pemain, melihat sekeliling, memperhatikan NPC terdekat, bereaksi pada hujan, sesekali emote, dan berkomentar sekali per area (13 area x 2 route, balon kata).
- Kupu-kupu di area luar siang hari; lampu jalan dan lentera berpendar saat malam, hujan, dan di Memory Realm.

### Pengujian yang benar-benar dijalankan
| Uji | Hasil |
|---|---|
| `javac --release 11` vs stub API | Lulus |
| LogicSelfTest (kedua route sampai Epilog, cutscene tervalidasi) | Lulus, 5.209 pemeriksaan |
| `check_layout.py` termasuk posisi akhir cutscene | Lulus |
| Pratinjau cutscene Prolog (`cine_preview.py`) dicek frame demi frame | Satu perbaikan: posisi gandengan tangan |
| **Belum:** build Gradle, APK di HP, playtest | — |

## v1.0.0 — Content Update (2026-11-22)

### Cerita & konten baru
- **Hari Bebas** di tiga chapter. Pemain memilih 2 dari 3 kegiatan kota sebelum cerita berlanjut:
  - C02 *Pagi yang Panjang*: menyiram 3 petak bunga untuk Nenek Sari, Hujan Bintang di arcade, petak umpet dengan Dito (3 tempat sembunyi).
  - C03 *Pasar Minggu* di plaza: tebak berat semangka, lapak buku bekas (3 pilihan buku), lempar gelang bersama Bang Juna.
  - C05 *Sore Sebelum Festival* (nuansa senja): tuang teh rempah bersama Kak Raka, menggantung 4 lentera di Taman Kota untuk Bu Melati (lentera benar-benar menyala di peta), menulis kartu harapan.
- **Festival Lentera** sebagai klimaks Epilog: malam di Taman Kota bersama semua NPC, pilih 3 dari 4 kegiatan (teh, mahkota bunga, Hujan Bintang, cerita Pak Udin), lalu melepas lentera bersama di kolam.
- 4 side quest baru: **Surat Pak Pos** (NPC baru, 5 surat dengan cerita kecil tiap penerima), **Koleksi Resep Kafe** (3 resep masak berbeda), **Buku yang Tersesat** (5 buku di 5 lokasi), **Mural Baru** (4 kaleng cat; mural plaza berganti gambar setelah selesai).
- Format naskah baru `me`/`partner`: satu adegan otomatis menjadi versi Arland dan versi Sofia (`ID@arland` / `ID@sofia`).
- Total: 189 adegan, 894 baris naskah, 62 step, 53 interaksi sampingan, 10 NPC, 43 item, 48 entri Memory Book.

### Gameplay & engine
- Minigame baru: **Hujan Bintang** (tangkap bintang jatuh, bintang emas bernilai 3), **Lempar Gelang** (5 lemparan), **Tuang Teh** (berhenti di garis).
- Minigame kini bisa memakai `type` di konfigurasi, jadi satu jenis permainan bisa dipakai ulang dengan isi berbeda (3 resep masak kafe).
- Percakapan pasangan mendukung id adegan khusus route.
- Props kondisional baru: lentera festival di Taman Kota, mural baru di plaza. Lapak payung dan peti di plaza.

### Pengujian yang benar-benar dijalankan
| Uji | Hasil |
|---|---|
| `javac --release 11` seluruh core + launcher vs stub API | Lulus |
| LogicSelfTest: Arland 72 step & Sofia 73 step sampai Festival + Epilog, 6 jenis minigame cerita, kredit, snapshot semua chapter | Lulus |
| 12 side quest + 23/23 percakapan pasangan di kedua route | Lulus |
| Validasi data (adegan per route, step, item, minigame, pembicara, gambar) + save/pemulihan | Lulus (4.779 pemeriksaan) |
| `check_layout.py` (BFS jangkauan fisik 15 peta) | Lulus |
| Estimasi durasi | Kedua route lengkap ±4,0 jam (cerita utama ±2,0 jam) |
| **Belum dijalankan:** Gradle build, APK di perangkat, playtest manusia | — |

### Menuju 6 jam (sisa ±2 jam terukur)
- 2–3 adegan khusus route per chapter, masing-masing dengan tugas di peta.
- 15–20 percakapan pasangan tambahan (Hari Bebas, festival, pasca-tamat).
- Koleksi lengkap 8 jenis ikan dan tantangan skor arcade sebagai target 100%.

## v0.9.0 — Story Complete Preview (2026-11-22)

### Peta (dibuat ulang total)
- 15 peta pixel art prosedural dengan tile bertekstur: rumput bergradasi + petak bunga + rumput tinggi, jalan tanah, batu paving, air dengan gradasi kedalaman, buih, dan pasir pantai, lantai kayu, ubin, wallpaper dengan wainscot, jendela bercahaya matahari.
- Bangunan sebagai props 3/4 yang bisa dilewati di belakangnya (atap genteng, jendela bertirai, kotak bunga, kanopi toko, papan nama). Bayangan dipanggang ke tanah.
- 6 peta lama diperbarui; 9 peta baru: Jalan Kota, Taman Kota (kolam, sungai, jembatan, gazebo), Dapur, Toko Bunga, Arcade, Lantern Field, Star Path, Starfall Village, Eternal Garden.
- Deretan pohon di tepi peta, dekorasi tersebar otomatis yang menghindari jalan, air, pintu, dan titik quest.
- Efek runtime: kilau air bergerak, kelopak sakura, kunang-kunang, bintang berkelip, hujan (Chapter 4), nuansa senja (C02), dan malam (C05). Lentera Lantern Field menyala setelah puzzle.
- Tetap pixel art: tampil tajam di layar HD/4K lewat scaling nearest-neighbor. Bukan lukisan beresolusi 4K (sengaja, agar menyatu dengan sprite karakter dan APK tetap kecil, aset ±13 MB).

### Cerita
- Chapter 2–6 + Epilog ditulis penuh untuk kedua route (canon Story Bible tetap utuh): kencan pertama, bunga dan foto kecil, memasak dan piknik, salah paham di hari hujan dan Lantern Field, Lumi si roh lentera, Star Path / jalur lentera menuju Starfall Village, Eternal Garden, halaman kosong "To Be Continued", kredit, dan Epilog bebas.
- 118 adegan, 578 baris naskah. Per route ±370 baris diputar (cerita + side + ngobrol).
- 23 percakapan opsional dengan pasangan (berdasarkan lokasi dan chapter, termasuk 6 percakapan pasca-tamat).
- NPC kota dengan dialog berubah per chapter: Kak Raka, Bu Melati, Bang Juna, Nenek Sari, Dito, Pak Udin, Lumi.
- 8 side quest; "Halaman yang Hilang" berisi 20 halaman lore yang membuka rahasia kecil Nenek Sari.

### Gameplay & engine
- Minigame: Photobooth (4 jepretan), Masak Bersama (8 langkah), Altar Lentera (3 papan, dijamin bisa diselesaikan), Peta Bintang (kompas Arland + warna lentera Sofia), Susun Halaman (9 kenangan), Mesin Capit, Memancing (8 jenis ikan, bisa diulang).
- Sistem kondisi data (flag, step, chapter, item, counter), aksi `if`, counter generik, NPC kota, side interactable, percakapan pasangan, prop alternatif berbasis flag, cuaca/tint per step.
- Memory Book: tab **Misi** (status side quest), main ulang semua chapter (snapshot termasuk chapter yang awalnya berbeda per route), bonus setelah kedua route tamat Chapter 6.
- Peta dimuat saat dibutuhkan dan dilepas saat pindah (hemat memori GPU untuk peta 2048 px).

### Pengujian yang benar-benar dijalankan
| Uji | Hasil |
|---|---|
| `javac --release 11` seluruh core + launcher vs stub API LibGDX/Android | Lulus |
| LogicSelfTest: Arland 54 step & Sofia 55 step dari New Game sampai Epilog, 5 minigame cerita, kredit, snapshot replay semua chapter | Lulus |
| 8 side quest + 23/23 percakapan pasangan + 20 halaman lore bisa diselesaikan di kedua route | Lulus |
| Validasi data (scene, step, item, minigame, pembicara, gambar) + save/pemulihan | Lulus (3.695 pemeriksaan) |
| `check_layout.py`: BFS jangkauan fisik semua titik di 15 peta | Lulus |
| Estimasi durasi | Kedua route lengkap ±3,0 jam (cerita utama ±1,6 jam) |
| **Belum dijalankan:** Gradle build, APK di perangkat/emulator, uji mode pesawat, multi-DPI, playtest manusia | — |

### Bug yang ditemukan oleh pengujian otomatis lalu diperbaiki
- Adegan renungan C04 belum memasang flag pembuka entri Memory Book.
- Rantai `if` jenis ikan tersusun terbalik (semua tangkapan tercatat sebagai Ikan Mas).
- Dua Halaman Hilang berada di kamar yang tidak bisa dimasuki oleh route lain (side quest mustahil diselesaikan).
- Save bisa tertulis di tengah rangkaian aksi saat aplikasi di-background (berpotensi terjebak di Memory Garden).

### Yang belum / rencana menuju 6 jam
- **Durasi:** estimasi terukur ±3 jam untuk kedua route. Untuk mendekati 6 jam masih dibutuhkan kira-kira: satu "hari bebas" per chapter dengan aktivitas kota (pasar, festival lentera sebagai event), 2–3 adegan tambahan per chapter per route, 4–6 side quest berlapis lagi, dan koleksi (resep, foto, ikan) dengan hadiah bertingkat.
- NPC memakai sprite Arland/Sofia yang diganti palet: wajah NPC laki-laki mirip Arland (berkacamata). Perlu sprite NPC orisinal.
- Animasi berjalan masih 3 frame per arah; belum ada pose lari, duduk, atau interaksi khusus.
- Musik masih placeholder sintesis.
- Belum diuji di perangkat nyata, belum ada impor save web v0.4, dan belum ada APK rilis bertanda tangan.

---

## v0.5.0 — Native Foundation (2026-11-22)

Migrasi dari prototipe web v0.4 (HTML5 Canvas) ke **project Android native LibGDX + Gradle**. Source v0.4 hanya dipakai sebagai referensi; tidak ada kode web yang dipakai saat runtime.

### Versi teknologi
Gradle 8.11.1 (wrapper) • Android Gradle Plugin 8.7.3 • JDK 17 • Java target 11 • LibGDX 1.13.1 • compileSdk/targetSdk 35 • minSdk 21 • ABI: armeabi-v7a, arm64-v8a, x86, x86_64.

### Status build (jujur)
- APK **belum** dibangun: lingkungan pembuatan tidak punya Android SDK dan akses ke repositori Maven/Google/Gradle diblokir.
- Yang terverifikasi: kompilasi seluruh kode Java terhadap stub API LibGDX/Android (signature asli LibGDX 1.13), 498 pemeriksaan logika, dan validasi tata letak peta.
- Build nyata pertama terjadi di Android Studio atau GitHub Actions (`.github/workflows/build-apk.yml`).

### ✅ Selesai
- Project Gradle `core/` + `android/` + Gradle Wrapper, siap dibuka di Android Studio.
- Launcher Android native (OpenGL ES): landscape terkunci, immersive mode, dukungan notch/cutout (safe inset), tanpa WebView, **tanpa izin internet** (dihapus paksa dari merged manifest), `allowBackup=false`.
- Layar: Judul (Lanjutkan, Game Baru, Muat, Pengaturan, Tentang, Keluar), Pilih Route (Arland/Sofia), Pilih Slot (2 slot per route, timpa/hapus dengan konfirmasi), Pengaturan, layar error (bukan layar hitam).
- Eksplorasi top-down: gerak 4 arah + diagonal ternormalisasi, kecepatan analog dari joystick, lari, collision kaki (kotak & elips), sliding di dinding, kamera mengikuti pemain dengan batas peta, render diurutkan berdasarkan Y (karakter bisa di depan/belakang pohon & furnitur).
- 6 peta: Kamar Arland, Kamar Sofia, Plaza Kota, Memory Garden, Kafe Senja, Tepi Danau. Masing-masing punya collision data, props orisinal, pintu dengan fade, label pintu, dan benda yang bisa diperiksa dengan monolog per route.
- Pintu cerdas: terkunci per step ("Sebelum pergi, aku mau menyiapkan sesuatu dulu."), per route (rumah Sofia tidak bisa dimasuki di route Arland), pemain didorong menjauh dari pintu terkunci.
- Companion mengikuti jejak pemain (breadcrumb, tidak menembus dinding) dan NPC pasangan menunggu di plaza.
- Sistem quest data-driven (`quests.json`): Prologue + Chapter 1 lengkap untuk **kedua route** (17 step), sesuai ID quest Story Bible (`Q_PRO_PHONE` … `Q_C01_LETTER`), flags route (`PRO_GIFT_ARLAND`, `C01_HINT_SOFIA`, …), dan canon (`CANON_PLAZA_MEET`, `CANON_BOOK_OPEN`, `CANON_MEMORY_GARDEN`, `CANON_CAFE_LETTER`, `CANON_RIVERSIDE`).
- Dialog dari Story Bible v1.0 (`story.json`, 32 adegan; 15 dipakai di v0.5): potret ekspresi dengan fallback, emote di atas kepala, teks muncul bertahap (4 kecepatan), lewati, pilihan dengan respons berbeda per route (P-X01).
- Hadiah bertukar tangan (bunga kertas ↔ kartu pos), Memory Book sebagai item, 3 keping cahaya dengan penghitung, gerbang pulang.
- Puzzle tiga simbol: urutan canon ARLAND = BUNGA–BUKU–BINTANG, SOFIA = BINTANG–BUKU–BUNGA. Salah = ulang tanpa hukuman, petunjuk muncul setelah 2 kali salah, bisa dibatalkan lalu diulang (tanpa softlock).
- Memory Book: tab **Kenangan** (entri shared/route, "sisi lain" dari route pasangan yang sudah dimainkan, bonus **Kenangan Dua Sisi** setelah kedua route tamat C01), tab **Tas** (item), tab **Bab** (status + **Main Ulang** chapter dari snapshot awal chapter tanpa mengubah progres utama).
- Kartu judul chapter dan kartu "chapter selesai".
- Save lokal: schema berversi, CRC32, tulis atomik, `.bak`, pemulihan otomatis, deteksi slot rusak, save global terpisah (bonus lintas route), autosave setelah setiap rangkaian aksi dan saat aplikasi ke background (tidak pernah menyimpan state setengah jadi).
- HUD: nama area, route + chapter, misi aktif (berkedip saat berubah, teks otomatis mengecil bila panjang), tombol Buku & Jeda, toast.
- Kontrol: joystick melayang, AKSI, LARI, multi-touch per pointer, ukuran (4 level) & transparansi kontrol bisa diatur, keyboard + tombol Back Android.
- Audio offline: 2 musik loop orisinal (kota, Memory Realm) dengan crossfade, 3 SFX dari v0.4, volume musik/efek terpisah.
- Aset karakter dari lembar desain pemilik: sprite 4 arah (3 frame/arah), 7 ekspresi Arland, 8 ekspresi Sofia, kartu profil, banner judul.
- Ketahanan: aset hilang diganti tekstur cadangan (tidak crash), adegan hilang dilewati, posisi save di dalam tembok dikembalikan ke spawn, save yang tidak cocok dengan data dilaporkan dengan pesan.

### 🟡 Sebagian
- **Animasi:** walk memakai 3 frame/arah + efek bob. Lembar desain hanya memuat 3 pose per arah yang nyaris identik; idle 4 frame, walk 8 frame, run 6 frame, interact, dan sit pada lembar desain belum dipotong karena posisinya tidak beraturan. Saat lari, animasi dipercepat (belum ada pose lari khusus).
- **Pathfinding companion:** mengikuti jejak pemain (aman dari dinding), belum A* penuh.
- **Peta:** masih memakai gambar latar v0.4 + data collision/props terpisah (bukan Tiled/TMX). Collision, interaksi, dan depth sudah dipisah dari art di `maps.json`/`props.json`.
- **Ekspresi Arland "Tersenyum":** di lembar desain, sel ke-8 baris Arland ternyata berisi wajah Sofia, jadi tidak dipakai (fallback ke "Senang").
- **Musik:** sintesis sederhana sebagai placeholder orisinal; perlu diganti musik final.

### ⬜ Belum (sesuai tahapan Master Prompt)
- v0.6: NPC kota (barista, penjaga toko bunga, dll.), zona indoor/outdoor tambahan, polish interaksi, variasi outfit.
- v0.7–v0.9: Chapter 2–6, Epilog, photobooth, memasak, hujan, Memory Realm penuh (data naskahnya sudah ada di `story.json`).
- Impor save web v0.4 (JSON eksplisit atas pilihan pengguna) — belum dibuat.
- Uji perangkat nyata: berbagai DPI, mode pesawat sejak install, rotasi, force-close di HP.
- APK/AAB rilis bertanda tangan (butuh keystore milik pemilik).

### 🧪 Pengujian yang benar-benar dijalankan
| Uji | Hasil |
|---|---|
| `javac --release 11` seluruh core + launcher vs stub API LibGDX/Android | Lulus, 0 error |
| `LogicSelfTest`: route Arland & Sofia otomatis dari New Game sampai C01 selesai (17 step, 11 adegan per route), termasuk batal puzzle lalu ulang | Lulus |
| Validasi data: semua scene/step/item/puzzle/chapter yang dirujuk ada, gambar ada, warp & spawn tidak di dalam tembok, target pintu tidak memantul | Lulus |
| Save: simpan/muat, `.bak`, file utama rusak → pulih, keduanya rusak → terdeteksi, isi diubah manual → checksum menolak, settings, global, hapus slot | Lulus |
| Puzzle: benar/salah/reset/petunjuk/selesai | Lulus |
| Replay: snapshot PRO & C01 benar | Lulus |
| `tools/check_layout.py`: jangkauan BFS semua spawn/pintu/interaksi di 6 peta | Lulus |
| **Belum dijalankan:** Gradle build, APK di perangkat/emulator, uji mode pesawat, multi-DPI | — |


## STORY OVERHAUL v4.6.9 — CHAPTER 3 / THE LITTLE THINGS (PRIVATE DRAFT)

- Extended prior v4.6.8 draft without deleting legacy scenes/maps/saves/media.
- C03 narrative expanded with 25 authored new scenes, 4 quest stages, 23 Memory Book entries, 5 collectible catalog items; both routes remember prior kencan response and photo choice.
- Arland repairs a memory frame through a native interactive game; Sofia builds a personal scrapbook; each returns a neighbor's borrowed object.
- Cooking, picnic, market dialogue, the half-letter, gallery invitation and original canon promise are real quest actions with player choices.
- Fixed two-route kitchen `enterArea` softlock, duplicate ingredient/decor counters, gallery completion testing, unreachable half-letter interaction.
- Added 4 original pixel-art icons, 2 original OGG music cues, 1 original WAV and runtime audio registration.
- 864 exhaustive branch-path simulations, 160,568 assertions, 67 navigation and 1,697 static checks passed; full two-route headless story test 26,337 checks passed.
- Idempotent re-apply + content rebuild pipeline integrated. NO ZIP or GitHub changes. Android APK and physical gameplay remain unverified.
