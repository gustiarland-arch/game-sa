package com.arlandsofia.olu.game;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.AudioManager;
import com.arlandsofia.olu.logic.MemoryBookDb;
import com.arlandsofia.olu.logic.QuestDb;
import com.arlandsofia.olu.logic.QuestEngine;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.utils.Align;
import java.util.ArrayList;
import java.util.List;

/** Layar katalog toko: tampil dan klik asli di dalam LibGDX, tidak memerlukan jaringan. */
public final class ShopOverlay {
    private final Assets a;
    private final AudioManager audio;
    private final QuestEngine engine;
    private final MemoryBookDb book;
    private final UiButton close;
    private final List<UiButton> buy = new ArrayList<>();
    private QuestDb.Shop shop;
    private Runnable onClose, onBuy;
    private boolean active;
    private String status = "";
    private float x, y, w, h;

    public ShopOverlay(Assets assets, QuestEngine engine, MemoryBookDb book, AudioManager audio) {
        this.a = assets; this.engine = engine; this.book = book; this.audio = audio;
        close = new UiButton("Selesai", new Runnable() { public void run() { close(); } });
        close.accent = true;
    }
    public boolean active() { return active; }
    public void open(String shopId, Runnable done, Runnable afterPurchase) {
        shop = engine.quests.shops.get(shopId); onClose = done; onBuy = afterPurchase;
        if (shop == null) { if (done != null) done.run(); return; }
        active = true; status = "Pilih barang yang ingin dibeli."; buy.clear();
        for (final QuestDb.Good good : shop.goods) {
            UiButton b = new UiButton("Beli • " + good.price, new Runnable() {
                public void run() {
                    status = engine.purchase(shop.id, good.item);
                    if (status.startsWith("Membeli ")) {
                        audio.sfx("coin", .65f);
                        if (onBuy != null) onBuy.run();
                    } else audio.sfx("soft_wrong", .30f);
                }
            });
            b.textScale = 0.82f;
            buy.add(b);
        }
    }
    public void close() {
        if (!active) return;
        active = false;
        Runnable cb = onClose; onClose = null;
        if (cb != null) cb.run(); // ActionRunner menyimpan transaksi saat kembali idle
    }
    private void layout(float W, float H) {
        w = Math.min(960f, W - 40); h = Math.min(620f, H - 30);
        x = (W - w) / 2; y = (H - h) / 2;
        close.set(x + w - 170, y + h - 78, 145, 54);
        float gap = Math.min(104f, (h - 190f) / Math.max(1, buy.size()));
        for (int i = 0; i < buy.size(); i++) {
            buy.get(i).set(x + w - 215, y + h - 171 - i * gap, 176, 56);
            QuestDb.Good good = shop.goods.get(i);
            buy.get(i).enabled = !engine.p.hasItem(good.item) && engine.p.coins >= good.price;
            buy.get(i).label = engine.p.hasItem(good.item) ? "Dimiliki" : engine.p.coins < good.price ? "Kurang koin" : "Beli • " + good.price;
        }
    }
    public boolean touchDown(float px, float py, int ptr) {
        if (!active) return false;
        if (close.down(px, py, ptr)) return true;
        for (UiButton b : buy) if (b.down(px, py, ptr)) return true;
        return true;
    }
    public boolean touchUp(float px, float py, int ptr) {
        if (!active) return false;
        if (close.up(px, py, ptr)) return true;
        for (UiButton b : buy) if (b.up(px, py, ptr)) return true;
        return true;
    }
    public void draw(Ui ui, float W, float H) {
        if (!active) return;
        layout(W, H);
        ui.rect(0, 0, W, H, Ui.BG, 0.73f);
        ui.panel(a.panelDark, x, y, w, h, 1f);
        ui.text(a.title, shop.title, x + 27, y + h - 22, Ui.CREAM, 0.54f, Align.left, w - 220);
        ui.text(a.body, "Penjual: " + shop.keeper + "    •    Saldo: " + engine.p.coins + " koin",
                x + 30, y + h - 90, Ui.GOLD, 0.88f, Align.left, w - 65);
        close.enabled = true; ui.button(close);
        float gap = Math.min(104f, (h - 190f) / Math.max(1, buy.size()));
        for (int i = 0; i < buy.size(); i++) {
            QuestDb.Good g = shop.goods.get(i);
            float yy = y + h - 171 - i * gap;
            ui.panel(a.panel, x + 24, yy - 10, w - 48, 84, 1f);
            MemoryBookDb.Item it = book.item(g.item);
            if (it != null) ui.image(a.tex(it.icon), x + 37, yy + 2, 52, 52, 1f);
            ui.text(a.body, g.name + " — " + g.price + " koin", x + 102, yy + 58, Ui.INK, 0.96f, Align.left, w - 340);
            ui.text(a.body, g.desc, x + 102, yy + 27, Ui.INK_SOFT, 0.73f, Align.left, w - 350);
            ui.button(buy.get(i));
        }
        ui.text(a.body, status, x + 28, y + 25, Ui.GOLD, 0.79f, Align.left, w - 50);
    }
}
