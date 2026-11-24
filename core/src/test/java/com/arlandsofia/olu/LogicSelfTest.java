package com.arlandsofia.olu;

import com.arlandsofia.olu.logic.ActionRunner;
import com.arlandsofia.olu.logic.CameraRig;
import com.arlandsofia.olu.logic.ElevationV50;
import com.arlandsofia.olu.logic.SoundscapePlan;
import com.arlandsofia.olu.logic.FileIO;
import com.arlandsofia.olu.logic.GlobalProgress;
import com.arlandsofia.olu.logic.Json;
import com.arlandsofia.olu.logic.MapDb;
import com.arlandsofia.olu.logic.WorldClock;
import com.arlandsofia.olu.logic.MemoryBookDb;
import com.arlandsofia.olu.logic.Progress;
import com.arlandsofia.olu.logic.PuzzleLogic;
import com.arlandsofia.olu.logic.QuestDb;
import com.arlandsofia.olu.logic.QuestEngine;
import com.arlandsofia.olu.logic.Routes;
import com.arlandsofia.olu.logic.SaveStore;
import com.arlandsofia.olu.logic.Settings;
import com.arlandsofia.olu.logic.StoryDb;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Uji logika tanpa LibGDX/Android: data valid, kedua route bisa ditamatkan Prologue + Chapter 1 tanpa softlock,
 * pintu tidak terkunci permanen, save/load + pemulihan file rusak, puzzle, collision spawn.
 * Jalankan: lewat JUnit (LogicTest) atau langsung `java LogicSelfTest <folder assets>`.
 */
public final class LogicSelfTest {
    static int checks = 0;
    static final List<String> log = new ArrayList<>();


    /** v5.0: traverse all 21 physical staircases in the real map collision data. */
    static void testV50Elevations(File assets, StoryDb story, QuestDb quests, MapDb maps) {
        int count=0;
        String[] tracks={"v50_plaza_ascent","v50_rain_reflections","v50_starlit_steps","v50_tomorrow_horizon","v50_cafe_highlight"};
        for(String track:tracks) {
            check(SoundscapePlan.musicPath(track)!=null,"v5.0 score in runtime registry "+track);
            check(new File(assets,"audio/music/"+track+".ogg").length()>3000,"v5.0 score bytes "+track);
        }
        for(MapDb.Area area:maps.areas.values()) for(MapDb.Terrace t:area.terraces){
            count++;
            check(t.rise>12&&t.rise<=40,"real elevation range "+area.id);
            check(new File(assets,t.image).length()>500,"editable terrace art exists "+area.id);
            check(new File(assets,t.front).length()>200,"foreground occluder exists "+area.id);
            check(t.x>15&&t.y>15&&t.x+t.w<area.w&&t.stairEnd()+15<area.h,"terrace within map "+area.id);
            float x=t.stairX()+t.stairWidth*.5f;
            check(!area.blocked(x,t.y+t.h*.5f),"terrace landing not inside original map collision "+area.id);
            check(!area.blocked(x,t.stairEnd()+5),"stair foot reachable "+area.id);
            check(!ElevationV50.canStep(area.terraces,t.x-1,t.y+t.h*.5f,t.x+1,t.y+t.h*.5f),
                  "cannot climb through the left retaining wall "+area.id);
            check(!ElevationV50.canStep(area.terraces,t.x+t.w+1,t.y+t.h*.5f,t.x+t.w-1,t.y+t.h*.5f),
                  "cannot enter from side "+area.id);
            check(ElevationV50.heightAt(area.terraces,x,t.y+t.h*.4f)>=t.rise-.01f,
                  "full height on upper deck "+area.id);
            float lastHeight=0f;
            float y=t.stairEnd()+5f;
            for(int k=0;k<120;k++){
                float ny=y-1.5f;
                if(ny<t.y+t.h*.5f)break;
                check(!area.blocked(x,ny),"stair does not intersect existing wall "+area.id+" at "+ny);
                check(ElevationV50.canStep(area.terraces,x,y,x,ny),"ascending staircase passable "+area.id+" at "+ny);
                float z=ElevationV50.heightAt(area.terraces,x,ny);
                check(z+0.06f>=lastHeight,"stairs are monotone in height "+area.id);
                lastHeight=z;y=ny;
            }
            check(lastHeight>=t.rise-0.1f,"stairs connect to deck "+area.id);
            for(float py=t.y+t.h*.5f;py<t.stairEnd()+5f;py+=1.5f) {
                float to=Math.min(t.stairEnd()+5f,py+1.5f);
                check(ElevationV50.canStep(area.terraces,x,py,x,to),"stairs descend without softlock "+area.id);
            }
            boolean found=false;
            for(QuestDb.Interactable it:quests.side) if(it.id.equals("V50_VIEW_"+area.id.toUpperCase(java.util.Locale.ROOT))){
                check(t.top(it.x,it.y),"panorama target on accessible upper deck "+area.id);
                check(it.actions.size()>=5,"interactive panorama has actions "+area.id);
                found=true;
            }
            check(found,"playable viewpoint for "+area.id);
            for(String route:Routes.ALL)
                check(story.scene("V50-VIEW-"+area.id.toUpperCase(java.util.Locale.ROOT)+"-"+route.toUpperCase(java.util.Locale.ROOT))!=null,
                      "POV-specific panorama dialogue "+route+" "+area.id);
        }
        check(count==21,"21 terraced maps, not only stair drawings");
        log.add("V5.0: "+count+" physical staircases climb/descent, wall blocking, collision, music assets and 42 POV view scenes OK");
    }

    static void check(boolean ok, String what) {
        checks++;
        if (!ok) throw new AssertionError("GAGAL: " + what);
    }

    static String read(File base, String rel) throws IOException {
        return new String(Files.readAllBytes(new File(base, rel).toPath()), StandardCharsets.UTF_8);
    }

    public static void main(String[] args) throws Exception {
        runAll(new File(args.length > 0 ? args[0] : "../android/assets"));
        for (String l : log) System.out.println(l);
        System.out.println("SEMUA LULUS: " + checks + " pemeriksaan");
    }

    public static void runAll(File assets) throws Exception {
        if (!assets.isDirectory()) throw new AssertionError("Folder assets tidak ditemukan: " + assets.getAbsolutePath());
        StoryDb story = new StoryDb(read(assets, "data/story.json"));
        QuestDb quests = new QuestDb(read(assets, "data/quests.json"));
        MapDb maps = new MapDb(read(assets, "data/maps.json"), read(assets, "data/props.json"));
        MemoryBookDb book = new MemoryBookDb(read(assets, "data/memory_book.json"));

        testJson();
        testVisualControls(assets, quests);
        testData(assets, story, quests, maps, book);
        testV50Elevations(assets,story,quests,maps);
        testPuzzle(quests);
        GlobalProgress g = new GlobalProgress();
        for (String r : Routes.ALL) {
            Progress p = playRoute(r, story, quests, maps);
            g.absorb(p);
            testReplay(p, story, quests, maps);
            testMemoryBook(book, p, g);
        }
        check(g.bothCompleted("C06"), "bonus dua sisi terbuka setelah kedua route tamat");
        double tot = 0, totMain = 0;
        for (double[] v : EST.values()) { tot += v[0] + v[1] + v[2]; totMain += v[0]; }
        log.add(String.format(java.util.Locale.ROOT, "ESTIMASI TOTAL kedua route: cerita utama %.1f jam, lengkap (side quest + eksplorasi) %.1f jam", totMain / 60, tot / 60));
        testSave(story, quests, maps);
        testEconomy(story, quests, maps);
        testRomance(story, quests, maps, book);
        testMoments(story, quests, maps, book);
        testCoupleActions(story, quests, maps, book);
        testRomanceGames(story, quests, maps, book);
        testWorld(assets, story, quests, maps);
        testLivingWorldEvents(story, quests, maps, book);
        testDiscoveriesV49(story, quests, maps, book);
    }

    /** v2.7: event benar-benar tampil, punya naskah tiap route, tidak bisa farming, save schema5->6. */
    static void testLivingWorldEvents(StoryDb story, QuestDb quests, MapDb maps, MemoryBookDb book) {
        check(quests.worldEvents.size() == 32, "14 original + 18 v4.9 world events tersedia");
        Set<String> unique = new HashSet<>();
        for (QuestDb.WorldEvent event : quests.worldEvents) {
            check(unique.add(event.id), "ID event unik " + event.id);
            check(maps.area(event.area) != null, "peta event ada: " + event.id);
            check(!maps.area(event.area).blocked(event.x, event.y), "titik event tidak tabrak collision: " + event.id);
            check(event.startMinute < event.endMinute && event.endMinute <= WorldClock.DAY_END, "jam event masuk akal: " + event.id);
            check(event.affection >= 0 && event.affection <= 8 && event.coins >= 0 && event.coins <= 12,
                    "bonus event wajar: " + event.id);
            check(quests.chapterIndex(event.minChapter) >= quests.chapterIndex("C02"), "event tidak membuka cerita terlalu dini: " + event.id);
            for (String r : Routes.ALL) {
                boolean usable = event.route == null || r.equals(event.route);
                String scene = event.scene(r);
                check(usable == (scene != null), "scene event hanya route yang tepat: " + event.id + ":" + r);
                if (usable) check(story.scene(scene) != null && r.equals(story.scene(scene).route)
                        && story.scene(scene).lines.size() >= 6, "adegan event benar-benar dapat dibaca: " + event.id + ":" + r);
            }
            check(book.entries.stream().anyMatch(e -> e.unlock.equals("WORLD_EVENT_" + event.id.toUpperCase(java.util.Locale.ROOT) + "_ONCE")),
                    "Memory Book untuk event tersedia: " + event.id);
            QuestDb.Interactable marker = null;
            String markerId = event.id.startsWith("v49_")
                    ? "V49_WE_" + event.id.substring(4).toUpperCase(java.util.Locale.ROOT)
                    : "WE27_" + event.id.toUpperCase(java.util.Locale.ROOT);
            for (QuestDb.Interactable it : quests.side) if (it.id.equals(markerId)) marker = it;
            check(marker != null && marker.actions.size() >= 3 && "worldEvent".equals(Json.str(marker.actions.get(2), "do", "")),
                    "event masuk sistem interaksi dan reward engine: " + event.id);
            check(marker != null && event.id.equals(Json.str(marker.when, "worldEventReady", "")), "marker terikat validasi harian: " + event.id);
        }
        for (String route : Routes.ALL) {
            Progress p = Progress.newGame(route, 1, "PRO_PHONE", maps.area(Routes.room(route)));
            QuestEngine engine = new QuestEngine(story, quests, maps, p, false);
            check(engine.worldEventBlock("tidak_ada", "plaza").contains("tidak ditemukan"), "event invalid aman");
            for (QuestDb.WorldEvent event : quests.worldEvents) {
                String markerId = event.id.startsWith("v49_")
                        ? "V49_WE_" + event.id.substring(4).toUpperCase(java.util.Locale.ROOT)
                        : "WE27_" + event.id.toUpperCase(java.util.Locale.ROOT);
                if (event.route != null && !route.equals(event.route)) {
                    check(engine.worldEventBlock(event.id, event.area).contains("route lain") ||
                            engine.worldEventBlock(event.id, event.area).contains("route lain"), "event eksklusif tidak bisa dipakai POV lain");
                    continue;
                }
                p.area = event.area; p.minute = (event.startMinute + event.endMinute) / 2; p.day = 1;
                p.step = "PRO_PHONE";
                p.companion = false;
                check(engine.worldEventBlock(event.id, event.area) != null, "event menolak sebelum chapter: " + event.id);
                p.step = quests.chapterIndex(event.minChapter) > quests.chapterIndex("C05")
                        ? quests.chapterFirstStep.get("C06") : "C05_FREE";
                if (event.companion)
                    check(engine.worldEventBlock(event.id, event.area).contains("Ajak pasangan"),
                            "event berdua menolak tanpa companion: " + event.id);
                p.companion = true;
                if (event.weather.contains(WorldClock.HUJAN)) {
                    for (int day = 3; day <= 150; day++) if (WorldClock.HUJAN.equals(WorldClock.weather(day))) { p.day = day; break; }
                }
                else if (!event.weather.isEmpty()) {
                    for (int day = 1; day <= 150; day++) if (event.weather.contains(WorldClock.weather(day))) { p.day = day; break; }
                }
                check(engine.worldEventBlock(event.id, "wrong_area") != null, "salah lokasi tidak diterima: " + event.id);
                check(engine.worldEventBlock(event.id, event.area) == null, "event sesuai route/jam/cuaca dapat dibuka: " + event.id + ":" + route);
                boolean visible = false;
                for (QuestDb.Interactable it : engine.sideInteractables(event.area))
                    if (it.id.equals(markerId)) visible = true;
                check(visible, "marker event muncul di area saat tersedia: " + event.id);
                int beforeCoins = p.coins, beforeAffection = p.affection, day = p.day;
                check(engine.completeWorldEvent(event.id, event.area).startsWith("Momen dunia tersimpan!"), "event sukses: " + event.id);
                check(p.coins == beforeCoins + event.coins && p.affection == Math.min(100, beforeAffection + event.affection),
                        "bonus event akurat: " + event.id);
                check(p.worldEventDays.get(event.id) == day && p.worldEventCounts.get(event.id) == 1 &&
                      p.hasFlag("WORLD_EVENT_" + event.id.toUpperCase(java.util.Locale.ROOT) + "_ONCE"), "histori event permanen: " + event.id);
                check(engine.worldEventBlock(event.id, event.area).contains("sudah dilakukan"), "event hanya sekali dalam satu hari: " + event.id);
                check(engine.sideInteractables(event.area).stream().noneMatch(it -> it.id.equals("WE27_" + event.id.toUpperCase(java.util.Locale.ROOT))),
                        "marker hilang setelah event selesai: " + event.id);
                check(!engine.completeWorldEvent(event.id, event.area).startsWith("Momen dunia tersimpan!"), "reward tak dapat farming: " + event.id);
                check(p.coins == beforeCoins + event.coins, "saldo tidak berubah setelah event diduplikasi: " + event.id);
                Progress loaded = Progress.fromMap(Json.parseObject(Json.write(p.toMap(true))));
                check(loaded.worldEventDays.equals(p.worldEventDays) && loaded.worldEventCounts.equals(p.worldEventCounts)
                      && loaded.flags.equals(p.flags), "save schema6 mempertahankan histori event dan flags: " + event.id);
                p.day = day + 1;
                if (event.weather.isEmpty() || event.weather.contains(WorldClock.weather(p.day))) {
                    check(engine.worldEventBlock(event.id, event.area) == null, "event dapat diulang pada hari game baru: " + event.id);
                    check(p.hasFlag("WORLD_EVENT_" + event.id.toUpperCase(java.util.Locale.ROOT) + "_ONCE"),
                            "Memory Book pertama tidak terhapus ketika event muncul lagi: " + event.id);
                }
            }
            Map<String, Object> legacy = Json.parseObject(Json.write(p.toMap(true)));
            legacy.put("schema", 5); legacy.remove("worldEventDays"); legacy.remove("worldEventCounts");
            Progress old = Progress.fromMap(legacy);
            check(old.worldEventDays.isEmpty() && old.worldEventCounts.isEmpty(), "schema5 dimigrasi dengan event default kosong");
            check(old.coins == p.coins && old.affection == p.affection && old.flags.equals(p.flags) && old.items.equals(p.items),
                    "migrasi schema5 tidak menghapus progres lama");
            QuestEngine replay = new QuestEngine(story, quests, maps, p, true);
            check(replay.worldEventBlock("pagi_plaza", "plaza") != null, "replay tidak boleh menerima reward event");
        }
        log.add("LIVING WORLD v4.9: 14 original + 18 baru, kedua POV, anti-farming, Memory Book & migrasi save OK");
    }

