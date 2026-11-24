# v5.4 Stair & Elevation Audit

Semua 21 platform elevasi dibaca dari `android/assets/data/maps.json` (`elevationPlatforms`). Koordinat dalam piksel dunia, y ke bawah. Tangga selalu turun ke arah selatan (naik = arah atas layar).

| Map | Platform (x,y,w,h) | Rise | Tangga x | Tangga y (atas→bawah) | Gaya | Catatan v5.4 |
|---|---|---|---|---|---|---|
| plaza | 765,450,168,92 | 26 | 821–877 | 536–620 | city | Lulus semua uji jalur |
| jalan_kota | 545,305,128,75 | 26 | 581–637 | 374–458 | city | Lulus semua uji jalur |
| taman_kota | 1085,355,168,92 | 26 | 1141–1197 | 441–525 | garden | Lulus semua uji jalur |
| riverside | 1060,490,168,92 | 26 | 1116–1172 | 576–660 | wood | Lulus semua uji jalur |
| cafe | 625,345,128,75 | 16 | 661–717 | 414–477 | cafe | Lulus semua uji jalur |
| toko_bunga | 745,280,128,75 | 16 | 781–837 | 349–412 | garden | Lulus semua uji jalur |
| arcade | 550,208,128,75 | 16 | 586–642 | 277–340 | night | Platform digeser 17 px ke atas (y 225→208). Sebelumnya kaki tangga berakhir 19 px dari mesin arcade tengah sehingga tidak bisa dilewati. |
| memory_garden | 1005,555,168,92 | 26 | 1061–1117 | 641–725 | memory | Lulus semua uji jalur |
| lantern_field | 845,340,168,92 | 26 | 901–957 | 426–510 | night | Lulus semua uji jalur |
| star_path | 1155,390,168,92 | 26 | 1211–1267 | 476–560 | star | Lulus semua uji jalur |
| starfall_village | 985,470,168,92 | 26 | 1041–1097 | 556–640 | star | Lulus semua uji jalur |
| eternal_garden | 915,545,168,92 | 26 | 971–1027 | 631–715 | memory | Lulus semua uji jalur |
| perumahan | 935,315,128,75 | 26 | 971–1027 | 384–468 | city | Lulus semua uji jalur |
| perpustakaan | 640,370,128,75 | 26 | 676–732 | 439–523 | cafe | Lulus semua uji jalur |
| dermaga | 895,225,168,92 | 26 | 951–1007 | 311–395 | wood | Pohon `tree_green` digeser 14 px ke kanan (x 1020→1034). Collider batangnya memotong sisi kanan mulut tangga sehingga pemain tersangkut saat turun. |
| hutan_bisik | 1095,765,168,92 | 26 | 1151–1207 | 851–935 | forest | Lulus semua uji jalur |
| bukit_bintang | 995,560,168,92 | 26 | 1051–1107 | 646–730 | garden | Lulus semua uji jalur |
| gua_kristal | 765,270,128,75 | 26 | 801–857 | 339–423 | crystal | Lulus semua uji jalur |
| galeri_komunitas | 350,185,128,75 | 16 | 386–442 | 254–317 | cafe | Lulus semua uji jalur |
| rain_garden | 1205,455,168,92 | 26 | 1261–1317 | 541–625 | memory | Lulus semua uji jalur |
| hall_of_tomorrow | 910,530,168,92 | 26 | 966–1022 | 616–700 | future | Lulus semua uji jalur |
