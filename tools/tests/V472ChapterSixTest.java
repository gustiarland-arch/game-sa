import com.arlandsofia.olu.logic.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
/** Actual production QuestEngine/ActionRunner sequence for entire Chapter6, both routes. */
public final class V472ChapterSixTest {
 static long checks=0, paths=0;
 static void ok(boolean v,String msg){checks++;if(!v)throw new AssertionError("C06 check "+checks+": "+msg);}
 static String read(String root,String file)throws Exception{return new String(Files.readAllBytes(Paths.get(root,"data",file)),StandardCharsets.UTF_8);}
 static class Sim implements ActionRunner.Presenter {
  final QuestEngine engine;final ActionRunner runner;final Progress p;final StoryDb story;final MapDb maps;
  final Set<String> seen=new HashSet<>();final Set<String> sounds=new HashSet<>();final Map<String,Integer> selected=new HashMap<>();
  boolean cancelNext=false;int endCount=0,creditsCount=0,cines=0;
  Sim(StoryDb s,QuestDb q,MapDb m,String route){
   story=s;maps=m;p=Progress.newGame(route,1,q.firstStep(),m.area(Routes.room(route)));
   p.step="C06_Q_REVEAL";p.area="eternal_garden";p.x=960;p.y=530;
   p.flags.add("V471_BRIDGE_RESTORED");p.flags.add("V471_QUIET_REVEALED");p.flags.add("V465_PROMISE_PROVEN");
   engine=new QuestEngine(s,q,m,p,false);runner=new ActionRunner(engine,this);MapDb.flags=f->p.hasFlag(f);
  }
  void select(String sc,int n){selected.put(sc,n);}
  void at(String id){
   QuestDb.Interactable found=null;
   for(QuestDb.Interactable it:engine.step().interactables)if(it.id.equals(id)&&it.forRoute(p.route)){found=it;break;}
   ok(found!=null,"required interactable " +id+" exists at "+p.step);
   p.area=Routes.resolve(found.area,p.route);
   ok(engine.interactables(p.area).contains(found),"interactable gated correctly: "+id+" step="+p.step);
   runner.run(engine.actionsFor(found));ok(!runner.busy(),"ActionRunner finished: "+id);
  }
  public void playScene(String id,Runnable done){
   StoryDb.Scene s=story.scene(id);ok(s!=null,"scene defined "+id);
   ok("shared".equals(s.route)||p.route.equals(s.route),"route of scene "+id);
   seen.add(id);
   if(!s.choices.isEmpty()){
    int i=selected.getOrDefault(id,0);ok(i>=0&&i<s.choices.size(),"valid selection "+id);
    StoryDb.Choice c=s.choices.get(i);ok(!c.response(p.route).isEmpty(),"branch response exists "+id);
    engine.addFlags(c.flags);
   }
   done.run();
  }
  public void playLines(List<StoryDb.Line> l,String n,Runnable done){done.run();}
  public void openPuzzle(String id,ActionRunner.BoolCallback done){done.done(true);}
  public void openMinigame(String id,ActionRunner.IntCallback done){if(cancelNext){cancelNext=false;done.done(-1);}else done.done(3);}
  public void openShop(String id,Runnable done){done.run();}
  public void warp(String area,float x,float y,String dir,Runnable done){
   String a=Routes.resolve(area,p.route);ok(maps.area(a)!=null,"warp map exists: "+a);
   ok(!maps.area(a).blocked(x,y),"warp spawn unblocked: "+a+" "+x+","+y);
   p.area=a;p.x=x;p.y=y;p.dir=dir;done.run();
  }
  public void chapterCard(String c,Runnable done){done.run();}
  public void chapterEnd(String c,Runnable done){endCount++;done.run();}
  public void credits(Runnable done){creditsCount++;done.run();}
  public void cine(List<Map<String,Object>> cmds,Runnable done){ok(!cmds.isEmpty(),"cine has commands");cines++;done.run();}
  public void toast(String s){}public void sfx(String id){sounds.add(id);}public void music(String id){sounds.add(id);}
  public void emote(String x,String y){}public void companionChanged(boolean on){}public void stepChanged(){}public void onIdle(){}
 }
 static void path(StoryDb s, QuestDb q, MapDb m,String route,int personal,int futures,int before,int closure,int cancel){
  Sim sim=new Sim(s,q,m,route);
  sim.p.flags.add(new String[]{"V467_C01_CHOOSE_LISTEN","V467_C01_CHOOSE_RECORD","V467_C01_CHOOSE_TRACE"}[before]);
  sim.p.flags.add("V469_GALLERY_INVITE_DONE");
  if(route.equals("arland"))sim.p.flags.add(new String[]{"V471_A_CHOOSE_TIME","V471_A_CHOOSE_ASK","V471_A_CHOOSE_HELP"}[before]);
  else{
   sim.p.flags.add(new String[]{"V471_S_CHOOSE_PRESENT","V471_S_CHOOSE_SPACE","V471_S_CHOOSE_LISTEN"}[before]);
   sim.p.flags.add(new String[]{"V468_S_REPLY_YES","V468_S_REPLY_LATER","V468_S_REPLY_NO"}[before]);
  }
  for(int n=0;n<3;n++){
   String id="V472-C06-ILLUSION-"+new String[]{"DATE","PRESENCE","AGREEMENT"}[n]+"-"+(route.equals("arland")?"A":"S");
   sim.select(id,(futures>>n)&1);
  }
  sim.select(route.equals("arland")?"V472-C06-ARLAND-REFLECTION":"V472-C06-SOFIA-REFLECTION",personal);
  sim.select("C06-X01",closure);
  sim.at("q_reveal");ok(sim.p.step.equals("V472_C06_HALL_ENTRY"),"reveal handoff points to new playable chapter arc");
  sim.at("v472_hall_gate");ok(sim.p.step.equals("V472_C06_FUTURES"),"enter future hall");
  ok(sim.p.area.equals("hall_of_tomorrow"),"physical level entry");
  sim.at("v472_future_date");sim.at("v472_future_presence");
  ok(sim.p.step.equals("V472_C06_FUTURES"),"requires all three futures");
  sim.at("v472_future_agreement");
  String tag=route.equals("arland")?"a":"s";
  ok(sim.p.step.equals("V472_C06_REFLECT_"+tag.toUpperCase()),"personal reflection stage");
  sim.at("v472_reflect_"+tag);ok(sim.p.step.equals("V472_C06_ALIGN"),"reflection leads to alignment");
  ok(sim.p.items.contains("v472_c06_future_note"),"personal note awarded");
  for(int i=1;i<=4;i++){
   String chapter="c0"+i;
   sim.at("v472_align_"+chapter);
   if(i<4)ok(sim.p.step.equals("V472_C06_ALIGN"),"all four panels required");
  }
  ok(sim.p.step.equals("V472_C06_PROMISE"),"four memories aligned");
  ok(sim.p.hasFlag("V472_C06_ALIGNED"),"shared memory flag saved");
  ok(sim.p.items.contains("v472_c06_two_sides"),"two view collectible");
  ok(sim.seen.contains("V472-C06-REAL-C04"),"gallery conflict receives payoff");
  sim.at("v472_listen");ok(sim.p.step.equals("V472_C06_PROMISE"),"real listening is required");
  sim.at("v472_return");ok(sim.p.step.equals("C06_LETTER"),"returns to legacy letter stage");
  ok(sim.p.area.equals("eternal_garden"),"back to existing original garden");
  if(cancel!=0){
   Progress loaded=Progress.fromMap(sim.p.toMap(true));
   ok(loaded.step.equals("C06_LETTER"),"save reload preserves new endgame step");
   ok(loaded.hasFlag("V472_C06_ALIGNED"),"save reload remembers aligned memories");
   ok(loaded.hasFlag(route.equals("arland")?new String[]{"V472_A_FUTURE_LISTEN","V472_A_FUTURE_PRESENT","V472_A_FUTURE_HELP"}[personal]:
            new String[]{"V472_S_FUTURE_VOICE","V472_S_FUTURE_SPACE","V472_S_FUTURE_COURAGE"}[personal]),"save reload remembers personal choice");
  }
  sim.at("letter_"+tag);ok(sim.p.step.equals("C06_TREE"),"original route letter still playable");
  sim.at("tree");ok(sim.p.step.equals("C06_FINAL"),"original canon finale is unchanged");
  if(cancel!=0){sim.cancelNext=true;sim.at("pages");ok(sim.p.step.equals("C06_FINAL"),"cancel final puzzle has retry path");ok(sim.creditsCount==0,"cancel does not give credits");}
  sim.at("pages");ok(sim.p.step.equals("EPI_FEST_GO"),"one canon ending and epilogue handoff");
  ok(sim.creditsCount==1,"canon credits triggered once");
  ok(sim.endCount==1,"canon C06 end triggered once");
  ok(sim.seen.contains("C06-X01"),"one original final canon scene");
  ok(sim.seen.contains(route.equals("arland")?"V472-C06-PAYOFF-ARLAND":"V472-C06-PAYOFF-SOFIA"),"route-specific final acknowledgement");
  ok(sim.seen.contains("V472-ECHO-"+(route.equals("arland")?"A_FUTURE_":"S_FUTURE_")+new String[][]{{"LISTEN","PRESENT","HELP"},{"VOICE","SPACE","COURAGE"}}[route.equals("arland")?0:1][personal]),"personally selected promise echoes before ending");
  for(int n=0;n<3;n++){
   String name=new String[]{"DATE","PRESENCE","AGREEMENT"}[n];
   String futureTag=route.equals("arland")?"A":"S";
   String chosen=((futures>>n)&1)==0?"SEE":"REFUSE";
   String other=chosen.equals("SEE")?"REFUSE":"SEE";
   ok(sim.seen.contains("V472-C06-RECALL-"+name+"-"+futureTag+"-"+chosen),"future response recalls actual choice");
   ok(!sim.seen.contains("V472-C06-RECALL-"+name+"-"+futureTag+"-"+other),"opposite choice does not falsely appear");
  }
  ok(sim.cines>=2,"original cinematic transitions are executed");
  paths++;
 }
 static void legacySaveAndEpilogue(StoryDb s,QuestDb q,MapDb m){
  for(String route:new String[]{"arland","sofia"})for(int c=0;c<3;c++){
   String tag=route.equals("arland")?"a":"s";
   String fl=route.equals("arland")?new String[]{"V472_A_FUTURE_LISTEN","V472_A_FUTURE_PRESENT","V472_A_FUTURE_HELP"}[c]:
        new String[]{"V472_S_FUTURE_VOICE","V472_S_FUTURE_SPACE","V472_S_FUTURE_COURAGE"}[c];
   // Old C06_LETTER save contains no new flags: it must reach canon finale safely.
   Sim old=new Sim(s,q,m,route);old.p.step="C06_LETTER";
   old.at("letter_"+tag);old.at("tree");old.at("pages");
   ok(old.p.step.equals("EPI_FEST_GO"),"older C06 letter save still finishes without new flags");
   ok(old.creditsCount==1,"legacy save sees one ending");
   // Epilogue must recall the exact future promise after the Lantern Festival.
   Sim epi=new Sim(s,q,m,route);epi.p.step="EPI_FEST_LEPAS";epi.p.area="taman_kota";
   epi.p.flags.add(fl);
   epi.at("fest_release");
   ok(epi.p.step.equals("V473_EPI_PLAZA"),"updated epilogue is a playable memory journey");
   epi.at("v473_plaza_memory");epi.at("v473_cafe_memory");epi.at("v473_gallery_memory");
   epi.at("v473_lake_photo");epi.at("v473_lake_letter");epi.at("v473_lake_ready");epi.at("v473_final_bench");
   ok(epi.p.step.equals("EPI_FREE"),"coda reaches postgame free roam after playable memories");
   ok(epi.seen.contains("V472-EPI-"+fl.substring(5)),"actual personal reflection revisited after credits");
   ok(!epi.seen.contains("V472-EPI-"+(route.equals("arland")?"S_FUTURE_VOICE":"A_FUTURE_LISTEN")),"wrong route coda never shown");
  }
 }
 public static void main(String[] args)throws Exception{
  String root=args[0];StoryDb s=new StoryDb(read(root,"story.json"));QuestDb q=new QuestDb(read(root,"quests.json"));MapDb m=new MapDb(read(root,"maps.json"),read(root,"props.json"));
  for(String route:new String[]{"arland","sofia"})for(int choice=0;choice<3;choice++)for(int futures=0;futures<8;futures++)for(int before=0;before<3;before++)for(int ending=0;ending<2;ending++)for(int cancel=0;cancel<2;cancel++)
   path(s,q,m,route,choice,futures,before,ending,cancel);
  legacySaveAndEpilogue(s,q,m);
  System.out.println("PASS C06: "+paths+" actual ActionRunner routes / "+checks+" checks, 3 futures, 4 memory panels, save reload, cancel/retry, one canon ending, 6 epilogue callbacks and legacy saves");
 }
}
