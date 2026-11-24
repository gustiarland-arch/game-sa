"""v1.5.0: katalog ekonomi & pekerjaan. Dieksekusi oleh tools/build_content.py.
Tidak edit JSON assets secara manual. Barang dibeli lewat layar toko dan tetap ada di Tas.
"""
SHOPS = {
 'senja': {'title': 'Kafe Senja', 'keeper': 'Kak Raka', 'goods': [
     {'item': 'kopi_senja', 'name': 'Kopi Senja', 'desc': 'Hangat dan sedikit manis.', 'price': 12},
     {'item': 'kukis_madu', 'name': 'Kukis Madu', 'desc': 'Renyan dari dapur kafe.', 'price': 16},
     {'item': 'roti_manis', 'name': 'Roti Kayu Manis', 'desc': 'Wangi untuk bekal perjalanan.', 'price': 20}]},
 'melati': {'title': 'Toko Bunga Melati', 'keeper': 'Bu Melati', 'goods': [
     {'item': 'tulip_kecil', 'name': 'Tulip Kecil', 'desc': 'Satu tangkai warna jingga.', 'price': 12},
     {'item': 'mawar_pita', 'name': 'Mawar Berpita', 'desc': 'Bunga dengan pita lembut.', 'price': 18},
     {'item': 'buket_senja', 'name': 'Buket Senja', 'desc': 'Rangkaian hangat untuk kenangan.', 'price': 25}]},
 'rini': {'title': 'Kios Bu Rini', 'keeper': 'Bu Rini', 'goods': [
     {'item': 'permen_stroberi', 'name': 'Permen Stroberi', 'desc': 'Manis kecil dalam kantong.', 'price': 8},
     {'item': 'kue_lapis_kios', 'name': 'Kue Lapis', 'desc': 'Resep keluarga Bu Rini.', 'price': 15},
     {'item': 'kartu_lucu', 'name': 'Kartu Bergambar', 'desc': 'Untuk ditulisi pesan.', 'price': 10}]},
}
JOBS = {
 'barista': {'title': 'Shift Barista', 'minigame': 'pour', 'minScore': 1, 'reward': 20},
 'perangkai': {'title': 'Merangkai Bunga', 'minigame': 'arrange_flowers', 'minScore': 1, 'reward': 22},
 'kurir': {'title': 'Antar Surat', 'minigame': '', 'minScore': 0, 'reward': 28, 'stops': ['plaza', 'jalan_kota', 'riverside']},
}
MINIGAMES['arrange_flowers'] = {
 'type': 'cooking', 'title': 'Merangkai Bunga',
 'desc': 'Pilih dan rapikan bunga dalam delapan langkah. Ketuk saat jarum masuk zona hijau.',
 'steps': ['Pilih mawar', 'Pilih tulip', 'Potong batang', 'Susun daun', 'Padukan warna', 'Ikat dengan tali', 'Beri pita', 'Rapikan buket']
}
ITEMS.update({
 'kopi_senja': ('Kopi Senja', 'items/tea_glass.png', 'Kopi hangat dari Kafe Senja.'),
 'kukis_madu': ('Kukis Madu', 'items/sandwich.png', 'Kukis renyah madu.'),
 'roti_manis': ('Roti Kayu Manis', 'items/sandwich.png', 'Roti yang harum.'),
 'tulip_kecil': ('Tulip Kecil', 'items/paper_flower.png', 'Tangkai tulip jingga.'),
 'mawar_pita': ('Mawar Berpita', 'items/bouquet.png', 'Mawar dengan pita.'),
 'buket_senja': ('Buket Senja', 'items/bouquet.png', 'Rangkaian bunga musim senja.'),
 'permen_stroberi': ('Permen Stroberi', 'items/fruit.png', 'Permen untuk menemani berjalan.'),
 'kue_lapis_kios': ('Kue Lapis', 'items/fruit.png', 'Kue lapis kios Bu Rini.'),
 'kartu_lucu': ('Kartu Bergambar', 'items/postcard.png', 'Kartu kecil untuk pesan.'),
})
# Lapak berada di interior / dekat kios eksisting, tidak mengubah peta.
ECON_AVAILABLE = {'minChapter': 'C02'}
SIDE.extend([
 I('shop_senja', 'cafe', A('cafe', 'counter'), 'Belanja di Kafe Senja', [{'do': 'shop', 'id': 'senja'}], when=ECON_AVAILABLE, r=84),
 I('job_barista', 'cafe', A('cafe', 'barista'), 'Shift barista (+20 koin)', [{'do': 'work', 'id': 'barista'}],
   when={'minChapter': 'C02', 'jobReady': 'barista', 'hours': ['08:00','21:00']}, r=74),
 I('shop_melati', 'toko_bunga', A('toko_bunga', 'counter_front'), 'Belanja Bunga', [{'do': 'shop', 'id': 'melati'}], when=ECON_AVAILABLE, r=84),
 I('job_perangkai', 'toko_bunga', A('toko_bunga', 'florist'), 'Rangkai bunga (+22 koin)', [{'do': 'work', 'id': 'perangkai'}],
   when={'minChapter': 'C02', 'jobReady': 'perangkai', 'hours': ['08:00','19:00']}, r=72),
 I('shop_rini', 'jalan_kota', A('jalan_kota', 'stall'), 'Belanja di Kios Bu Rini', [{'do': 'shop', 'id': 'rini'}], when=ECON_AVAILABLE, r=88),
 I('job_kurir_start', 'perumahan', A('perumahan', 'halte'), 'Ambil surat Pak Pos (+28 koin)', [{'do': 'deliveryStart'}],
   when={'minChapter': 'C02', 'jobReady': 'kurir', 'hours': ['07:00','19:00']}, r=88),
])
for area, target, label in [
 ('plaza', 'bench_w', 'Antar surat ke Plaza'),
 ('jalan_kota', 'bakery', 'Antar surat ke Jalan Kota'),
 ('riverside', 'bench_e', 'Antar surat ke Tepi Danau'),
]:
 SIDE.append(I('job_kurir_' + area, area, A(area, target), label,
     [{'do': 'deliveryDrop', 'address': area}],
     when={'minChapter': 'C02', 'deliveryOpen': True, 'deliveryNotDone': area}, r=82))
# Update memori setelah pekerjaan perdana masing-masing.
ENTRIES.extend([
 E('economy_barista', 'SIDE', 'shared', 'souvenir', 'JOB_BARISTA_ONCE', 'items/tea_glass.png', 'Shift Pertama', 'Secangkir teh yang disajikan dengan tangan sendiri.'),
 E('economy_florist', 'SIDE', 'shared', 'souvenir', 'JOB_PERANGKAI_ONCE', 'items/bouquet.png', 'Buket Pertama', 'Belajar merangkai kelopak satu demi satu.'),
 E('economy_kurir', 'SIDE', 'shared', 'souvenir', 'JOB_KURIR_ONCE', 'items/postcard.png', 'Surat Terkirim', 'Tiga surat sampai ke orang yang menunggunya.'),
])
