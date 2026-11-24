package com.arlandsofia.olu.logic;

/** Safe spawn and NPC placement shared by every map, independent from LibGDX. */
public final class WorldNavigationV52 {
    private WorldNavigationV52() {}
    public interface Collision { boolean blocked(float x,float y); }
    /** Keep the original point if legal; otherwise search nearest legal footprint. */
    public static float[] nearestOpen(Collision c, float x, float y, float fallbackX, float fallbackY) {
        if (c == null) return new float[]{x,y};
        if (Float.isFinite(x) && Float.isFinite(y) && !c.blocked(x,y)) return new float[]{x,y};
        float bx=Float.isFinite(x)?x:fallbackX, by=Float.isFinite(y)?y:fallbackY;
        for(int r=12;r<=168;r+=12) {
            int count=Math.max(12,(int)(r*0.75f));
            for(int i=0;i<count;i++) {
                double angle=Math.PI*2*i/count;
                float nx=bx+(float)Math.cos(angle)*r,ny=by+(float)Math.sin(angle)*r;
                if(!c.blocked(nx,ny))return new float[]{nx,ny};
            }
        }
        if (!c.blocked(fallbackX,fallbackY)) return new float[]{fallbackX,fallbackY};
        for(int r=12;r<=192;r+=12) {
            int count=Math.max(12,(int)(r*0.75f));
            for(int i=0;i<count;i++) {
                double angle=Math.PI*2*i/count;
                float nx=fallbackX+(float)Math.cos(angle)*r,ny=fallbackY+(float)Math.sin(angle)*r;
                if(!c.blocked(nx,ny))return new float[]{nx,ny};
            }
        }
        // Never silently teleport to an arbitrary other map.
        return new float[]{fallbackX,fallbackY};
    }
    /** Walk the shortened segment, not only its endpoint, to avoid clipping thin props. */
    public static boolean clearSegment(Collision c,float fx,float fy,float tx,float ty) {
        if(c==null || !Float.isFinite(tx) || !Float.isFinite(ty))return false;
        float dx=tx-fx,dy=ty-fy;
        int n=Math.max(1,(int)Math.ceil(Math.sqrt(dx*dx+dy*dy)/6.0));
        for(int i=1;i<=n;i++) if(c.blocked(fx+dx*i/n,fy+dy*i/n))return false;
        return true;
    }
}
