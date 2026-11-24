import com.arlandsofia.olu.logic.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
/** Physics-grid reachability of new Chapter-2 objectives. */
public final class V469ChapterThreeNavigationTest {
    static int checks;
    static void ok(boolean yes,String msg){checks++;if(!yes)throw new AssertionError("C03 NAV #"+checks+" "+msg);}
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
        for(String id:Arrays.asList("V469_C03_A_FRAME","V469_C03_S_SCRAP","V469_C03_NEIGHBOR",
              "V469_C03_HALF_LETTER","C03_A_INGREDIENTS","C03_S_DECOR","C03_S_ARRANGE",
              "C03_V26_DETAILS","C03_PICNIC","C03_V464_GALLERY_PREP")){
            QuestDb.Step st=q.step(id);
            ok(st!=null,"C03 quest stage exists "+id);
            for(QuestDb.Interactable it:st.interactables){
                MapDb.Area map=m.area(it.area);
                ok(map!=null,"interaction's map exists: "+it.id);
                ok(it.x>=0&&it.x<=map.w&&it.y>=0&&it.y<=map.h,"within bounds "+it.id);
                ok(reachable(map,it.x,it.y,it.r),"walkable from map spawn "+it.id);
            }
        }
        System.out.println("PASS: "+checks+" Chapter-3 collision-grid reachability checks");
    }
}
