package com.arlandsofia.olu.game;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.logic.Json;
import com.arlandsofia.olu.logic.CinematicMotionV463;
import com.arlandsofia.olu.ui.Ui;
import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.math.MathUtils;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

/**
 * Pemutar cutscene sinematik berbasis data. Perintah dijalankan berurutan; perintah yang memakan waktu
 * (move, cam, wait, say, line, fade, caption) menunggu selesai kecuali diberi "async": true.
 *
 * Perintah ("c"): wait, move, place, face, pose, emote, cam, follow, bars, fade, flash, tint, shake, fx,
 * say, line, caption, sfx, music, spawn, despawn, show, hide, alpha.
 * Aktor: "player", "partner", id NPC kota, atau id aktor sementara dari "spawn".
 */
public final class CutscenePlayer {

    public interface Host {
        Actor actor(String who);
        Actor spawn(String id, String sprite, float x, float y, int dir);
        void despawn(String id);
        void showPartner(boolean on);
        void say(String sceneId, int from, int n, Runnable done);
        void line(String speaker, String emotion, String text, Runnable done);
        void sfx(String id);
        void music(String id);
        /** pusat kamera saat ini (koordinat peta, y ke bawah) */
        float camX();
        float camY();
        /** Titik kaki untuk pasangan yang diatur pose bersama (hindari tembok). */
        boolean canStand(float x, float y);
    }

    private static final class Mover { Actor a; float[][] path; int idx; float speed; int endDir = -1; boolean run; }
    private static final class Fx { String kind; float x, y, t, dur; int n; float seed; }

    private final Host host;
    private final Assets assets;
    private final Texture cinematicBloom, captionRibbon, sceneOrnament;
    private final ArrayDeque<Map<String, Object>> queue = new ArrayDeque<>();
    private final List<Mover> movers = new ArrayList<>();
    private final List<Fx> fxs = new ArrayList<>();
    private Runnable done;
    private boolean active, waitingCallback;
    private float waitT;          // sisa waktu tunggu
    private Mover waitMover;      // tunggu aktor ini sampai
    public boolean fast;          // tahan layar = percepat (x3)

    // kamera
    private boolean camActive; private float camX, camY, camZoom = 1f;
    private float cx0, cy0, z0, cx1, cy1, z1, camT, camDur; private Actor camFollow;
    // layar
    private float bars, barsTarget, barsSpeed = 2f;
    private float fade, fade0, fade1, fadeT, fadeDur; private final Color fadeColor = new Color(0, 0, 0, 1);
    private float flash, flashDur; private final Color flashColor = new Color(1, 1, 1, 1);
    private float tintA, tintA0, tintA1, tintT, tintDur; private final Color tintColor = new Color(0, 0, 0, 1);
    private float shakeT, shakeAmp;
    private String capTitle, capSub, capArt; private float capT, capDur;
    private float time;
    private final List<String> spawned = new ArrayList<>();

    public CutscenePlayer(Host host, Assets assets) {
        this.host = host; this.assets = assets;
        cinematicBloom = assets.uiTex("ui/v32_bloom.png");
        captionRibbon = assets.uiTex("ui/v32_cinematic_ribbon.png");
        sceneOrnament = assets.uiTex("ui/v32_scene_ornament.png");
    }

    public boolean active() { return active; }

    public void start(List<Map<String, Object>> cmds, Runnable done) {
        queue.clear(); queue.addAll(cmds); movers.clear(); fxs.clear(); spawned.clear();
        this.done = done; active = true; waitingCallback = false; waitT = 0; waitMover = null; fast = false;
        camActive = true; camX = host.camX(); camY = host.camY(); camZoom = 1f; camDur = 0; camFollow = null;
        barsTarget = 1f; tintA = 0; tintDur = 0; fade = 0; fadeDur = 0; capDur = 0; shakeT = 0;
        pump();
    }

    // ------------------------------------------------------------------ eksekusi
    private void pump() {
        while (active && !waitingCallback && waitT <= 0 && waitMover == null && !(camDur > 0 && !asyncCam) && !(fadeDur > 0 && !asyncFade) && !(capDur > 0 && !asyncCap)) {
            Map<String, Object> c = queue.poll();
            if (c == null) { finish(); return; }
            exec(c);
        }
    }

