import com.arlandsofia.olu.logic.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Functional C05 branch runner using actual production QuestEngine/ActionRunner, no APK claims. */
public final class V471ChapterFiveTest {
 static int checks=0,paths=0;
 static void ok(boolean b,String msg){checks++;if(!b)throw new AssertionError("C05 #"+checks+" "+msg);}
 static String read(String root,String name)throws Exception{return new String(Files.readAllBytes(Paths.get(root,"data",name)),StandardCharsets.UTF_8);}
 static class Sim implements ActionRunner.Presenter {
  final QuestEngine engine;final ActionRunner runner;final Progress p;final StoryDb story;final MapDb maps;
  final Map<String,Integer> choices=new HashMap<>();final Set<String> seen=new HashSet<>(),tracks=new HashSet<>(),games=new HashSet<>();
  int cine=0;boolean cancelNextMini=false;
  Sim(StoryDb ss, QuestDb qq, MapDb mm,String route){
   story=ss;maps=mm;p=Progress.newGame(route,1,qq.firstStep(),mm.area(Routes.room(route)));
   p.step="C05_V26_STARGAZE";p.area="starfall_village";p.x=960;p.y=760;
   engine=new QuestEngine(ss,qq,mm,p,false);runner=new ActionRunner(engine,this);
   MapDb.flags=f->p.hasFlag(f);
  }
  void select(String id,int i){choices.put(id,i);}
  void at(String id){
   QuestDb.Interactable it=null;
   for(QuestDb.Interactable v:engine.step().interactables)if(v.id.equals(id)&&v.forRoute(p.route)){it=v;break;}
   ok(it!=null,"Interactable exists "+id+" at "+p.step);
   p.area=Routes.resolve(it.area,p.route);
   ok(engine.interactables(p.area).contains(it),"Interactable reachable via quest condition "+id);
   runner.run(engine.actionsFor(it));ok(!runner.busy(),"ActionRunner does not hang "+id);
  }
  public void playScene(String id,Runnable done){
   StoryDb.Scene sc=story.scene(id);ok(sc!=null,"Scene exists "+id);
   ok("shared".equals(sc.route)||p.route.equals(sc.route),"Scene route correct "+id);
   seen.add(id);
   if(!sc.choices.isEmpty()){
    int n=choices.getOrDefault(id,0);ok(n>=0&&n<sc.choices.size(),"Choice range "+id);
    StoryDb.Choice ch=sc.choices.get(n);
    ok(!ch.response(p.route).isEmpty(),"Choice has route response "+id);
    engine.addFlags(ch.flags);
   }
   done.run();
  }
  public void playLines(List<StoryDb.Line> lines,String n,Runnable done){done.run();}
  public void openPuzzle(String n,ActionRunner.BoolCallback done){done.done(true);}
  public void openMinigame(String n,ActionRunner.IntCallback done){games.add(n);if(cancelNextMini){cancelNextMini=false;done.done(-1);}else done.done(3);}
  public void openShop(String n,Runnable done){done.run();}
  public void warp(String area,float x,float y,String dir,Runnable done){
   String a=Routes.resolve(area,p.route);ok(maps.area(a)!=null,"Map exists "+a);
   ok(!maps.area(a).blocked(x,y),"Warp spawn walkable "+a+" "+x+" "+y);
   p.area=a;p.x=x;p.y=y;p.dir=dir;done.run();
  }
  public void chapterCard(String n,Runnable done){done.run();}
  public void chapterEnd(String n,Runnable done){done.run();}
  public void credits(Runnable done){done.run();}
  public void cine(List<Map<String,Object>> c,Runnable done){ok(!c.isEmpty(),"Cinema commands valid");cine++;done.run();}
  public void toast(String msg){}public void sfx(String n){}public void music(String n){tracks.add(n);}
  public void emote(String who,String what){}public void companionChanged(boolean yes){}public void stepChanged(){}public void onIdle(){}
 }
 static void path(StoryDb s,QuestDb q,MapDb m,String route,int routeChoice,int quietChoice,int conflict,int resume){
  Sim t=new Sim(s,q,m,route);
  t.p.flags.add("V470_C04_REPAIR_EARNED");
  String[] aa={"V464_A_WARN","V464_A_SILENT","V464_A_HELP"};
  String[] bb={"V470_S_NEED_PRESENT","V470_S_NEED_UPDATE","V470_S_NEED_LISTEN"};
  t.p.flags.add(route.equals("arland")?aa[conflict]:bb[conflict]);
  t.p.flags.add(new String[]{"V467_C01_CHOOSE_LISTEN","V467_C01_CHOOSE_RECORD","V467_C01_CHOOSE_TRACE"}[routeChoice]);
  t.p.flags.add("V469_GALLERY_INVITE_DONE");
  if(route.equals("sofia"))t.p.flags.add(new String[]{"V468_S_REPLY_YES","V468_S_REPLY_LATER","V468_S_REPLY_NO"}[conflict]);
  t.select(route.equals("arland")?"V471-C05-A-CHOICE":"V471-C05-S-CHOICE",routeChoice);
  t.select("V471-C05-QUIET-REVEAL",quietChoice);
  t.at("v26_stargaze");ok(t.p.step.equals("V471_C05_CLOCK_ENTRY"),"Old Stargaze enters expanded real C05 journey");
  t.at("v471_clock_gate");
  ok(t.p.step.equals(route.equals("arland")?"V471_C05_CLOCK_A":"V471_C05_CLOCK_S"),"Separate clock route");
  String tag=route.equals("arland")?"a":"s";
  for(int i=1;i<=3;i++){
   t.at("v471_"+tag+"_clock_"+i);
   if(i<3)ok(t.p.step.equals("V471_C05_CLOCK_"+tag.toUpperCase()),"Clock requires 3 independent observations");
  }
  ok(t.p.step.equals("V471_C05_CLOCK_PUZZLE_"+tag.toUpperCase()),"Three observations unlock retriable puzzle");
  if(resume==1){
   t.cancelNextMini=true;t.at("v471_clock_puzzle_"+tag);
   ok(t.p.step.equals("V471_C05_CLOCK_PUZZLE_"+tag.toUpperCase()),"Minigame cancel cannot softlock chapter");
   ok(!t.p.hasFlag("V471_CLOCK_"+tag.toUpperCase()+"_DONE"),"Cancel does not grant success");
  }
  t.at("v471_clock_puzzle_"+tag);
  ok(t.p.step.equals("V471_C05_CLOCK_SWITCHES"),"Correct handoff to clock switches");
  ok(t.games.contains(route.equals("arland")?"v26_night_compass":"v26_night_pages"),"Real route-specific native puzzle invoked");
  ok(t.p.items.contains("v471_clock_piece"),"Clock item persisted");
  t.at("v471_clock_switch_one");ok(t.p.step.equals("V471_C05_CLOCK_SWITCHES"),"Two switches required");
  t.at("v471_clock_switch_two");ok(t.p.step.equals(route.equals("arland")?"V471_C05_MOON_A":"V471_C05_MOON_S"),"Moon route stage");
  if(resume==1){
   Progress save=Progress.fromMap(t.p.toMap(true));ok(save.step.equals(t.p.step),"Save reload keeps new quest id");
   ok(save.area.equals(t.p.area),"Save reload keeps new area");
   ok(save.items.contains("v471_clock_piece"),"Save reload keeps inventory");
  }
  t.at("v471_moon_reflect_"+tag);
  ok(t.p.step.equals("V471_C05_MOON_SHARED"),"Moon view done");
  String[] flags=route.equals("arland")?new String[]{"V471_A_CHOOSE_TIME","V471_A_CHOOSE_ASK","V471_A_CHOOSE_HELP"}:
     new String[]{"V471_S_CHOOSE_PRESENT","V471_S_CHOOSE_SPACE","V471_S_CHOOSE_LISTEN"};
  ok(t.p.hasFlag(flags[routeChoice]),"Moon choice truly retained");
  if(route.equals("arland"))ok(t.seen.contains("V471-C05-MOON-C04-"+new String[]{"WARN","SILENT","HELP"}[conflict]),"Old projector decision acknowledged");
  else ok(t.seen.contains("V471-C05-MOON-S-"+new String[]{"PRESENT","UPDATE","LISTEN"}[conflict]),"Old Sofia boundary acknowledged");
  t.at("v471_moon_listen");ok(t.p.step.equals("V471_C05_MOON_SHARED"),"Two reflections required");
  t.at("v471_moon_note");ok(t.p.step.equals("V471_C05_BRIDGE_FRAGMENTS"),"Bridge begins only after two views");
  for(String key:new String[]{"presence","voice","time","space","tomorrow"})t.at("v471_fragment_"+key);
  ok(t.p.step.equals("V471_C05_BRIDGE_SEQUENCE"),"Five fragments required before four-alignment sequence");
  ok(t.p.count("v471_fragments")==5,"Exactly five fragments recorded");
  for(int i=1;i<=4;i++)t.at("v471_bridge_panel_"+i);
  ok(t.p.step.equals("V471_C05_BRIDGE_PUZZLE"),"All four old chapter memories required");
  ok(t.p.count("v471_panels")==4,"Four distinct chapters linked to puzzle");
  if(resume==1){t.cancelNextMini=true;t.at("v471_bridge_alignment");ok(t.p.step.equals("V471_C05_BRIDGE_PUZZLE"),"Bridge puzzle cancellation safe");}
  t.at("v471_bridge_alignment");ok(t.p.step.equals("V471_C05_QUIET_TRUTH"),"Actual native bridge minigame unlocks keeper");
  ok(t.seen.contains("V471-C05-BRIDGE-C01-"+new String[]{"LISTEN","RECORD","TRACE"}[routeChoice]),"C01 choice changes C05 scene");
  ok(t.seen.contains("V471-C05-BRIDGE-PROMISE"),"C03 gallery promise echoed in C05");
  if(route.equals("sofia"))ok(t.seen.contains("V471-C05-BRIDGE-S-"+new String[]{"YES","LATER","NO"}[conflict]),"C02 Sofias autonomy echoed");
  t.at("v471_lumi_truth");ok(t.p.hasFlag("V471_QUIET_REVEALED"),"Mystery reveals only after reaching keeper");
  ok(t.p.hasFlag(new String[]{"V471_QUIET_LISTEN","V471_QUIET_REMEMBER","V471_QUIET_FUTURE"}[quietChoice]),"Quiet choice meaningful");
  ok(t.p.step.equals("V471_C05_BRIDGE_RESTORE"),"Bridge repair step");
  ok(!t.engine.interactables("memory_bridge").stream().anyMatch(it->it.id.equals("v471_bridge_step")),"Cannot skip first repair phase");
  t.at("v471_bridge_mend");
  t.at("v471_bridge_step");ok(t.p.hasFlag("V471_BRIDGE_RESTORED"),"Bridge repair flag");
  t.at("v471_final_walk");ok(t.p.step.equals("C05_Q_ECHO"),"Resumes historical C05 ending step without removing save IDs");
  ok(t.seen.contains(route.equals("arland")?"V471-C05-FINAL-A":"V471-C05-FINAL-S"),"Route-specific emotional reflection");
  ok(t.tracks.contains("cinema_clockwork_v471")&&t.tracks.contains("cinema_two_sides_v471")&&t.tracks.contains("cinema_quiet_reveal_v471"),"New music cues actually executed");
  ok(t.cine>=3,"All key scenes have actual cinematography");
  t.at("q_echo");ok("C06_PETALS".equals(t.p.step),"Reaches Chapter6 correctly");
  ok(t.p.chapters.contains("C05"),"C05 actually finished");
  Progress loaded=Progress.fromMap(t.p.toMap(true));ok(loaded.hasFlag("V471_BRIDGE_RESTORED")&&loaded.hasFlag(flags[routeChoice]),"Save preserves consequences into C06");
  paths++;
 }
 public static void main(String[] args)throws Exception{
  String root=args.length>0?args[0]:"android/assets";
  StoryDb ss=new StoryDb(read(root,"story.json"));QuestDb qq=new QuestDb(read(root,"quests.json"));MapDb mm=new MapDb(read(root,"maps.json"),read(root,"props.json"));
  for(String rt:new String[]{"arland","sofia"}){
   Sim legacy=new Sim(ss,qq,mm,rt);legacy.p.step="C05_Q_ECHO";
   legacy.at("q_echo");ok("V471_C05_CLOCK_ENTRY".equals(legacy.p.step),"Legacy C05 save can't skip expanded story");
  }
  for(String rt:new String[]{"arland","sofia"})for(int a=0;a<3;a++)for(int b=0;b<3;b++)for(int c=0;c<3;c++)for(int d=0;d<2;d++)path(ss,qq,mm,rt,a,b,c,d);
  System.out.println("PASS V471 Chapter5: "+paths+" real engine paths / "+checks+" assertions, two routes, five fragments, bridge, old callbacks, save and C06 handoff");
 }
}
