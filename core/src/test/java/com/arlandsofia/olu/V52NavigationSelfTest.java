package com.arlandsofia.olu;

import com.arlandsofia.olu.logic.CameraFramingV52;
import com.arlandsofia.olu.logic.WorldNavigationV52;
import com.arlandsofia.olu.logic.Settings;
import com.arlandsofia.olu.logic.MapDb;
import com.arlandsofia.olu.logic.QuestDb;
import com.arlandsofia.olu.logic.QuestPathV52;
import com.arlandsofia.olu.logic.QuestCompass;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.HashMap;

/** Pure-Java regression for camera preferences, collision sweeping and save migration. */
public final class V52NavigationSelfTest {
    private static int checks;
    private static void yes(boolean ok,String msg){checks++;if(!ok)throw new AssertionError(msg);}
    public static void main(String[] args) throws Exception {
        yes(CameraFramingV52.gameplayScale(1,true)>CameraFramingV52.gameplayScale(1,false),"Indoor wide framing");
        yes(CameraFramingV52.gameplayScale(2,false)>CameraFramingV52.gameplayScale(1,false),"Wide preset");
        yes(CameraFramingV52.gameplayScale(0,false)<CameraFramingV52.gameplayScale(1,false),"Near preset");
        Settings s=new Settings();
        yes(s.cameraDistance==1,"Fresh install safe wider default");
        Map<String,Object> legacy=new HashMap<>();
        Settings restored=Settings.fromMap(legacy);
        yes(restored.cameraDistance==1,"Older settings migration");
        s.cameraDistance=2;
        Settings s2=Settings.fromMap(s.toMap());
        yes(s2.cameraDistance==2,"New camera preference saved");
        WorldNavigationV52.Collision c=new WorldNavigationV52.Collision(){
            public boolean blocked(float x,float y){return x<0||x>300||y<0||y>300||(x>=90&&x<=100&&y>=30&&y<=200);}
        };
        float[] normal=WorldNavigationV52.nearestOpen(c,42,100,50,50);
        yes(normal[0]==42&&normal[1]==100,"Legal spawn preserved");
        float[] recovered=WorldNavigationV52.nearestOpen(c,95,100,50,50);
        yes(!c.blocked(recovered[0],recovered[1]),"Blocked save recovered to nearby legal footprint");
        yes(!WorldNavigationV52.clearSegment(c,60,120,130,120),"Swept collision stops thin wall");
        yes(WorldNavigationV52.clearSegment(c,60,120,70,120),"Free movement preserved");
        yes(!WorldNavigationV52.clearSegment(c,60,120,Float.NaN,120),"Invalid coordinate rejected");
        if(args.length>0){
            String data=args[0]+"/data/";
            MapDb maps=new MapDb(new String(Files.readAllBytes(Paths.get(data+"maps.json")), StandardCharsets.UTF_8),
                    new String(Files.readAllBytes(Paths.get(data+"props.json")), StandardCharsets.UTF_8));
            QuestDb quests=new QuestDb(new String(Files.readAllBytes(Paths.get(data+"quests.json")), StandardCharsets.UTF_8));
            QuestDb.Step phone=quests.step("PRO_PHONE");
            yes(phone!=null,"prologue phone quest exists");
            for(String room:new String[]{"arland_room","sofia_room"}){
                MapDb.Area a=maps.area(room);
                QuestDb.Interactable target=null;
                for(QuestDb.Interactable it:phone.interactables) if(it.area.equals(room)){target=it;break;}
                yes(target!=null,"phone target in "+room);
                QuestPathV52.Result path=QuestPathV52.route(a,a.spawnX,a.spawnY,target.x,target.y,target.r);
                yes(path.found,"phone quest route remains traversable in "+room);
                yes(path.estimatedSteps>0,"nontrivial route in "+room);
                QuestCompass.Hint hint=QuestPathV52.hint(a,a.spawnX,a.spawnY,phone.interactables,
                        room.equals("arland_room")?"arland":"sofia");
                yes(hint!=null&&!hint.text().isEmpty(),"safe quest hint "+room);
            }
        }
        System.out.println("V5.2 NAVIGATION/CAMERA SELF TEST PASSED: "+checks+" checks");
    }
}
