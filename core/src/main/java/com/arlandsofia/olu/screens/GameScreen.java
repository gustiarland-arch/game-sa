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

/**
 * Layar bermain: eksplorasi top-down 3/4, collision kaki, pintu, companion, interaksi quest,
 * dialog, puzzle, Memory Book, pause, autosave. Implementasi Presenter untuk ActionRunner.
 */
public final class GameScreen extends BaseScreen implements ActionRunner.Presenter {
    private static final float WALK_SPEED = 112f, SPRINT_SPEED = 176f;

    private final Progress p;
    private final boolean replay, newGame;
    private final QuestEngine engine;
    private final ActionRunner runner;

    private final OrthographicCamera worldCam = new OrthographicCamera();
    private final ExtendViewport worldView = new ExtendViewport(760, 428, worldCam);
    private final CameraRig cameraRig = new CameraRig();
    /** Reused collision adapter: avoids allocating callbacks every frame. */
    private final WorldNavigationV52.Collision footCollision = new WorldNavigationV52.Collision() {
        @Override public boolean blocked(float sx,float sy) { return area == null || area.blocked(sx,sy); }
    };
    private float frameDt = 1f / 60f;

    private MapDb.Area area;
    /** Cached terrace textures are editor-replaceable PNGs loaded with other native assets. */
    private float lastTerrainHeight;
    private boolean previousStair;
    private Texture mapTex;
    private final Actor player, partner;
    private int partnerMode; // 0 tidak ada, 1 NPC diam, 2 companion
    private final ArrayDeque<float[]> trail = new ArrayDeque<>();

    private final TouchControls controls;
    private final MinigameOverlay minigame;
    private final CutscenePlayer cine;
    private boolean cineShowPartner;
    // companion hidup
    private float compIdle, compNext = 3f, pendingComment = -1f;
    private String bubbleText; private float bubbleTime;
    private final Map<String, Actor> cineActors = new LinkedHashMap<>();
    private final Map<String, Actor> townActors = new LinkedHashMap<>();
    /** otak NPC: {homeX, homeY, radius, targetX, targetY, timer, scheduleKey} */
    private final Map<String, float[]> npcBrain = new LinkedHashMap<>();
    private final Map<String, String> npcPlaceKey = new LinkedHashMap<>();
    private final List<Animal> animals = new ArrayList<>();
    private Animal targetAnimal; private boolean targetBed;
    private float clockAcc;
    private float soundscapeClock, footstepClock;
    private QuestDb.TownNpc targetNpc;
    private QuestDb.Interactable targetSide;
    private QuestDb.Talk targetTalk;
    private float creditsTime = -1; private Runnable creditsDone;
    private final float[] rainX = new float[140], rainY = new float[140];
    private final DialogBox dialog;
    private final DialogueHistoryOverlay dialogueHistory;
    private float autosaveAcc;
    private final PuzzleOverlay puzzle;
    private final MemoryBookOverlay book;
    private final ShopOverlay shop;
    private final RomanceOverlay romance;
    private boolean targetRomance;
    private final SettingsPanel settingsPanel;
    private boolean settingsOpen, pauseOpen;
    private final List<UiButton> pauseButtons = new ArrayList<>();
    private final UiButton hudBook, hudPause;
    private final Texture shadow, marker, sparkle, glow, coinIcon;
    private final WorldFx worldFx;
    /** Prerendered split regions for foliage; cache never modified after creation. */
    private final Map<Texture, TextureRegion[]> animatedTreeRegions = new java.util.IdentityHashMap<>();

    // target interaksi
    private QuestDb.Interactable targetQuest;
    private MapDb.Examine targetExamine;

    private String toastText; private float toastTime;
    private String bannerText; private float bannerTime;
    private float objectiveFlash;
    private float doorCooldown;
    private QuestCompass.Hint cachedQuestRoute;
    private float questRouteRefresh;

    private int fadePhase; private float fadeAlpha; private Runnable fadeMid, fadeEnd;
    private String cardTitle, cardSub; private float cardTime = -1; private Runnable cardDone;

    private final Color tint = new Color();
    private static final class DrawItem { float y; Object value; }
    private final List<DrawItem> drawList = new ArrayList<>();
    /** Reused list of quest markers: no new ArrayList in every rendered frame. */
    private final List<QuestDb.Interactable> drawMarkers = new ArrayList<>();
    private final List<DrawItem> drawPool = new ArrayList<>();
    /** Cache ukuran gambar prop per area; culling tidak memanggil Texture lookup tiap frame. */
    private final Map<MapDb.Prop, float[]> propMetrics = new java.util.IdentityHashMap<>();
    private int drawCursor;
    private float visibleL, visibleR, visibleB, visibleT;
    private final Comparator<DrawItem> bySortY = new Comparator<DrawItem>() {
        public int compare(DrawItem a, DrawItem b) { return Float.compare(a.y, b.y); }
    };

    /** Reuse urutan draw tanpa alokasi array kecil untuk setiap prop tiap frame. */
    private void addDraw(float y, Object value) {
        if (drawCursor >= drawPool.size()) drawPool.add(new DrawItem());
        DrawItem item = drawPool.get(drawCursor++);
        item.y = y; item.value = value;
        drawList.add(item);
    }

    private boolean visibleActor(float x, float y) {
        float drawY = area.h - y;
        return x >= visibleL - 75 && x <= visibleR + 75 && drawY >= visibleB - 75 && drawY <= visibleT + 75;
    }

    /** Bounds-aware prop culling BEFORE depth sort: avoids sorting hundreds of offscreen trees. */
    private boolean propVisible(MapDb.Prop pr) {
        float[] size = propMetrics.get(pr);
        if (size == null) {
            Texture normal = game.assets.tex(pr.def.image);
            Texture alternate = pr.alt == null ? normal : game.assets.tex(pr.alt.image);
            size = new float[]{normal.getWidth(), normal.getHeight(), alternate.getWidth(), alternate.getHeight()};
            propMetrics.put(pr, size);
        }
        boolean alternate = pr.alt != null && pr.altFlag != null && p.hasFlag(pr.altFlag);
        float width = size[alternate ? 2 : 0], height = size[alternate ? 3 : 1];
        float x = pr.x - width * 0.5f, y = area.h - pr.y;
        return !(x > visibleR || x + width < visibleL ||
                 y > visibleT || y + height < visibleB);
    }

    public GameScreen(final OluGame game, Progress progress, boolean replay, boolean newGame) {
        super(game);
        this.p = progress; this.replay = replay; this.newGame = newGame;
        this.engine = new QuestEngine(game.story, game.quests, game.maps, p, replay); // melempar bila step tidak dikenal
        this.engine.setGlobalProgress(game.global);
        MapDb.flags = new MapDb.FlagCheck() { public boolean has(String f) { return p.hasFlag(f); } };
        this.runner = new ActionRunner(engine, this);
        Assets a = game.assets;
        shadow = a.tex("fx/contact_shadow_v37.png"); marker = a.tex("ui/marker.png"); sparkle = a.tex("ui/sparkle.png"); glow = a.tex("ui/soft_glow.png"); coinIcon = a.tex("ui/icon_coin.png");
        worldFx = new WorldFx(a);
        player = new Actor(p.route);
        partner = new Actor(Routes.partner(p.route));
        controls = new TouchControls(a);
        dialog = new DialogBox(a, game.story, game.settings);
        dialogueHistory = new DialogueHistoryOverlay(a);
        dialog.setHistoryAction(new Runnable() { public void run() { openDialogueHistory(); } });
        puzzle = new PuzzleOverlay(a, game.audio);
        minigame = new MinigameOverlay(a, game.audio);
        cine = new CutscenePlayer(new CutscenePlayer.Host() {
            public Actor actor(String who) {
                if (who == null || who.equals("player") || who.equals(player.character)) return player;
                if (who.equals("partner") || who.equals(partner.character)) return partner;
                Actor c = cineActors.get(who); if (c != null) return c;
                c = townActors.get(who); if (c != null) return c;
                for (Actor t : townActors.values()) if (t.character.equals(who)) return t;
                return null;
            }
            public Actor spawn(String id, String sprite, float x, float y, int dir) {
                Actor ac = new Actor(sprite); ac.x = x; ac.y = y; ac.dir = dir; cineActors.put(id, ac); return ac;
            }
            public void despawn(String id) { cineActors.remove(id); }
            public void showPartner(boolean on) { cineShowPartner = on; partner.visible = true; }
            public void say(String sceneId, int from, int n, Runnable done) { playScenePart(sceneId, from, n, done); }
            public void line(String sp, String emo, String text, Runnable done) {
                List<StoryDb.Line> l = new ArrayList<>(); l.add(new StoryDb.Line(sp, emo, text)); playLines(l, null, done);
            }
            public void sfx(String id) { game.audio.sfx(id); }
            public void music(String id) { game.audio.music(id); }
            public float camX() { return worldCam.position.x; }
            public float camY() { return area.h - worldCam.position.y; }
            public boolean canStand(float x, float y) { return area != null && !area.blocked(x, y); }
        }, a);
        for (int i = 0; i < rainX.length; i++) { rainX[i] = (i * 97.31f) % 1f; rainY[i] = (i * 53.17f) % 1f; }
        book = new MemoryBookOverlay(a, game.book, game.story, game.quests, game.maps);
        shop = new ShopOverlay(a, engine, game.book, game.audio);
        romance = new RomanceOverlay(a, engine, game.book);
        settingsPanel = new SettingsPanel(game, new Runnable() { public void run() { settingsOpen = false; } });
        hudBook = new UiButton("Buku", new Runnable() { public void run() { openBook(); } });
        hudBook.icon = a.uiTex("ui/icon_heart.png"); hudBook.textScale = 0.8f;
        hudPause = new UiButton("II", new Runnable() { public void run() { openPause(); } });
        String[] labels = {"Lanjut bermain", "Memory Book", "Riwayat dialog", replay ? "Simpan (nonaktif di replay)" : "Simpan sekarang", "Romance Simulation 3.0", "Pengaturan", "Cara bermain", "Menu utama"};
        Runnable[] acts = {
                new Runnable() { public void run() { pauseOpen = false; } },
                new Runnable() { public void run() { pauseOpen = false; openBook(); } },
                new Runnable() { public void run() { openDialogueHistory(); } },
                new Runnable() { public void run() { if (saveNow()) { toast("Progress tersimpan"); pauseOpen = false; } } },
                new Runnable() { public void run() {
                    if (replay) { toast("Mode romance tidak tersedia saat replay"); return; }
                    if (saveNow()) {
                        pauseOpen = false;
                        controls.reset();
                        game.openRomanceSimulationV45(p.route, p.slot, p.day);
                    } else toast("Simpan progres dahulu sebelum masuk simulasi romance.");
                } },
                new Runnable() { public void run() { settingsOpen = true; } },
                new Runnable() { public void run() { showHowToPlay(); } },
                new Runnable() { public void run() { askMainMenu(); } }};
        for (int i = 0; i < labels.length; i++) { UiButton b = new UiButton(labels[i], acts[i]); pauseButtons.add(b); }
        pauseButtons.get(0).accent = true;
        pauseButtons.get(3).enabled = !replay;
        pauseButtons.get(4).enabled = !replay;

        MapDb.Area start = game.maps.area(p.area);
        if (start == null) start = game.maps.area(Routes.room(p.route));
        float sx = p.x, sy = p.y;
        // Resuming a v3.x save may place the hero in a newly illustrated
        // obstacle. Pick the nearest legal foot position before falling back
        // to the room spawn, preserving as much local progress as possible.
        if (start.blocked(sx, sy)) {
            boolean found = false;
            for (int radius = 12; radius <= 240 && !found; radius += 12) {
                for (int angle = 0; angle < 360; angle += 15) {
                    float rx = sx + radius * MathUtils.cosDeg(angle);
                    float ry = sy + radius * MathUtils.sinDeg(angle);
                    if (!start.blocked(rx, ry)) { sx = rx; sy = ry; found = true; break; }
                }
            }
            if (!found) { sx = start.spawnX; sy = start.spawnY; }
        }
        enterArea(start.id, sx, sy, Actor.dirOf(p.dir), false);
        if (p.companion) { partnerMode = 2; placeBeside(); }
    }

    private static Map<String, Object> act(String... kv) {
        Map<String, Object> m = new LinkedHashMap<>();
        for (int i = 0; i + 1 < kv.length; i += 2) m.put(kv[i], kv[i + 1]);
        return m;
    }

    @Override
    public void show() {
        super.show();
        syncSoundscape();
        if (newGame) {
            List<Map<String, Object>> l = new ArrayList<>();
            l.add(act("do", "chapterCard", "chapter", engine.chapter()));
            if (engine.step() != null) l.addAll(engine.resolve(engine.step().onStart));
            runner.run(l);
        } else {
            toast(replay ? "Mode replay: progres tidak disimpan" : "Cerita " + Routes.display(p.route) + " dimuat");
            // pengaman: bila step menunggu masuk area ini, picu sekarang (mencegah softlock setelah force-close)
            runner.run(engine.onEnterArea(area.id));
        }
    }