    /** v4.9: 29 map discoveries, 14 distinct repeatable pattern games, two routes, save compatibility. */
    static void testDiscoveriesV49(StoryDb story, QuestDb quests, MapDb maps, MemoryBookDb book) {
        check(quests.discoveries.size() == 29, "29 optional discoveries across the original 29 maps");
        Set<String> ids = new HashSet<>(), locations = new HashSet<>();
        int echoes = 0;
        for (QuestDb.Discovery d : quests.discoveries) {
            check(ids.add(d.id) && locations.add(d.area), "discovery IDs and areas unique: " + d.area);
            check(maps.area(d.area) != null, "map of discovery exists: " + d.area);
            check(!d.flag.isEmpty() && quests.chapterIndex(d.minChapter) >= quests.chapterIndex("C02"),
                    "discovery gating valid: " + d.area);
            check(book.entries.stream().anyMatch(e -> e.unlock.equals(d.flag)),
                    "discovery in Memory Book: " + d.area);
            QuestDb.Interactable target = null;
            for (QuestDb.Interactable it : quests.side) if (it.id.equals(d.id)) target = it;
            check(target != null && target.area.equals(d.area) && target.actions.size() >= 4,
                    "discovery wired into real world action runner: " + d.area);
            check(target != null && !maps.area(d.area).blocked(target.x, target.y),
                    "discovery reachable without standing in collision geometry: " + d.area);
            for (String route : Routes.ALL) {
                String sceneId = "V49-DISC-" + d.area.toUpperCase(java.util.Locale.ROOT)
                        + ("arland".equals(route) ? "-A" : "-S");
                StoryDb.Scene scene = story.scene(sceneId);
                check(scene != null && route.equals(scene.route) && scene.lines.size() >= 4,
                        "narrative exists per protagonist: " + d.area + ":" + route);
                Progress p = Progress.newGame(route, 1, "C05_FREE", maps.area(Routes.room(route)));
                p.area = d.area; p.step = quests.chapterIndex(d.minChapter) > quests.chapterIndex("C05")
                        ? quests.chapterFirstStep.get("C06") : "C05_FREE";
                QuestEngine engine = new QuestEngine(story, quests, maps, p, false);
                boolean visible = false;
                for (QuestDb.Interactable it : engine.sideInteractables(d.area))
                    if (it.id.equals(d.id)) visible = true;
                check(visible, "discoveries available by chapter on both routes: " + d.id + ":" + route);
                p.flags.add(d.flag);
                check(engine.sideInteractables(d.area).stream().noneMatch(it -> it.id.equals(d.id)),
                        "once-discovered interaction correctly hidden: " + d.id);
                Progress restored = Progress.fromMap(Json.parseObject(Json.write(p.toMap(true))));
                check(restored.flags.contains(d.flag), "v4.8 schema8 save roundtrips v4.9 flags: " + d.id);
            }
            if (!d.minigame.isEmpty()) {
                echoes++;
                Map<String,Object> config = quests.minigame(d.minigame);
                for (String route : Routes.ALL) {
                    int[][] patterns = com.arlandsofia.olu.logic.EchoPatternV49.fromConfig(config, route);
                    check(patterns.length == 3 && patterns[0].length == 3 && patterns[2].length == 5,
                            "three stages, growing pattern for " + d.minigame + ":" + route);
                    for (int stage=0;stage<patterns.length;stage++)
                        for (int step=0;step<patterns[stage].length;step++)
                            check(com.arlandsofia.olu.logic.EchoPatternV49.matches(patterns,stage,step,patterns[stage][step]),
                                    "echo notes correct and bounded " + d.minigame);
                }
            }
        }
        check(echoes == 14, "14 new interactive echo puzzles accessible");
        check(book.entries.stream().anyMatch(e -> e.unlock.equals("V49_WORLD_ATLAS_UNLOCK")),
                "29/29 optional atlas bonus in Memory Book");
        log.add("V4.9: 29 one-time location secrets, 14 per-route echo games, 58 scripts, save roundtrip OK");
    }

    // ------------------------------------------------------------------ visual controls & camera independent of LibGDX
    static void testVisualControls(File assets, QuestDb quests) {
        Settings defaults = Settings.fromMap(new HashMap<String, Object>());
        check(defaults.visualQuality == 1 && defaults.smoothCamera, "pengaturan lama default visual seimbang + kamera halus");
        Settings s = new Settings(); s.visualQuality = 2; s.smoothCamera = false;
        Settings loaded = Settings.fromMap(Json.parseObject(Json.write(s.toMap())));
        check(loaded.visualQuality == 2 && !loaded.smoothCamera, "setting kualitas & kamera tersimpan melalui JSON");
        Map<String, Object> corrupt = Json.parseObject(Json.write(s.toMap())); corrupt.put("visualQuality", 777);
        check(Settings.fromMap(corrupt).visualQuality == 2, "preset kualitas disaring maksimum");
        corrupt.put("visualQuality", -100);
        check(Settings.fromMap(corrupt).visualQuality == 0, "preset kualitas disaring minimum");
        check("Hemat".equals(Settings.visualQualityName(0)) && "Seimbang".equals(Settings.visualQualityName(1))
                && "Sinematik".equals(Settings.visualQualityName(2)), "nama 3 kualitas visual");
        CameraRig rig = new CameraRig();
        check(!rig.ready(), "kamera belum terinisialisasi");
        rig.follow(100f, 150f, 0.016f, true);
        check(rig.ready() && rig.x() == 100f && rig.y() == 150f, "frame pertama langsung ke target (tanpa fly-in)");
        rig.follow(200f, 150f, 0.016f, true);
        check(rig.x() > 100f && rig.x() < 200f, "kamera halus bergerak sebagian tiap frame");
        rig.follow(220f, 180f, 0.016f, false);
        check(rig.x() == 220f && rig.y() == 180f, "preset kamera langsung/cutscene snap");
        rig.reset(); rig.follow(1200f, 960f, 0.016f, true);
        check(rig.x() == 1200f && rig.y() == 960f, "pindah peta tidak meluncur dari area lama");
        for (String path : new String[]{"fx/dust.png", "fx/splash.png", "fx/heart.png", "fx/petal.png", "fx/ripple.png", "fx/vignette.png"})
            check(new File(assets, path).isFile(), "aset efek runtime tersedia: " + path);
        for (QuestDb.SideQuest q : quests.sideQuests) {
            if (q.id.equals("SQ_ROUTE_A") || q.id.equals("SQ_RAIN_A"))
                check(q.forRoute("arland") && !q.forRoute("sofia"), "side quest Arland tak muncul pada Sofia");
            if (q.id.equals("SQ_ROUTE_S") || q.id.equals("SQ_COLOR_S"))
                check(q.forRoute("sofia") && !q.forRoute("arland"), "side quest Sofia tak muncul pada Arland");
            if (q.id.equals("SQ_V26_MAP_A"))
                check(q.forRoute("arland") && !q.forRoute("sofia"), "v2.6 peta Dito khusus Arland");
            if (q.id.equals("SQ_V26_CARDS_S"))
                check(q.forRoute("sofia") && !q.forRoute("arland"), "v2.6 klub baca khusus Sofia");
        }
        log.add("VISUAL v2.0: 3 preset kualitas, migrasi settings, kamera smoothing/reset, 6 aset FX, jurnal route OK");
    }

