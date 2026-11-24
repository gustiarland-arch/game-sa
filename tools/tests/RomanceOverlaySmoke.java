import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.game.RomanceOverlay;
import com.arlandsofia.olu.logic.*;
import com.arlandsofia.olu.ui.Ui;
import java.nio.file.*;
import java.util.*;
public class RomanceOverlaySmoke {
 static String read(String name) throws Exception { return Files.readString(Path.of("android/assets/data/"+name)); }
 public static void main(String[] args) throws Exception {
  StoryDb s=new StoryDb(read("story.json"));QuestDb q=new QuestDb(read("quests.json"));
  MapDb m=new MapDb(read("maps.json"),read("props.json")); MemoryBookDb book=new MemoryBookDb(read("memory_book.json"));
  Progress p=Progress.newGame("sofia",1,"C02_PHONE",m.area("sofia_room"));
  p.companion=true; p.minute=10*60; p.items.add("kopi_senja");
  QuestEngine e=new QuestEngine(s,q,m,p,false);
  RomanceOverlay r=new RomanceOverlay(new Assets(),e,book);
  final int[] calls={0}; final String[] status={""};
  RomanceOverlay.Listener callback=(actions,msg)->{calls[0]++;status[0]=msg;
      if(actions.isEmpty() && !msg.startsWith("Berhenti bergandengan")) throw new AssertionError("no story");};
  r.open("taman_kota",callback);r.draw(new Ui(),1280,720);
  if(!r.active())throw new AssertionError("no panel");
  r.touchDown(970,480,0);r.touchUp(970,480,0);
  if(r.active()||calls[0]!=1||p.affection!=4||p.hasItem("kopi_senja"))throw new AssertionError("gift click failed");
  r.open("taman_kota",callback);r.draw(new Ui(),1280,720);
  r.touchDown(530,550,1);r.touchUp(530,550,1);r.draw(new Ui(),1280,720);
  r.touchDown(970,480,2);r.touchUp(970,480,2);
  if(r.active()||calls[0]!=2||p.affection!=14||p.coins!=4||!p.hasFlag("ROM_DATE_TAMAN_ONCE"))throw new AssertionError("date click failed "+p.affection+" "+p.coins);
  r.open("taman_kota",callback);r.draw(new Ui(),1280,720);
  r.touchDown(530,550,3);r.touchUp(530,550,3);r.draw(new Ui(),1280,720);
  r.touchDown(970,480,4);r.touchUp(970,480,4);
  if(calls[0]!=2||!r.active())throw new AssertionError("duplicate date should stay unavailable");
  p.minute=8*60;
  r.open("cafe",callback);r.draw(new Ui(),1280,720);
  // Buka tab Momen Harian ketiga dan jalankan kegiatan gratis pertama (pagi di kafe).
  r.touchDown(720,550,5);r.touchUp(720,550,5);r.draw(new Ui(),1280,720);
  int before=p.affection; int money=p.coins;
  r.touchDown(970,480,6);r.touchUp(970,480,6);
  if(r.active()||calls[0]!=3||p.affection!=before+3||p.coins!=money||p.momentCounts.get("pagi_kafe")!=1)
      throw new AssertionError("first daily moment click failed");
  // Double click pada hari yang sama tidak berhak menambah kedekatan.
  r.open("cafe",callback);r.draw(new Ui(),1280,720);
  r.touchDown(720,550,7);r.touchUp(720,550,7);r.draw(new Ui(),1280,720);
  r.touchDown(970,480,8);r.touchUp(970,480,8);
  if(calls[0]!=3||p.affection!=before+3||!r.active())throw new AssertionError("moment daily limit ignored");
  // Esoknya momen lain bisa dipilih: tombol baris kedua di Plaza siang hari.
  p.day++;p.minute=12*60;r.open("plaza",callback);r.draw(new Ui(),1280,720);
  r.touchDown(720,550,9);r.touchUp(720,550,9);r.draw(new Ui(),1280,720);
  r.touchDown(970,380,10);r.touchUp(970,380,10);
  if(r.active()||calls[0]!=4||p.momentCounts.get("genggam_tangan")!=1||p.affection!=before+7)
      throw new AssertionError("second daily moment click failed");
  if(!p.hasFlag("ROM_BOND_20"))throw new AssertionError("moment should unlock bond milestone");
  // v2.2: tab keempat, gandengan aktif/off/aktif lagi tanpa bonus ganda.
  p.minute=12*60; r.open("plaza",callback);r.draw(new Ui(),1280,720);
  r.touchDown(815,550,11);r.touchUp(815,550,11);r.draw(new Ui(),1280,720);
  int affection0=p.affection;
  r.touchDown(970,480,12);r.touchUp(970,480,12);
  if(r.active()||!p.holdingHands||calls[0]!=5||p.affection!=affection0+2)
      throw new AssertionError("couple handwalk click failed");
  r.open("plaza",callback);r.draw(new Ui(),1280,720);
  r.touchDown(815,550,13);r.touchUp(815,550,13);r.draw(new Ui(),1280,720);
  r.touchDown(970,480,14);r.touchUp(970,480,14);
  if(r.active()||p.holdingHands||calls[0]!=6||p.affection!=affection0+2)
      throw new AssertionError("couple handwalk off click failed");
  r.open("plaza",callback);r.draw(new Ui(),1280,720);
  r.touchDown(815,550,15);r.touchUp(815,550,15);r.draw(new Ui(),1280,720);
  r.touchDown(970,480,16);r.touchUp(970,480,16);
  if(r.active()||!p.holdingHands||calls[0]!=7||p.affection!=affection0+2||p.coupleActionCounts.get("gandengan")!=1)
      throw new AssertionError("couple handwalk toggle duplicate bonus");
  // Tos berada di halaman kedua dan bisa diklik tanpa memakan jatah daily moment.
  r.open("plaza",callback);r.draw(new Ui(),1280,720);
  r.touchDown(815,550,17);r.touchUp(815,550,17);r.draw(new Ui(),1280,720);
  r.touchDown(315,125,18);r.touchUp(315,125,18);r.draw(new Ui(),1280,720);
  r.touchDown(970,380,19);r.touchUp(970,380,19);
  if(r.active()||calls[0]!=8||p.coupleActionCounts.get("tos")!=1||p.affection!=affection0+3)
      throw new AssertionError("couple highfive page click failed");
  // v2.5: tab kelima Main Bareng memuat 6 game dan mengirim aksi ke ActionRunner, bukan memberi bonus sebelum main.
  int hearts = p.affection, callsBefore = calls[0];
  r.open("riverside", callback);r.draw(new Ui(),1280,720);
  r.touchDown(982,550,21);r.touchUp(982,550,21);r.draw(new Ui(),1280,720);
  r.touchDown(970,480,22);r.touchUp(970,480,22);
  if(r.active() || calls[0] != callsBefore+1 || p.affection!=hearts || !status[0].startsWith("Mulai Memancing"))
      throw new AssertionError("v2.5 romance game tab callback failed: "+status[0]);
  System.out.println("ROMANCE OVERLAY INPUT SMOKE OK: gift/date/moment/couple + v2.5 game tab; callbacks "+calls[0]);
 }
}
