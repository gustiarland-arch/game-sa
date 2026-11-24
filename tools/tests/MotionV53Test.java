import com.arlandsofia.olu.logic.MotionPersonalityV53;
import java.util.HashSet;
import java.util.Set;

public final class MotionV53Test {
    private static int checks=0;
    private static void check(boolean pass,String name) {
        checks++; if (!pass) throw new AssertionError(name);
    }
    public static void main(String[] args) {
        String[] ids={"arland","sofia","raka","rini","sari","melati","tigor","laras",
            "dito","wulan","juna","bimo","tika","darto","harun","ujang","ina","pos",
            "nara","bayu","eko","darmo","rara","udin","lumi"};
        Set<String> signatures=new HashSet<>();
        for(String id:ids) {
            MotionPersonalityV53.Style p=MotionPersonalityV53.forCharacter(id);
            check(p.cadence>=.70f && p.cadence<=1.30f,id+" cadence");
            check(p.walkSpeed>=.65f && p.walkSpeed<=1.3f,id+" walkSpeed");
            check(p.visualScale>=.90f && p.visualScale<=1.12f,id+" visual scale");
            check(p.bounce>=.30f && p.bounce<=1.65f,id+" bounce");
            check(p.daytimePose!=null && p.eveningPose!=null,id+" pose");
            check(MotionPersonalityV53.pauseSeconds(id,2,600)>0f,id+" pause");
            String sig=p.walkSpeed+":"+p.cadence+":"+p.bounce+":"+p.visualScale+":"+p.phase;
            check(signatures.add(sig),id+" must have individual motion signature");
            for(int day=1;day<=3;day++) for(int hour=0;hour<24;hour+=4) {
                check(MotionPersonalityV53.idlePose(id,hour,"cerah",false,day)!=null,id+" idle pose");
            }
        }
        check(MotionPersonalityV53.forCharacter("arland").walkSpeed==1f,"player walking physics unchanged");
        check(MotionPersonalityV53.forCharacter("sofia").walkSpeed==1f,"partner walking physics unchanged");
        check(MotionPersonalityV53.forCharacter("dito").walkSpeed>MotionPersonalityV53.forCharacter("sari").walkSpeed,
              "child moves faster than elder");
        check(MotionPersonalityV53.forCharacter("arland").bounce!=MotionPersonalityV53.forCharacter("sofia").bounce,
              "different emotional movement per route");
        System.out.println("V5.3 MotionPersonality: "+checks+" checks OK.");
    }
}
