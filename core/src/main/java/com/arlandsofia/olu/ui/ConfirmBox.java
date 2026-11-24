package com.arlandsofia.olu.ui;

import com.badlogic.gdx.utils.Align;

/** Kotak konfirmasi modal (Ya/Tidak atau satu tombol OK). */
public final class ConfirmBox {
    public final String title, message;
    public final UiButton yes, no;
    private float w, h, x, y;

    public ConfirmBox(String title, String message, String yesLabel, Runnable onYes, String noLabel, Runnable onNo) {
        this.title = title; this.message = message;
        yes = new UiButton(yesLabel, onYes); yes.accent = true;
        no = noLabel == null ? null : new UiButton(noLabel, onNo);
    }

    public void layout(float uiW, float uiH) {
        w = Math.min(760, uiW - 80); h = 330;
        x = (uiW - w) / 2; y = (uiH - h) / 2;
        if (no != null) {
            no.set(x + 40, y + 30, (w - 120) / 2, 72);
            yes.set(x + w / 2 + 20, y + 30, (w - 120) / 2, 72);
        } else yes.set(x + (w - 280) / 2, y + 30, 280, 72);
    }

    public void draw(Ui ui, float uiW, float uiH) {
        layout(uiW, uiH);
        ui.rect(0, 0, uiW, uiH, Ui.BG, 0.6f);
        ui.panel(ui.a.panel, x, y, w, h, 1f);
        ui.text(ui.a.title, title, x + 36, y + h - 34, Ui.INK, 0.62f, Align.left, 0);
        ui.wrap(ui.a.body, message, x + 36, y + h - 100, w - 72, Ui.INK, 0.95f, Align.left);
        ui.button(yes);
        if (no != null) ui.button(no);
    }

    public boolean down(float px, float py, int ptr) { return yes.down(px, py, ptr) || (no != null && no.down(px, py, ptr)); }
    public boolean up(float px, float py, int ptr) { return yes.up(px, py, ptr) || (no != null && no.up(px, py, ptr)); }
}
