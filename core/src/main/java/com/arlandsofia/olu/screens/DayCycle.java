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
final class DayCycle {
    private final GameScreen g;
    DayCycle(GameScreen g) { this.g = g; }

    /** step cerita bersuasana senja/malam memajukan jam dunia (hanya maju), agar HUD, NPC, dan langit selaras. */
    void syncClockToStep() {
        QuestDb.Step st = g.engine.step();
        if (st == null || st.id.equals(g.clockStep)) return;
        g.clockStep = st.id;
        if (st.tint == null || g.replay) return;
        Color c = Color.valueOf(st.tint);
        int target = c.b > c.r ? 20 * 60 : 17 * 60 + 30;
        if (g.p.minute < target) { g.p.minute = target; g.town.refreshTown(); g.town.spawnAnimals(); }
    }

    void newDay(String msg) {
        g.p.day++; g.p.minute = 7 * 60; g.clockAcc = 0;
        g.npcPlaceKey.clear(); g.townActors.clear(); g.npcBrain.clear();
        g.town.refreshTown(); g.town.spawnAnimals();
        g.syncSoundscape();
        String w = WorldClock.weather(g.p.day);
        g.toast(msg + " " + WorldClock.dayName(g.p.day) + ", hari ke-" + g.p.day + " • " + Character.toUpperCase(w.charAt(0)) + w.substring(1));
        g.saveNow();
    }

    void askSleep() {
        boolean early = g.p.minute < 17 * 60;
        g.confirm = new ConfirmBox("Tidur?", early ? "Masih " + WorldClock.hhmm(g.p.minute) + ". Tidur sampai besok pagi?" : "Istirahat sampai besok pagi. Progress tersimpan otomatis.",
                "Tidur", new Runnable() { public void run() { g.confirm = null; g.fade(new Runnable() { public void run() {
                    g.player.dir = Assets.DIR_DOWN; newDay("Selamat pagi!"); } }, null); } },
                "Nanti", new Runnable() { public void run() { g.confirm = null; } });
    }

    void passOut() {
        final String room = Routes.room(g.p.route);
        g.fade(new Runnable() { public void run() {
            MapDb.Area roomArea = g.game.maps.area(room);
            float[] bed = g.bedSpot(roomArea);
            g.enterArea(room, bed[0], bed[1] + 50f, Assets.DIR_DOWN, false);
            newDay("Kamu ketiduran sampai pagi...");
        } }, null);
    }
}
