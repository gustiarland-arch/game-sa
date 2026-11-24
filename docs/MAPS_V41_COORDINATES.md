# v4.1 — Koordinat 13 Map yang Diperbarui

Sistem koordinat tetap menggunakan piksel PNG, `(0,0)` kiri atas. **Tidak ada koordinat gameplay yang dipindahkan** dalam v4.1; semua spawn, portal, dan interaksi di bawah ini diambil langsung dari `maps.json` dan `quests.json` source keluaran.

| Map | Resolusi | Spawn (X,Y) | Portal | Examine | Penggantian prop |
|---|---|---|---:|---:|---:|
| `plaza` | 1920×1280 | (960,640) | 6 | 4 | 10 |
| `taman_kota` | 1920×1408 | (1840,705) | 2 | 3 | 9 |
| `riverside` | 1920×1088 | (960,70) | 2 | 1 | 6 |
| `cafe` | 960×640 | (400,270) | 2 | 2 | 6 |
| `memory_garden` | 1600×1200 | (800,1040) | 0 | 1 | 5 |
| `lantern_field` | 1920×1280 | (140,1150) | 1 | 0 | 7 |
| `star_path` | 2048×1024 | (120,520) | 1 | 0 | 8 |
| `starfall_village` | 1920×1280 | (80,640) | 1 | 0 | 5 |
| `eternal_garden` | 1920×1408 | (960,1340) | 0 | 0 | 4 |
| `dermaga` | 1920×1088 | (70,425) | 1 | 3 | 4 |
| `hutan_bisik` | 2560×1920 | (1280,1850) | 3 | 4 | 5 |
| `bukit_bintang` | 1920×1280 | (70,620) | 1 | 2 | 5 |
| `gua_kristal` | 1280×960 | (640,880) | 1 | 2 | 7 |

## Plaza Kota — `plaza`
- Spawn: `[960, 640]`; bounds `1920×1280`
- Walls: 7 rectangle; ellipses: 1; prop runtime: 129.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|
| `plaza_to_park` | `[0, 660, 18, 90]` | `taman_kota` | `[1880,700]` |
| `plaza_to_street` | `[1902, 660, 18, 90]` | `jalan_kota` | `[65,511]` |
| `plaza_to_lake` | `[905, 1262, 110, 18]` | `riverside` | `[960,60]` |
| `door_arland_house` | `[338, 426, 44, 16]` | `arland_room` | `[608,773]` |
| `door_sofia_house` | `[938, 426, 44, 16]` | `sofia_room` | `[609,775]` |
| `door_cafe` | `[1538, 426, 44, 16]` | `cafe` | `[400,270]` |

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|
| `fountain` | `[960,836]` | 56 |
| `notice` | `[1300,492]` | 56 |
| `bike` | `[230,490]` | 56 |
| `behind` | `[960,210]` | 56 |

Interaksi main story pada map ini: **14**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|
| `PRO_MEET` | `meet` | `[1090,600]` | 62 |
| `PRO_BOOK` | `book` | `[1160,890]` | 64 |
| `C01_MURAL` | `mural` | `[420,716]` | 64 |
| `C01_MURAL` | `mural` | `[420,716]` | 64 |
| `C02_FREE` | `f2_sari` | `[1420,610]` | 70 |
| `C02_FREE` | `f2_bed1` | `[1060,860]` | 56 |
| `C02_FREE` | `f2_bed2` | `[480,540]` | 56 |
| `C02_FREE` | `f2_bed3` | `[260,660]` | 56 |
| `C02_FREE` | `f2_sari_done` | `[1420,610]` | 70 |
| `C03_FREE` | `f3_buah` | `[760,660]` | 64 |
| `C03_FREE` | `f3_buku` | `[820,980]` | 64 |
| `C03_FREE` | `f3_gelang` | `[1250,760]` | 64 |
| `C03_A_INGREDIENTS` | `honey` | `[1420,610]` | 64 |
| `C05_FREE` | `f5_card` | `[1220,500]` | 60 |

