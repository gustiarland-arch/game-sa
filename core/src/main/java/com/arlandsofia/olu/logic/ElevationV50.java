package com.arlandsofia.olu.logic;

import java.util.List;

/** Pure-Java collision transitions and height sampling for walkable 2.5D terraces.
 * Original map walls/doors remain authoritative; new elevations add side barriers
 * and a single stair entrance without altering old quest/save coordinates.
 */
public final class ElevationV50 {
    private ElevationV50() {}

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
                // A true level boundary crossing occurs at the south edge on the stair centerline.
                if(!t.stairs(fromX,fromY) && !t.stairs(toX,toY))return false;
                float centerX=t.stairX()+t.stairWidth*.5f;
                if(Math.abs(toX-centerX)>t.stairWidth*.5f-6f)return false;
                if(Math.abs(toY-(t.y+t.h))>12f && Math.abs(fromY-(t.y+t.h))>12f)return false;
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
