import com.arlandsofia.olu.logic.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
/** Real map collision-grid accessibility and reciprocal portal protection. */
public final class V472ChapterSixNavigationTest {
 static int checks=0;
 static void ok(boolean yes,String msg){checks++;if(!yes)throw new AssertionError("C06 NAV #"+checks+" "+msg);}
 static String read(String root,String fn)throws Exception{return new String(Files.readAllBytes(Paths.get(root,"data",fn)),StandardCharsets.UTF_8);}
 static boolean reachable(MapDb.Area map,float x,float y,float rad){
  int tile=16,w=(int)Math.ceil(map.w/tile),h=(int)Math.ceil(map.h/tile);
  boolean[] seen=new boolean[w*h];ArrayDeque<Integer> q=new ArrayDeque<>();
  int sx=(int)(map.spawnX/tile),sy=(int)(map.spawnY/tile);
  sx=Math.max(0,Math.min(w-1,sx));sy=Math.max(0,Math.min(h-1,sy));
  for(int r=0;r<96&&q.isEmpty();r+=tile){
   for(int dx=-r;dx<=r;dx+=tile)for(int dy=-r;dy<=r;dy+=tile){
    int a=sx+dx/tile,b=sy+dy/tile;
    if(a<0||b<0||a>=w||b>=h||map.blocked(a*tile+8,b*tile+8))continue;
    q.add(b*w+a);seen[b*w+a]=true;break;
   }
  }
  int[] dx={1,-1,0,0,1,-1,1,-1},dy={0,0,1,-1,1,-1,-1,1};
  while(!q.isEmpty()){
   int v=q.remove(),ax=v%w,ay=v/w;
   float px=ax*tile+8,py=ay*tile+8;
   if((px-x)*(px-x)+(py-y)*(py-y)<=rad*rad)return true;
   for(int j=0;j<8;j++){
    int nx=ax+dx[j],ny=ay+dy[j];if(nx<0||ny<0||nx>=w||ny>=h)continue;
    int n=ny*w+nx;
    if(seen[n]||map.blocked(nx*tile+8,ny*tile+8))continue;
    if(j>=4&&(map.blocked(nx*tile+8,py)||map.blocked(px,ny*tile+8)))continue;
    seen[n]=true;q.add(n);
   }
  }
  return false;
 }
 static MapDb.Door door(MapDb.Area a,String name){for(MapDb.Door d:a.doors)if(d.id.equals(name))return d;return null;}
 public static void main(String[]args)throws Exception{
  String root=args.length>0?args[0]:"android/assets";
  MapDb m=new MapDb(read(root,"maps.json"),read(root,"props.json"));QuestDb q=new QuestDb(read(root,"quests.json"));
  for(String id:new String[]{"V472_C06_HALL_ENTRY","V472_C06_FUTURES","V472_C06_REFLECT_A","V472_C06_REFLECT_S","V472_C06_ALIGN","V472_C06_PROMISE"}){
   QuestDb.Step st=q.step(id);ok(st!=null,"chapter6 quest exists "+id);
   for(QuestDb.Interactable it:st.interactables){
    MapDb.Area a=m.area(it.area);ok(a!=null,"interaction map "+it.id);
    ok(it.x>0&&it.y>0&&it.x<a.w&&it.y<a.h,"interaction in bounds "+it.id);
    ok(reachable(a,it.x,it.y,it.r),"player can walk to "+it.id);
   }
  }
  for(String[] tuple:new String[][]{{"eternal_garden","v472_garden_to_hall"},{"hall_of_tomorrow","v472_hall_to_garden"}}){
   MapDb.Area from=m.area(tuple[0]);MapDb.Door d=door(from,tuple[1]);ok(d!=null,"physical portal exists "+tuple[1]);
   MapDb.Area to=m.area(d.to);ok(to!=null,"destination exists "+d.to);
   ok(!to.blocked(d.tx,d.ty),"portal arrival unblocked "+tuple[1]);
   ok(!d.touchesAnyDoor(to),"portal arrival does not bounce "+tuple[1]);
   ok(reachable(from,d.cx(),d.cy(),38),"player can approach door "+tuple[1]);
  }
  System.out.println("PASS C06 NAV "+checks+" collision-grid/quest/portal checks");
 }
}
