import com.arlandsofia.olu.logic.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Chapter 4 full two-route quest runner, uses production QuestEngine and ActionRunner. */
public final class V470ChapterFourTest {
 static int checks=0,paths=0;
 static void ok(boolean b,String m){checks++;if(!b)throw new AssertionError("C04 #"+checks+" "+m);}
 static String read(String r,String n)throws Exception{return new String(Files.readAllBytes(Paths.get(r,"data",n)),StandardCharsets.UTF_8);}
 static final class Sim implements ActionRunner.Presenter {
  final QuestEngine engine; final ActionRunner runner;final Progress p;final StoryDb story;final MapDb map;
  final Map<String,Integer> choice=new HashMap<>();final Set<String> sceneSeen=new HashSet<>(),music=new HashSet<>(),mini=new HashSet<>();
  int cineCount=0; boolean cancel;
  Sim(StoryDb s, QuestDb q, MapDb m,String route,String start){story=s;map=m;
   p=Progress.newGame(route,1,q.firstStep(),m.area(Routes.room(route)));p.step=start;
   engine=new QuestEngine(s,q,m,p,false);runner=new ActionRunner(engine,this);
   MapDb.flags=f->p.hasFlag(f);
  }
  void pick(String sc,int n){choice.put(sc,n);}
  void interact(String id){
    QuestDb.Interactable item=null;
    for(QuestDb.Interactable it:engine.step().interactables)if(it.id.equals(id)&&it.forRoute(p.route)){item=it;break;}
    ok(item!=null,"interaction "+id+" exists at "+p.step);
    p.area=Routes.resolve(item.area,p.route);
    ok(engine.interactables(p.area).contains(item),"interaction available: "+id+" at "+p.step);
    runner.run(engine.actionsFor(item));ok(!runner.busy(),"no hanging dialog: "+id);
  }
  public void playScene(String id,Runnable done){
    StoryDb.Scene sc=story.scene(id);ok(sc!=null,"scene exists "+id);
    ok(sc.route.equals("shared")||sc.route.equals(p.route),"scene route "+id);
    sceneSeen.add(id);
    if(!sc.choices.isEmpty()){
      int pick=choice.getOrDefault(id,0);
      ok(pick>=0&&pick<sc.choices.size(),"choice range "+id);
      StoryDb.Choice ch=sc.choices.get(pick);ok(!ch.response(p.route).isEmpty(),"choice response "+id);
      engine.addFlags(ch.flags);
    }
    done.run();
  }
  public void playLines(List<StoryDb.Line> lines,String n,Runnable done){done.run();}
  public void openPuzzle(String n,ActionRunner.BoolCallback done){done.done(true);}
  public void openMinigame(String n,ActionRunner.IntCallback done){mini.add(n);if(cancel){cancel=false;done.done(-1);}else done.done(3);}
  public void openShop(String n,Runnable done){done.run();}
  public void warp(String area,float x,float y,String dir,Runnable done){
    String a=Routes.resolve(area,p.route);ok(map.area(a)!=null,"warp area exists "+a);
    ok(!map.area(a).blocked(x,y),"warp not blocked: "+a+" "+x+","+y);
    p.area=a;p.x=x;p.y=y;p.dir=dir;done.run();
  }
  public void chapterCard(String ch,Runnable d){d.run();}public void chapterEnd(String ch,Runnable d){d.run();}
  public void credits(Runnable d){d.run();}
  public void cine(List<Map<String,Object>> cmds,Runnable d){ok(!cmds.isEmpty(),"cinematic commands");cineCount++;d.run();}
  public void toast(String s){}public void sfx(String id){}public void music(String id){music.add(id);}
  public void emote(String who,String emote){}public void companionChanged(boolean on){}
  public void stepChanged(){}public void onIdle(){}
 }
 static void path(StoryDb s,QuestDb q,MapDb m,String rt,int strategy,int conflict,int rain,int reflect,int reunion,int legacy){
  Sim e=new Sim(s,q,m,rt,rt.equals("arland")?"C04_A_WAKE":"C04_S_WAKE");
  if(rt.equals("arland")){
   e.pick("V464-C04-A-PROJECTOR",strategy);
   e.pick("V465-C04-A-GALLERY-RETURN",reflect);
   if(legacy==0)e.p.flags.add("V469_A_LETTER_ASK");else e.p.flags.add("V469_A_LETTER_NOTE");
  }else{
   e.pick("V470-C04-S-REHEARSE",strategy);
   e.pick("V464-C04-S-AFTER",conflict);
   e.pick("V465-C04-S-GALLERY-RETURN",reflect);
   e.pick("V470-C04-S-BOUNDARY",rain);
   if(legacy==0)e.p.flags.add("V469_S_LETTER_HONEST");else e.p.flags.add("V469_S_LETTER_WAIT");
  }
  String promiseFlag=new String[]{"V464_PROMISE_TIME","V464_PROMISE_LISTEN","V464_PROMISE_SIMPLE"}[(strategy+rain)%3];
  String invitationFlag=new String[]{"V469_GALLERY_ASK","V469_GALLERY_SCHEDULE"}[legacy];
  String oldC02Flag=rt.equals("arland")?new String[]{"V468_A_INVITE_SIMPLE","V468_A_INVITE_CARE","V468_A_INVITE_OPEN"}[strategy]:
            new String[]{"V468_S_REPLY_YES","V468_S_REPLY_LATER","V468_S_REPLY_NO"}[strategy];
  e.p.flags.add(promiseFlag);e.p.flags.add(invitationFlag);e.p.flags.add(oldC02Flag);
  e.pick("C04-X00",rain);e.pick("C04-X01",strategy%2);
  e.pick("V465-C04-SECOND-TALK",reunion);
  e.interact("phone4");
  if(rt.equals("arland")){
   ok("C04_V464_A_PROJECTOR".equals(e.p.step),"projector gate from wake");
   e.interact("projector_v464");
   if(strategy==0){ok("V470_C04_A_WARN".equals(e.p.step),"warn distinct stage");e.interact("v470_a_message");ok(e.p.hasFlag("V470_A_WARN_DONE"),"real warning sent");}
   if(strategy==1){ok("V470_C04_A_SILENT".equals(e.p.step),"silent distinct stage");e.interact("v470_a_fuse");
     ok("V470_C04_A_SILENT".equals(e.p.step),"repair requires 2 real actions");e.interact("v470_a_screen");}
   if(strategy==2){ok("V470_C04_A_HELP".equals(e.p.step),"help distinct stage");e.interact("v470_a_call");
     ok("V470_C04_A_HELP_OUT".equals(e.p.step),"help required follow-up");e.interact("v470_a_depart");}
   ok("C04_V464_A_GALLERY".equals(e.p.step),"gallery gate");e.interact("empty_chair_a");
   ok("V470_C04_A_AFTER".equals(e.p.step),"gallery witness stage");
   e.interact("v470_a_witness");e.interact("v470_a_ticket");
   ok(e.p.items.contains("v470_ticket"),"gallery physical ticket");
   ok(e.p.hasFlag(new String[]{"V464_A_WARN","V464_A_SILENT","V464_A_HELP"}[strategy]),"projector choice saved");
   ok(e.sceneSeen.contains("V470-C04-A-"+new String[]{"WARN","SILENT","HELP"}[strategy]+"-SEEN"),"outcome alters gallery dialogue");
  } else {
   ok("V470_C04_S_PREP".equals(e.p.step),"Sofia has playable presentation prep");
   e.interact("v470_s_note");ok("V470_C04_S_PREP".equals(e.p.step),"two actions required before presenting");
   e.interact("v470_s_rehearse");ok("C04_V464_S_GALLERY".equals(e.p.step),"presentation unlocked");
   e.interact("stage_s_v464");ok(e.sceneSeen.contains("V470-C04-S-PRESENT-"+new String[]{"FLOWER","WORK","GUESTS"}[strategy]),"real presentation variant visible");
   e.interact("chair_s_v464");ok("V470_C04_S_AFTER".equals(e.p.step),"private gallery followup playable");
   e.interact("v470_s_sketch");e.interact("v470_s_lights");
   ok(e.p.items.contains("v470_empty_chair_sketch"),"Sofia sketch collectible");
   ok(e.p.hasFlag(new String[]{"V464_S_SPACE","V464_S_SPEAK","V464_S_DRAW"}[conflict]),"hurt response persisted");
  }
  ok(e.sceneSeen.contains("V470-C04-PROMISE-"+new String[]{"TIME","LISTEN","SIMPLE"}[(strategy+rain)%3]),
     "Chapter3 exact promise callback appears in gallery");
  ok(e.sceneSeen.contains("V470-C04-INVITE-"+(legacy==0?"ASK":"SCHEDULE")),
     "Chapter3 exact invitation callback appears in gallery");
  ok(e.sceneSeen.contains("V470-C04-C02-"+(rt.equals("arland")?"A-":"S-")+
      new String[]{rt.equals("arland")?"SIMPLE":"YES",rt.equals("arland")?"CARE":"LATER",rt.equals("arland")?"OPEN":"NO"}[strategy]),
     "Chapter2 remembered in Chapter4 gallery");
  ok(e.p.step.equals(rt.equals("arland")?"C04_A_CAFE":"C04_S_CAFE"),"original rain chapter resumes");
  if(rt.equals("arland")){
   for(String i:new String[]{"raka4","halte","mbox","q_a_reply","meet4"})e.interact(i);
  }else{
   for(String i:new String[]{"raka4","laras4","read4","q_s_reply","gazebo4","meet4"})e.interact(i);
  }
  ok("C04_LIGHTS".equals(e.p.step),"reached five lanterns");
  ok(e.p.area.equals("rain_garden"),"C04 walks in dedicated Rain Garden, not reused Lantern Field");
  ok(e.engine.weatherNow().equals(WorldClock.HUJAN),"Rain Garden has deterministic emotional rain weather");
  ok(e.p.hasFlag(new String[]{"V464_REPAIR_SPACE","V464_REPAIR_OWN","V464_REPAIR_LETTER"}[rain]),"rain dialogue choice retained");
  ok(e.sceneSeen.contains("V470-C04-LETTER-"+(rt.equals("arland")?"A-":"S-")+
      (rt.equals("arland")?(legacy==0?"ASK":"NOTE"):(legacy==0?"HONEST":"WAIT"))),"C03 letter changed C04 actual dialogue");
  // Prevent repeated counting on already finished lights.
  for(String i:new String[]{"light_listen","light_honest","v470_light_presence","v470_light_boundary"})e.interact(i);
  ok("C04_LIGHTS".equals(e.p.step),"four of five lights must not advance");
  ok(e.p.count("cahaya")==4,"four lights counted");
  e.interact("v470_light_update");
  ok("C04_PUZZLE".equals(e.p.step),"all five lights gate puzzle");
  e.interact("shrine");ok("C04_V26_RECONCILE".equals(e.p.step),"lantern minigame opened rainy reflection");
  ok(e.mini.contains("lanterns"),"real lanterns minigame invoked");
  e.interact("v26_c04_gazebo");e.interact("v26_c04_pond");
  ok("C04_V26_VOW".equals(e.p.step),"two shared reflection tasks");
  e.interact("v26_c04_vow");ok(e.p.step.equals(rt.equals("arland")?"C04_V465_A_REFLECT":"C04_V465_S_REFLECT"),"existing route repair stage");
  e.interact(rt.equals("arland")?"v465_a_gallery":"v465_s_gallery");
  ok(e.p.step.equals(rt.equals("arland")?"V470_C04_A_PROOF":"V470_C04_S_PROOF"),"real repair proof must happen before reconciliation");
  if(rt.equals("arland")){e.interact("v470_a_agenda");e.interact("v470_a_listen");}
  else {e.interact("v470_s_boundaries");e.interact("v470_s_art");}
  ok("C04_V465_SECOND_TALK".equals(e.p.step),"proof tasks unlock reunion");
  e.interact("v465_second_talk");
  ok(e.p.chapters.contains("C04"),"chapter complete");
  ok(e.p.step.equals("C05_FREE"),"safe transition to Chapter5");
  ok(e.p.hasFlag("V470_C04_REPAIR_EARNED"),"reconciliation requires actions");
  ok(e.p.items.contains("v470_two_sides"),"memory artifact granted");
  ok(e.music.contains("cinema_empty_seat_v470")&&e.music.contains("cinema_rain_five_lights_v470")&&e.music.contains("cinema_listen_again_v470"),"new original music actually plays");
  ok(e.cineCount>=2,"new cinematography used");
  Progress loaded=Progress.fromMap(e.p.toMap(true));
  ok(loaded.step.equals("C05_FREE")&&loaded.hasFlag("V470_C04_REPAIR_EARNED"),"save/load checkpoint");
  ok(loaded.items.contains("v470_two_sides"),"memory keeps through serialization");
  paths++;
 }
 static void retry(StoryDb s,QuestDb q,MapDb m){
   Sim e=new Sim(s,q,m,"arland","C04_PUZZLE");e.cancel=true;e.interact("shrine");
   ok("C04_PUZZLE".equals(e.p.step),"canceled lantern puzzle cannot advance");
   ok(!e.p.hasFlag("C04_LANTERNS_LIT"),"no reward on canceled minigame");e.interact("shrine");
   ok("C04_V26_RECONCILE".equals(e.p.step),"retry works");
 }
 public static void main(String[] args)throws Exception{
  String root=args.length>0?args[0]:"android/assets";
  StoryDb s=new StoryDb(read(root,"story.json"));QuestDb q=new QuestDb(read(root,"quests.json"));
  MapDb m=new MapDb(read(root,"maps.json"),read(root,"props.json"));
  for(String route:new String[]{"arland","sofia"})for(int a=0;a<3;a++)for(int c=0;c<3;c++)
   for(int rain=0;rain<3;rain++)for(int reflect=0;reflect<3;reflect++)for(int legacy=0;legacy<2;legacy++)
    path(s,q,m,route,a,c,rain,reflect,(a+c+rain+reflect)%3,legacy);
  retry(s,q,m);
  System.out.println("PASS: "+paths+" playable Chapter4 routes, "+checks+" QuestEngine/ActionRunner checks including C03 flags, 5 lanterns, save, music, Chapter5");
 }
}
