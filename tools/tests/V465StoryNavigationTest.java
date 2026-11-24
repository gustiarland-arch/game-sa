import com.arlandsofia.olu.logic.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Reachability and collision regression of the added story hotspots. */
public final class V465StoryNavigationTest {
 private static int checks=0;
 private static void ok(boolean c,String m){checks++;if(!c)throw new AssertionError("Nav #"+checks+": "+m);}
 private static String read(String base,String name)throws Exception{return new String(Files.readAllBytes(Paths.get(base,"data",name)),StandardCharsets.UTF_8);}
 private static boolean near(MapDb.Area a,float sx,float sy,float tx,float ty,float threshold){
    final int step=16,w=(int)(a.w/step)+1,h=(int)(a.h/step)+1;
    boolean[] seen=new boolean[w*h];ArrayDeque<Integer> q=new ArrayDeque<>();
    int ix=Math.max(0,Math.min(w-1,Math.round(sx/step))),iy=Math.max(0,Math.min(h-1,Math.round(sy/step)));
    if(a.blocked(ix*step,iy*step))return false;
    int index=iy*w+ix;seen[index]=true;q.add(index);
    while(!q.isEmpty()){
       int v=q.removeFirst(),x=v%w,y=v/w;
       float px=x*step,py=y*step;
       if(Math.hypot(px-tx,py-ty)<=threshold)return true;
       int[][] neighbors={{x-1,y},{x+1,y},{x,y-1},{x,y+1}};
       for(int[] p:neighbors){int xx=p[0],yy=p[1];if(xx<0||yy<0||xx>=w||yy>=h)continue;
         int j=yy*w+xx;if(!seen[j]&&!a.blocked(xx*step,yy*step)){seen[j]=true;q.add(j);} }
    }
    return false;
 }
 public static void main(String[] args)throws Exception{
   String assets=args.length>0?args[0]:"android/assets";
   MapDb maps=new MapDb(read(assets,"maps.json"),read(assets,"props.json"));
   MapDb.Area g=maps.area("galeri_komunitas"),c=maps.area("cafe"),v=maps.area("starfall_village"),t=maps.area("taman_kota");
   ok(g!=null&&c!=null&&v!=null&&t!=null,"required areas exist");
   ok(!g.blocked(g.spawnX,g.spawnY),"gallery entry spawn must not be blocked");
   ok(!g.blocked(290,410),"gallery empty-chair interaction accessible");
   ok(!g.blocked(520,320),"Sofia presentation interaction accessible");
   ok(!g.blocked(705,405),"gallery projector interaction accessible");
   ok(near(g,g.spawnX,g.spawnY,290,410,94),"gallery player can reach empty seat");
   ok(near(g,g.spawnX,g.spawnY,520,320,94),"gallery player can reach presentation stage");
   ok(near(g,g.spawnX,g.spawnY,705,405,94),"gallery player can reach projector");
   ok(near(c,c.spawnX,c.spawnY,115,465,50),"cafe gallery door is reachable");
   ok(near(v,880,640,960,726,92),"star-village shared proof hotspot reachable from meeting");
   ok(near(t,1000,490,1000,490,50),"second conversation takes place on navigable ground");
   System.out.println("PASS: "+checks+" v4.6.5 navigation checks");
 }
}
