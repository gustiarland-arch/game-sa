package com.arlandsofia.olu.game;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.logic.Settings;
import com.arlandsofia.olu.logic.PremiumLayoutV463;
import com.arlandsofia.olu.logic.StoryDb;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.math.MathUtils;
import com.badlogic.gdx.utils.Align;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;

/** Kotak dialog dengan potret ekspresi, teks bertahap (opsional), lewati, dan pilihan. */
public final class DialogBox {
    public interface Listener {
        void onLine(StoryDb.Line line);
        void onChoice(StoryDb.Choice choice);
    }

    private static final Color NPC_TAG = new Color(0.36f, 0.58f, 0.5f, 1f);
    private final Assets a;
    private final StoryDb story;
    private final Settings settings;
    private final ArrayDeque<StoryDb.Line> queue = new ArrayDeque<>();
    private final List<UiButton> choiceButtons = new ArrayList<>();
    private final UiButton skip;
    private final UiButton historyButton;
    private Runnable historyAction;
    private final Texture ribbon, bloom;
    private List<StoryDb.Choice> choices = new ArrayList<>();
    private String route;
    private Listener listener;
    private Runnable done;
    private StoryDb.Line line;
    private float shown, blink, appear;
    private boolean active;
    private int touchPointer = -1;
    private int focusedChoice = 0;
    private float x, y, w, h;

    public DialogBox(Assets a, StoryDb story, Settings settings) {
        this.a = a; this.story = story; this.settings = settings;
        ribbon = a.uiTex("ui/v32_cinematic_ribbon.png");
        bloom = a.uiTex("ui/v32_bloom.png");
        skip = new UiButton("Lewati ▶", new Runnable() { public void run() { skipAll(); } });
        skip.textScale = 0.72f;
        historyButton = new UiButton("Riwayat", new Runnable() {
            public void run() { if (historyAction != null) historyAction.run(); }
        });
        historyButton.textScale = 0.72f;
    }

    public void setHistoryAction(Runnable action) { historyAction = action; }
    public boolean active() { return active; }

    public void start(List<StoryDb.Line> lines, List<StoryDb.Choice> choices, String route, Listener listener, Runnable done) {
        queue.clear(); queue.addAll(lines);
        this.choices = choices == null ? new ArrayList<StoryDb.Choice>() : new ArrayList<>(choices);
        this.route = route; this.listener = listener; this.done = done;
        choiceButtons.clear();
        touchPointer = -1; focusedChoice = 0;
        active = true;
        next();
    }

    private void next() {
        line = queue.poll();
        shown = 0; appear = 0f;
        if (line != null) {
            if (listener != null) listener.onLine(line);
            return;
        }
        if (!choices.isEmpty()) { buildChoices(); return; }
        finish();
    }

    private void finish() {
        active = false; line = null; choiceButtons.clear(); touchPointer = -1;
        Runnable d = done; done = null;
        if (d != null) d.run();
    }

    private void buildChoices() {
        choiceButtons.clear(); focusedChoice=0;
        int i=0;
        for (final StoryDb.Choice c : choices) {
            UiButton b = new UiButton((++i) + ".  " + c.text, new Runnable() { public void run() { pick(c); } });
            b.accent = false;
            choiceButtons.add(b);
        }
        if(!choiceButtons.isEmpty()) choiceButtons.get(0).focused=true;
    }

    private void pick(StoryDb.Choice c) {
        choices = new ArrayList<>();
        choiceButtons.clear(); touchPointer=-1;
        if (listener != null) listener.onChoice(c);
        queue.addAll(c.response(route));
        next();
    }

    private void skipAll() {
        queue.clear();
        line = null;
        if (!choices.isEmpty()) buildChoices(); else finish();
    }

    public void update(float dt) {
        if (!active || line == null) return;
        shown += dt * settings.charsPerSecond();
        blink += dt;
        appear = Math.min(1f, appear + Math.max(0f, dt) * 6f);
    }

    private boolean revealed() { return line == null || shown >= line.text.length(); }

    /** Ketuk/aksi: tampilkan penuh lalu lanjut. */
    public void advance() {
        if (!active || line == null) return;
        if (!revealed()) { shown = line.text.length(); return; }
        next();
    }

    public void layout(float uiW, float uiH, float inL, float inR, float inB) {
        PremiumLayoutV463.Rect box=PremiumLayoutV463.dialogue(uiW,uiH,inL,inR,inB);
        x=box.x;y=box.y;w=box.w;h=box.h;
        PremiumLayoutV463.Rect[] actions=PremiumLayoutV463.compactActions(box,uiW,inR);
        historyButton.set(actions[0].x,actions[0].y,actions[0].w,actions[0].h);
        skip.set(actions[1].x,actions[1].y,actions[1].w,actions[1].h);
        PremiumLayoutV463.Rect[] cells=PremiumLayoutV463.choices(uiW,uiH,inL,inR,inB,choiceButtons.size());
        for(int i=0;i<cells.length;i++) {
            PremiumLayoutV463.Rect cell=cells[i];
            choiceButtons.get(i).set(cell.x,cell.y,cell.w,cell.h);
        }
    }

    public boolean touchDown(float px, float py, int ptr) {
        if (!active) return false;
        if (touchPointer != -1) return true;
        touchPointer=ptr;
        if (!choiceButtons.isEmpty()) {
            for (UiButton b : choiceButtons) if (b.down(px, py, ptr)) return true;
            return true;
        }
        if (historyButton.down(px, py, ptr)) return true;
        if (skip.down(px, py, ptr)) return true;
        return true;
    }

