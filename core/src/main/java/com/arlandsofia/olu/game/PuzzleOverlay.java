package com.arlandsofia.olu.game;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.AudioManager;
import com.arlandsofia.olu.logic.ActionRunner;
import com.arlandsofia.olu.logic.PuzzleLogic;
import com.arlandsofia.olu.logic.QuestDb;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.math.MathUtils;
import com.badlogic.gdx.utils.Align;

import java.util.ArrayList;
import java.util.List;

/** Puzzle urutan tiga simbol (Kafe Senja). Tidak ada kondisi gagal permanen; petunjuk muncul setelah beberapa kali salah. */
public final class PuzzleOverlay {
    private final Assets a;
    private final AudioManager audio;
    private final List<UiButton> symbolButtons = new ArrayList<>();
    private final UiButton cancel;
    private QuestDb.Puzzle puzzle;
    private PuzzleLogic logic;
    private ActionRunner.BoolCallback callback;
    private boolean active, hasHint;
    private float shake, solvedTimer = -1;
    private String message = "";
    private float x, y, w, h;

    public PuzzleOverlay(Assets a, AudioManager audio) {
        this.a = a; this.audio = audio;
        cancel = new UiButton("Nanti saja", new Runnable() { public void run() { close(false); } });
    }

    public static String icon(String symbol) {
        if ("BUNGA".equals(symbol)) return "items/symbol_flower.png";
        if ("BUKU".equals(symbol)) return "items/symbol_book.png";
        return "items/symbol_star.png";
    }

    public boolean active() { return active; }

    public void open(QuestDb.Puzzle pz, String route, boolean hasHintFlag, ActionRunner.BoolCallback cb) {
        puzzle = pz; callback = cb; hasHint = hasHintFlag;
        logic = new PuzzleLogic(pz.order(route), pz.hintAfterFails);
        symbolButtons.clear();
        for (final String s : pz.symbols) {
            UiButton b = new UiButton(s, new Runnable() { public void run() { press(s); } });
            b.icon = a.tex(icon(s));
            symbolButtons.add(b);
        }
        message = "Ingat petunjuk mural yang kamu lihat di plaza.";
        solvedTimer = -1; shake = 0;
        active = true;
    }

    private void press(String s) {
        if (solvedTimer >= 0) return;
        PuzzleLogic.Result r = logic.input(s);
        if (r == PuzzleLogic.Result.WRONG) {
            audio.sfx("soft_wrong"); shake = 0.4f;
            message = "Urutannya belum tepat. Coba lagi dari awal, pelan-pelan saja.";
        } else if (r == PuzzleLogic.Result.SOLVED) {
            audio.sfx("sparkle"); solvedTimer = 0.9f; message = "Simbol-simbolnya menyala!";
        } else {
            audio.sfx("page"); message = "Simbol ke-" + logic.entered.size() + " menyala...";
        }
    }

    private void close(boolean ok) {
        active = false;
        ActionRunner.BoolCallback cb = callback; callback = null;
        if (cb != null) cb.done(ok);
    }

    public void update(float dt) {
        if (!active) return;
        if (shake > 0) shake -= dt;
        if (solvedTimer >= 0) { solvedTimer -= dt; if (solvedTimer < 0) close(true); }
    }

    public void layout(float uiW, float uiH) {
        w = Math.min(860, uiW - 60); h = Math.min(560, uiH - 60);
        x = (uiW - w) / 2; y = (uiH - h) / 2;
        float bw = (w - 120) / 3f;
        for (int i = 0; i < symbolButtons.size(); i++) symbolButtons.get(i).set(x + 30 + i * (bw + 30), y + 100, bw, 84);
        cancel.set(x + (w - 240) / 2, y + 24, 240, 64);
    }

    public boolean touchDown(float px, float py, int ptr) {
        if (!active) return false;
        for (UiButton b : symbolButtons) if (b.down(px, py, ptr)) return true;
        cancel.down(px, py, ptr);
        return true;
    }

    public boolean touchUp(float px, float py, int ptr) {
        if (!active) return false;
        for (UiButton b : symbolButtons) if (b.up(px, py, ptr)) return true;
        cancel.up(px, py, ptr);
        return true;
    }

    public void key(int index) { if (active && index >= 0 && index < symbolButtons.size()) symbolButtons.get(index).onClick.run(); }
    public void cancelKey() { if (active) close(false); }

    public void draw(Ui ui, float uiW, float uiH) {
        if (!active) return;
        layout(uiW, uiH);
        ui.rect(0, 0, uiW, uiH, Ui.BG, 0.6f);
        float sx = shake > 0 ? MathUtils.sin(shake * 60f) * 8f : 0f;
        ui.panel(a.panel, x + sx, y, w, h, 1f);
        ui.text(a.title, puzzle.title, x + 36 + sx, y + h - 34, Ui.INK, 0.6f, Align.left, 0);
        ui.text(a.body, "Susun tiga simbol di meja sesuai urutan petunjukmu.", x + 36 + sx, y + h - 100, Ui.INK_SOFT, 0.85f, Align.left, w - 72);
        float slot = 96, gap = 34, total = slot * 3 + gap * 2, sx0 = x + (w - total) / 2 + sx, sy = y + h - 250;
        for (int i = 0; i < logic.order.size(); i++) {
            float bx = sx0 + i * (slot + gap);
            ui.panel(a.panelDark, bx, sy, slot, slot, 1f);
            if (i < logic.entered.size()) {
                Texture t = a.tex(icon(logic.entered.get(i)));
                ui.image(t, bx + 12, sy + 12, slot - 24, slot - 24, 1f);
            } else ui.text(a.body, String.valueOf(i + 1), bx, sy + slot / 2 + 12, Ui.CREAM, 1.1f, Align.center, slot);
        }
        ui.text(a.body, message, x + 30, y + 336, Ui.INK, 0.85f, Align.center, w - 60);
        if (logic.hintVisible() && hasHint) {
            StringBuilder b = new StringBuilder("Petunjuk mural: ");
            for (int i = 0; i < logic.order.size(); i++) { if (i > 0) b.append(" → "); b.append(logic.order.get(i)); }
            ui.text(a.body, b.toString(), x + 30, y + 302, Ui.PINK_DEEP, 0.85f, Align.center, w - 60);
        }
        for (UiButton b : symbolButtons) ui.button(b);
        ui.button(cancel);
    }
}