## Taman Kota — `taman_kota`
- Spawn: `[1840, 705]`; bounds `1920×1408`
- Walls: 58 rectangle; ellipses: 0; prop runtime: 163.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|
| `park_to_forest` | `[900, 0, 120, 18]` | `hutan_bisik` | `[1280,1850]` |
| `park_to_plaza` | `[1902, 650, 18, 110]` | `plaza` | `[60,705]` |

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|
| `pond` | `[640,580]` | 56 |
| `gazebo_e` | `[1500,476]` | 56 |
| `old_tree` | `[1700,724]` | 56 |

Interaksi main story pada map ini: **24**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|
| `C02_FREE` | `f2_dito` | `[1100,540]` | 64 |
| `C02_FREE` | `f2_hide1` | `[420,430]` | 56 |
| `C02_FREE` | `f2_hide2` | `[1660,880]` | 56 |
| `C02_FREE` | `f2_hide3` | `[240,880]` | 56 |
| `C02_DATE` | `gazebo` | `[1500,470]` | 64 |
| `C03_A_INGREDIENTS` | `mint` | `[240,880]` | 64 |
| `C03_PICNIC` | `picnic` | `[1520,1060]` | 64 |
| `C04_A_PARK` | `meet4` | `[1500,470]` | 64 |
| `C04_S_PARK` | `gazebo4` | `[1500,470]` | 64 |
| `C04_S_MEET` | `meet4` | `[1000,490]` | 64 |
| `C04_V26_RECONCILE` | `v26_c04_gazebo` | `[1500,470]` | 65 |
| `C04_V26_RECONCILE` | `v26_c04_pond` | `[640,570]` | 65 |
| `C04_V26_VOW` | `v26_c04_vow` | `[1000,490]` | 70 |
| `C05_FREE` | `f5_lantern1` | `[1440,560]` | 56 |
| `C05_FREE` | `f5_lantern2` | `[720,620]` | 56 |
| `C05_FREE` | `f5_lantern3` | `[1300,1110]` | 56 |
| `C05_FREE` | `f5_lantern4` | `[1640,780]` | 56 |
| `C05_S_POND` | `portal_pond` | `[640,570]` | 70 |
| `EPI_SARI_CLOSURE` | `q_sari_closure` | `[1000,490]` | 80 |
| `EPI_FEST` | `fest_raka` | `[1360,560]` | 64 |
| `EPI_FEST` | `fest_melati` | `[1180,700]` | 64 |
| `EPI_FEST` | `fest_juna` | `[880,500]` | 64 |
| `EPI_FEST` | `fest_udin` | `[360,660]` | 64 |
| `EPI_FEST_LEPAS` | `fest_release` | `[640,570]` | 70 |

## Tepi Danau — `riverside`
- Spawn: `[960, 70]`; bounds `1920×1088`
- Walls: 42 rectangle; ellipses: 0; prop runtime: 94.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|
| `lake_to_pier` | `[1902, 560, 18, 100]` | `dermaga` | `[70,425]` |
| `lake_to_plaza` | `[905, 0, 110, 18]` | `plaza` | `[960,1210]` |

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|
| `lake` | `[600,690]` | 56 |

Interaksi main story pada map ini: **2**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|
| `C02_SUNSET` | `pier` | `[1220,840]` | 60 |
| `C05_A_PIER` | `portal_pier` | `[1220,840]` | 60 |

## Kafe Senja — `cafe`
- Spawn: `[400, 270]`; bounds `960×640`
- Walls: 4 rectangle; ellipses: 0; prop runtime: 21.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|
| `cafe_out` | `[370, 222, 60, 14]` | `plaza` | `[1560,460]` |
| `cafe_to_kitchen` | `[830, 222, 60, 14]` | `dapur` | `[599,777]` |

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|
| `cafe_case` | `[380,340]` | 56 |
| `cafe_shelf` | `[700,324]` | 56 |

Interaksi main story pada map ini: **6**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|
| `C01_PUZZLE` | `symbols` | `[480,494]` | 66 |
| `C02_TO_CAFE` | `date` | `[840,560]` | 64 |
| `C03_S_DECOR` | `lights` | `[210,300]` | 70 |
| `C04_A_CAFE` | `raka4` | `[210,300]` | 70 |
| `C04_S_CAFE` | `raka4` | `[210,300]` | 70 |
| `C05_FREE` | `f5_raka` | `[210,300]` | 70 |

