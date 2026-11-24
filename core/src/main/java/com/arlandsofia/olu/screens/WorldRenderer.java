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
final class WorldRenderer {
    private final GameScreen g;
    WorldRenderer(GameScreen g) { this.g = g; }

    /** Kilau bergerak di permukaan air (kolam, danau, air mancur). */
    void drawWater() {
        for (float[] f : g.area.waterFlow)
            g.worldFx.drawFlowV54(g.game.batch, g.game.assets.pixel, f[0], g.area.h - f[1] - f[3], f[2], f[3], f[4], f[5],
                    g.time, g.game.settings.visualQuality, "rain".equals(g.weather()),
                    g.visibleL, g.visibleB, g.visibleR - g.visibleL, g.visibleT - g.visibleB);
        for (float[] r : g.area.riverPaths)
            g.worldFx.drawRiverV54(g.game.batch, g.game.assets.pixel, r, g.area.h, g.time, g.game.settings.visualQuality,
                    "rain".equals(g.weather()), g.visibleL, g.visibleB, g.visibleR - g.visibleL, g.visibleT - g.visibleB);
        if (g.area.water.isEmpty()) return;
        for (float[] w : g.area.water) {
            int visual = g.game.settings.visualQuality;
            int n = (int) Math.min(visual == 2 ? 58 : 40, w[2] * w[3] / (visual == 2 ? 660f : 900f) + (visual == 0 ? 3 : 6));
            if (visual == 0) n = Math.max(3, n / 3);
            for (int i = 0; i < n; i++) {
                float ph = g.time * 0.6f + i * 1.37f;
                float u = ((i * 0.618f) % 1f) * 2f - 1f, v = ((i * 0.377f + 0.21f) % 1f) * 2f - 1f;
                if (u * u + v * v > 0.85f) continue;
                float al = Math.max(0f, MathUtils.sin(ph * 2f)) * 0.7f;
                float wx = w[0] + u * w[2] + MathUtils.sin(ph) * 6f, wy = w[1] + v * w[3];
                g.game.batch.setColor(0.9f, 0.97f, 1f, al);
                g.game.batch.draw(g.game.assets.pixel, wx, g.area.h - wy, 6 + (i % 3) * 2, 1.5f);
            }
            g.worldFx.drawRipples(g.game.batch, w[0], g.area.h - w[1], w[2], w[3], g.time, visual, "rain".equals(g.weather()));
            g.worldFx.drawWaterGlintsV462(g.game.batch,w[0],g.area.h-w[1],w[2],w[3],g.time,visual,"rain".equals(g.weather()));
        }
        g.game.batch.setColor(1, 1, 1, 1);
    }

