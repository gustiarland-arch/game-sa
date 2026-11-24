import com.arlandsofia.olu.logic.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
/** Physics-grid reachability of new Chapter-2 objectives. */
public final class V468ChapterTwoNavigationTest {
    static int checks;
    static void ok(boolean yes,String msg){checks++;if(!yes)throw new AssertionError("C02 NAV #"+checks+" "+msg);}
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
        for(String stepId:Arrays.asList("V468_C02_LATER_NOTE","V468_C02_NO_SKETCH", "V468_C02_NO_REINVITE", "V468_C02_REUNION", "V468_C02_PHOTO_REPAIR")){
            QuestDb.Step st=q.step(stepId);
            ok(st!=null,"required step exists "+stepId);
            for(QuestDb.Interactable it:st.interactables){
                MapDb.Area map=m.area(it.area);
                ok(map!=null,"new interaction's map exists: "+it.id);
                ok(it.x>=0&&it.x<=map.w&&it.y>=0&&it.y<=map.h,"interaction inside its map "+it.id);
                ok(reachable(map,it.x,it.y,it.r),"interaction path reachable from spawn "+it.id);
            }
        }
        for(String id:Arrays.asList("C02_A_FLORIST","C02_S_PRINT","C02_DATE","C02_SUNSET")){
            QuestDb.Step st=q.step(id);
            for(QuestDb.Interactable it:st.interactables){
                MapDb.Area map=m.area(it.area);
                ok(reachable(map,it.x,it.y,it.r),"pre-existing interaction still reachable: "+it.id);
            }
        }
        System.out.println("PASS: "+checks+" Chapter-2 navigation/physical-accessibility assertions");
    }
}