    private Actor who(Map<String, Object> c) { return host.actor(Json.str(c, "who", "player")); }

    private static float[] pt(Object o) {
        if (!(o instanceof List)) return null;
        List<?> l = (List<?>) o;
        if (l.size() < 2 || !(l.get(0) instanceof Number) || !(l.get(1) instanceof Number)) return null;
        return new float[]{((Number) l.get(0)).floatValue(), ((Number) l.get(1)).floatValue()};
    }

    private void exec(final Map<String, Object> c) {
        String k = Json.str(c, "c", "");
        boolean async = Json.bool(c, "async", false);
        switch (k) {
            case "wait": waitT = Json.num(c, "t", 0.5f); break;
            case "move": {
                Actor a = who(c); if (a == null) break;
                List<float[]> pts = new ArrayList<>();
                if (c.get("to") != null) { float[] point=pt(c.get("to")); if(point!=null) pts.add(point); }
                for (Object o : Json.list(c, "path")) { float[] point=pt(o); if(point!=null) pts.add(point); }
                if (pts.isEmpty()) break;
                for (Iterator<Mover> it = movers.iterator(); it.hasNext(); ) if (it.next().a == a) it.remove();
                Mover m = new Mover(); m.a = a; m.path = pts.toArray(new float[0][]); m.run = Json.bool(c, "run", false);
                m.speed = CinematicMotionV463.clamp(Json.num(c, "speed", m.run ? 150f : 78f), 12f, 350f);
                if (c.get("dir") != null) m.endDir = Actor.dirOf(Json.str(c, "dir", "down"));
                a.clearPose(); movers.add(m);
                if (!async) waitMover = m;
                break;
            }
            case "place": {
                Actor a = who(c); if (a == null) break;
                a.x = Json.num(c, "x", a.x); a.y = Json.num(c, "y", a.y);
                if (c.get("dir") != null) a.dir = Actor.dirOf(Json.str(c, "dir", "down"));
                a.visible = true;
                if ("partner".equals(Json.str(c, "who", ""))) host.showPartner(true);
                break;
            }
            case "face": {
                Actor a = who(c); if (a == null) break;
                if (c.get("at") != null) a.faceTo(host.actor(Json.str(c, "at", "")));
                else a.dir = Actor.dirOf(Json.str(c, "dir", "down"));
                break;
            }
            case "pair": {
                // Aksi pasangan ditempatkan berdekatan sekali, kedua pose dimulai pada frame yang sama.
                Actor pl = host.actor("player"), other = host.actor("partner");
                if (pl == null || other == null) break;
                String kind = Json.str(c, "kind", "highfive");
                float gap = "hug".equals(kind) ? 21f : "lean".equals(kind) ? 25f : "photo".equals(kind) ? 24f : 32f;
                float tx = pl.x + gap, ty = pl.y;
                if (!host.canStand(tx, ty)) { tx = pl.x - gap; }
                if (host.canStand(tx, ty)) { other.x = tx; other.y = ty; }
                boolean left = other.x < pl.x;
                if ("photo".equals(kind) || "lean".equals(kind)) { pl.dir = Assets.DIR_DOWN; other.dir = Assets.DIR_DOWN; }
                else { pl.dir = left ? Assets.DIR_LEFT : Assets.DIR_RIGHT; other.dir = left ? Assets.DIR_RIGHT : Assets.DIR_LEFT; }
                String pp, op;
                if ("hug".equals(kind)) { pp = "hug"; op = "hug"; }
                else if ("lean".equals(kind)) { pp = "sit"; op = "lean"; }
                else if ("photo".equals(kind)) { pp = "photo"; op = "cheer"; }
                else if ("dance".equals(kind)) { pp = "dance"; op = "dance"; }
                else if ("handwalk".equals(kind)) { pp = left ? "hold_l" : "hold_r"; op = left ? "hold_r" : "hold_l"; }
                else { pp = "highfive"; op = "highfive"; }
                float dur = Math.max(0.3f, Json.num(c, "t", 1.8f));
                pl.setPose(pp, dur); other.setPose(op, dur);
                pl.showEmote("heart", 1.4f); other.showEmote("heart", 1.4f);
                if (Json.bool(c, "block", true)) waitT = dur;
                break;
            }
            case "pose": {
                Actor a = who(c); if (a == null) break;
                String p = Json.str(c, "pose", null);
                if (p == null || p.equals("none")) a.clearPose(); else a.setPose(p, Json.num(c, "t", 0f));
                if (Json.bool(c, "block", false)) waitT = Json.num(c, "t", 0.6f);
                break;
            }
            case "emote": { Actor a = who(c); if (a != null) a.showEmote(Json.str(c, "e", "heart"), Json.num(c, "t", 1.8f)); break; }
            case "cam": {
                cx0 = camX; cy0 = camY; z0 = camZoom; camFollow = null;
                Actor on = c.get("on") != null ? host.actor(Json.str(c, "on", "")) : null;
                cx1 = on != null ? on.x : Json.num(c, "x", camX); cy1 = on != null ? on.y - 24 : Json.num(c, "y", camY);
                z1 = CinematicMotionV463.safeZoom(Json.num(c, "zoom", camZoom));
                float t = CinematicMotionV463.clamp(Json.num(c, "t", 1f), 0f, 8f);
                if (t <= 0) { camX = cx1; camY = cy1; camZoom = z1; camDur = 0f; asyncCam = false; }
                else { camT = 0; camDur = t; asyncCam = async; }
                break;
            }
            case "shot": {
                // v4.6.3: art-directed camera framing without modifying actors or story flags.
                Actor pl=host.actor("player"), partner=host.actor("partner");
                String frame=Json.str(c,"frame","intimate");
                String target=Json.str(c,"focus","couple");
                Actor single="partner".equals(target)?partner:pl;
                if("couple".equals(target) && pl!=null && partner!=null && partner.visible) {
                    cx1=CinematicMotionV463.midpoint(pl.x,partner.x);
                    cy1=CinematicMotionV463.midpoint(pl.y,partner.y)-30f;
                } else if(single!=null) { cx1=single.x; cy1=single.y-28f; }
                else break;
                cx0=camX;cy0=camY;z0=camZoom;camFollow=null;camActive=true;
                z1=CinematicMotionV463.safeZoom(Json.num(c,"zoom",CinematicMotionV463.presetZoom(frame)));
                float duration=CinematicMotionV463.clamp(Json.num(c,"t",.9f),0f,5f);
                if(Json.bool(c,"bars",true)) barsTarget=1f;
                if(duration<=0f) {camX=cx1;camY=cy1;camZoom=z1;camDur=0f;asyncCam=false;}
                else {camT=0f;camDur=duration;asyncCam=async;}
                break;
            }
            case "follow": camFollow = host.actor(Json.str(c, "who", "player")); camDur = 0; asyncCam = false; break;
            case "bars": barsTarget = Json.bool(c, "on", true) ? 1f : 0f; barsSpeed = 1f / Math.max(0.05f, Json.num(c, "t", 0.5f)); break;
            case "fade": {
                fade0 = fade; fade1 = CinematicMotionV463.clamp(Json.num(c, "to", 1f),0f,1f);
                fadeT = 0; fadeDur = CinematicMotionV463.clamp(Json.num(c, "t", 0.6f),0.01f,6f);
                fadeColor.set(Color.valueOf(Json.str(c, "color", "000000")));
                asyncFade = async;
                break;
            }
            case "flash": flashDur = Json.num(c, "t", 0.5f); flash = flashDur; flashColor.set(Color.valueOf(Json.str(c, "color", "ffffff"))); break;
            case "tint": {
                tintA0 = tintA; tintA1 = Json.num(c, "a", 0.3f); tintT = 0; tintDur = Math.max(0.01f, Json.num(c, "t", 1f));
                if (tintA0 <= 0.001f || c.get("color") != null) tintColor.set(Color.valueOf(Json.str(c, "color", "1b2350")));
                break;
            }
            case "shake": shakeT = Json.num(c, "t", 0.4f); shakeAmp = Json.num(c, "amp", 3f); break;
            case "fx": {
                Fx f = new Fx(); f.kind = Json.str(c, "kind", "sparkles");
                f.dur = CinematicMotionV463.clamp(Json.num(c, "t", 2f), .1f, 16f);
                f.n = Math.max(1,Math.min(80,(int) Json.num(c, "n", 24)));
                Actor on = c.get("on") != null ? host.actor(Json.str(c, "on", "")) : null;
                f.x = on != null ? on.x : Json.num(c, "x", camX); f.y = on != null ? on.y - 30 : Json.num(c, "y", camY);
                f.seed = MathUtils.random(0f, 100f);
                fxs.add(f);
                if ("lanterns".equals(f.kind)) host.sfx("lantern");
                else if ("restore".equals(f.kind)) host.sfx("quest_complete");
                else if ("hearts".equals(f.kind)) host.sfx("heart");
                if (Json.bool(c, "block", false)) waitT = f.dur;
                break;
            }
            case "say": {
                waitingCallback = true;
                host.say(Json.str(c, "scene", ""), (int) Json.num(c, "from", 0), (int) Json.num(c, "n", 0), new Runnable() { public void run() { waitingCallback = false; } });
                break;
            }
            case "line": {
                waitingCallback = true;
                host.line(Json.str(c, "s", "narrator"), Json.str(c, "e", "neutral"), Json.str(c, "t", ""), new Runnable() { public void run() { waitingCallback = false; } });
                break;
            }
            case "caption": capTitle = Json.str(c, "text", ""); capSub = Json.str(c, "sub", null);
                capArt = captionArt(capTitle, capSub);
                capT = 0; capDur = CinematicMotionV463.clamp(Json.num(c, "t", 2.6f),.1f,12f); asyncCap = async; break;
            case "sfx": host.sfx(Json.str(c, "id", "sparkle")); break;
            case "music": host.music(Json.str(c, "id", "town")); break;
            case "spawn": {
                String id = Json.str(c, "id", "extra");
                host.spawn(id, Json.str(c, "sprite", id), Json.num(c, "x", 0), Json.num(c, "y", 0), Actor.dirOf(Json.str(c, "dir", "down")));
                spawned.add(id);
                break;
            }
            case "despawn": host.despawn(Json.str(c, "id", "")); spawned.remove(Json.str(c, "id", "")); break;
            case "show": { Actor a = who(c); if (a != null) { a.visible = true; a.alpha = 1f; } if ("partner".equals(Json.str(c, "who", ""))) host.showPartner(true); break; }
            case "hide": { Actor a = who(c); if (a != null) a.visible = false; if ("partner".equals(Json.str(c, "who", ""))) host.showPartner(false); break; }
            case "alpha": { Actor a = who(c); if (a != null) { a.alpha = Json.num(c, "a", 1f); a.visible = true; } break; }
            default: break; // perintah tak dikenal dilewati (divalidasi oleh LogicSelfTest)
        }
    }
    private boolean asyncCam, asyncFade, asyncCap;

