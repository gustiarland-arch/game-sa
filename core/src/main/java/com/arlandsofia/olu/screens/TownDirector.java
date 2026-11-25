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
final class TownDirector {
    private final GameScreen g;
    TownDirector(GameScreen g) { this.g = g; }

    /** NPC sesuai jadwal & jam. Aktor yang masih di area ini dipertahankan dan berjalan ke titik barunya. */
    void refreshTown() {
        java.util.Set<String> keep = new java.util.HashSet<>();
        for (QuestDb.TownNpc n : g.engine.townNpcsNow(g.area.id)) {
            Object[] pl = g.engine.npcPlace(n);
            float x = ((Number) pl[1]).floatValue(), y = ((Number) pl[2]).floatValue(), rad = ((Number) pl[4]).floatValue();
            float[] npcSafe = WorldNavigationV52.nearestOpen(g.footCollision,x,y,g.area.spawnX,g.area.spawnY);
            x=npcSafe[0]; y=npcSafe[1];
            String key = pl[0] + "@" + Math.round(x) + "," + Math.round(y);
            keep.add(n.id);
            Actor ac = g.townActors.get(n.id);
            if (ac == null) {
                ac = new Actor(n.sprite); ac.x = x; ac.y = y; ac.dir = Actor.dirOf((String) pl[3]);
                g.townActors.put(n.id, ac); g.npcBrain.put(n.id, new float[]{x, y, rad, x, y, MathUtils.random(1f, 4f), 0f});
            } else if (!key.equals(g.npcPlaceKey.get(n.id))) {
                float[] b = g.npcBrain.get(n.id); b[0] = x; b[1] = y; b[2] = rad; b[3] = x; b[4] = y; b[5] = 0f; b[6] = 0f;
            }
            g.npcPlaceKey.put(n.id, key);
        }
        g.townActors.keySet().retainAll(keep); g.npcBrain.keySet().retainAll(keep); g.npcPlaceKey.keySet().retainAll(keep);
    }

    /** NPC berjalan pelan di sekitar titik jadwalnya, berhenti saat diajak bicara atau ada cutscene. */
    void updateNpcs(float dt) {
        if (g.cine.active()) return;
        for (Map.Entry<String, Actor> e : g.townActors.entrySet()) {
            Actor ac = e.getValue(); float[] b = g.npcBrain.get(e.getKey());
            if (b == null) continue;
            if (g.dialog.active() && g.targetNpc != null && g.targetNpc.id.equals(e.getKey())) { ac.walking = false; continue; }
            float dx = b[3] - ac.x, dy = b[4] - ac.y, d = (float) Math.sqrt(dx * dx + dy * dy);
            if (d > 2f) {
                float speed = LivingWorldV46.walkingSpeed(WorldClock.hour(g.p.minute), g.weather(), g.isIndoor())
                        * ac.motion.walkSpeed * ElevationV50.speedFactor(g.area.terraces, ac.x, ac.y);
                float sp = Math.min(d, speed * Math.max(0f, Math.min(.05f, dt)));
                float nx = ac.x + dx / d * sp, ny = ac.y + dy / d * sp;
                boolean nearPlayer = Math.abs(nx - g.player.x) < 22 && Math.abs(ny - g.player.y) < 16;
                boolean nearPartner = g.partnerMode == 2
                        && Math.abs(nx - g.partner.x) < 20 && Math.abs(ny - g.partner.y) < 16;
                boolean nearNpc = false;
                for (Map.Entry<String, Actor> other : g.townActors.entrySet()) {
                    if (other.getKey().equals(e.getKey())) continue;
                    Actor o = other.getValue();
                    if (Math.abs(nx - o.x) < 14 && Math.abs(ny - o.y) < 12) { nearNpc = true; break; }
                }
                if (WorldNavigationV52.clearSegment(g.footCollision,ac.x,ac.y,nx,ny)
                        && ElevationV50.canStep(g.area.terraces,ac.x,ac.y,nx,ny)
                        && !nearPlayer && !nearPartner && !nearNpc) {
                    ac.x = nx; ac.y = ny; ac.face(dx, dy); ac.walking = true;
                } else {
                    // No teleport-to-target: pause and seek a legal alternate waypoint.
                    b[3] = ac.x; b[4] = ac.y; b[5] = .55f; ac.walking = false;
                }
            } else {
                ac.walking = false;
                b[5] -= dt;
                if (b[5] <= 0f) {
                    b[5] = MotionPersonalityV53.pauseSeconds(e.getKey(), g.p.day, g.p.minute);
                    if (b[2] > 0) {
                        // Stable per-actor sequence creates different legal waypoints
                        // even before the next 15-minute window; no teleportation.
                        b[6] = (b[6] + 1f) % 4096f;
                        LivingWorldV46.Target next = LivingWorldV46.wanderTarget(
                                e.getKey(), g.p.day, g.p.minute, b[0], b[1], b[2], ac.x, ac.y,
                                g.isIndoor(), g.weather(), new LivingWorldV46.Collision() {
                                    public boolean blocked(float x,float y) { return g.area.blocked(x,y); }
                                }, (int)b[6]);
                        b[3] = next.x; b[4] = next.y;
                    } else if (MathUtils.random() < .3f) ac.dir = MathUtils.random(0, 3);
                    String act = g.npcIdleActivity(e.getKey());
                    if (act != null && ac.pose == null) ac.setPose(act,
                            1.1f + ac.motion.breathing * .9f);
                }
            }
        }
    }

    void spawnAnimals() {
        g.animals.clear();
        boolean day = !WorldClock.isNight(g.p.minute), rain = WorldClock.HUJAN.equals(g.engine.weatherNow());
        for (Map<String, Object> spec : g.area.animals) {
            String type = com.arlandsofia.olu.logic.Json.str(spec, "type", "cat");
            boolean dayOnly = com.arlandsofia.olu.logic.Json.bool(spec, "day", !type.startsWith("cat"));
            if (dayOnly && (!day || (rain && !type.equals("duck")))) continue; // bebek tetap berenang saat hujan
            float[] reg = com.arlandsofia.olu.logic.Json.floats(spec.get(spec.containsKey("water") ? "water" : "region"));
            int n = (int) com.arlandsofia.olu.logic.Json.num(spec, "n", 1);
            for (int i = 0; i < n; i++) {
                for (int k = 0; k < 12; k++) {
                    float x, y;
                    if (spec.containsKey("water")) { float a = MathUtils.random(0f, 6.28f), r = MathUtils.random(0f, 0.7f); x = reg[0] + MathUtils.cos(a) * reg[2] * r; y = reg[1] + MathUtils.sin(a) * reg[3] * r; }
                    else { x = reg[0] + MathUtils.random(0f, reg[2]); y = reg[1] + MathUtils.random(0f, reg[3]); }
                    if (!spec.containsKey("water") && g.area.blocked(x, y)) continue;
                    g.animals.add(new Animal(type, x, y, reg)); break;
                }
            }
        }
    }

    void refreshNpcs() {
        refreshTown();
        if (g.partnerMode == 2) return;
        g.partnerMode = 0;
        for (QuestEngine.NpcView n : g.engine.npcs(g.area.id)) {
            if (n.who.equals(g.partner.character)) {
                g.partnerMode = 1; g.partner.x = n.x; g.partner.y = n.y; g.partner.dir = Actor.dirOf(n.dir); g.partner.walking = false;
            }
        }
    }
}