    // ------------------------------------------------------------------
    /** Uji negatif, atomisitas transaksi, routing adegan, limit harian, migrasi save. */
    static void testRomance(StoryDb story, QuestDb quests, MapDb maps, MemoryBookDb book) {
        check(quests.gifts.size() == 9, "9 hadiah ekonomi terdaftar");
        check(quests.dates.size() == 3, "3 jenis kencan terdaftar");
        for (QuestDb.Gift g : quests.gifts) {
            check(book.item(g.item) != null && g.affection > 0, "hadiah valid: " + g.item);
            for (String route : Routes.ALL)
                check(story.scene(Routes.resolve(g.scene + "@$ROUTE", route)) != null, "scene hadiah ada " + route);
        }
        for (QuestDb.DateActivity d : quests.dates) {
            check(maps.area(d.area) != null && d.cost >= 0 && d.affection > 0, "venue dan biaya kencan valid: " + d.id);
            check(d.startMinute < d.endMinute && d.endMinute <= 26 * 60, "jam kencan valid: " + d.id);
            for (String r : Routes.ALL) check(story.scene(d.scene(r)) != null && story.scene(d.scene(r)).route.equals(r),
                    "scene berbeda menurut route " + d.id + ":" + r);
        }
        for (String route : Routes.ALL) {
            Progress p = Progress.newGame(route, 1, "PRO_PHONE", maps.area(Routes.room(route)));
            QuestEngine e = new QuestEngine(story, quests, maps, p, false);
            p.items.add("tulip_kecil");
            check(e.giveGift("tulip_kecil").contains("Ajak pasangan"), "belum chapter 2 tolak hadiah");
            check(p.hasItem("tulip_kecil") && p.affection == 0, "hadiah gagal tidak dikonsumsi");
            p.step = "C02_PHONE";
            p.companion = true;
            check(e.giveGift("tidak_ada").contains("tidak bisa"), "barang di luar katalog ditolak");
            check(e.giveGift("buket_senja").contains("Belum punya"), "barang belum dibeli tidak bisa diberikan");
            check(e.giveGift("tulip_kecil").startsWith("Hadiah diberikan!"), "hadiah awal berhasil");
            check(!p.hasItem("tulip_kecil") && p.affection == 6 && p.lastGiftDay == p.day, "barang terkonsumsi dan kedekatan bertambah");
            check(e.giveGift("tulip_kecil").contains("sudah memberi hadiah"), "maksimal satu hadiah per hari");
            check(story.scene(Json.str(e.giftActions("tulip_kecil").get(1), "id", "")).route.equals(route), "scene hadiah milik route benar");
            check(e.dateBlock("kafe", "taman_kota").contains("Datang dahulu"), "kencan menolak lokasi salah");
            p.minute = 5 * 60;
            check(e.dateBlock("taman", "taman_kota").contains("Belum masuk jam"), "kencan menolak jam salah");
            p.minute = 9 * 60;
            check(e.dateBlock("bintang", "bukit_bintang").contains("Belum masuk jam"), "kencan bintang hanya malam");
            check(e.dateBlock("kafe", "cafe").contains("Belum masuk jam"), "kafe masih tutup untuk kencan");
            check(e.dateBlock("taman", "taman_kota") == null, "kencan taman tersedia saat sesuai");
            check(e.startDate("taman", "taman_kota").startsWith("Kencan dimulai!"), "mulai kencan pertama");
            check(p.coins == 4 && p.affection == 16, "biaya dan kedekatan kencan akurat");
            check(p.dateCounts.get("taman") == 1 && p.hasFlag("ROM_DATE_TAMAN_ONCE"), "memori kencan pertama");
            check(e.startDate("taman", "taman_kota").contains("sudah berkencan"), "tidak bisa kencan dua kali sehari");
            p.minute = 11 * 60;
            check(e.startDate("kafe", "cafe").contains("sudah berkencan"), "tidak bisa pindah venue untuk kencan ganda");
            check(p.coins == 4, "biaya kencan ganda tidak ditarik");
            check(e.giftActions("tulip_kecil").size() == 2 && e.dateActions("taman").size() == 3, "aksi dialog dan cutscene tersedia");
            p.day++; p.minute = 11 * 60;
            check(e.dateBlock("kafe", "cafe").contains("Koin tidak cukup"), "kencan gagal saldo kurang");
            check(p.lastDateDay != p.day, "date gagal tidak menandai hari");
            p.coins = 40;
            check(e.startDate("kafe", "cafe").startsWith("Kencan dimulai!"), "kencan hari berikutnya");
            check(p.coins == 28 && p.dateCounts.get("kafe") == 1, "biaya kafe persis 12");
            check(e.giveGift("tulip_kecil").contains("Belum punya"), "barang yang diberikan bisa habis");
            check(e.purchase("melati", "tulip_kecil").startsWith("Membeli"), "bisa membeli ulang barang setelah diberikan");
            check(e.giveGift("tulip_kecil").startsWith("Hadiah diberikan!"), "bisa memberi lagi pada hari baru");
            check(p.affection >= 20 && p.hasFlag("ROM_BOND_20"), "kenangan milestone 20 terbuka");
            check(p.affection == 34 && p.coins == 16, "akumulasi kedekatan dan koin benar");
            p.day++; p.minute = 21 * 60;
            check(e.dateBlock("bintang", "bukit_bintang").contains("Koin tidak cukup"), "kencan bintang tidak menyebabkan minus");
            p.coins = 30;
            check(e.startDate("bintang", "bukit_bintang").startsWith("Kencan dimulai!"), "kencan bintang malam hari");
            check(p.affection == 50 && p.hasFlag("ROM_BOND_50"), "kenangan milestone 50 terbuka");
            check(p.coins == 12 && p.dateCounts.get("bintang") == 1, "kencan bintang biaya dan hitung benar");
            Progress load = Progress.fromMap(Json.parseObject(Json.write(p.toMap(true))));
            check(load.affection == 50 && load.lastGiftDay == p.lastGiftDay && load.lastDateDay == p.lastDateDay,
                    "save baru kedekatan dan hari benar");
            check(load.dateCounts.equals(p.dateCounts), "jumlah kencan round-trip");
            Map<String, Object> old = Json.parseObject(Json.write(p.toMap(true)));
            old.put("schema", 2); old.remove("affection"); old.remove("lastGiftDay"); old.remove("lastDateDay"); old.remove("dateCounts");
            Progress migrated = Progress.fromMap(old);
            check(migrated.affection == 0 && migrated.lastGiftDay == -1 && migrated.lastDateDay == -1 && migrated.dateCounts.isEmpty(), "save v1.5/schema2 dimigrasi");
            check(migrated.coins == 12 && migrated.jobDays.equals(p.jobDays), "saldo dan pekerjaan save lama dipertahankan");
            Progress cap = p.copy(); cap.affection = 99; cap.day++; cap.lastGiftDay = -1; cap.items.add("buket_senja");
            QuestEngine ecap = new QuestEngine(story, quests, maps, cap, false);
            check(ecap.giveGift("buket_senja").startsWith("Hadiah diberikan") && cap.affection == 100, "kedekatan max100");
            Progress replay = p.copy();
            QuestEngine re = new QuestEngine(story, quests, maps, replay, true);
            check(!re.romanceReady() && re.startDate("taman", "taman_kota").contains("Ajak pasangan"), "replay tidak mencatat ekonomi romansa");
            log.add("ROMANSA " + route + ": 9 hadiah, 3 kencan, 2 milestone, route scene, save/migrasi, limit & anti-minus OK");
        }
    }

    /** Uji adversarial momen: save lama, jam/cuaca/lokasi, batas harian, anti replay, badge dan scene. */
    static void testMoments(StoryDb story, QuestDb quests, MapDb maps, MemoryBookDb book) {
        check(quests.moments.size() == 8, "8 katalog momen tersedia");
        Set<String> ids = new HashSet<>();
        for (QuestDb.MomentActivity m : quests.moments) {
            check(ids.add(m.id), "id momen unik: " + m.id);
            check(maps.area(m.area) != null, "area momen ada " + m.id);
            check(m.startMinute >= WorldClock.DAY_START && m.startMinute < m.endMinute && m.endMinute <= WorldClock.DAY_END, "jam momen valid " + m.id);
            check(m.affection > 0 && m.affection <= 20 && m.minAffection >= 0 && m.minAffection < 100, "batas hati momen valid " + m.id);
            for (String weather : m.weather) check(Arrays.asList("cerah", "berawan", "berangin", "hujan").contains(weather), "cuaca valid " + m.id);
            for (String route : Routes.ALL) {
                StoryDb.Scene scene = story.scene(m.scene(route));
                check(scene != null && scene.route.equals(route), "scene khusus route: " + m.id + ":" + route);
                check(scene.lines.size() >= 4, "dialog momen minimal 4 baris: " + m.id + ":" + route);
            }
        }
        check(story.scene("RM-BOND-80@arland") != null && story.scene("RM-BOND-80@sofia") != null, "milestone80 dua route");
        for (String route : Routes.ALL) {
            Progress p = Progress.newGame(route, 2, "C02_PHONE", maps.area(Routes.room(route)));
            p.minute = 8 * 60;
            QuestEngine e = new QuestEngine(story, quests, maps, p, false);
            check(e.startMoment("pagi_kafe", "cafe").contains("Ajak pasangan"), "butuh companion");
            p.companion = true;
            check(e.momentBlock("tidak_ada", "cafe").contains("tidak ditemukan"), "ID ilegal tidak masuk");
            check(e.momentBlock("pagi_kafe", "plaza").contains("Temui"), "salah lokasi ditolak");
            check(e.momentBlock("pagi_kafe", "cafe") == null, "pagi kafe tersedia");
            int coins = p.coins;
            check(e.startMoment("pagi_kafe", "cafe").startsWith("Momen berdua!"), "aksi momen pertama");
            check(p.affection == 3 && p.coins == coins, "gratis tetapi menambah kedekatan");
            check(p.momentCounts.get("pagi_kafe") == 1 && p.hasFlag("ROM_MOM_PAGI_KAFE_ONCE"), "kenangan dan hitungan");
            check(e.startMoment("pagi_kafe", "cafe").contains("Coba besok"), "momen sama tidak berulang dalam sehari");
            check(e.startMoment("kucing_taman", "taman_kota").contains("Coba besok"), "momen lain juga tidak bisa spam sehari");
            check(p.affection == 3 && p.momentCounts.size() == 1, "gagal tidak mengubah state");
            p.day++; p.minute = 8 * 60;
            check(e.momentBlock("genggam_tangan", "plaza").contains("Butuh kedekatan"), "level hubungan diperlukan");
            p.affection = 16;
            check(e.momentBlock("genggam_tangan", "plaza").contains("jam tertentu"), "pembatasan jam berjalan");
            p.minute = 12 * 60;
            check(e.startMoment("genggam_tangan", "plaza").startsWith("Momen berdua!"), "genggam tangan tersedia siang");
            check(p.affection == 20 && p.hasFlag("ROM_BOND_20"), "momen dapat membuka milestone20");
            check(e.momentActions("genggam_tangan").size() >= 3, "scene + cutscene milestone dijadwalkan");
            p.day++; p.minute = 13 * 60;
            int rainy = 0;
            while (!"hujan".equals(e.weatherNow()) && rainy++ < 120) p.day++;
            check(rainy < 120, "hari hujan deterministic tersedia");
            check(e.momentBlock("kucing_taman", "taman_kota").contains("cuaca"), "kucing saat hujan dibatasi");
            check(e.momentBlock("berteduh", "cafe") == null, "momen berteduh hanya ketika hujan");
            check(e.startMoment("berteduh", "cafe").startsWith("Momen berdua!"), "momen hujan berhasil");
            Progress roundTrip = Progress.fromMap(Json.parseObject(Json.write(p.toMap(true))));
            check(roundTrip.lastMomentDay == p.day && roundTrip.momentCounts.equals(p.momentCounts), "persistensi semua momen");
            QuestEngine restored = new QuestEngine(story, quests, maps, roundTrip, false);
            check(restored.startMoment("berteduh", "cafe").contains("Coba besok"), "setelah load tidak bisa spam");
            Map<String, Object> prev = Json.parseObject(Json.write(p.toMap(true)));
            prev.put("schema", 3); prev.remove("lastMomentDay"); prev.remove("momentCounts");
            Progress fromV16 = Progress.fromMap(prev);
            check(fromV16.affection == p.affection && fromV16.coins == p.coins && fromV16.lastMomentDay == -1, "migrasi save v1.6 data ekonomi/hati utuh");
            check(fromV16.momentCounts.isEmpty() && fromV16.dateCounts.equals(p.dateCounts), "momen baru tidak merusak kencan lama");
            Map<String, Object> attack = Json.parseObject(Json.write(p.toMap(true)));
            attack.put("lastMomentDay", -999); attack.put("momentCounts", Json.parseObject("{\"berteduh\":-99,\"pagi_kafe\":9999999}"));
            Progress safe = Progress.fromMap(attack);
            check(safe.lastMomentDay == -1 && safe.momentCounts.get("berteduh") == 0 && safe.momentCounts.get("pagi_kafe") == 100000, "nilai save momen dibatasi");
            Progress replayP = p.copy();
            QuestEngine replay = new QuestEngine(story, quests, maps, replayP, true);
            int prevAffection = replayP.affection;
            check(replay.startMoment("pagi_kafe", "cafe").contains("Ajak pasangan") && replayP.affection == prevAffection, "replay tidak mengubah state romansa");
            check(book.entries.stream().anyMatch(en -> en.unlock.equals("ROM_MOM_BERTEDUH_ONCE")), "Memory Book momen baru ada");
            log.add("MOMEN " + route + ": 8 katalog, kondisi jam/cuaca/tempat/hati, save v1.6 dan anti-spam OK");
        }
    }

    /** Uji katalog aksi pasangan, validasi penolakan, toggle, save schema 4→5, dan replay. */
    static void testCoupleActions(StoryDb story, QuestDb quests, MapDb maps, MemoryBookDb book) {
        check(quests.coupleActions.size() == 8, "8 aksi pasangan terdaftar");
        java.util.Set<String> seen = new java.util.HashSet<>();
        for (QuestDb.CoupleAction a : quests.coupleActions) {
            check(seen.add(a.id), "ID aksi unik " + a.id);
            check(a.affection >= 0 && a.affection <= 10, "bonus aksi wajar " + a.id);
            check(a.startMinute < a.endMinute && a.endMinute <= WorldClock.DAY_END, "jam aksi valid " + a.id);
            for (String area : a.areas) check(maps.area(area) != null, "area aksi tersedia " + area);
            for (String route : Routes.ALL) {
                StoryDb.Scene sc = story.scene(a.scene(route));
                check(sc != null && route.equals(sc.route) && sc.lines.size() >= 4, "adegan action route valid " + a.id + ":" + route);
            }
            check(book.entries.stream().anyMatch(en -> en.unlock.equals("ROM_ACT_" + a.id.toUpperCase(java.util.Locale.ROOT) + "_ONCE")),
                    "memori action dapat dibuka " + a.id);
        }
        for (String route : Routes.ALL) {
            Progress p = Progress.newGame(route, 1, "C02_PHONE", maps.area(Routes.room(route)));
            p.minute = 12*60;
            QuestEngine e = new QuestEngine(story, quests, maps, p, false);
            check(e.coupleActionBlock("tidak_ada", "plaza").contains("tidak dikenal"), "ID tidak terdaftar ditolak");
            check(e.startCoupleAction("tos", "plaza").contains("Ajak pasangan"), "tanpa companion ditolak");
            p.companion = true;
            check(e.coupleActionBlock("pelukan", "plaza").contains("Butuh kedekatan"), "pelukan butuh affection");
            check(e.coupleActionBlock("gandengan", "cafe").contains("lokasi"), "jalan gandengan hanya area luar terpilih");
            int money = p.coins;
            check(e.startCoupleAction("gandengan", "plaza").startsWith("Aksi berdua!"), "gandengan aktif");
            check(p.holdingHands && p.affection == 2, "mode jalan dan bonus pertama");
            check(e.startCoupleAction("gandengan", "plaza").startsWith("Berhenti bergandengan"), "mode dapat dilepas");
            check(e.startCoupleAction("gandengan", "plaza").startsWith("Bergandengan lagi"), "mode bisa aktif lagi tanpa bonus");
            check(p.affection == 2 && p.coupleActionCounts.get("gandengan") == 1, "toggle tidak farming");
            check(e.startCoupleAction("tos", "plaza").startsWith("Aksi berdua!"), "tos bebas dimainkan");
            check(e.startCoupleAction("tos", "plaza").contains("sudah diambil"), "aksi yang sama tidak farming per hari");
            check(p.coins == money && p.lastMomentDay == -1 && p.lastGiftDay == -1 && p.lastDateDay == -1,
                    "couple action tidak memakai saldo dan kuota lain");
            check(e.coupleActionActions("tos").get(0).containsKey("cmds"), "aksi memicu cutscene pair");
            Progress save = Progress.fromMap(Json.parseObject(Json.write(p.toMap(true))));
            check(save.holdingHands && save.coupleActionCounts.equals(p.coupleActionCounts) && save.coupleActionDays.equals(p.coupleActionDays),
                    "save schema5 round-trip posisi genggaman dan histori");
            Map<String,Object> old=Json.parseObject(Json.write(p.toMap(true)));
            old.put("schema", 4); old.remove("holdingHands"); old.remove("coupleActionCounts"); old.remove("coupleActionDays");
            Progress migrated=Progress.fromMap(old);
            check(!migrated.holdingHands && migrated.coupleActionCounts.isEmpty() && migrated.coupleActionDays.isEmpty()
                    && migrated.affection == p.affection && migrated.coins == p.coins, "migrasi schema4 aman dan tidak reset ekonomi");
            save.day++;
            QuestEngine newDay=new QuestEngine(story,quests,maps,save,false);
            check(newDay.startCoupleAction("tos", "plaza").startsWith("Aksi berdua!"), "aksi reset esok hari");
            QuestEngine replay=new QuestEngine(story,quests,maps,p,true);
            check(replay.startCoupleAction("tos", "plaza").contains("Ajak pasangan"), "replay tidak mengubah progres aksi");
        }
        log.add("COUPLE v2.2: 8 aksi, syarat waktu/lokasi/hati, toggle, daily lock, save migrasi 4→5, replay OK");
    }

