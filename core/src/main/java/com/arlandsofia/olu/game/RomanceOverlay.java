package com.arlandsofia.olu.game;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.logic.MemoryBookDb;
import com.arlandsofia.olu.logic.QuestDb;
import com.arlandsofia.olu.logic.QuestEngine;
import com.arlandsofia.olu.logic.WorldClock;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.utils.Align;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** Menu berdua: hadiah, kencan berbayar, momen, aksi, serta minigame bersama. Offline. */
public final class RomanceOverlay {
    public interface Listener { void completed(List<Map<String, Object>> actions, String status); }

    private final Assets a;
    private final QuestEngine engine;
    private final MemoryBookDb book;
    private final UiButton close, giftsTab, datesTab, momentsTab, coupleTab, gamesTab, previous, next;
    private final List<UiButton> choices = new ArrayList<>();
    private String area, status = "", tab = "gift";
    private boolean active;
    private int page;
    private float x, y, w, h;
    private Listener listener;

    public RomanceOverlay(Assets a, QuestEngine engine, MemoryBookDb book) {
        this.a = a; this.engine = engine; this.book = book;
        close = new UiButton("Selesai", new Runnable() { public void run() { close(); } });
        giftsTab = new UiButton("Berikan Hadiah", new Runnable() { public void run() { tab = "gift"; page = 0; status = ""; rebuild(); } });
        datesTab = new UiButton("Ajak Kencan", new Runnable() { public void run() { tab = "date"; page = 0; status = ""; rebuild(); } });
        momentsTab = new UiButton("Momen Harian", new Runnable() { public void run() { tab = "moment"; page = 0; status = ""; rebuild(); } });
        coupleTab = new UiButton("Aksi Berdua", new Runnable() { public void run() { tab = "couple"; page = 0; status = ""; rebuild(); } });
        gamesTab = new UiButton("Main Bareng", new Runnable() { public void run() { tab = "game"; page = 0; status = ""; rebuild(); } });
        previous = new UiButton("<", new Runnable() { public void run() { if (page > 0) { page--; rebuild(); } } });
        next = new UiButton(">", new Runnable() { public void run() { if ((page + 1) * 3 < itemCount()) { page++; rebuild(); } } });
        giftsTab.accent = true;
        for (UiButton b : new UiButton[]{giftsTab, datesTab, momentsTab, coupleTab, gamesTab}) b.textScale = 0.68f;
        close.textScale = 0.85f;
    }
    public boolean active() { return active; }
    public void open(String area, Listener callback) {
        this.area = area; this.listener = callback; active = true; tab = "gift"; page = 0;
        status = "Hadiah, kencan, momen, aksi, dan enam permainan berdua.";
        rebuild();
    }
    public void close() { active = false; listener = null; }
    private int itemCount() {
        return "gift".equals(tab) ? engine.quests.gifts.size()
                : "date".equals(tab) ? engine.quests.dates.size()
                : "moment".equals(tab) ? engine.quests.moments.size()
                : "couple".equals(tab) ? engine.quests.coupleActions.size() : engine.quests.romanceGames.size();
    }
    private void rebuild() {
        choices.clear();
        final int n = itemCount();
        for (int i = page * 3; i < Math.min(n, page * 3 + 3); i++) {
            if ("gift".equals(tab)) {
                final QuestDb.Gift g = engine.quests.gifts.get(i);
                choices.add(new UiButton("Berikan", new Runnable() {
                    public void run() {
                        String message = engine.giveGift(g.item);
                        if (message.startsWith("Hadiah diberikan!")) {
                            List<Map<String, Object>> actions = engine.giftActions(g.item);
                            Listener cb = listener; close();
                            if (cb != null) cb.completed(actions, message);
                        } else status = message;
                    }
                }));
            } else if ("date".equals(tab)) {
                final QuestDb.DateActivity d = engine.quests.dates.get(i);
                choices.add(new UiButton("Kencan", new Runnable() {
                    public void run() {
                        String message = engine.startDate(d.id, area);
                        if (message.startsWith("Kencan dimulai!")) {
                            List<Map<String, Object>> actions = engine.dateActions(d.id);
                            Listener cb = listener; close();
                            if (cb != null) cb.completed(actions, message);
                        } else status = message;
                    }
                }));
            } else if ("moment".equals(tab)) {
                final QuestDb.MomentActivity m = engine.quests.moments.get(i);
                choices.add(new UiButton("Lakukan", new Runnable() {
                    public void run() {
                        String message = engine.startMoment(m.id, area);
                        if (message.startsWith("Momen berdua!")) {
                            List<Map<String, Object>> actions = engine.momentActions(m.id);
                            Listener cb = listener; close();
                            if (cb != null) cb.completed(actions, message);
                        } else status = message;
                    }
                }));
            } else if ("game".equals(tab)) {
                final QuestDb.RomanceGame g = engine.quests.romanceGames.get(i);
                choices.add(new UiButton("Main", new Runnable() {
                    public void run() {
                        String reason = engine.romanceGameBlock(g.id, area);
                        if (reason != null) { status = reason; return; }
                        Map<String, Object> action = new java.util.LinkedHashMap<>();
                        action.put("do", "romanceGame"); action.put("id", g.id); action.put("area", area);
                        Listener cb = listener; close();
                        if (cb != null) cb.completed(java.util.Collections.singletonList(action), "Mulai " + g.title);
                    }
                }));
            } else {
                final QuestDb.CoupleAction a = engine.quests.coupleActions.get(i);
                choices.add(new UiButton("Lakukan", new Runnable() {
                    public void run() {
                        String message = engine.startCoupleAction(a.id, area);
                        if (message.startsWith("Aksi berdua!") || message.startsWith("Bergandengan lagi.")
                                || message.startsWith("Berhenti bergandengan.")) {
                            List<Map<String, Object>> actions = !message.startsWith("Berhenti bergandengan.")
                                    ? engine.coupleActionActions(a.id) : java.util.Collections.<Map<String, Object>>emptyList();
                            Listener cb = listener; close();
                            if (cb != null) cb.completed(actions, message);
                        } else status = message;
                    }
                }));
            }
        }
    }
    private void layout(float W, float H) {
        w = Math.min(940f, W - 36f); h = Math.min(628f, H - 30f);
        x = (W - w) / 2f; y = (H - h) / 2f;
        float tabW = (w - 50f - 40f) / 5f;
        giftsTab.set(x + 25, y + h - 150, tabW, 53);
        datesTab.set(x + 25 + tabW + 10f, y + h - 150, tabW, 53);
        momentsTab.set(x + 25 + 2f * (tabW + 10f), y + h - 150, tabW, 53);
        coupleTab.set(x + 25 + 3f * (tabW + 10f), y + h - 150, tabW, 53);
        gamesTab.set(x + 25 + 4f * (tabW + 10f), y + h - 150, tabW, 53);
        close.set(x + w - 166, y + h - 76, 141, 51);
        previous.set(x + 32, y + 65, 66, 48);
        next.set(x + 112, y + 65, 66, 48);
        previous.enabled = page > 0;
        next.enabled = (page + 1) * 3 < itemCount();
        giftsTab.accent = "gift".equals(tab); datesTab.accent = "date".equals(tab);
        momentsTab.accent = "moment".equals(tab); coupleTab.accent = "couple".equals(tab); gamesTab.accent = "game".equals(tab);
        float top = y + h - 220;
        for (int i = 0; i < choices.size(); i++) {
            int idx = page * 3 + i;
            UiButton b = choices.get(i);
            b.set(x + w - 205, top - i * 101f, 164, 55);
            b.textScale = 0.84f;
            if ("gift".equals(tab)) {
                QuestDb.Gift g = engine.quests.gifts.get(idx);
                b.enabled = engine.p.hasItem(g.item) && engine.p.lastGiftDay != engine.p.day && engine.romanceReady();
                b.label = !engine.p.hasItem(g.item) ? "Belum punya" : engine.p.lastGiftDay == engine.p.day ? "Besok lagi" : "Berikan";
            } else if ("date".equals(tab)) {
                QuestDb.DateActivity d = engine.quests.dates.get(idx);
                b.enabled = engine.dateBlock(d.id, area) == null;
                b.label = b.enabled ? "Kencan • " + d.cost : "Belum bisa";
            } else if ("moment".equals(tab)) {
                QuestDb.MomentActivity m = engine.quests.moments.get(idx);
                b.enabled = engine.momentBlock(m.id, area) == null;
                b.label = b.enabled ? "Lakukan" : "Belum bisa";
            } else if ("game".equals(tab)) {
                QuestDb.RomanceGame g = engine.quests.romanceGames.get(idx);
                b.enabled = engine.romanceGameBlock(g.id, area) == null;
                b.label = "Main";
            } else {
                QuestDb.CoupleAction a = engine.quests.coupleActions.get(idx);
                b.enabled = engine.coupleActionBlock(a.id, area) == null;
                b.label = b.enabled ? ("gandengan".equals(a.id) && engine.p.holdingHands ? "Lepaskan" : "Lakukan") : "Belum bisa";
            }
        }
    }
    public boolean touchDown(float px, float py, int ptr) {
        if (!active) return false;
        if (close.down(px, py, ptr) || giftsTab.down(px, py, ptr) || datesTab.down(px, py, ptr)
                || momentsTab.down(px, py, ptr) || coupleTab.down(px, py, ptr) || gamesTab.down(px, py, ptr) || previous.down(px, py, ptr) || next.down(px, py, ptr)) return true;
        for (UiButton b : choices) if (b.down(px, py, ptr)) return true;
        return true;
    }
    public boolean touchUp(float px, float py, int ptr) {
        if (!active) return false;
        if (close.up(px, py, ptr) || giftsTab.up(px, py, ptr) || datesTab.up(px, py, ptr)
                || momentsTab.up(px, py, ptr) || coupleTab.up(px, py, ptr) || gamesTab.up(px, py, ptr) || previous.up(px, py, ptr) || next.up(px, py, ptr)) return true;
        for (UiButton b : choices) if (b.up(px, py, ptr)) return true;
        return true;
    }
    public void draw(Ui ui, float W, float H) {
        if (!active) return;
        layout(W, H);
        ui.rect(0, 0, W, H, Ui.BG, 0.75f);
        ui.panel(a.panelDark, x, y, w, h, 1f);
        ui.text(a.title, "Waktu Berdua ♥", x + 26, y + h - 24, Ui.CREAM, 0.55f, Align.left, w - 200);
        ui.text(a.body, "Kedekatan: " + engine.p.affection + "/100   •   Koin: " + engine.p.coins,
                x + 27, y + h - 84, Ui.GOLD, 0.88f, Align.left, w - 70);
        ui.button(close); ui.button(giftsTab); ui.button(datesTab); ui.button(momentsTab); ui.button(coupleTab); ui.button(gamesTab);
        float top = y + h - 220;
        for (int i = 0; i < choices.size(); i++) {
            int idx = page * 3 + i;
            float yy = top - i * 101f;
            ui.panel(a.panel, x + 22, yy - 10, w - 44, 87, 1f);
            if ("gift".equals(tab)) {
                QuestDb.Gift g = engine.quests.gifts.get(idx);
                MemoryBookDb.Item item = book.item(g.item);
                if (item != null) {
                    ui.image(a.tex(item.icon), x + 37, yy + 2, 54, 54, 1f);
                    ui.text(a.body, item.name + "  •  +" + g.affection + " ♥", x + 105, yy + 55,
                            Ui.INK, 0.9f, Align.left, w - 340);
                    ui.text(a.body, item.desc, x + 105, yy + 28, Ui.INK_SOFT, 0.7f, Align.left, w - 350);
                }
            } else if ("date".equals(tab)) {
                QuestDb.DateActivity d = engine.quests.dates.get(idx);
                ui.text(a.body, d.title + "  •  " + d.cost + " koin  •  +" + d.affection + " ♥",
                        x + 42, yy + 57, Ui.INK, 0.9f, Align.left, w - 270);
                String reason = engine.dateBlock(d.id, area);
                ui.text(a.body, reason == null ? d.desc : reason,
                        x + 42, yy + 28, Ui.INK_SOFT, 0.75f, Align.left, w - 285);
            } else if ("moment".equals(tab)) {
                QuestDb.MomentActivity m = engine.quests.moments.get(idx);
                String times = WorldClock.hhmm(m.startMinute) + "-" + WorldClock.hhmm(m.endMinute);
                ui.text(a.body, m.title + "  •  gratis  •  +" + m.affection + " ♥",
                        x + 42, yy + 57, Ui.INK, 0.9f, Align.left, w - 270);
                String reason = engine.momentBlock(m.id, area);
                ui.text(a.body, reason == null ? (times + "  •  " + m.desc) : reason,
                        x + 42, yy + 28, Ui.INK_SOFT, 0.75f, Align.left, w - 285);
            } else if ("game".equals(tab)) {
                QuestDb.RomanceGame g = engine.quests.romanceGames.get(idx);
                int best = engine.p.count("best_romgame_" + g.id);
                ui.text(a.body, g.title + "  •  +" + g.affection + " hati/hari  •  Rekor " + best,
                        x + 42, yy + 57, Ui.INK, 0.85f, Align.left, w - 270);
                String reason = engine.romanceGameBlock(g.id, area);
                String detail = engine.p.count("day_romgame_" + g.id) == engine.p.day ? "Bisa main ulang; bonus kedekatan sudah diambil hari ini." : g.desc;
                ui.text(a.body, reason == null ? detail : reason,
                        x + 42, yy + 28, Ui.INK_SOFT, 0.74f, Align.left, w - 280);
            } else {
                QuestDb.CoupleAction c = engine.quests.coupleActions.get(idx);
                ui.text(a.body, c.title + "  •  +" + c.affection + " ♥ / hari",
                        x + 42, yy + 57, Ui.INK, 0.9f, Align.left, w - 270);
                String reason = engine.coupleActionBlock(c.id, area);
                ui.text(a.body, reason == null ? ("gandengan".equals(c.id) && engine.p.holdingHands ? "Mode gandengan aktif • pilih Lepaskan" : c.desc) : reason,
                        x + 42, yy + 28, Ui.INK_SOFT, 0.72f, Align.left, w - 285);
            }
            ui.button(choices.get(i));
        }
        ui.button(previous); ui.button(next);
        ui.text(a.body, "Halaman " + (page + 1) + "/" + Math.max(1, (itemCount() + 2) / 3),
                x + 195, y + 98, Ui.CREAM, 0.73f, Align.left, 250);
        ui.text(a.body, status, x + 25, y + 30, Ui.GOLD, 0.74f, Align.left, w - 48);
    }
}
