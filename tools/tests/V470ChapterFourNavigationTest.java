import com.arlandsofia.olu.logic.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
/** Physics-grid reachability and save-compatible portals of Chapter 4 Rain Garden. */
public final class V470ChapterFourNavigationTest {
    static int checks;
    static void ok(boolean yes,String msg){checks++;if(!yes)throw new AssertionError("C04 NAV #"+checks+" "+msg);}
    static String read(String root,String fn)throws Exception{return new String(Files.readAllBytes(Paths.get(root,"data",fn)),StandardCharsets.UTF_8);}
    static boolean reachable(MapDb.Area map,float x,float y,float radius) {
        int tile=14,w=(int)Math.ceil(map.w/tile),h=(int)Math.ceil(map.h/tile);
        boolean[] seen=new boolean[w*h]; ArrayDeque<Integer> q=new ArrayDeque<>();
        int startX=(int)(map.spawnX/tile),startY=(int)(map.spawnY/tile);
        startX=Math.max(0,Math.min(w-1,startX));startY=Math.max(0,Math.min(h-1,startY));
        for(int r=0;r<100&&!(!q.isEmpty());r+=tile){
            for(int dx=-r;dx<=r;dx+=tile)for(int dy=-r;dy<=r;dy+=tile){
                int a=startX+dx/tile,b=startY+dy/tile;
                if(a<0||b<0||a>=w||b>=h||map.blocked(a*tile+7,b*tile+7))continue;
                q.add(b*w+a);seen[b*w+a]=true;break;
            }
        }
        int[] dx={1,-1,0,0,1,-1,1,-1},dy={0,0,1,-1,1,-1,-1,1};
        while(!q.isEmpty()){
            int c=q.poll(),gx=c%w,gy=c/w;
            float px=gx*tile+7,py=gy*tile+7;
            float distanceX=px-x,distanceY=py-y;
            if(distanceX*distanceX+distanceY*distanceY<=radius*radius)return true;
            for(int k=0;k<dx.length;k++){
                int nx=gx+dx[k],ny=gy+dy[k];
                if(nx<0||ny<0||nx>=w||ny>=h)continue;
                int next=ny*w+nx;
                if(seen[next]||map.blocked(nx*tile+7,ny*tile+7))continue;
                if(k>=4&&(map.blocked(nx*tile+7,py)||map.blocked(px,ny*tile+7)))continue;
                seen[next]=true;q.add(next);
            }
        }
        return false;
    }
    public static void main(String[] args)throws Exception{
        String assets=args.length>0?args[0]:"android/assets";
        QuestDb q=new QuestDb(read(assets,"quests.json"));
        MapDb m=new MapDb(read(assets,"maps.json"),read(assets,"props.json"));
        for(String id:Arrays.asList("V470_C04_A_WARN","V470_C04_A_SILENT","V470_C04_A_HELP","V470_C04_A_HELP_OUT",
              "V470_C04_S_PREP","V470_C04_A_AFTER","V470_C04_S_AFTER",
              "V470_C04_A_PROOF","V470_C04_S_PROOF","C04_LIGHTS",
              "C04_V464_A_GALLERY","C04_V464_S_GALLERY","C04_PUZZLE","C04_V465_SECOND_TALK")){
            QuestDb.Step st=q.step(id);
            ok(st!=null,"C04 quest stage exists "+id);
            for(QuestDb.Interactable it:st.interactables){
                MapDb.Area map=m.area(it.area);
                ok(map!=null,"interaction's map exists: "+it.id);
                ok(it.x>=0&&it.x<=map.w&&it.y>=0&&it.y<=map.h,"within bounds "+it.id);
                ok(reachable(map,it.x,it.y,it.r),"walkable from map spawn "+it.id);
            }
        }
        // New Rain Garden is reciprocal and does not bounce the player immediately.
        MapDb.Area park=m.area("taman_kota"), rain=m.area("rain_garden"), old=m.area("lantern_field");
        ok(rain!=null&&old!=null,"dedicated Rain Garden and preserved Lantern Field");
        ok(rain.w==1920&&rain.h==1280,"new map geometry matches original texture");
        MapDb.Door enter=null,back=null,legacy=null;
        for(MapDb.Door d:park.doors)if(d.id.equals("park_to_rain_garden"))enter=d;
        for(MapDb.Door d:rain.doors)if(d.id.equals("rain_garden_to_park"))back=d;
        for(MapDb.Door d:old.doors)if(d.id.equals("legacy_lantern_to_rain_garden"))legacy=d;
        ok(enter!=null&&back!=null&&legacy!=null,"forward, return and old-save rescue portal are all present");
        for(MapDb.Door d:new MapDb.Door[]{enter,back,legacy}){
            MapDb.Area source=d==enter?park:d==back?rain:old, target=m.area(d.to);
            ok(target!=null,"door destination exists "+d.id);
            ok(!target.blocked(d.tx,d.ty),"arrival not blocked "+d.id);
            ok(!d.touchesAnyDoor(target),"arrival does not immediately re-trigger another door "+d.id);
            ok(reachable(source,d.cx(),d.cy(),28),"door source reachable from spawn "+d.id);
        }
        StoryDb story=new StoryDb(read(assets,"story.json"));
        Progress p=Progress.newGame("arland",1,q.firstStep(),m.area("arland_room"));
        QuestEngine e=new QuestEngine(story,q,m,p,false);
        p.step="C01_PUZZLE";
        ok(e.doorLock(enter)!=null&&e.doorLock(legacy)!=null,"Rain Garden unavailable before conflict");
        p.step="C04_LIGHTS";
        ok(e.doorLock(enter)==null&&e.doorLock(legacy)==null,"Rain Garden open during C04 incl old C04 save at Lantern Field");
        p.step="C05_FREE";
        ok(e.doorLock(legacy)!=null,"old Lantern Field is reserved for Chapter 5 after conflict");

        System.out.println("PASS: "+checks+" Chapter-4 collision-grid reachability checks");
    }
}
