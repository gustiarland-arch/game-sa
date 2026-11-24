package com.arlandsofia.olu.logic;

/** Responsive, pure-Java geometry shared by phone & tablet menu screens.
 * Every rectangle is in the same 1280-base ExtendViewport coordinates as the UI.
 * Insets are already converted to UI world units by BaseScreen.
 */
public final class AdaptiveLayoutV44 {
    private AdaptiveLayoutV44() {}
    public static final class Rect {
        public final float x, y, w, h;
        public Rect(float x,float y,float w,float h){this.x=x;this.y=y;this.w=w;this.h=h;}
        public boolean contained(AdaptiveLayoutV43.Metrics m) {
            return x>=m.contentLeft-1 && y>=m.contentBottom-1
                && x+w<=m.contentRight+1 && y+h<=m.contentTop+1;
        }
        public boolean overlaps(Rect other){return x<other.x+other.w && other.x<x+w && y<other.y+other.h && other.y<y+h;}
    }
    /** 3 × 2 grid on widescreen phones; 2 × 3 on 4:3 and 16:10 tablets. */
    public static Rect[] titleButtons(AdaptiveLayoutV43.Metrics m) {
        boolean tablet=m.tabletRatio;
        int cols=tablet?2:3, rows=tablet?3:2;
        float gap=tablet?18:20;
        float h=tablet?76:74;
        float usable=m.contentRight-m.contentLeft;
        float w=Math.min(tablet?370:300,(usable-(cols-1)*gap-12)/cols);
        float gridW=cols*w+(cols-1)*gap;
        float left=m.centerX-gridW/2;
        float bottom=Math.max(m.contentBottom+40, m.contentBottom+32);
        Rect[] out=new Rect[6];
        for(int i=0;i<out.length;i++) {
            int row=i/cols, col=i%cols;
            out[i]=new Rect(left+col*(w+gap),bottom+(rows-1-row)*(h+gap),w,h);
        }
        return out;
    }
    /** Save-slot cards: 3×2 on phones to avoid 3 cramped rows, 2×3 on tablets. */
    public static Rect[] slots(AdaptiveLayoutV43.Metrics m,int count) {
        int cols=(!m.tabletRatio && count>=5)?3:2;
        int rows=(count+cols-1)/cols;
        float gap=20;
        float maxW=cols==3?410:560;
        float w=Math.min(maxW,(m.contentRight-m.contentLeft-16-(cols-1)*gap)/cols);
        float availableTop=m.contentTop-88;
        float bottom=m.contentBottom+88;
        float h=Math.min(260,(availableTop-bottom-(rows-1)*gap)/rows);
        float left=m.centerX-(cols*w+(cols-1)*gap)/2;
        Rect[] out=new Rect[count];
        for(int i=0;i<count;i++) {
            int row=i/cols,col=i%cols;
            out[i]=new Rect(left+col*(w+gap),availableTop-(row+1)*h-row*gap,w,h);
        }
        return out;
    }
    public static Rect settingsPanel(AdaptiveLayoutV43.Metrics m) {
        float w=Math.min(960, m.contentRight-m.contentLeft-28);
        float h=Math.min(732, m.contentTop-m.contentBottom-24);
        return new Rect(m.centerX-w/2,m.centerY-h/2,w,h);
    }
}
