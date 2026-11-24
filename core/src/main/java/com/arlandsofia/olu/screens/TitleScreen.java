package com.arlandsofia.olu.screens;

import com.arlandsofia.olu.OluGame;
import com.arlandsofia.olu.logic.Progress;
import com.arlandsofia.olu.logic.AdaptiveLayoutV44;
import com.arlandsofia.olu.logic.Routes;
import com.arlandsofia.olu.logic.SaveStore;
import com.arlandsofia.olu.ui.ConfirmBox;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.math.MathUtils;
import com.badlogic.gdx.utils.Align;

/** Layar judul: Lanjutkan, Game Baru, Muat, Pengaturan, Tentang, Keluar. */
public final class TitleScreen extends BaseScreen {
    private final UiButton cont, newGame, load, settingsBtn, about, quit;
    private Progress lastSave;
    private final Texture banner, glow, skyline, foreground;
    private final com.badlogic.gdx.graphics.Color sky = new com.badlogic.gdx.graphics.Color();

    public TitleScreen(final OluGame game) {
        super(game);
        banner = game.assets.uiTex("ui/title_banner.png");
        glow = game.assets.uiTex("ui/soft_glow.png");
        skyline = game.assets.tex("ui/v32_menu_far.png");
        foreground = game.assets.tex("ui/v32_menu_near.png");
        cont = new UiButton("Lanjutkan", new Runnable() { public void run() { continueGame(); } });
        cont.accent = true;
        newGame = new UiButton("Game Baru", new Runnable() { public void run() { game.switchScreen(new RouteSelectScreen(game)); } });
        load = new UiButton("Muat Game", new Runnable() { public void run() { game.switchScreen(new SlotScreen(game, null, false)); } });
        settingsBtn = new UiButton("Pengaturan", new Runnable() { public void run() { game.switchScreen(new SettingsScreen(game)); } });
        about = new UiButton("Tentang", new Runnable() { public void run() { showAbout(); } });
        quit = new UiButton("Keluar", new Runnable() { public void run() { askQuit(); } });
        buttons.add(cont); buttons.add(newGame); buttons.add(load); buttons.add(settingsBtn); buttons.add(about); buttons.add(quit);
    }

    @Override
    public void show() {
        super.show();
        game.audio.ambience(null);
        game.audio.music(game.settings.variedMusic ? "menu_theme" : "town");
        lastSave = null;
        if (game.global.lastRoute != null && Routes.valid(game.global.lastRoute)) {
            SaveStore.Loaded<Progress> l = game.store.loadSlot(game.global.lastRoute, Math.max(1, game.global.lastSlot));
            lastSave = l.value;
        }
        if (lastSave == null) {
            // cari save mana pun yang ada
            outer:
            for (String r : Routes.ALL) for (int s = 1; s <= SaveStore.SLOTS; s++) {
                SaveStore.Loaded<Progress> l = game.store.loadSlot(r, s);
                if (l.value != null) { lastSave = l.value; break outer; }
            }
        }
        cont.enabled = lastSave != null;
        load.enabled = true;
    }

    private void continueGame() {
        if (lastSave == null) return;
        try {
            game.switchScreen(new GameScreen(game, lastSave, false, false));
        } catch (RuntimeException e) {
            confirm = new ConfirmBox("Save tidak cocok", "Save ini tidak cocok dengan versi game sekarang (" + e.getMessage() + "). Buka menu Muat Game untuk memilih atau menghapusnya.",
                    "OK", new Runnable() { public void run() { confirm = null; } }, null, null);
        }
    }

    private void showAbout() {
        confirm = new ConfirmBox("Tentang",
                "Arland & Sofia: Our Little Universe v" + OluGame.VERSION + " (Story Overhaul Source Edition).\n"
                        + "Game Android native (LibGDX), 100% offline: tanpa internet, iklan, login, atau analitik.\n"
                        + "Semua dialog adalah cerita fiksi dan bukan catatan fakta hubungan nyata.",
                "Mengerti", new Runnable() { public void run() { confirm = null; } }, null, null);
    }

    private void askQuit() {
        confirm = new ConfirmBox("Keluar?", "Progress tersimpan otomatis di perangkat ini.", "Keluar",
                new Runnable() { public void run() { Gdx.app.exit(); } }, "Batal", new Runnable() { public void run() { confirm = null; } });
    }

