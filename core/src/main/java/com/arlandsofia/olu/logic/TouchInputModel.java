package com.arlandsofia.olu.logic;

/**
 * Hit-test kontrol landscape tanpa dependensi LibGDX (bisa diuji headless).
 * Semua koordinat dalam satuan UI dengan titik (0,0) di kiri bawah.
 * Satu jari memiliki tepat satu tombol; pointer berbeda boleh bekerja serentak.
 */
public final class TouchInputModel {
    public float uiW, uiH, scale = 1f;
    public float radius, knobRadius, restX, restY, baseX, baseY, knobX, knobY;
    public float actionX, actionY, actionR, sprintX, sprintY, sprintR;
    public float vx, vy;
    public boolean sprintHeld;
    public boolean leftHanded, floating = true;
    public float sensitivity = 1f;
    private int joyPointer = -1, sprintPointer = -1, actionPointer = -1;
    private boolean actionPressed;

    public void layout(float w, float h, float inL, float inR, float inB, float s,
                       boolean left, boolean isFloating, float sensitive) {
        uiW = Math.max(320, w);
        uiH = Math.max(180, h);
        scale = clamp(s, .70f, 1.6f);
        leftHanded = left;
        floating = isFloating;
        sensitivity = clamp(sensitive, .70f, 1.5f);
        radius = 108f * scale;
        knobRadius = 46f * scale;
        actionR = 78f * scale;
        sprintR = 54f * scale;
        float safeL = Math.max(0, inL), safeR = Math.max(0, inR), safeB = Math.max(0, inB);
        float margin = 40f * scale;
        float leftJoy = safeL + margin + radius;
        float rightJoy = uiW - safeR - margin - radius;
        restX = left ? rightJoy : leftJoy;
        restY = safeB + 42f * scale + radius;
        actionX = left ? safeL + margin + actionR : uiW - safeR - margin - actionR;
        actionY = safeB + 56f * scale + actionR;
        sprintX = actionX + (left ? 1 : -1) * (actionR + sprintR + 28f * scale);
        sprintY = safeB + 38f * scale + sprintR;
        if (joyPointer < 0) { baseX = knobX = restX; baseY = knobY = restY; }
    }

    private static float clamp(float n, float min, float max) { return Math.max(min, Math.min(max, n)); }
    private static boolean inside(float x,float y,float cx,float cy,float r){
        float dx=x-cx, dy=y-cy; return dx*dx+dy*dy<=r*r;
    }
    public boolean touchDown(float x, float y, int pointer) {
        if (pointer < 0 || pointer == joyPointer || pointer == actionPointer || pointer == sprintPointer) return false;
        if (actionPointer < 0 && inside(x,y,actionX,actionY,actionR*1.18f)) {
            actionPointer=pointer; actionPressed=true; return true;
        }
        if (sprintPointer < 0 && inside(x,y,sprintX,sprintY,sprintR*1.18f)) {
            sprintPointer=pointer; sprintHeld=true; return true;
        }
        if (joyPointer >= 0) return false;
        boolean onSide = leftHanded ? x > uiW*.52f : x < uiW*.48f;
        boolean nearRest = inside(x,y,restX,restY,radius*1.55f);
        boolean inRegion = y < uiH*.78f && onSide && x > 0 && x < uiW;
        if (floating ? inRegion : nearRest) {
            joyPointer=pointer;
            if (floating) {
                float lo=leftHanded ? uiW*.52f+radius : radius+8f;
                float hi=leftHanded ? uiW-radius-8f : uiW*.48f-radius;
                baseX=clamp(x,lo,Math.max(lo,hi));
                baseY=clamp(y,radius+8f,Math.max(radius+8f,uiH*.78f-radius));
            } else { baseX=restX; baseY=restY; }
            drag(x,y);
            return true;
        }
        return false;
    }

    public boolean touchDragged(float x,float y,int pointer) {
        if (pointer==joyPointer) { drag(x,y); return true; }
        return pointer==actionPointer || pointer==sprintPointer;
    }
    private void drag(float x,float y) {
        float dx=x-baseX, dy=y-baseY;
        float distance=(float)Math.sqrt(dx*dx+dy*dy);
        if (distance>radius) { dx=dx/distance*radius; dy=dy/distance*radius; distance=radius; }
        knobX=baseX+dx; knobY=baseY+dy;
        float normalized=distance/radius;
        if (normalized<=.18f) { vx=vy=0; return; }
        float power=clamp((normalized-.18f)/.82f*sensitivity,0f,1f);
        vx=dx/Math.max(distance,.0001f)*power;
        vy=dy/Math.max(distance,.0001f)*power;
    }
    public boolean touchUp(int pointer) {
        boolean consumed=false;
        if (pointer==joyPointer) { joyPointer=-1; vx=vy=0; baseX=knobX=restX; baseY=knobY=restY; consumed=true; }
        if (pointer==sprintPointer) { sprintPointer=-1; sprintHeld=false; consumed=true; }
        if (pointer==actionPointer) { actionPointer=-1; consumed=true; }
        return consumed;
    }
    public boolean actionHeld(){return actionPointer>=0;}
    public boolean consumeAction(){boolean ret=actionPressed;actionPressed=false;return ret;}
    public void reset(){
        joyPointer=sprintPointer=actionPointer=-1;
        vx=vy=0; sprintHeld=false; actionPressed=false;
        baseX=knobX=restX; baseY=knobY=restY;
    }
}
