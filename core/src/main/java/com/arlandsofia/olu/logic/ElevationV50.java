package com.arlandsofia.olu.logic;

import java.util.List;

/** Pure-Java collision transitions and height sampling for walkable 2.5D terraces.
 * Original map walls/doors remain authoritative; new elevations add side barriers
 * and a single stair entrance without altering old quest/save coordinates.
 */
public final class ElevationV50 {
    private ElevationV50() {}

    /** v5.4: walking pace on a flight of stairs relative to flat ground (player, partner, NPC). */
    public static final float STAIR_SPEED_FACTOR = 0.82f;

    /** Speed multiplier for a foot position: slower while on any stair flight. */
    public static float speedFactor(List<MapDb.Terrace> terraces,float x,float y){
        return onStairs(terraces,x,y)?STAIR_SPEED_FACTOR:1f;
    }

    /** Visual lift 0..rise. Foot position and save coordinates remain y-down. */
    public static float heightAt(List<MapDb.Terrace> terraces,float x,float y) {
        if(terraces==null) return 0f;
        float high=0f;
        for(MapDb.Terrace t:terraces){
            if(t.stairs(x,y)) {
                float u=(t.stairEnd()-y)/(t.stairEnd()-t.stairStart());
                high=Math.max(high,t.rise*Math.max(0f,Math.min(1f,u)));
            } else if(t.top(x,y)) high=Math.max(high,t.rise);
        }
        return high;
    }

    /** Additional topology rule. Enter/exit a plateau only via its stairs.
     * Prevent sideways walking off a stair at the upper half of its height.
     */
    public static boolean canStep(List<MapDb.Terrace> terraces,
                                  float fromX,float fromY,float toX,float toY) {
        if(terraces==null||terraces.isEmpty())return true;
        for(MapDb.Terrace t:terraces){
            boolean fromTop=t.top(fromX,fromY), toTop=t.top(toX,toY);
            if(fromTop!=toTop) {
                // A level boundary crossing is legal only through the stair mouth.
                if(!t.stairs(fromX,fromY) && !t.stairs(toX,toY))return false;
                // v5.4: accept the whole stair band that stairs() treats as walkable.
                // v5.0 only accepted the centre (width-12px), so feet near either railing
                // were "on the stairs" but could neither reach the top nor step down.
                if(toX<t.stairX() || toX>t.stairX()+t.stairWidth)return false;
                // Guard against frame-spike teleports across the whole flight.
                if(Math.abs(toY-fromY)>t.stairLength)return false;
            }
            boolean fromSt=t.stairs(fromX,fromY),toSt=t.stairs(toX,toY);
            if(fromSt!=toSt) {
                // The lower entrance is open; midway up the ramp the side railings are solid.
                float safe=t.stairEnd()-10f;
                if(fromY<safe && toY<safe && !fromTop && !toTop)return false;
            }
        }
        return true;
    }

    public static boolean onStairs(List<MapDb.Terrace> terraces,float x,float y){
        if(terraces==null)return false;
        for(MapDb.Terrace t:terraces)if(t.stairs(x,y))return true;
        return false;
    }

    public static String stepSound(List<MapDb.Terrace> terraces,float x,float y,String fallback){
        if(terraces==null)return fallback;
        for(MapDb.Terrace t:terraces)if(t.stairs(x,y)||t.top(x,y))
            return "wood".equals(t.style)||"cafe".equals(t.style)?"step_wood":"step_stone";
        return fallback;
    }
}
