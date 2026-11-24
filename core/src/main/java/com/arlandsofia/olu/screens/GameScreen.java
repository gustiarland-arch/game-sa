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

/**
 * Layar bermain: eksplorasi top-down 3/4, collision kaki, pintu, companion, interaksi quest,
 * dialog, puzzle, Memory Book, pause, autosave. Implementasi Presenter untuk ActionRunner.
 */
public final class GameScreen extends BaseScreen implements ActionRunner.Presenter {
    final TownDirector town = new TownDirector(this);
    final CompanionController companion = new CompanionController(this);
    final HudRenderer hud = new HudRenderer(this);
    final WorldRenderer worldRenderer = new WorldRenderer(this);
    static final float WALK_SPEED = 112f, SPRINT_SPEED = 176f;

    final Progress p;
    final boolean replay, newGame;
    final QuestEngine engine;
    final ActionRunner runner;

    final OrthographicCamera worldCam = new OrthographicCamera();
    final ExtendViewport worldView = new ExtendViewport(760, 428, worldCam);
    final CameraRig cameraRig = new CameraRig();
    /** Reused collision adapter: avoids allocating callbacks every frame. */
    final WorldNavigationV52.Collision footCollision = new WorldNavigationV52.Collision() {
        @Override public boolean blocked(float sx,float sy) { return area == null || area.blocked(sx,sy); }
    };
    float frameDt = 1f / 60f;

    MapDb.Area area;
    /** Cached terrace textures are editor-replaceable PNGs loaded with other native assets. */
    float lastTerrainHeight;
    boolean previousStair;
    Texture mapTex;
    final Actor player, partner;
    int partnerMode; // 0 tidak ada, 1 NPC diam, 2 companion
    final ArrayDeque<float[]> trail = new ArrayDeque<>();

    final TouchControls controls;
    final MinigameOverlay minigame;
    final CutscenePlayer cine;
    boolean cineShowPartner;
    // companion hidup
    float compIdle, compNext = 3f, pendingComment = -1f;
    String bubbleText; float bubbleTime;
    final Map<String, Actor> cineActors = new LinkedHashMap<>();
    final Map<String, Actor> townActors = new LinkedHashMap<>();
    /** otak NPC: {homeX, homeY, radius, targetX, targetY, timer, scheduleKey} */
    final Map<String, float[]> npcBrain = new LinkedHashMap<>();
    final Map<String, String> npcPlaceKey = new LinkedHashMap<>();
    final List<Animal> animals = new ArrayList<>();
    Animal targetAnimal; boolean targetBed;
    float clockAcc;
    float soundscapeClock, footstepClock;
    QuestDb.TownNpc targetNpc;
    QuestDb.Interactable targetSide;
    QuestDb.Talk targetTalk;
    float creditsTime = -1; Runnable creditsDone;
    final float[] rainX = new float[140], rainY = new float[140];
    final DialogBox dialog;
    final DialogueHistoryOverlay dialogueHistory;
    float autosaveAcc;
    final PuzzleOverlay puzzle;
    final MemoryBookOverlay book;
    final ShopOverlay shop;
    final RomanceOverlay romance;
    boolean targetRomance;
    final SettingsPanel settingsPanel;
    boolean settingsOpen, pauseOpen;
    final List<UiButton> pauseButtons = new ArrayList<>();
    final UiButton hudBook, hudPause;
    final Texture shadow, marker, sparkle, glow, coinIcon;
    final WorldFx worldFx;
    /** Prerendered split regions for foliage; cache never modified after creation. */
    final Map<Texture, TextureRegion[]> animatedTreeRegions = new java.util.IdentityHashMap<>();

    // target interaksi
    QuestDb.Interactable targetQuest;
    MapDb.Examine targetExamine;

    String toastText; float toastTime;
    String bannerText; float bannerTime;
    float objectiveFlash;
    float doorCooldown;
    QuestCompass.Hint cachedQuestRoute;
    float questRouteRefresh;

    int fadePhase; float fadeAlpha; Runnable fadeMid, fadeEnd;
    String cardTitle, cardSub; float cardTime = -1; Runnable cardDone;

