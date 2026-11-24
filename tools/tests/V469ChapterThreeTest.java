import com.arlandsofia.olu.logic.*;
import java.util.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

/** Run complete C03 quest paths with the real QuestEngine+ActionRunner (no LibGDX). */
public final class V469ChapterThreeTest {
 static int checks=0,paths=0;
 static void ok(boolean yes,String msg){checks++;if(!yes)throw new AssertionError("V469 #"+checks+" "+msg);}
 static String read(String a,String n)throws Exception{return new String(Files.readAllBytes(Paths.get(a,"data",n)),StandardCharsets.UTF_8);}
 static final class Run implements ActionRunner.Presenter {
  final QuestEngine e; final ActionRunner a;final Progress p;final StoryDb story;final MapDb maps;
  final Map<String,Integer> choice=new HashMap<>();final List<String> scenes=new ArrayList<>(),music=new ArrayList<>();
  final List<String> mini=new ArrayList<>();int cinema=0;
  boolean cancelNext;
  Run(StoryDb s,QuestDb q,MapDb map,String rt,String step){
   story=s;maps=map;p=Progress.newGame(rt,1,q.firstStep(),map.area(Routes.room(rt)));p.step=step;
   e=new QuestEngine(s,q,map,p,false);a=new ActionRunner(e,this);
   MapDb.flags=f->p.hasFlag(f);
  }
  void pick(String id,int n){choice.put(id,n);}
  void visit(String id){
   QuestDb.Interactable it=null;
   for(QuestDb.Interactable a:e.step().interactables)if(a.id.equals(id)&&a.forRoute(p.route)){it=a;break;}
   ok(it!=null,"exists "+id+" at "+p.step);
   p.area=Routes.resolve(it.area,p.route);
   ok(maps.area(p.area)!=null,"map exists "+p.area);
   ok(e.interactables(p.area).contains(it),"available "+id+" "+p.step);
   a.run(e.actionsFor(it));ok(!a.busy(),"runner idle "+id);
  }
  void enter(String area){
   p.area=area;ok(maps.area(area)!=null,"enter map exists "+area);
   List<Map<String,Object>> acts=e.onEnterArea(area);
   ok(!acts.isEmpty(),"enterArea event exists at "+p.step);
   a.run(acts);ok(!a.busy(),"entry finishes");
  }
  public void playScene(String id,Runnable done){
   StoryDb.Scene sc=story.scene(id);ok(sc!=null,"valid story scene "+id);
   ok(sc.route.equals("shared")||sc.route.equals(p.route),"right route "+id);
   scenes.add(id);
   if(!sc.choices.isEmpty()){
    int selected=choice.getOrDefault(id,0);ok(selected>=0&&selected<sc.choices.size(),"choice range "+id);
    StoryDb.Choice ch=sc.choices.get(selected);
    ok(!ch.response(p.route).isEmpty(),"response present "+id);
    e.addFlags(ch.flags);
   }
   done.run();
  }
  public void playLines(List<StoryDb.Line> lines,String name,Runnable done){done.run();}
  public void openPuzzle(String id,ActionRunner.BoolCallback done){done.done(true);}
  public void openMinigame(String id,ActionRunner.IntCallback done){
   mini.add(id);if(cancelNext){cancelNext=false;done.done(-1);}else done.done(3);
  }
  public void openShop(String id,Runnable done){done.run();}
  public void warp(String area,float x,float y,String dir,Runnable done){
    String actual=Routes.resolve(area,p.route);
    ok(maps.area(actual)!=null,"warp map exists "+actual);
    ok(!maps.area(actual).blocked(x,y),"warp location safe "+actual);
    p.area=actual;p.x=x;p.y=y;p.dir=dir;done.run();
  }
  public void chapterCard(String chapter,Runnable done){done.run();}
  public void chapterEnd(String chapter,Runnable done){done.run();}
  public void credits(Runnable done){done.run();}
  public void cine(List<Map<String,Object>> cmds,Runnable done){
   ok(cmds!=null&&!cmds.isEmpty(),"nonempty cinematic");cinema++;done.run();
  }
  public void toast(String t){}public void sfx(String t){}public void music(String t){music.add(t);}
  public void emote(String who,String e){}public void companionChanged(boolean enabled){}
  public void stepChanged(){}public void onIdle(){}
 }
 static void walk(StoryDb s,QuestDb q,MapDb m,String rt,int intro,int photo,int corner,int promise,int letter,int card,int gal){
   Run run=new Run(s,q,m,rt,rt.equals("arland")?"C03_A_IDEA":"C03_S_CORNER");
   run.pick("V469-C03-A-FRAME-BEGIN",intro%2);
   run.pick("V469-C03-S-SCRAP-BEGIN",intro%2);
   run.pick("C03-S02",corner);
   run.pick("V469-C03-HALF-"+(rt.equals("arland")?"A":"S"),letter);
   run.pick("V464-C03-PROMISE",promise);
   run.pick("V469-C03-PROJECTOR-REFLECT",gal);
   run.pick("V469-C03-SKETCH-REFLECT",gal);
   run.pick("V469-C03-GALLERY-CARD",card);
   run.p.flags.add("V468_C02_PHOTO_"+new String[]{"LAUGH","LOOK","BLUR"}[photo]);
   run.p.flags.add("V467_C01_RESULT_"+new String[]{"LISTEN","RECORD","TRACE"}[photo]);
   if(rt.equals("sofia"))run.p.flags.add("V468_S_REPLY_"+new String[]{"YES","LATER","NO"}[intro%3]);
   else run.p.flags.add("V468_A_INVITE_"+new String[]{"SIMPLE","CARE","OPEN"}[intro%3]);
   run.visit(rt.equals("arland")?"idea":"corner");
   ok(run.p.step.equals(rt.equals("arland")?"V469_C03_A_FRAME":"V469_C03_S_SCRAP"),"personal stage started");
   ok(run.scenes.contains(rt.equals("arland")?"V469-C03-A-INVITE-"+new String[]{"SIMPLE","CARE","OPEN"}[intro%3]:
               "V469-C03-S-DATE-"+new String[]{"YES","LATER","NO"}[intro%3]),
      "Chapter2 decision acknowledged in Chapter3 scene");
   run.visit(rt.equals("arland")?"v469_frame":"v469_scrap");
   ok(run.p.step.equals("C03_FREE"),"personal stage completed");
   ok(run.p.items.contains(rt.equals("arland")?"v469_frame":"v469_scrapbook"),"route exclusive item");
   ok(!run.p.items.contains(rt.equals("arland")?"v469_scrapbook":"v469_frame"),"no other route item");
   ok(run.mini.contains("scrapbook"),"playable scrapbook minigame");
   ok(run.scenes.contains("C03-FREE@"+rt),"legacy route-specific market intro retained");
   run.visit("f3_buah");run.visit("f3_buku");
   ok("V469_C03_NEIGHBOR".equals(run.p.step),"market leads to neighbor task");
   run.visit(rt.equals("arland")?"v469_return_a":"v469_return_s");
   ok(run.p.items.contains("v469_neighbor_note"),"neighbor reward earned");
   if(rt.equals("arland")){
    ok("C03_A_INGREDIENTS".equals(run.p.step),"Arland ingredients stage");
    for(String id:new String[]{"fridge","honey","mint"})run.visit(id);
    ok(run.p.count("bahan")==3,"three unique ingredients counted once");
    ok("C03_A_KITCHEN".equals(run.p.step),"finish ingredient search");
    run.visit(rt.equals("arland")?"v469_kitchen_arrive_a":"v469_kitchen_arrive_s");
   }else{
    ok("C03_S_DECOR".equals(run.p.step),"Sofia decor stage");
    for(String id:new String[]{"dried","lights","frame"})run.visit(id);
    ok(run.p.count("dekor")==3,"three unique decorations counted once");
    run.visit("arrange");
    ok("C03_S_KITCHEN".equals(run.p.step),"memory corner arrangement finished");
    ok(run.scenes.contains("V469-C03-CORNER-"+new String[]{"PHOTO","FLOWER","BOOK"}[corner]),"corner choice actual callback");
    run.visit(rt.equals("arland")?"v469_kitchen_arrive_a":"v469_kitchen_arrive_s");
   }
   ok("C03_COOK".equals(run.p.step),"both routes reach shared cooking");
   run.visit("stove");
   ok("C03_V26_DETAILS".equals(run.p.step),"cooking minigame done");
   ok(run.scenes.contains("V469-C03-COOK-CALLBACK-"+new String[]{"LAUGH","LOOK","BLUR"}[photo]),"choice from previous chapter changes cooking scene");
   ok(run.mini.contains("cooking"),"real cooking minigame invoked");
   run.visit("v26_c03_recipe");run.visit("v26_c03_packing");
   ok("V469_C03_HALF_LETTER".equals(run.p.step),"half-letter mandatory quest");
   run.visit(rt.equals("arland")?"v469_half_a":"v469_half_s");
   ok(run.p.hasFlag("HALF_LETTER_FOUND"),"hint not just text: story flag");
   ok(run.p.items.contains("v469_half_letter"),"physical half-letter collectible");
   ok(run.p.step.equals("C03_PICNIC"),"half letter returns to canonical picnic");
   ok(run.music.contains("cinema_small_things_v469"),"original clue theme really invoked");
   Progress round=Progress.fromMap(run.p.toMap(true));
   ok(round.hasFlag("HALF_LETTER_FOUND"),"letter survives save roundtrip");
   ok(round.items.contains("v469_half_letter"),"letter item survives save roundtrip");
   run.visit("picnic");
   ok(run.p.step.equals("C03_V464_GALLERY_PREP"),"gallery canon stage opened");
   ok(run.p.hasFlag("V464_GALLERY_PROMISED"),"canon promise remains");
   run.visit("gallery_seat");
   run.visit("gallery_projector");
   ok(run.p.count("v464_gallery_prep")==2,"two activities alone cannot finish gallery");
   ok(run.p.step.equals("C03_V464_GALLERY_PREP"),"third real gallery task required");
   run.visit("v469_gallery_card");
   ok(run.p.count("v464_gallery_prep")==3,"three unique galery tasks counted");
   ok(run.p.chapters.contains("C03"),"Chapter3 canon marked complete");
   ok(run.p.step.equals(rt.equals("arland")?"C04_A_WAKE":"C04_S_WAKE"),"route-specific Chapter4 handoff");
   ok(run.music.contains("cinema_gallery_promise_v469"),"cinematic gallery score invoked");
   ok(run.cinema>0,"gallery narrative cinematography invoked");
   ok(run.p.hasFlag("V469_C03_GALLERY_PREPARED"),"foreshadow flag saved");
   ok(run.p.items.contains("v469_gallery_invitation"),"gallery card collectible earned");
   ok(run.p.hasFlag(new String[]{"V469_GALLERY_ASK","V469_GALLERY_SCHEDULE"}[card]),"gallery player choice saved");
   ok(run.p.hasFlag(new String[]{"V464_PROMISE_TIME","V464_PROMISE_LISTEN","V464_PROMISE_SIMPLE"}[promise]),"promise choice saved");
   round=Progress.fromMap(run.p.toMap(true));
   ok(round.step.equals(run.p.step)&&round.hasFlag("V469_C03_GALLERY_PREPARED"),"postchapter save/load handoff");
   paths++;
 }
 static void cancelAndLegacy(StoryDb s,QuestDb q,MapDb m){
  for(String rt:Arrays.asList("arland","sofia")){
   Run run=new Run(s,q,m,rt,rt.equals("arland")?"V469_C03_A_FRAME":"V469_C03_S_SCRAP");
   run.cancelNext=true;
   run.visit(rt.equals("arland")?"v469_frame":"v469_scrap");
   ok(run.p.step.equals(rt.equals("arland")?"V469_C03_A_FRAME":"V469_C03_S_SCRAP"),"canceled minigame does not complete quest");
   ok(!run.p.items.contains(rt.equals("arland")?"v469_frame":"v469_scrapbook"),"no reward for canceled minigame");
   run.visit(rt.equals("arland")?"v469_frame":"v469_scrap");
   ok(run.p.step.equals("C03_FREE"),"retry succeeds");
   Run legacy=new Run(s,q,m,rt,"C03_V464_GALLERY_PREP");
   legacy.p.flags.add("V464_PREP_SEAT_DONE");legacy.p.flags.add("V464_PREP_ART_DONE");
   legacy.p.addCount("v464_gallery_prep",2);
   legacy.visit("v469_gallery_card");
   ok(legacy.p.step.equals(rt.equals("arland")?"C04_A_WAKE":"C04_S_WAKE"),"legacy 2/2 gallery save completes with new third task");
   Run post=new Run(s,q,m,rt,"C04_A_WAKE");
   ok(post.e.step()!=null,"legacy save at later chapter remains valid");
  }
 }
 public static void main(String[] args)throws Exception{
  String a=args.length>0?args[0]:"android/assets";
  StoryDb s=new StoryDb(read(a,"story.json"));QuestDb q=new QuestDb(read(a,"quests.json"));
  MapDb m=new MapDb(read(a,"maps.json"),read(a,"props.json"));
  for(String route:Arrays.asList("arland","sofia"))
   for(int intro=0;intro<3;intro++)for(int photo=0;photo<3;photo++)
    for(int corner=0;corner<(route.equals("sofia")?3:1);corner++)
     for(int promise=0;promise<3;promise++)for(int letter=0;letter<2;letter++)
      for(int card=0;card<2;card++)for(int gal=0;gal<2;gal++)
       walk(s,q,m,route,intro,photo,corner,promise,letter,card,gal);
  cancelAndLegacy(s,q,m);
  System.out.println("PASS: "+checks+" C03 runtime checks, "+paths+" full narrative combinations, retries, legacy saves");
 }
}
