#!/usr/bin/env python3
"""Story Overhaul 3.3 — Chapter 1 first pass, data-first and idempotent.

Applies only to C01 nodes in existing story/quest data, plus additive Memory Book
entries. Preserves original scene IDs, 23 maps and the unmodified save schema.
Run this AFTER the existing v4.6.6 story generators when rebuilding content.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'android/assets/data'
TAG = 'V467_C01'


def L(s, t, e='neutral'):
    return {'s':s,'e':e,'t':t}


def choice(text, flag, a, s):
    return {'text':text,'flags':[flag],'byRoute':{
        'arland':[L(x,y) for x,y in a], 'sofia':[L(x,y) for x,y in s]}}


def scene(story, sid, route, title, dialogue, place='perpustakaan'):
    story['scenes'][sid]={
        'title':title,'route':route,'chapter':'C01','location':place,
        'trigger':'Quest story choice','lines':dialogue,'choices':[],'flags':[],
        'note':'Story Overhaul 3.3: two perspectives, no new canon ending.'}


def action(do, **kw):
    return {'do':do,**kw}


def branch_when(flag, then, otherwise):
    return action('if',when={'flags':[flag]},then=then,**{'else':otherwise})


def apply():
    story=json.loads((DATA/'story.json').read_text(encoding='utf-8'))
    quests=json.loads((DATA/'quests.json').read_text(encoding='utf-8'))
    book=json.loads((DATA/'memory_book.json').read_text(encoding='utf-8'))
    steps={x['id']:x for x in quests['steps']}
    assert all(k in steps for k in ('C01_NOTE','C01_PUZZLE','C01_LARAS2','C01_SUNSET','C01_RIVERSIDE'))
    assert all(k in story['scenes'] for k in ('C01-X02','C01-A01','C01-S01','C01-PIER@arland','C01-PIER@sofia'))

    story['meta']['chapter1Overhaul']='v4.6.7: A Letter with Two Voices'
    story['meta']['chapter1ChoiceContract']='3 branches x 2 playable perspectives; old save steps fall back to C01_RIVERSIDE'

    # Original scenes still exist under exactly their old IDs. Narrative choices
    # are non-punitive; both sides matter and preserve the established route.
    a=story['scenes']['C01-A01']
    a['lines']=[L('narrator','Sinar pagi mengenai kertas yang pernah dilipat Arland berkali-kali.'),
        L('arland','Catatan ini ada di antara buku. Aku ingat tempatnya, tapi rasanya masih gugup.','malu'),
        L('arland','Kadang aku lebih gampang ngasih sesuatu daripada bilang kenapa aku membuatnya.'),
        L('narrator','Dua baris kosong di belakang catatan menunggu kata-kata yang belum dipilih.')]
    a['choices']=[choice('Bilang terus terang kalau aku gugup','V467_C01_INTRO_A_HONEST',
        [('arland','Kalau aku gugup, aku bakal bilang. Nggak perlu pura-pura selalu yakin.')],
        [('arland','Kalau aku gugup, aku bakal bilang. Nggak perlu pura-pura selalu yakin.')]),
        choice('Simpan dulu sampai aku tahu cara menjelaskannya','V467_C01_INTRO_A_WAIT',
        [('arland','Aku masih perlu waktu. Tapi nanti aku mau cerita dengan caraku sendiri.')],
        [('arland','Aku masih perlu waktu. Tapi nanti aku mau cerita dengan caraku sendiri.')])]
    s=story['scenes']['C01-S01']
    s['lines']=[L('narrator','Sofia memutar pembatas buku bergambar bintang di tangannya.'),
        L('sofia','Waktu kita ketemu kemarin, Arland tersenyum terus. Aku jadi ikut senang.','senyum'),
        L('sofia','Tapi aku juga gugup. Itu bagian yang nggak kelihatan di foto.'),
        L('narrator','Di tepi pembatas buku ada ruang yang cukup untuk satu kalimat.')]
    s['choices']=[choice('Aku juga mau berani bilang kalau sedang khawatir','V467_C01_INTRO_S_HONEST',
        [('sofia','Mungkin nggak harus selalu kelihatan baik-baik saja.')],
        [('sofia','Mungkin nggak harus selalu kelihatan baik-baik saja.')]),
        choice('Aku mau menulis perasaanku dulu','V467_C01_INTRO_S_WAIT',
        [('sofia','Kalau aku belum siap bicara, aku bisa mulai dengan menulis.')],
        [('sofia','Kalau aku belum siap bicara, aku bisa mulai dengan menulis.')])]
    story['scenes']['C01-A02']['lines']=[
        L('arland','Lihat, bagian yang paling terang itu bunga. Aku yakin ini petunjuk pertama.'),
        L('sofia','Aneh. Dari tempatku berdiri, justru bintangnya yang kelihatan lebih dulu.'),
        L('arland','Aku belum tentu salah. Tapi mungkin kamu juga nggak salah.','penasaran'),
        L('narrator','Saat mereka bergeser, mural yang sama seolah menyusun ulang warnanya.')]
    story['scenes']['C01-S02']['lines']=[
        L('sofia','Dari sini simbol bintangnya paling jelas. Aku baca bintang, buku, bunga.'),
        L('arland','Aku malah lihat bunga, buku, bintang. Aku sempat yakin cuma satu urutan.'),
        L('sofia','Kita tulis dua-duanya. Kalau berbeda, mungkin itu bagian petunjuknya.','penasaran'),
        L('narrator','Bayangan pada mural bergeser, tetapi gambar di dinding tidak berubah.')]
    story['scenes']['C01-X01']['lines']=[
        L('narrator','Di sudut kafe, kotak kayu menyimpan tiga keping simbol.'),
        L('arland','Aku lihat bunga lebih dulu. Sofia lihat bintang.'),
        L('sofia','Kalau begitu kita coba urutan masing-masing, bukan saling memaksa.'),
        L('arland','Siapa pun yang berhasil membuka kotak, petunjuknya tetap punya kita berdua.'),
        L('narrator','Tangan mereka berhenti di atas kotak sesaat sebelum teka-teki dimulai.')]
    story['scenes']['C01-X02']['lines']=[
        L('narrator','Tiga simbol itu membuka kotak. Sebuah surat tua terselip di dalamnya.'),
        L('sofia','Hurufnya kecil banget. Sini, kita baca sama-sama.'),
        L('arland','Dua sisi, satu tempat pulang...'),
        L('narrator','Dari sisi Arland, tinta di tepi kiri membentuk bunga. Dari sisi Sofia, tinta yang sama seperti sebuah bintang.'),
        L('sofia','Kalimatnya sama, tapi aku melihat hal yang berbeda. Kok bisa?','bingung'),
        L('arland','Aku mau tahu apa yang kamu lihat, bukan cuma membuktikan kalau versiku benar.'),
        L('narrator','Satu baris yang semula terbaca perlahan memudar. Bukan hilang seluruhnya: seperti menunggu suara lain.'),
        L('sofia','Jangan ditutup dulu. Ada sesuatu yang belum kita pahami.'),
        L('narrator','Pada bagian belakang surat tertera cap Arsip Nomor Tujuh, Perpustakaan Kota.'),
        L('arland','Kita cari asal capnya. Tapi nanti di tepi danau, aku pengen ngobrol tentang surat ini.'),
        L('sofia','Iya. Kita bawa dua ceritanya, bukan cuma satu.')]
    story['scenes']['C01-X02']['choices']=[
        choice('Dengarkan dulu apa yang dilihat pasangan','V467_C01_CHOOSE_LISTEN',
            [('arland','Sof, nanti ceritain bagian yang kamu lihat, ya. Aku nggak mau menyela.'),
             ('sofia','Mau. Aku juga ingin tahu kenapa kamu melihat bunga.')],
            [('sofia','Land, boleh aku cerita dulu sebelum kita menyimpulkan?'),
             ('arland','Boleh. Aku mau dengerin sampai selesai.')]),
        choice('Simpan dua versi surat di catatan bersama','V467_C01_CHOOSE_RECORD',
            [('arland','Kita tulis dua versi ini berdampingan. Biar nanti nggak ada yang tertukar.'),
             ('sofia','Aku suka. Aku bisa menggambar bintangnya di sebelah bungamu.')],
            [('sofia','Aku mau gambar yang kamu lihat, terus kamu tulis yang kulihat.'),
             ('arland','Deal. Dua halaman, satu cerita.')]),
        choice('Selidiki mengapa satu kalimat memudar','V467_C01_CHOOSE_TRACE',
            [('arland','Kalimat yang hilang itu aneh. Aku mau cari tahu sumbernya.'),
             ('sofia','Boleh, asal kita nggak lupa membicarakan apa yang kita rasakan.')],
            [('sofia','Hurufnya seperti hilang setelah kita saling berbeda pendapat.'),
             ('arland','Kita cari petunjuknya. Jangan buru-buru menyimpulkan.')])]

    for route in ('arland','sofia'):
        key='C01-ARC-2@'+route
        lines=story['scenes'][key]['lines']
        lines=[x for x in lines if x.get('t')!='Kalian sudah memegang dua bagian ceritanya. Jangan sampai satu suaranya tertinggal.']
        lines.insert(-1,L('laras','Kalian sudah memegang dua bagian ceritanya. Jangan sampai satu suaranya tertinggal.'))
        story['scenes'][key]['lines']=lines

    # Complete Story Bible C01-A03 / C01-S03: these used to be absent from the
    # actual main route. Both now include a two-interaction playable errand.
    scene(story,'V467-C01-A03-ASK','arland','Buku Pesanan yang Tertukar',[
        L('raka','Land, boleh bantu? Buku pesanan untuk meja depan hilang. Semua orang sudah menunggu.'),
        L('arland','Aku bantu cari, Kak. Terakhir dilihat di mana?'),
        L('raka','Tadi kubawa dekat meja sebelah jendela, lalu tertukar dengan album foto.'),
        L('sofia','Aku bantu lihat dari sini. Kamu cari judul di sampulnya, ya.'),
        L('arland','Oke. Kita kerjain pelan-pelan, biar nggak malah salah ambil.')],place='cafe')
    scene(story,'V467-C01-A03-FOUND','arland','Catatan Kecil Milik Kak Raka',[
        L('arland','Ini bukunya. Ternyata tertutup album foto. Ada dua tanda untuk pesanan yang sama.'),
        L('raka','Iya, dua orang pesan satu meja. Aku lupa menulis keduanya, jadi kelihatan salah.'),
        L('sofia','Untung kamu nggak buru-buru menghapus tanda yang satu lagi.'),
        L('arland','Aku baru sadar catatan yang terlihat beda bisa sama-sama penting.'),
        L('narrator','Kak Raka menghadiahkan secarik catatan kosong yang bisa dipakai Arland menyimpan petunjuk.')],place='cafe')
    scene(story,'V467-C01-S03-ASK','sofia','Surat Rara yang Terselip',[
        L('rara','Kak, aku kehilangan surat dari teman. Aku yakin tadi kuselipkan dekat buku menu.'),
        L('sofia','Kita cari bareng. Suratnya ada tanda khusus?'),
        L('rara','Ada gambar bintang kecil. Aku takut teman itu mengira aku tidak menjaga tulisannya.'),
        L('arland','Aku lihat di dekat rak. Kamu ingat bagian mejanya, Ra?'),
        L('sofia','Kita nggak perlu panik. Ceritain dari awal, nanti kita cocokkan.')],place='cafe')
    scene(story,'V467-C01-S03-FOUND','sofia','Yang Tidak Sengaja Terlupakan',[
        L('sofia','Ketemu! Ternyata surat itu terselip di balik daftar menu.'),
        L('rara','Makasih, Kak. Aku sempat takut kehilangan cerita yang belum sempat kubaca.'),
        L('sofia','Kalau sesuatu itu penting, kita boleh minta orang lain bantu menjaga.'),
        L('arland','Dan nggak perlu malu bilang kalau kita sedang khawatir.'),
        L('narrator','Rara memberikan pembatas bergambar bintang kecil sebagai tanda terima kasih.')],place='cafe')

    new_cafe_steps=[
        {'id':'V467_C01_CAFE_HELP','chapter':'C01','quest':'Q_V467_C01_PERSONAL_HELP',
         'objective':{'arland':'Bantu Kak Raka menemukan buku pesanan yang tertukar',
                      'sofia':'Bantu Rara menemukan surat bertanda bintang'},
         'interactables':[
            {'id':'v467_cafe_ask_a','area':'cafe','x':350,'y':418,'r':98,'route':'arland',
             'label':'Tanya Kak Raka soal buku pesanan',
             'actions':[action('scene',id='V467-C01-A03-ASK'),
                        action('step',id='V467_C01_CAFE_A_FIND')]},
            {'id':'v467_cafe_ask_s','area':'cafe','x':620,'y':425,'r':98,'route':'sofia',
             'label':'Bantu Rara mencari surat',
             'actions':[action('scene',id='V467-C01-S03-ASK'),
                        action('step',id='V467_C01_CAFE_S_FIND')]}]},
        {'id':'V467_C01_CAFE_A_FIND','chapter':'C01','quest':'Q_V467_C01_PERSONAL_HELP',
         'objective':{'arland':'Cari buku pesanan di dekat jendela kafe',
                      'sofia':'Cari buku pesanan di dekat jendela kafe'},
         'interactables':[{'id':'v467_cafe_find_a','area':'cafe','x':185,'y':486,'r':98,
             'route':'arland','label':'Ambil buku pesanan yang tertukar',
             'actions':[action('scene',id='V467-C01-A03-FOUND'),
                        action('item',id='v467_c01_barista_note'),
                        action('flag',id='V467_C01_A03_DONE'),
                        action('sfx',id='page'),action('step',id='C01_PUZZLE')]}]},
        {'id':'V467_C01_CAFE_S_FIND','chapter':'C01','quest':'Q_V467_C01_PERSONAL_HELP',
         'objective':{'arland':'Cari surat yang terselip di rak menu',
                      'sofia':'Cari surat yang terselip di rak menu'},
         'interactables':[{'id':'v467_cafe_find_s','area':'cafe','x':755,'y':485,'r':98,
             'route':'sofia','label':'Ambil surat Rara',
             'actions':[action('scene',id='V467-C01-S03-FOUND'),
                        action('item',id='v467_c01_rara_bookmark'),
                        action('flag',id='V467_C01_S03_DONE'),
                        action('sfx',id='page'),action('step',id='C01_PUZZLE')]}]}
    ]
    for step_data in new_cafe_steps:steps[step_data['id']]=step_data
    # Guarantee that the two people involved are visibly present during the
    # dedicated quest, rather than speaking from empty space. Extend existing
    # deterministic NPC schedules with conditional, last-priority entries.
    actor_positions={
        'raka':{'at':'00:00','area':'cafe','x':207,'y':273,'dir':'down',
            'wander':0,'when':{'route':'arland',
                'steps':['V467_C01_CAFE_HELP','V467_C01_CAFE_A_FIND']},
            'v467':'C01-cafe-personal'},
        'rara':{'at':'00:00','area':'cafe','x':561,'y':483,'dir':'left',
            'wander':0,'when':{'route':'sofia',
                'steps':['V467_C01_CAFE_HELP','V467_C01_CAFE_S_FIND']},
            'v467':'C01-cafe-personal'}}
    for actor in quests['townNpcs']:
        if actor['id'] in actor_positions:
            actor['schedule']=[row for row in actor.get('schedule',[])
                               if row.get('v467')!='C01-cafe-personal']
            actor['schedule'].append(actor_positions[actor['id']])

    cafe=steps['C01_CAFE']['enterArea']
    new_actions=[a for a in cafe['actions'] if not (a.get('do')=='step' and a.get('id') in
                  ('C01_PUZZLE','V467_C01_CAFE_HELP'))]
    new_actions.append(action('step',id='V467_C01_CAFE_HELP'))
    cafe['actions']=new_actions

    # The follow-up scene and each playable interaction have meaningful,
    # protagonist-specific responses rather than merely renaming characters.
    arc={
      'LISTEN':{
        'title':'Yang Tidak Kelihatan', 'area':(880,430), 'button':'Dengarkan pasangan di sisi rak',
        'objective':{'arland':'Dengarkan Sofia menjelaskan simbol yang ia lihat','sofia':'Ceritakan pada Arland mengapa bintang itu penting'},
        'item':'v467_c01_listening', 'flag':'V467_C01_RESULT_LISTEN'},
      'RECORD':{
        'title':'Dua Catatan, Satu Surat','area':(346,485),'button':'Buat catatan bersama di meja baca',
        'objective':{'arland':'Tulis dua versi petunjuk bersama Sofia','sofia':'Gambar dua sisi surat bersama Arland'},
        'item':'v467_c01_double_page','flag':'V467_C01_RESULT_RECORD'},
      'TRACE':{
        'title':'Tinta yang Memudar','area':(720,593),'button':'Periksa bekas tinta di rak',
        'objective':{'arland':'Cari sumber tinta pudar pada rak buku','sofia':'Amati huruf yang memudar tanpa menghapusnya'},
        'item':'v467_c01_fading_ink','flag':'V467_C01_RESULT_TRACE'}}
    scripts={
      'LISTEN':{
        'arland':[L('arland','Aku selalu lihat simbol bunga dulu. Mungkin karena aku masih ingat bunga kertas yang kubuat.'),
            L('sofia','Aku melihat bintang dulu. Semalam aku juga mimpi tentang cahaya di buku itu.'),
            L('arland','Jadi buat kamu, bintang bukan sekadar petunjuk. Itu terasa dekat sama sesuatu yang kamu alami.'),
            L('sofia','Iya. Makasih nggak langsung bilang aku salah.','lega'),
            L('narrator','Arland menyimpan cerita Sofia tanpa mencoba mengubah urutan simbolnya.')],
        'sofia':[L('sofia','Aku lihat bintang dulu karena semalam aku memimpikannya. Waktu itu aku agak takut.'),
            L('arland','Aku cuma lihat bunga karena aku baru membuat bunga kertas buat kamu.'),
            L('sofia','Oh... jadi kita sama-sama melihat sesuatu yang dekat sama perasaan kita.'),
            L('arland','Aku senang kamu cerita. Aku nggak akan ngetawain mimpimu.'),
            L('narrator','Sofia lega karena ceritanya didengar sebelum ia harus menjelaskan semuanya.')],
      },
      'RECORD':{
        'arland':[L('arland','Aku gambar bunganya. Kamu gambar bintangnya, boleh?'),
            L('sofia','Boleh. Tapi aku mau tulis juga perasaan waktu pertama kali melihatnya.'),
            L('arland','Benar. Kalau cuma menulis urutan, kita malah kehilangan ceritanya.'),
            L('narrator','Dua tulisan tangan berbeda berbagi satu halaman tanpa saling menutupi.'),
            L('sofia','Kita nggak harus sama untuk menyimpan ini bersama.','senyum')],
        'sofia':[L('sofia','Aku gambar bintangnya, Land. Di bawahnya aku tulis kenapa aku langsung ingat mimpiku.'),
            L('arland','Aku tulis bagian bunga. Bukan buat membantah, ya.'),
            L('sofia','Aku tahu. Justru kalau ada dua catatan, nanti kita bisa saling ingetin.'),
            L('narrator','Sofia menyelipkan kertas itu ke dalam buku, dengan kedua tanda tetap terlihat.'),
            L('arland','Jangan lupa tulis tanggalnya. Hari yang aneh tapi menyenangkan.')],
      },
      'TRACE':{
        'arland':[L('arland','Ada bekas tinta yang hilang dari kertas ini. Tapi jejak tekanannya masih ada.'),
            L('sofia','Kayak ada orang yang sudah menulis, tapi belum selesai bicara.'),
            L('arland','Aku hampir mau langsung mencari cara memperbaikinya.'),
            L('sofia','Cari boleh. Tapi kita juga perlu mendengar apa yang ditinggalkan.'),
            L('narrator','Jejak tinta memperlihatkan satu kata: pulang. Sisanya masih menjadi misteri.')],
        'sofia':[L('sofia','Di bawah cahaya, bekas kalimat ini seperti ada dua lapisan.'),
            L('arland','Kamu bisa lihat huruf yang aku nggak bisa lihat?'),
            L('sofia','Sebagiannya saja. Tapi aku nggak mau mengarang sisanya.'),
            L('arland','Bagus. Kita simpan petunjuknya sampai tahu cerita lengkapnya.'),
            L('narrator','Sofia menandai halaman itu dengan bintang kecil; kata pulang tetap terbaca samar.')],
      }}
    echo={
      'LISTEN':{
        'arland':[L('arland','Sof, aku baru sadar. Kalau tadi aku nggak dengerin, aku cuma akan ingat bunga.'),
            L('sofia','Dan kalau aku nggak cerita, kamu nggak akan tahu kenapa aku lihat bintang.'),
            L('arland','Kalau nanti ada yang kamu pikirkan, aku mau denger dari awal.'),
            L('narrator','Suara air menutup jeda dengan lembut. Dua versi cerita tetap mereka bawa pulang.')],
        'sofia':[L('sofia','Makasih udah mau denger mimpi anehku tanpa bilang itu cuma mimpi.'),
            L('arland','Aku justru senang kamu cerita. Aku jadi ngerti kenapa bintangnya penting.'),
            L('sofia','Kalau nanti aku diam, mungkin aku masih cari kata-kata. Boleh tanya pelan-pelan?'),
            L('arland','Boleh. Aku bakal coba nggak langsung nebak.'),
            L('narrator','Sofia menyandarkan tangannya di papan dermaga. Untuk sementara, ia tak perlu menyimpan semua perasaannya sendiri.')],
      },
      'RECORD':{
        'arland':[L('arland','Catatan kita ada dua tulisan tangan. Aku suka kelihatan bedanya.'),
            L('sofia','Yang satu kecil-kecil, yang satu agak miring. Tapi dua-duanya muat.'),
            L('arland','Nanti kalau kita beda ingatan, kita bisa buka ini lagi.'),
            L('narrator','Arland menyimpan halaman itu hati-hati di tempat yang mudah ia temukan.')],
        'sofia':[L('sofia','Land, lihat kertas ini. Gambar bintangnya nggak menutup bungamu.'),
            L('arland','Justru jadi lebih lengkap, ya.'),
            L('sofia','Aku pengen kita punya tempat buat cerita yang kadang beda.'),
            L('narrator','Sofia menulis satu kata terakhir di bawah gambar: bersama.')],
      },
      'TRACE':{
        'arland':[L('arland','Aku belum menemukan siapa yang menghapus baris surat itu.'),
            L('sofia','Nggak apa-apa. Kita nggak harus dapat semua jawabannya hari ini.'),
            L('arland','Benar. Tapi aku mau ingat bagaimana rasanya saat pertama kali lihat tinta itu.'),
            L('narrator','Jejak tinta di atas kertas berkilau sesaat, lalu tenang kembali.')],
        'sofia':[L('sofia','Bagian surat yang hilang itu membuatku penasaran, tapi juga sedikit takut.'),
            L('arland','Takut kita akan lupa?'),
            L('sofia','Mungkin. Aku cuma mau tahu apa yang sebaiknya kita jaga.'),
            L('arland','Kalau belum ada jawabannya, kita cari sama-sama.'),
            L('narrator','Di permukaan air, sebuah bintang kecil memantul lalu menghilang.')],
      }}
    intro_echo={
      'arland':{'HONEST':[L('arland','Tadi pagi aku bilang aku gugup. Sekarang masih, tapi nggak perlu disembunyikan.'),
                                    L('sofia','Aku lebih suka kamu cerita daripada memaksakan diri kelihatan tenang.')],
                'WAIT':[L('arland','Aku belum nemu semua kata yang pas buat jelasin perasaanku.'),
                                 L('sofia','Nggak apa-apa. Kita masih punya waktu buat nyari bareng.')]},
      'sofia':{'HONEST':[L('sofia','Tadi aku berjanji mau lebih jujur kalau ada yang mengganggu.'),
                                   L('arland','Makasih. Aku juga mau belajar dengerin tanpa buru-buru jawab.')],
               'WAIT':[L('sofia','Aku sempat menulis semua yang bikin aku gugup.'),
                                L('arland','Kalau nanti mau kamu ceritain, aku ada di sini.')]}}

    for k,v in arc.items():
        for r in ('arland','sofia'):
            scene(story, f'V467-C01-{k}@{r}',r,v['title'],scripts[k][r])
            scene(story, f'V467-C01-PIER-{k}@{r}',r,'Senja yang Berbeda',echo[k][r],place='dermaga')
        scene_id='V467_C01_'+k
        quest_step={
           'id':scene_id,'chapter':'C01','quest':'Q_V467_C01_TWO_SIDES',
           'objective':v['objective'],
           'interactables':[{ 'id':'v467_c01_'+k.lower(),'area':'perpustakaan',
               'x':v['area'][0],'y':v['area'][1],'r':90,'label':v['button'],
               'actions':[action('cine',cmds=[
                     {'c':'bars','on':True,'t':0.25},
                     {'c':'shot','focus':'couple','frame':'intimate','zoom':1.17,'t':1.0,'bars':False},
                     {'c':'fx','kind':'glow','on':'player','t':2.2},
                     {'c':'bars','on':False,'t':0.35}]),
                  action('scene',id=f'V467-C01-{k}@$ROUTE'),
                  action('item',id=v['item']),action('flag',id=v['flag']),
                  action('sfx',id='page'),action('step',id='C01_RIVERSIDE')]}]}
        steps[scene_id]=quest_step

    for r in ('arland','sofia'):
        for typ in ('HONEST','WAIT'):
            scene(story,f'V467-C01-INTRO-{r.upper()}-{typ}',r,'Kalimat yang Disimpan',intro_echo[r][typ],place='dermaga')

    # Replace the static letter reveal with an authored cinematic beat. Preserve
    # every original puzzle outcome and insert only a non-blocking mood cue.
    puzzle_step=steps['C01_PUZZLE']
    puzzle=next(it for it in puzzle_step['interactables'] if it['id']=='symbols')
    acts=[a for a in puzzle['actions'] if a.get('v467')!='letter-reveal']
    idx=next(i for i,a in enumerate(acts) if a.get('do')=='scene' and a.get('id')=='C01-X02')
    additions=[
        {'do':'music','id':'cinema_two_sides_v467','v467':'letter-reveal'},
        {'do':'cine','cmds':[
            {'c':'bars','on':True,'t':.35},
            {'c':'shot','focus':'couple','zoom':1.12,'frame':'intimate','t':1.1,'bars':False},
            {'c':'fx','kind':'book','on':'player','t':2.4},
            {'c':'wait','t':.35},
            {'c':'bars','on':False,'t':.35}], 'v467':'letter-reveal'}]
    puzzle['actions']=acts[:idx]+additions+acts[idx:]

    # Bu Laras's original conversation and the branch-selection action remain
    # entirely deterministic even on v4.6.6 saves that lack the new choice flags.
    laras=steps['C01_LARAS2']
    x=next(it for it in laras['interactables'] if it['id']=='laras2')
    x['actions']=[action('scene',id='C01-ARC-2@$ROUTE'),
        branch_when('V467_C01_CHOOSE_LISTEN',[action('step',id='V467_C01_LISTEN')],
           [branch_when('V467_C01_CHOOSE_RECORD',[action('step',id='V467_C01_RECORD')],
             [branch_when('V467_C01_CHOOSE_TRACE',[action('step',id='V467_C01_TRACE')],
                [action('step',id='C01_RIVERSIDE')])])])]

    # A branch receives a cinematic callback before the existing canonical pier
    # sequence. Existing pier cutscene, chapter completion, and route transition
    # remain unchanged. Older saves skip these additions without softlock.
    pier=next(it for it in steps['C01_SUNSET']['interactables'] if it['id']=='pierend')
    previous=[a for a in pier['actions'] if a.get('v467')!='chapter1']
    initial=[branch_when('V467_C01_RESULT_'+k,[action('scene',id=f'V467-C01-PIER-{k}@$ROUTE')],[])
             for k in ('LISTEN','RECORD','TRACE')]
    initial.extend([
        branch_when('V467_C01_INTRO_A_HONEST',[action('scene',id='V467-C01-INTRO-ARLAND-HONEST')],[]),
        branch_when('V467_C01_INTRO_A_WAIT',[action('scene',id='V467-C01-INTRO-ARLAND-WAIT')],[]),
        branch_when('V467_C01_INTRO_S_HONEST',[action('scene',id='V467-C01-INTRO-SOFIA-HONEST')],[]),
        branch_when('V467_C01_INTRO_S_WAIT',[action('scene',id='V467-C01-INTRO-SOFIA-WAIT')],[])
    ])
    for a in initial:a['v467']='chapter1'
    pier['actions']=initial+previous

    quests['steps']=[x for x in quests['steps'] if x['id'] not in set(arc)] # unrelated old IDs preserved
    quests['steps']=[x for x in quests['steps'] if not x['id'].startswith('V467_C01_')]
    idx=next(i for i,step in enumerate(quests['steps']) if step['id']=='C01_CAFE')+1
    quests['steps'][idx:idx]=new_cafe_steps
    i=next(i for i,s in enumerate(quests['steps']) if s['id']=='C01_LARAS2')+1
    quests['steps'][i:i]=[steps['V467_C01_'+k] for k in ('LISTEN','RECORD','TRACE')]

    for k,icon,name,desc in (
       ('v467_c01_listening','items/v467_c01_listening.png','Benang Percakapan','Dua perasaan dari satu kejadian yang didengarkan tanpa dipotong.'),
       ('v467_c01_double_page','items/v467_c01_double_page.png','Catatan Dua Sisi','Tulisan bunga dan gambar bintang berbagi satu halaman.'),
       ('v467_c01_fading_ink','items/v467_c01_fading_ink.png','Jejak Tinta','Bekas tulisan yang hilang menyisakan satu kata: pulang.')
    ):
        book['items'][k]={'name':name,'icon':icon,'desc':desc}
    book['entries']=[x for x in book['entries'] if not x.get('id','').startswith('v467_c01_')]
    book['items']['v467_c01_barista_note']={
        'name':'Catatan Pesanan Kak Raka','icon':'items/v467_c01_double_page.png',
        'desc':'Buku pesanan yang tidak sengaja menghapus satu nama dari meja bersama.'}
    book['items']['v467_c01_rara_bookmark']={
        'name':'Pembatas Bintang Rara','icon':'items/v467_c01_fading_ink.png',
        'desc':'Tanda terima kasih untuk surat penting yang hampir hilang di kafe.'}
    book['entries'].extend([
        {'id':'v467_c01_barista_a','chapter':'C01','route':'arland',
         'type':'fictional_memory','unlock':'V467_C01_A03_DONE',
         'icon':'items/v467_c01_double_page.png','title':'Satu Meja, Dua Nama',
         'text':'Arland membantu Kak Raka menemukan buku pesanan yang tertukar dan tidak menghapus salah satu nama.'},
        {'id':'v467_c01_rara_s','chapter':'C01','route':'sofia',
         'type':'fictional_memory','unlock':'V467_C01_S03_DONE',
         'icon':'items/v467_c01_fading_ink.png','title':'Surat yang Hampir Hilang',
         'text':'Sofia membantu Rara menemukan surat bertanda bintang yang belum sempat dibaca.'}
    ])

    for r in ('arland','sofia'):
        for k,v in arc.items():
            book['entries'].append({
              'id':f'v467_c01_{r}_{k.lower()}',
              'chapter':'C01','route':r,'type':'optional_story_branch',
              'unlock':v['flag'],'icon':book['items'][v['item']]['icon'],
              'title':('Arland' if r=='arland' else 'Sofia')+' — '+v['title'],
              'text':{
                  'LISTEN':{'arland':'Arland berhenti mencoba menjelaskan semuanya dan benar-benar mendengarkan alasan Sofia melihat bintang.',
                            'sofia':'Sofia berani menyampaikan mengapa bintang dari mimpinya membuatnya gugup.'},
                  'RECORD':{'arland':'Arland menuliskan versinya tanpa menutupi gambar Sofia.',
                            'sofia':'Sofia menggambar kedua sisi, menjaga agar tulisan Arland tetap terlihat.'},
                  'TRACE':{'arland':'Arland menemukan bekas huruf yang hilang, tetapi memilih tidak mengarang jawabannya.',
                           'sofia':'Sofia melihat dua lapisan pada tinta dan memilih menyimpan petunjuk dengan hati-hati.'}
                }[k][r]})

    for name,payload in (('story.json',story),('quests.json',quests),('memory_book.json',book)):
        (DATA/name).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('C01 Overhaul applied: 3 decision branches, 2 perspectives, legacy-safe route, 6 memories.')

if __name__=='__main__':apply()