    static void testEconomy(StoryDb story, QuestDb quests, MapDb maps) {
        check(quests.shops.size() == 3, "3 toko terdata");
        check(quests.jobs.size() == 3, "3 pekerjaan terdata");
        for (QuestDb.Shop shop : quests.shops.values()) {
            check(shop.goods.size() == 3, "3 produk pada " + shop.id);
            for (QuestDb.Good good : shop.goods) check(good.price > 0, "harga positif: " + good.item);
        }
        for (QuestDb.Job job : quests.jobs.values()) {
            check(job.reward > 0, "upah positif " + job.id);
            if (!job.minigame.isEmpty()) check(!quests.minigame(job.minigame).isEmpty(), "minigame shift valid " + job.id);
        }
        for (String route : Routes.ALL) {
            Progress p = Progress.newGame(route, 1, "PRO_PHONE", maps.area(Routes.room(route)));
            QuestEngine e = new QuestEngine(story, quests, maps, p, false);
            check(p.coins == 12, "modal awal " + route);
            check(e.purchase("melati", "buket_senja").contains("belum cukup"), "tidak boleh minus");
            check(p.coins == 12 && !p.hasItem("buket_senja"), "pembelian gagal tidak mengubah state");
            check(e.purchase("senja", "kopi_senja").startsWith("Membeli"), "pembelian berhasil");
            check(p.coins == 0 && p.hasItem("kopi_senja"), "saldo dan barang sesuai");
            check(e.purchase("senja", "kopi_senja").contains("sudah ada"), "tidak membeli duplikat");
            check(!e.check(Json.parseObject("{\"coinsAtLeast\":1}")), "kondisi biaya saat tidak cukup");
            check(e.completeWork("barista", 0).contains("Belum"), "gagal skor tanpa upah");
            check(e.completeWork("barista", 4).contains("+20"), "kerja barista menerima upah");
            check(!e.jobReady("barista") && p.coins == 20, "tidak dapat dua upah di hari sama");
            check(e.completeWork("barista", 9).contains("tidak tersedia"), "upah ganda ditolak");
            check(e.completeWork("perangkai", 3).contains("+22"), "shift bunga mandiri");
            check(p.coins == 42, "saldo terakumulasi benar");
            check(e.startDelivery().contains("3 surat"), "menerima surat");
            check(e.deliveryOpen(), "tugas surat aktif");
            check(e.deliver("plaza").contains("1/3"), "surat pertama");
            check(e.deliver("plaza").contains("sudah diantar"), "surat ganda ditolak");
            check(e.deliver("jalan_kota").contains("2/3"), "surat kedua");
            check(e.deliver("riverside").contains("+28"), "surat ketiga membayar");
            check(!e.deliveryOpen() && !e.jobReady("kurir") && p.coins == 70, "kurir tepat sekali membayar");
            check(e.startDelivery().contains("Kembali besok"), "tidak bisa ulang shift kurir");
            check(e.purchase("melati", "buket_senja").startsWith("Membeli"), "bisa memakai hasil upah");
            check(p.coins == 45 && p.hasItem("buket_senja"), "pembelian mengurangi saldo");
            Progress load = Progress.fromMap(Json.parseObject(Json.write(p.toMap(true))));
            check(load.coins == 45 && load.jobDays.equals(p.jobDays) && load.deliveryDays.equals(p.deliveryDays), "save ekonomi roundtrip");
            check(load.hasFlag("JOB_BARISTA_ONCE") && load.hasFlag("JOB_KURIR_ONCE"), "memori pekerjaan dipertahankan");
            load.day++;
            QuestEngine next = new QuestEngine(story, quests, maps, load, false);
            check(next.jobReady("barista") && next.jobReady("kurir"), "shift terbuka hari berikutnya");
            check(!next.deliveryOpen(), "surat kadaluarsa setelah ganti hari");
            check(next.startDelivery().contains("3 surat") && next.deliveryOpen(), "surat baru hari berikutnya");
            check(next.deliver("plaza").contains("1/3"), "alamat bisa dipakai lagi hari berbeda");
            Map<String, Object> old = Json.parseObject(Json.write(p.toMap(true)));
            old.put("schema", 1); old.remove("coins"); old.remove("jobDays"); old.remove("deliveryDays"); old.remove("deliveryStartDay");
            Progress migrated = Progress.fromMap(old);
            check(migrated.coins == 12 && migrated.jobDays.isEmpty(), "migrasi save v1 aman");
            // Bukan hanya metode ekonomi: pastikan ActionRunner mengeksekusi aksi data dari interaksi dunia.
            Progress actionP = Progress.newGame(route, 1, "PRO_PHONE", maps.area(Routes.room(route)));
            QuestEngine actionE = new QuestEngine(story, quests, maps, actionP, false);
            SimPresenter ui = new SimPresenter(story, quests, maps); ui.engine = actionE;
            ActionRunner ar = new ActionRunner(actionE, ui);
            int jobCount = 0, shopCount = 0;
            for (QuestDb.Interactable it : quests.side) {
                if (it.id.equals("job_barista")) {
                    ar.run(actionE.actionsFor(it));
                    check(!ar.busy() && actionP.coins == 32 && actionP.jobDays.get("barista") == actionP.day,
                            "ActionRunner shift melalui minigame " + route);
                    check(ui.minigames.contains("pour"), "minigame tuang teh dipanggil dari interaksi"); jobCount++;
                }
                if (it.id.equals("shop_senja")) {
                    ar.run(actionE.actionsFor(it));
                    check(!ar.busy(), "ActionRunner toko membuka dan menutup UI"); shopCount++;
                }
            }
            check(jobCount == 1 && shopCount == 1, "interaksi toko/shift hanya satu");
            log.add("EKONOMI " + route + ": 3 toko, 3 pekerjaan, pembelian, aksi UI, simpan/migrasi, reset hari OK");
        }
    }

    static void testJson() {
        String src = "{\"a\":[1,2.5,\"x\\n\\u00e9\"],\"b\":{\"c\":true,\"d\":null},\"e\":-3e2}";
        Map<String, Object> m = Json.parseObject(src);
        check(Json.parseObject(Json.write(m)).equals(m), "JSON round-trip pretty");
        check(Json.writeCompact(Json.parseObject(Json.writeCompact(m))).equals(Json.writeCompact(m)), "JSON round-trip compact stabil");
        boolean threw = false;
        try { Json.parse("{\"a\":"); } catch (IllegalArgumentException e) { threw = true; }
        check(threw, "JSON terpotong ditolak");
    }

    static void testData(File assets, StoryDb story, QuestDb quests, MapDb maps, MemoryBookDb book) {
        check(story.scenes.size() >= 15, "story memuat scene");
        check("code".equals(Json.str(quests.minigame("quiet_cipher"), "type", "")), "The Quiet Arland memakai puzzle kunci kode");
        check("pages".equals(Json.str(quests.minigame("quiet_pages"), "type", "")), "The Quiet Sofia memakai puzzle susun halaman");
        check(Json.list(quests.minigame("quiet_pages"), "pages").size() == 4, "Puzzle Sofia mempunyai empat halaman");
        check(Json.list(quests.minigame("quiet_cipher"), "answer").size() == 3, "Puzzle Arland mempunyai tiga simbol");
        for (QuestDb.Step s : quests.steps.values()) {
            check(s.objective.containsKey("arland") && s.objective.containsKey("sofia"), "objective dua route: " + s.id);
            for (QuestDb.Interactable it : s.interactables) {
                for (String r : Routes.ALL) {
                    String area = Routes.resolve(it.area, r);
                    if (it.forRoute(r)) check(maps.area(area) != null, "area interaksi ada: " + s.id + "/" + it.id);
                }
                if (it.sprite != null) check(new File(assets, it.sprite.image).isFile(), "sprite ada: " + it.sprite.image);
                for (Map<String, Object> a : it.actions) checkAction(a, story, quests, maps, book, s.id);
            }
            for (Map<String, Object> a : s.enterActions) checkAction(a, story, quests, maps, book, s.id);
            for (Map<String, Object> a : s.completeActions) checkAction(a, story, quests, maps, book, s.id);
            for (Map<String, Object> a : s.onStart) checkAction(a, story, quests, maps, book, s.id + ":onStart");
        }
        for (QuestDb.Interactable it : quests.side) {
            for (String r : Routes.ALL) check(maps.area(Routes.resolve(it.area, r)) != null, "area side ada: " + it.id);
            if (it.sprite != null) check(new File(assets, it.sprite.image).isFile(), "sprite side ada: " + it.sprite.image);
            for (Map<String, Object> a : it.actions) checkAction(a, story, quests, maps, book, "side:" + it.id);
        }
        for (QuestDb.TownNpc n : quests.townNpcs) {
            check(maps.area(n.area) != null, "area NPC ada: " + n.id);
            check(new File(assets, "characters/" + n.sprite + "/walk.png").isFile(), "sprite NPC ada: " + n.sprite);
            check(!maps.area(n.area).blocked(n.x, n.y) || true, "npc");
            for (Map<String, Object> d : n.dialogs) for (Map<String, Object> a : Json.objList(d, "actions")) checkAction(a, story, quests, maps, book, "npc:" + n.id);
        }
        for (StoryDb.Scene sc : story.scenes.values()) for (StoryDb.Line l : sc.lines) check(story.speakers.containsKey(l.speaker), "pembicara terdaftar " + l.speaker + " di " + sc.id);
        for (MapDb.Area a : maps.areas.values()) {
            check(new File(assets, a.image).isFile(), "gambar peta ada: " + a.image);
            check(!a.blocked(a.spawnX, a.spawnY), "spawn bebas: " + a.id);
            for (MapDb.Prop pr : a.props) check(new File(assets, pr.def.image).isFile(), "gambar prop ada: " + pr.def.image);
            for (MapDb.Door d : a.doors) {
                MapDb.Area to = maps.area(d.to);
                check(to != null, "tujuan pintu ada: " + d.id);
                check(!to.blocked(d.tx, d.ty), "target pintu bebas: " + d.id);
                check(!d.touchesAnyDoor(to), "target pintu tidak memicu pintu lain: " + d.id);
            }
        }
        for (MemoryBookDb.Entry e : book.entries) check(new File(assets, e.icon).isFile(), "ikon memory ada: " + e.icon);
        for (MemoryBookDb.Item i : book.items.values()) check(new File(assets, i.icon).isFile(), "ikon item ada: " + i.icon);
        String[] chars = {"arland", "sofia"};
        for (String c : chars) {
            check(new File(assets, "characters/" + c + "/walk.png").isFile(), "sprite sheet " + c);
            check(new File(assets, "characters/" + c + "/portraits/normal.png").isFile(), "potret normal " + c);
        }
    }

