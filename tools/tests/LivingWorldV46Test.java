import com.arlandsofia.olu.logic.LivingWorldV46;

public final class LivingWorldV46Test {
    static int checks = 0;
    static void require(boolean valid,String message) {
        checks++;
        if(!valid) throw new AssertionError(message);
    }
    public static void main(String[] args) {
        float day = LivingWorldV46.walkingSpeed(13,"cerah",false);
        float rain = LivingWorldV46.walkingSpeed(13,"rain",false);
        float night = LivingWorldV46.walkingSpeed(23,"cerah",false);
        require(day > rain && day > night,"weather/time changes actual walking pace");
        require(LivingWorldV46.walkingSpeed(13,"rain",true)==day,"rain doesn't slow indoor movement");
        LivingWorldV46.Collision allBlocked=(x,y)->true;
        LivingWorldV46.Target t=LivingWorldV46.wanderTarget("npc",2,600,30,30,50,30,30,false,"rain",allBlocked);
        require(t.x==30 && t.y==30,"blocked paths must not teleport");
        LivingWorldV46.Collision empty=(x,y)->false;
        LivingWorldV46.Target good=LivingWorldV46.wanderTarget("npc",2,600,30,30,50,30,30,false,"cerah",empty);
        require(Float.isFinite(good.x)&&Float.isFinite(good.y),"safe target must be finite");
        // NPC should not repeat one waypoint forever while the world minute
        // stays inside the same 15-minute interval.
        LivingWorldV46.Target seq1=LivingWorldV46.wanderTarget("npc",2,600,
                30,30,50,30,30,false,"cerah",empty,1);
        LivingWorldV46.Target seq2=LivingWorldV46.wanderTarget("npc",2,600,
                30,30,50,30,30,false,"cerah",empty,2);
        require(seq1.x!=seq2.x||seq1.y!=seq2.y,"consecutive waypoint selection must vary");
        LivingWorldV46.Target again=LivingWorldV46.wanderTarget("npc",2,600,
                30,30,50,30,30,false,"cerah",empty,1);
        require(seq1.x==again.x && seq1.y==again.y,"waypoint sequence remains deterministic");
        LivingWorldV46.Target noTeleport=LivingWorldV46.wanderTarget("npc",2,600,
                30,30,50,30,30,false,"cerah",allBlocked,5);
        require(noTeleport.x==30 && noTeleport.y==30,"blocked sequence never teleports");
        require(LivingWorldV46.pauseSeconds("npc",3,420)>=2.6f,"minimum pause time");
        require(LivingWorldV46.pauseSeconds("npc",3,420)
                ==LivingWorldV46.pauseSeconds("npc",3,420),"NPC routines deterministic");
        require("sweep".equals(LivingWorldV46.idlePose("darto",8,"cerah",false)),"morning job");
        require("sit".equals(LivingWorldV46.idlePose("darto",8,"rain",false)),"rain affects idle");
        require("read".equals(LivingWorldV46.idlePose("laras",21,"cerah",true)),"night habit");
        System.out.println("PASS: "+checks+" LivingWorld v4.6 assertions");
    }
}