    public boolean touchUp(float px, float py, int ptr) {
        if (!active) return false;
        if (touchPointer != ptr) return true;
        touchPointer=-1;
        if (!choiceButtons.isEmpty()) {
            for (UiButton b : new ArrayList<>(choiceButtons)) if (b.up(px, py, ptr)) return true;
            return true;
        }
        if (historyButton.up(px, py, ptr)) return true;
        if (skip.up(px, py, ptr)) return true;
        advance();
        return true;
    }

    /** Navigasi keyboard untuk pilihan (angka 1/2/3). */
    public void choose(int index) {
        if (index >= 0 && index < choiceButtons.size()) choiceButtons.get(index).onClick.run();
    }
    /** D-pad / keyboard focus; no story choice is committed until confirm. */
    public void focusChoice(int direction) {
        if (choiceButtons.isEmpty()) return;
        focusedChoice=Math.floorMod(focusedChoice+direction,choiceButtons.size());
        for(int i=0;i<choiceButtons.size();i++)choiceButtons.get(i).focused=i==focusedChoice;
    }
    public void confirmFocusedChoice() { if (choosing()) choose(focusedChoice); }
    public void cancelTouch(int pointer) {
        if(touchPointer!=pointer) return;
        touchPointer=-1;
        skip.cancel(); historyButton.cancel();
        for(UiButton b:choiceButtons) if(b.pointer==pointer)b.cancel();
    }

    public boolean choosing() { return active && !choiceButtons.isEmpty(); }

    public void draw(Ui ui, float uiW, float uiH, float inL, float inR, float inB) {
        if (!active) return;
        layout(uiW, uiH, inL, inR, inB);
        if (!choiceButtons.isEmpty()) {
            ui.rect(0, 0, uiW, uiH, Ui.BG, 0.53f);
            float headY=choiceButtons.get(0).y+choiceButtons.get(0).h+28;
            float headW=Math.min(690f,uiW-inL-inR-80f);
            ui.image(ribbon,(uiW-headW)/2,headY-45,headW,82,.96f);
            ui.textCenter(a.title,"Pilihanmu menentukan momen berikutnya",uiW/2,headY+1,Ui.CREAM,.49f);
            for (UiButton b : choiceButtons) ui.button(b);
            return;
        }
        if (line == null) return;
        StoryDb.Speaker sp = story.speaker(line.speaker);
        boolean narrator = sp.portrait == null && !sp.npc;
        float slide = (1f - appear) * 20f;
        float py = y - slide;
        ui.rect(0, 0, uiW, Math.max(0, py + h + 32), Ui.BG, 0.16f);
        ui.panel(a.panel, x, py, w, h, 0.98f);
        ui.rect(x + 17, py + 10, w - 34, 3, Ui.GOLD, 0.34f);
        if (settings.visualQuality > 0) {
            ui.image(bloom, x + w - 220, py + h - 172, 180, 180, 0.24f);
            ui.rect(x + 18, py + h - 8, w - 36, 3, Ui.PINK, 0.65f);
        }
        float tx = x + 30;
        if (sp.portrait != null) {
            if (settings.visualQuality > 0 && "jatuh_cinta".equals(line.emotion))
                ui.image(bloom, x + 24, py - 5, 210, 210, 0.16f + .06f * MathUtils.sin(blink * 2.1f));
            Texture pt = a.portrait(sp.portrait, story.emotion(line.emotion).portraits);
            float ph = h - 34, pw = ph * pt.getWidth() / pt.getHeight();
            float maxPw=Math.max(94,Math.min(190,w*.23f));
            if(pw>maxPw) { ph*=maxPw/pw; pw=maxPw; }
            ui.panel(a.panelDark, x + 14, py + 10, pw + 12, h - 20, 1f);
            float bob = settings.visualQuality == 2 ? MathUtils.sin(blink * 1.7f) * 1.5f : 0f;
            ui.image(pt, x + 20, py + 14 + bob, pw, ph, Math.min(1f, appear * 2f));
            tx = x + 20 + pw + 28;
        }
        Color tag = narrator ? Ui.INK_SOFT : sp.npc ? NPC_TAG : (line.speaker.startsWith("sofia") ? Ui.PINK_DEEP : Ui.LAVENDER);
        float nameW = Math.min(Math.max(140, ui.measure(a.body, sp.name, 0.85f) + 40),Math.max(145,w-(tx-x)-26));
        ui.rect(tx - 8, py + h - 13, nameW, 38, tag, 1f);
        ui.text(a.body, sp.name, tx - 8, py + h + 15, Ui.WHITE, 0.9f, Align.center, nameW);
        int n = Math.min(line.text.length(), Math.max(0, (int) shown));
        String txt = line.text.substring(0, n);
        if (sp.message) txt = "✉ " + txt;
        float textWidth=Math.max(130f,x+w-tx-34f);
        ui.wrap(a.body,txt,tx,py+h-51,textWidth,narrator?Ui.INK_SOFT:Ui.INK,
                textWidth<520f?.84f:1f,Align.left);
        // Reading progress below the text. No extra input and no effect on story flags.
        float progress = line.text.isEmpty() ? 1f : Math.min(1f, shown / line.text.length());
        ui.rect(tx, py + 20, Math.max(1, x + w - tx - 65), 4, Ui.LAVENDER, 0.22f);
        ui.rect(tx, py + 20, Math.max(0, x + w - tx - 65) * progress, 4, Ui.PINK_DEEP, 0.85f);
        if (revealed() && ((int) (blink * 2.5f)) % 2 == 0)
            ui.text(a.body,"▼",x+w-52,py+49,Ui.PINK_DEEP,.9f,Align.left,0);
        ui.button(historyButton);
        ui.button(skip);
    }
}