    /** Partikel ambient (kelopak, kunang-kunang, bintang) dan hujan, relatif terhadap kamera. */
    void drawAmbient() {
        float ww = g.worldView.getWorldWidth() * g.worldCam.zoom, wh = g.worldView.getWorldHeight() * g.worldCam.zoom;
        float left = g.worldCam.position.x - ww / 2, bottom = g.worldCam.position.y - wh / 2;
        String amb = g.area.ambient;
        float[] L = g.lightNow();
        boolean rain = "rain".equals(g.weather()) && !g.isIndoor();
        boolean night = !g.isIndoor() && L[3] > 0.18f;
        int visual = g.game.settings.visualQuality;
        if (visual > 0 && !g.isIndoor() && !g.realm()) {
            float halo = night ? (visual == 2 ? 220f : 140f) : (visual == 2 ? 250f : 165f);
            float hx = left + ww * (night ? 0.82f : 0.18f);
            float hy = bottom + wh * 0.80f;
            if (night) g.game.batch.setColor(0.72f, 0.78f, 1f, rain ? 0.12f : 0.18f);
            else g.game.batch.setColor(1f, 0.78f, 0.54f, rain ? 0.14f : 0.22f);
            g.game.batch.draw(g.glow, hx - halo / 2f, hy - halo / 2f, halo, halo);
            g.game.batch.setColor(1f, 1f, 1f, 1f);
        }
        if (amb != null && !rain) {
            for (int i = 0; i < (visual == 2 ? 28 : visual == 1 ? 18 : 8); i++) {
                float fx = ((i * 0.6180339f + g.time * (0.012f + (i % 5) * 0.004f)) % 1f) * ww;
                float fy = ((i * 0.3819f + ("petals".equals(amb) ? -g.time * 0.03f : MathUtils.sin(g.time * 0.3f + i) * 0.02f)) % 1f + 1f) % 1f * wh;
                if ("petals".equals(amb)) { g.game.batch.setColor(1f, 0.78f, 0.86f, 0.85f); g.game.batch.draw(g.game.assets.pixel, left + fx, bottom + fy, 3, 2); }
                else if ("fireflies".equals(amb)) { float al = 0.3f + 0.7f * Math.max(0, MathUtils.sin(g.time * 2 + i)); g.game.batch.setColor(1f, 0.95f, 0.55f, al); g.game.batch.draw(g.sparkle, left + fx, bottom + fy, 7, 7); }
                else { float al = 0.3f + 0.6f * Math.max(0, MathUtils.sin(g.time * 1.5f + i * 2)); g.game.batch.setColor(1f, 0.96f, 0.85f, al); g.game.batch.draw(g.sparkle, left + fx, bottom + fy, 6, 6); }
            }
        }
        if (rain) {
            int rainCount = visual == 2 ? g.rainX.length : visual == 1 ? 90 : 48;
            for (int i = 0; i < rainCount; i++) {
                float fx = ((g.rainX[i] + g.time * 0.05f) % 1f) * (ww + 60) - 30;
                float fy = ((g.rainY[i] - g.time * (1.1f + (i % 4) * 0.15f)) % 1f + 1f) % 1f * (wh + 40);
                g.game.batch.setColor(0.75f, 0.85f, 1f, 0.55f);
                g.game.batch.draw(g.game.assets.pixel, left + fx, bottom + fy, 1, 9);
            }
        }
        QuestDb.Step st = g.engine.step();
        night = L[3] >= 0.2f && !rain;
        if (!g.isIndoor() && !rain && !night && !g.realm()) { // kupu-kupu kecil di area luar siang hari
            for (int i = 0; i < (visual == 2 ? 7 : visual == 1 ? 4 : 2); i++) {
                float bx = ((i * 0.618f + MathUtils.sin(g.time * 0.11f + i) * 0.18f) % 1f + 1f) % 1f * ww;
                float by = ((i * 0.37f + MathUtils.cos(g.time * 0.09f + i * 2) * 0.15f) % 1f + 1f) % 1f * wh;
                float flap = Math.abs(MathUtils.sin(g.time * 14f + i)) * 2.2f + 0.6f;
                if (i % 2 == 0) g.game.batch.setColor(1f, 0.85f, 0.4f, 0.95f); else g.game.batch.setColor(0.95f, 0.75f, 0.95f, 0.95f);
                g.game.batch.draw(g.game.assets.pixel, left + bx - flap - 0.5f, bottom + by, flap, 2f);
                g.game.batch.draw(g.game.assets.pixel, left + bx + 0.5f, bottom + by, flap, 2f);
            }
        }
        float tintA = 0f; Color tc = null;
        if (rain || ("rain".equals(g.weather()) && g.isIndoor())) { tc = g.tint.set(0.25f, 0.3f, 0.42f, 1f); tintA = g.isIndoor() ? 0.12f : 0.28f; }
        else if (L[3] > 0.001f) { tc = g.tint.set(L[0], L[1], L[2], 1f); tintA = g.isIndoor() ? L[3] * 0.45f : L[3]; }
        if (!g.isIndoor() && !g.realm() && WorldClock.BERAWAN.equals(g.weather())) { g.game.batch.setColor(0.55f, 0.58f, 0.66f, 0.13f); g.game.batch.draw(g.game.assets.pixel, left - 10, bottom - 10, ww + 20, wh + 20); }
        if (!g.isIndoor() && !g.realm() && WorldClock.BERANGIN.equals(g.weather())) { // daun & kelopak terbawa angin
            for (int i = 0; i < (visual == 2 ? 35 : visual == 1 ? 22 : 10); i++) {
                float fx = ((i * 0.618f + g.time * (0.09f + (i % 4) * 0.02f)) % 1f) * (ww + 40) - 20;
                float fy = ((i * 0.37f + MathUtils.sin(g.time * 1.3f + i) * 0.03f) % 1f + 1f) % 1f * wh;
                if (i % 3 == 0) g.game.batch.setColor(1f, 0.78f, 0.86f, 0.9f); else g.game.batch.setColor(0.55f, 0.75f, 0.4f, 0.9f);
                g.game.batch.draw(g.game.assets.pixel, left + fx, bottom + fy, 3, 2);
            }
        }
        if (tc != null && tintA > 0) {
            g.game.batch.setColor(tc.r, tc.g, tc.b, tintA);
            g.game.batch.draw(g.game.assets.pixel, left - 10, bottom - 10, ww + 20, wh + 20);
        }
        if ("dark".equals(g.area.ambient)) { // gua: lingkar cahaya di sekitar pemain + pendar kristal
            Texture dk = g.game.assets.tex("ui/darkness.png");
            float R = 230f, px = g.player.x, py = g.area.h - g.player.y + 26;
            g.game.batch.setColor(1, 1, 1, 1);
            g.game.batch.draw(dk, px - R, py - R, R * 2, R * 2);
            g.game.batch.setColor(0.03f, 0.02f, 0.07f, 0.9f);
            g.game.batch.draw(g.game.assets.pixel, left - 10, bottom - 10, px - R - left + 10, wh + 20);
            g.game.batch.draw(g.game.assets.pixel, px + R, bottom - 10, left + ww - px - R + 10, wh + 20);
            g.game.batch.draw(g.game.assets.pixel, px - R, bottom - 10, R * 2, py - R - bottom + 10);
            g.game.batch.draw(g.game.assets.pixel, px - R, py + R, R * 2, bottom + wh - py - R + 10);
            for (MapDb.Prop pr : g.area.props) {
                if (!pr.def.image.contains("crystal")) continue;
                Texture t = g.game.assets.tex(pr.def.image);
                float s = 70 + MathUtils.sin(g.time * 1.6f + pr.x) * 6f;
                g.game.batch.setColor(0.7f, 0.85f, 1f, 0.5f);
                g.game.batch.draw(g.sparkle, pr.x - s / 2, g.area.h - pr.y + t.getHeight() / 2f - s / 2, s, s);
            }
            g.game.batch.setColor(1, 1, 1, 1);
        }
        if (night || rain || g.realm()) { // lampu jalan & lentera berpendar saat malam/hujan
            for (MapDb.Prop pr : g.area.props) {
                String img = (pr.alt != null && pr.altFlag != null && g.p.hasFlag(pr.altFlag) ? pr.alt : pr.def).image;
                if (!(img.contains("lamp") || img.contains("lantern_post") || img.contains("lantern_on"))) continue;
                Texture t = g.game.assets.tex(img);
                float gx = pr.x, gy = g.area.h - pr.y + t.getHeight() - 6;
                if (gx < left - 60 || gx > left + ww + 60 || gy < bottom - 60 || gy > bottom + wh + 60) continue;
                float s = 46 + MathUtils.sin(g.time * 2f + pr.x) * 3f;
                g.game.batch.setColor(1f, 0.85f, 0.55f, 0.45f);
                g.game.batch.draw(g.sparkle, gx - s / 2, gy - s / 2, s, s);
            }
        }
        g.game.batch.setColor(1, 1, 1, 1);
    }