    @Override
    protected void layout() {
        AdaptiveLayoutV44.Rect[] cells = AdaptiveLayoutV44.titleButtons(screenLayout());
        UiButton[] ordered = {cont, newGame, load, settingsBtn, about, quit};
        for (int i=0; i<ordered.length; i++) {
            AdaptiveLayoutV44.Rect r=cells[i]; ordered[i].set(r.x,r.y,r.w,r.h);
        }
    }

    @Override
    protected void drawUi() {
        float w = uiW(), h = uiH();
        // Panorama pixel-art v2.1: far skyline dan foreground mempunyai offset paralaks berbeda.
        ui.imageCover(skyline, 0, 0, w, h, 1f);
        float drift = MathUtils.sin(time * 0.18f) * (game.settings.visualQuality == 0 ? 0f : 13f);
        ui.imageCover(foreground, drift - 16f, -6, w + 32f, h + 12f, 1f);
        if (game.settings.visualQuality > 0) {
            ui.image(glow, w * 0.08f, h * 0.55f, 300, 300, 0.30f);
            ui.image(glow, w * 0.72f, h * 0.60f, 360, 360, 0.26f);
        }
        ui.rect(0, 0, w, h * 0.24f, sky.set(0.10f, 0.08f, 0.18f, 1f), 0.30f);
        for (int i = 0; i < (game.settings.visualQuality == 2 ? 38 : game.settings.visualQuality == 1 ? 24 : 8); i++) {
            float sx = (i * 173.7f + time * (6f + i % 3)) % w;
            float sy = h * 0.22f + (i * 97.3f) % (h * 0.68f);
            float a = 0.25f + 0.45f * (0.5f + 0.5f * MathUtils.sin(time * 1.5f + i));
            ui.rect(sx, sy, i % 3 == 0 ? 4 : 3, i % 3 == 0 ? 4 : 3, Ui.CREAM, a);
        }
        for (int i = 0; i < (game.settings.visualQuality == 2 ? 16 : game.settings.visualQuality == 1 ? 9 : 0); i++) {
            float px = (i * 149f + time * (14f + i)) % (w + 80) - 40f;
            float py = h * 0.18f + ((i * 61f + time * 7f) % (h * 0.4f));
            ui.rect(px, py, 8, 3, i % 2 == 0 ? Ui.PINK : Ui.LAVENDER, 0.45f);
        }
        float bw = Math.min(w - 120, 960), bh = bw * banner.getHeight() / banner.getWidth();
        if (bh > h - 340) { bh = h - 340; bw = bh * banner.getWidth() / banner.getHeight(); }
        ui.panel(game.assets.panel, (w - bw) / 2 - 10, h - bh - 34, bw + 20, bh + 20, 1f);
        ui.image(banner, (w - bw) / 2, h - bh - 24, bw, bh, 1f);
        drawButtons();
        // v4.6.3: save preview now sits between the menu grid and header art;
        // formerly rendered at y=62, on top of the bottom row of buttons.
        AdaptiveLayoutV44.Rect[] menuCells=AdaptiveLayoutV44.titleButtons(screenLayout());
        float menuTop=0f;
        for(AdaptiveLayoutV44.Rect cell:menuCells)menuTop=Math.max(menuTop,cell.y+cell.h);
        float infoY=menuTop+20f;
        float infoW=Math.min(950f,w-insetL()-insetR()-60f);
        float infoX=(w-infoW)*.5f;
        ui.panel(game.assets.panelDark,infoX,infoY,infoW,53f,.88f);
        String info = lastSave != null ? "Terakhir: " + Routes.display(lastSave.route) + " Route • Slot " + lastSave.slot + " • " + game.story.chapterTitle(chapterOf(lastSave)) : "Belum ada save — mulai Game Baru";
        float infoScale=Math.min(.79f,.79f*(infoW-36f)/Math.max(1f,ui.measure(game.assets.body,info,.79f)));
        ui.text(game.assets.body,info,infoX+18f,infoY+35f,Ui.CREAM,infoScale,Align.center,infoW-36f);
        ui.text(game.assets.body, "v" + OluGame.VERSION + "  •  100% offline", 20 + insetL(), 29, Ui.LAVENDER, 0.7f, Align.left, 0);
    }

    private String chapterOf(Progress p) {
        com.arlandsofia.olu.logic.QuestDb.Step s = game.quests.step(p.step);
        return s == null ? "" : s.chapter;
    }

    @Override protected void onBack() { askQuit(); }
}