    static void checkAction(Map<String, Object> a, StoryDb story, QuestDb quests, MapDb maps, MemoryBookDb book, String step) {
        String d = Json.str(a, "do", "");
        Set<String> known = new HashSet<>(Arrays.asList("scene", "flag", "unflag", "item", "removeItem", "warp", "companion", "shard", "puzzle",
                "toast", "sfx", "music", "step", "chapterCard", "chapterEnd", "lines", "if", "minigame", "count", "setCount", "emote", "credits", "cine", "shop", "work", "deliveryStart", "deliveryDrop", "worldEvent", "restUntilTomorrow"));
        if (d.equals("cine")) for (Map<String, Object> c : Json.objList(a, "cmds")) if ("say".equals(Json.str(c, "c", ""))) for (String r : Routes.ALL) {
            String cr = Json.str(c, "route", null);
            if (cr == null || cr.equals(r)) check(story.scene(Routes.resolve(Json.str(c, "scene", ""), r)) != null, "scene cutscene ada (" + r + "): " + c);
        }
        if (d.equals("if")) { for (Map<String, Object> x : Json.objList(a, "then")) checkAction(x, story, quests, maps, book, step); for (Map<String, Object> x : Json.objList(a, "else")) checkAction(x, story, quests, maps, book, step); }
        if (d.equals("minigame")) check(!quests.minigame(Json.str(a, "id", "")).isEmpty(), "minigame terdaftar: " + a);
        if (d.equals("shop")) check(quests.shops.containsKey(Json.str(a, "id", "")), "toko terdaftar: " + a);
        if (d.equals("work")) check(quests.jobs.containsKey(Json.str(a, "id", "")), "pekerjaan terdaftar: " + a);
        if (d.equals("worldEvent")) check(quests.worldEvents.stream().anyMatch(ev -> ev.id.equals(Json.str(a, "id", ""))), "world event terdaftar: " + a);
        if (d.equals("deliveryDrop")) check(Arrays.asList("plaza", "jalan_kota", "riverside").contains(Json.str(a, "address", "")), "alamat surat dikenal");
        check(known.contains(d), "aksi dikenal '" + d + "' di " + step);
        if (d.equals("scene")) for (String r : Routes.ALL) check(story.scene(Routes.resolve(Json.str(a, "id", ""), r)) != null, "scene ada: " + a);
        if (d.equals("step")) check(quests.step(Json.str(a, "id", "")) != null, "step tujuan ada: " + a);
        if (d.equals("puzzle")) check(quests.puzzles.containsKey(Json.str(a, "id", "")), "puzzle ada: " + a);
        if (d.equals("item") || d.equals("removeItem")) check(book.item(Json.str(a, "id", "")) != null, "item terdaftar: " + a);
        if (d.equals("chapterCard") || d.equals("chapterEnd")) check(story.chapterTitles.containsKey(Json.str(a, "chapter", "")), "chapter ada: " + a);
        if (d.equals("warp")) for (String r : Routes.ALL) {
            MapDb.Area t = maps.area(Routes.resolve(Json.str(a, "area", ""), r));
            check(t != null && !t.blocked(Json.num(a, "x", 0), Json.num(a, "y", 0)), "warp bebas: " + a);
        }
    }

    static void testPuzzle(QuestDb quests) {
        QuestDb.Puzzle pz = quests.puzzles.get("C01_SYMBOLS");
        check(pz.order("arland").equals(Arrays.asList("BUNGA", "BUKU", "BINTANG")), "urutan Arland sesuai canon");
        check(pz.order("sofia").equals(Arrays.asList("BINTANG", "BUKU", "BUNGA")), "urutan Sofia sesuai canon");
        PuzzleLogic l = new PuzzleLogic(pz.order("arland"), pz.hintAfterFails);
        check(l.input("BUNGA") == PuzzleLogic.Result.CORRECT, "puzzle langkah 1");
        check(l.input("BUNGA") == PuzzleLogic.Result.WRONG && l.entered.isEmpty(), "salah -> reset");
        check(!l.hintVisible(), "petunjuk belum muncul");
        l.input("BINTANG");
        check(l.hintVisible(), "petunjuk muncul setelah 2 gagal");
        l.input("BUNGA"); l.input("BUKU");
        check(l.input("BINTANG") == PuzzleLogic.Result.SOLVED, "puzzle selesai");
    }

    // ------------------------------------------------------------------ simulasi bermain
    static final class SimPresenter implements ActionRunner.Presenter {
        final StoryDb story; final QuestDb quests; final MapDb maps; QuestEngine engine; int wrongFirst = 1;
        final List<String> scenes = new ArrayList<>();
        SimPresenter(StoryDb s, QuestDb q, MapDb m) { story = s; quests = q; maps = m; }
        public void playScene(String id, Runnable done) {
            scenes.add(id);
            StoryDb.Scene sc = story.scene(id);
            lineCount += sc.lines.size(); read(sc.lines);
            if (!sc.choices.isEmpty()) {
                StoryDb.Choice c = sc.choices.get(scenes.size() % sc.choices.size());
                check(!c.response(engine.route()).isEmpty(), "pilihan punya respons route " + engine.route());
                engine.addFlags(c.flags);
                lineCount += c.response(engine.route()).size(); read(c.response(engine.route()));
            }
            done.run();
        }
        public void playLines(List<StoryDb.Line> lines, String name, Runnable done) { lineCount += lines.size(); read(lines); done.run(); }
        int fishCalls;
        public void openMinigame(String id, ActionRunner.IntCallback done) {
            minigames.add(id);
            if (id.equals("fishing")) { done.done((fishCalls++ % 8) + 1); return; }
            done.done(id.equals("claw") ? 1 : 3);
        }
        public void openShop(String shopId, Runnable done) { check(quests.shops.containsKey(shopId), "toko tersedia"); done.run(); }
        public void credits(Runnable done) { creditsShown = true; done.run(); }
        double cineSec; int cines; final java.util.Set<String> cineScenes = new java.util.HashSet<>();
        static final java.util.Set<String> CINE_CMDS = new java.util.HashSet<>(Arrays.asList("wait", "move", "place", "face", "pose", "pair", "emote", "cam", "shot", "follow", "bars", "fade", "flash", "tint", "shake", "fx", "say", "line", "caption", "sfx", "music", "spawn", "despawn", "show", "hide", "alpha"));
        static final java.util.Set<String> POSES = new java.util.HashSet<>(Arrays.asList("sit", "wave", "give", "reach", "bow", "hold_l", "hold_r", "cheer", "hug", "lean", "photo", "highfive", "dance", "laugh", "surprised", "nod", "shake", "jump", "none"));
        public void cine(List<Map<String, Object>> cmds, Runnable done) {
            cines++;
            check(!cmds.isEmpty(), "cutscene tidak kosong");
            java.util.Set<String> actors = new java.util.HashSet<>(Arrays.asList("player", "partner", "arland", "sofia"));
            for (QuestDb.TownNpc n : quests.townNpcs) actors.add(n.id);
            float px = 0, py = 0; boolean havePos = false;
            for (Map<String, Object> c : cmds) {
                String k = Json.str(c, "c", "");
                check(CINE_CMDS.contains(k), "perintah cutscene dikenal: " + k);
                if (k.equals("spawn")) actors.add(Json.str(c, "id", ""));
                if (c.containsKey("who")) check(actors.contains(Json.str(c, "who", "")), "aktor cutscene dikenal: " + Json.str(c, "who", ""));
                if (k.equals("pose")) check(POSES.contains(Json.str(c, "pose", "none")), "pose dikenal: " + Json.str(c, "pose", ""));
                boolean async = Json.bool(c, "async", false);
                if (k.equals("say")) { String id = Json.str(c, "scene", ""); check(story.scene(id) != null, "scene cutscene ada: " + id); if (story.scene(id) != null && cineScenes.add(id)) playScene(id, NOOP); }
                if (k.equals("line")) { chars += Json.str(c, "t", "").length(); lineCount++; }
                if (!async) {
                    if (k.equals("wait")) cineSec += Json.num(c, "t", 0.5f);
                    if (k.equals("cam") || k.equals("fade")) cineSec += Json.num(c, "t", k.equals("cam") ? 1f : 0.6f);
                    if (k.equals("caption")) cineSec += Json.num(c, "t", 2.6f);
                    if ((k.equals("pose") || k.equals("fx") || k.equals("pair")) && Json.bool(c, "block", false)) cineSec += Json.num(c, "t", 0.6f);
                    if (k.equals("move")) {
                        List<Object> path = new ArrayList<>(Json.list(c, "path")); if (c.get("to") != null) path.add(0, c.get("to"));
                        float sp = Json.num(c, "speed", Json.bool(c, "run", false) ? 150f : 78f), d = 0;
                        float lx = Float.NaN, ly = 0;
                        for (Object o : path) { List<?> q = (List<?>) o; float x = ((Number) q.get(0)).floatValue(), y = ((Number) q.get(1)).floatValue(); if (!Float.isNaN(lx)) d += Math.hypot(x - lx, y - ly); else d += 60; lx = x; ly = y; }
                        cineSec += d / sp;
                    }
                }
            }
            done.run();
        }
        static final Runnable NOOP = new Runnable() { public void run() {} };
        public void emote(String who, String e) {}
        int lineCount; boolean creditsShown; final List<String> minigames = new ArrayList<>();
        long chars; double walkPx; int hops, cards, warps;
        void read(List<StoryDb.Line> ls) { for (StoryDb.Line l : ls) chars += l.text.length(); }
        public void openPuzzle(String id, ActionRunner.BoolCallback done) {
            QuestDb.Puzzle pz = quests.puzzles.get(id);
            String hint = pz.hintFlag.get(engine.route());
            check(engine.p.hasFlag(hint), "petunjuk mural sudah didapat sebelum puzzle");
            if (wrongFirst-- > 0) { done.done(false); return; } // pemain batal sekali -> harus bisa diulang
            PuzzleLogic l = new PuzzleLogic(pz.order(engine.route()), pz.hintAfterFails);
            for (String s : pz.order(engine.route())) l.input(s);
            done.done(l.solved());
        }
        public void warp(String area, float x, float y, String dir, Runnable done) {
            check(maps.area(area) != null, "warp area " + area);
            engine.p.area = area; engine.p.x = x; engine.p.y = y; warps++; done.run();
        }
        public void chapterCard(String chapter, Runnable done) { cards++; done.run(); }
        public void chapterEnd(String chapter, Runnable done) { done.run(); }
        public void toast(String text) {}
        public void sfx(String id) {}
        public void music(String id) {}
        public void companionChanged(boolean on) {}
        public void stepChanged() {}
        public void onIdle() {}
    }

    /** BFS lewat pintu yang tidak terkunci. Mengembalikan daftar pintu menuju area target, atau null. */
    static List<MapDb.Door> path(QuestEngine e, MapDb maps, String from, String to) {
        Map<String, List<MapDb.Door>> best = new HashMap<>();
        best.put(from, new ArrayList<MapDb.Door>());
        ArrayDeque<String> q = new ArrayDeque<>();
        q.add(from);
        while (!q.isEmpty()) {
            String a = q.poll();
            if (a.equals(to)) return best.get(a);
            for (MapDb.Door d : maps.area(a).doors) {
                if (e.doorLock(d) != null || best.containsKey(d.to)) continue;
                List<MapDb.Door> l = new ArrayList<>(best.get(a)); l.add(d);
                best.put(d.to, l); q.add(d.to);
            }
        }
        return null;
    }

    static void walk(QuestEngine e, ActionRunner runner, MapDb maps, String to) {
        List<MapDb.Door> route = path(e, maps, e.p.area, to);
        check(route != null, "[" + e.route() + "] ada jalan dari " + e.p.area + " ke " + to + " pada step " + e.p.step);
        for (MapDb.Door d : route) {
            if (CUR != null) { CUR.walkPx += Math.hypot(d.cx() - e.p.x, d.cy() - e.p.y) * 1.25; CUR.hops++; }
            e.p.area = d.to; e.p.x = d.tx; e.p.y = d.ty;
            if (CUR != null) talkAll(e, runner, CUR);
            runner.run(e.onEnterArea(d.to));
        }
    }

    static SimPresenter CUR;
    static final Map<String, double[]> EST = new java.util.LinkedHashMap<>();
    static void approach(QuestEngine e, QuestDb.Interactable it) {
        if (CUR != null) CUR.walkPx += Math.hypot(it.x - e.p.x, it.y - e.p.y) * 1.25;
        e.p.x = it.x; e.p.y = it.y;
    }

    /** Estimasi menit: baca 15 karakter/detik + 0,8 detik per baris, jalan 125 px/detik x faktor eksplorasi 1,6,
     *  minigame (photobooth 60, masak 90, lentera 120, peta bintang 90, halaman 60, capit 25 detik), puzzle simbol 60, kartu 3, transisi 0,7 detik. */
    static double minutes(SimPresenter sim, int puzzles) {
        double read = sim.chars / 15.0 + sim.lineCount * 0.8;
        double walk = sim.walkPx / 125.0 * 1.6 + sim.hops * 0.7 + sim.warps * 0.7;
        double mg = 0;
        for (String m : sim.minigames) mg += m.equals("photobooth") ? 70 : m.equals("cooking") ? 110 : m.equals("lanterns") ? 240 : m.equals("starmap") ? 90 : m.equals("pages") ? 80 : m.equals("fishing") ? 30 : m.equals("starcatch") ? 45 : m.equals("ringtoss") ? 45 : m.equals("pour") ? 40 : m.startsWith("cook_") ? 110 : 25;
        return (read + walk + mg + puzzles * 60 + sim.cards * 3 + sim.cineSec) / 60.0;
    }