    /** Platform PNG covers a pixel-art deck, retaining wall, and traversable stairs. */
    void drawTerraceBase(MapDb.Terrace t){
        float x=t.x-20f, y=g.area.h-(t.y-40f+t.h+t.stairLength+64f);
        float w=t.w+40f, h=t.h+t.stairLength+64f;
        if(x>g.visibleR||x+w<g.visibleL||y>g.visibleT||y+h<g.visibleB)return;
        g.game.batch.setColor(1f,1f,1f,1f);
        g.game.batch.draw(g.game.assets.tex(t.image),x,y,w,h);
    }

    /** Foreground lip participates in world Y-sort for convincing edge overlap. */
    void drawTerraceFront(MapDb.Terrace t){
        float x=t.x-20f, y=g.area.h-(t.y-40f+t.h+t.stairLength+64f);
        float w=t.w+40f,h=t.h+t.stairLength+64f;
        if(x>g.visibleR||x+w<g.visibleL||y>g.visibleT||y+h<g.visibleB)return;
        g.game.batch.setColor(1f,1f,1f,1f);
        g.game.batch.draw(g.game.assets.tex(t.front),x,y,w,h);
    }

    /** Lightweight VFX on terraces; respects visualQuality and time/weather. */
    void drawTerraceAtmosphere(){
        if(g.game.settings.visualQuality==0||g.area.terraces.isEmpty())return;
        for(MapDb.Terrace t:g.area.terraces){
            float cx=t.x+t.w*.5f, cy=g.area.h-t.y-t.h*.45f+t.rise;
            if(!g.visibleActor(cx,t.y+t.h*.5f))continue;
            boolean magic="memory".equals(t.style)||"star".equals(t.style)||"crystal".equals(t.style)
                    ||"night".equals(t.style)||"future".equals(t.style);
            boolean night=WorldClock.isNight(g.p.minute);
            if(!magic && !night)continue;
            int count=g.game.settings.visualQuality>1?11:5;
            for(int i=0;i<count;i++){
                float sx=cx+MathUtils.sin(i*12.71f+g.time*.36f)*(t.w*.46f);
                float sy=cy+MathUtils.cos(i*7.37f+g.time*.48f)*(t.h*.40f)+MathUtils.sin(g.time*.92f+i)*7f;
                float alpha=.13f+.20f*(.5f+.5f*MathUtils.sin(g.time*1.4f+i*2.9f));
                g.game.batch.setColor(magic ? .84f : 1f,magic ? .78f : .86f,1f,alpha);
                g.game.batch.draw(g.sparkle,sx-2f,sy-2f,4.5f,4.5f);
            }
        }
        g.game.batch.setColor(1f,1f,1f,1f);
    }

