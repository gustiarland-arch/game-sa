import com.arlandsofia.olu.logic.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
/** Collision-grid BFS, reciprocal portals, legacy quest anchors, new C05 world access. */
public final class V471ChapterFiveNavigationTest {
 static int checks=0;
 static void ok(boolean yes,String msg){checks++;if(!yes)throw new AssertionError("C05 NAV #"+checks+" "+msg);}
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
  for(String id:new String[]{"V471_C05_CLOCK_ENTRY","V471_C05_CLOCK_A","V471_C05_CLOCK_S","V471_C05_CLOCK_SWITCHES",
        "V471_C05_MOON_A","V471_C05_MOON_S","V471_C05_MOON_SHARED","V471_C05_BRIDGE_FRAGMENTS",
        "V471_C05_BRIDGE_SEQUENCE","V471_C05_BRIDGE_PUZZLE","V471_C05_QUIET_TRUTH","V471_C05_BRIDGE_RESTORE","V471_C05_FINAL_WALK"}){
   QuestDb.Step st=q.step(id);ok(st!=null,"chapter5 quest exists "+id);
   for(QuestDb.Interactable i:st.interactables){
    MapDb.Area area=m.area(i.area);ok(area!=null,"interaction area "+i.id);
    ok(i.x>=0&&i.y>=0&&i.x<area.w&&i.y<area.h,"interaction inside "+i.id);
    ok(reachable(area,i.x,i.y,i.r),"walkable from spawn: "+i.id);
   }
  }
  for(String[] tuple:new String[][]{
     {"starfall_village","v471_village_to_clock"},
     {"clockwork_station","clock_to_village"},
     {"clockwork_station","clock_to_moon"},
     {"moonlight_lake","moon_to_clock"},
     {"moonlight_lake","moon_to_bridge"},
     {"memory_bridge","bridge_to_moon"},
     {"memory_bridge","bridge_to_village"}}){
   MapDb.Area a=m.area(tuple[0]);MapDb.Door d=door(a,tuple[1]);ok(d!=null,"door exists "+tuple[1]);
   MapDb.Area target=m.area(d.to);ok(target!=null,"portal target present "+d.to);
   ok(!target.blocked(d.tx,d.ty),"arrival outside collision "+d.id);
   ok(!d.touchesAnyDoor(target),"arrival does not bounce "+d.id);
   ok(reachable(a,d.cx(),d.cy(),32),"entrance walkable from spawn "+d.id);
  }
  for(String id:new String[]{"C05_A_STARS","C05_S_SPARKS","C05_TO_VILLAGE","C05_MEET","C05_STARMAP",
     "C05_V26_A_SURVEY","C05_V26_S_NOTES","C05_V26_NIGHT_TALK","C05_V26_STARGAZE","C05_Q_ECHO"})
   ok(q.step(id)!=null,"legacy C05 step preserved "+id);
  System.out.println("PASS C05 NAV "+checks+" source physics-grid, interactive access and portal checks");
 }
}
