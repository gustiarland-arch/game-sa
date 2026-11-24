package com.arlandsofia.olu.screens;

import com.arlandsofia.olu.OluGame;
import com.arlandsofia.olu.logic.AdaptiveLayoutV44;
import com.arlandsofia.olu.logic.Progress;
import com.arlandsofia.olu.logic.QuestDb;
import com.arlandsofia.olu.logic.Routes;
import com.arlandsofia.olu.logic.SaveStore;
import com.arlandsofia.olu.logic.romance.RomanceSaveV45;
import com.arlandsofia.olu.ui.ConfirmBox;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.utils.Align;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/** Pilih slot save. route==null -> tampilkan semua route (menu Muat). newGame -> mulai cerita baru di slot. */
public final class SlotScreen extends BaseScreen {
    private final String onlyRoute;
    private final boolean newGame;
    private final List<Slot> slots = new ArrayList<>();
    private final UiButton back;
    private final SimpleDateFormat fmt = new SimpleDateFormat("dd MMM yyyy HH:mm", Locale.forLanguageTag("id-ID"));

    private final class Slot {
        final String route; final int index;
        SaveStore.Loaded<Progress> data;
        final UiButton main, del;
        float x, y, w, h;
        Slot(final String route, final int index) {
            this.route = route; this.index = index;
            main = new UiButton("", new Runnable() { public void run() { activate(Slot.this); } });
            del = new UiButton("Hapus", new Runnable() { public void run() { askDelete(Slot.this); } });
            main.accent = true; del.textScale = 0.85f;
        }
    }

    public SlotScreen(final OluGame game, String route, boolean newGame) {
        super(game);
        this.onlyRoute = route; this.newGame = newGame;
        for (String r : Routes.ALL) {
            if (route != null && !route.equals(r)) continue;
            for (int i = 1; i <= SaveStore.SLOTS; i++) slots.add(new Slot(r, i));
        }
        back = new UiButton("Kembali", new Runnable() { public void run() { onBack(); } });
        refresh();
    }

    private void refresh() {
        buttons.clear();
        for (Slot s : slots) {
            s.data = game.store.loadSlot(s.route, s.index);
            boolean has = s.data.value != null;
            boolean corrupt = s.data.status == SaveStore.Status.CORRUPT || s.data.status == SaveStore.Status.INCOMPATIBLE;
            if (newGame) { s.main.label = has || corrupt ? "Timpa & Mulai" : "Mulai di sini"; s.main.enabled = true; }
            else { s.main.label = has ? "Lanjutkan" : (s.data.status == SaveStore.Status.INCOMPATIBLE ? "Versi baru" : (corrupt ? "Rusak" : "Kosong")); s.main.enabled = has; }
            s.del.visible = has || corrupt;
            buttons.add(s.main); buttons.add(s.del);
        }
        buttons.add(back);
        layout();
    }

    private void activate(final Slot s) {
        if (newGame) {
            if (s.data.value != null || s.data.status == SaveStore.Status.CORRUPT || s.data.status == SaveStore.Status.INCOMPATIBLE) {
                confirm = new ConfirmBox("Timpa save?", "Slot " + s.index + " " + Routes.display(s.route) + " akan diganti permanen. Cadangkan save bila berasal dari versi lebih baru.",
                        "Timpa", new Runnable() { public void run() { confirm = null; start(s); } },
                        "Batal", new Runnable() { public void run() { confirm = null; } });
            } else start(s);
        } else if (s.data.value != null) {
            try {
                game.switchScreen(new GameScreen(game, s.data.value, false, false));
            } catch (RuntimeException e) {
                confirm = new ConfirmBox("Save tidak cocok", "Save ini tidak cocok dengan data game versi ini (" + e.getMessage() + "). Kamu bisa menghapusnya lalu mulai baru.",
                        "OK", new Runnable() { public void run() { confirm = null; } }, null, null);
            }
        }
    }

    private void start(Slot s) {
        Progress p = Progress.newGame(s.route, s.index, game.quests.firstStep(), game.maps.area(Routes.room(s.route)));
        p.snapshot(game.quests.chapterFirstStep.keySet().iterator().next());
        if (!game.store.saveSlot(p)) {
            confirm = new ConfirmBox("Penyimpanan gagal", "Game baru tidak dapat dibuat. Periksa ruang penyimpanan lalu coba lagi.",
                    "OK", new Runnable() { public void run() { confirm = null; } }, null, null);
            return;
        }
        // New game / intentional overwrite: reset the matching romance namespace too.
        if (!RomanceSaveV45.resetSlot(s.route, s.index)) {
            confirm = new ConfirmBox("Simpan belum sinkron",
                    "Save utama dibuat, tetapi data romance lama belum berhasil dibersihkan. "
                            + "Periksa ruang penyimpanan sebelum melanjutkan.",
                    "OK", new Runnable() { public void run() { confirm = null; refresh(); } }, null, null);
            return;
        }
        game.global.lastRoute = s.route; game.global.lastSlot = s.index;
        game.store.saveGlobal(game.global);
        game.switchScreen(new GameScreen(game, p, false, true));
    }