    void drawProp(MapDb.Prop pr) {
        MapDb.PropDef def = pr.alt != null && pr.altFlag != null && g.p.hasFlag(pr.altFlag) ? pr.alt : pr.def;
        Texture t = g.game.assets.tex(def.image);
        float propX = pr.x - t.getWidth() / 2f, propY = g.area.h - pr.y;
        if (propX > g.visibleR || propX + t.getWidth() < g.visibleL || propY > g.visibleT || propY + t.getHeight() < g.visibleB) return;
        // v3.7: local ground-contact shadow follows identical Y-sort as the prop;
        // stays underneath its sprite, and never modifies collision or quest geometry.
        if (g.game.settings.visualQuality > 0 && !"floor".equals(def.layer)
                && def.cw >= 8f && def.ch > 0f) {
            float ww = WorldLightingV37.width(def.cw);
            float sx = WorldLightingV37.shadowOffsetX(g.p.minute, g.isIndoor(), "rain".equals(g.weather()), g.game.settings.visualQuality);
            float opacity = WorldLightingV37.contactOpacity(g.p.minute, g.isIndoor(), "rain".equals(g.weather()), g.game.settings.visualQuality);
            g.game.batch.setColor(1f, 1f, 1f, opacity);
            g.game.batch.draw(g.shadow, Math.round(pr.x + sx - ww * 0.5f),
                    Math.round(g.area.h - pr.y - 7f), ww, 14f);
            g.game.batch.setColor(1f, 1f, 1f, 1f);
        }
        String img = def.image;
        boolean lamp = img.contains("lamp") || img.contains("lantern");
        boolean crystal = img.contains("crystal");
        boolean warmWindow = img.contains("window") || img.contains("campfire") || img.contains("fire");
        boolean glowAllowed = g.game.settings.visualQuality > 0 &&
                (crystal || (lamp && (g.isIndoor() || g.realm() || WorldClock.isNight(g.p.minute) || "rain".equals(g.weather())))
                    || (warmWindow && (g.isIndoor() || WorldClock.isNight(g.p.minute))));
        if (glowAllowed) {
            float cx = pr.x;
            float cy = g.area.h - pr.y + t.getHeight() * (lamp ? 0.78f : 0.55f);
            float s = (lamp ? 92f : crystal ? 84f : 70f) * (g.game.settings.visualQuality == 2 ? 1.15f : 0.85f);
            float strength = g.game.settings.visualQuality == 2 ? 1f : 0.6f;
            if (lamp) g.game.batch.setColor(1f, 0.84f, 0.56f, 0.34f * strength);
            else if (crystal) g.game.batch.setColor(0.72f, 0.88f, 1f, 0.30f * strength);
            else g.game.batch.setColor(1f, 0.90f, 0.72f, 0.20f * strength);
            g.game.batch.draw(g.glow, cx - s / 2f, cy - s / 2f, s, s);
            g.game.batch.setColor(1, 1, 1, 1);
        }
        // High-quality animation: move only the upper third of a tree (the roots/trunk
        // remain fixed and collision unchanged). TextureRegions are cached once per texture.
        if (g.game.settings.visualQuality == 2 && (img.contains("/tree_") || img.contains("/wishing_tree"))
                && t.getHeight() >= 60 && !"floor".equals(def.layer)) {
            TextureRegion[] split = g.animatedTreeRegions.get(t);
            if (split == null) {
                int th = Math.max(12, t.getHeight() / 3);
                split = new TextureRegion[]{new TextureRegion(t, 0, th, t.getWidth(), t.getHeight()-th),
                        new TextureRegion(t, 0, 0, t.getWidth(), th)};
                g.animatedTreeRegions.put(t, split);
            }
            float sway = MathUtils.sin(g.time * 1.05f + pr.x * 0.013f + pr.y * 0.009f) * 2.0f;
            float x = Math.round(pr.x - t.getWidth() / 2f), y = Math.round(g.area.h - pr.y);
            int bottomH = split[0].getRegionHeight();
            g.game.batch.draw(split[0], x, y, t.getWidth(), bottomH);
            g.game.batch.draw(split[1], x + sway, y + bottomH, t.getWidth(), split[1].getRegionHeight());
        } else {
            g.game.batch.draw(t, Math.round(pr.x - t.getWidth() / 2f), Math.round(g.area.h - pr.y), t.getWidth(), t.getHeight());
        }
        if (WorldFx.animatedWater(img)) // v5.4: fountains and waterfalls actually move
            g.worldFx.drawPropWaterV54(g.game.batch, g.game.assets.pixel, img, Math.round(pr.x - t.getWidth() / 2f),
                    Math.round(g.area.h - pr.y) + t.getHeight(), g.time, g.game.settings.visualQuality);
    }

