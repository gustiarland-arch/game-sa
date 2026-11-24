package com.arlandsofia.olu.ui;

import com.arlandsofia.olu.OluGame;
import com.arlandsofia.olu.logic.Settings;
import com.arlandsofia.olu.logic.AdaptiveLayoutV43;
import com.arlandsofia.olu.logic.AdaptiveLayoutV44;
import com.badlogic.gdx.utils.Align;
import java.util.ArrayList;
import java.util.List;

/** Pengaturan bertab v2.8: tombol cukup besar untuk touch landscape dan notch. */
public final class SettingsPanel {
    private final OluGame game;
    private final Runnable onClose;
    public final List<UiButton> buttons = new ArrayList<>();
    private static final String[] LABELS = {
            "Kecepatan teks", "Volume musik", "Volume ambience", "Volume efek",
            "Soundtrack beragam", "Suara langkah", "Ukuran kontrol", "Transparansi kontrol",
            "Penanda misi", "Kualitas visual", "Kamera halus",
            "Tangan dominan", "Posisi joystick", "Sensitivitas joystick", "Jarak kamera"
    };
    private static final int[][] PAGES = {
            {1,2,3,4,5}, {0,8,9,10,14}, {6,7,11,12,13}
    };
    private static final String[] TITLES = {"Audio", "Tampilan", "Kontrol"};
    private final UiButton[] minus = new UiButton[LABELS.length], plus = new UiButton[LABELS.length];
    private final UiButton[] tabs = new UiButton[3];
    private final UiButton done;
    private int activePage;
    private float x,y,w,h;
    private float safeL,safeR,safeT,safeB;

    /** Safe insets are UI-world units, provided by the owning screen. */
    public void safeInsets(float left,float right,float top,float bottom) {
        safeL=left;safeR=right;safeT=top;safeB=bottom;
    }

    public SettingsPanel(OluGame g,Runnable onClose){
        game=g; this.onClose=onClose;
        for(int i=0;i<LABELS.length;i++){
            final int row=i;
            minus[i]=new UiButton("‹",()->change(row,-1));
            plus[i]=new UiButton("›",()->change(row,1));
            minus[i].textScale=1.45f; plus[i].textScale=1.45f;
            buttons.add(minus[i]); buttons.add(plus[i]);
        }
        for(int i=0;i<tabs.length;i++){
            final int target=i;
            tabs[i]=new UiButton(TITLES[i],()->activePage=target);
            buttons.add(tabs[i]);
        }
        done=new UiButton("Simpan & tutup",()->{
            game.saveSettings();
            if(this.onClose!=null)this.onClose.run();
        });
        done.accent=true;
        buttons.add(done);
    }

