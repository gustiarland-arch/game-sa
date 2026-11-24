package com.arlandsofia.olu.screens;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.OluGame;
import com.arlandsofia.olu.game.Actor;
import com.arlandsofia.olu.game.Animal;
import com.arlandsofia.olu.game.WorldFx;
import com.arlandsofia.olu.logic.WorldClock;
import com.arlandsofia.olu.logic.LivingWorldV46;
import com.arlandsofia.olu.logic.MotionPersonalityV53;
import com.arlandsofia.olu.logic.WorldLightingV37;
import com.arlandsofia.olu.logic.SoundscapePlan;
import com.arlandsofia.olu.logic.CameraRig;
import com.arlandsofia.olu.logic.CameraFramingV52;
import com.arlandsofia.olu.logic.WorldNavigationV52;
import com.arlandsofia.olu.logic.ElevationV50;
import com.arlandsofia.olu.logic.PixelPerfectV54;
import com.arlandsofia.olu.logic.WeatherFxV54;
import com.arlandsofia.olu.logic.AdaptiveLayoutV43;
import com.arlandsofia.olu.logic.Achievements;
import com.arlandsofia.olu.game.CutscenePlayer;
import com.arlandsofia.olu.game.DialogBox;
import com.arlandsofia.olu.game.DialogueHistoryOverlay;
import com.arlandsofia.olu.game.MemoryBookOverlay;
import com.arlandsofia.olu.game.ShopOverlay;
import com.arlandsofia.olu.game.RomanceOverlay;
import com.arlandsofia.olu.game.PuzzleOverlay;
import com.arlandsofia.olu.game.TouchControls;
import com.arlandsofia.olu.game.minigame.MinigameOverlay;
import com.arlandsofia.olu.logic.ActionRunner;
import com.arlandsofia.olu.logic.MapDb;
import com.arlandsofia.olu.logic.Progress;
import com.arlandsofia.olu.logic.QuestDb;
import com.arlandsofia.olu.logic.QuestEngine;
import com.arlandsofia.olu.logic.QuestCompass;
import com.arlandsofia.olu.logic.QuestPathV52;
import com.arlandsofia.olu.logic.Routes;
import com.arlandsofia.olu.logic.StoryDb;
import com.arlandsofia.olu.ui.ConfirmBox;
import com.arlandsofia.olu.ui.SettingsPanel;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Input;
import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.TextureRegion;
import com.badlogic.gdx.math.MathUtils;
import com.badlogic.gdx.math.Vector2;
import com.badlogic.gdx.utils.Align;
import com.badlogic.gdx.utils.viewport.ExtendViewport;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Extracted from GameScreen in v6 (mechanical move; state stays on GameScreen). */
final class HudRenderer {
    private final GameScreen g;
    HudRenderer(GameScreen g) { this.g = g; }

    
    void drawUi() {
        Assets a = g.game.assets;
        float W = g.uiW(), H = g.uiH(), inL = g.insetL(), inR = g.insetR(), inT = g.insetT(), inB = g.insetB();
        boolean overlay = g.dialog.active() || g.puzzle.active() || g.minigame.active() || g.creditsTime >= 0 || g.book.active() || g.shop.active() || g.romance.active() || g.pauseOpen || g.settingsOpen || g.cardTime >= 0 || g.cine.active();
        if (g.cine.active() || g.cine.letterboxed()) { drawCineUi(W, H, inL, inR, inB); return; }

        // label pintu terdekat
        if (!overlay) {
            for (MapDb.Door d : g.area.doors) {
                float dx = d.cx() - g.player.x, dy = d.cy() - g.player.y;
                if (dx * dx + dy * dy < 120 * 120 && d.label.length() > 0) {
                    Vector2 v = g.mapToUi(d.cx(), d.y - 6);
                    g.ui.text(a.label, d.label, v.x - 200, v.y + 34, Ui.WHITE, 0.9f, Align.center, 400);
                }
            }
        }

        // HUD kiri atas
        float hx = inL + 16, hy = H - inT - 16;
        float aw = Math.max(360, g.ui.measure(a.body, g.area.name, 1.05f) + 140);
        g.ui.panel(a.panelDark, hx, hy - 126, aw, 126, 0.95f);
        g.ui.rect(hx + 14, hy - 36, aw - 28, 3, Ui.PINK, 0.45f);
        g.ui.text(a.body, g.area.name, hx + 22, hy - 16, Ui.CREAM, 1.05f, Align.left, 0);
        String wz = g.weather(); String wl = "rain".equals(wz) ? "Hujan" : WorldClock.BERAWAN.equals(wz) ? "Berawan" : WorldClock.BERANGIN.equals(wz) ? "Berangin" : "Cerah";
        g.ui.text(a.body, WorldClock.dayName(g.p.day) + " • Hari " + g.p.day + " • " + WorldClock.hhmm(g.p.minute) + " • " + wl, hx + 22, hy - 92, Ui.GOLD, 0.72f, Align.left, 0);
        g.ui.image(g.coinIcon, hx + aw - 136, hy - 34, 24, 24, 1f);
        g.ui.text(a.body, String.valueOf(g.p.coins), hx + aw - 106, hy - 18, Ui.GOLD, 0.84f, Align.left, 0);
        g.ui.text(a.body, "♥ " + g.p.affection + "/100", hx + aw - 136, hy - 54, Ui.PINK, 0.80f, Align.left, 0);
        if (g.p.holdingHands && g.partnerMode == 2) g.ui.text(a.body, "♡ Gandengan", hx + aw - 139, hy - 108, Ui.PINK, 0.67f, Align.left, 0);
        QuestDb.Step st = g.engine.step();
        String chName = st == null ? "" : (st.chapter.equals("PRO") ? "PROLOG" : "CHAPTER " + st.chapter.substring(1).replaceFirst("^0", ""));
        g.ui.text(a.body, Routes.upper(g.p.route) + " ROUTE • " + chName, hx + 22, hy - 56, Ui.LAVENDER, 0.72f, Align.left, 0);

        // misi aktif (tengah atas)
        String obj = g.engine.objectiveText();
        float ow = Math.min(W - aw - 420 - inL - inR, Math.max(360, g.ui.measure(a.body, obj, 0.9f) + 60));
        float ox = Math.max(hx + aw + 14, (W - ow) / 2);
        float flash = g.objectiveFlash > 0 ? 0.5f + 0.5f * MathUtils.sin(g.objectiveFlash * 12f) : 0f;
        g.ui.panel(a.panelDark, ox, hy - 88, ow, 88, 0.95f);
        if (flash > 0) g.ui.rect(ox + 10, hy - 84, ow - 20, 4, Ui.GOLD, flash);
        g.ui.text(a.body, "✦ MISI AKTIF", ox, hy - 14, Ui.PINK, 0.66f, Align.center, ow);
        float objScale = Math.min(0.9f, 0.9f * (ow - 40) / Math.max(1f, g.ui.measure(a.body, obj, 0.9f)));
        g.ui.text(a.body, obj, ox + 20, hy - 46, Ui.CREAM, objScale, Align.center, ow - 40);
        // Petunjuk arah untuk interaksi *utama yang saat ini aktif*, bukan jalur semu lintas peta.
        if (!overlay && g.game.settings.showHints) {
            if (g.questRouteRefresh<=0f) {
                g.cachedQuestRoute=QuestPathV52.hint(g.area,g.player.x,g.player.y,g.engine.interactables(g.area.id),g.p.route);
                g.questRouteRefresh=.65f;
            }
            QuestCompass.Hint hint=g.cachedQuestRoute;
            if (hint != null) {
                float ww = Math.max(300, Math.min(ow + 40, 510));
                g.ui.panel(a.panelDark, ox + (ow - ww) / 2, hy - 133, ww, 40, .89f);
                String direction = hint.text();
                if (direction.length() > 62) direction = direction.substring(0, 59) + "...";
                g.ui.text(a.body, direction, ox + (ow - ww) / 2 + 12, hy - 106,
                        Ui.GOLD, .63f, Align.center, ww - 24);
            }
        }
        // Notifikasi kecil: event hanya tampil bila area/jam/cuaca/route dan batas harian cocok.
        if (!overlay && g.game.settings.showHints) {
            for (QuestDb.WorldEvent ev : g.game.quests.worldEvents) {
                if (ev.area.equals(g.area.id) && g.engine.worldEventBlock(ev.id, g.area.id) == null) {
                    g.ui.text(a.body, "✦ EVENT HARI INI: " + ev.title, ox + 20, hy - 72,
                            Ui.GOLD, 0.56f, Align.center, ow - 40);
                    break;
                }
            }
        }

        if (!overlay && g.engine.deliveryOpen()) {
            g.ui.panel(a.panelDark, W / 2 - 255, hy - 151, 510, 45, 0.94f);
            g.ui.text(a.body, "Antar surat: " + g.engine.deliveredToday() + "/3  •  Plaza / Jalan Kota / Tepi Danau",
                    W / 2 - 240, hy - 118, Ui.GOLD, 0.73f, Align.center, 480);
        }
        g.ui.button(g.hudBook);
        g.ui.button(g.hudPause);
        if (g.replay) {
            g.ui.panel(a.panelDark, W / 2 - 250, hy - 140, 500, 44, 0.9f);
            g.ui.text(a.body, "MODE REPLAY • progres tidak disimpan", W / 2 - 250, hy - 108, Ui.GOLD, 0.72f, Align.center, 500);
        }

        if (!overlay && g.fadePhase == 0) {
            // Pilihan kontrol berlaku segera setelah pemain menutup Pengaturan.
            g.controls.layout(W, H, inL, inR, inB, AdaptiveLayoutV43.controlScale(g.screenLayout(), g.game.settings.controlScale),
                    g.game.settings.leftHanded, g.game.settings.floatingJoystick, g.game.settings.joystickSensitivity);
            String prompt = g.targetQuest != null ? "✦ " + g.targetQuest.label(g.p.route)
                    : g.targetSide != null ? (g.targetSide.id.startsWith("WE27_") ? "✦ Event: " : "♪ ") + g.targetSide.label(g.p.route)
                    : g.targetNpc != null ? "Bicara: " + g.targetNpc.name
                    : g.targetAnimal != null ? "Elus " + g.animalName(g.targetAnimal.type)
                    : g.targetBed ? "Tidur" 
                    : g.targetTalk != null ? "♥ Ngobrol" 
                    : g.targetRomance ? "♥ Waktu Berdua"
                    : (g.targetExamine != null ? g.targetExamine.label : null);
            g.controls.draw(g.ui, g.game.settings.controlOpacity, prompt);
        }

        if (g.bannerTime > 0 && !overlay) {
            float al = Math.min(1f, g.bannerTime * 2f);
            g.ui.textCenter(a.title, g.bannerText, W / 2, H * 0.62f, g.tint.set(1, 1, 1, al), 0.62f);
        }
        if (g.toastTime > 0) {
            float al = Math.min(1f, g.toastTime * 3f);
            float tw = Math.min(W - 80, g.ui.measure(a.body, g.toastText, 0.9f) + 60);
            float ty = g.dialog.active() ? H * 0.62f : H * 0.66f;
            g.ui.panel(a.panelDark, (W - tw) / 2, ty - 30, tw, 58, al);
            g.ui.text(a.body, g.toastText, (W - tw) / 2, ty + 12, g.tint.set(Ui.CREAM.r, Ui.CREAM.g, Ui.CREAM.b, al), 0.9f, Align.center, tw);
        }

        if (g.bubbleTime > 0 && g.bubbleText != null && g.partnerMode == 2 && !overlay) {
            float al = Math.min(1f, Math.min(g.bubbleTime * 2f, (3.6f - g.bubbleTime) * 4f));
            Vector2 v = g.mapToUi(g.partner.x, g.partner.y - g.partner.drawHeight() - 4);
            float bw = Math.min(560, g.ui.measure(a.body, g.bubbleText, 0.78f) + 44), bx = MathUtils.clamp(v.x - bw / 2, inL + 10, W - inR - bw - 10);
            g.ui.panel(a.panel, bx, v.y + 8, bw, 62, al);
            g.ui.text(a.body, g.bubbleText, bx, v.y + 52, g.tint.set(Ui.INK.r, Ui.INK.g, Ui.INK.b, al), 0.78f, Align.center, bw);
        }
        g.dialog.draw(g.ui, W, H, inL, inR, inB);
        g.puzzle.draw(g.ui, W, H);
        g.minigame.draw(g.ui, W, H);
        if (g.creditsTime >= 0) drawCredits(W, H);
        if (g.pauseOpen) drawPause();
        g.book.draw(g.ui, W, H);
        g.shop.draw(g.ui, W, H);
        g.romance.draw(g.ui, W, H);
        if (g.settingsOpen) g.settingsPanel.draw(g.ui, W, H);
        g.dialogueHistory.draw(g.ui, W, H);

        if (g.cardTime >= 0) {
            float al = Math.min(1f, g.cardTime * 3f);
            g.ui.rect(0, 0, W, H, Ui.BG, 0.92f * al);
            g.ui.textCenter(a.title, g.cardTitle, W / 2, H / 2 + 60, g.tint.set(1, 1, 1, al), 0.7f);
            g.ui.wrap(a.body, g.cardSub, W * 0.15f, H / 2 - 20, W * 0.7f, g.tint.set(Ui.LAVENDER.r, Ui.LAVENDER.g, Ui.LAVENDER.b, al), 1f, Align.center);
            if (g.cardTime > 0.6f) g.ui.textCenter(a.body, "Ketuk untuk lanjut", W / 2, 70, g.tint.set(1, 1, 1, 0.6f * al), 0.75f);
        }
        if (g.fadeAlpha > 0) g.ui.rect(0, 0, W, H, Ui.BG, g.fadeAlpha);
    }

