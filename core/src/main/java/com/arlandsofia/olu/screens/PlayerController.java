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
final class PlayerController {
    private final GameScreen g;
    PlayerController(GameScreen g) { this.g = g; }

    void move(float dt) {
        float kx = 0, ky = 0;
        if (Gdx.input.isKeyPressed(Input.Keys.A) || Gdx.input.isKeyPressed(Input.Keys.LEFT)) kx -= 1;
        if (Gdx.input.isKeyPressed(Input.Keys.D) || Gdx.input.isKeyPressed(Input.Keys.RIGHT)) kx += 1;
        if (Gdx.input.isKeyPressed(Input.Keys.W) || Gdx.input.isKeyPressed(Input.Keys.UP)) ky -= 1;
        if (Gdx.input.isKeyPressed(Input.Keys.S) || Gdx.input.isKeyPressed(Input.Keys.DOWN)) ky += 1;
        float dx = kx, dy = ky;
        if (dx == 0 && dy == 0) { dx = g.controls.vx; dy = -g.controls.vy; }
        float len = (float) Math.sqrt(dx * dx + dy * dy);
        boolean sprint = !g.p.holdingHands && (g.controls.sprintHeld || Gdx.input.isKeyPressed(Input.Keys.SHIFT_LEFT) || Gdx.input.isKeyPressed(Input.Keys.SHIFT_RIGHT));
        if (len < 0.01f) { g.player.walking = false; return; }
        float mag = Math.min(1f, len);
        dx /= len; dy /= len; // diagonal dinormalisasi
        float speed = (sprint ? g.SPRINT_SPEED : g.WALK_SPEED) * Math.max(0.45f, mag) * dt
                * ElevationV50.speedFactor(g.area.terraces, g.player.x, g.player.y);
        float ox = g.player.x, oy = g.player.y;
        float nx = g.player.x + dx * speed;
        // Swept foot collision prevents slipping through thin walls at low FPS.
        if (WorldNavigationV52.clearSegment(g.footCollision,g.player.x,g.player.y,nx,g.player.y)
                && ElevationV50.canStep(g.area.terraces,g.player.x,g.player.y,nx,g.player.y)) g.player.x = nx;
        float ny = g.player.y + dy * speed;
        if (WorldNavigationV52.clearSegment(g.footCollision,g.player.x,g.player.y,g.player.x,ny)
                && ElevationV50.canStep(g.area.terraces,g.player.x,g.player.y,g.player.x,ny)) g.player.y = ny;
        g.player.face(dx, dy);
        g.player.sprinting = sprint;
        float moved = Math.abs(g.player.x - ox) + Math.abs(g.player.y - oy);
        g.player.walking = moved > 0.01f;
        if (g.partnerMode == 2 && g.player.walking && !g.p.holdingHands) {
            float[] last = g.trail.peekLast();
            if (last == null || Math.abs(last[0] - g.player.x) + Math.abs(last[1] - g.player.y) > 6) g.trail.addLast(new float[]{g.player.x, g.player.y});
            while (g.trail.size() > 80) g.trail.pollFirst();
        }
        g.p.x = g.player.x; g.p.y = g.player.y; g.p.dir = Actor.dirName(g.player.dir);
        checkDoors(ox, oy);
    }

    void checkDoors(float ox, float oy) {
        if (g.doorCooldown > 0) return;
        for (final MapDb.Door d : g.area.doors) {
            if (!d.touches(g.player.x, g.player.y)) continue;
            String lock = g.engine.doorLock(d);
            if (lock != null) {
                g.toast(lock);
                g.game.audio.sfx("soft_wrong");
                g.player.x = ox; g.player.y = oy;
                if (d.touches(g.player.x, g.player.y)) { // masih di zona: dorong menjauh dari pusat pintu
                    float vx = g.player.x - d.cx(), vy = g.player.y - d.cy();
                    float l = Math.max(1f, (float) Math.sqrt(vx * vx + vy * vy));
                    float tx = g.player.x + vx / l * 14, ty = g.player.y + vy / l * 14;
                    if (!g.area.blocked(tx, ty) && ElevationV50.canStep(g.area.terraces,g.player.x,g.player.y,tx,ty)) { g.player.x = tx; g.player.y = ty; }
                }
                g.doorCooldown = 1.2f;
                return;
            }
            g.controls.reset();
            g.fade(new Runnable() { public void run() { g.enterArea(d.to, d.tx, d.ty, Actor.dirOf(d.dir), true); } },
                    new Runnable() { public void run() { g.runner.run(g.engine.onEnterArea(g.area.id)); } });
            return;
        }
    }

