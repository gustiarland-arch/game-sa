import com.arlandsofia.olu.logic.SoundscapePlan;
import com.arlandsofia.olu.logic.Settings;
import java.util.*;

public final class SoundscapePlanTest {
    static int n;
    static void check(boolean ok, String explanation) { n++; if (!ok) throw new AssertionError(explanation); }
    public static void main(String[] args) {
        String[][] area = {
          {"arland_room","town"},{"sofia_room","town"},{"plaza","town"},{"jalan_kota","town"},
          {"taman_kota","town"},{"riverside","town"},{"cafe","cafe"},{"dapur","cafe"},
          {"toko_bunga","town"},{"arcade","game"},{"memory_garden","memory"},
          {"lantern_field","memory"},{"star_path","star"},{"starfall_village","star"},
          {"eternal_garden","tender"},{"perumahan","town"},{"perpustakaan","cafe"},
          {"ruang_arsip","memory"},{"dermaga","town"},{"hutan_bisik","memory"},
          {"bukit_bintang","star"},{"gua_kristal","memory"}
        };
        Set<String> reached=new LinkedHashSet<>();
        for (String[] entry:area) {
            String name=entry[0], old=entry[1];
            for(int minute:new int[]{390,850,1020,1250,1480}) {
                for(String weather:new String[]{"cerah","rain","hujan"}) {
                    boolean indoor=name.endsWith("room")||name.equals("cafe")||name.equals("dapur")||name.equals("perpustakaan")||name.equals("arcade")||name.equals("toko_bunga")||name.equals("ruang_arsip");
                    String a=SoundscapePlan.musicFor(name,old,weather,indoor,minute,5,true,null);
                    check(SoundscapePlan.musicPath(a)!=null,"Unknown BGM " + name + " " + a);
                    reached.add(a);
                    String ambience=SoundscapePlan.ambienceFor(name,weather,indoor,minute);
                    check(ambience==null||SoundscapePlan.ambientPath(ambience)!=null,"Unknown ambience " + name + " "+ ambience);
                    String classic=SoundscapePlan.musicFor(name,old,weather,indoor,minute,5,false,null);
                    check(SoundscapePlan.musicPath(classic)!=null,"Unknown legacy music " + name);
                    check("memory".equals(SoundscapePlan.musicFor(name,old,weather,indoor,minute,5,true,"memory")),"Quest override ignored");
                }
            }
        }
        for (String id:SoundscapePlan.MUSIC) if(!id.equals("menu_theme")) check(reached.contains(id),"New track never selected: "+id);
        check(reached.size()>=24,"Insufficient music coverage");
        check(SoundscapePlan.MUSIC.length==25,"New track catalog");
        check(SoundscapePlan.AMBIENTS.length==14,"Ambience catalog");
        check(SoundscapePlan.SFX.length==32,"SFX with legacy catalog plus cinematic effects");
        check(SoundscapePlan.CINEMATIC.length==10,"Seven original cinematic cues, two gallery cues and one final-letter cue");
        check(SoundscapePlan.musicPath("cinema_letter_tomorrow")!=null,"New letter soundtrack must be playable");
        for(String cue:SoundscapePlan.CINEMATIC) {
            check(SoundscapePlan.musicPath(cue)!=null,"Cinematic music path missing: "+cue);
            check(!reached.contains(cue),"Cinematic cue must be scene-triggered: "+cue);
        }
        for(String cue:new String[]{"flower_pick","paper_fold","cinema_heartbeat","cinema_whoosh"}) {
            check(SoundscapePlan.contains(SoundscapePlan.SFX,cue),"Missing cinematic SFX: "+cue);
        }
        check(SoundscapePlan.musicPath("../../evil")==null,"Unsafe music path");
        check(SoundscapePlan.ambientPath("../../evil")==null,"Unsafe ambience path");
        check("step_grass".equals(SoundscapePlan.footstepFor("taman_kota")),"Grass sound");
        check("step_wood".equals(SoundscapePlan.footstepFor("arland_room")),"Wood sound");
        check("step_stone".equals(SoundscapePlan.footstepFor("plaza")),"Stone sound");
        Settings s=new Settings();
        Map<String,Object> old=new HashMap<>();old.put("schema",1);old.put("music",.4);old.put("sfx",.6);
        Settings migrated=Settings.fromMap(old);
        check(migrated.variedMusic && migrated.footsteps,"V2.3 settings migration defaults");
        check(migrated.ambience>.01f,"Ambience should default on");
        Map<String,Object> saved=migrated.toMap();check(((Number)saved.get("schema")).intValue()==3,"Settings schema v2.8");
        saved.put("ambience",3); saved.put("music",-1);
        Settings clamped=Settings.fromMap(saved);check(clamped.ambience==1f && clamped.music==0f,"Clamp settings");
        System.out.println("SOUNDSCAPE PLAN OK: " + n + " checks, " + reached.size() + " reachable in-game music tracks");
    }
}
