import com.arlandsofia.olu.logic.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Actual ActionRunner/QuestEngine regression: Prologue handoff through Chapter 1. */
public final class V467ChapterOneTest {
    static int checks=0;
    static void ok(boolean value, String message) {
        checks++;
        if(!value) throw new AssertionError("C01 assertion #"+checks+": "+message);
    }
    static String read(String folder,String name) throws Exception {
        return new String(Files.readAllBytes(Paths.get(folder,"data",name)),StandardCharsets.UTF_8);
    }
    static final class Env implements ActionRunner.Presenter {
        final QuestEngine engine;
        final ActionRunner runner;
        final StoryDb story;
        final QuestDb quests;
        final Progress p;
        final MapDb maps;
        final Map<String,Integer> selections=new HashMap<>();
        final List<String> scenes=new ArrayList<>();
        Env(StoryDb story,QuestDb quests,MapDb maps,String route,String currentStep) {
            this.story=story;this.quests=quests;this.maps=maps;
            p=Progress.newGame(route,1,quests.firstStep(),maps.area(Routes.room(route)));
            p.step=currentStep;
            engine=new QuestEngine(story,quests,maps,p,false);
            runner=new ActionRunner(engine,this);
            MapDb.flags=f->p.hasFlag(f);
        }
        void select(String sceneId,int idx){selections.put(sceneId,idx);}
        void at(String area) {
            p.area=Routes.resolve(area,p.route);
            ok(maps.area(p.area)!=null,"area exists: "+p.area);
            List<Map<String,Object>> entered=engine.onEnterArea(p.area);
            ok(!entered.isEmpty(),"entry action for "+p.step+" at "+area);
            runner.run(entered);
            ok(!runner.busy(),"entry completed "+area);
        }
        void interact(String id) {
            QuestDb.Interactable chosen=null;
            for(QuestDb.Interactable it:engine.step().interactables)
                if(it.id.equals(id) && it.forRoute(p.route)) chosen=it;
            ok(chosen!=null,"interaction exists "+id+" at "+p.step);
            p.area=Routes.resolve(chosen.area,p.route);
            ok(engine.interactables(p.area).contains(chosen),"interaction available to route "+id);
            runner.run(engine.actionsFor(chosen));
            ok(!runner.busy(),"interaction completed "+id);
        }
        public void playScene(String id,Runnable done) {
            StoryDb.Scene sc=story.scene(id);
            ok(sc!=null,"scene exists "+id);
            ok(sc.route.equals("shared") || sc.route.equals(p.route),"route-correct scene "+id);
            scenes.add(id);
            if(!sc.choices.isEmpty()){
                int index=selections.getOrDefault(id,0);
                ok(index>=0 && index<sc.choices.size(),"valid decision "+id);
                StoryDb.Choice c=sc.choices.get(index);
                ok(!c.response(p.route).isEmpty(),"route-specific response to "+id);
                engine.addFlags(c.flags);
            }
            done.run();
        }
        public void playLines(List<StoryDb.Line> lines,String who,Runnable done){done.run();}
        public void openPuzzle(String id,ActionRunner.BoolCallback done){done.done(true);}
        public void openMinigame(String id,ActionRunner.IntCallback done){done.done(3);}
        public void openShop(String id,Runnable done){done.run();}
        public void warp(String area,float x,float y,String dir,Runnable done){
            String resolved=Routes.resolve(area,p.route);
            ok(maps.area(resolved)!=null,"warp destination exists "+resolved);
            ok(!maps.area(resolved).blocked(x,y),"warp destination traversable "+resolved);
            p.area=resolved;p.x=x;p.y=y;p.dir=dir;done.run();
        }
        public void chapterCard(String chapter,Runnable done){done.run();}
        public void chapterEnd(String chapter,Runnable done){p.chapters.add(chapter);done.run();}
        public void credits(Runnable done){done.run();}
        public void cine(List<Map<String,Object>> cmds,Runnable done){done.run();}
        public void toast(String text){}
        public void sfx(String id){}
        public void music(String id){}
        public void emote(String who,String id){}
        public void companionChanged(boolean enabled){}
        public void stepChanged(){}
        public void onIdle(){}
    }
    static void path(StoryDb s,QuestDb q,MapDb maps,String route,int intro,int choice) {
        String[] branch={"LISTEN","RECORD","TRACE"};
        String[] item={"v467_c01_listening","v467_c01_double_page","v467_c01_fading_ink"};
        String b=branch[choice];
        Env e=new Env(s,q,maps,route,"C01_NOTE");
        e.select("C01-"+(route.equals("arland")?"A":"S")+"01",intro);
        e.select("C01-X02",choice);
        e.interact("note");
        ok(e.p.step.equals("C01_GO_PLAZA"),"note completes");
        e.at("plaza");e.interact("mural");
        e.at("cafe");
        ok(e.p.step.equals("V467_C01_CAFE_HELP"),"route-exclusive cafe help is required");
        boolean aRoute=route.equals("arland");
        for(int time:new int[]{8*60,13*60,18*60,23*60}) {
            e.p.minute=time;
            boolean expectedNpcPresent=false;
            for(QuestDb.TownNpc actor:e.engine.townNpcsNow("cafe"))
                if(actor.id.equals(aRoute?"raka":"rara")) expectedNpcPresent=true;
            ok(expectedNpcPresent,"story quest actor visible at cafe regardless of clock time");
        }
        e.p.minute=7*60;
        e.interact(aRoute?"v467_cafe_ask_a":"v467_cafe_ask_s");
        ok(e.p.step.equals(aRoute?"V467_C01_CAFE_A_FIND":"V467_C01_CAFE_S_FIND"),
            "route-specific cafe task has real follow-up objective");
        e.interact(aRoute?"v467_cafe_find_a":"v467_cafe_find_s");
        ok(e.p.hasFlag(aRoute?"V467_C01_A03_DONE":"V467_C01_S03_DONE"),
            "personal cafe quest completed");
        ok(e.p.items.contains(aRoute?"v467_c01_barista_note":"v467_c01_rara_bookmark"),
            "personal cafe collectible awarded");
        ok(!e.p.items.contains(aRoute?"v467_c01_rara_bookmark":"v467_c01_barista_note"),
            "other route's item is not awarded");
        ok(e.p.step.equals("C01_PUZZLE"),"personal cafe quest rejoins symbolic puzzle");
        e.interact("symbols");
        ok(e.p.step.equals("C01_LIBRARY_GO"),"Cafe puzzle advances correctly");
        ok(e.p.hasFlag("V467_C01_CHOOSE_"+b),"player decision flag: "+b);
        e.at("perpustakaan");e.interact("laras1");
        for(int i=1;i<=3;i++)e.interact("libbook"+i);
        ok(e.p.step.equals("C01_TABLE"),"book collecting done only once");
        e.interact("libtable");
        e.at("ruang_arsip");e.interact("pedestal");
        e.interact(route.equals("arland")?"q_a_map":"q_s_margin");
        e.interact("laras2");
        ok(e.p.step.equals("V467_C01_"+b),"real different quest branch after letter: "+b);
        e.interact("v467_c01_"+b.toLowerCase(Locale.ROOT));
        ok(e.p.step.equals("C01_RIVERSIDE"),"branch returns to canon quest");
        ok(e.p.hasFlag("V467_C01_RESULT_"+b),"unique branch completion flag");
        ok(e.p.items.contains(item[choice]),"unique earned item");
        for(int j=0;j<3;j++)if(j!=choice){
            ok(!e.p.hasFlag("V467_C01_RESULT_"+branch[j]),"no contradictory branch flags");
            ok(!e.p.items.contains(item[j]),"no wrong item reward");
        }
        Progress roundTrip=Progress.fromMap(e.p.toMap(true));
        ok(roundTrip.hasFlag("V467_C01_RESULT_"+b),"decision persists in save");
        ok(roundTrip.items.contains(item[choice]),"collectible persists in save");
        e.at("riverside");e.at("dermaga");e.interact("pierend");
        ok(e.p.step.equals("C02_PHONE"),"C01 finishes and C02 starts");
        ok(e.p.chapters.contains("C01"),"C01 canonical complete");
        ok(e.p.hasFlag("CANON_CAFE_LETTER") && e.p.hasFlag("CANON_RIVERSIDE"),"canon unchanged");
        ok(e.scenes.contains("V467-C01-"+b+"@"+route),"branch specific dialogue heard");
        ok(e.scenes.contains("V467-C01-PIER-"+b+"@"+route),"branch callback at pier");
        String introFlag="V467_C01_INTRO_"+(route.equals("arland")?"A":"S")+"_"+(intro==0?"HONEST":"WAIT");
        ok(e.p.hasFlag(introFlag),"introduction choice persists");
        ok(e.scenes.contains("V467-C01-INTRO-"+route.toUpperCase(Locale.ROOT)+"-"+(intro==0?"HONEST":"WAIT")),
           "opening callback appears at sunset");
        ok(!e.scenes.contains("V467-C01-PIER-"+branch[(choice+1)%3]+"@"+route),"no other branch's pier dialogue");
    }
    static void oldSaveContinuation(StoryDb s,QuestDb q,MapDb maps,String route) {
        Env e=new Env(s,q,maps,route,"C01_LARAS2");
        e.interact("laras2");
        ok("C01_RIVERSIDE".equals(e.p.step),"legacy save without branch flags continues");
        e.at("riverside");e.at("dermaga");e.interact("pierend");
        ok("C02_PHONE".equals(e.p.step),"legacy save still reaches C02");
    }
    static void validation(StoryDb s,QuestDb q,MapDb m,String root) {
        Set<String> ids=new HashSet<>();
        for(QuestDb.Step step:q.steps.values())ok(ids.add(step.id),"no duplicate quest step "+step.id);
        for(String route:Arrays.asList("arland","sofia")) for(int i=0;i<2;i++) for(int choice=0;choice<3;choice++){
            path(s,q,m,route,i,choice);
        }
        for(String route:Arrays.asList("arland","sofia"))oldSaveContinuation(s,q,m,route);
    }
    public static void main(String[] args)throws Exception{
        String path=args.length>0?args[0]:"android/assets";
        StoryDb s=new StoryDb(read(path,"story.json"));
        QuestDb q=new QuestDb(read(path,"quests.json"));
        MapDb m=new MapDb(read(path,"maps.json"),read(path,"props.json"));
        validation(s,q,m,path);
        System.out.println("PASS: "+checks+" chapter-one quest/choice/save/canon assertions");
    }
}