## Memory Garden — `memory_garden`
- Spawn: `[800, 1040]`; bounds `1600×1200`
- Walls: 4 rectangle; ellipses: 0; prop runtime: 106.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|
| `mg_crystal` | `[330,484]` | 56 |

Interaksi main story pada map ini: **4**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|
| `PRO_SHARDS` | `shard_1` | `[270,770]` | 64 |
| `PRO_SHARDS` | `shard_2` | `[1330,770]` | 64 |
| `PRO_SHARDS` | `shard_3` | `[800,1090]` | 64 |
| `PRO_PORTAL` | `portal` | `[800,400]` | 80 |

## Lantern Field — `lantern_field`
- Spawn: `[140, 1150]`; bounds `1920×1280`
- Walls: 5 rectangle; ellipses: 0; prop runtime: 100.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|
| `lantern_to_village` | `[1902, 240, 18, 120]` | `starfall_village` | `[60,640]` |

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|

Interaksi main story pada map ini: **8**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|
| `C04_LIGHTS` | `light_listen` | `[560,1010]` | 64 |
| `C04_LIGHTS` | `light_honest` | `[1420,360]` | 64 |
| `C04_PUZZLE` | `shrine` | `[960,800]` | 80 |
| `C05_S_SPARKS` | `spark1` | `[420,1020]` | 64 |
| `C05_S_SPARKS` | `spark2` | `[900,860]` | 64 |
| `C05_S_SPARKS` | `spark3` | `[1300,900]` | 64 |
| `C05_S_SPARKS` | `spark4` | `[1180,300]` | 64 |
| `C05_S_SHRINE` | `shrine5` | `[960,800]` | 80 |

## Star Path — `star_path`
- Spawn: `[120, 520]`; bounds `2048×1024`
- Walls: 6 rectangle; ellipses: 0; prop runtime: 53.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|
| `star_to_village` | `[2030, 470, 18, 110]` | `starfall_village` | `[60,640]` |

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|

Interaksi main story pada map ini: **6**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|
| `C05_A_STARS` | `stone1` | `[380,330]` | 64 |
| `C05_A_STARS` | `stone2` | `[700,750]` | 64 |
| `C05_A_STARS` | `stone3` | `[1020,360]` | 64 |
| `C05_A_STARS` | `stone4` | `[1340,770]` | 64 |
| `C05_A_STARS` | `stone5` | `[1660,400]` | 64 |
| `C05_A_COMPASS` | `compass` | `[1020,470]` | 64 |

## Starfall Village — `starfall_village`
- Spawn: `[80, 640]`; bounds `1920×1280`
- Walls: 5 rectangle; ellipses: 0; prop runtime: 97.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|
| `village_to_lantern` | `[0, 590, 18, 100]` | `lantern_field` | `[1860,300]` |

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|

Interaksi main story pada map ini: **13**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|
| `C05_MEET` | `meet5` | `[880,640]` | 64 |
| `C05_STARMAP` | `starmap` | `[960,726]` | 72 |
| `C05_V26_A_SURVEY` | `v26_a_clue_1` | `[960,1030]` | 70 |
| `C05_V26_A_SURVEY` | `v26_a_clue_2` | `[960,470]` | 70 |
| `C05_V26_A_SURVEY` | `v26_a_clue_3` | `[960,760]` | 70 |
| `C05_V26_A_KEY` | `v26_a_key` | `[960,1030]` | 72 |
| `C05_V26_S_NOTES` | `v26_s_note_1` | `[960,470]` | 70 |
| `C05_V26_S_NOTES` | `v26_s_note_2` | `[960,1030]` | 70 |
| `C05_V26_S_NOTES` | `v26_s_note_3` | `[960,760]` | 70 |
| `C05_V26_S_COMPOSE` | `v26_s_compose` | `[960,1030]` | 72 |
| `C05_V26_NIGHT_TALK` | `v26_night_talk` | `[960,1030]` | 75 |
| `C05_V26_STARGAZE` | `v26_stargaze` | `[960,760]` | 72 |
| `C05_Q_ECHO` | `q_echo` | `[960,1030]` | 72 |

## Eternal Garden — `eternal_garden`
- Spawn: `[960, 1340]`; bounds `1920×1408`
- Walls: 19 rectangle; ellipses: 0; prop runtime: 131.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|

