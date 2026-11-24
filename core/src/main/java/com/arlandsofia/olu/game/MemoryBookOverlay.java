package com.arlandsofia.olu.game;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.logic.GlobalProgress;
import com.arlandsofia.olu.logic.Achievements;
import com.arlandsofia.olu.logic.MemoryBookDb;
import com.arlandsofia.olu.logic.MapDb;
import com.arlandsofia.olu.logic.Progress;
import com.arlandsofia.olu.logic.QuestDb;
import com.arlandsofia.olu.logic.Routes;
import com.arlandsofia.olu.logic.StoryDb;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.utils.Align;

import java.util.ArrayList;
import java.util.List;

/** Memory Book: Kenangan (dua sisi), Tas (item), Bab (status + main ulang). */
public final class MemoryBookOverlay {
    public interface ReplayHandler { void replay(String chapter); }

    private static final int PER_PAGE = 6;
    private final Assets a;
    private final MemoryBookDb db;
    private final StoryDb story;
    private final QuestDb quests;
    private final MapDb maps;
    private final UiButton tabMem, tabBag, tabCh, tabSide, tabAchievements, tabExplore, close, prev, next;
    private final List<UiButton> replayButtons = new ArrayList<>();
    private final List<String> replayChapters = new ArrayList<>();
    private final Color tmp = new Color();
    private Progress p;
    private GlobalProgress g;
    private boolean replayMode, active;
    private ReplayHandler handler;
    private int tab, page;
    private float x, y, w, h;

    public MemoryBookOverlay(Assets a, MemoryBookDb db, StoryDb story, QuestDb quests, MapDb maps) {
        this.a = a; this.db = db; this.story = story; this.quests = quests; this.maps = maps;
        tabMem = new UiButton("Kenangan", new Runnable() { public void run() { tab = 0; page = 0; } });
        tabBag = new UiButton("Tas", new Runnable() { public void run() { tab = 1; page = 0; } });
        tabCh = new UiButton("Bab", new Runnable() { public void run() { tab = 2; page = 0; } });
        tabSide = new UiButton("Misi", new Runnable() { public void run() { tab = 3; page = 0; } });
        tabAchievements = new UiButton("Prestasi", new Runnable() { public void run() { tab = 4; page = 0; } });
        tabExplore = new UiButton("Jelajah", new Runnable() { public void run() { tab = 5; page = 0; } });
        close = new UiButton("Tutup", new Runnable() { public void run() { active = false; } });
        prev = new UiButton("◀", new Runnable() { public void run() { page = Math.max(0, page - 1); } });
        next = new UiButton("▶", new Runnable() { public void run() { page++; } });
    }

    public boolean active() { return active; }
    public void close() { active = false; }

    public void open(Progress p, GlobalProgress g, boolean replayMode, ReplayHandler handler) {
        this.p = p; this.g = g; this.replayMode = replayMode; this.handler = handler;
        tab = 0; page = 0; active = true;
        replayButtons.clear(); replayChapters.clear();
        for (final String ch : quests.chapterOrder) {
            if ("EPI".equals(ch)) continue;
            replayChapters.add(ch);
            UiButton b = new UiButton("Main ulang", new Runnable() { public void run() { if (MemoryBookOverlay.this.handler != null) MemoryBookOverlay.this.handler.replay(ch); } });
            b.textScale = 0.85f;
            replayButtons.add(b);
        }
    }

    private List<UiButton> all() {
        List<UiButton> l = new ArrayList<>();
        l.add(tabMem); l.add(tabBag); l.add(tabCh); l.add(tabSide); l.add(tabAchievements); l.add(tabExplore); l.add(close); l.add(prev); l.add(next);
        if (tab == 2) l.addAll(replayButtons);
        return l;
    }

