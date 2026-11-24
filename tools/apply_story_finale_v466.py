#!/usr/bin/env python3
"""v4.6.6: choice-reactive finale + postgame gallery, safe after v4.6.5 patch.

Only overwrites IDs owned by v4.6.6. A repeated run is idempotent. Existing quest,
plot, route and saved-state identifiers are never renamed or deleted.
"""
import json
from pathlib import Path
from apply_story_overhaul_v464 import L, scene, choice, action, interact

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'android/assets/data'


def add_book(book, entry):
    book['entries']=[e for e in book['entries'] if e.get('id')!=entry['id']]
    book['entries'].append(entry)


def run():
    story=json.loads((DATA/'story.json').read_text(encoding='utf-8'))
    quests=json.loads((DATA/'quests.json').read_text(encoding='utf-8'))
    book=json.loads((DATA/'memory_book.json').read_text(encoding='utf-8'))
    steps={s['id']:s for s in quests['steps']}
    for key in ('C06_FINAL','EPI_FEST_LEPAS','EPI_FREE'):
        if key not in steps: raise RuntimeError('Missing existing main-story step: '+key)
    if 'V465-C06-AFTER-EMPTY' not in story['scenes']:
        raise RuntimeError('Must apply v4.6.5 story completion first')

    story['meta']['storyOverhaul']='3.2 - The Promise We Almost Forgot / Letters of Tomorrow'
    story['meta']['storyOverhaulVersion']='4.6.6'
    story['meta']['legacyScenesRetainedForSaveCompatibility']=True
    story['meta']['requiresRebuildOrder']=[
        'tools/build_content.py','tools/apply_v463_cinematic.py',
        'tools/apply_story_overhaul_v464.py','tools/apply_story_completion_v465.py',
        'tools/apply_story_finale_v466.py']

    # The two choices are genuinely different viewpoints, not a route name swap.
    scene(story,'V466-C06-A-LETTER','Surat yang Tidak Harus Sempurna','C06','arland',[
        L('narrator','Arland menemukan kembali bunga kertas yang dulu ia lipat berulang kali. Lipatannya tetap tidak rata.'),
        L('arland','Dulu aku pikir kalau sesuatu nggak sempurna, aku harus bikin ulang sampai bagus.'),
        L('sofia','Aku masih simpan bunga itu karena kamu yang bikin, bukan karena lipatannya rapi.', 'senyum'),
        L('arland','Aku pernah terlalu sibuk memperbaiki semuanya sampai lupa hadir. Aku mau menuliskan apa yang kupelajari.'),
        L('narrator','Di belakang bunga itu, Arland menambahkan satu kalimat untuk hari-hari yang belum datang.')],
        [choice('Aku akan datang dan mengabari kalau rencana berubah','V466_A_PRESENT',[
            L('arland','Kalau kamu perlu aku hadir, aku nggak mau lagi menggantinya dengan kejutan.'),
            L('sofia','Makasih. Aku akan cerita terus terang kalau aku butuh ditemani.', 'lega')]),
         choice('Aku akan mendengarkan sebelum mencoba memperbaiki','V466_A_LISTEN',[
            L('arland','Aku mau dengerin sampai selesai, bahkan ketika aku belum tahu jawabannya.'),
            L('sofia','Kamu nggak harus punya jawaban buat semua hal. Duduk di sini juga cukup.', 'senyum')]),
         choice('Kita boleh salah dan tetap belajar bersama','V466_A_LEARN',[
            L('arland','Aku nggak bisa janji kita nggak salah lagi. Aku cuma bisa janji buat terus belajar.'),
            L('sofia','Itu justru janji yang bisa kita jalanin bareng.', 'lega')])],
        flags=['V466_A_LETTER'],location='eternal_garden')

    scene(story,'V466-C06-S-LETTER','Catatan Sofia untuk Hari Berikutnya','C06','sofia',[
        L('narrator','Sofia membuka sketsa kursi kosong. Ia tak merobeknya. Di halaman sebelah tergambar bangku yang pernah mereka bangun bersama.'),
        L('sofia','Dulu aku kira kalau aku bilang sedang kecewa, hari itu bakal jadi lebih buruk.'),
        L('arland','Aku malah baru ngerti setelah kamu berani cerita. Maaf aku terlambat dengerinnya.'),
        L('sofia','Aku juga belajar kalau perasaanku boleh punya tempat. Aku mau menulis satu kalimat di halaman ini.'),
        L('narrator','Sofia menyiapkan catatan yang akan ia baca kembali bila suatu hari kata-katanya terasa berat.')],
        [choice('Aku akan mengatakan saat aku membutuhkanmu','V466_S_TELL',[
            L('sofia','Kalau aku butuh ditemani, aku akan bilang. Bukan berharap kamu bisa baca pikiranku.'),
            L('arland','Aku akan dengar. Kalau aku bingung, aku akan tanya.', 'lega')]),
         choice('Aku akan memberi kita ruang, tanpa memendam semuanya','V466_S_SPACE',[
            L('sofia','Aku boleh perlu waktu sendiri. Setelahnya, kita tetap bisa bicara.'),
            L('arland','Aku nggak akan memaksa kamu buru-buru merasa baik-baik saja.', 'senyum')]),
         choice('Aku akan merayakan keberanian kecilku sendiri','V466_S_PROUD',[
            L('sofia','Aku bangga waktu itu berhasil berdiri di depan orang-orang, bahkan saat kursinya kosong.'),
            L('arland','Aku juga bangga sama kamu. Itu pencapaianmu, bukan sesuatu yang harus aku perbaiki.', 'senyum')])],
        flags=['V466_S_LETTER'],location='eternal_garden')

    scene(story,'V466-C06-SHARED-PAGE','Dua Surat, Satu Halaman Kosong','C06','shared',[
        L('narrator','Di antara kenangan mereka kini ada dua catatan yang ditulis tanpa menyalahkan siapa pun.'),
        L('sofia','Kalau nanti ada hari yang susah, kita nggak perlu pura-pura semuanya indah.'),
        L('arland','Kalau ada yang sulit diceritakan, kita bisa mulai dari satu kalimat dulu.'),
        L('narrator','Mereka menyelipkan kedua catatan ke dalam buku. Lembar berikutnya berkilau, menunggu untuk dibuka bersama.')])

    for route,who,entries in (
        ('a','arland',[
            ('PRESENT','Hari yang kita pilih','Aku akan mengingat bukan cuma tempatnya, tapi alasan aku datang.'),
            ('LISTEN','Duduk tanpa solusi','Saat Sofia bicara, Arland tidak perlu memperbaiki semuanya.'),
            ('LEARN','Berani tak sempurna','Mereka tidak berhenti belajar setelah mengucapkan maaf.')]),
        ('s','sofia',[
            ('TELL','Kata yang berani diucapkan','Sofia menyadari kebutuhan dan harapannya juga pantas didengarkan.'),
            ('SPACE','Ruang untuk kembali','Mereka bisa memberi jarak sejenak tanpa saling meninggalkan.'),
            ('PROUD','Gambar yang tidak dihapus','Sofia merayakan keberanian presentasinya, bukan hanya kehadiran orang lain.')])):
        for suffix,title,content in entries:
            scene(story,f'V466-EPI-{route.upper()}-{suffix}',title,'EPI',who,[
                L('narrator',content),
                L('arland' if route=='a' else 'sofia',
                  'Hari ini aku mau ingat satu hal: kita masih bisa belajar mendengar satu sama lain.', 'senyum'),
                L('sofia' if route=='a' else 'arland',
                  'Dan kalau nanti ada yang tidak berjalan sesuai rencana, kita bisa cerita lagi.', 'lega')])

    scene(story,'V466-EPI-OLD-CHAPTER','Halaman yang Tetap Terbuka','EPI','shared',[
        L('narrator','Ada bagian perjalanan yang tidak terekam pada halaman-halaman sebelumnya.'),
        L('arland','Aku mungkin nggak ingat setiap kata, tapi aku masih ingin mendengarkan.'),
        L('sofia','Kita nggak perlu memaksa kenangan yang hilang jadi sempurna. Kita bisa mulai dari hari ini.')])
    scene(story,'V466-EPI-A-GALLERY','Arland Datang Sebelum Diminta','EPI','arland',[
        L('narrator','Arland kembali mengunjungi Galeri Komunitas. Kursi yang dulu kosong kini terisi pengunjung lain.'),
        L('arland','Aku nggak bisa mengulang presentasi itu. Tapi aku bisa datang untuk hal-hal yang penting setelahnya.'),
        L('sofia','Kamu datang bukan karena ada kejutan, kan?', 'penasaran'),
        L('arland','Aku datang karena ingin lihat apa yang kamu gambar selanjutnya.'),
        L('narrator','Kali ini mereka melihat karya-karya baru bersama. Hari yang lama tidak dihapus.')],
        flags=['V466_GALLERY_ARLAND'])
    scene(story,'V466-EPI-S-GALLERY','Sofia Menyimpan Dua Gambar','EPI','sofia',[
        L('narrator','Sofia kembali ke galeri membawa dua sketsa: kursi kosong dan bangku yang dibuat bersama.'),
        L('sofia','Aku nggak mau membuang gambar pertama. Aku juga nggak mau berhenti menggambar karenanya.'),
        L('arland','Kalau kamu mau, aku duduk di sini sambil kamu pilih tempatnya.'),
        L('sofia','Duduk aja. Nanti aku cerita kenapa aku gambar dua-duanya.', 'senyum'),
        L('narrator','Ia memajang kedua gambar berdampingan, tanpa perlu menyembunyikan yang lama.')],
        flags=['V466_GALLERY_SOFIA'])

    # Place the optional personal letter before the EXISTING canon finale, not after credits.
    pages=next(i for i in steps['C06_FINAL']['interactables'] if i['id']=='pages')
    original=pages['actions']
    original=[a for a in original if a.get('v466') is not True]
    index=next(i for i,a in enumerate(original) if a.get('do')=='scene' and a.get('id')=='C06-X01')
    finale=[dict(action('if',when={'route':'arland'},then=[action('scene',id='V466-C06-A-LETTER')],
                              otherwise=[action('scene',id='V466-C06-S-LETTER')]),v466=True),
            dict(action('scene',id='V466-C06-SHARED-PAGE'),v466=True)]
    original[index:index]=finale
    pages['actions']=original

    # Coda honors what the player actually wrote. Older saves receive a safe fallback.
    release=next(i for i in steps['EPI_FEST_LEPAS']['interactables'] if i['id']=='fest_release')
    original=[a for a in release['actions'] if a.get('v466') is not True]
    index=next(i for i,a in enumerate(original) if a.get('do')=='scene' and a.get('id')=='V465-EPI-LAKE')
    custom=[dict(action('music',id='cinema_letter_tomorrow'),v466=True)]
    for flag,sceneid in (
        ('V466_A_PRESENT','V466-EPI-A-PRESENT'),('V466_A_LISTEN','V466-EPI-A-LISTEN'),('V466_A_LEARN','V466-EPI-A-LEARN'),
        ('V466_S_TELL','V466-EPI-S-TELL'),('V466_S_SPACE','V466-EPI-S-SPACE'),('V466_S_PROUD','V466-EPI-S-PROUD')):
        custom.append(dict(action('if',when={'flags':[flag]},then=[action('scene',id=sceneid)],otherwise=[]),v466=True))
    custom.append(dict(action('if',when={'route':'arland','notFlags':['V466_A_LETTER']},
                              then=[action('scene',id='V466-EPI-OLD-CHAPTER')],otherwise=[]),v466=True))
    custom.append(dict(action('if',when={'route':'sofia','notFlags':['V466_S_LETTER']},
                              then=[action('scene',id='V466-EPI-OLD-CHAPTER')],otherwise=[]),v466=True))
    original[index:index]=custom
    release['actions']=original

    # Postgame *playable* visit: available during free roam, once per save slot.
    free=steps['EPI_FREE']
    other=[i for i in free.get('interactables',[]) if i['id']!='v466_gallery_return']
    other.append(interact('v466_gallery_return','galeri_komunitas',300,405,
             'Lihat kembali kursi dan gambar di galeri',[
                 action('music',id='cinema_letter_tomorrow'),
                 action('if',when={'route':'arland'},then=[action('scene',id='V466-EPI-A-GALLERY')],
                        otherwise=[action('scene',id='V466-EPI-S-GALLERY')]),
                 action('flag',id='V466_GALLERY_RETURN_DONE'),action('sfx',id='page')],
             when={'notFlags':['V466_GALLERY_RETURN_DONE']},radius=115))
    free['interactables']=other

    add_book(book,{'id':'v466_letter_arland','chapter':'C06','route':'arland',
                   'type':'fictional_memory','unlock':'V466_A_LETTER',
                   'icon':'items/v466_letter_arland.png','title':'Surat di Balik Bunga',
                   'text':'Arland menuliskan sesuatu untuk masa depan: hadir, mendengarkan, dan mengizinkan dirinya belajar.'})
    add_book(book,{'id':'v466_letter_sofia','chapter':'C06','route':'sofia',
                   'type':'fictional_memory','unlock':'V466_S_LETTER',
                   'icon':'items/v466_letter_sofia.png','title':'Catatan di Samping Kursi',
                   'text':'Sofia menyimpan dua gambar tanpa menutupi yang pertama. Kini ia juga berani meminta untuk didengarkan.'})
    add_book(book,{'id':'v466_gallery_return','chapter':'EPI','route':'shared',
                   'type':'optional_postgame','unlock':'V466_GALLERY_RETURN_DONE',
                   'icon':'items/v466_gallery_revisit.png','title':'Hari ketika Mereka Kembali',
                   'text':'Setelah kredit, Arland dan Sofia kembali ke galeri tanpa janji yang harus dibuktikan. Hanya ada waktu untuk melihat hari baru.'})
    for name,title,text in (
        ('v466_letter_arland','Surat di Balik Bunga','Surat Arland tentang belajar hadir ketika dibutuhkan.'),
        ('v466_letter_sofia','Catatan di Samping Kursi','Catatan Sofia tentang keberanian mengutarakan perasaan.'),
        ('v466_gallery_revisit','Hari Baru di Galeri','Kunjungan pasca-cerita yang tidak menghapus kenangan lama.')):
        book['items'][name]={'name':title,'icon':'items/'+name+'.png','desc':text}

    for name,data in [('story.json',story),('quests.json',quests),('memory_book.json',book)]:
        (DATA/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('v4.6.6 applied:',len(story['scenes']),'scenes,',len(quests['steps']),'steps,',len(book['entries']),'memories')

if __name__=='__main__':run()
