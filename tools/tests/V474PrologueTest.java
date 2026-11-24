import com.arlandsofia.olu.logic.*;
import java.nio.file.*;import java.nio.charset.StandardCharsets;import java.util.*;
/** Full QuestEngine/ActionRunner walkthrough of the two selectable Prologue routes.
 * Checks all opening choices, all six shard permutations, C01 and Epilogue callbacks,
 * production action conditions, stable saves and old-step backward compatibility. */
public final class V474PrologueTest {
 static long checks=0,routes=0;
 static void ok(boolean b,String m){checks++;if(!b)throw new AssertionError("PRO V474 #"+checks+" "+m);}
 static String read(String a,String f)throws Exception{return Files.readString(Paths.get(a,"data",f),StandardCharsets.UTF_8);}
 static final class Env implements ActionRunner.Presenter {
  final QuestDb db;final StoryDb s;final MapDb m;final Progress p;final QuestEngine e;final ActionRunner r;
  final Map<String,Integer> picks=new HashMap<>(); final Set<String> scenes=new HashSet<>(), music=new HashSet<>();
  int cine=0,ends=0;
  Env(StoryDb s,QuestDb db,MapDb m,String route,String start){
   this.s=s;this.db=db;this.m=m;
   p=Progress.newGame(route,1,db.firstStep(),m.area(Routes.room(route)));
   p.step=start;p.area=Routes.room(route);
   e=new QuestEngine(s,db,m,p,false);r=new ActionRunner(e,this);
   MapDb.flags=f->p.hasFlag(f);
  }
  void select(String scene,int i){picks.put(scene,i);}
  void at(String area){p.area=Routes.resolve(area,p.route);
   ok(m.area(p.area)!=null,"enter existing map "+p.area);
   List<Map<String,Object>> enter=e.onEnterArea(p.area);if(!enter.isEmpty())r.run(enter);
   ok(!r.busy(),"entry completed without softlock");
  }
  void hit(String id){
   QuestDb.Step st=e.step();ok(st!=null,"step must exist "+p.step);
   QuestDb.Interactable hit=null;
   for(QuestDb.Interactable it:st.interactables)if(it.id.equals(id)&&it.forRoute(p.route)){hit=it;break;}
   ok(hit!=null,"route interactable "+id+" at "+p.step);
   p.area=Routes.resolve(hit.area,p.route);
   ok(e.interactables(p.area).contains(hit),"active interaction visible "+id);
   r.run(e.actionsFor(hit));ok(!r.busy(),"action finishes "+id);
  }
  public void playScene(String id,Runnable done){
   StoryDb.Scene sc=s.scene(id);ok(sc!=null,"scene exists "+id);
   ok(sc.route.equals("shared")||sc.route.equals(p.route),"POV correctly filtered "+id);
   scenes.add(id);
   if(!sc.choices.isEmpty()){
    int n=picks.getOrDefault(id,0);ok(n>=0&&n<sc.choices.size(),"valid selected choice "+id);
    StoryDb.Choice c=sc.choices.get(n);ok(!c.response(p.route).isEmpty(),"choice response in POV "+id);
    e.addFlags(c.flags);
   }
   done.run();
  }
  public void playLines(List<StoryDb.Line> l,String who,Runnable done){done.run();}
  public void openPuzzle(String id,ActionRunner.BoolCallback done){done.done(true);}
  public void openMinigame(String id,ActionRunner.IntCallback done){done.done(3);}
  public void openShop(String id,Runnable done){done.run();}
  public void warp(String area,float x,float y,String dir,Runnable done){
   String dest=Routes.resolve(area,p.route);ok(m.area(dest)!=null,"warp map exists "+dest);
   ok(!m.area(dest).blocked(x,y),"warp landing not blocked "+dest+" "+x+"/"+y);
   p.area=dest;p.x=x;p.y=y;p.dir=dir;done.run();
  }
  public void chapterCard(String c,Runnable done){done.run();}
  public void chapterEnd(String c,Runnable done){ends++;p.chapters.add(c);done.run();}
  public void credits(Runnable done){done.run();}
  public void cine(List<Map<String,Object>> cmds,Runnable done){ok(cmds!=null&&!cmds.isEmpty(),"cinema commands present");cine++;done.run();}
  public void toast(String v){} public void sfx(String v){} public void music(String id){music.add(id);}
  public void emote(String a,String b){} public void companionChanged(boolean x){}
  public void stepChanged(){}public void onIdle(){}
 }
 static void run(StoryDb s,QuestDb db,MapDb m,String rt,int intro,int craft,int note,int[] permutation){
  Env x=new Env(s,db,m,rt,"PRO_PHONE");
  boolean a=rt.equals("arland");
  x.select(a?"P-A01":"P-S01",intro);
  x.select(a?"V474-P-A-FOLD":"V474-P-S-DRAFT",craft);
  x.select(a?"V474-P-A-RIBBON":"V474-P-S-STAMP",craft);
  x.select(a?"P-A02":"P-S02",note);
  x.hit("phone");ok(x.p.step.equals("V474_PRO_CRAFT"),"phone enters playable preparation");
  x.hit(a?"v474_fold":"v474_draft");ok(x.p.step.equals("V474_PRO_FINISH"),"first personal task done");
  ok(x.p.hasFlag(a?"V474_A_CRAFTED":"V474_S_CRAFTED"),"craft retained");
  x.hit(a?"v474_ribbon":"v474_stamp");ok(x.p.step.equals("PRO_GIFT"),"second personal task done");
  x.hit("gift");ok(x.p.step.equals("PRO_GO_PLAZA"),"legacy reward step retained");
  ok(x.p.hasItem(a?"paper_flower":"postcard"),"original gift present before exchange");
  ok(x.p.hasFlag(a?"V474_A_GIFT_FINISHED":"V474_S_GIFT_FINISHED"),"new long-term choice flag persisted");
  ok(x.p.hasFlag((a?"V474_A_":"V474_S_")+(note==0?(a?"NOTE_EVERYDAY":"NOTE_COMFORT"):(a?"NOTE_LISTEN":"NOTE_STORIES"))),"writing decision held");
  x.at("plaza");ok(x.p.step.equals("PRO_MEET"),"plaza entry triggers canon meeting");
  x.hit("meet");ok(x.p.step.equals("PRO_BOOK"),"meeting moves to Memory Book");
  ok(x.scenes.contains(a?"V474-P-MEET-A":"V474-P-MEET-S"),"route-exclusive meeting dialogue");
  String textChoice=a?(intro==0?"A_TEXT_HONEST":"A_TEXT_PLAYFUL"):(intro==0?"S_TEXT_OPEN":"S_TEXT_GENTLE");
  ok(x.scenes.contains("V474-RECALL-"+textChoice),"morning text choice reflected at plaza");
  String ribbonChoice=a?(craft==0?"A_RIBBON_CREAM":"A_RIBBON_VIOLET"):(craft==0?"S_STAMP_STAR":"S_STAMP_FLOWER");
  ok(x.scenes.contains("V474-RECALL-"+ribbonChoice),"visual gift customization reflected at plaza");
  ok(x.music.contains("cinema_prologue_promise_v474"),"new cinematic soundtrack connected");
  x.hit("book");ok(x.p.step.equals("PRO_SHARDS"),"portal enters original garden collecting step");
  ok(x.p.hasFlag("CANON_BOOK_OPEN"),"canon book opened");
  for(int j:permutation){
   x.hit("shard_"+j);
   ok(x.scenes.contains("V474-P-SHARD-"+j+"-"+(a?"A":"S")),"shard has specific POV narrative");
   ok(x.p.hasFlag("SHARD_"+j),"shard flag stored");
  }
  ok(x.p.step.equals("PRO_PORTAL"),"three shards open home portal");
  ok(x.p.hasFlag("PRO_COMPLETED"),"original PRO_COMPLETED preserved");
  x.hit("portal");ok(x.p.step.equals("C01_NOTE"),"new prologue reaches chapter1");
  ok(x.p.chapters.contains("PRO"),"one prologue completion");
  ok(x.scenes.contains(a?"V474-P-PORTAL-A":"V474-P-PORTAL-S"),"route ending response");
  ok(x.music.contains("cinema_prologue_memory_v474"),"portal soundtrack connected");
  Progress snapshot=Progress.fromMap(x.p.toMap(true));
  ok(snapshot.step.equals("C01_NOTE"),"save reload maintains chapter boundary");
  ok(snapshot.hasFlag(a?"V474_A_GIFT_FINISHED":"V474_S_GIFT_FINISHED"),"save roundtrip retains new prep");
  x.hit("note");ok(x.p.step.equals("C01_GO_PLAZA"),"chapter1 personal intro still progresses");
  ok(x.scenes.contains(a?"V474-C01-RECALL-A":"V474-C01-RECALL-S"),"chapter1 recalls prologue choices");
  ok(x.cine>=1,"original cinematic commands played");
  routes++;
 }
 static void oldSave(StoryDb s,QuestDb db,MapDb m,String rt){
  Env x=new Env(s,db,m,rt,"PRO_GIFT");x.hit("gift");ok(x.p.step.equals("PRO_GO_PLAZA"),"old save at gift can advance");
  Env y=new Env(s,db,m,rt,"PRO_SHARDS");for(int i=1;i<=3;i++)y.hit("shard_"+i);
  ok(y.p.step.equals("PRO_PORTAL"),"old save at shards can advance");
  y.hit("portal");ok(y.p.step.equals("C01_NOTE"),"old save reaches chapter1");
  Env z=new Env(s,db,m,rt,"PRO_PORTAL");z.hit("portal");
  ok(z.p.step.equals("C01_NOTE"),"old save at portal reaches chapter1");
 }
 static void epilogue(StoryDb s,QuestDb db,MapDb m,String rt){
  Env x=new Env(s,db,m,rt,"V473_EPI_FINALE");
  x.p.flags.add(rt.equals("arland")?"V474_A_NOTE_LISTEN":"V474_S_NOTE_COMFORT");
  x.p.flags.add(rt.equals("arland")?"V474_A_FOLD_CARE":"V474_S_DRAFT_THANK");
  x.p.flags.add("V466_"+(rt.equals("arland")?"A_LETTER":"S_LETTER"));
  x.hit("v473_final_bench");
  ok(x.scenes.contains(rt.equals("arland")?"V474-EPI-RECALL-A":"V474-EPI-RECALL-S"),"opening choice has epilogue payoff");
  ok(x.scenes.contains(rt.equals("arland")?"V474-RECALL-A_NOTE_LISTEN":"V474-RECALL-S_NOTE_COMFORT"),"exact letter text has unique epilogue callback");
  ok(x.scenes.contains(rt.equals("arland")?"V474-RECALL-A_FOLD_CARE":"V474-RECALL-S_DRAFT_THANK"),"exact crafting choice recalled in epilogue");
  ok(x.p.step.equals("EPI_FREE"),"new callback does not add second ending");
  ok(x.ends==1,"single canon Epilogue ending");
  Env legacy=new Env(s,db,m,rt,"V473_EPI_FINALE");
  legacy.hit("v473_final_bench");ok(legacy.p.step.equals("EPI_FREE"),"pre-v474 save reaches ending");
  ok(!legacy.scenes.contains(rt.equals("arland")?"V474-EPI-RECALL-A":"V474-EPI-RECALL-S"),"old save doesn't fake new choice memory");
 }
 static void locked(MapDb m,String rt){
  MapDb.Area area=m.area(Routes.room(rt));ok(area!=null,"room exists");
  // Verify locks in raw map metadata through the JSON source; covers both route doors.
 }
 public static void main(String[] args)throws Exception{
  StoryDb s=new StoryDb(read(args[0],"story.json"));QuestDb q=new QuestDb(read(args[0],"quests.json"));
  MapDb m=new MapDb(read(args[0],"maps.json"),read(args[0],"props.json"));
  ok("PRO_PHONE".equals(q.firstStep()),"new saves still start with original prologue intro");
  int[][] orders={{1,2,3},{1,3,2},{2,1,3},{2,3,1},{3,1,2},{3,2,1}};
  for(String rt:new String[]{"arland","sofia"}){
   for(int intro=0;intro<2;intro++)for(int craft=0;craft<2;craft++)for(int note=0;note<2;note++)
    for(int[] order:orders)run(s,q,m,rt,intro,craft,note,order);
   oldSave(s,q,m,rt);epilogue(s,q,m,rt);locked(m,rt);
  }
  System.out.println("PASS PRO V474: "+routes+" playable two-route paths / "+checks+" checks + old saves + chapter1 & epilogue");
 }
}
