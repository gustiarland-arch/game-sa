import com.arlandsofia.olu.logic.AnimationMathV462;
import com.arlandsofia.olu.logic.WorldAtmosphereV462;
import com.arlandsofia.olu.logic.WorldClock;
import java.util.HashSet;

/** Pure headless regression checks: facing, FPS independence, lighting budgets, all original area themes plus later chapters. */
public final class VisualV462Test {
    private static int n;
    private static void ok(boolean b,String why){ n++;if(!b)throw new AssertionError(why); }
    public static void main(String[] args){
        int[] dx={0,-1,-1,-1,0,1,1,1};
        int[] dy={1,1,0,-1,-1,-1,0,1};
        for(int i=0;i<8;i++)ok(AnimationMathV462.facing(dx[i],dy[i],0)==i,"facing 8-way "+i);
        ok(AnimationMathV462.facing(0,0,7)==7,"zero delta preserves visual facing");
        ok(AnimationMathV462.diagonalLean(1)<0 && AnimationMathV462.diagonalLean(7)>0,"diagonal lean");
        float v1=0f,v2=0f;
        for(int i=0;i<60;i++)v1=AnimationMathV462.blend(v1,1f,1f/60f,12f);
        for(int i=0;i<120;i++)v2=AnimationMathV462.blend(v2,1f,1f/120f,12f);
        ok(Math.abs(v1-v2)<0.001f,"independent of display refresh rate");
        ok(AnimationMathV462.blend(1,0,1f/60f,12)<1,"stop transitions smoothly");
        HashSet<String> seen=new HashSet<>();
        for(int i=0;i<WorldAtmosphereV462.count();i++){
            String id=WorldAtmosphereV462.areaId(i);
            ok(seen.add(id),"unique area theme: "+id);
            ok(WorldAtmosphereV462.isMapped(id),"mapped area: "+id);
            int type=WorldAtmosphereV462.type(id);
            ok(type>=0&&type<=5,"valid profile: "+id);
            ok(WorldAtmosphereV462.particleCount(0,false,type)==0,"quality 0 effects disabled");
            ok(WorldAtmosphereV462.particleCount(2,false,type)>=WorldAtmosphereV462.particleCount(1,false,type),"quality budget");
        }
        ok(WorldAtmosphereV462.count()>=27,"all original map themes survive later chapters");
        ok(WorldAtmosphereV462.isMapped("hall_of_tomorrow"),"Chapter6 new map has rendering profile");
        ok(WorldAtmosphereV462.type("hall_of_tomorrow")==WorldAtmosphereV462.STAR,"future hall visual style");
        ok(WorldAtmosphereV462.type("clockwork_station")==WorldAtmosphereV462.STAR,"clockwork atmosphere");
        ok(WorldAtmosphereV462.type("moonlight_lake")==WorldAtmosphereV462.WATER,"moonlight atmosphere");
        ok(WorldAtmosphereV462.type("memory_bridge")==WorldAtmosphereV462.STAR,"bridge atmosphere");
        ok(!WorldAtmosphereV462.isMapped("not_a_map"),"unsupported area not silently accepted");
        int forest=WorldAtmosphereV462.type("hutan_bisik");
        ok(WorldAtmosphereV462.fireflies(forest,false,false,22*60),"night fireflies outdoors");
        ok(!WorldAtmosphereV462.fireflies(forest,false,true,22*60),"no fireflies in rain");
        ok(!WorldAtmosphereV462.fireflies(forest,true,false,22*60),"no fireflies indoors");
        ok(WorldAtmosphereV462.mistAlpha(forest,false,true,7*60)>0,"forest mist during rain");
        ok(WorldAtmosphereV462.sunbeamAlpha(forest,false,false,7*60)>0,"forest morning sunbeams");
        ok(WorldAtmosphereV462.sunbeamAlpha(forest,false,true,7*60)==0,"rays hidden by rain");
        ok(WorldAtmosphereV462.sunbeamAlpha(forest,false,false,23*60)==0,"rays hidden at night");
        for(int i=0;i<30;i++){
            float x=WorldAtmosphereV462.frac(i,17);
            ok(x>=0f&&x<1f,"deterministic particle interval");
            ok(x==WorldAtmosphereV462.frac(i,17),"stable random visual positions");
        }
        System.out.println("PASS: "+n+" v4.6.2 animation and world-graphics assertions");
    }
}
