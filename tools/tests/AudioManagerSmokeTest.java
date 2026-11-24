import com.arlandsofia.olu.AudioManager;
import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.logic.Settings;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.audio.Music;
import com.badlogic.gdx.files.FileHandle;
import java.util.*;

public final class AudioManagerSmokeTest {
    static int checks;
    static void check(boolean v,String text){ checks++;if(!v)throw new AssertionError(text); }
    static final List<MockMusic> streams=new ArrayList<>();
    static final class MockMusic implements Music {
        final String id;
        float volume;
        boolean playing,disposed,looping;
        MockMusic(String name){id=name;streams.add(this);}
        public void setLooping(boolean b){looping=b;}
        public void setVolume(float v){volume=v;check(v>=0&&v<=1,"volume out of range");}
        public void play(){check(!disposed,"playing disposed music");playing=true;}
        public void pause(){playing=false;}
        public void stop(){playing=false;}
        public void dispose(){check(!disposed,"double dispose");disposed=true;}
    }
    public static void main(String[] args){
        Gdx.audio=new Gdx.Audio(){public Music newMusic(FileHandle h){return new MockMusic(h.path);}};
        Gdx.app=new Gdx.App(){public void error(String t,String x,Throwable e){throw new AssertionError(x);}
            public void error(String t,String x){throw new AssertionError(x);} };
        Settings settings=new Settings();
        AudioManager a=new AudioManager(new Assets(),settings);
        a.music("menu_theme");a.update(2f);
        check(streams.size()==1&&streams.get(0).playing,"initial track starts");
        check(streams.get(0).volume>0.55f,"music volume");
        a.music("menu_theme");check(streams.size()==1,"same BGM must not reload");
        a.music("city_morning");a.ambience("birds_morning");
        check(streams.size()==3,"crossfade and ambience loaded");
        for(int i=0;i<100;i++)a.update(.03f);
        check(streams.get(0).disposed,"previous BGM released");
        check(!streams.get(1).disposed&&streams.get(1).playing,"new BGM survives");
        check(streams.get(2).playing,"ambience mixed concurrently");
        float before=streams.get(1).volume;
        a.duck(true);for(int i=0;i<100;i++)a.update(.03f);
        check(streams.get(1).volume<before*.75f,"dialog ducking");
        a.duck(false);for(int i=0;i<100;i++)a.update(.03f);
        check(streams.get(1).volume>before*.90f,"ducking restoration");
        settings.music=0f;a.update(.03f);check(streams.get(1).volume==0,"live music mute");
        settings.music=.6f;a.music("../../invalid");check(streams.size()==3,"unknown ID must not load");
        a.pauseAll();check(!streams.get(1).playing&&!streams.get(2).playing,"background pause");
        a.resumeAll();check(streams.get(1).playing&&streams.get(2).playing,"foreground resume");
        a.ambience(null);for(int i=0;i<110;i++)a.update(.03f);
        check(streams.get(2).disposed,"ambience crossfade-to-silence cleanup");
        a.music("rain_lullaby");a.music("city_evening");a.music("home_morning");
        for(int i=0;i<150;i++)a.update(.03f);
        int live=0;for(MockMusic m:streams)if(!m.disposed)live++;
        check(live==1,"rapid changes must release old streams");
        a.sfx("door_open",.3f);a.sfx("../invalid");
        a.dispose();for(MockMusic m:streams)check(m.disposed,"all streams released on dispose");
        System.out.println("AUDIO ENGINE HEADLESS OK: " +checks+" checks, crossfade/duck/pause/volume/lifetime");
    }
}
