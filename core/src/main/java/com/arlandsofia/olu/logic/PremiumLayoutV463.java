package com.arlandsofia.olu.logic;

/** Compact, safe-area-aware menu/dialogue geometry for phone and Android tablet. */
public final class PremiumLayoutV463 {
    private PremiumLayoutV463() {}
    public static final class Rect {
        public final float x, y, w, h;
        public Rect(float x, float y, float w, float h) {
            this.x=x; this.y=y; this.w=w; this.h=h;
        }
        public boolean inside(float screenW,float screenH,float left,float right,float bottom,float top) {
            return x>=left-0.01f && y>=bottom-0.01f && x+w<=screenW-right+0.01f
                && y+h<=screenH-top+0.01f;
        }
        public boolean overlaps(Rect other) {
            return x < other.x+other.w && other.x < x+w && y < other.y+other.h && other.y < y+h;
        }
    }
    private static float limit(float v,float lo,float hi) { return Math.max(lo,Math.min(hi,v)); }
    public static Rect dialogue(float w,float h,float left,float right,float bottom) {
        float available=Math.max(200f,w-left-right-32f);
        float pw=Math.min(1220f,available);
        float ph=limit(h*.29f,168f,224f);
        float x=left+(w-left-right-pw)*.5f;
        return new Rect(x,bottom+20,pw,ph);
    }
    public static Rect[] choices(float w,float h,float left,float right,float bottom,int count) {
        if(count<=0) return new Rect[0];
        if(count>8) throw new IllegalArgumentException("Max 8 choices per dialogue");
        float availW=Math.max(320,w-left-right-60);
        boolean two= count>=4 && availW>=850;
        int cols=two?2:1;
        int rows=(count+cols-1)/cols;
        float gap=14;
        float buttonH=limit((h-bottom-170-(rows-1)*gap)/rows,52,76);
        float buttonW=Math.min(two?510:760,(availW-(cols-1)*gap)/cols);
        float totalW=cols*buttonW+(cols-1)*gap;
        float centerX=left+(w-left-right)*.5f;
        float top=limit(h-130,h*.57f,h-90);
        // Keep last row above the safe bottom even on short phone viewports.
        float gridHeight=rows*buttonH+(rows-1)*gap;
        if(top-gridHeight<bottom+68) top=bottom+68+gridHeight;
        float startX=centerX-totalW/2;
        Rect[] out=new Rect[count];
        for(int i=0;i<count;i++) {
            int row=i/cols,col=i%cols;
            out[i]=new Rect(startX+col*(buttonW+gap),top-buttonH-row*(buttonH+gap),buttonW,buttonH);
        }
        return out;
    }
    public static Rect[] compactActions(Rect panel,float screenW,float rightInset) {
        float actionW=limit(panel.w*.18f,105,152);
        float actionH=limit(panel.h*.24f,43,52);
        float x=Math.min(panel.x+panel.w-actionW,screenW-rightInset-actionW-12);
        return new Rect[]{new Rect(x-actionW-10,panel.y+panel.h+8,actionW,actionH),
                          new Rect(x,panel.y+panel.h+8,actionW,actionH)};
    }
}
