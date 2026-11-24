#!/usr/bin/env python3
"""Prologue narrative lock, playable preparation and two-view Memory Garden.
Run AFTER all v4.7.3 Epilogue patches. Deterministic/idempotent and save-safe:
legacy PRO_GIFT / PRO_SHARDS / PRO_PORTAL step IDs remain valid.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'android/assets/data'
V='V474'
def act(do,**kwargs):return {'do':do,**kwargs}
def L(w,t,e='neutral'):return {'s':w,'t':t,'e':e}
def C(label,flag,reply):
    return {'text':label,'flags':[flag],'byRoute':{r:[L(*x) for x in reply] for r in ('arland','sofia')}}
def sc(s,id,route,title,loc,lines,choices=()):
    s['scenes'][id]={'title':title,'route':route,'chapter':'PRO','location':loc,'trigger':'V474 playable Prologue',
                       'lines':[L(*x) for x in lines],'choices':list(choices),'flags':[]}
def it(id,room,x,y,label,actions,route=None,sprite=None):
    o={'id':id,'area':room,'x':x,'y':y,'r':95,'label':label,'actions':actions}
    if route:o['route']=route
    if sprite:o['sprite']={'image':'items/'+sprite,'x':x,'y':y-15,'bob':True}
    return o
def step(id,obj,its):return {'id':id,'chapter':'PRO','quest':'Q_PRO_GIFT','objective':{'arland':obj[0],'sofia':obj[1]},'interactables':its}
def require(flag,yes,no=()):return act('if',when={'flags':[flag]},then=list(yes),**{'else':list(no)})
def mem(b,id,route,title,flag,icon,desc):
    b['entries'].append({'id':'v474_pro_'+id,'chapter':'PRO','route':route,'type':'optional_story_branch',
       'unlock':flag,'icon':'items/'+icon,'title':title,'text':desc})
def apply():
    s=json.loads((DATA/'story.json').read_text(encoding='utf8'))
    q=json.loads((DATA/'quests.json').read_text(encoding='utf8'))
    b=json.loads((DATA/'memory_book.json').read_text(encoding='utf8'))
    maps=json.loads((DATA/'maps.json').read_text(encoding='utf8'))
    steps={x['id']:x for x in q['steps']}
    for id in ('PRO_PHONE','PRO_GIFT','PRO_GO_PLAZA','PRO_MEET','PRO_BOOK','PRO_SHARDS','PRO_PORTAL','C01_NOTE','V473_EPI_FINALE'):
        assert id in steps,id
    for id in ('P-A01','P-S01','P-A02','P-S02','P-X01','P-X02','P-X03','P-X04','C01-A01','C01-S01'):
        assert id in s['scenes'],id
    # Remove only content owned by this patch so repeated builds stay identical.
    s['scenes']={k:v for k,v in s['scenes'].items() if not k.startswith(V+'-')}
    q['steps']=[x for x in q['steps'] if not x['id'].startswith(V+'_PRO_')]
    b['entries']=[x for x in b['entries'] if not x['id'].startswith('v474_pro_')]
    for k in list(b['items']):
        if k.startswith('v474_pro_'):del b['items'][k]
    steps={x['id']:x for x in q['steps']}
    # Strip ONLY our previously injected actions, including v474's first
    # untagged draft. This makes repeat builds byte-identical and prevents
    # duplicate dialog, rewards, scene callbacks and cinematic effects.
    def ours(x):
        if x.get('v474'):return True
        if x.get('do')=='music' and x.get('id') in ('cinema_prologue_promise_v474','cinema_prologue_memory_v474'):return True
        if x.get('do')=='flag' and x.get('id')=='V474_PRO_NEW_COMPLETE':return True
        if x.get('do')=='cine' and any(c.get('c')=='shot' and c.get('frame')=='intimate' and c.get('zoom')==1.26 for c in x.get('cmds',[])):return True
        if x.get('do')=='if':
            for b in ('then','else'):
                if any(str(nested.get('id','')).startswith('V474-') for nested in x.get(b,[])):return True
        return False
    for key in ('PRO_MEET','PRO_PORTAL'):
        for entry in steps[key].get('interactables',[]):entry['actions']=[ac for ac in entry['actions'] if not ours(ac)]
    for key in ('C01_NOTE','V473_EPI_FINALE','PRO_SHARDS'):
        for entry in steps[key].get('interactables',[]):entry['actions']=[ac for ac in entry['actions'] if not ours(ac)]
    s['meta']['prologueOverhaul']='v4.7.4: crafted promises, three dual-view shards, two-perspective emotional payoffs'
    s['meta']['prologueMigration']='retained old steps PRO_PHONE PRO_GIFT PRO_SHARDS PRO_PORTAL; old saves resume without reset'
    s['scenes']['P-A01']['lines']=[L('narrator','Pagi masih tenang. Di meja Arland ada lipatan kertas yang semalam belum selesai.'),
       L('arland','Sofia bilang ketemu di plaza. Aku pengen bawa sesuatu yang dibuat sendiri.'),
       L('sofia_msg','Pagi, Land! Jangan lupa sarapan sebelum berangkat, ya.'),
       L('arland','Dia masih inget aku suka buru-buru kalau ada rencana. Kok aku jadi gugup, sih?')]
    s['scenes']['P-A01']['choices']=[
       C('Balas: Aku senang bisa ketemu kamu','V474_A_TEXT_HONEST',[('arland','Aku senang bisa ketemu kamu. Sampai nanti, Sof.'),('sofia_msg','Aku juga. Hati-hati di jalan!')]),
       C('Balas: Ada kejutan kecil, jangan penasaran dulu','V474_A_TEXT_PLAYFUL',[('arland','Ada sesuatu yang mau aku kasih nanti. Tapi jangan ditebak!'),('sofia_msg','Ya ampun, bikin penasaran aja. Hahaha.')])]
    s['scenes']['P-S01']['lines']=[L('narrator','Sofia terbangun dari mimpi tentang buku dua warna yang terbuka di taman bercahaya.'),
       L('sofia','Aku lupa wajah orang di mimpinya, tapi rasanya seperti pernah didengarkan.'),
       L('arland_msg','Sof, nanti di Plaza ya. Aku berangkat setelah beresin sesuatu.'),
       L('sofia','Dia pasti lagi menyiapkan sesuatu. Aku ingin menyampaikan perasaanku dengan caraku juga.')]
    s['scenes']['P-S01']['choices']=[
       C('Balas: Aku nggak sabar cerita banyak nanti','V474_S_TEXT_OPEN',[('sofia','Aku nggak sabar cerita banyak nanti. Ada mimpi aneh juga.'),('arland_msg','Aku dengerin nanti ya. Penasaran!')]),
       C('Balas: Sampai nanti, jangan terburu-buru','V474_S_TEXT_GENTLE',[('sofia','Sampai nanti. Jangan buru-buru, Land.'),('arland_msg','Siap! Tenang aja, aku ingat.')])]
    # Playable route-private preparation: two environmental steps before existing gift collection.
    sc(s,'V474-P-A-FOLD','arland','Lipatannya Tidak Harus Sempurna','arland_room',[
       ('narrator','Kertas berwarna hangat dan pita tipis tersusun di meja. Satu sudut bunganya terlipat miring.'),
       ('arland','Aku bisa bikin ulang, tapi apa Sofia bakal peduli kalau lipatannya sedikit salah?'),
       ('narrator','Arland menyelesaikan kelopak terakhir dengan tangannya sendiri.')],[
       C('Pertahankan lipatan asli','V474_A_FOLD_REAL',[('arland','Biarkan saja. Yang penting ini kubuat sendiri.')]),
       C('Rapikan perlahan tanpa membuang bunganya','V474_A_FOLD_CARE',[('arland','Aku rapikan sedikit. Nggak perlu mulai dari nol.')])])
    sc(s,'V474-P-S-DRAFT','sofia','Tulisan Kecil di Kartu Pos','sofia_room',[
       ('narrator','Sofia mencoba menulis kalimat pertama. Ia mencoretnya, lalu berhenti sebentar.'),
       ('sofia','Aku pengen Arland tahu aku senang ketemu dia. Tapi ngomong terus terang nggak selalu gampang.'),
       ('narrator','Di belakang kartu pos masih tersisa ruang untuk satu kalimat yang jujur.')],[
       C('Tulis: Terima kasih sudah mau mendengar','V474_S_DRAFT_THANK',[('sofia','Kalimat sederhana, tapi ini yang benar-benar aku rasakan.')]),
       C('Tulis: Aku ingin punya banyak cerita denganmu','V474_S_DRAFT_TOMORROW',[('sofia','Mungkin suatu hari nanti kita bakal baca ini sambil tertawa.')])])
    sc(s,'V474-P-A-RIBBON','arland','Pita dan Janji Kecil','arland_room',[
       ('narrator','Ada dua pita di kotak kecil. Bukan harganya yang membuat pilihan ini berarti.'),
       ('arland','Sofia suka hal sederhana. Aku cuma mau dia tahu aku benar-benar mengingatnya.')],[
       C('Pita krem, seperti cahaya pagi','V474_A_RIBBON_CREAM',[('arland','Warna tenang. Aku mau ingat pagi saat memutuskan bikin ini.')]),
       C('Pita ungu, seperti langit menjelang malam','V474_A_RIBBON_VIOLET',[('arland','Ini cocok dengan kartu kecil yang pernah ia suka.')])])
    sc(s,'V474-P-S-STAMP','sofia','Satu Simbol yang Disimpan','sofia_room',[
       ('narrator','Sofia memilih satu cap kecil untuk sudut kartu pos. Bintang dan bunga sama-sama indah.'),
       ('sofia','Aku nggak tahu kenapa gambar bintang membuatku ingat mimpi tadi.')],[
       C('Cap bintang, sebagai harapan','V474_S_STAMP_STAR',[('sofia','Bintangnya kecil. Tapi aku ingin mengingat mimpi itu.')]),
       C('Cap bunga, seperti hadiah sederhana','V474_S_STAMP_FLOWER',[('sofia','Bunga ini bisa mengingatkan kami pada hari biasa yang berarti.')])])
    a='arland_room';sf='sofia_room'
    p1=step('V474_PRO_CRAFT',('Lipat bunga kertas di meja kerja','Tulis satu kalimat pribadi pada kartu pos'),[
       it('v474_fold',a,620,512,'Lipat bunga kertas',[act('scene',id='V474-P-A-FOLD'),act('sfx',id='paper_fold'),act('flag',id='V474_A_CRAFTED'),act('step',id='V474_PRO_FINISH')],'arland','v474_folded_flower.png'),
       it('v474_draft',sf,695,512,'Tulis kartu pos',[act('scene',id='V474-P-S-DRAFT'),act('sfx',id='page'),act('flag',id='V474_S_CRAFTED'),act('step',id='V474_PRO_FINISH')],'sofia','v474_postcard.png')])
    p2=step('V474_PRO_FINISH',('Pilih pita bunga sebelum berangkat','Pilih simbol kartu pos sebelum berangkat'),[
       it('v474_ribbon',a,550,530,'Pilih pita bunga',[act('scene',id='V474-P-A-RIBBON'),act('flag',id='V474_A_GIFT_FINISHED'),act('step',id='PRO_GIFT')],'arland','v474_ribbon.png'),
       it('v474_stamp',sf,630,544,'Pilih cap kartu pos',[act('scene',id='V474-P-S-STAMP'),act('flag',id='V474_S_GIFT_FINISHED'),act('step',id='PRO_GIFT')],'sofia','v474_postcard.png')])
    q['steps']=[p1,p2]+q['steps']
    # Phone interaction forwards to new interactive workshop, preserving same original phone IDs.
    for x in steps['PRO_PHONE']['interactables']:
        for ac in x['actions']:
            if ac.get('do')=='step' and ac.get('id')=='PRO_GIFT': ac['id']='V474_PRO_CRAFT'
    # Room doors prevent premature exit if developer manually warps a save into the new steps.
    # All old step IDs are still valid; a migrated save does not have to replay the new workshop.
    # Keep the original room doors locked during new preparation steps; this is
    # crucial for preventing premature departure (and invisible quest objectives).
    for room in ('arland_room','sofia_room'):
        for door in maps['areas'][room]['doors']:
            for lock in door.get('locked',[]):
                if 'PRO_PHONE' in lock.get('steps',[]) and 'PRO_GIFT' in lock.get('steps',[]):
                    lock['steps']=list(dict.fromkeys(lock['steps']+['V474_PRO_CRAFT','V474_PRO_FINISH']))
    # Character-focused gift dialogue; choices are remembered via persistent flags.
    s['scenes']['P-A02']['lines']=[L('arland','Lipatan yang ini masih agak miring.'),
       L('arland','Tapi aku ingat waktu melipatnya. Aku ingin Sofia menerima apa adanya, bukan karena sempurna.')]
    s['scenes']['P-A02']['choices']=[
       C('Tulis: Terima kasih sudah ada di hari-hari biasa','V474_A_NOTE_EVERYDAY',[('arland','Aku mau bilang terima kasih untuk hal-hal kecil yang dia lakukan.')]),
       C('Tulis: Kalau kamu sedih, aku mau mendengarkan','V474_A_NOTE_LISTEN',[('arland','Semoga aku nggak lupa kalau mendengar lebih penting daripada selalu punya jawaban.')])]
    s['scenes']['P-S02']['lines']=[L('sofia','Tulisan ini nggak panjang. Tapi aku memilih setiap kata pelan-pelan.'),
       L('sofia','Aku berharap Arland nggak cuma membacanya, tapi juga tahu kalau aku sungguh-sungguh.')]
    s['scenes']['P-S02']['choices']=[
       C('Tambahkan: Aku nyaman jadi diriku di dekatmu','V474_S_NOTE_COMFORT',[('sofia','Aku ingin dia tahu ini. Nggak selalu mudah ngomongnya langsung.')]),
       C('Tambahkan: Yuk, saling cerita tanpa harus sempurna','V474_S_NOTE_STORIES',[('sofia','Hari yang nggak sempurna pun bisa punya cerita yang indah.')])]
    # Shared cutscene P-X01 splits into three parts using *fixed indices*. Keep 7 lines
    # so existing timed gestures stay paired with the correct speaker.
    s['scenes']['P-X01']['lines']=[L('arland','Sof! Aku di sini!'),L('sofia','Aku lihat. Kamu kelihatan semangat banget.'),
       L('arland','Ada sesuatu kecil yang kubuat sendiri.'),L('sofia','Kebetulan aku juga menulis sesuatu buat kamu.'),
       L('narrator','Mereka bertukar hadiah. Tidak ada yang sempurna, tetapi keduanya tersenyum tanpa dipaksa.'),
       L('narrator','Di belakang bunga kertas terdapat tulisan tangan Arland; pada kartu pos ada simbol kecil milik Sofia.'),
       L('sofia','Jangan buru-buru dibaca, ya. Aku pengen kita punya waktu untuk cerita pelan-pelan.')]
    # Added after existing P-X01 timed segment; route-specific follow-up is invoked as normal scene.
    sc(s,'V474-P-MEET-A','arland','Hadiah yang Tidak Dipaksakan','plaza',[
       ('arland','Aku sempat takut bunganya nggak bagus, Sof.'),('sofia','Aku suka karena kamu bikin sendiri. Itu udah cukup.'),
       ('arland','Boleh aku dengar cerita di balik kartu pos ini?'),('sofia','Boleh. Nanti gantian aku baca punyamu, ya.')])
    sc(s,'V474-P-MEET-S','sofia','Yang Ditulis dengan Pelan','plaza',[
       ('sofia','Aku lama banget milih kata di kartu ini.'),('arland','Aku juga lama melipat bunganya. Kita sama-sama gugup, ternyata.'),
       ('sofia','Boleh aku baca pesannya sendiri dulu?'),('arland','Tentu. Kalau mau cerita, aku dengerin.')])
    mt=steps['PRO_MEET']['interactables'][0]['actions']
    at=next((i for i,z in enumerate(mt) if z.get('do')=='flag' and z.get('id')=='PRO_MET_PARTNER'),None)
    assert at is not None
    mt[at:at]=[act('if',when={'route':'arland'},then=[act('scene',id='V474-P-MEET-A')],**{'else':[act('scene',id='V474-P-MEET-S')]}),
         act('music',id='cinema_prologue_promise_v474')]
    s['scenes']['P-X02']['lines']=[L('sofia','Arland... buku itu tadi nggak ada di bangku.'),L('arland','Sampulnya dua warna. Ada tanda bunga dan bintang.'),
       L('sofia','Aku pernah melihat cahayanya di mimpi. Tapi nggak persis seperti ini.'),
       L('narrator','Halaman pertama menampilkan dua tulisan tangan yang berbeda. Saat disentuh bersama, cahaya membuka pintu.')]
    s['scenes']['P-X03']['lines']=[L('arland','Ini taman apa? Kok rasanya seperti mengingat tempat yang belum pernah kita datangi?'),
       L('sofia','Ada tiga keping cahaya. Aku bisa lihat satu bentuk bintang di sana.'),
       L('arland','Aku melihat kelopak bunga. Kita ikuti yang kita lihat masing-masing, ya.'),
       L('sofia','Iya. Kita saling cerita kalau ada yang berbeda.')]
    # Three shard interactions are playable, and route-specific dialogue reveals
    # differences instead of artificially counting three pickups as three quests.
    shard_lines={
       1:[('narrator','Keping pertama menggambarkan meja kecil dan hadiah buatan tangan.'),
          ('arland','Aku ingat tangan yang berkali-kali salah melipat.'),('sofia','Aku melihat seseorang menunggu dan berani menyampaikan perasaannya.')],
       2:[('narrator','Keping kedua memperlihatkan dua orang di satu tempat, tetapi langit di atas mereka berbeda.'),
          ('arland','Dalam ingatanku, kami sama-sama tertawa.'),('sofia','Aku juga tertawa... sambil gugup. Ternyata dua perasaan itu bisa ada bersamaan.')],
       3:[('narrator','Keping terakhir menyimpan ruang kosong di sebelah tulisan yang hampir memudar.'),
          ('sofia','Ada kalimat yang belum selesai. Kenapa satu sisinya seperti hilang?'),
          ('arland','Kalau satu bagian belum kelihatan, jangan langsung kita anggap nggak ada.')]
    }
    for n,lines in shard_lines.items():
        for rt in ('arland','sofia'):
            # Different emphasis depending on whose memory is playable.
            unique= [('arland','Bunga yang kulipat mungkin jelek, tapi aku ingat kenapa aku membuatnya.') if n==1 else
                     ('arland','Aku harus tanya apa yang Sofia rasakan, bukan hanya menebaknya.') if n==2 else
                     ('arland','Ada bagian yang belum bisa kubaca. Aku mau menunggu suaranya.') ] if rt=='arland' else [
                    ('sofia','Kartu kecil ini menyimpan keberanian yang nggak terlihat dari luar.') if n==1 else
                    ('sofia','Kalau aku takut bilang sedang gugup, Arland mungkin nggak akan tahu.') if n==2 else
                    ('sofia','Aku ingin bisa bilang apa yang kurasakan sebelum kalimatnya hilang.')]
            sc(s,f'V474-P-SHARD-{n}-{rt[0].upper()}',rt,'Dua Sisi Serpihan '+str(n),'memory_garden',lines+unique)
        target=steps['PRO_SHARDS']['interactables'][n-1]
        assert target['id']=='shard_'+str(n)
        target['actions'][:0]=[act('if',when={'route':'arland'},then=[act('scene',id=f'V474-P-SHARD-{n}-A')],
                     **{'else':[act('scene',id=f'V474-P-SHARD-{n}-S')]})]
        # No double-collection: existing hideIfFlag + counter/shard retained.
    s['scenes']['P-X04']['lines']=[L('narrator','Tiga keping cahaya menyatu. Pada satu halaman, bunga dan bintang akhirnya terlihat berdampingan.'),
       L('sofia','Ternyata yang kamu lihat dan yang kulihat sama-sama punya tempat.'),
       L('arland','Ada satu baris kosong. Bukunya seperti menunggu cerita dari dua sisi.'),
       L('narrator','Gerbang pulang menyala. Pada halaman berikutnya tertulis: The Beginning of Us.')]
    sc(s,'V474-P-PORTAL-A','arland','Sebelum Melangkah Pulang','memory_garden',[
       ('arland','Aku nggak paham semua yang barusan terjadi.'),('sofia','Aku juga. Tapi aku senang kita saling cerita, bukan saling nebak.'),
       ('arland','Kalau nanti aku lupa, ingetin aku ya. Aku pengen belajar mendengar.')])
    sc(s,'V474-P-PORTAL-S','sofia','Dua Suara, Satu Jalan Pulang','memory_garden',[
       ('sofia','Aku takut mimpi itu pertanda sesuatu. Tapi sekarang aku nggak sendirian.'),
       ('arland','Aku nggak tahu artinya, Sof. Kita cari tahu bareng, boleh?'),('sofia','Boleh. Kita mulai dari yang kita lihat sendiri-sendiri.')])
    portal=steps['PRO_PORTAL']['interactables'][0]['actions']
    portal[:0]=[act('music',id='cinema_prologue_memory_v474'),
       act('cine',cmds=[{'c':'bars','on':True,'t':.4},{'c':'shot','focus':'partner','zoom':1.26,'frame':'intimate','t':1.8,'bars':False},
                       {'c':'fx','kind':'sparkles','on':'player','t':2.4,'n':16},{'c':'bars','on':False,'t':.5}]),
       act('if',when={'route':'arland'},then=[act('scene',id='V474-P-PORTAL-A')],**{'else':[act('scene',id='V474-P-PORTAL-S')]}),
       act('flag',id='V474_PRO_NEW_COMPLETE')]
    # Long-range payoff, including old-save fallback (both absence of the two
    # unique route flags and presence of the original prologue chapter completion).
    sc(s,'V474-C01-RECALL-A','arland','Tinta dari Pagi Itu','arland_room',[
       ('arland','Bunga yang kubawa ke plaza bukan hal terbesar yang pernah kuberi.'),
       ('arland','Tapi waktu menulis pesannya aku memutuskan untuk mencoba lebih jujur.')])
    s['scenes']['V474-C01-RECALL-A']['chapter']='C01'
    sc(s,'V474-C01-RECALL-S','sofia','Satu Kartu, Dua Perasaan','sofia_room',[
       ('sofia','Aku masih ingat bagaimana memilih kata di kartu pos.'),
       ('sofia','Kadang perasaan memang lebih mudah ditulis dulu. Yang penting nanti tetap berani bicara.')])
    s['scenes']['V474-C01-RECALL-S']['chapter']='C01'
    for x in steps['C01_NOTE']['interactables']:
        # Place payoff after personal chapter1 scene but before its own existing step switch.
        pos=next(i for i,z in enumerate(x['actions']) if z.get('do')=='step')
        flag='V474_A_GIFT_FINISHED' if x['route']=='arland' else 'V474_S_GIFT_FINISHED'
        scene='V474-C01-RECALL-A' if x['route']=='arland' else 'V474-C01-RECALL-S'
        x['actions'][pos:pos]=[require(flag,[act('scene',id=scene)])]
    sc(s,'V474-EPI-RECALL-A','arland','Bunga Kertas yang Tetap Ada','riverside',[
       ('narrator','Arland menemukan satu lipatan miring pada bunga yang dahulu ia buat.'),
       ('arland','Dulu aku takut kamu cuma melihat bagian yang salah.'),
       ('sofia','Aku ingat kamu sudah berusaha. Yang paling penting, sekarang kamu juga tahu kapan harus hadir.')])
    s['scenes']['V474-EPI-RECALL-A']['chapter']='EPI'
    sc(s,'V474-EPI-RECALL-S','sofia','Kartu Pos yang Tak Pernah Diburu','riverside',[
       ('narrator','Sofia membuka kartu pos tua. Simbol kecil di pojoknya sudah sedikit pudar.'),
       ('sofia','Dulu aku nggak berani menulis semuanya.'),
       ('arland','Sekarang kamu boleh cerita sebanyak yang kamu mau. Aku akan dengerin.')])
    s['scenes']['V474-EPI-RECALL-S']['chapter']='EPI'
    e=steps['V473_EPI_FINALE']['interactables'][0]['actions']
    # Place before terminal chapter completion and only if the newly-played prologue is on this save.
    pos=next(i for i,z in enumerate(e) if z.get('do')=='chapterEnd')
    e[pos:pos]=[
       require('V474_A_NOTE_EVERYDAY',[act('scene',id='V474-EPI-RECALL-A')]),
       require('V474_A_NOTE_LISTEN',[act('scene',id='V474-EPI-RECALL-A')]),
       require('V474_S_NOTE_COMFORT',[act('scene',id='V474-EPI-RECALL-S')]),
       require('V474_S_NOTE_STORIES',[act('scene',id='V474-EPI-RECALL-S')])]
    # Memory Book entries are optional for mutually exclusive choices.
    for rt,side in (('arland','a'),('sofia','s')):
        mem(b,side+'_written',rt,'Janji Kecil dari Pagi','V474_'+side.upper()+'_GIFT_FINISHED',
            'v474_postcard.png' if rt=='sofia' else 'v474_folded_flower.png',
            'Pemain menyiapkan hadiah melalui beberapa langkah, bukan mengambilnya begitu saja.')
        for suffix,title in ([('A_NOTE_EVERYDAY','Hari-Hari Biasa'),('A_NOTE_LISTEN','Belajar Mendengar')] if rt=='arland' else
                             [('S_NOTE_COMFORT','Menjadi Diri Sendiri'),('S_NOTE_STORIES','Cerita yang Belum Selesai')]):
            mem(b,suffix.lower(),rt,title,'V474_'+suffix,'v474_postcard.png' if rt=='sofia' else 'v474_folded_flower.png',
                'Kalimat yang dipilih sejak Prolog kembali bermakna setelah perjalanan sampai Epilog.')
    for i in (1,2,3):
        # Same shard in both routes, but monologue differs.
        mem(b,'shard_'+str(i),'shared',['Hadiah dari Dua Sisi','Hari dengan Dua Langit','Kalimat yang Belum Lengkap'][i-1],
            'SHARD_'+str(i),'v474_shard.png',
            'Kenangan ini dibaca dengan dua cara berbeda tanpa menghapus salah satu suara.')
    # Pay off all first-morning and keepsake choices; choices that are merely
    # stored but never mentioned would be false branching. New optional scenes
    # are short, non-canon callbacks, not extra required steps for older saves.
    reactions=[
       ('A_TEXT_HONEST','arland','Janji yang Dikatakan','Aku memang bilang senang ketemu Sofia. Kali ini aku mau membuktikannya dengan hadir.'),
       ('A_TEXT_PLAYFUL','arland','Kejutan yang Punya Tempat','Aku senang bisa bercanda dengannya. Tapi aku juga harus tahu kapan ia butuh jawaban serius.'),
       ('S_TEXT_OPEN','sofia','Cerita yang Sejak Awal Ditunggu','Aku pernah menulis kalau ingin banyak bercerita. Aku nggak mau kehilangan keberanian itu.'),
       ('S_TEXT_GENTLE','sofia','Jangan Terburu-buru','Sejak awal aku mengingatkan Arland agar tidak terburu-buru. Sekarang aku juga belajar memintanya hadir.'),
       ('A_FOLD_REAL','arland','Lipatan yang Dibiarkan Asli','Salah lipat itu masih ada. Sofia tidak pernah meminta aku memperbaiki semua hal.'),
       ('A_FOLD_CARE','arland','Merawat Bukan Mengulang','Aku pernah merapikan bunga tanpa merobeknya. Mungkin itu juga cara merawat hubungan.'),
       ('S_DRAFT_THANK','sofia','Ucapan Terima Kasih','Kalimat pertamaku bukan tentang hadiah. Aku cuma ingin dia tahu bahwa aku merasa didengar.'),
       ('S_DRAFT_TOMORROW','sofia','Cerita Hari Esok','Sejak kartu pertama, aku sudah ingin punya banyak cerita. Bukan kisah tanpa salah, melainkan kisah yang sungguh kami jalani.'),
       ('A_RIBBON_CREAM','arland','Pita Cahaya Pagi','Aku memilih pita seperti pagi. Awalnya aku pikir semuanya harus cerah setiap hari.'),
       ('A_RIBBON_VIOLET','arland','Pita Langit Senja','Aku memilih pita ungu karena Sofia menyukai langit sore. Waktu itu aku ingat detail kecilnya.'),
       ('S_STAMP_STAR','sofia','Bintang di Kartu Pos','Aku memilih bintang tanpa tahu bahwa kelak kita akan mengikuti langit sampai Memory Bridge.'),
       ('S_STAMP_FLOWER','sofia','Bunga di Ujung Kalimat','Aku memilih gambar bunga. Sekarang aku tahu betapa lama Arland membuatnya dengan tangannya sendiri.'),
       ('A_NOTE_EVERYDAY','arland','Terima Kasih untuk Hari Biasa','Aku menulis tentang hari-hari biasa. Setelah galeri, aku belajar bahwa hadir adalah cara menjaganya.'),
       ('A_NOTE_LISTEN','arland','Janji untuk Mendengar','Aku menulis ingin mendengar saat Sofia sedih. Sekarang aku paham mendengar itu bukan sekadar menawarkan solusi.'),
       ('S_NOTE_COMFORT','sofia','Boleh Menjadi Diri Sendiri','Aku menulis bahwa aku nyaman menjadi diriku. Sekarang aku juga berani bilang kalau sesuatu menyakitkan.'),
       ('S_NOTE_STORIES','sofia','Dua Cerita, Bukan Satu','Aku menulis agar kami saling bercerita. Sekarang aku tidak takut kalau versi kami berbeda.')]
    for flag,rt,title,spoken in reactions:
        sid='V474-RECALL-'+flag
        sc(s,sid,rt,title,'plaza' if ('TEXT_' in flag or 'RIBBON' in flag or 'STAMP' in flag) else 'riverside',[
            (rt,spoken),('narrator','Kalimat itu tersimpan sebagai bagian dari ingatan, bukan sebagai jawaban yang paling benar.')])
        if not ('TEXT_' in flag or 'RIBBON_' in flag or 'STAMP_' in flag):
            s['scenes'][sid]['chapter']='EPI'
        # A remembered first response at the plaza OR a written letter seen
        # again by the end; both stay conditional to avoid wrong-POV content.
        callback=require('V474_'+flag,[act('scene',id=sid)])
        if 'TEXT_' in flag or 'RIBBON_' in flag or 'STAMP_' in flag:
            p=next(i for i,z in enumerate(mt) if z.get('do')=='flag' and z.get('id')=='PRO_MET_PARTNER')
            mt[p:p]=[callback]
        else:
            p=next(i for i,z in enumerate(e) if z.get('do')=='chapterEnd')
            e[p:p]=[callback]
        mem(b,'choice_'+flag.lower(),rt,title,'V474_'+flag,
            'v474_postcard.png' if rt=='sofia' else 'v474_folded_flower.png',spoken)
    # Link assets to inventory metadata, preserve original paper_flower and postcard IDs.
    for name,title,desc,icon in [
        ('v474_pro_flower_sketch','Sketsa Bunga Pertama','Catatan kecil tentang lipatan yang tidak sempurna.','v474_folded_flower.png'),
        ('v474_pro_postcard_notes','Draf Kartu Pos','Kata-kata pertama yang ditulis perlahan.','v474_postcard.png')]:
        b['items'][name]={'name':title,'icon':'items/'+icon,'desc':desc}
    for path,obj in [('story.json',s),('quests.json',q),('memory_book.json',b),('maps.json',maps)]:
        (DATA/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('PASS V474 playable prologue: 2 preparation stages, route exclusive gifts, 3 dual-view shards, C01 and Epilogue payoff')
if __name__=='__main__':apply()
