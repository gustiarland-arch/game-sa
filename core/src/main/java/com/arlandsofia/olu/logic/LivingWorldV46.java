package com.arlandsofia.olu.logic;

/**
 * Living World 3.0: deterministic ambient NPC routines. Uses existing
 * maps, actor sprites, time and weather; no new save schema or assets.
 */
public final class LivingWorldV46 {
    private LivingWorldV46() {}

    public interface Collision {
        boolean blocked(float x, float y);
    }

    public static final class Target {
        public final float x, y;
        public Target(float x,float y) {this.x=x;this.y=y;}
    }

    public static float walkingSpeed(int hour,String weather,boolean indoor) {
        float base=(hour >= 20 || hour < 6) ? 29f : 38f;
        if(!indoor && ("rain".equals(weather)||"hujan".equals(weather))) base*=0.75f;
        return base;
    }

    public static float pauseSeconds(String id,int day,int minute) {
        long seed=mix(id,day,minute/15);
        return 2.6f + Math.floorMod(seed,4500L)/1000f;
    }

    /**
     * Finds a legal short-range waypoint. If the direct route is blocked,
     * preserve the actor's current coordinates rather than teleporting.
     */
    public static Target wanderTarget(String id,int day,int minute,
                                      float homeX,float homeY,float radius,
                                      float currentX,float currentY,
                                      boolean indoor,String weather,Collision collision) {
        return wanderTarget(id,day,minute,homeX,homeY,radius,currentX,currentY,
                indoor,weather,collision,0);
    }

    /**
     * The sequence advances whenever an NPC chooses a new waypoint, even if
     * the in-game clock has not entered the next 15-minute window. This avoids
     * repeatedly choosing exactly the same destination and freezing NPC motion.
     */
    public static Target wanderTarget(String id,int day,int minute,
                                      float homeX,float homeY,float radius,
                                      float currentX,float currentY,
                                      boolean indoor,String weather,Collision collision,
                                      int sequence) {
        if(collision==null || radius<=0f) return new Target(currentX,currentY);
        float max=Math.min(120f,Math.max(4f,radius));
        if(!indoor && ("rain".equals(weather)||"hujan".equals(weather))) max*=0.48f;
        if(!indoor && (Math.floorMod(minute,1440)<360 || Math.floorMod(minute,1440)>=1200)) max*=0.68f;
        long seed=mix(id,day,minute/15L+Math.max(0,sequence)*17L);
        for(int i=0;i<8;i++) {
            long q=seed+i*104729L;
            float xx=homeX+(Math.floorMod(q,2001L)/1000f-1f)*max;
            float yy=homeY+(Math.floorMod(q>>>10,2001L)/1000f-1f)*max*0.6f;
            if(!Float.isFinite(xx)||!Float.isFinite(yy)) continue;
            if(collision.blocked(xx,yy)) continue;
            boolean lineClear=true;
            for(int step=1;step<=5;step++) {
                float fraction=step/5f;
                if(collision.blocked(currentX+(xx-currentX)*fraction,
                                     currentY+(yy-currentY)*fraction)) {
                    lineClear=false;break;
                }
            }
            if(lineClear) return new Target(xx,yy);
        }
        return new Target(currentX,currentY);
    }

    public static String idlePose(String id,int hour,String weather,boolean indoor) {
        if(id==null) return "sit";
        if(!indoor && ("rain".equals(weather)||"hujan".equals(weather))) return "sit";
        if(hour >= 19 || hour < 6) {
            return ("laras".equals(id)||"sari".equals(id))?"read":"wave";
        }
        if(hour < 10 && ("darto".equals(id)||"eko".equals(id)||"udin".equals(id)))return "sweep";
        if("laras".equals(id)||"sari".equals(id)||"darmo".equals(id)||"wulan".equals(id))return "read";
        if("melati".equals(id)||"harun".equals(id)||"tika".equals(id))return "water";
        if("raka".equals(id)||"rini".equals(id))return "give";
        if("juna".equals(id)||"dito".equals(id)||"rara".equals(id)||"bimo".equals(id))return "wave";
        if("udin".equals(id)||"bayu".equals(id)||"nara".equals(id))return "reach";
        if("darto".equals(id)||"eko".equals(id))return "sweep";
        return "sit";
    }

    private static long mix(String id,int day,long window) {
        long v=(id==null?0:id.hashCode()) * 0x9E3779B97F4A7C15L
                + day*0xBF58476D1CE4E5B9L + window*0x94D049BB133111EBL;
        v^=v>>>30;v*=0xBF58476D1CE4E5B9L;v^=v>>>27;
        v*=0x94D049BB133111EBL;v^=v>>>31;
        return v;
    }
}
