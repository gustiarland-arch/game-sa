package com.arlandsofia.olu.game;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.logic.DialogueHistory;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.utils.Align;

/** Penampil riwayat dialog yang tidak mengubah quest, flag, atau urutan cerita. */
public final class DialogueHistoryOverlay {
    private static final int PAGE_SIZE = 4;
    private final Assets assets;
    private DialogueHistory history;
    private boolean open;
    private int page;
    private final UiButton older, newer, close;

    public DialogueHistoryOverlay(Assets assets) {
        this.assets = assets;
        older = new UiButton("Lebih lama", new Runnable() { public void run() { page++; clamp(); } });
        newer = new UiButton("Lebih baru", new Runnable() { public void run() { page--; clamp(); } });
        close = new UiButton("Tutup", new Runnable() { public void run() { close(); } });
    }
    private int pages() { return Math.max(1, (history == null ? 0 : history.size() + PAGE_SIZE - 1) / PAGE_SIZE); }
    private void clamp() { page = Math.max(0, Math.min(page, pages() - 1)); }
    public void open(DialogueHistory lines) { history = lines; open = true; page = 0; clamp(); }
    public void close() { open = false; older.cancel(); newer.cancel(); close.cancel(); }
    public boolean active() { return open; }
    public void pageOlder() { page++; clamp(); }
    public void pageNewer() { page--; clamp(); }
    public void layout(float w, float h) {
        float bottom = h * .10f, col = (w - 660) / 2;
        older.set(col + 22, bottom + 10, 182, 52);
        newer.set(col + 217, bottom + 10, 182, 52);
        close.set(col + 451, bottom + 10, 182, 52);
        older.enabled = page < pages() - 1;
        newer.enabled = page > 0;
    }
    public boolean down(float x, float y, int ptr) {
        if (!open) return false;
        return older.down(x, y, ptr) || newer.down(x, y, ptr) || close.down(x, y, ptr) || true;
    }
    public boolean up(float x, float y, int ptr) {
        if (!open) return false;
        if (older.up(x, y, ptr) || newer.up(x, y, ptr) || close.up(x, y, ptr)) return true;
        return true;
    }
    public void cancel(int pointer) {
        if (older.pointer == pointer) older.cancel();
        if (newer.pointer == pointer) newer.cancel();
        if (close.pointer == pointer) close.cancel();
    }
    public void draw(Ui ui, float w, float h) {
        if (!open) return;
        layout(w, h);
        ui.rect(0, 0, w, h, Ui.BG, .84f);
        float pw = Math.min(w - 80, 920), ph = Math.min(h - 45, 650), px = (w - pw) / 2, py = (h - ph) / 2;
        ui.panel(assets.panel, px, py, pw, ph, 1f);
        ui.text(assets.title, "Riwayat Dialog", px + 15, py + ph - 23, Ui.INK, .59f, Align.center, pw - 30);
        ui.text(assets.body, "Disimpan offline per slot • maksimal 72 baris", px + 18, py + ph - 64, Ui.INK_SOFT, .65f, Align.center, pw - 36);
        int end = history == null ? 0 : history.size() - page * PAGE_SIZE;
        for (int i = 0; i < PAGE_SIZE && end - i > 0; i++) {
            DialogueHistory.Entry e = history.get(end - i - 1);
            float top = py + ph - 99 - i * 117;
            ui.panel(assets.panelDark, px + 42, top - 100, pw - 84, 108, .96f);
            ui.text(assets.body, e.speaker + "  •  Hari " + e.day, px + 59, top - 10, Ui.PINK, .76f, Align.left, pw - 115);
            String content = e.text;
            if (content.length() > 215) content = content.substring(0, 212) + "...";
            ui.wrap(assets.body, content, px + 59, top - 39, pw - 120, Ui.CREAM, .69f, Align.left);
        }
        if (history == null || history.size() == 0)
            ui.text(assets.body, "Belum ada dialog pada slot ini.", px + 45, py + ph / 2, Ui.INK_SOFT, .85f, Align.center, pw - 90);
        ui.text(assets.body, "Halaman " + (page + 1) + "/" + pages(), px + 40, py + 91, Ui.INK_SOFT, .74f, Align.center, pw - 80);
        ui.button(older); ui.button(newer); ui.button(close);
    }
}