Interaksi main story pada map ini: **16**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|
| `C06_PETALS` | `petal1` | `[420,870]` | 64 |
| `C06_PETALS` | `petal2` | `[1500,1040]` | 64 |
| `C06_PETALS` | `petal3` | `[960,1210]` | 64 |
| `C06_Q_A_TRACES` | `q_a_1` | `[420,870]` | 68 |
| `C06_Q_A_TRACES` | `q_a_2` | `[1500,1040]` | 68 |
| `C06_Q_A_TRACES` | `q_a_3` | `[960,660]` | 68 |
| `C06_Q_S_TRACES` | `q_s_1` | `[960,660]` | 68 |
| `C06_Q_S_TRACES` | `q_s_2` | `[1500,1040]` | 68 |
| `C06_Q_S_TRACES` | `q_s_3` | `[420,870]` | 68 |
| `C06_Q_A_CIPHER` | `q_a_cipher` | `[960,500]` | 78 |
| `C06_Q_S_PAGES` | `q_s_pages` | `[960,660]` | 78 |
| `C06_Q_REVEAL` | `q_reveal` | `[960,500]` | 80 |
| `C06_LETTER` | `letter_a` | `[840,660]` | 64 |
| `C06_LETTER` | `letter_s` | `[1080,660]` | 64 |
| `C06_TREE` | `tree` | `[960,500]` | 80 |
| `C06_FINAL` | `pages` | `[960,520]` | 80 |

## Dermaga Danau — `dermaga`
- Spawn: `[70, 425]`; bounds `1920×1088`
- Walls: 71 rectangle; ellipses: 0; prop runtime: 98.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|
| `pier_to_lake` | `[0, 380, 18, 90]` | `riverside` | `[1860,610]` |

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|
| `pier_boat` | `[1000,760]` | 56 |
| `pier_hut` | `[1460,494]` | 56 |
| `pier_water` | `[960,945]` | 56 |

Interaksi main story pada map ini: **1**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|
| `C01_SUNSET` | `pierend` | `[960,930]` | 60 |

## Hutan Bisik — `hutan_bisik`
- Spawn: `[1280, 1850]`; bounds `2560×1920`
- Walls: 138 rectangle; ellipses: 0; prop runtime: 468.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|
| `forest_to_cave` | `[474, 238, 52, 16]` | `gua_kristal` | `[640,880]` |
| `forest_to_park` | `[1220, 1902, 120, 18]` | `taman_kota` | `[960,70]` |
| `forest_to_hill` | `[2542, 360, 18, 80]` | `bukit_bintang` | `[70,620]` |

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|
| `hb_ring` | `[1280,470]` | 56 |
| `hb_tent` | `[1110,1130]` | 56 |
| `hb_falls` | `[1820,160]` | 56 |
| `hb_stairs` | `[560,600]` | 56 |

Interaksi main story pada map ini: **0**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|

## Bukit Bintang — `bukit_bintang`
- Spawn: `[70, 620]`; bounds `1920×1280`
- Walls: 23 rectangle; ellipses: 0; prop runtime: 129.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|
| `hill_to_forest` | `[0, 580, 18, 80]` | `hutan_bisik` | `[2500,400]` |

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|
| `bb_edge` | `[900,962]` | 56 |
| `bb_obs` | `[1100,592]` | 56 |

Interaksi main story pada map ini: **0**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|

## Gua Kristal — `gua_kristal`
- Spawn: `[640, 880]`; bounds `1280×960`
- Walls: 143 rectangle; ellipses: 0; prop runtime: 16.

| Portal ID | Rect `[x,y,w,h]` | Destinasi | Arrival `[tx,ty]` |
|---|---|---|---|
| `cave_to_forest` | `[580, 942, 120, 18]` | `hutan_bisik` | `[500,320]` |

| Examine ID | Titik `[x,y]` | Radius |
|---|---|---:|
| `gk_pond` | `[700,640]` | 56 |
| `gk_wall` | `[380,470]` | 56 |

Interaksi main story pada map ini: **0**.

| Step | Trigger ID | Titik `[x,y]` | Radius |
|---|---|---|---:|
