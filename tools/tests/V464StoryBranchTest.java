import com.arlandsofia.olu.logic.*;
import java.util.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

/** End-to-end headless checks of playable v4.6.4 story choices and their late payoffs. */
public final class V464StoryBranchTest {
    private static int checks = 0;
    private static void ok(boolean yes, String what) {
        checks++;
        if (!yes) throw new AssertionError("Story test #"+checks+": "+what);
    }
    private static String read(String base,String f) throws Exception {
        return new String(Files.readAllBytes(Paths.get(base,"data",f)),StandardCharsets.UTF_8);
    }
    private static final class Env implements ActionRunner.Presenter {
        final StoryDb story;
        final QuestDb quests;
        final MapDb maps;
        final Progress p;
        final QuestEngine engine;
        final ActionRunner runner;
        final Map<String,Integer> picks = new HashMap<>();
        final List<String> played = new ArrayList<>();
        final List<String> music = new ArrayList<>();
        int choices;
        Env(StoryDb s, QuestDb q, MapDb m,String route,String step) {
            story=s; quests=q; maps=m;
            p=Progress.newGame(route,1,q.firstStep(),m.area(Routes.room(route)));
            p.step=step;
            engine=new QuestEngine(s,q,m,p,false);
            runner=new ActionRunner(engine,this);
            MapDb.flags = flag -> p.hasFlag(flag);
        }
        Env pick(String scene,int choice) {picks.put(scene,choice); return this;}
        void interact(String id) {
            QuestDb.Interactable found=null;
            for(QuestDb.Interactable it:engine.step().interactables) if(it.id.equals(id)) found=it;
            ok(found!=null,"quest interactable must exist: "+id+" in "+p.step);
            p.area=Routes.resolve(found.area,p.route);
            boolean visible=false;
            for(QuestDb.Interactable it:engine.interactables(p.area)) if(it.id.equals(id)) visible=true;
            ok(visible,"interactable must be visible: "+id+", route "+p.route+" step "+p.step);
            runner.run(engine.actionsFor(found));
            ok(!runner.busy(),"headless action runner must finish "+id);
        }
        void scene(String scene) { runner.run(Collections.singletonList(Map.of("do","scene","id",scene))); }
        public void playScene(String id,Runnable done) {
            StoryDb.Scene sc=story.scene(id);
            ok(sc!=null,"scene exists: "+id);
            played.add(id);
            if(!sc.choices.isEmpty()) {
                int selected=picks.getOrDefault(id,0);
                ok(selected>=0 && selected<sc.choices.size(),"valid selected scene choice "+id);
                StoryDb.Choice c=sc.choices.get(selected);
                ok(c.text!=null && !c.text.trim().isEmpty(),"choice label not empty "+id);
                ok(!c.response(p.route).isEmpty(),"choice route response exists "+id+"/"+p.route);
                engine.addFlags(c.flags);
                choices++;
            }
            done.run();
        }
        public void playLines(List<StoryDb.Line> lines,String speaker,Runnable done){done.run();}
        public void openPuzzle(String id,ActionRunner.BoolCallback done){done.done(true);}
        public void openMinigame(String id,ActionRunner.IntCallback done){done.done(3);}
        public void openShop(String id,Runnable done){done.run();}
        public void warp(String area,float x,float y,String dir,Runnable done){
            String dest=Routes.resolve(area,p.route);
            ok(maps.area(dest)!=null,"warp destination valid: "+dest);
            p.area=dest;p.x=x;p.y=y;p.dir=dir;
            ok(!maps.area(dest).blocked(x,y),"warp must not land in collision: "+dest+":"+x+","+y);
            done.run();
        }
        public void chapterCard(String chapter,Runnable done){done.run();}
        public void chapterEnd(String chapter,Runnable done){done.run();}
        public void credits(Runnable done){done.run();}
        public void cine(List<Map<String,Object>> cmds,Runnable done){
            ok(cmds!=null && !cmds.isEmpty(),"cinematic commands must be defined");
            done.run();
        }
        public void toast(String s){}
        public void sfx(String s){}
        public void music(String id){ music.add(id); }
        public void emote(String w,String e){}
        public void companionChanged(boolean value){}
        public void stepChanged(){}
        public void onIdle(){}
    }