    public void layout(float uiW, float uiH) {
        w = Math.min(1080, uiW - 60); h = Math.min(640, uiH - 40);
        x = (uiW - w) / 2; y = (uiH - h) / 2;
        float tw = Math.min(126, (w - 245) / 6f - 9);
        UiButton[] tabs = {tabMem, tabBag, tabCh, tabSide, tabAchievements, tabExplore};
        for (int i = 0; i < tabs.length; i++) {
            tabs[i].set(x + 20 + i * (tw + 8), y + h - 96, tw, 58);
            tabs[i].accent = tab == i;
        }
        close.set(x + w - 152, y + h - 96, 128, 58);
        prev.set(x + w - 250, y + 20, 90, 54); next.set(x + w - 130, y + 20, 90, 54);
        for (int i = 0; i < replayButtons.size(); i++) {
            int col = i / 4, row = i % 4;
            replayButtons.get(i).set(x + 30 + col * ((w - 60) / 2) + (w - 60) / 2 - 220, y + h - 176 - row * 104, 200, 56);
        }
    }

    public boolean touchDown(float px, float py, int ptr) {
        if (!active) return false;
        for (UiButton b : all()) if (b.down(px, py, ptr)) return true;
        return true;
    }

    public boolean touchUp(float px, float py, int ptr) {
        if (!active) return false;
        for (UiButton b : all()) if (b.up(px, py, ptr)) return true;
        return true;
    }

    private interface Cell { void draw(Ui ui, float cx, float cy, float cw, float chh); }

