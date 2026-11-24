package com.arlandsofia.olu;
import com.arlandsofia.olu.logic.AdaptiveLayoutV43;
import com.arlandsofia.olu.logic.AdaptiveLayoutV44;
/** Headless collision/out-of-bounds tests for six phone/tablet landscape formats. */
public final class TabletLayoutV44Test {
    private static int checks;
    static void check(boolean ok,String message){ checks++;if(!ok) throw new AssertionError(message); }
    public static void main(String[] args){
        float[][] configs={{1280,720,0,0,0,0},{1600,900,0,30,0,15},{1280,800,0,0,0,0},
                {1280,960,0,0,0,0},{1280,960,40,35,20,20},{1344,1008,16,16,30,24}};
        for(float[] c:configs){
            AdaptiveLayoutV43.Metrics m=AdaptiveLayoutV43.of(c[0],c[1],c[2],c[3],c[4],c[5]);
            AdaptiveLayoutV44.Rect[] title=AdaptiveLayoutV44.titleButtons(m);
            check(title.length==6,"title six buttons");
            for(int i=0;i<6;i++){
                check(title[i].contained(m),"title out of safe area "+i);
                check(title[i].w>=220 && title[i].h>=60,"title hit size");
                for(int j=0;j<i;j++)check(!title[i].overlaps(title[j]),"title overlap");
            }
            for(int slotCount:new int[]{3,6}) {
                AdaptiveLayoutV44.Rect[] slots=AdaptiveLayoutV44.slots(m,slotCount);
                for(int i=0;i<slots.length;i++){
                    check(slots[i].contained(m),"slot bounds "+i);
                    check(slots[i].h>=125 && slots[i].w>=360,"slot too small");
                    for(int j=0;j<i;j++)check(!slots[i].overlaps(slots[j]),"slot overlap");
                }
            }
            check(AdaptiveLayoutV44.settingsPanel(m).contained(m),"settings bounds");
        }
        System.out.println("TABLET V4.4 LAYOUT OK: "+checks+" checks across 6 aspect/safe-inset profiles");
    }
}
