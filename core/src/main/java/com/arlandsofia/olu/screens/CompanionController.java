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
final class CompanionController {
    private final GameScreen g;
    CompanionController(GameScreen g) { this.g = g; }

    /** komentar pasangan sekali per area (disimpan sebagai flag CMT_<area>). */
    void queueComment() {
        Map<String, List<String>> m = g.game.quests.comments.get(g.area.id);
        if (m == null || g.p.hasFlag("CMT_" + g.area.id)) return;
        List<String> l = m.get(g.p.route);
        if (l == null || l.isEmpty()) return;
        g.pendingComment = 1.4f;
    }

    void showComment() {
        List<String> l = g.game.quests.comments.get(g.area.id).get(g.p.route);
        g.bubbleText = l.get(MathUtils.random(0, l.size() - 1)); g.bubbleTime = 3.6f;
        g.p.flags.add("CMT_" + g.area.id);
        g.partner.faceTo(g.player); g.partner.showEmote("note", 1.2f);
    }

    /** perilaku kecil companion saat diam: menoleh, melihat sekeliling, bereaksi pada hujan, memperhatikan target interaksi. */
    void companionLife(float dt) {
        if (g.partnerMode != 2 || g.cine.active() || g.partner.walking || g.p.holdingHands) { g.compIdle = 0; return; }
        Object tgt = g.targetQuest != null ? g.targetQuest : g.targetNpc != null ? g.targetNpc : g.targetSide;
        if (tgt != null) {
            float tx = g.targetQuest != null ? g.targetQuest.x : g.targetNpc != null ? g.targetNpc.x : g.targetSide.x;
            float ty = g.targetQuest != null ? g.targetQuest.y : g.targetNpc != null ? g.targetNpc.y : g.targetSide.y;
            g.partner.face(tx - g.partner.x, ty - g.partner.y); g.compIdle = 0; return;
        }
        g.compIdle += dt;
        if (g.compIdle < g.compNext) return;
        g.compIdle = 0; g.compNext = MathUtils.random(2.5f, 6f);
        boolean rain = "rain".equals(g.weather()) && !g.isIndoor();
        int r = MathUtils.random(0, 9);
        // Reactions remain cosmetic (do not change romance rewards or story flags).
        if (!rain && g.p.affection >= 75 && r >= 8 && g.dist(g.partner.x,g.partner.y)<90f) {
            g.partner.faceTo(g.player);
            g.partner.setPose(r == 8 ? "shy" : "excited",1.15f);
            g.partner.showEmote("heart",1.3f);
        } else if (rain && r < 3) { g.partner.showEmote("sweat", 1.4f); g.partner.faceTo(g.player); }
        else if (r < 4) { g.partner.faceTo(g.player); g.partner.setPose("ponder",1.0f); }
        else if (r < 7) g.partner.dir = MathUtils.random(0, 3);
        else if (r < 9) {
            Actor near = null; float best = 220 * 220;
            for (Actor t : g.townActors.values()) { float dx = t.x - g.partner.x, dy = t.y - g.partner.y; if (dx * dx + dy * dy < best) { best = dx * dx + dy * dy; near = t; } }
            if (near != null) g.partner.faceTo(near); else g.partner.faceTo(g.player);
        } else { g.partner.faceTo(g.player); g.partner.showEmote(MathUtils.random(0, 1) == 0 ? "note" : "heart", 1.4f); }
    }

    void placeBeside() {
        float[][] offs = {{-30, 6}, {30, 6}, {0, 24}, {0, -24}, {-44, 0}, {44, 0}};
        for (float[] o : offs) {
            float nx = g.player.x + o[0], ny = g.player.y + o[1];
            if (!g.area.blocked(nx, ny)) { g.partner.x = nx; g.partner.y = ny; g.partner.dir = g.player.dir; return; }
        }
        // If there is no adjacent safe tile, keep the companion behind until a legal spot appears.
        float[] safe = WorldNavigationV52.nearestOpen(g.footCollision,g.player.x-34,g.player.y,g.player.x,g.player.y);
        g.partner.x = safe[0]; g.partner.y = safe[1];
    }

    void followCompanion(float dt) {
        if (g.cine.active()) return; // cutscene menguasai pose dan posisi kedua aktor
        if (g.partnerMode == 2 && g.p.holdingHands) {
            float sign = (g.player.dir == Assets.DIR_LEFT) ? -1f : 1f;
            float tx = g.player.x + 25f * sign, ty = g.player.y + 3f;
            if (g.area.blocked(tx, ty) || !ElevationV50.canStep(g.area.terraces,g.partner.x,g.partner.y,tx,ty)) tx = g.player.x - 25f * sign;
            if (!g.area.blocked(tx, ty) && ElevationV50.canStep(g.area.terraces,g.partner.x,g.partner.y,tx,ty)) {
                float k = Math.min(1f, dt * 14f);
                float stepX=g.partner.x+(tx-g.partner.x)*k, stepY=g.partner.y+(ty-g.partner.y)*k;
                if (!WorldNavigationV52.clearSegment(g.footCollision,g.partner.x,g.partner.y,stepX,stepY)) { g.partner.walking=false; return; }
                g.partner.x=stepX; g.partner.y=stepY;
                g.partner.dir = g.player.dir;
                g.partner.walking = g.player.walking;
                g.partner.sprinting = false;
                String pp = tx > g.player.x ? "hold_r" : "hold_l";
                String po = tx > g.player.x ? "hold_l" : "hold_r";
                if (!pp.equals(g.player.pose)) g.player.setPose(pp, 0f);
                if (!po.equals(g.partner.pose)) g.partner.setPose(po, 0f);
                g.trail.clear();
                return;
            }
            // Koridor sempit: kembali ke follow normal sampai jalur cukup lebar.
        }
        if ("hold_l".equals(g.player.pose) || "hold_r".equals(g.player.pose)) g.player.clearPose();
        if ("hold_l".equals(g.partner.pose) || "hold_r".equals(g.partner.pose)) g.partner.clearPose();
        if (g.cine.active()) return; // cutscene mengatur posisi companion
        if (g.partnerMode != 2) { g.partner.walking = false; return; }
        float dxp = g.player.x - g.partner.x, dyp = g.player.y - g.partner.y;
        float distP = (float) Math.sqrt(dxp * dxp + dyp * dyp);
        if (distP > 260) { placeBeside(); g.trail.clear(); return; }
        if (distP < 34 || g.trail.isEmpty()) {
            g.partner.walking = false;
            if (distP < 34 && g.trail.size() > 4) g.trail.pollFirst();
            return;
        }
        float[] t = g.trail.peekFirst();
        float ex = t[0] - g.partner.x, ey = t[1] - g.partner.y;
        float d = (float) Math.sqrt(ex * ex + ey * ey);
        if (d < 3f) { g.trail.pollFirst(); return; }
        float speed = (g.player.sprinting ? g.SPRINT_SPEED : g.WALK_SPEED) * 1.05f * dt
                * ElevationV50.speedFactor(g.area.terraces, g.partner.x, g.partner.y);
        float k = Math.min(d, speed);
        float destX=g.partner.x+ex/d*k, destY=g.partner.y+ey/d*k;
        if(!g.area.blocked(destX,destY)&&ElevationV50.canStep(g.area.terraces,g.partner.x,g.partner.y,destX,destY)) {
            g.partner.x=destX;g.partner.y=destY;
        } else { g.partner.walking=false; return; }
        g.partner.face(ex, ey);
        g.partner.walking = true;
        g.partner.sprinting = g.player.sprinting;
    }
}
