#!/usr/bin/env python3
"""Story Overhaul 3.1, narrative completion pass.

Run AFTER apply_story_overhaul_v464.py. Preserves all existing quest IDs, flags,
save schema, routes, original side quests, final canon and asset files.
Idempotent: every new scene/step is addressed by a stable ID; action arrays
are rebuilt from anchored story steps, never appended repeatedly.
"""
import json
from pathlib import Path
import sys
# python -I omits the script directory; explicitly load bundled sibling generator.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_story_overhaul_v464 import L, lines, scene, choice, action, interact, step

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'android/assets/data'


def require_interact(steps, step_id, interaction):
    found=[i for i in steps[step_id]['interactables'] if i['id']==interaction]
    if len(found)!=1: raise RuntimeError('Unexpected quest structure: '+step_id+'/'+interaction)
    return found[0]


def run():
    story=json.loads((DATA/'story.json').read_text(encoding='utf-8'))
    quests=json.loads((DATA/'quests.json').read_text(encoding='utf-8'))
    book=json.loads((DATA/'memory_book.json').read_text(encoding='utf-8'))
    steps={s['id']:s for s in quests['steps']}
    for sid in ('C04_V26_VOW','C05_MEET','C06_FINAL','EPI_FEST_LEPAS'):
        if sid not in steps: raise RuntimeError('Missing canon quest: '+sid)
    for sid in ('V464-C04-A-LATE','V464-C05-REPAIR','V464-C06-EMPTY-SEAT'):
        if sid not in story['scenes']: raise RuntimeError('Run v464 patch before v465: '+sid)

    story['meta']['storyOverhaul']='3.1 - The Promise We Almost Forgot / The Empty Seat (complete emotional progression)'
    story['meta']['storyOverhaulVersion']='4.6.5'
    story['meta']['requiresRebuildOrder']=['tools/build_content.py','tools/apply_v463_cinematic.py',
                                           'tools/apply_story_overhaul_v464.py','tools/apply_story_completion_v465.py']
    # Chapter 4 now includes consequences that cannot be fixed by one cutscene.
    scene(story,'V465-C04-NOT-YET','Belum Selesai Karena Satu Maaf','C04','shared',[
        L('narrator','Hujan berhenti. Namun Arland dan Sofia belum otomatis kembali seperti sebelum acara galeri.'),
        L('sofia','Aku mau kita pelan-pelan dulu. Aku masih belum sanggup pura-pura semua baik-baik aja.', 'serius'),
        L('arland','Boleh. Aku tetap di sini, tanpa nuntut kamu langsung memaafkan.', 'serius'),
        L('narrator','Buku kenangan membiarkan halaman kursi itu terbuka. Tidak ada tombol untuk menghapusnya.')],
          flags=['V465_REPAIR_INTRO'])
    scene(story,'V465-C04-A-GALLERY-RETURN','Arland Kembali ke Galeri','C04','arland',[
        L('narrator','Arland kembali ke galeri tanpa membawa proyektor atau hadiah.'),
        L('arland','Aku selalu nyangka membantu berarti memperbaiki sesuatu. Kemarin aku sampai lupa hadir.'),
        L('narrator','Ia mengangkat satu kursi dan membantu merapikan galeri tanpa menunggu pujian.'),
        L('laras','Sofia bekerja keras buat acara ini. Rasanya sedih kalau orang yang ia nantikan nggak ada.'),
        L('arland','Iya. Aku nggak bisa mengganti hari itu. Aku cuma mau belajar lebih peka.')],
          [choice('Dengarkan cerita orang yang hadir','V465_A_LISTEN',[
              L('arland','Boleh ceritain bagian presentasi Sofia yang aku lewatkan?', 'serius'),
              L('laras','Dia sempat gemetar, tapi tetap menyelesaikan ceritanya. Dia berani, Land.')]),
           choice('Tulis permintaan maaf tanpa alasan','V465_A_LETTER',[
              L('arland','Aku mau tulis satu surat. Bukan buat minta dia cepat lupa, tapi biar aku nggak mengulanginya.'),
              L('narrator','Arland menyimpan surat itu di samping tiket galeri.')]),
           choice('Susun ulang kursi untuk acara berikutnya','V465_A_WORK',[
              L('narrator','Arland mengatur tempat duduk tanpa mengharapkan kedatangannya dianggap istimewa.'),
              L('arland','Lain kali aku mau datang lebih awal. Bukan demi dilihat, tapi buat hadir.')])],
          flags=['V465_A_REFLECTED'])
    scene(story,'V465-C04-S-GALLERY-RETURN','Sofia Tidak Menghapus Sketsa','C04','sofia',[
        L('narrator','Sofia kembali ke galeri ketika ruangan sudah sepi. Ia membuka halaman kursi kosong.'),
        L('sofia','Aku bisa bangga karena berani presentasi, sekaligus kecewa karena kursinya kosong.'),
        L('narrator','Ia menggeser pensilnya ke halaman sebelah. Tidak ada kewajiban untuk menutupi gambar pertama.')],
          [choice('Gambar kursi kedua, untuk hari baru','V465_S_DRAW_NEW',[
              L('sofia','Aku pengen punya gambar baru. Bukan buat mengganti yang lama.', 'senyum'),
              L('narrator','Sebuah bangku dengan dua tempat duduk muncul di halaman sebelah.')]),
           choice('Tulis apa yang sebenarnya dibutuhkan','V465_S_SPEAK_NEED',[
              L('sofia','Yang aku butuh bukan kejutan besar. Aku butuh kamu tanya dan hadir.'),
              L('narrator','Sofia menulis kalimat itu agar tidak lagi menyembunyikannya.')]),
           choice('Berikan diri sendiri waktu untuk tenang','V465_S_TIME',[
              L('sofia','Aku boleh menunggu sampai kata-kataku nggak lagi terasa berat.'),
              L('narrator','Ia duduk beberapa menit, mendengar suara galeri yang mulai sunyi.')])],
          flags=['V465_S_REFLECTED'])
    scene(story,'V465-C04-SECOND-TALK','Percakapan yang Tidak Dipaksakan','C04','shared',[
        L('narrator','Beberapa waktu kemudian mereka duduk di taman. Tidak langsung berpegangan tangan seperti biasa.'),
        L('arland','Aku tahu maaf nggak bikin kursi itu tiba-tiba terisi, Sof.'),
        L('sofia','Aku masih sedih kalau ingat. Tapi aku seneng kamu nggak maksa semuanya langsung selesai.'),
        L('arland','Aku pengen ngerti apa yang kamu perlukan lain kali. Aku mau dengerin.'),
        L('sofia','Aku butuh kita ngasih kabar, bukan saling menebak. Dan aku bakal coba bilang kalau aku kecewa.'),
        L('narrator','Angin lewat. Kali ini mereka memberi ruang pada jeda, bukan terburu-buru mengisinya.')],
         [choice('Sepakati untuk saling mengabari','V465_PLAN_UPDATE',[
             L('arland','Kalau rencana berubah, aku bakal bilang secepatnya.'),
             L('sofia','Aku juga. Biar kita nggak perlu menebak lagi.', 'lega')]),
          choice('Dengarkan satu cerita yang terlewat','V465_PLAN_LISTEN',[
             L('arland','Kamu mau cerita dari awal, bagian yang nggak sempat aku dengar?'),
             L('sofia','Mau. Tapi jangan buru-buru cari solusi dulu, ya.', 'senyum')]),
          choice('Buat rencana kecil untuk hari berikutnya','V465_PLAN_SMALL',[
             L('sofia','Besok jalan sebentar tanpa kejutan macam-macam aja, ya?'),
             L('arland','Iya. Aku datang buat bersama kamu.', 'senyum')])],
         flags=['V465_REPAIR_DONE'])
    # Chapter 5 requires actual shared actions; don't hand out trust just by hearing dialogue.
    scene(story,'V465-C05-A-LISTEN','Arland Mendengar Lagi','C05','arland',[
        L('narrator','Dalam pantulan jembatan, Arland melihat pertunjukan yang ia lewatkan.'),
        L('arland','Sofia berani meskipun aku nggak ada di sana. Aku harus mengakui keberaniannya, bukan mengasihani dirinya.'),
        L('sofia','Aku seneng kamu sekarang mau tahu, bukan cuma bilang maaf.', 'lega')],
          flags=['V465_STAR_LISTEN'])
    scene(story,'V465-C05-S-LISTEN','Sofia Membiarkan Dirinya Didengar','C05','sofia',[
        L('sofia','Aku juga belajar kalau pura-pura nggak apa-apa bikin kita sama-sama jauh.'),
        L('arland','Kamu nggak harus menahan semuanya demi aku, Sof.', 'serius'),
        L('sofia','Aku mau kamu tahu aku berhasil presentasi, dan aku masih sedih kamu nggak ada.')],
          flags=['V465_STAR_LISTEN'])
    scene(story,'V465-C05-SHARED-STEP','Satu Langkah yang Nyata','C05','shared',[
        L('narrator','Di antara lampu bintang yang mati, keduanya menemukan sebuah bangku kayu yang belum selesai dibuat.'),
        L('sofia','Kalau kita kerjakan sama-sama, mungkin nggak perlu sempurna hari ini.'),
        L('arland','Kita kerjain pelan-pelan. Aku nggak pergi duluan.', 'senyum'),
        L('narrator','Dua lentera di dekat bangku menyala. Tidak ada satu pihak yang harus mengerjakan semuanya sendiri.')],
         flags=['V465_STAR_COOPERATE'])
    scene(story,'V465-C05-PROMISE-PAID','Bukti Sebelum Kata-Kata','C05','shared',[
        L('narrator','Memory Book memperlihatkan kursi kosong itu, lalu sebuah bangku yang baru selesai mereka kerjakan.'),
        L('arland','Dulu aku pikir semuanya harus aku beresin sendiri.'),
        L('sofia','Sekarang kita bisa bilang kalau butuh bantuan. Nggak perlu saling menebak.'),
        L('narrator','Tidak semua luka hilang, tetapi mulai ada ruang untuk kenangan berikutnya.')],
          flags=['V465_PROMISE_PROVEN'])
    scene(story,'V465-C06-AFTER-EMPTY','Dua Gambar di Halaman yang Sama','C06','shared',[
        L('narrator','Halaman pertama memperlihatkan kursi kosong yang tak pernah benar-benar mereka lupakan.'),
        L('narrator','Di sampingnya ada gambar bangku yang mereka perbaiki bersama di Memory Realm.'),
        L('sofia','Aku nggak mau menghapus gambar yang pertama.'),
        L('arland','Kita juga nggak perlu. Kita cukup kasih tempat buat yang berikutnya.'),
        L('sofia','Makasih udah belajar hadir, Land. Aku juga belajar cerita kalau ada yang sakit.'),
        L('narrator','Buku itu menutup halaman tanpa menghapus satu garis pun.')])
    scene(story,'V465-C06-WITHOUT-PROOF','Halaman yang Masih Belajar','C06','shared',[
        L('narrator','Tidak semua kenangan sudah pulih. Di antara lembar-lembar yang berwarna masih ada satu bagian pudar.'),
        L('arland','Aku belum selalu bisa ngelakuin yang terbaik. Tapi aku mau terus belajar.'),
        L('sofia','Kita masih punya banyak hari. Kita bisa saling dengar pelan-pelan.')])
    scene(story,'V465-EPI-LAKE','Tempat Duduk untuk Hari Berikutnya','EPI','shared',[
        L('narrator','Setelah kredit, sebuah bangku di tepi danau menyimpan dua bekas tapak sepatu kecil.'),
        L('sofia','Kalau ada hari yang berat lagi, kita bakal gimana?'),
        L('arland','Kita ngobrol. Dan kalau belum siap, kita kasih waktu. Nggak perlu pura-pura sempurna.'),
        L('sofia','Oke. Aku juga akan bilang kalau ada yang mau kuceritakan.'),
        L('narrator','Dua orang itu kembali berjalan. Halaman kosongnya masih menunggu hal-hal baik yang belum mereka kenal.')],
          flags=['V465_EPILOG_MEMORY'])
    # Insert the follow-up segment between the old rain narrative and Chapter 5.
    vow=require_interact(steps,'C04_V26_VOW','v26_c04_vow')
    old=vow['actions']
    if any(a.get('do')=='chapterEnd' and a.get('chapter')=='C04' for a in old):
        original_exit=old[next(i for i,x in enumerate(old) if x.get('do')=='chapterEnd' and x.get('chapter')=='C04'):]
    else:
        # Re-running this generator: use stable original contract, not a stale tail.
        original_exit=[action('chapterEnd',chapter='C04'),action('companion',on=False),
            action('warp',area='$ROOM',x=480,y=440,dir='down'),action('chapterCard',chapter='C05'),
            action('scene',id='C05-FREE@$ROUTE'),action('step',id='C05_FREE')]
    assert original_exit[0]['do']=='chapterEnd'
    vow['actions']=[x for x in old if x.get('do')=='cine'][:1]+[
        action('scene',id='V26-C04-VOW'),action('scene',id='V465-C04-NOT-YET'),
        action('if',when={'route':'arland'},then=[action('step',id='C04_V465_A_REFLECT')],
               otherwise=[action('step',id='C04_V465_S_REFLECT')])]
    # Re-entering the Gallery is a playable act (must physically travel there).
    quests['steps']=[x for x in quests['steps'] if not x['id'].startswith(('C04_V465_','C05_V465_'))]
    quests['steps'].append(step('C04_V465_A_REFLECT','C04',
        ('Kembali ke galeri dan dengarkan cerita yang terlewat','Pikirkan kembali hari di galeri'),
        [interact('v465_a_gallery','galeri_komunitas',290,410,'Lihat kursi yang dulu kosong',[
            action('music',id='cinema_gallery_empty'),action('scene',id='V465-C04-A-GALLERY-RETURN'),
            action('flag',id='V465_REFLECTED'),action('step',id='C04_V465_SECOND_TALK')],
            radius=120,route='arland')]))
    quests['steps'].append(step('C04_V465_S_REFLECT','C04',
        ('Kembali ke galeri untuk mengenang','Gambar dan ceritakan yang belum sempat dikatakan'),
        [interact('v465_s_gallery','galeri_komunitas',290,410,'Buka lagi buku sketsa',[
            action('music',id='cinema_gallery_empty'),action('scene',id='V465-C04-S-GALLERY-RETURN'),
            action('flag',id='V465_REFLECTED'),action('step',id='C04_V465_SECOND_TALK')],
            radius=120,route='sofia')]))
    quests['steps'].append(step('C04_V465_SECOND_TALK','C04',
        ('Bicaralah lagi ketika sama-sama siap','Temui pasangan di taman untuk bicara tanpa terburu-buru'),
        [interact('v465_second_talk','taman_kota',1000,490,'Duduk dan bicarakan hari berikutnya',
         [action('music',id='cinema_gallery_repair'),
          action('cine',cmds=[{'c':'bars','on':True,'t':0.4},
                              {'c':'shot','focus':'couple','zoom':1.16,'frame':'intimate','t':1.1,'bars':False},
                              {'c':'caption','text':'Beberapa Waktu Kemudian','sub':'Tidak ada maaf yang menggantikan kehadiran','t':2.4},
                              {'c':'bars','on':False,'t':0.4}]),
          action('scene',id='V465-C04-SECOND-TALK'),*original_exit],radius=100)]))
    # Proof-of-change is a real two-location/interaction task within the star village.
    meet=require_interact(steps,'C05_MEET','meet5')
    original=meet['actions']; assert any(a.get('do')=='scene' and a.get('id')=='V464-C05-REPAIR' for a in original)
    meet['actions']=[a for a in original if not (a.get('do')=='step' and a.get('id') in ('C05_STARMAP','C05_V465_PROOF'))]
    meet['actions'].append(action('step',id='C05_V465_PROOF'))
    proof=[
       interact('v465_star_listen','starfall_village',880,640,'Dengarkan pasangan sampai selesai',[
           action('if',when={'route':'arland'},then=[action('scene',id='V465-C05-A-LISTEN')],
                  otherwise=[action('scene',id='V465-C05-S-LISTEN')]),
           action('flag',id='V465_LISTEN_ACT'),action('count',id='v465_star_actions',add=1)],
           when={'notFlags':['V465_LISTEN_ACT']},radius=96),
       interact('v465_star_together','starfall_village',960,726,'Bangun bangku kenangan bersama',[
           action('scene',id='V465-C05-SHARED-STEP'),
           action('flag',id='V465_TOGETHER_ACT'),action('count',id='v465_star_actions',add=1)],
           when={'notFlags':['V465_TOGETHER_ACT']},radius=100)]
    quests['steps'].append(step('C05_V465_PROOF','C05',
       ('Dengarkan pasangan dan kerjakan sesuatu bersama','Dengarkan pasangan dan perbaiki bangku bersama'),
       proof,complete={'counter':'v465_star_actions','count':2,'actions':[
           action('scene',id='V465-C05-PROMISE-PAID'),action('step',id='C05_STARMAP')]}))
    # The old ending and old chapter flags are preserved exactly: only conditional
    # detail insertions are made, never an alternate canon ending.
    pages=require_interact(steps,'C06_FINAL','pages')
    acts=[x for x in pages['actions'] if not (x.get('do')=='if' and x.get('when',{}).get('flags')==['V465_PROMISE_PROVEN'])]
    i=next(i for i,a in enumerate(acts) if a.get('do')=='scene' and a.get('id')=='C06-X01')
    acts.insert(i,action('if',when={'flags':['V465_PROMISE_PROVEN']},
                          then=[action('scene',id='V465-C06-AFTER-EMPTY')],
                          otherwise=[action('scene',id='V465-C06-WITHOUT-PROOF')]))
    pages['actions']=acts
    # Epilogue recalled in the actual canon festival exit, not a duplicate ending.
    release=require_interact(steps,'EPI_FEST_LEPAS','fest_release')
    acts=[x for x in release['actions'] if x.get('id')!='V465-EPI-LAKE']
    i=next((i for i,a in enumerate(acts) if a.get('do')=='chapterEnd'),len(acts))
    acts.insert(i,action('scene',id='V465-EPI-LAKE'))
    release['actions']=acts
    # Recoverable gallery memory collectible, with original editable pixel-art icon.
    book['entries']=[x for x in book['entries'] if x.get('id')!='v465_second_chance']
    book['entries'].append({'id':'v465_second_chance','chapter':'C05','route':'shared',
        'type':'fictional_memory','unlock':'V465_PROMISE_PROVEN','icon':'items/v465_bench_memory.png',
        'title':'Dua Tempat Duduk, Dua Suara',
        'text':'Mereka kembali belajar hadir, mendengarkan, dan saling membantu. Bangku baru tidak menghapus kursi yang pernah kosong.'})
    book.setdefault('items',{})['v465_bench_memory']={
        'name':'Sketsa Bangku Berdua','icon':'items/v465_bench_memory.png',
        'desc':'Mereka memilih menyimpan kenangan yang sulit dan menuliskan hari yang lebih hangat di sebelahnya.'}
    for file,data in [('story.json',story),('quests.json',quests),('memory_book.json',book)]:
        (DATA/file).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Story completion applied: ',len(story['scenes']),'scenes,',len(quests['steps']),'steps,',len(book['entries']),'memories')

if __name__=='__main__':run()