    private void askDelete(final Slot s) {
        confirm = new ConfirmBox("Hapus save?", "Slot " + s.index + " " + Routes.display(s.route) + " akan dihapus permanen dari perangkat ini.",
                "Hapus", new Runnable() { public void run() {
                    game.store.deleteSlot(s.route, s.index);
                    boolean romanceDeleted = RomanceSaveV45.resetSlot(s.route, s.index);
                    confirm = null; refresh();
                    if (!romanceDeleted) {
                        confirm = new ConfirmBox("Hapus belum lengkap",
                                "Save utama sudah dihapus, tetapi data romance belum berhasil dibersihkan.",
                                "OK", new Runnable() { public void run() { confirm = null; } }, null, null);
                    }
                } },
                "Batal", new Runnable() { public void run() { confirm = null; } });
    }

    @Override
    protected void layout() {
        AdaptiveLayoutV44.Rect[] cells = AdaptiveLayoutV44.slots(screenLayout(), slots.size());
        for (int i=0; i<slots.size(); i++) {
            Slot s=slots.get(i); AdaptiveLayoutV44.Rect r=cells[i];
            s.x=r.x; s.y=r.y; s.w=r.w; s.h=r.h;
            float delW=130;
            s.main.set(s.x+16,s.y+14,Math.max(142,s.w-delW-48),60);
            s.del.set(s.x+s.w-delW-16,s.y+14,delW,60);
        }
        back.set(30+insetL(),26+insetB(),210,62);
    }

    @Override
    protected void drawUi() {
        String head = newGame ? "Pilih slot untuk " + Routes.display(onlyRoute) + " Route" : "Muat Game";
        ui.textCenter(game.assets.title, head, uiW() / 2, uiH() - 30, Ui.CREAM, 0.66f);
        for (Slot s : slots) {
            ui.panel(game.assets.panel, s.x, s.y, s.w, s.h, 1f);
            ui.rect(s.x+17,s.y+s.h-9,s.w-34,3,Ui.GOLD,.35f);
            ui.rect(s.x + 20, s.y + s.h - 56, Math.min(250,s.w-40), 36,
                    s.route.equals(Routes.ARLAND) ? Ui.LAVENDER : Ui.PINK, 1f);
            ui.text(game.assets.body, Routes.upper(s.route) + " • SLOT " + s.index, s.x + 32, s.y + s.h - 28, Ui.WHITE, 0.85f, Align.left, 0);
            float ty = s.y + s.h - 74;
            Progress p = s.data.value;
            if (p != null) {
                QuestDb.Step st = game.quests.step(p.step);
                String ch = st == null ? "?" : game.story.chapterTitle(st.chapter);
                ui.text(game.assets.body, ch, s.x + 24, ty, Ui.INK, 0.85f, Align.left, s.w - 48);
                String obj = st == null ? "Step tidak dikenal" : st.objective(p.route);
                String shortObjective=obj.length()>90?obj.substring(0,87)+"...":obj;
                ui.text(game.assets.body, "✦ " + shortObjective, s.x + 24, ty - 30,
                        Ui.INK_SOFT, Math.min(.75f,.75f*(s.w-48)/Math.max(1f,ui.measure(game.assets.body,shortObjective,.75f))),
                        Align.left, s.w - 48);
                int mins = (int) (p.playSeconds / 60);
                String when = p.savedAt > 0 ? fmt.format(new Date(p.savedAt)) : "-";
                ui.text(game.assets.body, "Waktu main " + mins + " mnt • " + when, s.x + 24, ty - 58, Ui.INK_SOFT, 0.7f, Align.left, s.w - 48);
                if (s.data.status == SaveStore.Status.RECOVERED)
                    ui.text(game.assets.body, "Dipulihkan dari file sementara/cadangan", s.x + 24, ty - 84, Ui.PINK_DEEP, 0.68f, Align.left, s.w - 48);
            } else if (s.data.status == SaveStore.Status.INCOMPATIBLE) {
                ui.wrap(game.assets.body, "Save dibuat di versi game lebih baru. Jangan hapus jika ingin mempertahankan progresnya.", s.x + 24, ty, s.w - 48, Ui.PINK_DEEP, 0.75f, Align.left);
            } else if (s.data.status == SaveStore.Status.CORRUPT) {
                ui.wrap(game.assets.body, "Save rusak dan cadangan tidak bisa dipakai. Hapus slot ini untuk memakainya lagi.", s.x + 24, ty, s.w - 48, Ui.PINK_DEEP, 0.75f, Align.left);
            } else {
                ui.text(game.assets.body, "Slot kosong", s.x + 24, ty, Ui.INK_SOFT, 0.85f, Align.left, 0);
            }
        }
        drawButtons();
    }

    @Override
    protected void onBack() {
        if (newGame) game.switchScreen(new RouteSelectScreen(game));
        else game.switchScreen(new TitleScreen(game));
    }
}
