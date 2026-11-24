package com.arlandsofia.olu.ui;

import com.badlogic.gdx.graphics.Texture;

/** Tombol UI sederhana (koordinat UI virtual 1280x720, y ke atas). */
public final class UiButton {
    public float x, y, w, h;
    public String label;
    public Texture icon;
    public boolean enabled = true, visible = true, pressed, accent, focused;
    public float textScale = 1f;
    public int pointer = -1;
    public Runnable onClick;

    public UiButton(String label, Runnable onClick) { this.label = label; this.onClick = onClick; }

    public UiButton set(float x, float y, float w, float h) { this.x = x; this.y = y; this.w = w; this.h = h; return this; }

    public boolean contains(float px, float py) {
        return visible && px >= x && px <= x + w && py >= y && py <= y + h;
    }

    public boolean down(float px, float py, int ptr) {
        // A second finger must not steal an in-flight press from another pointer.
        if (!enabled || pointer != -1 || !contains(px, py)) return false;
        pressed = true; pointer = ptr;
        return true;
    }

    /** true bila klik selesai di atas tombol (dan onClick dipanggil). */
    public boolean up(float px, float py, int ptr) {
        if (pointer != ptr) return false;
        boolean hit = pressed && contains(px, py);
        pressed = false; pointer = -1;
        if (hit && enabled && onClick != null) { onClick.run(); return true; }
        return false;
    }

    public void cancel() { pressed = false; pointer = -1; }
}
