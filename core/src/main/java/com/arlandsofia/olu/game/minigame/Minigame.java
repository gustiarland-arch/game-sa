package com.arlandsofia.olu.game.minigame;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.AudioManager;
import com.arlandsofia.olu.ui.Ui;

import java.util.Map;

/** Dasar minigame. Koordinat UI (y ke atas) di dalam area kerja (x, y, w, h) yang disediakan overlay. */
public abstract class Minigame {
    protected Assets a;
    protected AudioManager audio;
    protected Map<String, Object> cfg;
    protected String route;
    protected float x, y, w, h, t;
    /** true bila selesai; score >= 0. */
    protected boolean finished;
    protected int score;
    protected String resultText = "";

    public void init(Assets a, AudioManager audio, Map<String, Object> cfg, String route) {
        this.a = a; this.audio = audio; this.cfg = cfg; this.route = route;
        start();
    }

    public void area(float x, float y, float w, float h) { this.x = x; this.y = y; this.w = w; this.h = h; }

    protected abstract void start();
    public void update(float dt) { t += dt; }
    public abstract void draw(Ui ui);
    /** Ketukan utama (layar/tombol aksi/spasi). */
    public void tap(float px, float py) {}
    public void key(int index) {}
    public boolean finished() { return finished; }
    public int score() { return score; }
    public String resultText() { return resultText; }

    protected static boolean in(float px, float py, float bx, float by, float bw, float bh) {
        return px >= bx && px <= bx + bw && py >= by && py <= by + bh;
    }
}
