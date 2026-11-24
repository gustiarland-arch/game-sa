import com.arlandsofia.olu.logic.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Chapter 2 narrative QA: plays ALL mandatory quest stages via real engine. */
public final class V468ChapterTwoTest {
    static int checks;
    static void ok(boolean b,String name){checks++;if(!b)throw new AssertionError("C02 runtime #"+checks+" "+name);}
    static String read(String root,String name)throws Exception{
        return new String(Files.readAllBytes(Paths.get(root,"data",name)),StandardCharsets.UTF_8);
    }
    static final class Run implements ActionRunner.Presenter {
        final QuestEngine e;
        final ActionRunner a;
        final Progress p;
        final StoryDb story;
        final MapDb maps;
        final Map<String,Integer> picks=new HashMap<>();
        final List<String> seen=new ArrayList<>(),music=new ArrayList<>(),sfx=new ArrayList<>();
        int cine,photoGames;
        boolean cancelPhoto;
        Run(StoryDb s,QuestDb q,MapDb maps,String r,String step) {
            this.story=s;this.maps=maps;
            p=Progress.newGame(r,1,q.firstStep(),maps.area(Routes.room(r)));
            p.step=step;
            e=new QuestEngine(s,q,maps,p,false);
            a=new ActionRunner(e,this);
            MapDb.flags=f->p.hasFlag(f);
        }
        Run select(String id,int n){picks.put(id,n);return this;}
        void interact(String id) {
            QuestDb.Interactable choice=null;
            for(QuestDb.Interactable it:e.step().interactables)
                if(it.id.equals(id)&&it.forRoute(p.route)){choice=it;break;}
            ok(choice!=null,"Interactable registered "+id+" at "+p.step);
            p.area=Routes.resolve(choice.area,p.route);
            ok(maps.area(p.area)!=null,"area exists for "+id);
            ok(e.interactables(p.area).contains(choice),"interactable currently enabled "+id+" / "+p.route+" / "+p.step);
            a.run(e.actionsFor(choice));
            ok(!a.busy(),"interact completed synchronously "+id);
        }
        public void playScene(String id,Runnable done) {
            StoryDb.Scene scene=story.scene(id);
            ok(scene!=null,"scene loaded "+id);
            ok(scene.route.equals("shared")||scene.route.equals(p.route),"scene route "+id);
            seen.add(id);
            if(!scene.choices.isEmpty()) {
                int selected=picks.getOrDefault(id,0);
                ok(selected>=0&&selected<scene.choices.size(),"choice index "+id);
                StoryDb.Choice c=scene.choices.get(selected);
                ok(!c.response(p.route).isEmpty(),"route-specific dialogue for "+id);
                e.addFlags(c.flags);
            }
            done.run();
        }
        public void playLines(List<StoryDb.Line> lines,String name,Runnable done){done.run();}
        public void openPuzzle(String id,ActionRunner.BoolCallback done){done.done(true);}
        public void openMinigame(String id,ActionRunner.IntCallback done){
            if("photobooth".equals(id)){photoGames++;if(cancelPhoto){done.done(-1);return;}}
            done.done(3);
        }
        public void openShop(String id,Runnable done){done.run();}
        public void warp(String area,float x,float y,String dir,Runnable done){
            String actual=Routes.resolve(area,p.route);
            ok(maps.area(actual)!=null,"warp destination valid "+actual);
            ok(!maps.area(actual).blocked(x,y),"warp destination not inside obstacle "+actual+" at "+x+","+y);
            p.area=actual;p.x=x;p.y=y;p.dir=dir;done.run();
        }
        public void chapterCard(String chapter,Runnable done){done.run();}
        public void chapterEnd(String chapter,Runnable done){done.run();}
        public void credits(Runnable done){done.run();}
        public void cine(List<Map<String,Object>> cmds,Runnable done){
            ok(cmds!=null&&!cmds.isEmpty(),"cinematic command list exists");cine++;done.run();
        }
        public void toast(String t){}
        public void sfx(String id){sfx.add(id);}
        public void music(String id){music.add(id);}
        public void emote(String who,String emotion){}
        public void companionChanged(boolean value){}
        public void stepChanged(){}
        public void onIdle(){}
    }
    static void freeDay(Run e) {
        ok(e.p.step.equals("C02_FREE"),"free day reached");
        e.interact("f2_juna");
        ok(e.p.count("hari_C02")==1,"first side mission actually completed");
        e.interact("f2_dito");
        e.interact("f2_hide1");e.interact("f2_hide2");e.interact("f2_hide3");
        ok(e.p.hasFlag("C02_FREE_DONE"),"two distinct side missions complete");
        ok(e.p.count("hari_C02")>=2,"free activity counter persists");
    }
    static void path(StoryDb s,QuestDb q,MapDb m,String route,int answer,int style,int gaze,int pose,int c01,int order) {
        Run r=new Run(s,q,m,route,"C02_PHONE");
        String c01flag=new String[]{"LISTEN","RECORD","TRACE"}[c01];
        r.p.flags.add("V467_C01_RESULT_"+c01flag);
        String intro=route.equals("arland")?"V468-C02-A-INVITE":"V468-C02-S-REPLY";
        r.select(intro,answer).select("V464-C02-WALK-"+(route.equals("arland")?"A":"S"),style)
          .select("V468-C02-S-NEW-INVITE",style%2)
          .select("V468-C02-GAZEBO",gaze).select("V468-C02-PHOTO-CHOICE",pose);
        r.interact("phone2");
        if(route.equals("sofia")){
            ok(r.p.step.equals("C02_S_OUTFIT"),"Sofia retains wardrobe prep");
            r.interact("wardrobe");
        }
        freeDay(r);
        if(route.equals("arland")) {
            ok(r.p.step.equals("C02_A_FLORIST"),"Arland keeps exclusive florist beat");
            r.interact("florist");
            ok(r.p.hasFlag("C02_ARLAND_GIFT_READY"),"Arland gift prepared");
            ok(r.p.hasItem("bunga_pita"),"Arland owns ribbon flower, not Sofia photo");
        } else {
            ok(r.p.step.equals("C02_S_PRINT"),"Sofia retains exclusive photo printing");
            r.interact("juna_print");
            ok(r.p.hasItem("foto_kecil"),"Sofia prepared the city photo");
        }
        boolean skipped=route.equals("sofia")&&answer!=0;
        int startDay=r.p.day;
        if(route.equals("sofia")&&answer==2) {
            ok("V468_C02_NO_SKETCH".equals(r.p.step),"decline truly opens a different gallery quest");
            ok(!r.p.companion,"decline does not automatically put Arland into the party");
            r.interact("v468_solo_sketch");
            ok(r.p.hasItem("v468_independent_sketch"),"meaningful independently earned sketch item");
            ok("V468_C02_NO_REINVITE".equals(r.p.step),"no automatic immediate reunion");
            r.interact("v468_solo_note");
            ok(r.p.hasFlag("V468_S_REINVITE_BY_CHOICE"),"reinvitation comes from Sofia choice");
        } else if(route.equals("sofia")&&answer==1) {
            ok("V468_C02_LATER_NOTE".equals(r.p.step),"postponement opens journal quest, not date");
            r.interact("v468_later_note");
            ok(r.p.hasItem("v468_date_note"),"postponement keeps a tangible plan");
        }
        if(skipped) {
            ok(r.p.day==startDay+1,"postpone / decline moves a real in-game day");
            ok(r.p.minute==7*60,"new day begins in morning");
            ok(r.p.step.equals("V468_C02_REUNION"),"user choices require player to go to agreed reunion");
            ok(!r.seen.contains("C02-X01"),"canon date NOT forced on same-day decline");
            Progress snapshot=Progress.fromMap(r.p.toMap(true));
            ok(snapshot.day==startDay+1&&snapshot.step.equals("V468_C02_REUNION"),"save round-trip preserves postponed route and date");
            r.interact("v468_reunion");
            ok(r.p.hasFlag("V468_C02_REUNITED"),"reunion happens by choice");
            ok(r.p.step.equals("C02_DATE"),"both alternate routes resume canonical date on next day");
        } else {
            ok(r.p.step.equals("C02_TO_CAFE"),"direct yes invitation leads to cafe");
            r.interact("date");
            ok(r.p.step.equals("C02_V464_INTERLUDE"),"same-day date opens an activity choice");
            String branch=route.equals("arland")?new String[]{"v464_park","v464_later","v464_ask"}[style]
                :new String[]{"v464_park","v464_solo","v464_later"}[style];
            r.interact(branch);
            ok(r.p.step.equals("C02_DATE"),"optional activity genuinely completed");
            ok(r.p.day==startDay,"accepting does not skip a calendar day");
        }
        ok(r.p.companion,"partner accompanies actual date");
        ok(r.seen.contains("C02-X01"),"canonical shared cafe scene occurs");
        ok(r.seen.contains("V468-C02-SOFT-SKETCH"),"gallery promise foreshadow present");
        if(order==0){r.interact("gazebo");r.interact("booth");}
        else {r.interact("booth");}
        if(route.equals("arland")){
            ok(r.p.step.equals("V468_C02_PHOTO_REPAIR"),"Arland real machine repair quest mandatory");
            r.interact("v468_photo_panel");
            ok(r.p.step.equals("C02_DATE"),"machine repair returns to original date quest");
            ok(r.p.hasFlag("V468_C02_PHOTO_FIXED"),"machine really repaired");
            r.interact("booth");
        }
        if(order==1)r.interact("gazebo");
        ok(r.p.step.equals("C02_SUNSET"),"both photo + garden needed to unlock sunset");
        ok(r.p.hasFlag("CANON_DATE_PHOTO"),"existing photo canon preserved");
        ok(r.p.hasFlag("V468_C02_LANTERN_CLUE"),"new photo mystery playable");
        ok(r.p.hasFlag("V468_C02_GAZEBO_"+new String[]{"LAUGH","QUIET","LISTEN"}[gaze]),"gazebo decision saved");
        ok(r.p.hasFlag("V468_C02_PHOTO_"+new String[]{"LAUGH","LOOK","BLUR"}[pose]),"photo pose decision saved");
        ok(r.seen.contains("V468-C02-CH1-"+c01flag),"prior chapter perspective recalled");
        ok(r.p.hasItem("v468_lantern_photo"),"unique lantern print collected");
        ok(r.cine>=1&&r.sfx.contains("photo_lantern_v468"),"photo cinematic with original SFX actually runs");
        ok(r.music.contains("cinema_date_choices_v468"),"new original audio played");
        Progress before=Progress.fromMap(r.p.toMap(true));
        ok(before.hasFlag("V468_C02_LANTERN_CLUE"),"new mystery persists in save");
        ok(before.hasFlag("V467_C01_RESULT_"+c01flag),"C01 decision persists in save");
        r.interact("pier");
        ok(r.p.chapters.contains("C02"),"C02 completed and marked");
        ok(r.p.step.equals(route.equals("arland")?"C03_A_IDEA":"C03_S_CORNER"),"real Chapter 3 entry step reached");
        ok(r.seen.contains("C02-X04"),"preserved canonical sunset played");
        String selectedMemory="V468-C02-PHOTO-MEMORY-"+new String[]{"LAUGH","LOOK","BLUR"}[pose];
        ok(r.seen.contains(selectedMemory),"specific photo decision recalled at pier");
        if(route.equals("sofia")){
            ok(r.p.items.contains("bunga_pita"),"Sofia receives ribbon flower");
            ok(!r.p.items.contains("foto_kecil"),"Sofia gives away small printed photo");
            String name=new String[]{"YES","LATER","NO"}[answer];
            ok(r.seen.contains("V468-C02-PAYOFF-"+name),"consent and timing remembered at sunset");
        } else {
            ok(r.p.items.contains("foto_kecil"),"Arland receives printed small photo");
            ok(!r.p.items.contains("bunga_pita"),"Arland gives away ribbon flower");
        }
        ok(!r.seen.contains("V468-C02-PAYOFF-"+(route.equals("arland")?"NO":"BLANK")),"no unearned consent scenes");
    }
    static void retries(StoryDb s,QuestDb q,MapDb m) {
        Run r=new Run(s,q,m,"arland","C02_DATE");
        r.cancelPhoto=true;
        // The machine is already repaired in this cancellation-only scenario.
        r.p.flags.add("V468_C02_PHOTO_FIXED");
        r.interact("booth");
        ok(r.p.step.equals("C02_DATE"),"cancelled photobooth retains quest");
        ok(!r.p.hasFlag("CANON_DATE_PHOTO"),"no photo completion from cancelled minigame");
        ok(r.p.count("date_spots")==0,"no unearned photo progress");
        r.cancelPhoto=false;
        r.interact("booth");
        ok(r.p.count("date_spots")==1,"minigame can be retried and completed");
    }
    static void legacy(StoryDb s,QuestDb q,MapDb m) {
        for(String route:Arrays.asList("arland","sofia")){
            Run r=new Run(s,q,m,route,"C02_TO_CAFE");
            r.interact("date");
            ok(r.p.step.equals("C02_V464_INTERLUDE"),"legacy save can still reach cafe outing");
            r.interact("v464_park");
            if(route.equals("arland")){
                r.interact("booth");r.interact("v468_photo_panel");
            }
            r.interact("booth");r.interact("gazebo");r.interact("pier");
            ok(r.p.step.startsWith("C03_"),"legacy save with no new flags reaches C03");
        }
    }
    public static void main(String[] args)throws Exception{
        String asset=args.length>0?args[0]:"android/assets";
        StoryDb s=new StoryDb(read(asset,"story.json"));
        QuestDb q=new QuestDb(read(asset,"quests.json"));
        MapDb m=new MapDb(read(asset,"maps.json"),read(asset,"props.json"));
        for(int answer=0;answer<3;answer++)
            for(int style=0;style<3;style++)
                for(int gaze=0;gaze<3;gaze++)
                    for(int pose=0;pose<3;pose++)
                        for(int c01=0;c01<3;c01++){
                            path(s,q,m,"arland",answer,style,gaze,pose,c01,(style+pose)%2);
                            path(s,q,m,"sofia",answer,style,gaze,pose,c01,(style+c01)%2);
                        }
        retries(s,q,m);
        legacy(s,q,m);
        System.out.println("PASS: "+checks+" Chapter-2 runtime checks (486 full routes + cancellation + legacy + saves)");
    }
}