    // ================================================================== area & posisi
    private void enterArea(String id, float x, float y, int dir, boolean announce) {
        MapDb.Area a = game.maps.area(id);
        if (a == null) a = game.maps.area(Routes.room(p.route));
        if (area != null && !area.image.equals(a.image)) game.assets.unloadMap(area.image);
        if (area != a) propMetrics.clear();
        area = a;
        if (announce) game.audio.sfx("door_open", .45f);
        game.assets.warmArea(a);
        mapTex = game.assets.mapTex(a.image);
        // Correct invalid saved locations/door landings using the SAME foot collision as movement.
        float[] safe = WorldNavigationV52.nearestOpen(footCollision,x,y,a.spawnX,a.spawnY);
        x=safe[0]; y=safe[1];
        player.x = x; player.y = y; player.dir = dir; player.walking = false;
        p.area = a.id; p.x = x; p.y = y; p.dir = Actor.dirName(dir);
        if (!replay) p.visitedAreas.add(a.id);
        trail.clear();
        cachedQuestRoute=null; questRouteRefresh=0f;
        cameraRig.reset();
        worldFx.reset();
        soundscapeClock = 0f; footstepClock = 0f;
        lastTerrainHeight = ElevationV50.heightAt(a.terraces, x, y);
        previousStair = ElevationV50.onStairs(a.terraces,x,y);
        if (partnerMode == 2) placeBeside();
        refreshNpcs();
        spawnAnimals();
        syncSoundscape();
        if (announce) { bannerText = a.name; bannerTime = 2.2f; }
        if (partnerMode == 2) queueComment();
        doorCooldown = 0.5f;
    }

    /** komentar pasangan sekali per area (disimpan sebagai flag CMT_<area>). */
    private void queueComment() {
        Map<String, List<String>> m = game.quests.comments.get(area.id);
        if (m == null || p.hasFlag("CMT_" + area.id)) return;
        List<String> l = m.get(p.route);
        if (l == null || l.isEmpty()) return;
        pendingComment = 1.4f;
    }

    private void showComment() {
        List<String> l = game.quests.comments.get(area.id).get(p.route);
        bubbleText = l.get(MathUtils.random(0, l.size() - 1)); bubbleTime = 3.6f;
        p.flags.add("CMT_" + area.id);
        partner.faceTo(player); partner.showEmote("note", 1.2f);
    }

    /** perilaku kecil companion saat diam: menoleh, melihat sekeliling, bereaksi pada hujan, memperhatikan target interaksi. */
    private void companionLife(float dt) {
        if (partnerMode != 2 || cine.active() || partner.walking || p.holdingHands) { compIdle = 0; return; }
        Object tgt = targetQuest != null ? targetQuest : targetNpc != null ? targetNpc : targetSide;
        if (tgt != null) {
            float tx = targetQuest != null ? targetQuest.x : targetNpc != null ? targetNpc.x : targetSide.x;
            float ty = targetQuest != null ? targetQuest.y : targetNpc != null ? targetNpc.y : targetSide.y;
            partner.face(tx - partner.x, ty - partner.y); compIdle = 0; return;
        }
        compIdle += dt;
        if (compIdle < compNext) return;
        compIdle = 0; compNext = MathUtils.random(2.5f, 6f);
        boolean rain = "rain".equals(weather()) && !isIndoor();
        int r = MathUtils.random(0, 9);
        // Reactions remain cosmetic (do not change romance rewards or story flags).
        if (!rain && p.affection >= 75 && r >= 8 && dist(partner.x,partner.y)<90f) {
            partner.faceTo(player);
            partner.setPose(r == 8 ? "shy" : "excited",1.15f);
            partner.showEmote("heart",1.3f);
        } else if (rain && r < 3) { partner.showEmote("sweat", 1.4f); partner.faceTo(player); }
        else if (r < 4) { partner.faceTo(player); partner.setPose("ponder",1.0f); }
        else if (r < 7) partner.dir = MathUtils.random(0, 3);
        else if (r < 9) {
            Actor near = null; float best = 220 * 220;
            for (Actor t : townActors.values()) { float dx = t.x - partner.x, dy = t.y - partner.y; if (dx * dx + dy * dy < best) { best = dx * dx + dy * dy; near = t; } }
            if (near != null) partner.faceTo(near); else partner.faceTo(player);
        } else { partner.faceTo(player); partner.showEmote(MathUtils.random(0, 1) == 0 ? "note" : "heart", 1.4f); }
    }

    private void placeBeside() {
        float[][] offs = {{-30, 6}, {30, 6}, {0, 24}, {0, -24}, {-44, 0}, {44, 0}};
        for (float[] o : offs) {
            float nx = player.x + o[0], ny = player.y + o[1];
            if (!area.blocked(nx, ny)) { partner.x = nx; partner.y = ny; partner.dir = player.dir; return; }
        }
        // If there is no adjacent safe tile, keep the companion behind until a legal spot appears.
        float[] safe = WorldNavigationV52.nearestOpen(footCollision,player.x-34,player.y,player.x,player.y);
        partner.x = safe[0]; partner.y = safe[1];
    }

    /** NPC sesuai jadwal & jam. Aktor yang masih di area ini dipertahankan dan berjalan ke titik barunya. */
    private void refreshTown() {
        java.util.Set<String> keep = new java.util.HashSet<>();
        for (QuestDb.TownNpc n : engine.townNpcsNow(area.id)) {
            Object[] pl = engine.npcPlace(n);
            float x = ((Number) pl[1]).floatValue(), y = ((Number) pl[2]).floatValue(), rad = ((Number) pl[4]).floatValue();
            float[] npcSafe = WorldNavigationV52.nearestOpen(footCollision,x,y,area.spawnX,area.spawnY);
            x=npcSafe[0]; y=npcSafe[1];
            String key = pl[0] + "@" + Math.round(x) + "," + Math.round(y);
            keep.add(n.id);
            Actor ac = townActors.get(n.id);
            if (ac == null) {
                ac = new Actor(n.sprite); ac.x = x; ac.y = y; ac.dir = Actor.dirOf((String) pl[3]);
                townActors.put(n.id, ac); npcBrain.put(n.id, new float[]{x, y, rad, x, y, MathUtils.random(1f, 4f), 0f});
            } else if (!key.equals(npcPlaceKey.get(n.id))) {
                float[] b = npcBrain.get(n.id); b[0] = x; b[1] = y; b[2] = rad; b[3] = x; b[4] = y; b[5] = 0f; b[6] = 0f;
            }
            npcPlaceKey.put(n.id, key);
        }
        townActors.keySet().retainAll(keep); npcBrain.keySet().retainAll(keep); npcPlaceKey.keySet().retainAll(keep);
    }

    /** NPC berjalan pelan di sekitar titik jadwalnya, berhenti saat diajak bicara atau ada cutscene. */
    private void updateNpcs(float dt) {
        if (cine.active()) return;
        for (Map.Entry<String, Actor> e : townActors.entrySet()) {
            Actor ac = e.getValue(); float[] b = npcBrain.get(e.getKey());
            if (b == null) continue;
            if (dialog.active() && targetNpc != null && targetNpc.id.equals(e.getKey())) { ac.walking = false; continue; }
            float dx = b[3] - ac.x, dy = b[4] - ac.y, d = (float) Math.sqrt(dx * dx + dy * dy);
            if (d > 2f) {
                float speed = LivingWorldV46.walkingSpeed(WorldClock.hour(p.minute), weather(), isIndoor())
                        * ac.motion.walkSpeed * ElevationV50.speedFactor(area.terraces, ac.x, ac.y);
                float sp = Math.min(d, speed * Math.max(0f, Math.min(.05f, dt)));
                float nx = ac.x + dx / d * sp, ny = ac.y + dy / d * sp;
                boolean nearPlayer = Math.abs(nx - player.x) < 22 && Math.abs(ny - player.y) < 16;
                boolean nearPartner = partnerMode == 2
                        && Math.abs(nx - partner.x) < 20 && Math.abs(ny - partner.y) < 16;
                boolean nearNpc = false;
                for (Map.Entry<String, Actor> other : townActors.entrySet()) {
                    if (other.getKey().equals(e.getKey())) continue;
                    Actor o = other.getValue();
                    if (Math.abs(nx - o.x) < 14 && Math.abs(ny - o.y) < 12) { nearNpc = true; break; }
                }
                if (WorldNavigationV52.clearSegment(footCollision,ac.x,ac.y,nx,ny)
                        && ElevationV50.canStep(area.terraces,ac.x,ac.y,nx,ny)
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
                    b[5] = MotionPersonalityV53.pauseSeconds(e.getKey(), p.day, p.minute);
                    if (b[2] > 0) {
                        // Stable per-actor sequence creates different legal waypoints
                        // even before the next 15-minute window; no teleportation.
                        b[6] = (b[6] + 1f) % 4096f;
                        LivingWorldV46.Target next = LivingWorldV46.wanderTarget(
                                e.getKey(), p.day, p.minute, b[0], b[1], b[2], ac.x, ac.y,
                                isIndoor(), weather(), new LivingWorldV46.Collision() {
                                    public boolean blocked(float x,float y) { return area.blocked(x,y); }
                                }, (int)b[6]);
                        b[3] = next.x; b[4] = next.y;
                    } else if (MathUtils.random() < .3f) ac.dir = MathUtils.random(0, 3);
                    String act = npcIdleActivity(e.getKey());
                    if (act != null && ac.pose == null) ac.setPose(act,
                            1.1f + ac.motion.breathing * .9f);
                }
            }
        }
    }

    /** Aktivitas idle dari kebijakan dunia v4.6, memakai animasi atlas asli. */
    private String npcIdleActivity(String id) {
        return MotionPersonalityV53.idlePose(id, WorldClock.hour(p.minute), weather(), isIndoor(), p.day);
    }