    public void draw(Ui ui, float uiW, float uiH) {
        if (!active) return;
        layout(uiW, uiH);
        ui.rect(0, 0, uiW, uiH, Ui.BG, 0.6f);
        ui.panel(a.panel, x, y, w, h, 1f);
        ui.text(a.title, "Our Memory Book", x + 32, y + h - 22, Ui.INK, 0.5f, Align.left, 0);
        int discoveredCount = 0;
        for (QuestDb.Discovery secret : quests.discoveries) if (p.hasFlag(secret.flag)) discoveredCount++;
        int panoramaCount=0;
        for (MapDb.Area each : maps.areas.values())
            if(!each.terraces.isEmpty() && p.hasFlag("V50_VIEW_"+each.id.toUpperCase(java.util.Locale.ROOT)+"_DONE")) panoramaCount++;
        String sub = tab == 5
                ? Routes.display(p.route) + " • Jelajah " + p.visitedAreas.size() + "/" + maps.areas.size()
                    + " • Jejak " + discoveredCount + "/" + quests.discoveries.size()
                    + " • Panorama " + panoramaCount + "/21"
                : Routes.display(p.route) + " Route" + (replayMode ? " • REPLAY" : "") + " • "
                    + g.achievements.size() + "/" + Achievements.ALL.length + " prestasi";
        ui.text(a.body, sub, x + w - 520, y + h - 30, Ui.INK_SOFT, 0.75f, Align.right, 480);
        ui.button(tabMem); ui.button(tabBag); ui.button(tabCh); ui.button(tabSide); ui.button(tabAchievements); ui.button(tabExplore); ui.button(close);
        final float top = y + h - 120, left = x + 30, cw = (w - 80) / 2f, chh = 120;
        List<Cell> cells = new ArrayList<>();
        if (tab == 0) {
            final boolean bonus = g.bothCompleted("C06");
            cells.add(new Cell() { public void draw(Ui u, float cx, float cy, float cwid, float ch) {
                entry(u, cx, cy, cwid, ch, bonus ? db.bonusIcon : null, bonus ? db.bonusTitle : "Bonus: Kenangan Dua Sisi",
                        bonus ? db.bonusText : "Tamatkan cerita di route Arland dan Sofia untuk membuka halaman ini.", bonus ? 2 : 0);
            } });
            for (final MemoryBookDb.Entry e : db.entriesFor(p.route)) {
                final MemoryBookDb.State st = db.state(e, p, g);
                if (!e.route.equals("shared") && !e.route.equals(p.route) && st == MemoryBookDb.State.LOCKED) {
                    cells.add(new Cell() { public void draw(Ui u, float cx, float cy, float cwid, float ch) {
                        entry(u, cx, cy, cwid, ch, null, "Sisi lain (" + Routes.display(e.route) + ")", "Mainkan route " + Routes.display(e.route) + " untuk melihat kenangan ini.", 0);
                    } });
                    continue;
                }
                cells.add(new Cell() { public void draw(Ui u, float cx, float cy, float cwid, float ch) {
                    if (st == MemoryBookDb.State.LOCKED) entry(u, cx, cy, cwid, ch, null, "◇ Belum ditemukan", "Bab " + story.chapterTitle(e.chapter), 0);
                    else entry(u, cx, cy, cwid, ch, e.icon, e.title + (st == MemoryBookDb.State.OTHER_SIDE ? "  (sisi " + Routes.display(e.route) + ")" : ""), e.text, st == MemoryBookDb.State.OTHER_SIDE ? 1 : 2);
                } });
            }
        } else if (tab == 1) {
            if (p.items.isEmpty()) cells.add(new Cell() { public void draw(Ui u, float cx, float cy, float cwid, float ch) { entry(u, cx, cy, cwid, ch, null, "Tas masih kosong", "Item yang kamu temukan akan muncul di sini.", 0); } });
            for (String id : p.items) {
                final MemoryBookDb.Item it = db.item(id);
                if (it == null) continue;
                cells.add(new Cell() { public void draw(Ui u, float cx, float cy, float cwid, float ch) { entry(u, cx, cy, cwid, ch, it.icon, it.name, it.desc, 2); } });
            }
        }
        if (tab == 3) {
            for (final QuestDb.SideQuest q : quests.sideQuests) {
                if (!q.forRoute(p.route)) continue;
                final boolean done = p.hasFlag(q.doneFlag), started = p.hasFlag(q.startFlag);
                final boolean available = quests.chapterIndex(chapterNow()) >= quests.chapterIndex(q.chapter);
                cells.add(new Cell() { public void draw(Ui u, float cx, float cy, float cwid, float ch) {
                    if (done) entry(u, cx, cy, cwid, ch, null, "✓ " + q.title, q.desc, 2);
                    else if (started) entry(u, cx, cy, cwid, ch, null, "♪ " + q.title + " (aktif)", q.desc, 1);
                    else entry(u, cx, cy, cwid, ch, null, available ? "◇ Misi tersedia di kota" : "◇ Belum tersedia", available ? "Ajak bicara penduduk kota atau lihat papan pengumuman." : "Lanjutkan cerita untuk membuka.", 0);
                } });
            }
        }
        if (tab == 2) {
            drawChapters(ui, left, top);
            prev.visible = false; next.visible = false;
            return;
        }
        if (tab == 4) {
            for (final Achievements.Def d : Achievements.ALL) {
                final boolean achieved = g.achievements.contains(d.id);
                cells.add(new Cell() { public void draw(Ui u, float cx, float cy, float width, float height) {
                    entry(u, cx, cy, width, height, null,
                            (achieved ? "✓ " : "◇ ") + d.name,
                            achieved ? "Terbuka • " + d.hint : d.hint,
                            achieved ? 2 : 0);
                } });
            }
        }
        if (tab == 5) {
            for (final MapDb.Area place : maps.areas.values()) {
                final boolean discovered = p.visitedAreas.contains(place.id) || p.area.equals(place.id);
                QuestDb.Discovery found = null;
                for (QuestDb.Discovery d : quests.discoveries)
                    if (d.area.equals(place.id)) { found = d; break; }
                final QuestDb.Discovery secret = found;
                final boolean secretFound = secret != null && p.hasFlag(secret.flag);
                final boolean hasView=!place.terraces.isEmpty();
                final boolean viewDone=hasView && p.hasFlag("V50_VIEW_"+place.id.toUpperCase(java.util.Locale.ROOT)+"_DONE");
                cells.add(new Cell() { public void draw(Ui u, float cx, float cy, float width, float height) {
                    String status = secret == null ? "Belum ada jejak tambahan."
                            : secretFound ? "Jejak terungkap: " + secret.title
                            : "Jejak belum ditemukan — cari penanda bintang di area ini.";
                    String vertical = hasView ? (viewDone ? " • Panorama terbuka" : " • Cari tangga ke pelataran") : "";
                    entry(u, cx, cy, width, height, null,
                            discovered ? "✓ " + place.name : "◇ Belum ditemukan",
                            discovered ? status+vertical : "Jelajahi kota dan ikuti cerita untuk menemukannya.",
                            (secretFound||viewDone) ? 2 : (discovered ? 1 : 0));
                } });
            }
        }
        int pages = Math.max(1, (cells.size() + PER_PAGE - 1) / PER_PAGE);
        if (page >= pages) page = pages - 1;
        for (int i = page * PER_PAGE; i < Math.min(cells.size(), (page + 1) * PER_PAGE); i++) {
            int k = i - page * PER_PAGE;
            float cx = left + (k % 2) * (cw + 20), cy = top - (k / 2 + 1) * (chh + 14);
            cells.get(i).draw(ui, cx, cy, cw, chh);
        }
        prev.visible = pages > 1; next.visible = pages > 1;
        prev.enabled = page > 0; next.enabled = page < pages - 1;
        ui.button(prev); ui.button(next);
        if (pages > 1) ui.text(a.body, "Hal. " + (page + 1) + "/" + pages, x + 30, y + 58, Ui.INK_SOFT, 0.8f, Align.left, 0);
    }

