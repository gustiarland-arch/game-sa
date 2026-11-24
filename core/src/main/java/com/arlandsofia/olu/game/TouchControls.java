package com.arlandsofia.olu.game;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.logic.TouchInputModel;
import com.arlandsofia.olu.ui.Ui;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.utils.Align;

/** Renderer kontrol sentuh; semua hit-test dan multi-pointer ditangani model headless. */
public final class TouchControls {
    private final Assets a;
    private final Texture base, knob, action, round, roundOn, heart;
    private final TouchInputModel model = new TouchInputModel();
    public float vx, vy;
    public boolean sprintHeld;

    public TouchControls(Assets a) {
        this.a=a;
        base=a.uiTex("ui/joy_base.png"); knob=a.uiTex("ui/joy_knob.png");
        action=a.uiTex("ui/btn_action.png"); round=a.uiTex("ui/btn_round.png");
        roundOn=a.uiTex("ui/btn_round_on.png"); heart=a.uiTex("ui/icon_heart.png");
    }
    public void layout(float w,float h,float left,float right,float bottom,float scale,
                       boolean leftHanded,boolean floatingJoystick,float sensitivity) {
        model.layout(w,h,left,right,bottom,scale,leftHanded,floatingJoystick,sensitivity);
        sync();
    }
    private void sync(){vx=model.vx;vy=model.vy;sprintHeld=model.sprintHeld;}
    public boolean touchDown(float x,float y,int pointer){boolean b=model.touchDown(x,y,pointer);sync();return b;}
    public boolean touchDragged(float x,float y,int pointer){boolean b=model.touchDragged(x,y,pointer);sync();return b;}
    public boolean touchUp(int pointer){boolean b=model.touchUp(pointer);sync();return b;}
    public boolean consumeAction(){return model.consumeAction();}
    public void reset(){model.reset();sync();}
    public void draw(Ui ui,float opacity,String prompt){
        float r=model.radius, kr=model.knobRadius, aR=model.actionR, sR=model.sprintR;
        float aX=model.actionX, aY=model.actionY, sX=model.sprintX, sY=model.sprintY;
        ui.image(base,model.baseX-r,model.baseY-r,r*2,r*2,opacity*.9f);
        ui.image(knob,model.knobX-kr,model.knobY-kr,kr*2,kr*2,opacity);
        float pressed=model.actionHeld() ? .94f : 1f;
        ui.image(action,aX-aR*pressed,aY-aR*pressed,aR*2*pressed,aR*2*pressed,opacity);
        float hs=aR*.62f;
        ui.image(heart,aX-hs/2,aY-hs/2+8*model.scale,hs,hs,opacity);
        ui.text(a.body,"AKSI",aX-60,aY-aR*.42f,Ui.WHITE,.62f*model.scale,Align.center,120);
        ui.image(sprintHeld?roundOn:round,sX-sR,sY-sR,sR*2,sR*2,opacity);
        ui.text(a.body,"LARI",sX-60,sY+10*model.scale,Ui.INK,.72f*model.scale,Align.center,120);
        if(prompt!=null){
            float w=Math.max(200,ui.measure(a.body,prompt,.85f)+40);
            float x=Math.max(12,Math.min(aX-w/2,model.uiW-w-12));
            ui.panel(a.panelDark,x,aY+aR+12,w,52,opacity);
            ui.text(a.body,prompt,x,aY+aR+50,Ui.CREAM,.85f,Align.center,w);
        }
    }
}
