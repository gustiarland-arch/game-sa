import com.arlandsofia.olu.logic.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
/** Production QuestEngine + ActionRunner checks for the complete playable memory walk, both routes,
 *  two-route global bonus (never unlocked by a local flag), and old-save compatibility. */
public final class V473EpilogueTest {
 static long checks=0, paths=0;
 static void ok(boolean v,String text){checks++;if(!v)throw new AssertionError("EPI #"+checks+" "+text);}
 static String read(String dir,String name)throws Exception{return new String(Files.readAllBytes(Paths.get(dir,"data",name)),StandardCharsets.UTF_8);}
 static final class Sim implements ActionRunner.Presenter {
  final StoryDb s;final QuestEngine e;final ActionRunner r;final Progress p;final MapDb m;
  final Set<String> played=new HashSet<>(),aud=new HashSet<>();final Map<String,Integer> picks=new HashMap<>();
  int ends=0,cines=0;
  Sim(StoryDb s,QuestDb q,MapDb m,String route,String stage){
   this.s=s;this.m=m;p=Progress.newGame(route,1,q.firstStep(),m.area(Routes.room(route)));
   p.step=stage;p.area="taman_kota";p.x=650;p.y=720;
   e=new QuestEngine(s,q,m,p,false);r=new ActionRunner(e,this);MapDb.flags=flag->p.hasFlag(flag);
  }
  void global(boolean complete){
   GlobalProgress g=new GlobalProgress();
   if(complete){g.completed.get("arland").add("C06");g.completed.get("sofia").add("C06");}
   e.setGlobalProgress(g);
  }
  void select(String id,int n){picks.put(id,n);}
  void at(String id){
   QuestDb.Interactable found=null;
   for(QuestDb.Interactable it:e.step().interactables)if(it.id.equals(id)&&it.forRoute(p.route)){found=it;break;}
   ok(found!=null,"interactable defined "+id+" at "+p.step);
   p.area=Routes.resolve(found.area,p.route);
   ok(e.interactables(p.area).contains(found),"interactable is reachable by conditions "+id+" at "+p.step);
   r.run(e.actionsFor(found));ok(!r.busy(),"action callback queue idle after "+id);
  }
  public void playScene(String id,Runnable done){
   StoryDb.Scene v=s.scene(id);ok(v!=null,"scene exists "+id);
   ok("shared".equals(v.route)||p.route.equals(v.route),"no wrong POV scene "+id);
   played.add(id);
   if(!v.choices.isEmpty()){
    int n=picks.getOrDefault(id,0);ok(n>=0&&n<v.choices.size(),"valid choice index");
    StoryDb.Choice c=v.choices.get(n);ok(!c.response(p.route).isEmpty(),"reply exists for each route");
    e.addFlags(c.flags);
   }
   done.run();
  }
  public void playLines(List<StoryDb.Line> l,String n,Runnable done){done.run();}
  public void openPuzzle(String id,ActionRunner.BoolCallback done){done.done(true);}
  public void openMinigame(String id,ActionRunner.IntCallback done){done.done(4);}
  public void openShop(String id,Runnable done){done.run();}
  public void warp(String area,float x,float y,String dir,Runnable done){
   String dest=Routes.resolve(area,p.route);ok(m.area(dest)!=null,"warp destination valid "+dest);
   ok(!m.area(dest).blocked(x,y),"safe landing in "+dest);
   p.area=dest;p.x=x;p.y=y;p.dir=dir;done.run();
  }
  public void chapterCard(String c,Runnable done){done.run();}
  public void chapterEnd(String c,Runnable done){ends++;e.p.chapters.add(c);done.run();}
  public void credits(Runnable done){done.run();}
  public void cine(List<Map<String,Object>> cmds,Runnable done){ok(!cmds.isEmpty(),"real cinematic instructions");cines++;done.run();}
  public void toast(String t){} public void sfx(String id){aud.add(id);} public void music(String id){aud.add(id);}
  public void emote(String s,String t){} public void companionChanged(boolean x){}public void stepChanged(){}public void onIdle(){}
 }
 static void walk(StoryDb s,QuestDb q,MapDb m,String route,int plaza,int cafe,int gallery,boolean old){
  Sim x=new Sim(s,q,m,route,"EPI_FEST_LEPAS");x.global(false);
  if(!old){
   x.p.flags.add(route.equals("sofia")?"V466_S_TELL":"V466_A_PRESENT");
   x.p.flags.add("V470_S_NEED_LISTEN");x.p.flags.add("V471_QUIET_REVEALED");
  }
  x.select("V473-EPI-PLAZA",plaza);x.select("V473-EPI-CAFE",cafe);x.select("V473-EPI-GALLERY",gallery);
  x.at("fest_release");ok(x.p.step.equals("V473_EPI_PLAZA"),"festival must lead to playable memory walk, not instantly free roam");
  ok(x.ends==0,"no early Epilogue end at festival");ok(!x.played.contains("V465-EPI-LAKE"),"quiet lakeside moment not incorrectly shown in park");
  x.at("v473_plaza_memory");ok(x.p.step.equals("V473_EPI_CAFE"),"plaza quest progresses to cafe");
  ok(x.p.hasFlag(plaza==0?"V473_PLAZA_GIFT":"V473_PLAZA_COURAGE"),"plaza choice saved");
  x.at("v473_cafe_memory");ok(x.p.step.equals("V473_EPI_GALLERY"),"cafe to gallery");
  ok(x.p.hasFlag(cafe==0?"V473_CAFE_LISTEN":"V473_CAFE_TWO_SIDES"),"cafe choice saved");
  x.at("v473_gallery_memory");ok(x.p.step.equals("V473_EPI_LAKE_MEMORIES"),"gallery to lake");
  ok(x.p.hasFlag(gallery==0?"V473_GALLERY_KEEP":"V473_GALLERY_PAIR"),"gallery choice saved");
  x.at("v473_lake_photo");ok(x.p.step.equals("V473_EPI_LAKE_MEMORIES"),"lake photo alone not enough");
  x.at("v473_lake_letter");ok(x.p.step.equals("V473_EPI_LAKE_MEMORIES"),"lake letter alone not enough");
  Progress saved=Progress.fromMap(x.p.toMap(true));ok(saved.hasFlag("V473_LAKE_PHOTO")&&saved.hasFlag("V473_LAKE_LETTER"),"save preserves both lake clues");
  x.at("v473_lake_ready");ok(x.p.step.equals("V473_EPI_FINALE"),"both clues unlock quiet ending");
  x.at("v473_final_bench");ok(x.p.step.equals("EPI_FREE"),"full Epilogue now ends with free roam");
  ok(x.played.contains("V473-EPI-LAKE-END"),"original emotional ending happens physically at lake");
  ok(x.played.contains("V465-EPI-LAKE"),"v4.6.5 canonical coda preserved");
  ok(x.ends==1,"exactly one Epilogue chapter completion");
  ok(x.p.hasFlag("V473_EPI_COMPLETE"),"Epilogue completion flag");
  ok(x.cines>=2,"festival + gallery + lake have cinematic camera commands");
  ok(x.played.contains(old?"V466-EPI-OLD-CHAPTER":(route.equals("arland")?"V466-EPI-A-PRESENT":"V466-EPI-S-TELL")),"legacy and new finale callbacks remain conditional");
  ok(x.aud.contains("cinema_homecoming_v473"),"new soundtrack is played");
  Progress reloaded=Progress.fromMap(x.p.toMap(true));ok(reloaded.step.equals("EPI_FREE")&&reloaded.chapters.contains("EPI"),"save roundtrip completed epilogue");
  // Post-credit journey, each interaction only once.
  x.at("v473_post_plaza");x.at("v473_post_cafe");x.at("v473_post_lake");
  ok(x.e.interactables("plaza").stream().noneMatch(it->"v473_post_plaza".equals(it.id)),"postgame no repeatable reward");
  paths++;
 }
 static void dualBonus(StoryDb s,QuestDb q,MapDb m,String route,int ending){
  Sim x=new Sim(s,q,m,route,"EPI_FREE");x.global(false);
  ok(x.e.interactables("galeri_komunitas").stream().noneMatch(it->"v473_bonus_gate".equals(it.id)),"bonus locked for single completed route");
  x.p.flags.add("V473_BONUS_DONE");
  ok(x.e.interactables("galeri_komunitas").stream().noneMatch(it->"v473_bonus_gate".equals(it.id)),"local spoofed completion flag never unlocks global bonus");
  x.p.flags.remove("V473_BONUS_DONE");x.global(true);
  ok(x.e.interactables("galeri_komunitas").stream().anyMatch(it->"v473_bonus_gate".equals(it.id)),"both completed chapter6 routes unlock bonus");
  x.at("v473_bonus_gate");ok(x.p.step.equals("V473_EPI_BONUS_ENTER"),"bonus enters new playable quest");
  ok("ruang_dua_surat".equals(x.p.area),"bonus actually travels to new room");
  x.at("v473_bonus_sofia");ok("V473_EPI_BONUS_ENTER".equals(x.p.step),"one letter insufficient");
  x.at("v473_bonus_arland");ok("V473_EPI_BONUS_CLOSE".equals(x.p.step),"both letters required");
  ok(x.played.contains("V473-EPI-BONUS-LETTER-A")&&x.played.contains("V473-EPI-BONUS-LETTER-S"),"both letters played no perspective skipped");
  Progress save=Progress.fromMap(x.p.toMap(true));ok(save.step.equals("V473_EPI_BONUS_CLOSE"),"mid-bonus save can resume");
  x.select("V473-EPI-BONUS-CHOICE",ending);x.at("v473_bonus_page");
  ok(x.p.step.equals("EPI_FREE"),"bonus returns to free roam, no alternative canon ending");
  ok(x.p.hasFlag(ending==0?"V473_BONUS_KEEP":"V473_BONUS_NEW_PAGE"),"bonus choice remains distinct");
  ok(x.p.hasFlag("V473_BONUS_DONE")&&x.p.hasItem("v473_two_letters"),"two-letter reward saved");
  ok(x.ends==0,"bonus never repeats main chapter-ending event");
  ok(x.e.interactables("galeri_komunitas").stream().noneMatch(it->"v473_bonus_gate".equals(it.id)),"bonus cannot farm rewards");
  paths++;
 }
 public static void main(String[]args)throws Exception{
  String root=args[0];StoryDb s=new StoryDb(read(root,"story.json"));QuestDb q=new QuestDb(read(root,"quests.json"));MapDb m=new MapDb(read(root,"maps.json"),read(root,"props.json"));
  for(String rt:new String[]{"arland","sofia"})for(int a=0;a<2;a++)for(int b=0;b<2;b++)for(int c=0;c<2;c++)for(boolean old:new boolean[]{false,true})walk(s,q,m,rt,a,b,c,old);
  for(String rt:new String[]{"arland","sofia"})for(int k=0;k<2;k++)dualBonus(s,q,m,rt,k);
  for(String rt:new String[]{"arland","sofia"}){
   Sim old=new Sim(s,q,m,rt,"EPI_FREE");old.global(false);
   old.at("v466_gallery_return");ok(old.p.hasFlag("V466_GALLERY_RETURN_DONE"),"old EPI_FREE save still plays optional gallery");
  }
  System.out.println("PASS EPI V473: "+paths+" real ActionRunner routes; "+checks+" checks; mandatory memories, single canon coda, two-route bonus, old save, one-time postgame");
 }
}
