# v2.7 Living World: dijalankan oleh tools/build_content.py setelah _snap dibuat.
WORLD_EVENTS = []
WORLD_EVENTS.append(dict(id='pagi_plaza', title='Bunga di Pagi Plaza', area='plaza', x=A('plaza', 'bench_w')[0], y=A('plaza', 'bench_w')[1], hours=['07:00', '10:00'], minChapter='C02', weather=['cerah', 'berawan'], route=None, coins=3, affection=2, companion=True))
WORLD_EVENTS.append(dict(id='kafe_catatan', title='Pesan di Alas Cangkir', area='cafe', x=A('cafe', 'table_date')[0], y=A('cafe', 'table_date')[1], hours=['10:00', '14:00'], minChapter='C03', weather=[], route=None, coins=2, affection=3, companion=True))
WORLD_EVENTS.append(dict(id='ikan_pondok', title='Penjaga Kolam Koi', area='taman_kota', x=A('taman_kota', 'pond_dock')[0], y=A('taman_kota', 'pond_dock')[1], hours=['13:00', '18:00'], minChapter='C02', weather=[], route=None, coins=1, affection=3, companion=True))
WORLD_EVENTS.append(dict(id='senja_danau', title='Cahaya di Permukaan Danau', area='riverside', x=A('riverside', 'bench_e')[0], y=A('riverside', 'bench_e')[1], hours=['16:00', '19:00'], minChapter='C02', weather=['cerah', 'berawan'], route=None, coins=2, affection=4, companion=True))
WORLD_EVENTS.append(dict(id='perpustakaan_senyap', title='Buku yang Dipinjamkan', area='perpustakaan', x=A('perpustakaan', 'sofa')[0], y=A('perpustakaan', 'sofa')[1], hours=['09:00', '17:00'], minChapter='C02', weather=[], route=None, coins=0, affection=3, companion=True))
WORLD_EVENTS.append(dict(id='melati_merangkai', title='Belajar dari Bu Melati', area='toko_bunga', x=A('toko_bunga', 'counter_front')[0], y=A('toko_bunga', 'counter_front')[1], hours=['10:00', '18:00'], minChapter='C02', weather=[], route=None, coins=2, affection=2, companion=True))
WORLD_EVENTS.append(dict(id='arcade_tiket', title='Tiket yang Tertinggal', area='arcade', x=A('arcade', 'cabinets')[0], y=A('arcade', 'cabinets')[1], hours=['15:00', '22:00'], minChapter='C03', weather=[], route=None, coins=4, affection=2, companion=True))
WORLD_EVENTS.append(dict(id='halte_hujan', title='Cerita di Bawah Atap Halte', area='jalan_kota', x=A('jalan_kota', 'halte')[0], y=A('jalan_kota', 'halte')[1], hours=['11:00', '24:00'], minChapter='C04', weather=['hujan'], route=None, coins=0, affection=5, companion=True))
WORLD_EVENTS.append(dict(id='dermaga_papan', title='Nama di Papan Dermaga', area='dermaga', x=A('dermaga', 'bench')[0], y=A('dermaga', 'bench')[1], hours=['16:00', '19:00'], minChapter='C03', weather=[], route=None, coins=3, affection=3, companion=True))
WORLD_EVENTS.append(dict(id='hutan_gema', title='Gema di Hutan Bisik', area='hutan_bisik', x=A('hutan_bisik', 'camp')[0], y=A('hutan_bisik', 'camp')[1], hours=['09:00', '17:00'], minChapter='C05', weather=[], route=None, coins=0, affection=4, companion=True))
WORLD_EVENTS.append(dict(id='desa_bintang', title='Lampu Jendela Starfall', area='starfall_village', x=A('starfall_village', 'bench')[0], y=A('starfall_village', 'bench')[1], hours=['18:00', '24:00'], minChapter='C05', weather=[], route=None, coins=0, affection=4, companion=True))
WORLD_EVENTS.append(dict(id='bukit_teleskop', title='Satu Bintang yang Sama', area='bukit_bintang', x=A('bukit_bintang', 'deck')[0], y=A('bukit_bintang', 'deck')[1], hours=['19:00', '25:00'], minChapter='C03', weather=['cerah', 'berawan'], route=None, coins=0, affection=5, companion=True))
WORLD_EVENTS.append(dict(id='arlan_peta', title='Jalur Kecil untuk Dito', area='perumahan', x=A('perumahan', 'bench')[0], y=A('perumahan', 'bench')[1], hours=['09:00', '17:00'], minChapter='C03', weather=[], route='arland', coins=5, affection=3, companion=True))
WORLD_EVENTS.append(dict(id='sofia_halaman', title='Halaman untuk Bu Laras', area='perpustakaan', x=A('perpustakaan', 'table2')[0], y=A('perpustakaan', 'table2')[1], hours=['10:00', '17:00'], minChapter='C03', weather=[], route='sofia', coins=4, affection=4, companion=True))
for event in WORLD_EVENTS:
    # Posisi event harus benar-benar dapat dicapai. Peta, pintu dan collision tidak diubah.
    # Coba kandidat jarak dekat secara deterministik; tidak menghitung ulang BFS 22 peta.
    sx, sy = event['x'], event['y']
    candidates = [(sx, sy)] + [(sx + dx, sy + dy)
                               for radius in (16, 32, 48, 64, 96, 128)
                               for dx, dy in ((radius, 0), (-radius, 0), (0, radius), (0, -radius),
                                              (radius, radius), (-radius, radius), (radius, -radius), (-radius, -radius))]
    safe = next(((x, y) for x, y in candidates if not _blocked(event['area'], x, y, 6)), None)
    if safe is None: raise AssertionError('Titik event tidak aman: ' + event['id'])
    event['x'], event['y'] = safe
    event['r'] = 69
    event['scenes'] = {r: 'WE27-' + event['id'].replace('_','-').upper() + ('-A' if r == 'arland' else '-S')
                       for r in ('arland', 'sofia') if event['route'] is None or r == event['route']}
    for sc in event['scenes'].values(): assert sc in scenes, ('World Event scene tidak ada', sc)
    acts = [
        {'do': 'sfx', 'id': 'page_turn'},
        {'do': 'if', 'when': {'route': 'arland'},
         'then': [{'do': 'scene', 'id': event['scenes'].get('arland', event['scenes'].get('sofia'))}],
         'else': [{'do': 'scene', 'id': event['scenes'].get('sofia', event['scenes'].get('arland'))}]},
        {'do': 'worldEvent', 'id': event['id']},
        {'do': 'sfx', 'id': 'heart'}]
    quests['side'].append(I('WE27_' + event['id'].upper(), event['area'],
                            (event['x'], event['y']), event['title'], acts,
                            route=event['route'], r=event['r'],
                            when={'worldEventReady': event['id']}))
    ENTRIES.append(E('m_we27_' + event['id'], 'SIDE', event['route'] or 'shared',
                     'fictional_memory', 'WORLD_EVENT_' + event['id'].upper() + '_ONCE',
                     'items/memory_page.png', event['title'],
                     'Kisah dunia yang hidup pada waktu dan suasana tertentu.'))
quests['worldEvents'] = WORLD_EVENTS
# Book memakai referensi ENTRIES yang sama.
assert book['entries'] is ENTRIES