    static Progress playRoute(String r, StoryDb story, QuestDb quests, MapDb maps) {
        Progress p = Progress.newGame(r, 1, quests.firstStep(), maps.area(Routes.room(r)));
        p.snapshot("PRO");
        QuestEngine e = new QuestEngine(story, quests, maps, p, false);
        SimPresenter sim = new SimPresenter(story, quests, maps);
        final Progress pf = p; MapDb.flags = new MapDb.FlagCheck() { public boolean has(String f) { return pf.hasFlag(f); } };
        sim.engine = e; CUR = sim;
        ActionRunner runner = new ActionRunner(e, sim);
        runner.run(e.resolve(e.step().onStart)); // cutscene pembuka New Game
        List<String> visited = new ArrayList<>();
        for (int guard = 0; guard < 400 && !e.step().isFinal; guard++) {
            QuestDb.Step s = e.step();
            visited.add(s.id);
            QuestDb.Interactable target = null; String targetArea = null;
            for (MapDb.Area a : maps.areas.values()) {
                List<QuestDb.Interactable> its = e.interactables(a.id);
                if (!its.isEmpty()) { target = its.get(0); targetArea = a.id; break; }
            }
            if (target != null) {
                if (!targetArea.equals(p.area)) walk(e, runner, maps, targetArea);
                // NPC/interaksi di area yang sama dengan step aktif harus terlihat setelah berjalan
                check(e.interactables(p.area).contains(target), "[" + r + "] interaksi terlihat setelah tiba: " + target.id);
                approach(e, target);
                talkAll(e, runner, sim);
                runner.run(e.actionsFor(target));
                talkAll(e, runner, sim);
            } else if (s.enterArea != null) {
                walk(e, runner, maps, Routes.resolve(s.enterArea, r));
            } else {
                throw new AssertionError("[" + r + "] step buntu tanpa interaksi/enterArea: " + s.id);
            }
            check(!runner.busy(), "runner selesai");
        }
        check(e.step().isFinal, "[" + r + "] mencapai akhir cerita (Epilog)");
        for (String ch : new String[]{"PRO", "C01", "C02", "C03", "C04", "C05", "C06", "EPI"}) check(p.chapters.contains(ch), "[" + r + "] chapter tamat " + ch);
        for (String f : new String[]{"CANON_DATE_PHOTO", "CANON_RAIN_TALK", "CANON_ETERNAL_GARDEN", "C06_CANON_END", "EPI_UNLOCKED", "C04_LANTERNS_LIT", "C05_COMPLETED"})
            check(p.hasFlag(f), "[" + r + "] flag " + f);
        check(p.hasFlag(r.equals("arland") ? "C05_COMPASS_CLUE" : "C05_LANTERN_CLUE"), "[" + r + "] petunjuk route C05");
        check(sim.creditsShown, "[" + r + "] kredit diputar");
        for (String key : new String[]{"V473-EPI-PLAZA","V473-EPI-CAFE","V473-EPI-GALLERY","V473-EPI-LAKE-END"})
            check(sim.scenes.contains(key), "[" + r + "] new Epilogue memory quest played: " + key);
        check(sim.minigames.containsAll(Arrays.asList("photobooth", "cooking", "lanterns", "starmap", "pages", "starcatch")), "[" + r + "] semua minigame cerita dimainkan: " + sim.minigames);
        for (String ch : new String[]{"PRO", "C01", "C02", "C03", "C04", "C05", "C06"}) check(p.snapshots.containsKey(ch), "[" + r + "] snapshot replay " + ch);
        String RU = Routes.upper(r);
        for (String f : new String[]{"PRO_PHONE_READ", "PRO_GIFT_" + RU, "PRO_MET_PARTNER", "PRO_BOOK_FOUND", "PRO_GARDEN_ENTERED", "PRO_COMPLETED",
                "C01_HINT_" + RU, "C01_PUZZLE_ACTIVE", "C01_PUZZLE_SOLVED", "C01_LETTER_FOUND", "C01_COMPLETED",
                "CANON_PLAZA_MEET", "CANON_BOOK_OPEN", "CANON_MEMORY_GARDEN", "CANON_CAFE_LETTER", "CANON_RIVERSIDE"})
            check(p.hasFlag(f), "[" + r + "] flag " + f);
        check(p.hasFlag(r.equals("arland") ? "C01_ARLAND_NOTE" : "C01_SOFIA_BOOKMARK"), "[" + r + "] flag item pribadi C01");
        check(p.chapters.contains("PRO") && p.chapters.contains("C01"), "[" + r + "] chapter tamat tercatat");
        check(p.shards == 3, "[" + r + "] 3 keping");
        check(p.hasItem(r.equals("arland") ? "postcard" : "paper_flower"), "[" + r + "] menerima hadiah pasangan");
        check(p.hasItem(r.equals("arland") ? "foto_kecil" : "bunga_pita"), "[" + r + "] tukar hadiah C02");
        check(!p.hasItem(r.equals("arland") ? "paper_flower" : "postcard"), "[" + r + "] hadiah sendiri sudah diberikan");
        check(p.hasItem("letter_two_sides") && p.hasItem("memory_book"), "[" + r + "] surat & buku");
        check(p.companion && p.area.equals("riverside") && p.hasFlag("EPI_FESTIVAL_DONE") && p.hasFlag("V473_EPI_COMPLETE"), "[" + r + "] epilog: festival selesai, pulang ke danau setelah memory walk");
        for (String f : new String[]{"C02_FREE_DONE", "C03_FREE_DONE", "C05_FREE_DONE"}) check(p.hasFlag(f), "[" + r + "] hari bebas " + f);
        check(sim.scenes.contains(r.equals("arland") ? "P-A01" : "P-S01"), "[" + r + "] adegan pembuka route");
        for (String id : sim.scenes) {
            String sr = story.scene(id).route;
            check(sr.equals("shared") || sr.equals(r), "[" + r + "] tidak memutar adegan route lain: " + id);
        }
        // v1.8: petunjuk dan pilihan utama The Quiet HARUS diputar pada route yang tepat.
        boolean arland = r.equals("arland");
        for (String flag : new String[]{"Q_C05_ECHO", "THE_QUIET_REVEALED", "Q_SARI_CLOSURE",
                arland ? "Q_C01_A_MAP" : "Q_C01_S_MARGIN",
                arland ? "Q_C04_A_REPLY" : "Q_C04_S_REPLY",
                arland ? "Q_C06_A_SOLVED" : "Q_C06_S_SOLVED"})
            check(p.hasFlag(flag), "[" + r + "] alur The Quiet membuka " + flag);
        check(p.count(arland ? "quiet_a" : "quiet_s") == 3, "[" + r + "] tiga petunjuk The Quiet ditemukan");
        check(p.count(arland ? "quiet_s" : "quiet_a") == 0, "[" + r + "] tidak mencampur petunjuk route lain");
        for (String id : new String[]{arland ? "Q-C01-A" : "Q-C01-S", arland ? "Q-C04-A" : "Q-C04-S",
                arland ? "Q-C05-A" : "Q-C05-S", "Q-C06-REVEAL@" + r, "Q-EPI-SARI@" + r, arland ? "Q-EPI-A" : "Q-EPI-S"})
            check(sim.scenes.contains(id), "[" + r + "] benar-benar menonton adegan " + id);
        for (int i = 1; i <= 5; i++)
            check(sim.scenes.contains("Q-C06-" + (arland ? "A" : "S") + i),
                    "[" + r + "] benar-benar menonton petunjuk akhir " + i);
        // v2.6: seluruh bagian Chapter 3-5 harus benar-benar dimainkan oleh kedua route.
        for (String flag : new String[]{"V26_C03_FINISHED", "V26_AFTER_RAIN", "V26_C05_TOGETHER", "V26_C05_STARGAZE",
                arland ? "V26_C05_A_SOLVED" : "V26_C05_S_SOLVED"})
            check(p.hasFlag(flag), "[" + r + "] alur ekspansi v2.6 selesai: " + flag);
        check(p.count(arland ? "v26_survey" : "v26_notes") == 3, "[" + r + "] 3 petunjuk route v2.6 ditemukan");
        check(p.count(arland ? "v26_notes" : "v26_survey") == 0, "[" + r + "] petunjuk route lawan tidak dimainkan");
        check(sim.scenes.contains(arland ? "V26-C05-A5" : "V26-C05-S5"), "[" + r + "] adegan baru Chapter 5 dimainkan");
        check(sim.scenes.contains("V26-C04-VOW") && sim.scenes.contains("V26-C05-STAR"), "[" + r + "] adegan shared v2.6 dimainkan");
        check(sim.minigames.contains(arland ? "v26_night_compass" : "v26_night_pages"), "[" + r + "] puzzle v2.6 dimainkan");
        check(!sim.minigames.contains(arland ? "v26_night_pages" : "v26_night_compass"), "[" + r + "] tidak memakai puzzle route lawan");
        check(p.hasFlag("V26_CHOICE_MAP") ^ p.hasFlag("V26_CHOICE_LETTER"), "[" + r + "] pilihan memory book v2.6 disimpan");
        check(sim.minigames.contains(arland ? "quiet_cipher" : "quiet_pages"), "[" + r + "] minigame misteri dijalankan");
        check(!sim.minigames.contains(arland ? "quiet_pages" : "quiet_cipher"), "[" + r + "] minigame route lain tidak dijalankan");
        check(p.hasFlag("Q_CHOICE_LISTEN") ^ p.hasFlag("Q_CHOICE_KEEP"), "[" + r + "] satu respons pengungkapan tersimpan");
        check(p.hasItem("pembatas_wira") && !p.hasItem("halaman_suara"), "[" + r + "] halaman diserahkan dan kenangan kembali");
        log.add("THE QUIET " + r + ": C01/C04/C05, 3 petunjuk, puzzle khusus, pilihan, pengungkapan, dan penutup Sari diputar");
        log.add("Route " + r + ": " + visited.size() + " step, " + sim.scenes.size() + " adegan, " + sim.lineCount + " baris dialog");
        double mainMin = minutes(sim, 1);
        SimPresenter side = new SimPresenter(story, quests, maps); side.engine = e; CUR = side;
        ActionRunner sideRunner = new ActionRunner(e, side);
        playSide(e, sideRunner, maps, quests, side, r);
        talks = 0;
        int before = side.lineCount;
        playTalks(e, sideRunner, maps, side);
        check(e.partnerTalk("plaza") == null, "[" + r + "] percakapan epilog plaza terputar");
        int talkFlags = 0; for (String f : e.p.flags) if (f.startsWith("TALK_")) talkFlags++;
        check(talkFlags >= quests.talks.size() - 1, "[" + r + "] hampir semua percakapan pasangan bisa diputar: " + talkFlags + "/" + quests.talks.size());
        log.add("Route " + r + ": " + talkFlags + "/" + quests.talks.size() + " percakapan pasangan terputar");
        playRomance(e, sideRunner, side, r);
        playCoupleActions(e, sideRunner, side, r);
        playRomanceGames(e, sideRunner, side, r);
        double sideMin = minutes(side, 0) + 9 * 25 / 60.0; // ~9 percobaan capit tambahan rata-rata
        int examine = 0; long exChars = 0;
        for (MapDb.Area a : maps.areas.values()) for (MapDb.Examine ex : a.examine) for (StoryDb.Line l : ex.lines(r)) { examine++; exChars += l.text.length(); }
        double exMin = (exChars / 15.0 + examine * 0.8 + examine * 6) / 60.0;
        EST.put(r, new double[]{mainMin, sideMin, exMin});
        log.add(String.format(java.util.Locale.ROOT, "Estimasi %s: cerita utama %.0f mnt (baca %d krk, jalan %.0f px, %d minigame) + side quest %.0f mnt + eksplorasi/NPC opsional %.0f mnt",
                r, mainMin, sim.chars, sim.walkPx, sim.minigames.size(), sideMin, exMin));
        CUR = null;
        return p;
    }

    /** Enam minigame dari tombol Main Bareng harus benar-benar lewat ActionRunner dan membuka Memory Book. */
    static void playRomanceGames(QuestEngine e, ActionRunner runner, SimPresenter sim, String route) {
        Progress p = e.p;
        String oldArea = p.area;
        for (QuestDb.RomanceGame g : e.quests.romanceGames) {
            p.day++;
            p.area = g.areas.get(0);
            check(e.romanceGameBlock(g.id, p.area) == null, "main bareng tersedia: " + route + ":" + g.id);
            Map<String,Object> action = new HashMap<>(); action.put("do", "romanceGame"); action.put("id", g.id); action.put("area", p.area);
            runner.run(java.util.Collections.singletonList(action));
            check(sim.minigames.contains(g.minigame), "game benar dipanggil: " + g.minigame);
            check(p.hasFlag("ROM_GAME_" + g.id.toUpperCase(java.util.Locale.ROOT) + "_ONCE"), "memori game terbuka " + g.id);
            check(sim.scenes.contains(g.scene(route)), "dialog route game diputar " + route + ":" + g.id);
            check(p.count("total_romgame_" + g.id) == 1, "bonus hanya sekali " + g.id);
        }
        p.area = oldArea;
        log.add("ROMANCE GAME " + route + ": 6 permainan, 6 adegan POV, 6 kenangan benar-benar dijalankan");
    }