    /** Saat cutscene: HUD disembunyikan, hanya letterbox, dialog, toast, dan fade. */
    void drawCineUi(float W, float H, float inL, float inR, float inB) {
        g.cine.drawUi(g.ui, W, H);
        if (g.toastTime > 0) {
            float al = Math.min(1f, g.toastTime * 3f);
            float tw = Math.min(W - 80, g.ui.measure(g.game.assets.body, g.toastText, 0.9f) + 60);
            g.ui.panel(g.game.assets.panelDark, (W - tw) / 2, H * 0.7f - 30, tw, 58, al);
            g.ui.text(g.game.assets.body, g.toastText, (W - tw) / 2, H * 0.7f + 12, g.tint.set(Ui.CREAM.r, Ui.CREAM.g, Ui.CREAM.b, al), 0.9f, Align.center, tw);
        }
        g.dialog.draw(g.ui, W, H, inL, inR, inB);
        if (g.pauseOpen) drawPause();
        if (g.settingsOpen) g.settingsPanel.draw(g.ui, W, H);
        g.dialogueHistory.draw(g.ui, W, H);
        if (g.fadeAlpha > 0) g.ui.rect(0, 0, W, H, Ui.BG, g.fadeAlpha);
    }

    void drawCredits(float W, float H) {
        g.ui.rect(0, 0, W, H, Ui.BG, Math.min(1f, g.creditsTime));
        float y0 = -60 + g.creditsTime * 70f;
        List<String> lines = g.game.quests.credits;
        for (int i = 0; i < lines.size(); i++) {
            float y = y0 - i * 64;
            if (y < -40 || y > H + 60) continue;
            g.ui.text(i == 0 ? g.game.assets.title : g.game.assets.body, lines.get(i), 0, y, i == 0 ? Ui.GOLD : Ui.CREAM, i == 0 ? 0.6f : 1f, Align.center, W);
        }
        g.ui.text(g.game.assets.body, "Ketuk untuk mempercepat", 0, 50, Ui.LAVENDER, 0.7f, Align.center, W);
    }

    void drawPause() {
        float W = g.uiW(), H = g.uiH();
        g.ui.rect(0, 0, W, H, Ui.BG, 0.6f);
        float pw = Math.min(520, W - g.insetL() - g.insetR() - 28);
        float ph = Math.min(670, H - g.insetT() - g.insetB() - 20);
        float px = (W - pw) / 2, py = (H - ph) / 2;
        g.ui.panel(g.game.assets.panel, px, py, pw, ph, 1f);
        g.ui.text(g.game.assets.title, "Jeda", px, py + ph - 26, Ui.INK, 0.6f, Align.center, pw);
        int mins = (int) (g.p.playSeconds / 60);
        g.ui.text(g.game.assets.body, Routes.display(g.p.route) + " Route • Slot " + g.p.slot + " • " + mins + " menit", px, py + 46, Ui.INK_SOFT, 0.72f, Align.center, pw);
        for (UiButton b : g.pauseButtons) g.ui.button(b);
    }
}
