import com.arlandsofia.olu.logic.*;
import java.util.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

/** End-to-end headless checks of playable v4.6.4 story choices and their late payoffs. */
public final class V465StoryCompletionTest {
    private static int checks = 0;
    private static void ok(boolean yes, String what) {
        checks++;
        if (!yes) throw new AssertionError("Story completion test #"+checks+": "+what);
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

    private static void repairIsPlayed(StoryDb s, QuestDb q, MapDb m) {
        for(String route:Arrays.asList("arland","sofia")) for(int option=0;option<3;option++) {
            Env e=new Env(s,q,m,route,"C04_V26_VOW");
            e.interact("v26_c04_vow");
            ok(e.played.contains("V465-C04-NOT-YET"),"no instant forgiveness cutscene");
            ok(e.p.step.equals("arland".equals(route)?"C04_V465_A_REFLECT":"C04_V465_S_REFLECT"),
                "follow-up story step must route correctly");
            e.pick("arland".equals(route)?"V465-C04-A-GALLERY-RETURN":"V465-C04-S-GALLERY-RETURN",option);
            e.interact("arland".equals(route)?"v465_a_gallery":"v465_s_gallery");
            ok(e.p.step.equals("arland".equals(route)?"V470_C04_A_PROOF":"V470_C04_S_PROOF"),
                "new playable accountability tasks must unlock after gallery return");
            ok(e.p.hasFlag("V465_REFLECTED"),"reflection persisted in saved flags");
            if("arland".equals(route)) {
                e.interact("v470_a_agenda");
                ok(e.p.step.equals("V470_C04_A_PROOF"),"one concrete action does not grant reconciliation");
                e.interact("v470_a_listen");
            } else {
                e.pick("V470-C04-S-BOUNDARY",option);
                e.interact("v470_s_boundaries");
                ok(e.p.step.equals("V470_C04_S_PROOF"),"Sofia must finish personal response and art");
                e.interact("v470_s_art");
            }
            ok(e.p.step.equals("C04_V465_SECOND_TALK"),"two proof actions are needed before meeting");
            e.pick("V465-C04-SECOND-TALK",option);
            e.interact("v465_second_talk");
            ok(e.p.step.equals("C05_FREE"),"transition to original chapter 5 intact");
            ok(e.p.hasFlag("V465_REPAIR_DONE"),"honest communication recorded");
            ok(e.p.chapters.contains("C04"),"original chapter completion still awarded");
            String marker="arland".equals(route)?"V465_A_":"V465_S_";
            boolean chosen=false;for(String flag:e.p.flags) if(flag.startsWith(marker)) chosen=true;
            ok(chosen,"route-specific follow-up decision saved");
            Progress restored=Progress.fromMap(e.p.toMap(true));
            ok(restored.hasFlag("V465_REPAIR_DONE") && restored.step.equals("C05_FREE"),
                "can restore post-conflict state on same route");
        }
    }
    private static void actionsInsteadOfAutomaticRewards(StoryDb s, QuestDb q, MapDb m) {
        for(String route:Arrays.asList("arland","sofia")) {
            Env e=new Env(s,q,m,route,"C05_MEET");
            e.interact("meet5");
            ok(e.p.step.equals("C05_V465_PROOF"),"star encounter unlocks interactive proof");
            ok(!e.p.hasFlag("V465_PROMISE_PROVEN"),"no reward before showing up");
            e.interact("v465_star_together");
            ok(e.p.step.equals("C05_V465_PROOF"),"one interaction not enough");
            e.interact("v465_star_listen");
            ok(e.p.step.equals("C05_STARMAP"),"both tasks advance original puzzle path");
            ok(e.p.hasFlag("V465_STAR_LISTEN")&&e.p.hasFlag("V465_STAR_COOPERATE"),
                "both dedicated story scenes played");
            ok(e.p.hasFlag("V465_PROMISE_PROVEN"),"actual activity unlocks proof flag");
            Progress loaded=Progress.fromMap(e.p.toMap(true));
            ok(loaded.hasFlag("V465_PROMISE_PROVEN"),"promise flag save roundtrip");
        }
    }
    private static void finaleAndEpilogueAreCanonical(StoryDb s, QuestDb q, MapDb m) {
        for(String route:Arrays.asList("arland","sofia")) for(boolean proof:new boolean[]{false,true}) {
            Env e=new Env(s,q,m,route,"C06_FINAL");
            if(proof)e.p.flags.add("V465_PROMISE_PROVEN");
            e.interact("pages");
            ok(e.played.contains(proof?"V465-C06-AFTER-EMPTY":"V465-C06-WITHOUT-PROOF"),
                "final memory follows relationship progress");
            ok(e.played.contains("C06-X01") && e.played.contains("C06-X03"),
                "both routes and choices use the same canon ending");
            ok(e.p.chapters.contains("C06"),"chapter six completed");
            Env epi=new Env(s,q,m,route,"EPI_FEST_LEPAS");
            epi.interact("fest_release");
            epi.interact("v473_plaza_memory");
            epi.interact("v473_cafe_memory");
            epi.interact("v473_gallery_memory");
            epi.interact("v473_lake_photo");
            epi.interact("v473_lake_letter");
            epi.interact("v473_lake_ready");
            epi.interact("v473_final_bench");
            ok(epi.played.contains("V465-EPI-LAKE"),"new epilogue scene is actually played");
            ok(epi.p.chapters.contains("EPI") && epi.p.step.equals("EPI_FREE"),
                "free roam and original epilogue still work");
        }
    }
    private static void dataIntegrity(StoryDb s, QuestDb q, MapDb m) {
        ok(m.area("galeri_komunitas")!=null,"gallery map is loaded");
        ok(s.scene("V465-C04-NOT-YET")!=null && s.scene("V465-C06-AFTER-EMPTY")!=null,
            "full middle-to-ending chain exists");
        for(QuestDb.Step step:q.steps.values()) for(QuestDb.Interactable it:step.interactables) {
            for(Map<String,Object> act:it.actions) if("scene".equals(act.get("do")) && act.get("id") instanceof String) {
                String id=(String)act.get("id");
                if(!id.contains("@$") && !id.contains("$ROUTE"))
                    ok(s.scene(id)!=null,"scene ref must exist: "+id);
            }
        }
    }
    public static void main(String[] args) throws Exception {
        String assets=args.length>0?args[0]:"android/assets";
        StoryDb story=new StoryDb(read(assets,"story.json"));
        QuestDb quests=new QuestDb(read(assets,"quests.json"));
        MapDb maps=new MapDb(read(assets,"maps.json"),read(assets,"props.json"));
        repairIsPlayed(story,quests,maps);
        actionsInsteadOfAutomaticRewards(story,quests,maps);
        finaleAndEpilogueAreCanonical(story,quests,maps);
        dataIntegrity(story,quests,maps);
        System.out.println("PASS: "+checks+" v4.6.5 completion/compatibility assertions");
    }
}
