#!/usr/bin/env python3
"""Thoughtful optional dialogue beats around original canon. No flags/choices changed."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]; P=R/'android/assets/data/story.json'
lines={
'P-X01':[
('arland','malu','Aku tahu ini cuma benda kecil. Tapi aku membuatnya sambil membayangkan kita akan tertawa hari ini.'),
('sofia','senyum','Bukan ukurannya yang penting. Aku suka kamu mau cerita kenapa memilihnya.')],
'P-X02':[
('arland','bingung','Kalau dua tulisan itu berbeda, apa bukunya bisa salah mengingat?'),
('sofia','penasaran','Atau justru kita yang belum selesai saling bercerita?')],
'C01-X02':[
('sofia','serius','Aku tidak ingin memilih simbol hanya karena yang lain memilihnya.'),
('arland','lega','Iya, kalau petunjuk kita berbeda, kita dengarkan dulu alasannya.')],
'V468-C02-A-INVITE':[
('arland','malu','Aku boleh menyusun rencananya, tapi Sofia tetap bebas memilih cara dan waktunya.'),
('narrator','neutral','Ia menghapus satu kalimat yang terdengar terlalu memaksa.')],
'V468-C02-S-REPLY':[
('sofia','penasaran','Kalau aku memilih waktu lain, semoga dia tahu aku tetap menghargai ajakannya.'),
('narrator','neutral','Sofia memeriksa kembali pesannya sebelum mengirim.')],
'V468-C02-S-REUNION':[
('sofia','senyum','Aku senang kita bisa bertemu setelah sama-sama memberi ruang.'),
('arland','lega','Aku belajar untuk tidak menebak isi pikiranmu dari jawaban yang singkat.')],
'V469-C03-A-FRAME-DONE':[
('arland','senyum','Foto ini tidak sempurna, tapi aku ingat suara tawa di belakang kamera.'),
('narrator','neutral','Di tepi bingkai, ada tempat kecil untuk menuliskan cerita dari sisi Sofia.')],
'V469-C03-S-SCRAP-DONE':[
('sofia','senyum','Kalau suatu hari warnanya pudar, ceritanya masih bisa kita ceritakan lagi.'),
('narrator','neutral','Ia menyisakan satu halaman untuk catatan yang belum ditulis.')],
'V470-C04-A-WARN':[
('arland','khawatir','Mengirim kabar itu penting, tetapi aku juga perlu memastikan dia benar-benar menerimanya.'),
('narrator','neutral','Layar ponsel menyala sebentar, lalu kembali redup di bawah hujan.')],
'V470-C04-S-NOTE':[
('sofia','serius','Aku ingin bilang kecewa tanpa membuatnya merasa seluruh usahanya tidak berarti.'),
('narrator','neutral','Ia membaca ulang satu kalimat, kemudian menghapus kata yang terdengar terlalu keras.')],
'V471-C05-A-REFLECT':[
('arland','lega','Aku tidak bisa mengulang hari itu, tapi aku masih bisa belajar mendengarkan hari ini.'),
('narrator','neutral','Cahaya di roda gigi berhenti berputar sejenak, seperti memberi ruang pada kata-katanya.')],
'V471-C05-S-REFLECT':[
('sofia','lega','Mengerti alasan orang lain tidak berarti perasaanku sendiri harus hilang.'),
('narrator','neutral','Pantulan di permukaan danau memperlihatkan dua cahaya yang sama-sama utuh.')],
'V471-C05-MOON-TOGETHER':[
('arland','penasaran','Di sini aku melihat jalannya dari kanan. Punyamu terlihat seperti apa?'),
('sofia','senyum','Dari kiri, garisnya berbeda. Kalau kita gabung, baru kelihatan jembatannya.')],
'V471-C05-QUIET-REVEAL':[
('sofia','serius','Berarti The Quiet bukan suara yang harus kita bungkam?'),
('arland','lega','Mungkin dia mengingatkan kita pada percakapan yang belum sempat selesai.')],
'V472-C06-ARLAND-REFLECTION':[
('arland','senyum','Aku boleh ingin menjaga hubungan ini tanpa berpura-pura bisa menyelesaikan semuanya sendiri.'),
('narrator','neutral','Di cermin aula, satu pintu baru terlihat ketika ia berhenti berlari.')],
'V472-C06-SOFIA-REFLECTION':[
('sofia','senyum','Aku tidak harus selalu punya jawaban sekarang supaya kita bisa melanjutkan perjalanan.'),
('narrator','neutral','Ia menyentuh tepian halaman kosong dan membiarkan cahaya masuk.')],
'V472-C06-PROMISE':[
('sofia','senyum','Kalau nanti aku lupa mendengarkan, boleh ingatkan dengan lembut?'),
('arland','senyum','Boleh. Dan kalau aku terlalu buru-buru, kamu boleh minta aku duduk sebentar.')],
'V472-C06-THREE-FUTURES':[
('arland','serius','Aku tidak ingin memilih hidup yang kelihatan paling mudah hanya karena takut salah.'),
('sofia','lega','Kita boleh punya rencana berbeda. Yang penting masih bisa dibicarakan.')],
'V473-EPI-LAKE-END':[
('arland','senyum','Besok mungkin biasa saja. Kita mungkin cuma pulang, makan, lalu cerita.'),
('sofia','senyum','Justru aku suka ada hari-hari biasa yang tidak harus dijadikan petualangan besar.')],
}

def main():
 data=json.loads(P.read_text(encoding='utf-8'))
 for id,notes in lines.items():
   sc=data['scenes'].get(id)
   if not sc:raise AssertionError('Old canon scene missing: '+id)
   if sc.get('v50DialogueExpanded'):continue
   idx=max(0,len(sc['lines'])-1)
   extra=[{'s':who,'e':emo,'t':txt} for who,emo,txt in notes]
   sc['lines'][idx:idx]=extra
   sc['v50DialogueExpanded']=True
 data['meta']['v50EmotionalNarrative']='19 established scenes with extra emotional beats; no choices/flags or canon modified'
 P.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Expanded',len(lines),'existing scenes with',sum(len(v) for v in lines.values()),'original narrative dialogue lines.')
if __name__=='__main__':main()