    private void finish() {
        active = false; barsTarget = 0f; tintDur = 0;
        camDur=0; asyncCam=false; waitMover=null; waitT=0; waitingCallback=false;
        for (String id : spawned) host.despawn(id);
        spawned.clear();
        for (Mover m : movers) m.a.walking = false;
        movers.clear();
        Runnable d = done; done = null;
        if (d != null) d.run();
    }

    // ------------------------------------------------------------------ update
    public void update(float rawDt) {
        float dt = CinematicMotionV463.clamp(rawDt,0f,.05f) * (fast && !waitingCallback ? 3f : 1f);
        time += dt;
        // efek layar tetap meluruh setelah cutscene selesai
        bars += Math.signum(barsTarget - bars) * Math.min(Math.abs(barsTarget - bars), dt * barsSpeed);
        if (flash > 0) flash -= dt;
        if (shakeT > 0) shakeT -= dt;
        if (!active) {
            if (camActive) { // kembalikan kamera ke pemain dengan halus
                Actor pl = host.actor("player");
                float tx = pl.x, ty = pl.y - 24;
                float smooth=CinematicMotionV463.damp(5f,dt);
                camX += (tx-camX)*smooth; camY += (ty-camY)*smooth;
                camZoom += (1f-camZoom)*smooth;
                if (Math.abs(tx - camX) < 1f && Math.abs(ty - camY) < 1f && Math.abs(camZoom - 1f) < 0.01f) camActive = false;
            }
            if (tintA > 0) tintA = Math.max(0, tintA - dt * 0.8f);
            if (fade > 0 && fadeDur <= 0) fade = Math.max(0, fade - dt * 2f);
            for (Iterator<Fx> it = fxs.iterator(); it.hasNext(); ) { Fx f = it.next(); f.t += dt; if (f.t > f.dur) it.remove(); }
            return;
        }
        // kamera
        if (camDur > 0) {
            camT += dt; float k = CinematicMotionV463.progress(camT,camDur);
            float e = CinematicMotionV463.ease(k);
            camX = CinematicMotionV463.lerp(cx0,cx1,e);
            camY = CinematicMotionV463.lerp(cy0,cy1,e);
            camZoom = CinematicMotionV463.safeZoom(CinematicMotionV463.lerp(z0,z1,e));
            if (k >= 1f) { camDur = 0; asyncCam = false; }
        } else if (camFollow != null) {
            float smooth=CinematicMotionV463.damp(4f,dt);
            camX+=(camFollow.x-camX)*smooth;camY+=(camFollow.y-24-camY)*smooth;
        }
        if (fadeDur > 0) {
            fadeT += dt; float k=CinematicMotionV463.progress(fadeT,fadeDur);
            fade=CinematicMotionV463.lerp(fade0,fade1,CinematicMotionV463.ease(k));
            if(k>=1f) {fadeDur=0f;asyncFade=false;}
        }
        if (tintDur > 0) { tintT += dt; float k = Math.min(1f, tintT / tintDur); tintA = tintA0 + (tintA1 - tintA0) * k; if (k >= 1f) tintDur = 0; }
        if (capDur > 0) { capT += dt; if (capT >= capDur) { capDur = 0; asyncCap = false; } }
        if (waitT > 0) waitT -= dt;
        // aktor bergerak
        for (Iterator<Mover> it = movers.iterator(); it.hasNext(); ) {
            Mover m = it.next();
            float[] tgt = m.path[m.idx];
            float dx = tgt[0] - m.a.x, dy = tgt[1] - m.a.y, d = (float) Math.sqrt(dx * dx + dy * dy);
            float step = m.speed * dt;
            if (d <= step) {
                m.a.x = tgt[0]; m.a.y = tgt[1]; m.idx++;
                if (m.idx >= m.path.length) {
                    m.a.walking = false; m.a.sprinting = false;
                    if (m.endDir >= 0) m.a.dir = m.endDir;
                    it.remove(); if (waitMover == m) waitMover = null;
                    continue;
                }
            } else { m.a.x += dx / d * step; m.a.y += dy / d * step; m.a.face(dx, dy); }
            m.a.walking = true; m.a.sprinting = m.run;
        }
        for (Iterator<Fx> it = fxs.iterator(); it.hasNext(); ) { Fx f = it.next(); f.t += dt; if (f.t > f.dur) it.remove(); }
        pump();
    }