    private void spawnAnimals() {
        animals.clear();
        boolean day = !WorldClock.isNight(p.minute), rain = WorldClock.HUJAN.equals(engine.weatherNow());
        for (Map<String, Object> spec : area.animals) {
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
                    if (!spec.containsKey("water") && area.blocked(x, y)) continue;
                    animals.add(new Animal(type, x, y, reg)); break;
                }
            }
        }
    }

    private void refreshNpcs() {
        refreshTown();
        if (partnerMode == 2) return;
        partnerMode = 0;
        for (QuestEngine.NpcView n : engine.npcs(area.id)) {
            if (n.who.equals(partner.character)) {
                partnerMode = 1; partner.x = n.x; partner.y = n.y; partner.dir = Actor.dirOf(n.dir); partner.walking = false;
            }
        }
    }

    // ================================================================== loop
    private boolean free() {
        return !dialogueHistory.active() && !dialog.active() && !puzzle.active() && !minigame.active() && creditsTime < 0 && !book.active() && !shop.active() && !romance.active() && !pauseOpen && !settingsOpen && confirm == null
                && fadePhase == 0 && cardTime < 0 && !runner.busy() && !cine.active();
    }

    @Override
    protected void update(float dt) {
        frameDt = dt;
        updateFade(dt);
        if (cardTime >= 0) { cardTime += dt; if (cardTime > 3.2f) finishCard(); }
        if (!dialogueHistory.active()) {
            dialog.update(dt);
            cine.update(dt);
        }
        for (Actor ac : cineActors.values()) ac.update(dt);
        puzzle.update(dt);
        minigame.update(dt);
        if (creditsTime >= 0) { creditsTime += dt; if (creditsTime > 4f + game.quests.credits.size() * 1.6f) finishCredits(); }
        if (toastTime > 0) toastTime -= dt;
        if (bannerTime > 0) bannerTime -= dt;
        if (objectiveFlash > 0) objectiveFlash -= dt;
        if (doorCooldown > 0) doorCooldown -= dt;
        if (questRouteRefresh > 0) questRouteRefresh -= dt;
        soundscapeClock -= dt;
        footstepClock -= dt;
        game.audio.duck(dialog.active() || cine.active());
        if (soundscapeClock <= 0f && !cine.active() && !runner.busy() && creditsTime < 0) {
            soundscapeClock = 1.2f;
            syncSoundscape();
        }

        syncClockToStep();
        boolean free = free();
        if (free && !replay) {
            autosaveAcc += dt;
            // Save reguler hanya di gameplay bebas; tidak memotong cutscene atau puzzle.
            if (autosaveAcc >= 90f) saveNow();
        }
        if (free) {
            if (!replay) p.playSeconds += dt;
            if (!realm()) clockAcc += dt; // jam berhenti di dunia kenangan
            while (clockAcc >= 1f) {
                clockAcc -= 1f; p.minute++;
                if (p.minute % 10 == 0) { refreshTown(); if (!cine.active()) syncSoundscape(); }
                if (p.minute == 19 * 60 + 30) spawnAnimals(); // hewan siang pulang, kucing malam keluar
                if (p.minute >= WorldClock.DAY_END) { passOut(); break; }
            }
            move(dt);
            if (player.walking && game.settings.footsteps && footstepClock <= 0f) {
                boolean stairsNow=ElevationV50.onStairs(area.terraces,player.x,player.y);
                game.audio.sfx(stairsNow ? "v50_stair_foot" : ElevationV50.stepSound(
                        area.terraces,player.x,player.y,SoundscapePlan.footstepFor(area.id)), .19f);
                footstepClock = player.sprinting ? .22f : .35f;
            }
            boolean onStairsNow=ElevationV50.onStairs(area.terraces,player.x,player.y);
            if(onStairsNow && !previousStair)game.audio.sfx("v50_stair_enter",.38f);
            previousStair=onStairsNow;
            lastTerrainHeight=ElevationV50.heightAt(area.terraces,player.x,player.y);
            findTarget();
            if (controls.consumeAction()) interact();
        } else {
            player.walking = false;
            controls.consumeAction();
            targetQuest = null; targetExamine = null; targetNpc = null; targetSide = null;
        }
        followCompanion(dt);
        companionLife(dt);
        if (bubbleTime > 0) bubbleTime -= dt;
        if (pendingComment > 0 && free() && partnerMode == 2) { pendingComment -= dt; if (pendingComment <= 0) showComment(); }
        player.update(dt);
        partner.update(dt);
        for (Actor ac : townActors.values()) ac.update(dt);
        updateNpcs(dt);
        for (int i = animals.size() - 1; i >= 0; i--) { Animal an = animals.get(i); an.update(dt, area, player.x, player.y); if (an.gone()) animals.remove(i); }
        worldFx.update(dt, player.x, area.h - player.y, player.walking, player.sprinting,
                "rain".equals(weather()), isIndoor(), partner.x, area.h - partner.y,
                partnerMode == 2, p.affection, game.settings.visualQuality);
    }

    // ================================================================== hari & tidur
    private String clockStep;
    /** step cerita bersuasana senja/malam memajukan jam dunia (hanya maju), agar HUD, NPC, dan langit selaras. */
    private void syncClockToStep() {
        QuestDb.Step st = engine.step();
        if (st == null || st.id.equals(clockStep)) return;
        clockStep = st.id;
        if (st.tint == null || replay) return;
        Color c = Color.valueOf(st.tint);
        int target = c.b > c.r ? 20 * 60 : 17 * 60 + 30;
        if (p.minute < target) { p.minute = target; refreshTown(); spawnAnimals(); }
    }
    private void newDay(String msg) {
        p.day++; p.minute = 7 * 60; clockAcc = 0;
        npcPlaceKey.clear(); townActors.clear(); npcBrain.clear();
        refreshTown(); spawnAnimals();
        syncSoundscape();
        String w = WorldClock.weather(p.day);
        toast(msg + " " + WorldClock.dayName(p.day) + ", hari ke-" + p.day + " • " + Character.toUpperCase(w.charAt(0)) + w.substring(1));
        saveNow();
    }

    private void askSleep() {
        boolean early = p.minute < 17 * 60;
        confirm = new ConfirmBox("Tidur?", early ? "Masih " + WorldClock.hhmm(p.minute) + ". Tidur sampai besok pagi?" : "Istirahat sampai besok pagi. Progress tersimpan otomatis.",
                "Tidur", new Runnable() { public void run() { confirm = null; fade(new Runnable() { public void run() {
                    player.dir = Assets.DIR_DOWN; newDay("Selamat pagi!"); } }, null); } },
                "Nanti", new Runnable() { public void run() { confirm = null; } });
    }

    private void passOut() {
        final String room = Routes.room(p.route);
        fade(new Runnable() { public void run() {
            MapDb.Area roomArea = game.maps.area(room);
            float[] bed = bedSpot(roomArea);
            enterArea(room, bed[0], bed[1] + 50f, Assets.DIR_DOWN, false);
            newDay("Kamu ketiduran sampai pagi...");
        } }, null);
    }

    private void move(float dt) {
        float kx = 0, ky = 0;
        if (Gdx.input.isKeyPressed(Input.Keys.A) || Gdx.input.isKeyPressed(Input.Keys.LEFT)) kx -= 1;
        if (Gdx.input.isKeyPressed(Input.Keys.D) || Gdx.input.isKeyPressed(Input.Keys.RIGHT)) kx += 1;
        if (Gdx.input.isKeyPressed(Input.Keys.W) || Gdx.input.isKeyPressed(Input.Keys.UP)) ky -= 1;
        if (Gdx.input.isKeyPressed(Input.Keys.S) || Gdx.input.isKeyPressed(Input.Keys.DOWN)) ky += 1;
        float dx = kx, dy = ky;
        if (dx == 0 && dy == 0) { dx = controls.vx; dy = -controls.vy; }
        float len = (float) Math.sqrt(dx * dx + dy * dy);
        boolean sprint = !p.holdingHands && (controls.sprintHeld || Gdx.input.isKeyPressed(Input.Keys.SHIFT_LEFT) || Gdx.input.isKeyPressed(Input.Keys.SHIFT_RIGHT));
        if (len < 0.01f) { player.walking = false; return; }
        float mag = Math.min(1f, len);
        dx /= len; dy /= len; // diagonal dinormalisasi
        float speed = (sprint ? SPRINT_SPEED : WALK_SPEED) * Math.max(0.45f, mag) * dt
                * ElevationV50.speedFactor(area.terraces, player.x, player.y);
        float ox = player.x, oy = player.y;
        float nx = player.x + dx * speed;
        // Swept foot collision prevents slipping through thin walls at low FPS.
        if (WorldNavigationV52.clearSegment(footCollision,player.x,player.y,nx,player.y)
                && ElevationV50.canStep(area.terraces,player.x,player.y,nx,player.y)) player.x = nx;
        float ny = player.y + dy * speed;
        if (WorldNavigationV52.clearSegment(footCollision,player.x,player.y,player.x,ny)
                && ElevationV50.canStep(area.terraces,player.x,player.y,player.x,ny)) player.y = ny;
        player.face(dx, dy);
        player.sprinting = sprint;
        float moved = Math.abs(player.x - ox) + Math.abs(player.y - oy);
        player.walking = moved > 0.01f;
        if (partnerMode == 2 && player.walking && !p.holdingHands) {
            float[] last = trail.peekLast();
            if (last == null || Math.abs(last[0] - player.x) + Math.abs(last[1] - player.y) > 6) trail.addLast(new float[]{player.x, player.y});
            while (trail.size() > 80) trail.pollFirst();
        }
        p.x = player.x; p.y = player.y; p.dir = Actor.dirName(player.dir);
        checkDoors(ox, oy);
    }

    private void checkDoors(float ox, float oy) {
        if (doorCooldown > 0) return;
        for (final MapDb.Door d : area.doors) {
            if (!d.touches(player.x, player.y)) continue;
            String lock = engine.doorLock(d);
            if (lock != null) {
                toast(lock);
                game.audio.sfx("soft_wrong");
                player.x = ox; player.y = oy;
                if (d.touches(player.x, player.y)) { // masih di zona: dorong menjauh dari pusat pintu
                    float vx = player.x - d.cx(), vy = player.y - d.cy();
                    float l = Math.max(1f, (float) Math.sqrt(vx * vx + vy * vy));
                    float tx = player.x + vx / l * 14, ty = player.y + vy / l * 14;
                    if (!area.blocked(tx, ty) && ElevationV50.canStep(area.terraces,player.x,player.y,tx,ty)) { player.x = tx; player.y = ty; }
                }
                doorCooldown = 1.2f;
                return;
            }
            controls.reset();
            fade(new Runnable() { public void run() { enterArea(d.to, d.tx, d.ty, Actor.dirOf(d.dir), true); } },
                    new Runnable() { public void run() { runner.run(engine.onEnterArea(area.id)); } });
            return;
        }
    }

    private void followCompanion(float dt) {
        if (cine.active()) return; // cutscene menguasai pose dan posisi kedua aktor
        if (partnerMode == 2 && p.holdingHands) {
            float sign = (player.dir == Assets.DIR_LEFT) ? -1f : 1f;
            float tx = player.x + 25f * sign, ty = player.y + 3f;
            if (area.blocked(tx, ty) || !ElevationV50.canStep(area.terraces,partner.x,partner.y,tx,ty)) tx = player.x - 25f * sign;
            if (!area.blocked(tx, ty) && ElevationV50.canStep(area.terraces,partner.x,partner.y,tx,ty)) {
                float k = Math.min(1f, dt * 14f);
                float stepX=partner.x+(tx-partner.x)*k, stepY=partner.y+(ty-partner.y)*k;
                if (!WorldNavigationV52.clearSegment(footCollision,partner.x,partner.y,stepX,stepY)) { partner.walking=false; return; }
                partner.x=stepX; partner.y=stepY;
                partner.dir = player.dir;
                partner.walking = player.walking;
                partner.sprinting = false;
                String pp = tx > player.x ? "hold_r" : "hold_l";
                String po = tx > player.x ? "hold_l" : "hold_r";
                if (!pp.equals(player.pose)) player.setPose(pp, 0f);
                if (!po.equals(partner.pose)) partner.setPose(po, 0f);
                trail.clear();
                return;
            }
            // Koridor sempit: kembali ke follow normal sampai jalur cukup lebar.
        }
        if ("hold_l".equals(player.pose) || "hold_r".equals(player.pose)) player.clearPose();
        if ("hold_l".equals(partner.pose) || "hold_r".equals(partner.pose)) partner.clearPose();
        if (cine.active()) return; // cutscene mengatur posisi companion
        if (partnerMode != 2) { partner.walking = false; return; }
        float dxp = player.x - partner.x, dyp = player.y - partner.y;
        float distP = (float) Math.sqrt(dxp * dxp + dyp * dyp);
        if (distP > 260) { placeBeside(); trail.clear(); return; }
        if (distP < 34 || trail.isEmpty()) {
            partner.walking = false;
            if (distP < 34 && trail.size() > 4) trail.pollFirst();
            return;
        }
        float[] t = trail.peekFirst();
        float ex = t[0] - partner.x, ey = t[1] - partner.y;
        float d = (float) Math.sqrt(ex * ex + ey * ey);
        if (d < 3f) { trail.pollFirst(); return; }
        float speed = (player.sprinting ? SPRINT_SPEED : WALK_SPEED) * 1.05f * dt
                * ElevationV50.speedFactor(area.terraces, partner.x, partner.y);
        float k = Math.min(d, speed);
        float destX=partner.x+ex/d*k, destY=partner.y+ey/d*k;
        if(!area.blocked(destX,destY)&&ElevationV50.canStep(area.terraces,partner.x,partner.y,destX,destY)) {
            partner.x=destX;partner.y=destY;
        } else { partner.walking=false; return; }
        partner.face(ex, ey);
        partner.walking = true;
        partner.sprinting = player.sprinting;
    }

    private void findTarget() {
        targetQuest = null; targetExamine = null; targetNpc = null; targetSide = null; targetTalk = null; targetRomance = false; targetAnimal = null; targetBed = false;
        float best = Float.MAX_VALUE;
        for (QuestDb.Interactable it : engine.interactables(area.id)) {
            float d = dist(it.x, it.y);
            if (d <= it.r && d < best) { best = d; targetQuest = it; }
        }
        if (targetQuest != null) return;
        best = Float.MAX_VALUE;
        for (QuestDb.Interactable it : engine.sideInteractables(area.id)) {
            float d = dist(it.x, it.y);
            if (d <= it.r && d < best) { best = d; targetSide = it; }
        }
        for (QuestDb.TownNpc n : engine.townNpcsNow(area.id)) {
            Actor ac = townActors.get(n.id); if (ac == null) continue;
            float d = dist(ac.x, ac.y);
            if (d <= 64 && d < best && engine.npcDialog(n) != null) { best = d; targetNpc = n; targetSide = null; }
        }
        if (targetSide != null || targetNpc != null) return;
        for (Animal an : animals) if (an.pettable && dist(an.x, an.y) < 40) { targetAnimal = an; return; }
        if (area.id.equals(Routes.room(p.route))) {
            float[] bed = bedSpot(area);
            if (dist(bed[0], bed[1]) < 60) { targetBed = true; return; }
        }
        if (partnerMode == 2 && dist(partner.x, partner.y) <= 58) {
            targetTalk = engine.partnerTalk(area.id);
            targetRomance = engine.romanceReady();
            if (targetTalk != null || targetRomance) return;
        }
        best = Float.MAX_VALUE;
        for (MapDb.Examine e : engine.examine(area)) {
            float d = dist(e.x, e.y);
            if (d <= e.r && d < best) { best = d; targetExamine = e; }
        }
    }

    /** Bed position from map data (v5.4 rescaled rooms); legacy constants as fallback. */
    private float[] bedSpot(MapDb.Area a) {
        if (a != null && !Float.isNaN(a.bedX)) return new float[]{a.bedX, a.bedY};
        return new float[]{p.route.equals("arland") ? 830f : 130f, 380f};
    }

    private float dist(float x, float y) { float dx = x - player.x, dy = y - player.y; return (float) Math.sqrt(dx * dx + dy * dy); }

    private void interact() {
        if (targetQuest != null) {
            player.face(targetQuest.x - player.x, targetQuest.y - player.y);
            runner.run(engine.actionsFor(targetQuest));
        } else if (targetSide != null) {
            player.face(targetSide.x - player.x, targetSide.y - player.y);
            runner.run(engine.actionsFor(targetSide));
        } else if (targetTalk != null) {
            player.face(partner.x - player.x, partner.y - player.y);
            partner.face(player.x - partner.x, player.y - partner.y);
            runner.run(engine.talkActions(targetTalk));
        } else if (targetRomance) {
            player.face(partner.x - player.x, partner.y - player.y);
            partner.face(player.x - partner.x, player.y - partner.y);
            controls.reset();
            romance.open(area.id, new RomanceOverlay.Listener() {
                public void completed(List<Map<String, Object>> acts, String message) {
                    saveNow();
                    toast(message);
                    if (message.startsWith("Hadiah")) game.audio.sfx("gift", .7f);
                    else if (message.startsWith("Kencan")) game.audio.sfx("heart", .7f);
                    else if (message.startsWith("Aksi berdua")) game.audio.sfx("hug", .6f);
                    runner.run(acts);
                }
            });
        } else if (targetAnimal != null) {
            player.face(targetAnimal.x - player.x, targetAnimal.y - player.y);
            targetAnimal.pet();
            String animalSfx = targetAnimal.type.startsWith("cat") ? "cat_meow"
                    : targetAnimal.type.startsWith("dog") ? "dog_bark"
                    : targetAnimal.type.startsWith("duck") ? "duck_quack" : "bird_chirp";
            game.audio.sfx(animalSfx, .52f);
            p.flags.add("PET_" + targetAnimal.type.replaceAll("_.*", "").toUpperCase(java.util.Locale.ROOT));
            if (p.petted.add(targetAnimal.type.replaceAll("_.*", ""))) toast("Teman berbulu baru! (" + p.petted.size() + " jenis)");
            if (partnerMode == 2) partner.showEmote("heart", 1.4f);
        } else if (targetBed) {
            askSleep();
        } else if (targetNpc != null) {
            Actor ac = townActors.get(targetNpc.id);
            if (ac != null) player.face(ac.x - player.x, ac.y - player.y);
            if (ac != null) ac.face(player.x - ac.x, player.y - ac.y);
            Map<String, Object> d = engine.npcDialog(targetNpc);
            if (d != null) runner.run(engine.resolve(com.arlandsofia.olu.logic.Json.objList(d, "actions")));
        } else if (targetExamine != null) {
            player.face(targetExamine.x - player.x, targetExamine.y - player.y);
            game.audio.sfx("page_turn", .42f);
            dialog.start(targetExamine.lines(p.route), null, p.route, dialogListener(), null);
            controls.reset();
        } else {
            toast("Dekati penanda ✦ untuk berinteraksi");
        }
    }

    private DialogBox.Listener dialogListener() {
        return new DialogBox.Listener() {
            public void onLine(StoryDb.Line line) {
                p.dialogueHistory.add(game.story.speaker(line.speaker).name, line.emotion, line.text, p.area, p.day);
                StoryDb.Emotion e = game.story.emotion(line.emotion);
                Actor who = line.speaker.equals(player.character) ? player : (line.speaker.equals(partner.character) && partnerMode != 0 ? partner : null);
                if (who == null) for (Actor ac : townActors.values()) if (ac.character.equals(game.story.speaker(line.speaker).sprite)) who = ac;
                if (who != null && e != null && e.emote != null) who.showEmote(e.emote, 1.8f);
                if ("jatuh_cinta".equals(line.emotion)) game.audio.sfx("cinema_heartbeat", 0.18f);
                else if ("lega".equals(line.emotion)) game.audio.sfx("flower_pick", 0.12f);
            }
            public void onChoice(StoryDb.Choice c) {
                p.dialogueHistory.add("Pilihanmu", "neutral", c.text, p.area, p.day);
                engine.addFlags(c.flags);
            }
        };
    }

    // ================================================================== fade & kartu chapter
    private void fade(Runnable mid, Runnable end) {
        fadePhase = 1; fadeAlpha = 0f; fadeMid = mid; fadeEnd = end;
        controls.reset();
    }

    private void updateFade(float dt) {
        if (fadePhase == 1) {
            fadeAlpha += dt * 4f;
            if (fadeAlpha >= 1f) { fadeAlpha = 1f; fadePhase = 2; Runnable m = fadeMid; fadeMid = null; if (m != null) m.run(); }
        } else if (fadePhase == 2) {
            fadeAlpha -= dt * 3.2f;
            if (fadeAlpha <= 0f) { fadeAlpha = 0f; fadePhase = 0; Runnable e = fadeEnd; fadeEnd = null; if (e != null) e.run(); }
        }
    }

    private void showCard(String title, String sub, Runnable done) {
        cardTitle = title; cardSub = sub; cardTime = 0f; cardDone = done;
        controls.reset();
    }

    private void finishCard() {
        cardTime = -1f;
        Runnable d = cardDone; cardDone = null;
        if (d != null) d.run();
    }

    // ================================================================== Presenter
    @Override
    public void playScene(String sceneId, Runnable done) {
        StoryDb.Scene sc = game.story.scene(sceneId);
        if (sc == null) { done.run(); return; }
        if (partnerMode != 0 && !cine.active()) {
            partner.face(player.x - partner.x, player.y - partner.y);
            if (partnerMode == 1) player.face(partner.x - player.x, partner.y - player.y);
        }
        controls.reset();
        dialog.start(sc.lines, sc.choices, p.route, dialogListener(), done);
    }

    /** Sebagian baris adegan (untuk cutscene yang menyisipkan gestur di antara baris). Pilihan hanya muncul bila bagian ini mencapai akhir adegan. */
    private void playScenePart(String sceneId, int from, int n, Runnable done) {
        StoryDb.Scene sc = game.story.scene(sceneId);
        if (sc == null) { done.run(); return; }
        int a = Math.max(0, Math.min(from, sc.lines.size())), b = n <= 0 ? sc.lines.size() : Math.min(sc.lines.size(), a + n);
        controls.reset();
        dialog.start(new ArrayList<>(sc.lines.subList(a, b)), b >= sc.lines.size() ? sc.choices : null, p.route, dialogListener(), done);
    }

    @Override
    public void openPuzzle(String puzzleId, ActionRunner.BoolCallback done) {
        QuestDb.Puzzle pz = engine.puzzle(puzzleId);
        if (pz == null) { done.done(true); return; }
        controls.reset();
        puzzle.open(pz, p.route, p.hasFlag(pz.hintFlag.get(p.route)), done);
    }

    @Override
    public void playLines(List<StoryDb.Line> lines, String speakerName, Runnable done) {
        controls.reset();
        dialog.start(lines, null, p.route, dialogListener(), done);
    }

    @Override
    public void openMinigame(String id, ActionRunner.IntCallback done) {
        controls.reset();
        minigame.open(id, game.quests.minigame(id), p.route, done);
    }

    @Override
    public void openShop(String shopId, Runnable done) {
        controls.reset();
        shop.open(shopId, done, new Runnable() { public void run() { saveNow(); } });
    }

    @Override
    public void cine(List<Map<String, Object>> cmds, final Runnable done) {
        controls.reset();
        cine.start(cmds, new Runnable() { public void run() {
            cineShowPartner = false; cineActors.clear();
            player.clearPose(); partner.clearPose(); partner.alpha = 1f; player.alpha = 1f;
            for (Actor t : townActors.values()) t.clearPose();
            p.x = player.x; p.y = player.y; p.dir = Actor.dirName(player.dir);
            trail.clear();
            if (partnerMode == 2 && Math.abs(partner.x - player.x) + Math.abs(partner.y - player.y) > 200) placeBeside();
            done.run();
        } });
    }

    @Override
    public void credits(Runnable done) {
        controls.reset();
        creditsTime = 0f; creditsDone = done;
        game.audio.music("cinema_our_tomorrow");
    }

    private void finishCredits() {
        creditsTime = -1f;
        Runnable d = creditsDone; creditsDone = null;
        if (d != null) d.run();
    }

    @Override
    public void emote(String who, String e) {
        Actor a = who.equals(player.character) ? player : (who.equals(partner.character) ? partner : townActors.get(who));
        if (a != null) a.showEmote(e, 1.8f);
    }

    @Override
    public void warp(final String areaId, final float x, final float y, final String dir, final Runnable done) {
        fade(new Runnable() { public void run() { enterArea(areaId, x, y, Actor.dirOf(dir), true); } }, done);
    }

    @Override
    public void chapterCard(String chapter, Runnable done) {
        showCard(game.story.chapterTitle(chapter), Routes.upper(p.route) + " ROUTE", done);
    }

    @Override
    public void chapterEnd(String chapter, final Runnable done) {
        String sub;
        if ("C01".equals(chapter))
            sub = "Kisah berlanjut di Chapter 2 pada versi berikutnya. Coba juga " + Routes.display(Routes.partner(p.route)) + " Route untuk melihat sisi lain.";
        else sub = "Progress tersimpan. Memory Book diperbarui.";
        if (replay) sub = "Replay selesai. Kembali ke menu utama.";
        showCard("✦ " + game.story.chapterTitle(chapter) + " — selesai ✦", sub, new Runnable() {
            public void run() {
                if (replay) game.switchScreen(new TitleScreen(game));
                else done.run();
            }
        });
    }

    @Override public void toast(String text) { toastText = text; toastTime = 2.6f; }
    @Override public void sfx(String id) { game.audio.sfx(id); }
    @Override public void music(String id) { game.audio.music(id); }

    @Override
    public void companionChanged(boolean on) {
        if (on) pendingComment = -1f;
        if (on) {
            if (partnerMode != 1) placeBeside();
            partnerMode = 2;
            trail.clear();
        } else {
            partnerMode = 0;
            p.holdingHands = false;
            refreshNpcs();
        }
    }

    @Override
    public void stepChanged() {
        refreshNpcs();
        if (!cine.active()) syncSoundscape();
        game.audio.sfx("quest_complete", .22f);
        objectiveFlash = 1.6f;
    }

    @Override public void onIdle() { saveNow(); }

    /** Simpan hanya saat tidak ada rangkaian aksi berjalan -> save selalu konsisten (tidak ada state setengah jadi). */
    private boolean saveNow() {
        if (replay || (runner.busy() && !shop.active())) return false;
        p.x = player.x; p.y = player.y; p.dir = Actor.dirName(player.dir);
        if (!game.store.saveSlot(p)) { toast("Gagal menyimpan! Periksa ruang penyimpanan."); return false; }
        autosaveAcc = 0f;
        java.util.Set<String> before = new java.util.LinkedHashSet<>(game.global.achievements);
        game.global.absorb(p);
        if (!game.store.saveGlobal(game.global)) {
            toast("Save slot aman, tetapi progres global gagal tersimpan.");
        } else {
            for (String unlocked : game.global.achievements) {
                if (before.contains(unlocked)) continue;
                Achievements.Def definition = Achievements.find(unlocked);
                if (definition != null) { toast("Prestasi dibuka: " + definition.name); break; }
            }
        }
        return true;
    }

    // ================================================================== overlay
    private void openDialogueHistory() {
        controls.reset();
        dialogueHistory.open(p.dialogueHistory);
    }

    private void openBook() {
        controls.reset();
        book.open(p, game.global, replay, new MemoryBookOverlay.ReplayHandler() {
            public void replay(final String chapter) {
                final Progress rp = p.replayFrom(chapter);
                if (rp == null) { toast("Replay belum tersedia"); return; }
                confirm = new ConfirmBox("Main ulang?", "Memainkan ulang " + game.story.chapterTitle(chapter) + ". Progres utama tetap aman dan tidak berubah.",
                        "Main ulang", new Runnable() { public void run() {
                            confirm = null; saveNow();
                            try { game.switchScreen(new GameScreen(game, rp, true, true)); } catch (RuntimeException e) { toast("Replay gagal: " + e.getMessage()); }
                        } },
                        "Batal", new Runnable() { public void run() { confirm = null; } });
            }
        });
    }

    /** Panduan selalu tersedia dari menu Pause, termasuk ketika pemain baru mulai. */
    private void showHowToPlay() {
        confirm = new ConfirmBox("Cara bermain",
                "GERAK: gunakan joystick di layar atau tombol WASD.\n"
                        + "LARI: tahan tombol LARI / Shift. AKSI: tombol AKSI / E.\n"
                        + "BUKU: lihat misi, tas, bab, dan 12 prestasi.\n"
                        + "Jelajahi area, ikuti penanda interaksi dan kompas misi, lalu ajak pasangan.\n"
                        + "Jeda > Pengaturan: ubah joystick, audio, dan tampilan.\n"
                        + "Gunakan Simpan sekarang sebelum keluar atau pindah versi.",
                "Mengerti", new Runnable() { public void run() { confirm = null; } }, null, null);
    }

    private void openPause() { controls.reset(); pauseOpen = true; }

    private void askMainMenu() {
        confirm = new ConfirmBox("Kembali ke menu?", replay ? "Replay akan diakhiri. Progres utama tidak berubah." : "Progress akan disimpan otomatis.",
                "Menu utama", new Runnable() { public void run() {
                    confirm = null;
                    if (!replay && !saveNow()) {
                        toast("Tidak bisa keluar: simpan gagal. Coba lagi.");
                        return;
                    }
                    game.switchScreen(new TitleScreen(game));
                } },
                "Batal", new Runnable() { public void run() { confirm = null; } });
    }

    // ================================================================== render
    @Override
    public void resize(int width, int height) {
        super.resize(width, height);
        worldView.update(width, height, false);
    }

    @Override
    protected void layout() {
        settingsPanel.safeInsets(insetL(),insetR(),insetT(),insetB());
        float top = uiH() - insetT() - 16;
        hudPause.set(uiW() - insetR() - 16 - 76, top - 66, 76, 66);
        hudBook.set(hudPause.x - 12 - 150, top - 66, 150, 66);
        controls.layout(uiW(), uiH(), insetL(), insetR(), insetB(), AdaptiveLayoutV43.controlScale(screenLayout(), game.settings.controlScale),
                game.settings.leftHanded, game.settings.floatingJoystick, game.settings.joystickSensitivity);
        AdaptiveLayoutV43.Metrics metrics = screenLayout();
        float bw = AdaptiveLayoutV43.menuWidth(metrics, 420f), bh = 52, gap = 8f;
        float y0 = AdaptiveLayoutV43.stackedMenuTop(metrics, pauseButtons.size(), bh, gap) - bh;
        for (int i = 0; i < pauseButtons.size(); i++) pauseButtons.get(i).set((uiW() - bw) / 2, y0 - i * (bh + gap), bw, bh);
    }

    @Override
    protected void drawWorld() {
        float zoom = cine.camActive() ? Math.max(0.5f, cine.zoom()) : 1f;
        // Wider world view only during free exploration; scripted cinematics retain their zoom.
        float framing = cine.camActive() ? 1f : CameraFramingV52.gameplayScale(game.settings.cameraDistance, area.indoor);
        // v5.4: exploration snaps to a whole number of screen pixels per texel.
        int pixelGrid = 0;
        if (!cine.camActive() && game.settings.pixelPerfect && worldView.getScreenHeight() > 0) {
            pixelGrid = PixelPerfectV54.pixelsPerUnit(framing, worldView.getWorldHeight(), worldView.getScreenHeight());
            framing = PixelPerfectV54.zoom(framing, worldView.getWorldHeight(), worldView.getScreenHeight());
        }
        worldCam.zoom = framing / zoom;
        float ww = worldView.getWorldWidth() * framing / zoom;
        float wh = worldView.getWorldHeight() * framing / zoom;
        boolean inCutsceneCamera = cine.camActive();
        float focusX = inCutsceneCamera ? cine.camX() : player.x;
        float focusY = inCutsceneCamera ? area.h - cine.camY() : area.h - player.y + 24 + lastTerrainHeight*.55f;
        // Look-ahead kecil hanya saat eksplorasi, tidak merusak komposisi cutscene.
        if (!inCutsceneCamera && player.walking && game.settings.smoothCamera) {
            if (player.dir == Assets.DIR_LEFT) focusX -= 12f;
            if (player.dir == Assets.DIR_RIGHT) focusX += 12f;
            if (player.dir == Assets.DIR_UP) focusY += 8f;
            if (player.dir == Assets.DIR_DOWN) focusY -= 8f;
        }
        float cx = area.w <= ww ? area.w / 2 : MathUtils.clamp(focusX, ww / 2, area.w - ww / 2);
        float cy = area.h <= wh ? area.h / 2 : MathUtils.clamp(focusY, wh / 2, area.h - wh / 2);
        cameraRig.follow(cx, cy, frameDt, !inCutsceneCamera && game.settings.smoothCamera);
        float smoothX = area.w <= ww ? area.w / 2 : MathUtils.clamp(cameraRig.x(), ww / 2, area.w - ww / 2);
        float smoothY = area.h <= wh ? area.h / 2 : MathUtils.clamp(cameraRig.y(), wh / 2, area.h - wh / 2);
        if (pixelGrid > 0) worldCam.position.set(PixelPerfectV54.snap(smoothX, pixelGrid), PixelPerfectV54.snap(smoothY, pixelGrid), 0);
        else worldCam.position.set(zoom == 1f ? Math.round(smoothX) : smoothX, zoom == 1f ? Math.round(smoothY) : smoothY, 0);
        visibleL = worldCam.position.x - ww / 2 - 110;
        visibleR = worldCam.position.x + ww / 2 + 110;
        visibleB = worldCam.position.y - wh / 2 - 110;
        visibleT = worldCam.position.y + wh / 2 + 110;
        worldView.apply();
        worldCam.update();
        game.batch.setProjectionMatrix(worldCam.combined);
        game.batch.begin();
        game.batch.setColor(1, 1, 1, 1);
        game.batch.draw(mapTex, 0, 0, area.w, area.h);
        worldFx.drawSceneAtmosphere(game.batch, game.assets.pixel, glow, sparkle,
                area.id, area.indoor, area.h, worldCam.position.x, worldCam.position.y,
                ww, wh, time, game.settings.visualQuality, WorldClock.isNight(p.minute));
        worldFx.drawWorldBackdropV462(game.batch,area.id,area.indoor,
                "rain".equals(weather()),p.minute,worldCam.position.x,worldCam.position.y,
                ww,wh,time,game.settings.visualQuality);
        for (MapDb.Prop pr : area.props) if ("floor".equals(pr.def.layer) && propVisible(pr)) drawProp(pr);
        // v5.0: original 2.5D decks and real stairs overlay map art without
        // mutating the baked backgrounds or old story/door coordinates.
        for(MapDb.Terrace terrace:area.terraces)drawTerraceBase(terrace);
        // v3.7: riak dan kilau air berada pada lapisan lantai; sebelum karakter/prop.
        drawWater();

        drawList.clear(); drawCursor = 0;
        for (MapDb.Prop pr : area.props) if (!"floor".equals(pr.def.layer) && propVisible(pr)) addDraw(pr.y, pr);
        drawMarkers.clear();
        drawMarkers.addAll(engine.interactables(area.id));
        List<QuestDb.Interactable> its = drawMarkers;
        List<QuestDb.Interactable> sides = engine.sideInteractables(area.id);
        for (QuestDb.Interactable it : its) if (it.sprite != null && visibleActor(it.sprite.x, it.sprite.y)) addDraw(it.sprite.y, it.sprite);
        for (QuestDb.Interactable it : sides) if (it.sprite != null && visibleActor(it.sprite.x, it.sprite.y)) addDraw(it.sprite.y, it.sprite);
        for(MapDb.Terrace t:area.terraces) addDraw(t.y+t.h-1f,t); // front lip occludes upper feet
        player.terrainLift=ElevationV50.heightAt(area.terraces,player.x,player.y);
        addDraw(player.y, player);
        if (partnerMode != 0 || cineShowPartner) {
            partner.terrainLift=ElevationV50.heightAt(area.terraces,partner.x,partner.y);
            addDraw(partner.y, partner);
        }
        for (Actor ac : townActors.values()) if (visibleActor(ac.x,ac.y)) {
            ac.terrainLift=ElevationV50.heightAt(area.terraces,ac.x,ac.y);
            addDraw(ac.y, ac);
        }
        for (Actor ac : cineActors.values()) if (visibleActor(ac.x,ac.y)) {
            ac.terrainLift=ElevationV50.heightAt(area.terraces,ac.x,ac.y);
            addDraw(ac.y, ac);
        }
        for (Animal an : animals) if (visibleActor(an.x,an.y)) addDraw(an.y, an);
        for (QuestDb.Interactable it : sides) if (it.marker) its.add(it);
        Collections.sort(drawList, bySortY);
        for (DrawItem o : drawList) {
            Object r = o.value;
            if (r instanceof MapDb.Terrace) drawTerraceFront((MapDb.Terrace)r);
            else if (r instanceof MapDb.Prop) drawProp((MapDb.Prop) r);
            else if (r instanceof QuestDb.Sprite) {
                QuestDb.Sprite s = (QuestDb.Sprite) r;
                Texture t = game.assets.tex(s.image);
                float bob = s.bob ? MathUtils.sin(time * 3f + s.x) * 3f : 0f;
                game.batch.draw(t, Math.round(s.x - t.getWidth() / 2f), Math.round(area.h - s.y + bob), t.getWidth(), t.getHeight());
            } else if (r instanceof Animal) ((Animal) r).draw(game.batch, game.assets, area.h, shadow);
            else ((Actor) r).draw(game.batch, game.assets, area.h, shadow);
        }

        worldFx.draw(game.batch, game.settings.visualQuality);
        if (realm()) { // partikel cahaya Memory Realm
            for (int i = 0; i < 26; i++) {
                float sx = (i * 211.3f + time * 9f * (1 + i % 3)) % area.w;
                float sy = (i * 137.9f + time * 14f) % area.h;
                float al = 0.35f + 0.35f * MathUtils.sin(time * 2f + i);
                game.batch.setColor(1f, 0.93f, 0.75f, al);
                game.batch.draw(sparkle, sx, sy, 9, 9);
            }
            game.batch.setColor(1, 1, 1, 1);
        }

        if (game.settings.showHints) {
            for (QuestDb.Interactable it : its) {
                float my;
                if (it.sprite != null) my = it.sprite.y - game.assets.tex(it.sprite.image).getHeight() - 8;
                else if (partnerMode == 1 && Math.abs(partner.x - it.x) < 20 && Math.abs(partner.y - it.y) < 20) my = partner.y - partner.drawHeight() - 8;
                else my = it.y - 40;
                float bob = MathUtils.sin(time * 4f + it.x) * 3f;
                boolean gold = it.id.startsWith("shard") || it.id.startsWith("WE27_") || it.id.startsWith("V50_");
                if (gold) game.batch.setColor(1f, 0.85f, 0.45f, 1f); else game.batch.setColor(0.97f, 0.7f, 0.83f, 1f);
                game.batch.draw(marker, it.x - 7, area.h - my + bob, 14, 14);
            }
            game.batch.setColor(1, 1, 1, 1);
        }
        drawEmote(player);
        if (partnerMode != 0 || cineShowPartner) drawEmote(partner);
        for (Actor ac : townActors.values()) drawEmote(ac);
        for (Actor ac : cineActors.values()) drawEmote(ac);
        if (partnerMode == 2 && partner.emote == null && engine.partnerTalk(area.id) != null && game.settings.showHints) {
            Texture ht = game.assets.tex("ui/emote_heart.png");
            float bob = MathUtils.sin(time * 3f) * 2f;
            game.batch.setColor(1, 1, 1, 0.75f);
            game.batch.draw(ht, partner.x - 8, area.h - partner.y + partner.drawHeight() + 2 + bob, 16, 16);
            game.batch.setColor(1, 1, 1, 1);
        }
        drawTerraceAtmosphere();
        drawAmbient();
        {
            float vw = worldView.getWorldWidth() * worldCam.zoom, vh = worldView.getWorldHeight() * worldCam.zoom;
            float left = worldCam.position.x - vw / 2, bottom = worldCam.position.y - vh / 2;
            worldFx.drawForeground(game.batch, left, bottom, vw, vh, area.ambient, time, game.settings.visualQuality);
            worldFx.drawWorldForegroundV462(game.batch,area.id,area.indoor,
                    "rain".equals(weather()),WorldClock.BERANGIN.equals(weather()),p.minute,
                    worldCam.position.x,worldCam.position.y,vw,vh,time,game.settings.visualQuality);
            worldFx.drawVignette(game.batch, left, bottom, vw, vh, game.settings.visualQuality);
            cine.drawWorld(game.batch, area.h, left, bottom, vw, vh);
        }
        game.batch.end();
    }

    private String weather() {
        String w = engine.weatherNow();
        return WorldClock.HUJAN.equals(w) ? "rain" : w;
    }

    /** Kilau bergerak di permukaan air (kolam, danau, air mancur). */
    private void drawWater() {
        if (area.water.isEmpty()) return;
        for (float[] w : area.water) {
            int visual = game.settings.visualQuality;
            int n = (int) Math.min(visual == 2 ? 58 : 40, w[2] * w[3] / (visual == 2 ? 660f : 900f) + (visual == 0 ? 3 : 6));
            if (visual == 0) n = Math.max(3, n / 3);
            for (int i = 0; i < n; i++) {
                float ph = time * 0.6f + i * 1.37f;
                float u = ((i * 0.618f) % 1f) * 2f - 1f, v = ((i * 0.377f + 0.21f) % 1f) * 2f - 1f;
                if (u * u + v * v > 0.85f) continue;
                float al = Math.max(0f, MathUtils.sin(ph * 2f)) * 0.7f;
                float wx = w[0] + u * w[2] + MathUtils.sin(ph) * 6f, wy = w[1] + v * w[3];
                game.batch.setColor(0.9f, 0.97f, 1f, al);
                game.batch.draw(game.assets.pixel, wx, area.h - wy, 6 + (i % 3) * 2, 1.5f);
            }
            worldFx.drawRipples(game.batch, w[0], area.h - w[1], w[2], w[3], time, visual, "rain".equals(weather()));
            worldFx.drawWaterGlintsV462(game.batch,w[0],area.h-w[1],w[2],w[3],time,visual,"rain".equals(weather()));
        }
        game.batch.setColor(1, 1, 1, 1);
    }

    /** Partikel ambient (kelopak, kunang-kunang, bintang) dan hujan, relatif terhadap kamera. */
    private void drawAmbient() {
        float ww = worldView.getWorldWidth() * worldCam.zoom, wh = worldView.getWorldHeight() * worldCam.zoom;
        float left = worldCam.position.x - ww / 2, bottom = worldCam.position.y - wh / 2;
        String amb = area.ambient;
        float[] L = lightNow();
        boolean rain = "rain".equals(weather()) && !isIndoor();
        boolean night = !isIndoor() && L[3] > 0.18f;
        int visual = game.settings.visualQuality;
        if (visual > 0 && !isIndoor() && !realm()) {
            float halo = night ? (visual == 2 ? 220f : 140f) : (visual == 2 ? 250f : 165f);
            float hx = left + ww * (night ? 0.82f : 0.18f);
            float hy = bottom + wh * 0.80f;
            if (night) game.batch.setColor(0.72f, 0.78f, 1f, rain ? 0.12f : 0.18f);
            else game.batch.setColor(1f, 0.78f, 0.54f, rain ? 0.14f : 0.22f);
            game.batch.draw(glow, hx - halo / 2f, hy - halo / 2f, halo, halo);
            game.batch.setColor(1f, 1f, 1f, 1f);
        }
        if (amb != null && !rain) {
            for (int i = 0; i < (visual == 2 ? 28 : visual == 1 ? 18 : 8); i++) {
                float fx = ((i * 0.6180339f + time * (0.012f + (i % 5) * 0.004f)) % 1f) * ww;
                float fy = ((i * 0.3819f + ("petals".equals(amb) ? -time * 0.03f : MathUtils.sin(time * 0.3f + i) * 0.02f)) % 1f + 1f) % 1f * wh;
                if ("petals".equals(amb)) { game.batch.setColor(1f, 0.78f, 0.86f, 0.85f); game.batch.draw(game.assets.pixel, left + fx, bottom + fy, 3, 2); }
                else if ("fireflies".equals(amb)) { float al = 0.3f + 0.7f * Math.max(0, MathUtils.sin(time * 2 + i)); game.batch.setColor(1f, 0.95f, 0.55f, al); game.batch.draw(sparkle, left + fx, bottom + fy, 7, 7); }
                else { float al = 0.3f + 0.6f * Math.max(0, MathUtils.sin(time * 1.5f + i * 2)); game.batch.setColor(1f, 0.96f, 0.85f, al); game.batch.draw(sparkle, left + fx, bottom + fy, 6, 6); }
            }
        }
        if (rain) {
            int rainCount = visual == 2 ? rainX.length : visual == 1 ? 90 : 48;
            for (int i = 0; i < rainCount; i++) {
                float fx = ((rainX[i] + time * 0.05f) % 1f) * (ww + 60) - 30;
                float fy = ((rainY[i] - time * (1.1f + (i % 4) * 0.15f)) % 1f + 1f) % 1f * (wh + 40);
                game.batch.setColor(0.75f, 0.85f, 1f, 0.55f);
                game.batch.draw(game.assets.pixel, left + fx, bottom + fy, 1, 9);
            }
        }
        QuestDb.Step st = engine.step();
        night = L[3] >= 0.2f && !rain;
        if (!isIndoor() && !rain && !night && !realm()) { // kupu-kupu kecil di area luar siang hari
            for (int i = 0; i < (visual == 2 ? 7 : visual == 1 ? 4 : 2); i++) {
                float bx = ((i * 0.618f + MathUtils.sin(time * 0.11f + i) * 0.18f) % 1f + 1f) % 1f * ww;
                float by = ((i * 0.37f + MathUtils.cos(time * 0.09f + i * 2) * 0.15f) % 1f + 1f) % 1f * wh;
                float flap = Math.abs(MathUtils.sin(time * 14f + i)) * 2.2f + 0.6f;
                if (i % 2 == 0) game.batch.setColor(1f, 0.85f, 0.4f, 0.95f); else game.batch.setColor(0.95f, 0.75f, 0.95f, 0.95f);
                game.batch.draw(game.assets.pixel, left + bx - flap - 0.5f, bottom + by, flap, 2f);
                game.batch.draw(game.assets.pixel, left + bx + 0.5f, bottom + by, flap, 2f);
            }
        }
        float tintA = 0f; Color tc = null;
        if (rain || ("rain".equals(weather()) && isIndoor())) { tc = tint.set(0.25f, 0.3f, 0.42f, 1f); tintA = isIndoor() ? 0.12f : 0.28f; }
        else if (L[3] > 0.001f) { tc = tint.set(L[0], L[1], L[2], 1f); tintA = isIndoor() ? L[3] * 0.45f : L[3]; }
        if (!isIndoor() && !realm() && WorldClock.BERAWAN.equals(weather())) { game.batch.setColor(0.55f, 0.58f, 0.66f, 0.13f); game.batch.draw(game.assets.pixel, left - 10, bottom - 10, ww + 20, wh + 20); }
        if (!isIndoor() && !realm() && WorldClock.BERANGIN.equals(weather())) { // daun & kelopak terbawa angin
            for (int i = 0; i < (visual == 2 ? 35 : visual == 1 ? 22 : 10); i++) {
                float fx = ((i * 0.618f + time * (0.09f + (i % 4) * 0.02f)) % 1f) * (ww + 40) - 20;
                float fy = ((i * 0.37f + MathUtils.sin(time * 1.3f + i) * 0.03f) % 1f + 1f) % 1f * wh;
                if (i % 3 == 0) game.batch.setColor(1f, 0.78f, 0.86f, 0.9f); else game.batch.setColor(0.55f, 0.75f, 0.4f, 0.9f);
                game.batch.draw(game.assets.pixel, left + fx, bottom + fy, 3, 2);
            }
        }
        if (tc != null && tintA > 0) {
            game.batch.setColor(tc.r, tc.g, tc.b, tintA);
            game.batch.draw(game.assets.pixel, left - 10, bottom - 10, ww + 20, wh + 20);
        }
        if ("dark".equals(area.ambient)) { // gua: lingkar cahaya di sekitar pemain + pendar kristal
            Texture dk = game.assets.tex("ui/darkness.png");
            float R = 230f, px = player.x, py = area.h - player.y + 26;
            game.batch.setColor(1, 1, 1, 1);
            game.batch.draw(dk, px - R, py - R, R * 2, R * 2);
            game.batch.setColor(0.03f, 0.02f, 0.07f, 0.9f);
            game.batch.draw(game.assets.pixel, left - 10, bottom - 10, px - R - left + 10, wh + 20);
            game.batch.draw(game.assets.pixel, px + R, bottom - 10, left + ww - px - R + 10, wh + 20);
            game.batch.draw(game.assets.pixel, px - R, bottom - 10, R * 2, py - R - bottom + 10);
            game.batch.draw(game.assets.pixel, px - R, py + R, R * 2, bottom + wh - py - R + 10);
            for (MapDb.Prop pr : area.props) {
                if (!pr.def.image.contains("crystal")) continue;
                Texture t = game.assets.tex(pr.def.image);
                float s = 70 + MathUtils.sin(time * 1.6f + pr.x) * 6f;
                game.batch.setColor(0.7f, 0.85f, 1f, 0.5f);
                game.batch.draw(sparkle, pr.x - s / 2, area.h - pr.y + t.getHeight() / 2f - s / 2, s, s);
            }
            game.batch.setColor(1, 1, 1, 1);
        }
        if (night || rain || realm()) { // lampu jalan & lentera berpendar saat malam/hujan
            for (MapDb.Prop pr : area.props) {
                String img = (pr.alt != null && pr.altFlag != null && p.hasFlag(pr.altFlag) ? pr.alt : pr.def).image;
                if (!(img.contains("lamp") || img.contains("lantern_post") || img.contains("lantern_on"))) continue;
                Texture t = game.assets.tex(img);
                float gx = pr.x, gy = area.h - pr.y + t.getHeight() - 6;
                if (gx < left - 60 || gx > left + ww + 60 || gy < bottom - 60 || gy > bottom + wh + 60) continue;
                float s = 46 + MathUtils.sin(time * 2f + pr.x) * 3f;
                game.batch.setColor(1f, 0.85f, 0.55f, 0.45f);
                game.batch.draw(sparkle, gx - s / 2, gy - s / 2, s, s);
            }
        }
        game.batch.setColor(1, 1, 1, 1);
    }

    private boolean isIndoor() { return area.indoor; }
    private static String animalName(String t) {
        if (t.startsWith("cat")) return "kucing"; if (t.equals("dog")) return "anjing"; if (t.equals("duck")) return "bebek";
        if (t.equals("chicken")) return "ayam"; if (t.equals("rabbit")) return "kelinci"; return t;
    }
    /** cahaya efektif: tint step cerita bila ada, selain itu dari jam dunia. {r,g,b,a} */
    private float[] lightNow() {
        QuestDb.Step st = engine.step();
        if (st != null && st.tint != null) { Color c = Color.valueOf(st.tint); return new float[]{c.r, c.g, c.b, st.tintAlpha}; }
        if (realm()) return new float[]{1, 1, 1, 0};
        return WorldClock.light(p.minute);
    }
    private boolean realm() { return "memory".equals(area.music) || "star".equals(area.music) || "tender".equals(area.music); }

    /** Musik kota/cerita dengan 25 komposisi baru; perintah musik khusus quest selalu didahulukan. */
    private String musicFor() {
        QuestDb.Step st = engine.step();
        String override = st != null && st.music != null && (st.musicAreas.isEmpty() || st.musicAreas.contains(area.id)) ? st.music : null;
        return SoundscapePlan.musicFor(area.id, area.music, weather(), isIndoor(), p.minute, p.day,
                game.settings.variedMusic, override);
    }

    private void syncSoundscape() {
        if (area == null) return;
        game.audio.music(musicFor());
        game.audio.ambience(SoundscapePlan.ambienceFor(area.id, weather(), isIndoor(), p.minute));
    }

    /** Platform PNG covers a pixel-art deck, retaining wall, and traversable stairs. */
    private void drawTerraceBase(MapDb.Terrace t){
        float x=t.x-20f, y=area.h-(t.y-40f+t.h+t.stairLength+64f);
        float w=t.w+40f, h=t.h+t.stairLength+64f;
        if(x>visibleR||x+w<visibleL||y>visibleT||y+h<visibleB)return;
        game.batch.setColor(1f,1f,1f,1f);
        game.batch.draw(game.assets.tex(t.image),x,y,w,h);
    }

    /** Foreground lip participates in world Y-sort for convincing edge overlap. */
    private void drawTerraceFront(MapDb.Terrace t){
        float x=t.x-20f, y=area.h-(t.y-40f+t.h+t.stairLength+64f);
        float w=t.w+40f,h=t.h+t.stairLength+64f;
        if(x>visibleR||x+w<visibleL||y>visibleT||y+h<visibleB)return;
        game.batch.setColor(1f,1f,1f,1f);
        game.batch.draw(game.assets.tex(t.front),x,y,w,h);
    }

    /** Lightweight VFX on terraces; respects visualQuality and time/weather. */
    private void drawTerraceAtmosphere(){
        if(game.settings.visualQuality==0||area.terraces.isEmpty())return;
        for(MapDb.Terrace t:area.terraces){
            float cx=t.x+t.w*.5f, cy=area.h-t.y-t.h*.45f+t.rise;
            if(!visibleActor(cx,t.y+t.h*.5f))continue;
            boolean magic="memory".equals(t.style)||"star".equals(t.style)||"crystal".equals(t.style)
                    ||"night".equals(t.style)||"future".equals(t.style);
            boolean night=WorldClock.isNight(p.minute);
            if(!magic && !night)continue;
            int count=game.settings.visualQuality>1?11:5;
            for(int i=0;i<count;i++){
                float sx=cx+MathUtils.sin(i*12.71f+time*.36f)*(t.w*.46f);
                float sy=cy+MathUtils.cos(i*7.37f+time*.48f)*(t.h*.40f)+MathUtils.sin(time*.92f+i)*7f;
                float alpha=.13f+.20f*(.5f+.5f*MathUtils.sin(time*1.4f+i*2.9f));
                game.batch.setColor(magic ? .84f : 1f,magic ? .78f : .86f,1f,alpha);
                game.batch.draw(sparkle,sx-2f,sy-2f,4.5f,4.5f);
            }
        }
        game.batch.setColor(1f,1f,1f,1f);
    }

    private void drawProp(MapDb.Prop pr) {
        MapDb.PropDef def = pr.alt != null && pr.altFlag != null && p.hasFlag(pr.altFlag) ? pr.alt : pr.def;
        Texture t = game.assets.tex(def.image);
        float propX = pr.x - t.getWidth() / 2f, propY = area.h - pr.y;
        if (propX > visibleR || propX + t.getWidth() < visibleL || propY > visibleT || propY + t.getHeight() < visibleB) return;
        // v3.7: local ground-contact shadow follows identical Y-sort as the prop;
        // stays underneath its sprite, and never modifies collision or quest geometry.
        if (game.settings.visualQuality > 0 && !"floor".equals(def.layer)
                && def.cw >= 8f && def.ch > 0f) {
            float ww = WorldLightingV37.width(def.cw);
            float sx = WorldLightingV37.shadowOffsetX(p.minute, isIndoor(), "rain".equals(weather()), game.settings.visualQuality);
            float opacity = WorldLightingV37.contactOpacity(p.minute, isIndoor(), "rain".equals(weather()), game.settings.visualQuality);
            game.batch.setColor(1f, 1f, 1f, opacity);
            game.batch.draw(shadow, Math.round(pr.x + sx - ww * 0.5f),
                    Math.round(area.h - pr.y - 7f), ww, 14f);
            game.batch.setColor(1f, 1f, 1f, 1f);
        }
        String img = def.image;
        boolean lamp = img.contains("lamp") || img.contains("lantern");
        boolean crystal = img.contains("crystal");
        boolean warmWindow = img.contains("window") || img.contains("campfire") || img.contains("fire");
        boolean glowAllowed = game.settings.visualQuality > 0 &&
                (crystal || (lamp && (isIndoor() || realm() || WorldClock.isNight(p.minute) || "rain".equals(weather())))
                    || (warmWindow && (isIndoor() || WorldClock.isNight(p.minute))));
        if (glowAllowed) {
            float cx = pr.x;
            float cy = area.h - pr.y + t.getHeight() * (lamp ? 0.78f : 0.55f);
            float s = (lamp ? 92f : crystal ? 84f : 70f) * (game.settings.visualQuality == 2 ? 1.15f : 0.85f);
            float strength = game.settings.visualQuality == 2 ? 1f : 0.6f;
            if (lamp) game.batch.setColor(1f, 0.84f, 0.56f, 0.34f * strength);
            else if (crystal) game.batch.setColor(0.72f, 0.88f, 1f, 0.30f * strength);
            else game.batch.setColor(1f, 0.90f, 0.72f, 0.20f * strength);
            game.batch.draw(glow, cx - s / 2f, cy - s / 2f, s, s);
            game.batch.setColor(1, 1, 1, 1);
        }
        // High-quality animation: move only the upper third of a tree (the roots/trunk
        // remain fixed and collision unchanged). TextureRegions are cached once per texture.
        if (game.settings.visualQuality == 2 && (img.contains("/tree_") || img.contains("/wishing_tree"))
                && t.getHeight() >= 60 && !"floor".equals(def.layer)) {
            TextureRegion[] split = animatedTreeRegions.get(t);
            if (split == null) {
                int th = Math.max(12, t.getHeight() / 3);
                split = new TextureRegion[]{new TextureRegion(t, 0, th, t.getWidth(), t.getHeight()-th),
                        new TextureRegion(t, 0, 0, t.getWidth(), th)};
                animatedTreeRegions.put(t, split);
            }
            float sway = MathUtils.sin(time * 1.05f + pr.x * 0.013f + pr.y * 0.009f) * 2.0f;
            float x = Math.round(pr.x - t.getWidth() / 2f), y = Math.round(area.h - pr.y);
            int bottomH = split[0].getRegionHeight();
            game.batch.draw(split[0], x, y, t.getWidth(), bottomH);
            game.batch.draw(split[1], x + sway, y + bottomH, t.getWidth(), split[1].getRegionHeight());
        } else {
            game.batch.draw(t, Math.round(pr.x - t.getWidth() / 2f), Math.round(area.h - pr.y), t.getWidth(), t.getHeight());
        }
    }

    private void drawEmote(Actor a) {
        if (a.emote == null) return;
        Texture t = game.assets.tex("ui/emote_" + a.emote + ".png");
        float pop = Math.min(1f, (1.8f - a.emoteTime) * 6f);
        game.batch.draw(t, a.x - 11, area.h - a.y + a.terrainLift + a.drawHeight() + 2, 22 * pop, 22 * pop);
    }

    /** Konversi koordinat peta -> UI (kedua viewport menutupi seluruh layar). */
    private final Vector2 tmpV = new Vector2();
    private Vector2 mapToUi(float mx, float my) {
        float ww = worldView.getWorldWidth() * worldCam.zoom, wh = worldView.getWorldHeight() * worldCam.zoom;
        float left = worldCam.position.x - ww / 2, bottom = worldCam.position.y - wh / 2;
        return tmpV.set((mx - left) * uiW() / ww, ((area.h - my) - bottom) * uiH() / wh);
    }

    @Override
    protected void drawUi() {
        Assets a = game.assets;
        float W = uiW(), H = uiH(), inL = insetL(), inR = insetR(), inT = insetT(), inB = insetB();
        boolean overlay = dialog.active() || puzzle.active() || minigame.active() || creditsTime >= 0 || book.active() || shop.active() || romance.active() || pauseOpen || settingsOpen || cardTime >= 0 || cine.active();
        if (cine.active() || cine.letterboxed()) { drawCineUi(W, H, inL, inR, inB); return; }

        // label pintu terdekat
        if (!overlay) {
            for (MapDb.Door d : area.doors) {
                float dx = d.cx() - player.x, dy = d.cy() - player.y;
                if (dx * dx + dy * dy < 120 * 120 && d.label.length() > 0) {
                    Vector2 v = mapToUi(d.cx(), d.y - 6);
                    ui.text(a.label, d.label, v.x - 200, v.y + 34, Ui.WHITE, 0.9f, Align.center, 400);
                }
            }
        }

        // HUD kiri atas
        float hx = inL + 16, hy = H - inT - 16;
        float aw = Math.max(360, ui.measure(a.body, area.name, 1.05f) + 140);
        ui.panel(a.panelDark, hx, hy - 126, aw, 126, 0.95f);
        ui.rect(hx + 14, hy - 36, aw - 28, 3, Ui.PINK, 0.45f);
        ui.text(a.body, area.name, hx + 22, hy - 16, Ui.CREAM, 1.05f, Align.left, 0);
        String wz = weather(); String wl = "rain".equals(wz) ? "Hujan" : WorldClock.BERAWAN.equals(wz) ? "Berawan" : WorldClock.BERANGIN.equals(wz) ? "Berangin" : "Cerah";
        ui.text(a.body, WorldClock.dayName(p.day) + " • Hari " + p.day + " • " + WorldClock.hhmm(p.minute) + " • " + wl, hx + 22, hy - 92, Ui.GOLD, 0.72f, Align.left, 0);
        ui.image(coinIcon, hx + aw - 136, hy - 34, 24, 24, 1f);
        ui.text(a.body, String.valueOf(p.coins), hx + aw - 106, hy - 18, Ui.GOLD, 0.84f, Align.left, 0);
        ui.text(a.body, "♥ " + p.affection + "/100", hx + aw - 136, hy - 54, Ui.PINK, 0.80f, Align.left, 0);
        if (p.holdingHands && partnerMode == 2) ui.text(a.body, "♡ Gandengan", hx + aw - 139, hy - 108, Ui.PINK, 0.67f, Align.left, 0);
        QuestDb.Step st = engine.step();
        String chName = st == null ? "" : (st.chapter.equals("PRO") ? "PROLOG" : "CHAPTER " + st.chapter.substring(1).replaceFirst("^0", ""));
        ui.text(a.body, Routes.upper(p.route) + " ROUTE • " + chName, hx + 22, hy - 56, Ui.LAVENDER, 0.72f, Align.left, 0);

        // misi aktif (tengah atas)
        String obj = engine.objectiveText();
        float ow = Math.min(W - aw - 420 - inL - inR, Math.max(360, ui.measure(a.body, obj, 0.9f) + 60));
        float ox = Math.max(hx + aw + 14, (W - ow) / 2);
        float flash = objectiveFlash > 0 ? 0.5f + 0.5f * MathUtils.sin(objectiveFlash * 12f) : 0f;
        ui.panel(a.panelDark, ox, hy - 88, ow, 88, 0.95f);
        if (flash > 0) ui.rect(ox + 10, hy - 84, ow - 20, 4, Ui.GOLD, flash);
        ui.text(a.body, "✦ MISI AKTIF", ox, hy - 14, Ui.PINK, 0.66f, Align.center, ow);
        float objScale = Math.min(0.9f, 0.9f * (ow - 40) / Math.max(1f, ui.measure(a.body, obj, 0.9f)));
        ui.text(a.body, obj, ox + 20, hy - 46, Ui.CREAM, objScale, Align.center, ow - 40);
        // Petunjuk arah untuk interaksi *utama yang saat ini aktif*, bukan jalur semu lintas peta.
        if (!overlay && game.settings.showHints) {
            if (questRouteRefresh<=0f) {
                cachedQuestRoute=QuestPathV52.hint(area,player.x,player.y,engine.interactables(area.id),p.route);
                questRouteRefresh=.65f;
            }
            QuestCompass.Hint hint=cachedQuestRoute;
            if (hint != null) {
                float ww = Math.max(300, Math.min(ow + 40, 510));
                ui.panel(a.panelDark, ox + (ow - ww) / 2, hy - 133, ww, 40, .89f);
                String direction = hint.text();
                if (direction.length() > 62) direction = direction.substring(0, 59) + "...";
                ui.text(a.body, direction, ox + (ow - ww) / 2 + 12, hy - 106,
                        Ui.GOLD, .63f, Align.center, ww - 24);
            }
        }
        // Notifikasi kecil: event hanya tampil bila area/jam/cuaca/route dan batas harian cocok.
        if (!overlay && game.settings.showHints) {
            for (QuestDb.WorldEvent ev : game.quests.worldEvents) {
                if (ev.area.equals(area.id) && engine.worldEventBlock(ev.id, area.id) == null) {
                    ui.text(a.body, "✦ EVENT HARI INI: " + ev.title, ox + 20, hy - 72,
                            Ui.GOLD, 0.56f, Align.center, ow - 40);
                    break;
                }
            }
        }

        if (!overlay && engine.deliveryOpen()) {
            ui.panel(a.panelDark, W / 2 - 255, hy - 151, 510, 45, 0.94f);
            ui.text(a.body, "Antar surat: " + engine.deliveredToday() + "/3  •  Plaza / Jalan Kota / Tepi Danau",
                    W / 2 - 240, hy - 118, Ui.GOLD, 0.73f, Align.center, 480);
        }
        ui.button(hudBook);
        ui.button(hudPause);
        if (replay) {
            ui.panel(a.panelDark, W / 2 - 250, hy - 140, 500, 44, 0.9f);
            ui.text(a.body, "MODE REPLAY • progres tidak disimpan", W / 2 - 250, hy - 108, Ui.GOLD, 0.72f, Align.center, 500);
        }

        if (!overlay && fadePhase == 0) {
            // Pilihan kontrol berlaku segera setelah pemain menutup Pengaturan.
            controls.layout(W, H, inL, inR, inB, AdaptiveLayoutV43.controlScale(screenLayout(), game.settings.controlScale),
                    game.settings.leftHanded, game.settings.floatingJoystick, game.settings.joystickSensitivity);
            String prompt = targetQuest != null ? "✦ " + targetQuest.label(p.route)
                    : targetSide != null ? (targetSide.id.startsWith("WE27_") ? "✦ Event: " : "♪ ") + targetSide.label(p.route)
                    : targetNpc != null ? "Bicara: " + targetNpc.name
                    : targetAnimal != null ? "Elus " + animalName(targetAnimal.type)
                    : targetBed ? "Tidur" 
                    : targetTalk != null ? "♥ Ngobrol" 
                    : targetRomance ? "♥ Waktu Berdua"
                    : (targetExamine != null ? targetExamine.label : null);
            controls.draw(ui, game.settings.controlOpacity, prompt);
        }

        if (bannerTime > 0 && !overlay) {
            float al = Math.min(1f, bannerTime * 2f);
            ui.textCenter(a.title, bannerText, W / 2, H * 0.62f, tint.set(1, 1, 1, al), 0.62f);
        }
        if (toastTime > 0) {
            float al = Math.min(1f, toastTime * 3f);
            float tw = Math.min(W - 80, ui.measure(a.body, toastText, 0.9f) + 60);
            float ty = dialog.active() ? H * 0.62f : H * 0.66f;
            ui.panel(a.panelDark, (W - tw) / 2, ty - 30, tw, 58, al);
            ui.text(a.body, toastText, (W - tw) / 2, ty + 12, tint.set(Ui.CREAM.r, Ui.CREAM.g, Ui.CREAM.b, al), 0.9f, Align.center, tw);
        }

        if (bubbleTime > 0 && bubbleText != null && partnerMode == 2 && !overlay) {
            float al = Math.min(1f, Math.min(bubbleTime * 2f, (3.6f - bubbleTime) * 4f));
            Vector2 v = mapToUi(partner.x, partner.y - partner.drawHeight() - 4);
            float bw = Math.min(560, ui.measure(a.body, bubbleText, 0.78f) + 44), bx = MathUtils.clamp(v.x - bw / 2, inL + 10, W - inR - bw - 10);
            ui.panel(a.panel, bx, v.y + 8, bw, 62, al);
            ui.text(a.body, bubbleText, bx, v.y + 52, tint.set(Ui.INK.r, Ui.INK.g, Ui.INK.b, al), 0.78f, Align.center, bw);
        }
        dialog.draw(ui, W, H, inL, inR, inB);
        puzzle.draw(ui, W, H);
        minigame.draw(ui, W, H);
        if (creditsTime >= 0) drawCredits(W, H);
        if (pauseOpen) drawPause();
        book.draw(ui, W, H);
        shop.draw(ui, W, H);
        romance.draw(ui, W, H);
        if (settingsOpen) settingsPanel.draw(ui, W, H);
        dialogueHistory.draw(ui, W, H);

        if (cardTime >= 0) {
            float al = Math.min(1f, cardTime * 3f);
            ui.rect(0, 0, W, H, Ui.BG, 0.92f * al);
            ui.textCenter(a.title, cardTitle, W / 2, H / 2 + 60, tint.set(1, 1, 1, al), 0.7f);
            ui.wrap(a.body, cardSub, W * 0.15f, H / 2 - 20, W * 0.7f, tint.set(Ui.LAVENDER.r, Ui.LAVENDER.g, Ui.LAVENDER.b, al), 1f, Align.center);
            if (cardTime > 0.6f) ui.textCenter(a.body, "Ketuk untuk lanjut", W / 2, 70, tint.set(1, 1, 1, 0.6f * al), 0.75f);
        }
        if (fadeAlpha > 0) ui.rect(0, 0, W, H, Ui.BG, fadeAlpha);
    }

    /** Saat cutscene: HUD disembunyikan, hanya letterbox, dialog, toast, dan fade. */
    private void drawCineUi(float W, float H, float inL, float inR, float inB) {
        cine.drawUi(ui, W, H);
        if (toastTime > 0) {
            float al = Math.min(1f, toastTime * 3f);
            float tw = Math.min(W - 80, ui.measure(game.assets.body, toastText, 0.9f) + 60);
            ui.panel(game.assets.panelDark, (W - tw) / 2, H * 0.7f - 30, tw, 58, al);
            ui.text(game.assets.body, toastText, (W - tw) / 2, H * 0.7f + 12, tint.set(Ui.CREAM.r, Ui.CREAM.g, Ui.CREAM.b, al), 0.9f, Align.center, tw);
        }
        dialog.draw(ui, W, H, inL, inR, inB);
        if (pauseOpen) drawPause();
        if (settingsOpen) settingsPanel.draw(ui, W, H);
        dialogueHistory.draw(ui, W, H);
        if (fadeAlpha > 0) ui.rect(0, 0, W, H, Ui.BG, fadeAlpha);
    }

    private void drawCredits(float W, float H) {
        ui.rect(0, 0, W, H, Ui.BG, Math.min(1f, creditsTime));
        float y0 = -60 + creditsTime * 70f;
        List<String> lines = game.quests.credits;
        for (int i = 0; i < lines.size(); i++) {
            float y = y0 - i * 64;
            if (y < -40 || y > H + 60) continue;
            ui.text(i == 0 ? game.assets.title : game.assets.body, lines.get(i), 0, y, i == 0 ? Ui.GOLD : Ui.CREAM, i == 0 ? 0.6f : 1f, Align.center, W);
        }
        ui.text(game.assets.body, "Ketuk untuk mempercepat", 0, 50, Ui.LAVENDER, 0.7f, Align.center, W);
    }

    private void drawPause() {
        float W = uiW(), H = uiH();
        ui.rect(0, 0, W, H, Ui.BG, 0.6f);
        float pw = Math.min(520, W - insetL() - insetR() - 28);
        float ph = Math.min(670, H - insetT() - insetB() - 20);
        float px = (W - pw) / 2, py = (H - ph) / 2;
        ui.panel(game.assets.panel, px, py, pw, ph, 1f);
        ui.text(game.assets.title, "Jeda", px, py + ph - 26, Ui.INK, 0.6f, Align.center, pw);
        int mins = (int) (p.playSeconds / 60);
        ui.text(game.assets.body, Routes.display(p.route) + " Route • Slot " + p.slot + " • " + mins + " menit", px, py + 46, Ui.INK_SOFT, 0.72f, Align.center, pw);
        for (UiButton b : pauseButtons) ui.button(b);
    }

    // ================================================================== input
    @Override
    public boolean touchDown(int sx, int sy, int pointer, int button) {
        Vector2 v = toUi(sx, sy);
        float x = v.x, y = v.y;
        if (fadePhase != 0) return true;
        if (confirm != null) { confirm.down(x, y, pointer); return true; }
        if (dialogueHistory.active()) return dialogueHistory.down(x, y, pointer);
        if (cine.active() && !dialog.active() && !pauseOpen && !settingsOpen) { cine.fast = true; return true; }
        if (cardTime >= 0) { if (cardTime > 0.6f) finishCard(); return true; }
        if (creditsTime >= 0) { creditsTime += 2.5f; return true; }
        if (settingsOpen) { for (UiButton b : settingsPanel.buttons) if (b.down(x, y, pointer)) return true; return true; }
        if (romance.active()) return romance.touchDown(x, y, pointer);
        if (shop.active()) return shop.touchDown(x, y, pointer);
        if (book.active()) return book.touchDown(x, y, pointer);
        if (pauseOpen) { for (UiButton b : pauseButtons) if (b.down(x, y, pointer)) return true; return true; }
        if (puzzle.active()) return puzzle.touchDown(x, y, pointer);
        if (minigame.active()) return minigame.touchDown(x, y, pointer);
        if (dialog.active()) return dialog.touchDown(x, y, pointer);
        if (hudBook.down(x, y, pointer) || hudPause.down(x, y, pointer)) return true;
        if (runner.busy()) return true;
        return controls.touchDown(x, y, pointer);
    }

    @Override
    public boolean touchUp(int sx, int sy, int pointer, int button) {
        Vector2 v = toUi(sx, sy);
        float x = v.x, y = v.y;
        cine.fast = false;
        controls.touchUp(pointer);
        if (confirm != null) { if (confirm.up(x, y, pointer)) game.audio.sfx("page"); return true; }
        if (dialogueHistory.active()) return dialogueHistory.up(x, y, pointer);
        if (settingsOpen) { for (UiButton b : new ArrayList<>(settingsPanel.buttons)) if (b.up(x, y, pointer)) { game.audio.sfx("page"); return true; } return true; }
        if (romance.active()) return romance.touchUp(x, y, pointer);
        if (shop.active()) return shop.touchUp(x, y, pointer);
        if (book.active()) { boolean r = book.touchUp(x, y, pointer); return r; }
        if (pauseOpen) { for (UiButton b : new ArrayList<>(pauseButtons)) if (b.up(x, y, pointer)) { game.audio.sfx("page"); return true; } return true; }
        if (puzzle.active()) return puzzle.touchUp(x, y, pointer);
        if (minigame.active()) return minigame.touchUp(x, y, pointer);
        if (dialog.active()) return dialog.touchUp(x, y, pointer);
        if (hudBook.up(x, y, pointer) || hudPause.up(x, y, pointer)) { game.audio.sfx("page"); return true; }
        return false;
    }

    @Override
    public boolean touchDragged(int sx, int sy, int pointer) {
        Vector2 v = toUi(sx, sy);
        return controls.touchDragged(v.x, v.y, pointer);
    }

    @Override
    public boolean touchCancelled(int sx, int sy, int pointer, int button) {
        controls.touchUp(pointer);
        dialogueHistory.cancel(pointer);
        hudBook.cancel(); hudPause.cancel();
        dialog.cancelTouch(pointer);
        for (UiButton b : pauseButtons) if (b.pointer == pointer) b.cancel();
        for (UiButton b : settingsPanel.buttons) if (b.pointer == pointer) b.cancel();
        return true;
    }

    @Override
    public boolean keyDown(int k) {
        if (fadePhase != 0) return true;
        boolean back = k == Input.Keys.BACK || k == Input.Keys.ESCAPE;
        if (dialogueHistory.active()) {
            if (back || k == Input.Keys.H || k == Input.Keys.ENTER) dialogueHistory.close();
            else if (k == Input.Keys.LEFT) dialogueHistory.pageOlder();
            else if (k == Input.Keys.RIGHT) dialogueHistory.pageNewer();
            return true;
        }
        if (confirm != null) {
            if (back) { if (confirm.no != null && confirm.no.onClick != null) confirm.no.onClick.run(); else confirm = null; }
            else if (k == Input.Keys.ENTER || k == Input.Keys.E) { if (confirm.yes.onClick != null) confirm.yes.onClick.run(); }
            return true;
        }
        if (cardTime >= 0) { if (cardTime > 0.6f && (back || k == Input.Keys.ENTER || k == Input.Keys.SPACE || k == Input.Keys.E)) finishCard(); return true; }
        if (settingsOpen) { if (back) { game.saveSettings(); settingsOpen = false; } return true; }
        if (romance.active()) { if (back || k == Input.Keys.ENTER) romance.close(); return true; }
        if (shop.active()) { if (back || k == Input.Keys.ENTER) shop.close(); return true; }
        if (book.active()) { if (back || k == Input.Keys.M) book.close(); return true; }
        if (pauseOpen) { if (back || k == Input.Keys.P) pauseOpen = false; else if (k == Input.Keys.H) openDialogueHistory(); return true; }
        if (creditsTime >= 0) { creditsTime += 2.5f; return true; }
        if (minigame.active()) {
            if (back) minigame.cancel();
            else if (k == Input.Keys.SPACE || k == Input.Keys.E) minigame.key(0);
            else if (k == Input.Keys.ENTER) minigame.key(99);
            else if (k >= Input.Keys.NUM_1 && k <= Input.Keys.NUM_4) minigame.key(k - Input.Keys.NUM_1);
            return true;
        }
        if (puzzle.active()) {
            if (back) puzzle.cancelKey();
            else if (k >= Input.Keys.NUM_1 && k <= Input.Keys.NUM_3) puzzle.key(k - Input.Keys.NUM_1);
            return true;
        }
        if (dialog.active()) {
            if (k == Input.Keys.H) { openDialogueHistory(); return true; }
            if (dialog.choosing()) {
                if (k >= Input.Keys.NUM_1 && k <= Input.Keys.NUM_8) dialog.choose(k - Input.Keys.NUM_1);
                else if (k == Input.Keys.DOWN || k == Input.Keys.RIGHT || k == Input.Keys.S || k == Input.Keys.D) dialog.focusChoice(1);
                else if (k == Input.Keys.UP || k == Input.Keys.LEFT || k == Input.Keys.W || k == Input.Keys.A) dialog.focusChoice(-1);
                else if (k == Input.Keys.E || k == Input.Keys.SPACE || k == Input.Keys.ENTER) dialog.confirmFocusedChoice();
            } else if (k == Input.Keys.E || k == Input.Keys.SPACE || k == Input.Keys.ENTER) dialog.advance();
            return true;
        }
        if (back || k == Input.Keys.P) { openPause(); return true; }
        if (k == Input.Keys.M) { openBook(); return true; }
        if (k == Input.Keys.H) { openDialogueHistory(); return true; }
        if ((k == Input.Keys.E || k == Input.Keys.SPACE || k == Input.Keys.ENTER) && free()) { interact(); return true; }
        return false;
    }

    @Override
    public void pause() {
        super.pause(); // hentikan music/ambience saat aplikasi tidak aktif
        // aplikasi ke background / layar mati: simpan & lepaskan input
        controls.reset();
        saveNow(); // diabaikan otomatis bila rangkaian aksi sedang berjalan
    }

    @Override
    public void resume() { super.resume(); controls.reset(); }

    @Override
    public void hide() { controls.reset(); }
}
