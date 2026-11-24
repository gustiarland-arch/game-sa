import com.arlandsofia.olu.logic.CinematicMotionV463;
import com.arlandsofia.olu.logic.PremiumLayoutV463;

public final class V463CinematicUiLogicTest {
    static int count;
    static void check(boolean result,String msg) { count++; if(!result)throw new AssertionError(msg); }
    public static void main(String[] args) {
        for(float t=0;t<=1.01f;t+=.01f) {
            float k=CinematicMotionV463.ease(t);
            check(k>=0f && k<=1f,"ease bound");
            check(Math.abs(CinematicMotionV463.ease(1f-t)-(1f-k))<.0001,"symmetric easing");
        }
        check(CinematicMotionV463.safeZoom(-2)==.67f,"zoom min");
        check(CinematicMotionV463.safeZoom(99)==1.5f,"zoom max");
        check(CinematicMotionV463.progress(1,0)==1f,"instant cut");
        check(CinematicMotionV463.damp(5,1f/30)>CinematicMotionV463.damp(5,1f/60),"dt damping");
        check(CinematicMotionV463.presetZoom("intimate")>1f,"intimate composition");
        for(float[] display:new float[][]{{1280,720,0,0,0},{1280,960,0,0,0},
              {1460,720,38,20,16},{1280,820,48,48,30},{1680,900,0,0,0}}) {
            float w=display[0],h=display[1],l=display[2],r=display[3],b=display[4];
            PremiumLayoutV463.Rect box=PremiumLayoutV463.dialogue(w,h,l,r,b);
            check(box.inside(w,h,l,r,b,0),"dialogue in safe area");
            for(int n=1;n<=8;n++) {
                PremiumLayoutV463.Rect[] items=PremiumLayoutV463.choices(w,h,l,r,b,n);
                check(items.length==n,"choice count");
                for(int i=0;i<items.length;i++) {
                    check(items[i].inside(w,h,l,r,b,64),"choices in safe area n="+n);
                    for(int j=i+1;j<items.length;j++)check(!items[i].overlaps(items[j]),"choices do not overlap");
                }
            }
            PremiumLayoutV463.Rect[] actions=PremiumLayoutV463.compactActions(box,w,r);
            check(!actions[0].overlaps(actions[1]),"controls no overlap");
        }
        System.out.println("V4.6.3 cinematic/UI layout checks PASS: "+count);
    }
}