    void findTarget() {
        g.targetQuest = null; g.targetExamine = null; g.targetNpc = null; g.targetSide = null; g.targetTalk = null; g.targetRomance = false; g.targetAnimal = null; g.targetBed = false;
        float best = Float.MAX_VALUE;
        for (QuestDb.Interactable it : g.engine.interactables(g.area.id)) {
            float d = g.dist(it.x, it.y);
            if (d <= it.r && d < best) { best = d; g.targetQuest = it; }
        }
        if (g.targetQuest != null) return;
        best = Float.MAX_VALUE;
        for (QuestDb.Interactable it : g.engine.sideInteractables(g.area.id)) {
            float d = g.dist(it.x, it.y);
            if (d <= it.r && d < best) { best = d; g.targetSide = it; }
        }
        for (QuestDb.TownNpc n : g.engine.townNpcsNow(g.area.id)) {
            Actor ac = g.townActors.get(n.id); if (ac == null) continue;
            float d = g.dist(ac.x, ac.y);
            if (d <= 64 && d < best && g.engine.npcDialog(n) != null) { best = d; g.targetNpc = n; g.targetSide = null; }
        }
        if (g.targetSide != null || g.targetNpc != null) return;
        for (Animal an : g.animals) if (an.pettable && g.dist(an.x, an.y) < 40) { g.targetAnimal = an; return; }
        if (g.area.id.equals(Routes.room(g.p.route))) {
            float[] bed = g.bedSpot(g.area);
            if (g.dist(bed[0], bed[1]) < 60) { g.targetBed = true; return; }
        }
        if (g.partnerMode == 2 && g.dist(g.partner.x, g.partner.y) <= 58) {
            g.targetTalk = g.engine.partnerTalk(g.area.id);
            g.targetRomance = g.engine.romanceReady();
            if (g.targetTalk != null || g.targetRomance) return;
        }
        best = Float.MAX_VALUE;
        for (MapDb.Examine e : g.engine.examine(g.area)) {
            float d = g.dist(e.x, e.y);
            if (d <= e.r && d < best) { best = d; g.targetExamine = e; }
        }
    }

    void interact() {
        if (g.targetQuest != null) {
            g.player.face(g.targetQuest.x - g.player.x, g.targetQuest.y - g.player.y);
            g.runner.run(g.engine.actionsFor(g.targetQuest));
        } else if (g.targetSide != null) {
            g.player.face(g.targetSide.x - g.player.x, g.targetSide.y - g.player.y);
            g.runner.run(g.engine.actionsFor(g.targetSide));
        } else if (g.targetTalk != null) {
            g.player.face(g.partner.x - g.player.x, g.partner.y - g.player.y);
            g.partner.face(g.player.x - g.partner.x, g.player.y - g.partner.y);
            g.runner.run(g.engine.talkActions(g.targetTalk));
        } else if (g.targetRomance) {
            g.player.face(g.partner.x - g.player.x, g.partner.y - g.player.y);
            g.partner.face(g.player.x - g.partner.x, g.player.y - g.partner.y);
            g.controls.reset();
            g.romance.open(g.area.id, new RomanceOverlay.Listener() {
                public void completed(List<Map<String, Object>> acts, String message) {
                    g.saveNow();
                    g.toast(message);
                    if (message.startsWith("Hadiah")) g.game.audio.sfx("gift", .7f);
                    else if (message.startsWith("Kencan")) g.game.audio.sfx("heart", .7f);
                    else if (message.startsWith("Aksi berdua")) g.game.audio.sfx("hug", .6f);
                    g.runner.run(acts);
                }
            });
        } else if (g.targetAnimal != null) {
            g.player.face(g.targetAnimal.x - g.player.x, g.targetAnimal.y - g.player.y);
            g.targetAnimal.pet();
            String animalSfx = g.targetAnimal.type.startsWith("cat") ? "cat_meow"
                    : g.targetAnimal.type.startsWith("dog") ? "dog_bark"
                    : g.targetAnimal.type.startsWith("duck") ? "duck_quack" : "bird_chirp";
            g.game.audio.sfx(animalSfx, .52f);
            g.p.flags.add("PET_" + g.targetAnimal.type.replaceAll("_.*", "").toUpperCase(java.util.Locale.ROOT));
            if (g.p.petted.add(g.targetAnimal.type.replaceAll("_.*", ""))) g.toast("Teman berbulu baru! (" + g.p.petted.size() + " jenis)");
            if (g.partnerMode == 2) g.partner.showEmote("heart", 1.4f);
        } else if (g.targetBed) {
            g.days.askSleep();
        } else if (g.targetNpc != null) {
            Actor ac = g.townActors.get(g.targetNpc.id);
            if (ac != null) g.player.face(ac.x - g.player.x, ac.y - g.player.y);
            if (ac != null) ac.face(g.player.x - ac.x, g.player.y - ac.y);
            Map<String, Object> d = g.engine.npcDialog(g.targetNpc);
            if (d != null) g.runner.run(g.engine.resolve(com.arlandsofia.olu.logic.Json.objList(d, "actions")));
        } else if (g.targetExamine != null) {
            g.player.face(g.targetExamine.x - g.player.x, g.targetExamine.y - g.player.y);
            g.game.audio.sfx("page_turn", .42f);
            g.dialog.start(g.targetExamine.lines(g.p.route), null, g.p.route, g.dialogListener(), null);
            g.controls.reset();
        } else {
            g.toast("Dekati penanda ✦ untuk berinteraksi");
        }
    }
}
