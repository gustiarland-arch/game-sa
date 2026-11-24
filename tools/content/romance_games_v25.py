"""v2.5: enam permainan Waktu Berdua (dua tipe baru). Hadiah hanya sesudah berhasil."""
ROMANCE_GAMES = [
  {'id':'memancing', 'title':'Memancing Berdua', 'minigame':'fishing', 'areas':['riverside','dermaga'], 'affection':4, 'minScore':1, 'desc':'Tarik ikan bersama di tepi danau.', 'scene':'RG-FISH'},
  {'id':'memasak', 'title':'Resep Berdua', 'minigame':'cooking', 'areas':['cafe','dapur'], 'affection':4, 'minScore':1, 'desc':'Kerjakan resep sederhana bersama.', 'scene':'RG-COOK'},
  {'id':'buket', 'title':'Merangkai Buket', 'minigame':'bouquet', 'areas':['toko_bunga'], 'affection':5, 'minScore':1, 'desc':'Pilih bunga sesuai pesanan hati.', 'scene':'RG-BOUQUET'},
  {'id':'scrapbook', 'title':'Album Cerita Kita', 'minigame':'scrapbook', 'areas':['cafe','perpustakaan','arland_room','sofia_room'], 'affection':5, 'minScore':1, 'desc':'Urutkan empat kenangan di album.', 'scene':'RG-SCRAPBOOK'},
  {'id':'bintang', 'title':'Tangkap Bintang', 'minigame':'starcatch', 'areas':['bukit_bintang','star_path'], 'affection':5, 'minScore':1, 'desc':'Bintang jatuh, satu harapan baru.', 'scene':'RG-STARS'},
  {'id':'foto', 'title':'Photobooth Berdua', 'minigame':'photobooth', 'areas':['arcade'], 'affection':4, 'minScore':1, 'desc':'Ambil foto manis yang bisa dikenang.', 'scene':'RG-PHOTO'},
]