    // ------------------------------------------------------------------ kamera
    public boolean camActive() { return camActive; }
    public float camX() { return camX + (shakeT > 0 ? MathUtils.sin(time * 70f) * shakeAmp : 0f); }
    public float camY() { return camY + (shakeT > 0 ? MathUtils.cos(time * 53f) * shakeAmp * 0.6f : 0f); }
    public float zoom() { return camZoom; }

    // ------------------------------------------------------------------ gambar
    /** Efek dunia (dipanggil dalam batch kamera dunia). */
    public void drawWorld(SpriteBatch b, float mapH, float left, float bottom, float ww, float wh) {
        Texture sp = assets.tex("ui/sparkle.png");
        for (Fx f : fxs) {
            float k = f.t / f.dur, fadeOut = Math.min(1f, (f.dur - f.t) * 2f), fadeIn = Math.min(1f, f.t * 3f);
            float al = Math.min(fadeOut, fadeIn);
            float gx = f.x, gy = mapH - f.y;
            switch (f.kind) {
                case "fireflies": {
                    for(int i=0;i<f.n;i++) {
                        float angle=i*2.39996f+f.seed;
                        float radius=22f+(i%9)*13f;
                        float drift=MathUtils.sin(time*.65f+i*.93f)*12f;
                        float x=gx+MathUtils.cos(angle)*radius+drift;
                        float y=gy+MathUtils.sin(angle)*radius*.65f+MathUtils.cos(time*.88f+i)*10f;
                        float pulse=.45f+.5f*Math.max(0f,MathUtils.sin(time*2f+i*1.4f));
                        b.setColor(1f,.91f,.57f,al*pulse*.72f);
                        b.draw(sp,x-4f,y-4f,8f,8f);
                    }
                    break;
                }
                case "mist": {
                    for(int i=0;i<Math.min(f.n,24);i++) {
                        float xx=left+(((i*.61f+f.t*.013f)%1f)+1f)%1f*ww;
                        float yy=bottom+((i*.42f)%1f)*wh;
                        float width=42f+(i%4)*35f;
                        b.setColor(.80f,.84f,.95f,al*.10f);
                        b.draw(assets.pixel,xx-width*.5f,yy,width,2f+(i%3));
                    }
                    break;
                }
                case "aurora": {
                    for(int i=0;i<Math.min(f.n,32);i++) {
                        float xx=left+(((i*.0313f+f.t*.015f)%1f)+1f)%1f*ww;
                        float yy=bottom+wh*.55f+MathUtils.sin(i*.31f+time*.38f)*wh*.12f;
                        float height=18f+(i%4)*14f;
                        b.setColor(i%2==0?.55f:.85f,.75f,1f,al*.065f);
                        b.draw(assets.pixel,xx,yy,Math.max(4f,ww/36f),height);
                    }
                    break;
                }
                case "rainlight": {
                    for(int i=0;i<Math.min(f.n,65);i++) {
                        float xx=left+(((i*.61803f+f.t*.115f)%1f)+1f)%1f*ww;
                        float yy=bottom+((((i*.37011f-f.t*.3f)%1f)+1f)%1f)*wh;
                        b.setColor(.72f,.85f,1f,al*.21f);
                        b.draw(assets.pixel,xx,yy,1.8f,14f+(i%4)*7f);
                    }
                    break;
                }
                case "sparkles":
                    for (int i = 0; i < f.n; i++) {
                        float ang = i * 2.39996f + f.seed, r = 8 + k * (40 + (i % 5) * 12);
                        b.setColor(1f, 0.92f, 0.7f, al * (0.5f + 0.5f * MathUtils.sin(time * 6 + i)));
                        b.draw(sp, gx + MathUtils.cos(ang) * r - 4, gy + MathUtils.sin(ang) * r * 0.8f + k * 18 - 4, 8, 8);
                    }
                    break;
                case "hearts": {
                    Texture h = assets.tex("ui/emote_heart.png");
                    for (int i = 0; i < Math.min(f.n, 8); i++) {
                        float tt = (f.t * 0.6f + i * 0.37f) % 1f;
                        b.setColor(1, 1, 1, al * (1f - tt));
                        b.draw(h, gx + MathUtils.sin(i * 1.7f + f.t * 2) * 18 - 7, gy + 50 + tt * 50, 14, 14);
                    }
                    break;
                }
                case "petals":
                    for (int i = 0; i < 40; i++) {
                        float px = ((i * 0.618f + f.t * (0.03f + (i % 4) * 0.01f)) % 1f) * ww;
                        float py = (((i * 0.382f - f.t * 0.08f) % 1f) + 1f) % 1f * wh;
                        b.setColor(1f, 0.76f, 0.86f, al * 0.9f);
                        b.draw(assets.pixel, left + px, bottom + py, 3, 2);
                    }
                    break;
                case "portal": {
                    float rad = 6 + Math.min(1f, k * 1.6f) * 46;
                    b.setColor(0.85f, 0.75f, 1f, al * 0.45f);
                    b.draw(sp, gx - rad * 1.4f, gy - rad * 1.4f + 30, rad * 2.8f, rad * 2.8f);
                    for (int i = 0; i < 36; i++) {
                        float ang = i / 36f * MathUtils.PI * 2 + time * 2.2f;
                        float rr = rad * (0.75f + 0.25f * MathUtils.sin(time * 3 + i));
                        b.setColor(i % 2 == 0 ? 1f : 0.8f, 0.85f, 1f, al);
                        b.draw(sp, gx + MathUtils.cos(ang) * rr - 4, gy + 30 + MathUtils.sin(ang) * rr * 1.2f - 4, 8, 8);
                    }
                    for (int i = 0; i < 12; i++) {
                        float tt = (time * 0.7f + i / 12f) % 1f;
                        b.setColor(1f, 0.95f, 0.8f, al * (1 - tt));
                        b.draw(sp, gx + MathUtils.sin(i * 2.1f) * rad * (1 - tt), gy + 30 + MathUtils.cos(i * 2.1f) * rad * (1 - tt), 6, 6);
                    }
                    break;
                }
                case "glow": {
                    float s = 50 + MathUtils.sin(time * 3) * 6;
                    b.setColor(1f, 0.9f, 0.65f, al * 0.55f);
                    b.draw(sp, gx - s, gy - s + 20, s * 2, s * 2);
                    break;
                }
                case "book": {
                    Texture bk = assets.tex("props/glowing_book.png");
                    float lift = Math.min(1f, k * 2f) * 34 + MathUtils.sin(time * 2.5f) * 3;
                    b.setColor(1f, 0.9f, 0.6f, al * 0.6f);
                    b.draw(sp, gx - 40, gy + lift - 22, 80, 80);
                    b.setColor(1, 1, 1, al);
                    b.draw(bk, gx - bk.getWidth() / 2f, gy + lift, bk.getWidth(), bk.getHeight());
                    break;
                }
                case "lanterns": {
                    Texture ln = assets.tex("items/lantern_paper.png");
                    for (int i = 0; i < f.n; i++) {
                        float delay = (i * 0.37f) % 2.5f, tt = f.t - delay; if (tt < 0) continue;
                        float lx = gx + ((i * 0.618f) % 1f - 0.5f) * 260 + MathUtils.sin(tt + i) * 6, ly = gy + tt * 22 * (0.7f + (i % 3) * 0.2f);
                        b.setColor(1f, 0.8f, 0.5f, al * 0.35f); b.draw(sp, lx - 16, ly - 16, 32, 32);
                        b.setColor(1, 1, 1, al); b.draw(ln, lx - 8, ly - 8, 16, 16);
                    }
                    break;
                }
                case "beam": {
                    b.setColor(1f, 0.95f, 0.8f, al * 0.35f);
                    b.draw(assets.pixel, gx - 14, gy, 28, wh);
                    b.setColor(1f, 1f, 1f, al * 0.5f);
                    b.draw(assets.pixel, gx - 5, gy, 10, wh);
                    break;
                }
                case "restore": { // gelombang warna yang memulihkan area
                    float rr = k * 420;
                    for (int i = 0; i < 64; i++) {
                        float ang = i / 64f * MathUtils.PI * 2;
                        b.setColor(1f, 0.9f, 0.7f, al * (1 - k));
                        b.draw(sp, gx + MathUtils.cos(ang) * rr - 5, gy + MathUtils.sin(ang) * rr * 0.7f - 5, 10, 10);
                    }
                    break;
                }
                case "stars":
                    for (int i = 0; i < f.n; i++) {
                        float px = ((i * 0.618f) % 1f) * ww, py = ((i * 0.382f + 0.3f) % 1f) * wh;
                        b.setColor(1f, 0.97f, 0.85f, al * (0.4f + 0.6f * Math.max(0, MathUtils.sin(time * 2 + i))));
                        b.draw(sp, left + px, bottom + py, 7, 7);
                    }
                    break;
                default: break;
            }
        }
        if (tintA > 0) { b.setColor(tintColor.r, tintColor.g, tintColor.b, tintA); b.draw(assets.pixel, left - 10, bottom - 10, ww + 20, wh + 20); }
        b.setColor(1, 1, 1, 1);
    }