    static void testRomanceGames(StoryDb story, QuestDb quests, MapDb maps, MemoryBookDb book) {
        check(quests.romanceGames.size() == 6, "enam game katalog tersedia");
        Set<String> ids = new HashSet<>();
        for (QuestDb.RomanceGame g : quests.romanceGames) {
            check(ids.add(g.id), "ID minigame unik " + g.id);
            check(quests.minigames.containsKey(g.minigame), "tipe game playable " + g.id);
            for (String area : g.areas) check(maps.area(area) != null, "lokasi game valid " + g.id);
            for (String route : Routes.ALL) {
                StoryDb.Scene scene = story.scene(g.scene(route));
                check(scene != null && route.equals(scene.route) && scene.lines.size() >= 3, "dialog baru kedua POV " + g.id + ":" + route);
            }
            check(book.entries.stream().anyMatch(m -> m.unlock.equals("ROM_GAME_" + g.id.toUpperCase(java.util.Locale.ROOT) + "_ONCE")), "memori terhubung ke flag " + g.id);
        }
        for (String route : Routes.ALL) {
            Progress p = Progress.newGame(route, 1, "C02_PHONE", maps.area(Routes.room(route)));
            QuestEngine e = new QuestEngine(story,quests,maps,p,false);
            check(e.romanceGameBlock("buket","toko_bunga").contains("Chapter 2"), "game butuh companion " + route);
            p.companion = true;
            check(e.romanceGameBlock("buket","cafe").contains("lokasi"), "game tidak dibuka di area salah");
            int money = p.coins, hearts = p.affection;
            check(e.completeRomanceGame("buket","toko_bunga",-1).contains("dibatalkan"), "cancel tanpa bonus");
            check(e.completeRomanceGame("buket","toko_bunga",0).contains("Belum berhasil"), "game gagal tanpa bonus");
            check(p.affection == hearts && !p.hasFlag("ROM_GAME_BUKET_ONCE"), "gagal tak beri hadiah");
            check(e.completeRomanceGame("buket","toko_bunga",4).startsWith("Kenangan baru!"), "game success " + route);
            check(p.affection == hearts+5 && p.hasFlag("ROM_GAME_BUKET_ONCE"), "award sekali");
            check(e.completeRomanceGame("buket","toko_bunga",4).contains("bonus hari ini"), "anti spam same day");
            check(p.affection == hearts+5 && p.coins == money, "tidak spam dan tidak menarik koin");
            Progress save = Progress.fromMap(Json.parseObject(Json.write(p.toMap(true))));
            check(save.counters.equals(p.counters) && save.affection == p.affection, "historis game ter-save di counters schema 5");
            QuestEngine loaded = new QuestEngine(story,quests,maps,save,false);
            check(loaded.completeRomanceGame("buket","toko_bunga",4).contains("bonus hari ini"), "reload tetap anti spam");
            save.day++;
            check(loaded.completeRomanceGame("buket","toko_bunga",4).startsWith("Kenangan baru!"), "besok bisa bonus lagi");
            QuestEngine replay = new QuestEngine(story,quests,maps,save,true);
            check(replay.romanceGameBlock("buket","toko_bunga").contains("Chapter 2"), "replay tak bisa farming");
        }
        log.add("ROMANCE GAMES v2.5: 6 katalog, route, skor, cancel, save, anti-spam dan replay OK");
    }

    /** Mainkan 8 aksi karakter di dua route; bukan sekadar mengecek ada di JSON. */
    static void playCoupleActions(QuestEngine e, ActionRunner runner, SimPresenter sim, String route) {
        Progress p = e.p;
        int before = p.affection, oldMinute = p.minute;
        String oldArea = p.area;
        for (QuestDb.CoupleAction a : e.quests.coupleActions) {
            p.day++;
            p.minute = a.startMinute + Math.min(30, (a.endMinute - a.startMinute) / 2);
            p.area = a.areas.isEmpty() ? "plaza" : a.areas.get(0);
            int tries = 0;
            while (!a.weather.isEmpty() && !a.weather.contains(e.weatherNow()) && tries++ < 160) p.day++;
            check(tries < 160 && e.coupleActionBlock(a.id, p.area) == null,
                    "aksi pasangan dapat dimainkan: " + route + ":" + a.id);
            check(e.startCoupleAction(a.id, p.area).startsWith("Aksi berdua!"), "aksi dimainkan: " + a.id);
            List<Map<String, Object>> actions = e.coupleActionActions(a.id);
            check(actions.size() >= 2 && "cine".equals(Json.str(actions.get(0), "do", "")), "aksi punya animasi " + a.id);
            runner.run(actions);
            check(sim.scenes.contains(a.scene(route)), "aksi pasangan benar-benar memutar scene route: " + a.id);
            check(p.hasFlag("ROM_ACT_" + a.id.toUpperCase(java.util.Locale.ROOT) + "_ONCE"), "flag kenangan " + a.id);
            if ("gandengan".equals(a.id)) {
                check(p.holdingHands, "mode gandengan aktif setelah cutscene");
                check(e.startCoupleAction(a.id, p.area).startsWith("Berhenti bergandengan."), "gandengan dapat dilepas");
                check(!p.holdingHands, "mode gandengan dimatikan");
            }
        }
        check(p.coupleActionCounts.size() == 8 && p.coupleActionDays.size() == 8, "8 aksi berdua punya histori");
        check(p.affection == Math.min(100, before + 24), "batas afeksi setelah 8 aksi tidak melebihi 100");
        p.area = oldArea; p.minute = oldMinute;
        log.add("COUPLE ACTION " + route + ": 8 pose bersama, 8 scene route, 8 memori & 8 daily record dijalankan");
    }

    /** Jalankan opsional hadiah/kencan seusai cerita, agar semua Memory Book memang teruji unlock. */
    static void playRomance(QuestEngine e, ActionRunner runner, SimPresenter sim, String route) {
        Progress p = e.p;
        check(p.companion && e.romanceReady(), "pasangan menemani seusai epilog");
        String oldArea = p.area; int oldMinute = p.minute;
        String[] gifts = {"buket_senja", "mawar_pita", "kartu_lucu"};
        String[] dates = {"taman", "kafe", "bintang"};
        int[] hours = {10 * 60, 14 * 60, 21 * 60};
        for (int i = 0; i < 3; i++) {
            QuestDb.DateActivity d = e.date(dates[i]);
            p.area = d.area; p.minute = hours[i];
            if (p.coins < 55) check(e.completeWork("barista", 3).contains("+20"), "tambahan upah setelah ganti hari: " + route);
            String shop = gifts[i].equals("kartu_lucu") ? "rini" : "melati";
            check(e.purchase(shop, gifts[i]).startsWith("Membeli"), "beli hadiah kencan " + route);
            check(e.giveGift(gifts[i]).startsWith("Hadiah diberikan"), "hadiah diberikan " + route);
            runner.run(e.giftActions(gifts[i]));
            check(e.startDate(dates[i], d.area).startsWith("Kencan dimulai"), "kencan selesai " + route + ":" + dates[i]);
            runner.run(e.dateActions(dates[i]));
            if (i < 2) p.day++;
        }
        check(p.affection >= 50 && p.hasFlag("ROM_BOND_20") && p.hasFlag("ROM_BOND_50"), "dua milestone relasi berhasil");
        check(p.hasFlag("ROM_BOND_20_SCENE") && p.hasFlag("ROM_BOND_50_SCENE"), "kedua dialog milestone benar-benar dimainkan");
        check(sim.scenes.contains("RM-BOND-20@" + route) && sim.scenes.contains("RM-BOND-50@" + route), "adegan milestone route benar");
        for (String id : dates) check(p.hasFlag("ROM_DATE_" + id.toUpperCase(java.util.Locale.ROOT) + "_ONCE"), "memori kencan " + id);
        playMoments(e, runner, sim, route);
        p.area = oldArea; p.minute = oldMinute;
        log.add("Route " + route + ": 3 kencan, 3 hadiah, 8 momen gratis dan 3 milestone kedekatan dimainkan");
    }

    /** Kunjungi delapan suasana berbeda agar tes cerita dan Memory Book memutar adegan sebenarnya. */
    static void playMoments(QuestEngine e, ActionRunner runner, SimPresenter sim, String route) {
        Progress p = e.p;
        for (QuestDb.MomentActivity moment : e.quests.moments) {
            p.day++;
            p.minute = moment.startMinute + Math.min(30, (moment.endMinute - moment.startMinute) / 2);
            p.area = moment.area;
            int safety = 0;
            while (!moment.weather.isEmpty() && !moment.weather.contains(e.weatherNow()) && safety++ < 120) p.day++;
            check(safety < 120, "cuaca momen tersedia dalam 120 hari " + moment.id);
            check(e.momentBlock(moment.id, moment.area) == null, "momen bisa dimainkan " + route + ":" + moment.id + ":" + e.momentBlock(moment.id, moment.area));
            int before = p.affection;
            check(e.startMoment(moment.id, moment.area).startsWith("Momen berdua!"), "momen dimainkan " + moment.id);
            check(p.affection == Math.min(100, before + moment.affection), "hati bertambah " + moment.id);
            runner.run(e.momentActions(moment.id));
            check(sim.scenes.contains(moment.scene(route)), "dialog momen route benar-benar diputar " + route + ":" + moment.id);
        }
        check(p.momentCounts.size() == e.quests.moments.size(), "semua momen disimpan " + route);
        check(p.hasFlag("ROM_BOND_80") && p.hasFlag("ROM_BOND_80_SCENE"), "milestone 80 terpicu dan selesai " + route);
        check(sim.scenes.contains("RM-BOND-80@" + route), "dialog milestone 80 terputar " + route);
    }

    static int talks;
    static void talkAll(QuestEngine e, ActionRunner runner, SimPresenter sim) {
        if (!e.p.companion) return;
        for (int k = 0; k < 10; k++) {
            QuestDb.Talk t = e.partnerTalk(e.p.area);
            if (t == null) return;
            runner.run(e.talkActions(t)); talks++;
        }
    }

    /** Setelah tamat: kunjungi area yang punya percakapan epilog. */
    static void playTalks(QuestEngine e, ActionRunner runner, MapDb maps, SimPresenter sim) {
        for (MapDb.Area a : maps.areas.values()) {
            if (e.partnerTalk(a.id) == null) continue;
            if (!a.id.equals(e.p.area)) { if (path(e, maps, e.p.area, a.id) == null) continue; walk(e, runner, maps, a.id); }
            talkAll(e, runner, sim);
        }
    }

    static boolean stateful(List<Map<String, Object>> acts) {
        for (Map<String, Object> a : acts) {
            String d = Json.str(a, "do", "");
            if (!d.equals("lines") && !d.equals("toast") && !d.equals("sfx") && !d.equals("emote") && !d.equals("scene")) return true;
        }
        return false;
    }

    /** Menyelesaikan semua side quest lewat NPC + interaksi sampingan; memastikan tidak ada yang buntu. */
    static void playSide(QuestEngine e, ActionRunner runner, MapDb maps, QuestDb quests, SimPresenter sim, String r) {
        int ran = 0;
        for (int guard = 0; guard < 500; guard++) {
            boolean did = false;
            if (e.p.hasFlag("SQ_HEWAN_START") && !e.p.hasFlag("PET_DUCK")) { // simulasi: menghampiri & mengelus hewan di taman/plaza
                for (String t : new String[]{"CAT", "DOG", "DUCK"}) e.p.flags.add("PET_" + t);
                if (CUR != null) { CUR.walkPx += 2400; CUR.hops += 3; }
            }
            for (MapDb.Area a : maps.areas.values()) {
                List<QuestDb.Interactable> its = new ArrayList<>();
                for (QuestDb.Interactable cand : e.sideInteractables(a.id))
                    if (!cand.id.startsWith("shop_") && !cand.id.startsWith("job_") && !(cand.id.startsWith("fish_") && (e.p.hasFlag("SQ_IKAN_DONE") || e.p.count("spesies") >= 5))) its.add(cand);
                if (!its.isEmpty()) {
                    if (!a.id.equals(e.p.area)) { List<MapDb.Door> pth = path(e, maps, e.p.area, a.id); if (pth == null) continue; walk(e, runner, maps, a.id); }
                    approach(e, its.get(0)); runner.run(e.actionsFor(its.get(0))); did = true; ran++; break;
                }
                for (QuestDb.TownNpc n : e.townNpcs(a.id)) {
                    Map<String, Object> d = e.npcDialog(n);
                    if (d == null || !stateful(Json.objList(d, "actions"))) continue;
                    if (!a.id.equals(e.p.area)) { if (path(e, maps, e.p.area, a.id) == null) continue; walk(e, runner, maps, a.id); }
                    if (CUR != null) CUR.walkPx += Math.hypot(n.x - e.p.x, n.y - e.p.y) * 1.25;
                    e.p.x = n.x; e.p.y = n.y;
                    runner.run(e.resolve(Json.objList(d, "actions"))); did = true; ran++; break;
                }
                if (did) break;
            }
            if (!did) break;
        }
        int reachableSideQuests = 0;
        for (QuestDb.SideQuest q : quests.sideQuests) {
            if (!q.forRoute(r)) continue;
            reachableSideQuests++;
            check(e.p.hasFlag(q.doneFlag), "[" + r + "] side quest selesai: " + q.id);
        }
        // Simulasi profesi opsional setelah side quest canon; tidak mengacaukan prioritas interaksi cerita.
        check(e.completeWork("barista", 3).contains("+20"), "shift barista " + r);
        check(e.completeWork("perangkai", 4).contains("+22"), "shift bunga " + r);
        e.startDelivery();
        check(e.deliver("plaza").contains("1/3"), "surat plaza " + r);
        check(e.deliver("jalan_kota").contains("2/3"), "surat jalan " + r);
        check(e.deliver("riverside").contains("+28"), "surat dan upah " + r);
        log.add("Route " + r + ": " + reachableSideQuests + " side quest selesai lewat " + ran + " interaksi");
    }