    final Color tint = new Color();
    static final class DrawItem { float y; Object value; }
    final List<DrawItem> drawList = new ArrayList<>();
    /** Reused list of quest markers: no new ArrayList in every rendered frame. */
    final List<QuestDb.Interactable> drawMarkers = new ArrayList<>();
    final List<DrawItem> drawPool = new ArrayList<>();
    /** Cache ukuran gambar prop per area; culling tidak memanggil Texture lookup tiap frame. */
    final Map<MapDb.Prop, float[]> propMetrics = new java.util.IdentityHashMap<>();
    int drawCursor;
    float visibleL, visibleR, visibleB, visibleT;
    // v5.4 weather: storm scheduler, rain puddles and ground wetness (cosmetic, never saved).
    final WeatherFxV54.Storm storm;
    java.util.List<float[]> puddles = new java.util.ArrayList<>();
    float wetness;
    final Comparator<DrawItem> bySortY = new Comparator<DrawItem>() {
        public int compare(DrawItem a, DrawItem b) { return Float.compare(a.y, b.y); }
    };

    /** Reuse urutan draw tanpa alokasi array kecil untuk setiap prop tiap frame. */
    void addDraw(float y, Object value) {
        if (drawCursor >= drawPool.size()) drawPool.add(new DrawItem());
        DrawItem item = drawPool.get(drawCursor++);
        item.y = y; item.value = value;
        drawList.add(item);
    }

    boolean visibleActor(float x, float y) {
        float drawY = area.h - y;
        return x >= visibleL - 75 && x <= visibleR + 75 && drawY >= visibleB - 75 && drawY <= visibleT + 75;
    }

    /** Bounds-aware prop culling BEFORE depth sort: avoids sorting hundreds of offscreen trees. */
    boolean propVisible(MapDb.Prop pr) {
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
        // Storm timing is varied per in-game day but reproducible (same day, same storm).
        this.storm = new WeatherFxV54.Storm(p.day * 7919L + 17L);
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
        if (p.companion) { partnerMode = 2; companion.placeBeside(); }
    }