    /** Overlay layar (letterbox, fade, flash, caption) di koordinat UI. */
    public void drawUi(Ui ui, float W, float H) {
        if (bars > 0.001f) {
            float bh = H * 0.11f * bars;
            ui.rect(0, H - bh, W, bh, Ui.INK, 1f); ui.rect(0, 0, W, bh, Ui.INK, 1f);
            ui.rect(0, H - bh - 2, W, 2, Ui.GOLD, bars * 0.55f);
            ui.rect(0, bh, W, 2, Ui.GOLD, bars * 0.36f);
            if (active) ui.text(assets.label, fast ? "▶▶" : "Tahan layar untuk mempercepat", W - 520, bh * 0.75f, Ui.LAVENDER, 0.7f, com.badlogic.gdx.utils.Align.right, 500);
        }
        if (capDur > 0) {
            float a = CinematicMotionV463.ease(Math.max(0f, Math.min(1f,
                    Math.min(capT * 2f, (capDur - capT) * 2f))));
            float shift = (1f - a) * 16f;
            // v3.2: artbook composition from the current game's world assets.
            // A separate still exists for every canonical chapter caption, loaded only when used.
            if (capArt != null) {
                Texture still = assets.uiTex("ui/v32_cinema/" + capArt + ".png");
                float sw = Math.min(W * 0.76f, 940f);
                ui.image(still, (W - sw) / 2f, H * 0.14f, sw, sw * 432f / 768f, a * 0.48f);
            }
            float cw=Math.min(700f,W*.82f), ch=cw*206f/700f;
            ui.image(cinematicBloom, W / 2 - 230, H / 2 - 210, 460, 460, a * 0.52f);
            ui.image(captionRibbon, W/2-cw/2, H/2-ch/2-shift, cw,ch, a*.87f);
            // v3.2: fine pixel-art ornamental framing (no new story timing or input).
            ui.image(sceneOrnament, W / 2 - 382, H / 2 - 126 - shift, 124, 124, a * 0.92f);
            ui.image(sceneOrnament, W / 2 + 258, H / 2 - 126 - shift, 124, 124, a * 0.72f);
            ui.textCenter(assets.title, capTitle, W / 2, H / 2 + 45 - shift, tmpC(Ui.CREAM, a), 0.69f);
            if (capSub != null) ui.textCenter(assets.body, capSub, W / 2, H / 2 - 14 - shift, tmpC(Ui.GOLD, a), 0.89f);
        }
        // Subtle chapter framing, reused from the existing pixel-art palette.
        if (active && bars > .55f && capDur <= 0 && W >= 750f) {
            ui.rect(W*.5f-34,H-H*.11f-6f,68f,2f,Ui.GOLD,.28f*bars);
        }
        if (fade > 0.001f) ui.rect(0, 0, W, H, fadeColor, fade);
        if (flash > 0) ui.rect(0, 0, W, H, flashColor, Math.min(1f, flash / Math.max(0.01f, flashDur)));
    }
    private final Color tc = new Color();
    private Color tmpC(Color c, float a) { tc.set(c.r, c.g, c.b, a); return tc; }

    /** true saat caption tampil di tengah layar (UI lain sebaiknya disembunyikan). */
    /** Illustrations are selected from actual scripted captions, not arbitrary story or save flags. */
    static String captionArt(String title, String sub) {
        if (title == null) return null;
        if ("Sabtu pagi".equals(title)) return sub != null && sub.contains("Sofia") ? "sofia_morning" : "arland_morning";
        if ("Plaza Kota".equals(title)) return "plaza_intro";
        if ("Memory Garden".equals(title)) return "garden_portal";
        if ("Perpustakaan Kota".equals(title)) return "library";
        if ("Arsip No. 7".equals(title)) return "archive";
        if ("Dermaga Danau".equals(title)) return "pier";
        if (title.startsWith("Halte")) return "rain";
        if ("Setelah Hujan".equals(title)) return "reunion";
        if ("Satu Langit".equals(title)) return "sky";
        if ("The Quiet".equals(title)) return "quiet";
        if ("Festival Lentera".equals(title)) return "lantern";
        return null;
    }

    public boolean letterboxed() { return bars > 0.5f; }
}
