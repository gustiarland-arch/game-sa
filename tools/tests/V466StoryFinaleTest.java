import com.arlandsofia.olu.logic.*;
import java.util.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

/** v4.6.6 story choices, finale, old saves and optional postgame gallery. */
public final class V466StoryFinaleTest {
    private static int checked;
    private static void ok(boolean yes,String message) {
        checked++; if(!yes) throw new AssertionError("v4.6.6 #"+checked+": "+message);
    }
    private static String data(String folder,String file) throws Exception {
        return new String(Files.readAllBytes(Paths.get(folder,"data",file)), StandardCharsets.UTF_8);
    }
    private static final class Env implements ActionRunner.Presenter {
        final QuestEngine engine;
        final ActionRunner runner;
        final Progress p;
        final StoryDb story;
        final MapDb maps;
        final Map<String,Integer> picks=new HashMap<>();
        final List<String> played=new ArrayList<>();
        final List<String> music=new ArrayList<>();
        Env(StoryDb s,QuestDb q,MapDb m,String route,String step) {
            story=s;maps=m;
            p=Progress.newGame(route,1,q.firstStep(),m.area(Routes.room(route)));
            p.step=step;
            engine=new QuestEngine(s,q,m,p,false);
            runner=new ActionRunner(engine,this);
            MapDb.flags=flag->p.hasFlag(flag);
        }
        Env choose(String scene,int index) { picks.put(scene,index);return this; }
        void playInteract(String id) {
            QuestDb.Interactable found=null;
            for(QuestDb.Interactable it:engine.step().interactables)
                if(id.equals(it.id))found=it;
            ok(found!=null,"interaction exists "+id);
            p.area=Routes.resolve(found.area,p.route);
            ok(engine.interactables(p.area).stream().anyMatch(i->id.equals(i.id)),
               "interaction accessible for route/flags "+id);
            runner.run(engine.actionsFor(found));
            ok(!runner.busy(),"runner completes "+id);
        }
        public void playScene(String id,Runnable done) {
            StoryDb.Scene sc=story.scene(id);
            ok(sc!=null,"story scene exists "+id);
            ok("shared".equals(sc.route)||p.route.equals(sc.route),"scene route isolation "+id);
            played.add(id);
            if(!sc.choices.isEmpty()) {
                int index=picks.getOrDefault(id,0);
                ok(index>=0 && index<sc.choices.size(),"valid choice index "+id);
                StoryDb.Choice c=sc.choices.get(index);
                ok(!c.response(p.route).isEmpty(),"response for protagonist "+id);
                engine.addFlags(c.flags);
            }
            done.run();
        }
        public void playLines(List<StoryDb.Line> lines,String who,Runnable done){done.run();}
        public void openPuzzle(String id,ActionRunner.BoolCallback cb){cb.done(true);}
        public void openMinigame(String id,ActionRunner.IntCallback cb){cb.done(3);}
        public void openShop(String id,Runnable cb){cb.run();}
        public void warp(String area,float x,float y,String dir,Runnable cb){
            String dest=Routes.resolve(area,p.route);
            ok(maps.area(dest)!=null,"valid destination "+dest);
            ok(!maps.area(dest).blocked(x,y),"destination not blocked "+dest);
            p.area=dest;p.x=x;p.y=y;p.dir=dir;cb.run();
        }
        public void chapterCard(String chapter,Runnable cb){cb.run();}
        public void chapterEnd(String chapter,Runnable cb){p.chapters.add(chapter);cb.run();}
        public void credits(Runnable cb){cb.run();}
        public void cine(List<Map<String,Object>> cmds,Runnable cb){cb.run();}
        public void toast(String text){}
        public void sfx(String id){}
        public void music(String id){music.add(id);}
        public void emote(String who,String id){}
        public void companionChanged(boolean b){}
        public void stepChanged(){}
        public void onIdle(){}
    }
    /** v4.7.3: keep all original callback assertions, but physically traverse the new memory walk first. */
    private static void finishEpilogue(Env epi) {
        epi.playInteract("v473_plaza_memory");
        epi.playInteract("v473_cafe_memory");
        epi.playInteract("v473_gallery_memory");
        epi.playInteract("v473_lake_photo");
        epi.playInteract("v473_lake_letter");
        epi.playInteract("v473_lake_ready");
        epi.playInteract("v473_final_bench");
    }
    private static void newRouteLetters(StoryDb s,QuestDb q,MapDb m) {
        String[] a={"V466_A_PRESENT","V466_A_LISTEN","V466_A_LEARN"};
        String[] b={"V466_S_TELL","V466_S_SPACE","V466_S_PROUD"};
        String[] ca={"V466-EPI-A-PRESENT","V466-EPI-A-LISTEN","V466-EPI-A-LEARN"};
        String[] cb={"V466-EPI-S-TELL","V466-EPI-S-SPACE","V466-EPI-S-PROUD"};
        for(String route:Arrays.asList("arland","sofia")) for(int k=0;k<3;k++) {
            boolean isA="arland".equals(route);
            String letter=isA?"V466-C06-A-LETTER":"V466-C06-S-LETTER";
            Env finale=new Env(s,q,m,route,"C06_FINAL");
            finale.p.flags.add("V465_PROMISE_PROVEN");
            finale.choose(letter,k).playInteract("pages");
            ok(finale.played.contains(letter),"right route letter plays");
            ok(!finale.played.contains(isA?"V466-C06-S-LETTER":"V466-C06-A-LETTER"),"opposite letter never plays");
            ok(finale.played.contains("V466-C06-SHARED-PAGE"),"both share final page");
            ok(finale.played.contains("C06-X01")&&finale.played.contains("C06-X03"),"canonical ending kept");
            ok("EPI_FEST_GO".equals(finale.p.step),"chapter six transitions to epilogue");
            ok(finale.p.hasFlag(isA?a[k]:b[k]),"selected letter persisted");
            for(int j=0;j<3;j++)if(j!=k)ok(!finale.p.hasFlag(isA?a[j]:b[j]),"no contradictory response flag");
            Progress restored=Progress.fromMap(finale.p.toMap(true));
            ok(restored.hasFlag(isA?a[k]:b[k]),"save roundtrip preserves letter choice");
            Env epi=new Env(s,q,m,route,"EPI_FEST_LEPAS");
            epi.p.flags.addAll(restored.flags);
            epi.playInteract("fest_release");
            finishEpilogue(epi);
            ok(epi.played.contains(isA?ca[k]:cb[k]),"matching letter coda plays");
            for(int j=0;j<3;j++)if(j!=k)ok(!epi.played.contains(isA?ca[j]:cb[j]),"other coda is absent");
            ok(!epi.played.contains("V466-EPI-OLD-CHAPTER"),"new save does not show legacy fallback");
            ok(epi.played.contains("V465-EPI-LAKE"),"prior epilogue is intact");
            ok("EPI_FREE".equals(epi.p.step),"free roam stays available");
            ok(epi.music.contains("cinema_letter_tomorrow"),"letter score triggers");
            epi.playInteract("v466_gallery_return");
            ok(epi.played.contains(isA?"V466-EPI-A-GALLERY":"V466-EPI-S-GALLERY"),"optional gallery is playable");
            ok(epi.p.hasFlag("V466_GALLERY_RETURN_DONE"),"gallery visit cannot be repeated for rewards");
            ok(epi.engine.interactables("galeri_komunitas").stream().noneMatch(it->it.id.equals("v466_gallery_return")),
                "optional event disappears after visit");
            Progress after=Progress.fromMap(epi.p.toMap(true));
            ok(after.hasFlag("V466_GALLERY_RETURN_DONE"),"epilogue choice survives restart");
        }
    }
    private static void oldSavesRemainPlayable(StoryDb s,QuestDb q,MapDb m) {
        for(String route:Arrays.asList("arland","sofia")) {
            Env old=new Env(s,q,m,route,"EPI_FEST_LEPAS");
            old.playInteract("fest_release");
            finishEpilogue(old);
            ok(old.played.contains("V466-EPI-OLD-CHAPTER"),"legacy epilogue has a valid fallback");
            ok(old.played.contains("V465-EPI-LAKE"),"legacy epilogue retains old chapter");
            ok("EPI_FREE".equals(old.p.step),"legacy epilogue not softlocked");
            old.playInteract("v466_gallery_return");
            ok(old.p.hasFlag("V466_GALLERY_RETURN_DONE"),"legacy save can enjoy postgame gallery");
        }
    }
    public static void main(String[] args) throws Exception {
        String folder=args.length==0?"android/assets":args[0];
        StoryDb s=new StoryDb(data(folder,"story.json"));
        QuestDb q=new QuestDb(data(folder,"quests.json"));
        MapDb m=new MapDb(data(folder,"maps.json"),data(folder,"props.json"));
        newRouteLetters(s,q,m);
        oldSavesRemainPlayable(s,q,m);
        ok(s.scenes.size()>=457,"previous narrative content remains intact");
        System.out.println("PASS: "+checked+" v4.6.6 route letters, epilogue, gallery and save assertions");
    }
}
