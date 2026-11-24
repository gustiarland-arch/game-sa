import com.arlandsofia.olu.logic.TouchInputModel;
public final class TouchInputModelTest {
    static int checks;
    static void ok(boolean p,String label){checks++;if(!p)throw new AssertionError(label);}
    static void near(float a,float b,float eps,String m){ok(Math.abs(a-b)<=eps,m+" got "+a+" expected "+b);}
    static TouchInputModel init(boolean left,boolean floating,float sensitivity){
        TouchInputModel m=new TouchInputModel();m.layout(1280,720,35,48,20,1f,left,floating,sensitivity);return m;
    }
    public static void main(String[] args){
        for(float width:new float[]{1280,1480,1600,1920,2520})
        for(float scale:new float[]{.85f,1f,1.2f,1.4f})
        for(boolean left:new boolean[]{false,true})
        for(boolean floating:new boolean[]{false,true}){
            TouchInputModel m=new TouchInputModel();m.layout(width,720,32,60,25,scale,left,floating,1f);
            ok(m.restX-m.radius>=32,"stick beyond notch");
            ok(m.restX+m.radius<=width-60,"stick beyond right notch");
            ok(m.actionX-m.actionR>=32,"action beyond notch");
            ok(m.actionX+m.actionR<=width-60,"action beyond right notch");
            ok(m.sprintX-m.sprintR>=32,"sprint beyond notch");
            ok(m.sprintX+m.sprintR<=width-60,"sprint beyond right notch");
            ok(m.actionY-m.actionR>=25,"action below bottom inset");
            ok(m.restY-m.radius>=25,"stick below bottom inset");
            ok(left== (m.restX>width/2f),"left-handed joystick should flip");
        }
        TouchInputModel m=init(false,true,1f);
        ok(m.touchDown(m.restX,m.restY,0),"joystick grabs pointer");
        ok(m.touchDown(m.actionX,m.actionY,1),"simultaneous action");
        ok(m.touchDown(m.sprintX,m.sprintY,2),"simultaneous sprint");
        ok(m.sprintHeld,"sprint held");
        ok(m.consumeAction(),"action down event");
        ok(!m.consumeAction(),"action only once");
        ok(!m.touchDown(m.actionX,m.actionY,3),"action cannot be stolen");
        ok(!m.touchDown(m.sprintX,m.sprintY,1),"one pointer cannot own two controls");
        ok(m.touchDragged(m.baseX+m.radius,m.baseY,0),"stick dragging");
        near(m.vx,1f,.0001f,"full right stick");near(m.vy,0f,.0001f,"no vertical drift");
        ok(m.touchUp(1),"release action");
        ok(!m.actionHeld() && m.sprintHeld,"action release doesn't release sprint");
        ok(m.touchUp(0),"release stick");
        near(m.vx,0,0,"release stops x");near(m.vy,0,0,"release stops y");
        ok(m.touchUp(2)&&!m.sprintHeld,"release sprint");
        m=init(false,true,1f);
        ok(m.touchDown(m.restX,m.restY,11),"drag test");
        m.touchDragged(m.baseX+m.radius*.13f,m.baseY,11);
        near(m.vx,0,0,"deadzone");
        m.touchDragged(m.baseX+m.radius*.59f,m.baseY,11);
        near(m.vx,.5f,.04f,"deadzone adjusted response");
        m.touchDragged(m.baseX-m.radius*2,m.baseY,11);
        near(m.vx,-1f,.001f,"clamped negative direction");
        m.reset();ok(!m.sprintHeld&&!m.actionHeld()&&m.vx==0,"reset all");
        TouchInputModel slow=init(false,false,.8f),fast=init(false,false,1.3f);
        ok(!slow.touchDown(640,250,20),"fixed stick ignores distant taps");
        ok(slow.touchDown(slow.restX,slow.restY,20),"fixed stick accepts center");
        ok(fast.touchDown(fast.restX,fast.restY,20),"fast stick accepts center");
        slow.touchDragged(slow.baseX+slow.radius*.7f,slow.baseY,20);
        fast.touchDragged(fast.baseX+fast.radius*.7f,fast.baseY,20);
        ok(fast.vx>slow.vx,"sensitivity changes stick response");
        for(boolean left:new boolean[]{false,true}){
            TouchInputModel hand=init(left,true,1f);
            ok(hand.touchDown(hand.restX,hand.restY,5),"left/right stick pickup");
            ok(hand.touchDown(hand.actionX,hand.actionY,6),"left/right action pickup");
            hand.reset();
        }
        System.out.println("ANDROID TOUCH MODEL OK: "+checks+" assertions");
    }
}
