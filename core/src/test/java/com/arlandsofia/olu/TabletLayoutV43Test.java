package com.arlandsofia.olu;
import com.arlandsofia.olu.logic.AdaptiveLayoutV43;
import com.arlandsofia.olu.logic.TouchInputModel;
/** Deterministic regression for 16:9 phones, 16:10 / 4:3 Android tablets. */
public final class TabletLayoutV43Test {
    private static int checks;
    private static void ok(boolean yes, String why) { checks++; if (!yes) throw new AssertionError(why); }
    private static void test(float width, float height, float inL, float inR, float inT, float inB) {
        AdaptiveLayoutV43.Metrics m = AdaptiveLayoutV43.of(width,height,inL,inR,inT,inB);
        float cy = AdaptiveLayoutV43.cardBottom(m,470f);
        ok(cy >= m.contentBottom, "card off bottom");
        ok(cy + 470f <= m.contentTop - 65f, "card off top");
        float top = AdaptiveLayoutV43.stackedMenuTop(m,7,56f,11f);
        ok(top <= m.contentTop - 70f, "pause heading clipped");
        ok(top - (7*56f+6*11f) >= m.contentBottom, "pause last row clipped");
        float scale = AdaptiveLayoutV43.controlScale(m,1.2f);
        TouchInputModel pad = new TouchInputModel();
        for (boolean left : new boolean[]{false,true}) {
            for (boolean floating : new boolean[]{false,true}) {
                pad.layout(width,height,inL,inR,inB,scale,left,floating,1.2f);
                ok(pad.baseX-pad.radius >= m.insetL, "joystick clipped on left");
                ok(pad.baseX+pad.radius <= width-m.insetR, "joystick clipped on right");
                ok(pad.actionX-pad.actionR >= m.insetL, "action clipped on left");
                ok(pad.actionX+pad.actionR <= width-m.insetR, "action clipped on right");
                ok(pad.restY-pad.radius >= m.insetB, "joystick clipped at bottom");
                ok(pad.actionY-pad.actionR >= m.insetB, "action clipped at bottom");
                ok(Math.abs(pad.actionX-pad.restX) > pad.actionR + pad.radius,"controls overlap");
                // Multiple touch pointers retain independent ownership.
                ok(pad.touchDown(pad.actionX,pad.actionY,0),"action touch missed");
                ok(pad.touchDown(pad.restX,pad.restY,1),"joystick touch missed");
                ok(pad.consumeAction(),"action lost on second pointer");
                ok(pad.touchUp(0),"action release lost");
                ok(pad.touchUp(1),"joystick release lost");
            }
        }
    }
    public static void main(String[] args) {
        test(1280,720,0,0,0,0);              // 16:9 phone
        test(1280,800,0,0,0,0);              // 16:10 tablet
        test(1280,960,0,0,0,0);              // 4:3 tablet
        test(1280,800,30,30,24,22);         // tablet with safe insets
        test(1280,960,38,30,32,28);         // 4:3 + notch / rounded corners
        test(1600,720,40,40,10,10);         // ultrawide mobile
        System.out.println("TABLET LAYOUT OK — " + checks + " assertions across six device profiles");
    }
}