    private void change(int k,int d){
        Settings s=game.settings;
        switch(k){
            case 0: s.textSpeed=Math.max(0,Math.min(3,s.textSpeed+d));break;
            case 1: s.music=Math.min(1f,vol(s.music+d*.1f));break;
            case 2: s.ambience=Math.min(1f,vol(s.ambience+d*.1f));break;
            case 3: s.sfx=Math.min(1f,vol(s.sfx+d*.1f));game.audio.sfx("sparkle",.35f);break;
            case 4: s.variedMusic=!s.variedMusic;break;
            case 5: s.footsteps=!s.footsteps;break;
            case 6: {
                float[] steps={.85f,1f,1.2f,1.4f};
                int idx=1;for(int i=0;i<steps.length;i++)if(Math.abs(steps[i]-s.controlScale)<.05f)idx=i;
                s.controlScale=steps[Math.max(0,Math.min(steps.length-1,idx+d))];break;
            }
            case 7: s.controlOpacity=Math.min(1f,vol(Math.max(.3f,s.controlOpacity+d*.1f)));break;
            case 8: s.showHints=!s.showHints;break;
            case 9: s.visualQuality=Math.max(0,Math.min(2,s.visualQuality+d));break;
            case 10: s.smoothCamera=!s.smoothCamera;break;
            case 11: s.leftHanded=!s.leftHanded;break;
            case 12: s.floatingJoystick=!s.floatingJoystick;break;
            case 13: s.joystickSensitivity=Math.max(.7f,Math.min(1.5f,vol(s.joystickSensitivity+d*.1f)));break;
            case 14: s.cameraDistance=Math.max(0,Math.min(2,s.cameraDistance+d));break;
            default:break;
        }
    }
    private static float vol(float v){return Math.round(Math.max(0f,Math.min(1.5f,v))*10f)/10f;}
    private String value(int k){
        Settings s=game.settings;
        switch(k){
            case 0:return Settings.textSpeedName(s.textSpeed);
            case 1:return Math.round(s.music*100)+"%";
            case 2:return Math.round(s.ambience*100)+"%";
            case 3:return Math.round(s.sfx*100)+"%";
            case 4:return s.variedMusic?"Dinamis":"Klasik";
            case 5:return s.footsteps?"Aktif":"Nonaktif";
            case 6:return s.controlScale<.9f?"Kecil":s.controlScale<1.1f?"Sedang":s.controlScale<1.3f?"Besar":"Ekstra besar";
            case 7:return Math.round(s.controlOpacity*100)+"%";
            case 8:return s.showHints?"Tampil":"Sembunyi";
            case 9:return Settings.visualQualityName(s.visualQuality);
            case 10:return s.smoothCamera?"Aktif":"Nonaktif";
            case 11:return s.leftHanded?"Kiri":"Kanan";
            case 12:return s.floatingJoystick?"Melayang":"Tetap";
            case 13:return Math.round(s.joystickSensitivity*100)+"%";
            case 14:return com.arlandsofia.olu.logic.CameraFramingV52.presetName(s.cameraDistance);
            default:return "";
        }
    }
    public void layout(float screenW,float screenH){
        AdaptiveLayoutV43.Metrics m=AdaptiveLayoutV43.of(screenW,screenH,safeL,safeR,safeT,safeB);
        AdaptiveLayoutV44.Rect panel=AdaptiveLayoutV44.settingsPanel(m);
        w=panel.w;h=panel.h;x=panel.x;y=panel.y;
        float tabW=(w-68f)/3f;
        for(int i=0;i<tabs.length;i++){
            tabs[i].accent=i==activePage;
            tabs[i].set(x+28+i*tabW,y+h-165,tabW-7,58);
        }
        for(int i=0;i<LABELS.length;i++){
            minus[i].visible=false;plus[i].visible=false;
        }
        int[] rows=PAGES[activePage];
        float rowH=Math.min(72f,(h-268f)/rows.length);
        for(int pos=0;pos<rows.length;pos++){
            int row=rows[pos];
            float ry=y+h-185-(pos+1)*rowH;
            minus[row].set(x+w-322,ry+4,62,rowH-9);
            plus[row].set(x+w-87,ry+4,62,rowH-9);
            minus[row].visible=true;plus[row].visible=true;
        }
        done.set(x+(w-282f)/2,y+14,282,60);
    }
    public void draw(Ui ui,float screenW,float screenH){
        layout(screenW,screenH);
        ui.rect(0,0,screenW,screenH,Ui.BG,.62f);
        ui.panel(ui.a.panel,x,y,w,h,1f);
        ui.text(ui.a.title,"Pengaturan",x+36,y+h-30,Ui.INK,.64f,Align.left,0);
        ui.text(ui.a.body,"Pilih kategori. Semua pengaturan tersimpan secara lokal.",
                x+38,y+h-76,Ui.INK_SOFT,.73f,Align.left,w-76);
        int[] rows=PAGES[activePage];
        float rowH=Math.min(72f,(h-268f)/rows.length);
        for(int pos=0;pos<rows.length;pos++){
            int row=rows[pos];float ry=y+h-185-(pos+1)*rowH;
            ui.text(ui.a.body,LABELS[row],x+40,ry+rowH/2+10,Ui.INK,.86f,Align.left,0);
            ui.text(ui.a.body,value(row),x+w-252,ry+rowH/2+10,Ui.INK,.88f,Align.center,154);
        }
        for(UiButton b:buttons)if(b.visible)ui.button(b);
    }
}