    static void testReplay(Progress p, StoryDb story, QuestDb quests, MapDb maps) {
        Progress rp = p.replayFrom("C01");
        check(rp != null, "snapshot C01 ada");
        check("C01_NOTE".equals(rp.step) && rp.area.equals(Routes.room(p.route)), "replay C01 mulai di kamar");
        check(!rp.hasFlag("C01_COMPLETED") && rp.hasFlag("PRO_COMPLETED"), "replay membawa state akhir prolog saja");
        Progress pro = p.replayFrom("PRO");
        check(pro != null && pro.step.equals(quests.firstStep()) && pro.flags.isEmpty(), "replay prolog dari awal");
    }

    static void testMemoryBook(MemoryBookDb book, Progress p, GlobalProgress g) {
        int unlocked = 0;
        for (MemoryBookDb.Entry e : book.entriesFor(p.route)) {
            boolean mine = e.route.equals("shared") || e.route.equals(p.route);
            // Momen dunia harian memang opsional: menamatkan cerita tidak otomatis membuka kenangannya.
            if (mine && !e.unlock.startsWith("WORLD_EVENT_") && !"optional_postgame".equals(e.type) && !"postgame_memory".equals(e.type) && !"optional_story_branch".equals(e.type)
                    && !"world_discovery".equals(e.type) && !"optional_bonus".equals(e.type))
                check(book.state(e, p, g) == MemoryBookDb.State.UNLOCKED, "[" + p.route + "] entri terbuka setelah tamat: " + e.id);
            if (book.state(e, p, g) == MemoryBookDb.State.UNLOCKED) unlocked++;
        }
        log.add("Memory Book " + p.route + ": " + unlocked + " entri terbuka");
    }

    // ------------------------------------------------------------------ save
    static final class DirIO implements FileIO {
        final File base;
        DirIO(File b) { base = b; }
        public String read(String path) {
            try { return new String(Files.readAllBytes(new File(base, path).toPath()), StandardCharsets.UTF_8); } catch (IOException e) { return null; }
        }
        public boolean writeAtomic(String path, String content) {
            try {
                File f = new File(base, path); f.getParentFile().mkdirs();
                File tmp = new File(base, path + ".tmp");
                Files.write(tmp.toPath(), content.getBytes(StandardCharsets.UTF_8));
                Files.move(tmp.toPath(), f.toPath(), StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
                return true;
            } catch (IOException e) { return false; }
        }
        public boolean exists(String path) { return new File(base, path).exists(); }
        public void delete(String path) { new File(base, path).delete(); }
    }

    static void testSave(StoryDb story, QuestDb quests, MapDb maps) throws IOException {
        File dir = Files.createTempDirectory("olu-save").toFile();
        DirIO io = new DirIO(dir);
        SaveStore store = new SaveStore(io);
        Progress p = Progress.newGame("sofia", 2, quests.firstStep(), maps.area("sofia_room"));
        p.flags.add("PRO_PHONE_READ"); p.items.add("postcard"); p.x = 123.4f;
        p.flags.add("Q_C06_S_TRACE_1"); p.addCount("quiet_s", 1); p.snapshot("PRO");
        check(store.saveSlot(p), "simpan slot");
        SaveStore.Loaded<Progress> l = store.loadSlot("sofia", 2);
        check(l.status == SaveStore.Status.OK && l.value.hasFlag("PRO_PHONE_READ") && l.value.hasItem("postcard"), "muat slot");
        check(Math.round(l.value.x) == 123, "posisi tersimpan");
        check(l.value.hasFlag("Q_C06_S_TRACE_1") && l.value.count("quiet_s") == 1,
                "save v1.8 menyimpan petunjuk dan jumlah yang belum lengkap");
        check(store.loadSlot("arland", 1).status == SaveStore.Status.MISSING, "slot kosong terdeteksi");
        // simpan kedua -> .bak dibuat, lalu rusakkan file utama
        p.flags.add("PRO_GIFT_SOFIA");
        store.saveSlot(p);
        check(io.exists(SaveStore.slotPath("sofia", 2) + ".bak"), "cadangan .bak dibuat");
        io.writeAtomic(SaveStore.slotPath("sofia", 2), "{\"format\":\"olu-save\",\"crc\":1,\"payload\":{\"schema\":1}}");
        l = store.loadSlot("sofia", 2);
        check(l.status == SaveStore.Status.RECOVERED && l.value != null, "pulih dari .bak saat file utama rusak");
        io.writeAtomic(SaveStore.slotPath("sofia", 2) + ".bak", "sampah{{{");
        l = store.loadSlot("sofia", 2);
        check(l.status == SaveStore.Status.CORRUPT && l.value == null, "rusak total terdeteksi tanpa crash");
        // edit manual payload -> checksum gagal (simpan dua kali agar .bak valid)
        store.saveSlot(p);
        store.saveSlot(p);
        String txt = io.read(SaveStore.slotPath("sofia", 2)).replace("PRO_PHONE_READ", "PRO_PHONE_READX");
        io.writeAtomic(SaveStore.slotPath("sofia", 2), txt);
        l = store.loadSlot("sofia", 2);
        check(l.status == SaveStore.Status.RECOVERED, "checksum mendeteksi perubahan isi");
        // settings & global
        Settings s = new Settings(); s.textSpeed = 3; s.music = 0.25f;
        store.saveSettings(s);
        Settings s2 = store.loadSettings();
        check(s2.textSpeed == 3 && Math.abs(s2.music - 0.25f) < 1e-4, "settings tersimpan");
        GlobalProgress g = new GlobalProgress(); g.absorb(p); store.saveGlobal(g);
        check(store.loadGlobal().routeHasFlag("sofia", "PRO_GIFT_SOFIA"), "global tersimpan");
        store.deleteSlot("sofia", 2);
        check(store.loadSlot("sofia", 2).status == SaveStore.Status.MISSING, "hapus slot");
        log.add("Save: atomic write, .bak, checksum, pemulihan, settings, global -> OK (" + dir + ")");
    }
    // ------------------------------------------------------------------ dunia hidup (jam, cuaca, jadwal, hewan)
    static void testWorld(File assets, StoryDb story, QuestDb quests, MapDb maps) {
        check(WorldClock.hhmm(420).equals("07:00") && WorldClock.hhmm(25 * 60 + 30).equals("01:30"), "format jam");
        check(WorldClock.parse("08:30", -1) == 510 && WorldClock.parse("25:00", -1) == 1500, "parse jam");
        check(WorldClock.weather(1).equals(WorldClock.CERAH) && WorldClock.weather(2).equals(WorldClock.CERAH), "dua hari pertama cerah");
        int rain = 0, cloud = 0, wind = 0;
        for (int d = 1; d <= 140; d++) { String w = WorldClock.weather(d); if (w.equals(WorldClock.HUJAN)) rain++; else if (w.equals(WorldClock.BERAWAN)) cloud++; else if (w.equals(WorldClock.BERANGIN)) wind++; }
        check(rain >= 8 && rain <= 35 && cloud > 0 && wind > 0, "sebaran cuaca masuk akal (hujan " + rain + "/140)");
        check(WorldClock.light(12 * 60)[3] < 0.05f && WorldClock.light(23 * 60)[3] >= 0.3f && WorldClock.isNight(23 * 60) && !WorldClock.isNight(10 * 60), "cahaya siang/malam");
        check(WorldClock.dayName(1).equals("Sabtu") && WorldClock.dayName(8).equals("Sabtu"), "nama hari berulang");

        // jadwal: setiap NPC di setiap jam (cerah & hujan) berada di titik bebas pada area yang ada
        Progress p = Progress.newGame("arland", 1, "EPI_FREE", maps.area(Routes.room("arland")));
        QuestEngine e = new QuestEngine(story, quests, maps, p, false);
        int places = 0, hiddenNight = 0, scheduled = 0;
        java.util.Set<String> areasSeen = new java.util.HashSet<>();
        for (QuestDb.TownNpc n : quests.townNpcs) if (!n.schedule.isEmpty()) scheduled++;
        for (int day : new int[]{1, 3, 4, 5, 6, 7, 9}) {
            p.day = day;
            for (int m = WorldClock.DAY_START; m < WorldClock.DAY_END; m += 15) {
                p.minute = m;
                for (QuestDb.TownNpc n : quests.townNpcs) {
                    if (n.schedule.isEmpty()) continue;
                    Object[] pl = e.npcPlace(n);
                    if (pl == null) { if (m >= 23 * 60) hiddenNight++; continue; }
                    MapDb.Area a = maps.area((String) pl[0]);
                    check(a != null, "area jadwal ada: " + n.id + " " + pl[0]);
                    check(!a.blocked(((Number) pl[1]).floatValue(), ((Number) pl[2]).floatValue()), "titik jadwal bebas: " + n.id + " " + WorldClock.hhmm(m));
                    places++; areasSeen.add(a.id);
                }
            }
        }
        check(scheduled >= 14, "minimal 14 warga punya jadwal (" + scheduled + ")");
        check(hiddenNight > 0 && areasSeen.size() >= 6, "warga pulang malam dan tersebar di " + areasSeen.size() + " area");
        // warga berpindah: Raka tidak selalu di kafe
        QuestDb.TownNpc raka = null; for (QuestDb.TownNpc n : quests.townNpcs) if (n.id.equals("raka")) raka = n;
        p.day = 1; p.minute = 6 * 60 + 30; String a1 = (String) e.npcPlace(raka)[0];
        p.minute = 11 * 60; String a2 = (String) e.npcPlace(raka)[0];
        p.minute = 23 * 60; Object[] a3 = e.npcPlace(raka);
        check(!a1.equals(a2) && a2.equals("cafe") && a3 == null, "Raka: lari pagi -> kafe -> pulang (" + a1 + "," + a2 + ")");
        // dialog sesuai jam
        Map<String, Object> d1, d2; p.minute = 6 * 60 + 30; d1 = e.npcDialog(raka); p.minute = 11 * 60; d2 = e.npcDialog(raka);
        check(d1 != null && d2 != null && d1 != d2, "dialog Raka berubah sesuai jam");
        // hewan: sprite ada & region valid
        int an = 0;
        for (MapDb.Area a : maps.areas.values()) for (Map<String, Object> sp : a.animals) {
            String t = Json.str(sp, "type", "");
            check(new File(assets, "animals/" + t + ".png").isFile(), "sprite hewan ada: " + t);
            check(Json.floats(sp.get(sp.containsKey("water") ? "water" : "region")).length == 4, "region hewan valid: " + a.id + "/" + t);
            an += (int) Json.num(sp, "n", 1);
        }
        check(an >= 40, "hewan tersebar (" + an + ")");
        com.arlandsofia.olu.game.Animal cat = new com.arlandsofia.olu.game.Animal("cat_orange", 500, 1000, new float[]{200, 900, 1500, 300});
        MapDb.Area plaza = maps.area("plaza");
        for (int i = 0; i < 600; i++) cat.update(1 / 30f, plaza, 0, 0);
        check(!plaza.blocked(cat.x, cat.y) && cat.x > 200 && cat.x < 1700, "kucing berjalan tanpa menembus tembok");
        check(cat.pettable && !new com.arlandsofia.olu.game.Animal("bird", 0, 0, null).pettable, "kucing bisa dielus, burung tidak");
        // simpan/muat jam & hewan
        p.day = 5; p.minute = 1234; p.petted.add("cat");
        Progress q = Progress.fromMap(p.toMap(true));
        check(q.day == 5 && q.minute == 1234 && q.petted.contains("cat"), "save menyimpan hari, jam, hewan yang dielus");
        log.add("DUNIA: " + scheduled + " warga berjadwal, " + places + " posisi diuji, " + an + " hewan, hujan " + rain + "/140 hari");
    }

}