    /** state 0 = terkunci, 1 = sisi lain, 2 = terbuka. */
    private void entry(Ui ui, float cx, float cy, float cw, float ch, String icon, String title, String text, int state) {
        tmp.set(state == 0 ? 0.92f : 1f, state == 0 ? 0.9f : (state == 1 ? 0.94f : 0.97f), state == 0 ? 0.93f : 1f, 1f);
        ui.rect(cx, cy, cw, ch, tmp, 1f);
        ui.rect(cx, cy, 6, ch, state == 2 ? Ui.PINK : (state == 1 ? Ui.LAVENDER : Ui.INK_SOFT), 1f);
        float tx = cx + 20;
        if (icon != null) { ui.image(a.tex(icon), cx + 18, cy + (ch - 64) / 2, 64, 64, 1f); tx = cx + 96; }
        ui.text(a.body, title, tx, cy + ch - 16, state == 0 ? Ui.INK_SOFT : Ui.INK, 0.88f, Align.left, cx + cw - tx - 12);
        ui.wrap(a.body, text, tx, cy + ch - 50, cx + cw - tx - 14, Ui.INK_SOFT, 0.72f, Align.left);
    }

    private String chapterNow() { QuestDb.Step cur = quests.step(p.step); return cur == null ? "PRO" : cur.chapter; }

    private void drawChapters(Ui ui, float left, float top) {
        float colW = (w - 60) / 2;
        for (int i = 0; i < replayChapters.size(); i++) {
            String ch = replayChapters.get(i);
            int col = i / 4, row = i % 4;
            float cx = left + col * colW, cy = top - 90 - row * 104;
            boolean done = p.chapters.contains(ch);
            boolean playing = chapterNow().equals(ch) && !done;
            tmp.set(1f, 0.97f, 1f, 1f);
            ui.rect(cx, cy - 10, colW - 12, 94, tmp, 1f);
            ui.text(a.body, story.chapterTitle(ch), cx + 16, cy + 68, Ui.INK, 0.78f, Align.left, colW - 250);
            ui.text(a.body, done ? "✓ Tamat" : (playing ? "Sedang dimainkan" : "Belum dibuka"), cx + 16, cy + 30, done ? Ui.PINK_DEEP : Ui.INK_SOFT, 0.75f, Align.left, 0);
            UiButton b = replayButtons.get(i);
            b.visible = done && !replayMode && p.snapshots.containsKey(ch);
            ui.button(b);
        }
        ui.wrap(a.body, "Main ulang memakai salinan progres di awal chapter: progres utama dan save-mu tidak berubah.",
                left, y + 70, w - 80, Ui.INK_SOFT, 0.72f, Align.left);
    }
}
