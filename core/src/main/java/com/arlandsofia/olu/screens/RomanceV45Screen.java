package com.arlandsofia.olu.screens;

import com.arlandsofia.olu.OluGame;
import com.arlandsofia.olu.logic.romance.RomanceEngineV45;
import com.arlandsofia.olu.logic.romance.RomanceSaveV45;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.Screen;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.utils.Align;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Real gameplay UI using the existing Indonesian-friendly font, NinePatch and
 * 1280x720 adaptive UI. Does not replace original quest/story/canon logic.
 */
public final class RomanceV45Screen extends BaseScreen {
    private final Screen previous;
    private final int slot;
    private final RomanceEngineV45 engine;
    private final Texture background;
    private final UiButton back;
    private final ArrayList<UiButton> options=new ArrayList<>();
    private String tab="home",message="Pilih aktivitas bersama.",selectedId="";
    private int page=0;
    private boolean leaving=false, allowExitWithoutSave=false;

    public RomanceV45Screen(final OluGame game,String route,int slot,int worldDay,Screen previous){
        super(game);
        if(previous==null)throw new IllegalArgumentException("Previous screen is required");
        this.previous=previous;this.slot=slot;
        engine=RomanceSaveV45.load(route,slot,worldDay);
        if (engine.day() > worldDay) {
            message="Save cerita utama lebih lama daripada progres romance. Hari romance dijaga agar tidak mundur.";
        }
        background=game.assets.uiTex("ui/v32_menu_far.png");
        back=new UiButton("Kembali",new Runnable(){public void run(){goBack();}});
        buildHome();
    }
    private UiButton add(String label,Runnable action){
        UiButton b=new UiButton(label,action);b.textScale=0.76f;
        options.add(b);return b;
    }
    private void open(String name){tab=name;page=0;message="Pilih kegiatan yang ingin dimainkan.";rebuild();}
    private void action(RomanceEngineV45.Result result){
        message=result.text;
        if(result.ok)allowExitWithoutSave=false;
        if(result.ok&&!RomanceSaveV45.save(engine,slot))
            message="Progres belum tersimpan. Save lama tidak boleh ditimpa.";
        rebuild();
    }
    private void buildHome(){
        tab="home";options.clear();
        add("Kencan Dinamis",()->open("date"));
        add("Percakapan Berdua",()->open("dialog"));
        add("Hadiah Khusus",()->open("gift"));
        add("Janji Kita",()->open("promise"));
        add("Momen Istimewa",()->open("moment"));
        add("Buku Kenangan",()->open("journal"));
        add("Kembali Bermain",this::goBack);
        rebuildButtons();
    }
    private void rebuild(){
        if("home".equals(tab)){buildHome();return;}
        options.clear();
        switch(tab){
            case "date":
                if(!engine.activeDateId().isEmpty()) {
                    add("Lanjutkan Kencan",()->open("date-choice"));
                } else for(final RomanceEngineV45.Scene s:engine.availableDates())
                    add(s.title,()->{action(engine.startDate(s.id));if(!engine.activeDateId().isEmpty())open("date-choice");});
                break;
            case "date-choice":
                for(final RomanceEngineV45.Choice c:engine.dateChoices())
                    add(c.label,()->{action(engine.chooseDate(c.id));tab="home";buildHome();});
                break;
            case "dialog":
                for(final RomanceEngineV45.Choice c:engine.dialogueChoices())
                    add(c.label,()->{action(engine.chooseDialogue(c.id));buildHome();});
                break;
            case "gift":
                for(final RomanceEngineV45.Gift g:engine.gifts())
                    add(g.name+" ("+g.tokenCost+" token)",()->action(engine.giveGift(g.id)));
                break;
            case "promise":
                for(final Map.Entry<String,String> item:engine.promiseCatalog().entrySet()){
                    RomanceEngineV45.PromiseRecord existing=null;
                    for(RomanceEngineV45.PromiseRecord p:engine.promises())if(item.getKey().equals(p.id))existing=p;
                    final boolean created=existing!=null;
                    final String id=item.getKey();
                    String label=item.getValue()+(created?" ["+existing.status+"]":" [Buat janji]");
                    add(label,()->action(created?engine.fulfillPromise(id):engine.makePromise(id)));
                }
                break;
            case "moment":
                for(final RomanceEngineV45.Moment m:engine.availableMoments())
                    add(m.title,()->{selectedId=m.id;open("moment-choice");message=m.description;});
                break;
            case "moment-choice":
                for(final RomanceEngineV45.Choice c:engine.momentChoices(selectedId))
                    add(c.label,()->{action(engine.resolveMoment(selectedId,c.id));buildHome();});
                break;
            case "journal":
                List<String> log=engine.journalEntries();
                for(int i=log.size()-1;i>=0;i--){
                    final String line=log.get(i);
                    add(line.length()>65?line.substring(0,62)+"...":line,()->message=line);
                }
                break;
            default:break;
        }
        if(options.isEmpty())message="Belum ada aktivitas yang tersedia. Coba lanjutkan cerita utama.";
        rebuildButtons();
    }
    private void rebuildButtons(){
        buttons.clear();
        buttons.addAll(options);
        if(!"home".equals(tab))buttons.add(back);
        layout();
    }
    @Override protected void layout(){
        float w=uiW(),h=uiH();
        float safeL=insetL()+30,safeR=insetR()+30,safeB=insetB()+26;
        float available=w-safeL-safeR;
        float bw=Math.min(available,920);
        float x=(w-bw)/2f;
        float bh=Math.max(52,Math.min(66,(h-insetT()-safeB-240)/5f));
        float gap=12;
        int offset=page*5;
        for(int i=0;i<options.size();i++){
            UiButton b=options.get(i);
            b.visible=(i>=offset&&i<offset+5);
            int row=i-offset;
            if(b.visible)b.set(x, h-insetT()-216-(row+1)*bh-row*gap,bw,bh);
        }
        back.set(safeL,safeB,175,60);
    }
    @Override protected void drawUi(){
        float w=uiW(),h=uiH();
        ui.imageCover(background,0,0,w,h,1f);
        ui.rect(0,0,w,h,Ui.BG,0.71f);
        ui.panel(game.assets.panel,Math.max(12,insetL()+12),Math.max(12,insetB()+12),
                w-insetL()-insetR()-24,h-insetT()-insetB()-24,0.96f);
        ui.text(game.assets.title,"ROMANCE SIMULATION 3.0",w/2-550,h-insetT()-42,
                Ui.PINK_DEEP,0.62f,Align.center,1100);
        String state="Route "+("arland".equals(engine.route())?"Arland":"Sofia")+
                " - Slot "+slot+" - Hari "+engine.day()+" - Percaya "+engine.trust()+
                " - Sayang "+engine.affection()+" - Token "+engine.tokens();
        ui.text(game.assets.body,state,45+insetL(),h-insetT()-104,Ui.INK,0.74f,Align.center,w-90-insetL()-insetR());
        ui.wrap(game.assets.body,message,48+insetL(),h-insetT()-147,
                w-96-insetL()-insetR(),Ui.INK_SOFT,0.78f,Align.center);
        for(UiButton b:options)ui.button(b);
        if(!"home".equals(tab))ui.button(back);
        if(options.size()>5){
            ui.textCenter(game.assets.body,"Halaman "+(page+1)+" / "+((options.size()+4)/5)
                    +" - geser kiri atau kanan / tombol panah",w/2,Math.max(38,insetB()+58),Ui.INK_SOFT,0.66f);
        }
        ui.textCenter(game.assets.body,"Cerita utama dan satu canon ending tetap sama.",w/2,
                Math.max(18,insetB()+15),Ui.INK_SOFT,0.62f);
    }
    private void pageBy(int delta){
        int max=Math.max(0,(options.size()-1)/5);
        page=Math.max(0,Math.min(max,page+delta));layout();
    }
    // Only the pointer that began the gesture may flip pages. Secondary
    // touches must never move the journal or accidentally activate a button.
    private int swipePointer=-1, touchX;
    @Override public boolean touchDown(int sx,int sy,int pointer,int button){
        if (swipePointer == -1) { swipePointer=pointer; touchX=sx; }
        return super.touchDown(sx,sy,pointer,button);
    }
    @Override public boolean touchUp(int sx,int sy,int pointer,int button){
        if (pointer != swipePointer) return super.touchUp(sx,sy,pointer,button);
        swipePointer=-1;
        int delta=sx-touchX;
        if(Math.abs(delta)>100 && options.size()>5){
            for(UiButton b:buttons)b.cancel();
            pageBy(delta<0?1:-1);return true;
        }
        return super.touchUp(sx,sy,pointer,button);
    }
    @Override public boolean touchCancelled(int sx,int sy,int pointer,int button){
        if (pointer==swipePointer) swipePointer=-1;
        return super.touchCancelled(sx,sy,pointer,button);
    }
    @Override public boolean keyDown(int keycode){
        if(keycode==com.badlogic.gdx.Input.Keys.LEFT){pageBy(-1);return true;}
        if(keycode==com.badlogic.gdx.Input.Keys.RIGHT){pageBy(1);return true;}
        return super.keyDown(keycode);
    }
    @Override protected void onBack(){
        if("home".equals(tab))goBack();else{tab="home";page=0;buildHome();}
    }
    private void goBack(){
        if(leaving)return;
        if(!RomanceSaveV45.save(engine,slot) && !allowExitWithoutSave){
            message="Gagal menyimpan romance. Tekan Kembali lagi untuk keluar tanpa menyimpan perubahan.";
            allowExitWithoutSave=true;
            return;
        }
        leaving=true;
        game.setScreen(previous); // previous GameScreen stays alive (do not dispose it).
        dispose();
    }
    @Override public void pause(){
        super.pause();RomanceSaveV45.save(engine,slot);
    }
}
