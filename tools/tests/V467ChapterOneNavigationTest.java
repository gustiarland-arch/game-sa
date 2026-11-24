import com.arlandsofia.olu.logic.*;
import java.util.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

/** Verify new C01 interactions are physically approachable without teleporting. */
public final class V467ChapterOneNavigationTest {
    static int count=0;
    static void ok(boolean cond,String msg){count++; if(!cond) throw new AssertionError("C01-NAV #"+count+": "+msg);}
    static String read(String f,String p)throws Exception{return new String(Files.readAllBytes(Paths.get(f,"data",p)),StandardCharsets.UTF_8);}
    static boolean reachable(MapDb.Area map,float x,float y,float radius) {
        final int tile=14;
        int w=(int)Math.ceil(map.w/tile),h=(int)Math.ceil(map.h/tile);
        boolean[] seen=new boolean[w*h];
        ArrayDeque<Integer> queue=new ArrayDeque<>();
        int startX=Math.max(0,Math.min(w-1,(int)(map.spawnX/tile)));
        int startY=Math.max(0,Math.min(h-1,(int)(map.spawnY/tile)));
        for(int dist=0;dist<=70;dist+=tile) {
            for(int dx=-dist;dx<=dist;dx+=tile)for(int dy=-dist;dy<=dist;dy+=tile) {
                int xx=startX+dx/tile,yy=startY+dy/tile;
                if(xx>=0&&yy>=0&&xx<w&&yy<h&&!map.blocked(xx*tile+tile/2,yy*tile+tile/2)){
                    int start=yy*w+xx;seen[start]=true;queue.add(start);dist=80;break;
                }
            }
        }
        int[] ox={1,-1,0,0,1,-1,1,-1},oy={0,0,1,-1,1,-1,-1,1};
        int iterations=0;
        while(!queue.isEmpty()) {
            int current=queue.removeFirst(),gx=current%w,gy=current/w;
            float px=gx*tile+tile/2f,py=gy*tile+tile/2f;
            float dx=px-x,dy=py-y;
            if(dx*dx+dy*dy<=radius*radius)return true;
            for(int k=0;k<ox.length;k++) {
                int nx=gx+ox[k],ny=gy+oy[k];
                if(nx<0||ny<0||nx>=w||ny>=h)continue;
                int index=ny*w+nx;
                if(seen[index]||map.blocked(nx*tile+tile/2f,ny*tile+tile/2f))continue;
                if(k>=4 && (map.blocked(nx*tile+tile/2f,py)||map.blocked(px,ny*tile+tile/2f)))continue;
                seen[index]=true;queue.add(index);
            }
            if(++iterations>w*h)break;
        }
        return false;
    }
    public static void main(String[] args)throws Exception{
        String root=args.length>0?args[0]:"android/assets";
        MapDb m=new MapDb(read(root,"maps.json"),read(root,"props.json"));
        QuestDb q=new QuestDb(read(root,"quests.json"));
        for(String id:Arrays.asList("V467_C01_LISTEN","V467_C01_RECORD","V467_C01_TRACE")) {
            QuestDb.Step step=q.step(id);
            ok(step!=null,"new branch exists "+id);
            for(QuestDb.Interactable it:step.interactables) {
                MapDb.Area map=m.area(it.area);
                ok(map!=null,"branch's area exists");
                ok(it.x>=0&&it.x<=map.w&&it.y>=0&&it.y<=map.h,"interaction within area bounds");
                ok(reachable(map,it.x,it.y,it.r),"interaction reachable from area spawn: "+id);
            }
        }
        for(String id:Arrays.asList("V467_C01_CAFE_HELP", "V467_C01_CAFE_A_FIND", "V467_C01_CAFE_S_FIND")) {
            QuestDb.Step step=q.step(id);
            ok(step!=null,"cafe quest exists "+id);
            for(QuestDb.Interactable it:step.interactables) {
                MapDb.Area map=m.area(it.area);
                ok(map!=null,"cafe quest map exists");
                ok(reachable(map,it.x,it.y,it.r),"cafe action reachable from spawn: "+it.id);
            }
        }
        System.out.println("PASS: "+count+" C01 navigation accessibility assertions");
    }
}