    static Map<String, Object> act(String... kv) {
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
    void enterArea(String id, float x, float y, int dir, boolean announce) {
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
        storm.reset();
        puddles = WeatherFxV54.puddles(a);
        wetness = "rain".equals(weather()) && !a.indoor ? 1f : 0f; // arriving mid-shower: ground is already wet
        soundscapeClock = 0f; footstepClock = 0f;
        lastTerrainHeight = ElevationV50.heightAt(a.terraces, x, y);
        previousStair = ElevationV50.onStairs(a.terraces,x,y);
        if (partnerMode == 2) companion.placeBeside();
        town.refreshNpcs();
        town.spawnAnimals();
        syncSoundscape();
        if (announce) { bannerText = a.name; bannerTime = 2.2f; }
        if (partnerMode == 2) companion.queueComment();
        doorCooldown = 0.5f;
    }













    /** Aktivitas idle dari kebijakan dunia v4.6, memakai animasi atlas asli. */
    String npcIdleActivity(String id) {
        return MotionPersonalityV53.idlePose(id, WorldClock.hour(p.minute), weather(), isIndoor(), p.day);
    }





    // ================================================================== loop
    boolean free() {
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
                if (p.minute % 10 == 0) { town.refreshTown(); if (!cine.active()) syncSoundscape(); }
                if (p.minute == 19 * 60 + 30) town.spawnAnimals(); // hewan siang pulang, kucing malam keluar
                if (p.minute >= WorldClock.DAY_END) { passOut(); break; }
            }
            move(dt);
            if (player.walking && game.settings.footsteps && footstepClock <= 0f) {
                boolean stairsNow=ElevationV50.onStairs(area.terraces,player.x,player.y);
                boolean puddleStep = wetness > 0.35f && WeatherFxV54.inPuddle(puddles, player.x, player.y);
                if (puddleStep) worldFx.splashAt(player.x, area.h - player.y, game.settings.visualQuality);
                game.audio.sfx(puddleStep ? "v54_step_puddle" : stairsNow ? "v50_stair_foot" : ElevationV50.stepSound(
                        area.terraces,player.x,player.y,SoundscapePlan.footstepFor(area.id)), puddleStep ? .34f : .19f);
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
        companion.followCompanion(dt);
        companion.companionLife(dt);
        if (bubbleTime > 0) bubbleTime -= dt;
        if (pendingComment > 0 && free() && partnerMode == 2) { pendingComment -= dt; if (pendingComment <= 0) companion.showComment(); }
        player.update(dt);
        partner.update(dt);
        for (Actor ac : townActors.values()) ac.update(dt);
        town.updateNpcs(dt);
        for (int i = animals.size() - 1; i >= 0; i--) { Animal an = animals.get(i); an.update(dt, area, player.x, player.y); if (an.gone()) animals.remove(i); }
        worldFx.update(dt, player.x, area.h - player.y, player.walking, player.sprinting,
                "rain".equals(weather()), isIndoor(), partner.x, area.h - partner.y,
                partnerMode == 2, p.affection, game.settings.visualQuality);
        boolean raining = "rain".equals(weather());
        wetness = WeatherFxV54.wetness(wetness, dt, raining && !isIndoor() && !realm());
        storm.update(dt, WeatherFxV54.stormAllowed(area.id, raining, isIndoor(), realm()) && !cine.camActive());
        float thunder = storm.consumeThunder();
        if (thunder > 0f) game.audio.sfx("v54_thunder", 0.45f + 0.55f * thunder);
    }

    // ================================================================== hari & tidur
    String clockStep;
    /** step cerita bersuasana senja/malam memajukan jam dunia (hanya maju), agar HUD, NPC, dan langit selaras. */
    void syncClockToStep() {
        QuestDb.Step st = engine.step();
        if (st == null || st.id.equals(clockStep)) return;
        clockStep = st.id;
        if (st.tint == null || replay) return;
        Color c = Color.valueOf(st.tint);
        int target = c.b > c.r ? 20 * 60 : 17 * 60 + 30;
        if (p.minute < target) { p.minute = target; town.refreshTown(); town.spawnAnimals(); }
    }
    void newDay(String msg) {
        p.day++; p.minute = 7 * 60; clockAcc = 0;
        npcPlaceKey.clear(); townActors.clear(); npcBrain.clear();
        town.refreshTown(); town.spawnAnimals();
        syncSoundscape();
        String w = WorldClock.weather(p.day);
        toast(msg + " " + WorldClock.dayName(p.day) + ", hari ke-" + p.day + " • " + Character.toUpperCase(w.charAt(0)) + w.substring(1));
        saveNow();
    }

    void askSleep() {
        boolean early = p.minute < 17 * 60;
        confirm = new ConfirmBox("Tidur?", early ? "Masih " + WorldClock.hhmm(p.minute) + ". Tidur sampai besok pagi?" : "Istirahat sampai besok pagi. Progress tersimpan otomatis.",
                "Tidur", new Runnable() { public void run() { confirm = null; fade(new Runnable() { public void run() {
                    player.dir = Assets.DIR_DOWN; newDay("Selamat pagi!"); } }, null); } },
                "Nanti", new Runnable() { public void run() { confirm = null; } });
    }

    void passOut() {
        final String room = Routes.room(p.route);
        fade(new Runnable() { public void run() {
            MapDb.Area roomArea = game.maps.area(room);
            float[] bed = bedSpot(roomArea);
            enterArea(room, bed[0], bed[1] + 50f, Assets.DIR_DOWN, false);
            newDay("Kamu ketiduran sampai pagi...");
        } }, null);
    }

    void move(float dt) {
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

    void checkDoors(float ox, float oy) {
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



    void findTarget() {
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
    float[] bedSpot(MapDb.Area a) {
        if (a != null && !Float.isNaN(a.bedX)) return new float[]{a.bedX, a.bedY};
        return new float[]{p.route.equals("arland") ? 830f : 130f, 380f};
    }

    float dist(float x, float y) { float dx = x - player.x, dy = y - player.y; return (float) Math.sqrt(dx * dx + dy * dy); }

    void interact() {
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

    DialogBox.Listener dialogListener() {
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
    void fade(Runnable mid, Runnable end) {
        fadePhase = 1; fadeAlpha = 0f; fadeMid = mid; fadeEnd = end;
        controls.reset();
    }

    void updateFade(float dt) {
        if (fadePhase == 1) {
            fadeAlpha += dt * 4f;
            if (fadeAlpha >= 1f) { fadeAlpha = 1f; fadePhase = 2; Runnable m = fadeMid; fadeMid = null; if (m != null) m.run(); }
        } else if (fadePhase == 2) {
            fadeAlpha -= dt * 3.2f;
            if (fadeAlpha <= 0f) { fadeAlpha = 0f; fadePhase = 0; Runnable e = fadeEnd; fadeEnd = null; if (e != null) e.run(); }
        }
    }

    void showCard(String title, String sub, Runnable done) {
        cardTitle = title; cardSub = sub; cardTime = 0f; cardDone = done;
        controls.reset();
    }

    void finishCard() {
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
    void playScenePart(String sceneId, int from, int n, Runnable done) {
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
            if (partnerMode == 2 && Math.abs(partner.x - player.x) + Math.abs(partner.y - player.y) > 200) companion.placeBeside();
            done.run();
        } });
    }

    @Override
    public void credits(Runnable done) {
        controls.reset();
        creditsTime = 0f; creditsDone = done;
        game.audio.music("cinema_our_tomorrow");
    }

    void finishCredits() {
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
            if (partnerMode != 1) companion.placeBeside();
            partnerMode = 2;
            trail.clear();
        } else {
            partnerMode = 0;
            p.holdingHands = false;
            town.refreshNpcs();
        }
    }

    @Override
    public void stepChanged() {
        town.refreshNpcs();
        if (!cine.active()) syncSoundscape();
        game.audio.sfx("quest_complete", .22f);
        objectiveFlash = 1.6f;
    }

    @Override public void onIdle() { saveNow(); }

    /** Simpan hanya saat tidak ada rangkaian aksi berjalan -> save selalu konsisten (tidak ada state setengah jadi). */
    boolean saveNow() {
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
    void openDialogueHistory() {
        controls.reset();
        dialogueHistory.open(p.dialogueHistory);
    }

    void openBook() {
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
    void showHowToPlay() {
        confirm = new ConfirmBox("Cara bermain",
                "GERAK: gunakan joystick di layar atau tombol WASD.\n"
                        + "LARI: tahan tombol LARI / Shift. AKSI: tombol AKSI / E.\n"
                        + "BUKU: lihat misi, tas, bab, dan 12 prestasi.\n"
                        + "Jelajahi area, ikuti penanda interaksi dan kompas misi, lalu ajak pasangan.\n"
                        + "Jeda > Pengaturan: ubah joystick, audio, dan tampilan.\n"
                        + "Gunakan Simpan sekarang sebelum keluar atau pindah versi.",
                "Mengerti", new Runnable() { public void run() { confirm = null; } }, null, null);
    }

    void openPause() { controls.reset(); pauseOpen = true; }

    void askMainMenu() {
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



    String weather() {
        String w = engine.weatherNow();
        return WorldClock.HUJAN.equals(w) ? "rain" : w;
    }





    boolean isIndoor() { return area.indoor; }
    static String animalName(String t) {
        if (t.startsWith("cat")) return "kucing"; if (t.equals("dog")) return "anjing"; if (t.equals("duck")) return "bebek";
        if (t.equals("chicken")) return "ayam"; if (t.equals("rabbit")) return "kelinci"; return t;
    }
    /** cahaya efektif: tint step cerita bila ada, selain itu dari jam dunia. {r,g,b,a} */
    float[] lightNow() {
        QuestDb.Step st = engine.step();
        if (st != null && st.tint != null) { Color c = Color.valueOf(st.tint); return new float[]{c.r, c.g, c.b, st.tintAlpha}; }
        if (realm()) return new float[]{1, 1, 1, 0};
        return WorldClock.light(p.minute);
    }
    boolean realm() { return "memory".equals(area.music) || "star".equals(area.music) || "tender".equals(area.music); }

    /** Musik kota/cerita dengan 25 komposisi baru; perintah musik khusus quest selalu didahulukan. */
    String musicFor() {
        QuestDb.Step st = engine.step();
        String override = st != null && st.music != null && (st.musicAreas.isEmpty() || st.musicAreas.contains(area.id)) ? st.music : null;
        return SoundscapePlan.musicFor(area.id, area.music, weather(), isIndoor(), p.minute, p.day,
                game.settings.variedMusic, override);
    }

    void syncSoundscape() {
        if (area == null) return;
        game.audio.music(musicFor());
        game.audio.ambience(SoundscapePlan.ambienceFor(area.id, weather(), isIndoor(), p.minute));
    }











    /** Konversi koordinat peta -> UI (kedua viewport menutupi seluruh layar). */
    final Vector2 tmpV = new Vector2();
    Vector2 mapToUi(float mx, float my) {
        float ww = worldView.getWorldWidth() * worldCam.zoom, wh = worldView.getWorldHeight() * worldCam.zoom;
        float left = worldCam.position.x - ww / 2, bottom = worldCam.position.y - wh / 2;
        return tmpV.set((mx - left) * uiW() / ww, ((area.h - my) - bottom) * uiH() / wh);
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
    @Override
    protected void drawWorld() { worldRenderer.drawWorld(); }
    @Override
    protected void drawUi() { hud.drawUi(); }
}