    private static void dateChoices(StoryDb s,QuestDb q,MapDb m) {
        for(String route:Arrays.asList("arland","sofia")) for(int c=0;c<3;c++) {
            Env e=new Env(s,q,m,route,"C02_TO_CAFE");
            e.pick("arland".equals(route)?"V464-C02-WALK-A":"V464-C02-WALK-S",c);
            e.interact("date");
            ok("C02_V464_INTERLUDE".equals(e.p.step),"date branch opens actual side activity: "+route+" "+c);
            ok(e.choices>0,"player choice executed");
            String key=null;
            for(String x:Arrays.asList("V464_WALK_PARK","V464_WALK_LATER","V464_WALK_SOLO","V464_WALK_ASK")) if(e.p.hasFlag(x)) key=x;
            ok(key!=null,"date decision recorded");
            String interact=key.equals("V464_WALK_PARK")?"v464_park":key.equals("V464_WALK_LATER")?"v464_later":key.equals("V464_WALK_SOLO")?"v464_solo":"v464_ask";
            e.interact(interact);
            ok("C02_DATE".equals(e.p.step),"date activity advances existing story: "+route+" "+c);
            ok(e.p.hasFlag(key),"choice persists in save flags");
        }
    }
    private static void galleryPrep(StoryDb s,QuestDb q,MapDb m) {
        for(String route:Arrays.asList("arland","sofia")) {
            Env e=new Env(s,q,m,route,"C03_PICNIC");
            e.interact("picnic");
            ok("C03_V464_GALLERY_PREP".equals(e.p.step),"gallery preparation quest unlocked");
            ok("galeri_komunitas".equals(e.p.area),"new area actually entered");
            e.interact("gallery_seat");
            ok(e.p.hasFlag("V464_PREP_SEAT_DONE"),"seat prepared");
            e.interact("gallery_projector");
            ok(e.p.hasFlag("V464_PREP_ART_DONE"),"gallery art prepared");
            ok("C03_V464_GALLERY_PREP".equals(e.p.step),"two gallery interactions no longer prematurely finish Chapter 3");
            e.interact("v469_gallery_card");
            ok(e.p.hasFlag("V469_GALLERY_INVITE_DONE"),"gallery schedule and invitation are really prepared");
            ok(e.p.step.startsWith("C04_"),"all three gallery interactions complete Chapter 3 and start Chapter 4");
        }
    }
    private static void galleryConflict(StoryDb s,QuestDb q,MapDb m) {
        for(int c=0;c<3;c++){
            Env a=new Env(s,q,m,"arland","C04_A_WAKE");
            a.pick("V464-C04-A-PROJECTOR",c);
            a.interact("phone4");
            ok("C04_V464_A_PROJECTOR".equals(a.p.step),"Arland projector stage");
            a.interact("projector_v464");
            ok(("V470_C04_A_"+new String[]{"WARN","SILENT","HELP"}[c]).equals(a.p.step),"decision creates new playable step");
            if(c==0)a.interact("v470_a_message");
            else if(c==1){a.interact("v470_a_fuse");a.interact("v470_a_screen");}
            else {a.interact("v470_a_call");a.interact("v470_a_depart");}
            ok("C04_V464_A_GALLERY".equals(a.p.step),"Arland eventually reaches empty gallery");
            a.interact("empty_chair_a");
            ok("V470_C04_A_AFTER".equals(a.p.step),"Arland hears witness story before rain");
            a.interact("v470_a_witness");a.interact("v470_a_ticket");
            ok("C04_A_CAFE".equals(a.p.step),"Arland reaches original rain chapter with context");
            ok(a.p.hasFlag("V464_SEAT_EMPTY") && a.p.hasFlag("V464_PROMISE_MISSED"),"major conflict persists");
            ok(a.played.contains("V464-C04-A-LATE"),"empty-seat event was seen");
            ok(a.music.contains("cinema_gallery_empty"),"gallery theme plays");
            Env f=new Env(s,q,m,"sofia","C04_S_WAKE");
            f.pick("V470-C04-S-REHEARSE",c);
            f.pick("V464-C04-S-AFTER",c);
            f.interact("phone4");
            ok("V470_C04_S_PREP".equals(f.p.step),"Sofia prepares gallery presentation first");
            f.interact("v470_s_note");f.interact("v470_s_rehearse");
            ok("C04_V464_S_GALLERY".equals(f.p.step),"Sofia presents artwork");
            f.interact("stage_s_v464");
            ok("C04_V464_S_REFLECT".equals(f.p.step),"Sofia controls post-show choice");
            f.interact("chair_s_v464");
            ok("V470_C04_S_AFTER".equals(f.p.step),"Sofia must reflect privately");
            f.interact("v470_s_sketch");f.interact("v470_s_lights");
            ok("C04_S_CAFE".equals(f.p.step),"Sofia reaches rain chapter");
            ok(f.p.hasFlag("V464_SEAT_EMPTY"),"Sofia remembers empty seat");
            ok(f.played.contains("V464-C04-S-PRESENT"),"Sofia stage was really played");
        }
    }
    private static void foreshadowAndFinale(StoryDb s,QuestDb q,MapDb m) {
        for(String route:Arrays.asList("arland","sofia")) {
            Env e=new Env(s,q,m,route,"C05_MEET");
            e.interact("meet5");
            ok("C05_V465_PROOF".equals(e.p.step),"Memory Realm now requires an interactive trust milestone");
            e.interact("v465_star_listen");e.interact("v465_star_together");
            ok("C05_STARMAP".equals(e.p.step),"completed proof leads to original C05 navigation");
            ok(e.p.hasFlag("V464_QUIET_TWO_SIDES"),"both viewpoints registered in canon lore");
            ok(e.played.contains("arland".equals(route)?"V464-C05-MEMORY-A":"V464-C05-MEMORY-S"),"route-specific revealed scene");
            Env finale=new Env(s,q,m,route,"C06_FINAL");
            finale.p.flags.add("V464_WALK_PARK");
            if("arland".equals(route)) finale.p.flags.add("V464_A_HELP");
            else finale.p.flags.add("V464_S_DRAW");
            finale.interact("pages");
            ok(finale.p.hasFlag("V464_SEAT_RESTORED"),"new memory restored in finale");
            ok(finale.played.contains("V464-C06-EMPTY-SEAT"),"empty-seat payoff played");
            ok(finale.played.contains("V464-C06-WALK-PARK"),"C02 choice recalled at finale");
            ok(finale.played.contains("arland".equals(route)?"V464-C06-PAYOFF-HELP":"V464-C06-PAYOFF-DRAW"),"C04 choice recalled at finale");
            ok(finale.played.contains("C06-X01"),"one shared original canon-ending scene preserved");
        }
    }
    private static void saveRoundTrip(StoryDb s,QuestDb q,MapDb m) {
        Env a=new Env(s,q,m,"sofia","C04_S_WAKE");
        a.pick("V464-C04-S-AFTER",2);
        a.interact("phone4");a.interact("v470_s_note");a.interact("v470_s_rehearse");
        a.interact("stage_s_v464"); a.interact("chair_s_v464");a.interact("v470_s_sketch");a.interact("v470_s_lights");
        Progress reloaded=Progress.fromMap(a.p.toMap(true));
        ok(reloaded.hasFlag("V464_S_DRAW") && reloaded.hasFlag("V464_SEAT_EMPTY"),"Sofia decisions persist across save/load");
        ok("C04_S_CAFE".equals(reloaded.step),"old schema retains story step");
        ok(reloaded.route.equals("sofia") && reloaded.slot==1,"old route/slot boundaries intact");
    }
    public static void main(String[] args) throws Exception {
        String assets=args.length>0?args[0]:"android/assets";
        StoryDb story=new StoryDb(read(assets,"story.json"));
        QuestDb quests=new QuestDb(read(assets,"quests.json"));
        MapDb maps=new MapDb(read(assets,"maps.json"),read(assets,"props.json"));
        ok(maps.area("galeri_komunitas")!=null,"new gallery map loads");
        dateChoices(story,quests,maps);
        galleryPrep(story,quests,maps);
        galleryConflict(story,quests,maps);
        foreshadowAndFinale(story,quests,maps);
        saveRoundTrip(story,quests,maps);
        System.out.println("PASS: "+checks+" v4.6.4 branching-story runtime assertions");
    }
}
