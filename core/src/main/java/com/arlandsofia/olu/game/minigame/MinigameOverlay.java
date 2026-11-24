package com.arlandsofia.olu.game.minigame;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.AudioManager;
import com.arlandsofia.olu.logic.ActionRunner;
import com.arlandsofia.olu.logic.Json;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.utils.Align;

import java.util.Map;

/** Bingkai minigame: judul, petunjuk, tombol keluar, layar hasil. Hasil dikirim ke ActionRunner (-1 = batal). */
public final class MinigameOverlay {
    private final Assets a;
    private final AudioManager audio;
    private Minigame game;
    private ActionRunner.IntCallback cb;
    private String title = "", desc = "";
    private boolean active, showResult;
    private final UiButton quit, done;
    private float px, py, pw, ph;

    public MinigameOverlay(Assets a, AudioManager audio) {
        this.a = a; this.audio = audio;
        quit = new UiButton("Keluar", new Runnable() { public void run() { finish(-1); } });
        quit.textScale = 0.85f;
        done = new UiButton("Lanjut", new Runnable() { public void run() { finish(game.score()); } });
        done.accent = true;
    }

    public boolean active() { return active; }

    public void open(String id, Map<String, Object> cfg, String route, ActionRunner.IntCallback cb) {
        this.cb = cb; game = Games.create(Json.str(cfg, "type", id)); game.init(a, audio, cfg, route);
        title = Json.str(cfg, "title", "Minigame"); desc = Json.str(cfg, "desc", "");
        active = true; showResult = false;
    }

    private void finish(int score) {
        active = false;
        ActionRunner.IntCallback c = cb; cb = null;
        if (c != null) c.done(score);
    }

    public void update(float dt) {
        if (!active) return;
        game.update(dt);
        if (game.finished() && !showResult) showResult = true;
    }

    private void layout(float W, float H) {
        pw = Math.min(980, W - 40); ph = Math.min(640, H - 40); px = (W - pw) / 2; py = (H - ph) / 2;
        game.area(px + 24, py + 24, pw - 48, ph - 150);
        quit.set(px + pw - 160, py + ph - 76, 140, 56);
        done.set(px + (pw - 260) / 2, py + 30, 260, 66);
    }

    public boolean touchDown(float x, float y, int p) {
        if (!active) return false;
        if (showResult) { done.down(x, y, p); return true; }
        if (quit.down(x, y, p)) return true;
        game.tap(x, y);
        return true;
    }

    public boolean touchUp(float x, float y, int p) {
        if (!active) return false;
        if (showResult) { done.up(x, y, p); return true; }
        quit.up(x, y, p);
        return true;
    }

    public void key(int index) { if (active && !showResult) game.key(index); else if (active && showResult && index == 99) finish(game.score()); }
    public void cancel() { if (active && !showResult) finish(-1); }

    public void draw(Ui ui, float W, float H) {
        if (!active) return;
        layout(W, H);
        ui.rect(0, 0, W, H, Ui.BG, 0.7f);
        ui.panel(a.panelDark, px, py, pw, ph, 1f);
        ui.text(a.title, title, px + 28, py + ph - 24, Ui.CREAM, 0.55f, Align.left, 0);
        ui.text(a.body, desc, px + 28, py + ph - 84, Ui.LAVENDER, 0.75f, Align.left, pw - 220);
        if (showResult) {
            ui.text(a.title, "★ " + game.resultText(), px, py + ph / 2 + 40, Ui.GOLD, 0.45f, Align.center, pw);
            ui.button(done);
        } else {
            game.draw(ui);
            ui.button(quit);
        }
    }
}