    void drawEmote(Actor a) {
        if (a.emote == null) return;
        Texture t = g.game.assets.tex("ui/emote_" + a.emote + ".png");
        float pop = Math.min(1f, (1.8f - a.emoteTime) * 6f);
        g.game.batch.draw(t, a.x - 11, g.area.h - a.y + a.terrainLift + a.drawHeight() + 2, 22 * pop, 22 * pop);
    }

    
    void drawWorld() {
        float zoom = g.cine.camActive() ? Math.max(0.5f, g.cine.zoom()) : 1f;
        // Wider world view only during free exploration; scripted cinematics retain their zoom.
        float framing = g.cine.camActive() ? 1f : CameraFramingV52.gameplayScale(g.game.settings.cameraDistance, g.area.indoor);
        // v5.4: exploration snaps to a whole number of screen pixels per texel.
        int pixelGrid = 0;
        if (!g.cine.camActive() && g.game.settings.pixelPerfect && g.worldView.getScreenHeight() > 0) {
            pixelGrid = PixelPerfectV54.pixelsPerUnit(framing, g.worldView.getWorldHeight(), g.worldView.getScreenHeight());
            framing = PixelPerfectV54.zoom(framing, g.worldView.getWorldHeight(), g.worldView.getScreenHeight());
        }
        g.worldCam.zoom = framing / zoom;
        float ww = g.worldView.getWorldWidth() * framing / zoom;
        float wh = g.worldView.getWorldHeight() * framing / zoom;
        boolean inCutsceneCamera = g.cine.camActive();
        float focusX = inCutsceneCamera ? g.cine.camX() : g.player.x;
        float focusY = inCutsceneCamera ? g.area.h - g.cine.camY() : g.area.h - g.player.y + 24 + g.lastTerrainHeight*.55f;
        // Look-ahead kecil hanya saat eksplorasi, tidak merusak komposisi cutscene.
        if (!inCutsceneCamera && g.player.walking && g.game.settings.smoothCamera) {
            if (g.player.dir == Assets.DIR_LEFT) focusX -= 12f;
            if (g.player.dir == Assets.DIR_RIGHT) focusX += 12f;
            if (g.player.dir == Assets.DIR_UP) focusY += 8f;
            if (g.player.dir == Assets.DIR_DOWN) focusY -= 8f;
        }
        float cx = g.area.w <= ww ? g.area.w / 2 : MathUtils.clamp(focusX, ww / 2, g.area.w - ww / 2);
        float cy = g.area.h <= wh ? g.area.h / 2 : MathUtils.clamp(focusY, wh / 2, g.area.h - wh / 2);
        g.cameraRig.follow(cx, cy, g.frameDt, !inCutsceneCamera && g.game.settings.smoothCamera);
        float smoothX = g.area.w <= ww ? g.area.w / 2 : MathUtils.clamp(g.cameraRig.x(), ww / 2, g.area.w - ww / 2);
        float smoothY = g.area.h <= wh ? g.area.h / 2 : MathUtils.clamp(g.cameraRig.y(), wh / 2, g.area.h - wh / 2);
        if (pixelGrid > 0) g.worldCam.position.set(PixelPerfectV54.snap(smoothX, pixelGrid), PixelPerfectV54.snap(smoothY, pixelGrid), 0);
        else g.worldCam.position.set(zoom == 1f ? Math.round(smoothX) : smoothX, zoom == 1f ? Math.round(smoothY) : smoothY, 0);
        g.visibleL = g.worldCam.position.x - ww / 2 - 110;
        g.visibleR = g.worldCam.position.x + ww / 2 + 110;
        g.visibleB = g.worldCam.position.y - wh / 2 - 110;
        g.visibleT = g.worldCam.position.y + wh / 2 + 110;
        g.worldView.apply();
        g.worldCam.update();
        g.game.batch.setProjectionMatrix(g.worldCam.combined);
        g.game.batch.begin();
        g.game.batch.setColor(1, 1, 1, 1);
        g.game.batch.draw(g.mapTex, 0, 0, g.area.w, g.area.h);
        g.worldFx.drawSceneAtmosphere(g.game.batch, g.game.assets.pixel, g.glow, g.sparkle,
                g.area.id, g.area.indoor, g.area.h, g.worldCam.position.x, g.worldCam.position.y,
                ww, wh, g.time, g.game.settings.visualQuality, WorldClock.isNight(g.p.minute));
        g.worldFx.drawWorldBackdropV462(g.game.batch,g.area.id,g.area.indoor,
                "rain".equals(g.weather()),g.p.minute,g.worldCam.position.x,g.worldCam.position.y,
                ww,wh,g.time,g.game.settings.visualQuality);
        for (MapDb.Prop pr : g.area.props) if ("floor".equals(pr.def.layer) && g.propVisible(pr)) g.worldRenderer.drawProp(pr);
        // v5.0: original 2.5D decks and real stairs overlay map art without
        // mutating the baked backgrounds or old story/door coordinates.
        for(MapDb.Terrace terrace:g.area.terraces)g.worldRenderer.drawTerraceBase(terrace);
        // v3.7: riak dan kilau air berada pada lapisan lantai; sebelum karakter/prop.
        g.worldRenderer.drawWater();
        g.worldFx.drawPuddlesV54(g.game.batch, g.puddles, g.area.h, g.wetness, "rain".equals(g.weather()) && !g.isIndoor(),
                g.time, g.game.settings.visualQuality, g.storm.flashAlpha(g.game.settings.visualQuality),
                g.visibleL, g.visibleB, g.visibleR - g.visibleL, g.visibleT - g.visibleB);

        g.drawList.clear(); g.drawCursor = 0;
        for (MapDb.Prop pr : g.area.props) if (!"floor".equals(pr.def.layer) && g.propVisible(pr)) g.addDraw(pr.y, pr);
        g.drawMarkers.clear();
        g.drawMarkers.addAll(g.engine.interactables(g.area.id));
        List<QuestDb.Interactable> its = g.drawMarkers;
        List<QuestDb.Interactable> sides = g.engine.sideInteractables(g.area.id);
        for (QuestDb.Interactable it : its) if (it.sprite != null && g.visibleActor(it.sprite.x, it.sprite.y)) g.addDraw(it.sprite.y, it.sprite);
        for (QuestDb.Interactable it : sides) if (it.sprite != null && g.visibleActor(it.sprite.x, it.sprite.y)) g.addDraw(it.sprite.y, it.sprite);
        for(MapDb.Terrace t:g.area.terraces) g.addDraw(t.y+t.h-1f,t); // front lip occludes upper feet
        g.player.terrainLift=ElevationV50.heightAt(g.area.terraces,g.player.x,g.player.y);
        g.addDraw(g.player.y, g.player);
        if (g.partnerMode != 0 || g.cineShowPartner) {
            g.partner.terrainLift=ElevationV50.heightAt(g.area.terraces,g.partner.x,g.partner.y);
            g.addDraw(g.partner.y, g.partner);
        }
        for (Actor ac : g.townActors.values()) if (g.visibleActor(ac.x,ac.y)) {
            ac.terrainLift=ElevationV50.heightAt(g.area.terraces,ac.x,ac.y);
            g.addDraw(ac.y, ac);
        }
        for (Actor ac : g.cineActors.values()) if (g.visibleActor(ac.x,ac.y)) {
            ac.terrainLift=ElevationV50.heightAt(g.area.terraces,ac.x,ac.y);
            g.addDraw(ac.y, ac);
        }
        for (Animal an : g.animals) if (g.visibleActor(an.x,an.y)) g.addDraw(an.y, an);
        for (QuestDb.Interactable it : sides) if (it.marker) its.add(it);
        Collections.sort(g.drawList, g.bySortY);
        for (GameScreen.DrawItem o : g.drawList) {
            Object r = o.value;
            if (r instanceof MapDb.Terrace) g.worldRenderer.drawTerraceFront((MapDb.Terrace)r);
            else if (r instanceof MapDb.Prop) g.worldRenderer.drawProp((MapDb.Prop) r);
            else if (r instanceof QuestDb.Sprite) {
                QuestDb.Sprite s = (QuestDb.Sprite) r;
                Texture t = g.game.assets.tex(s.image);
                float bob = s.bob ? MathUtils.sin(g.time * 3f + s.x) * 3f : 0f;
                g.game.batch.draw(t, Math.round(s.x - t.getWidth() / 2f), Math.round(g.area.h - s.y + bob), t.getWidth(), t.getHeight());
            } else if (r instanceof Animal) ((Animal) r).draw(g.game.batch, g.game.assets, g.area.h, g.shadow);
            else ((Actor) r).draw(g.game.batch, g.game.assets, g.area.h, g.shadow);
        }

        g.worldFx.draw(g.game.batch, g.game.settings.visualQuality);
        if (g.realm()) { // partikel cahaya Memory Realm
            for (int i = 0; i < 26; i++) {
                float sx = (i * 211.3f + g.time * 9f * (1 + i % 3)) % g.area.w;
                float sy = (i * 137.9f + g.time * 14f) % g.area.h;
                float al = 0.35f + 0.35f * MathUtils.sin(g.time * 2f + i);
                g.game.batch.setColor(1f, 0.93f, 0.75f, al);
                g.game.batch.draw(g.sparkle, sx, sy, 9, 9);
            }
            g.game.batch.setColor(1, 1, 1, 1);
        }

        if (g.game.settings.showHints) {
            for (QuestDb.Interactable it : its) {
                float my;
                if (it.sprite != null) my = it.sprite.y - g.game.assets.tex(it.sprite.image).getHeight() - 8;
                else if (g.partnerMode == 1 && Math.abs(g.partner.x - it.x) < 20 && Math.abs(g.partner.y - it.y) < 20) my = g.partner.y - g.partner.drawHeight() - 8;
                else my = it.y - 40;
                float bob = MathUtils.sin(g.time * 4f + it.x) * 3f;
                boolean gold = it.id.startsWith("shard") || it.id.startsWith("WE27_") || it.id.startsWith("V50_");
                if (gold) g.game.batch.setColor(1f, 0.85f, 0.45f, 1f); else g.game.batch.setColor(0.97f, 0.7f, 0.83f, 1f);
                g.game.batch.draw(g.marker, it.x - 7, g.area.h - my + bob, 14, 14);
            }
            g.game.batch.setColor(1, 1, 1, 1);
        }
        g.worldRenderer.drawEmote(g.player);
        if (g.partnerMode != 0 || g.cineShowPartner) g.worldRenderer.drawEmote(g.partner);
        for (Actor ac : g.townActors.values()) g.worldRenderer.drawEmote(ac);
        for (Actor ac : g.cineActors.values()) g.worldRenderer.drawEmote(ac);
        if (g.partnerMode == 2 && g.partner.emote == null && g.engine.partnerTalk(g.area.id) != null && g.game.settings.showHints) {
            Texture ht = g.game.assets.tex("ui/emote_heart.png");
            float bob = MathUtils.sin(g.time * 3f) * 2f;
            g.game.batch.setColor(1, 1, 1, 0.75f);
            g.game.batch.draw(ht, g.partner.x - 8, g.area.h - g.partner.y + g.partner.drawHeight() + 2 + bob, 16, 16);
            g.game.batch.setColor(1, 1, 1, 1);
        }
        g.worldRenderer.drawTerraceAtmosphere();
        g.worldRenderer.drawAmbient();
        {
            float vw = g.worldView.getWorldWidth() * g.worldCam.zoom, vh = g.worldView.getWorldHeight() * g.worldCam.zoom;
            float left = g.worldCam.position.x - vw / 2, bottom = g.worldCam.position.y - vh / 2;
            g.worldFx.drawForeground(g.game.batch, left, bottom, vw, vh, g.area.ambient, g.time, g.game.settings.visualQuality);
            g.worldFx.drawWorldForegroundV462(g.game.batch,g.area.id,g.area.indoor,
                    "rain".equals(g.weather()),WorldClock.BERANGIN.equals(g.weather()),g.p.minute,
                    g.worldCam.position.x,g.worldCam.position.y,vw,vh,g.time,g.game.settings.visualQuality);
            g.worldFx.drawLightningV54(g.game.batch, g.game.assets.pixel, left, bottom, vw, vh,
                    g.storm.flashAlpha(g.game.settings.visualQuality));
            g.worldFx.drawVignette(g.game.batch, left, bottom, vw, vh, g.game.settings.visualQuality);
            g.cine.drawWorld(g.game.batch, g.area.h, left, bottom, vw, vh);
        }
        g.game.batch.end();
    }
}
