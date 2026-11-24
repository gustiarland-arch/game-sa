import com.arlandsofia.olu.logic.*;
import java.nio.file.*;import java.nio.charset.StandardCharsets;import java.util.*;
/** Real MapDb collision-grid path access and reciprocal return portal for the Epilogue. */
public final class V473EpilogueNavigationTest {
 static int checks=0;
 static void ok(boolean v,String msg){checks++;if(!v)throw new AssertionError("Epilogue NAV "+checks+" "+msg);}
 static String read(String base,String name)throws Exception{return new String(Files.readAllBytes(Paths.get(base,"data",name)),StandardCharsets.UTF_8);}
 static boolean reach(MapDb.Area a,float x,float y,float radius){
  int t=16,w=(int)Math.ceil(a.w/(float)t),h=(int)Math.ceil(a.h/(float)t);
  boolean[] used=new boolean[w*h];ArrayDeque<Integer> todo=new ArrayDeque<>();
  int sx=(int)a.spawnX/t,sy=(int)a.spawnY/t;
  for(int r=0;r<96&&todo.isEmpty();r+=t){
   for(int dx=-r;dx<=r&&todo.isEmpty();dx+=t)for(int dy=-r;dy<=r;dy+=t){
    int nx=sx+dx/t,ny=sy+dy/t;if(nx<0||ny<0||nx>=w||ny>=h||a.blocked(nx*t+8,ny*t+8))continue;
    int v=ny*w+nx;used[v]=true;todo.add(v);break;
   }
  }
  int[] xs={1,-1,0,0,1,-1,1,-1},ys={0,0,1,-1,1,-1,-1,1};
  while(!todo.isEmpty()){
   int i=todo.remove(),ax=i%w,ay=i/w;
   float px=ax*t+8,py=ay*t+8;
   if((px-x)*(px-x)+(py-y)*(py-y)<=(radius+8)*(radius+8))return true;
   for(int z=0;z<8;z++){
    int nx=ax+xs[z],ny=ay+ys[z];if(nx<0||ny<0||nx>=w||ny>=h)continue;
    int j=ny*w+nx;if(used[j]||a.blocked(nx*t+8,ny*t+8))continue;
    if(z>=4&&(a.blocked(nx*t+8,py)||a.blocked(px,ny*t+8)))continue;
    used[j]=true;todo.add(j);
   }
  }
  return false;
 }
 static MapDb.Door door(MapDb.Area a,String id){for(MapDb.Door d:a.doors)if(d.id.equals(id))return d;return null;}
 public static void main(String[]args)throws Exception{
  String root=args[0]; MapDb map=new MapDb(read(root,"maps.json"),read(root,"props.json"));QuestDb quests=new QuestDb(read(root,"quests.json"));
  for(QuestDb.Step stage:quests.steps.values())if(stage.id.startsWith("V473_EPI_"))for(QuestDb.Interactable it:stage.interactables){
   MapDb.Area area=map.area(it.area);ok(area!=null,"map exists "+it.id);
   ok(!area.blocked(area.spawnX,area.spawnY),"spawn clear "+area.id);
   ok(reach(area,it.x,it.y,it.r),"interaction reachable from room spawn "+it.id+" at "+area.id);
  }
  for(String[] pair:new String[][]{{"galeri_komunitas","v473_gallery_to_letters"},{"ruang_dua_surat","v473_letters_exit"}}){
   MapDb.Area source=map.area(pair[0]);MapDb.Door d=door(source,pair[1]);ok(d!=null,"portal "+pair[1]+" present");
   MapDb.Area target=map.area(d.to);ok(target!=null,"destination map registered");
   ok(!target.blocked(d.tx,d.ty),"safe landing at "+d.to);
   ok(!d.touchesAnyDoor(target),"no door bounce at arrival "+d.to);
   ok(reach(source,d.cx(),d.cy(),24),"entrance reachable "+d.id);
  }
  // The global dual-route check cannot be spoofed by a local save flag.
  Progress p=Progress.newGame("arland",1,quests.firstStep(),map.area("arland_room"));p.step="EPI_FREE";p.area="galeri_komunitas";
  QuestEngine e=new QuestEngine(new StoryDb(read(root,"story.json")),quests,map,p,false);
  GlobalProgress g=new GlobalProgress();e.setGlobalProgress(g);
  MapDb.Door enter=door(map.area("galeri_komunitas"),"v473_gallery_to_letters");
  ok(e.doorLock(enter)!=null,"locked for single route completion");
  g.completed.get("arland").add("C06");ok(e.doorLock(enter)!=null,"still locked after only Arland route");
  g.completed.get("sofia").add("C06");ok(e.doorLock(enter)==null,"unlocks after BOTH chapter6 routes");
  System.out.println("PASS EPI NAV: "+checks+" collision BFS, two-way safe doors, global two-route gate");
 }
}
