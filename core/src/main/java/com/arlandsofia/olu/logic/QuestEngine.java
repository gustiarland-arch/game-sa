package com.arlandsofia.olu.logic;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Mesin quest murni (tanpa LibGDX): step aktif, side quest, NPC kota, kondisi, penerapan aksi state.
 */
public final class QuestEngine {
    public final StoryDb story;
    public final QuestDb quests;
    public final MapDb maps;
    public final Progress p;
    public final boolean replay;

    public QuestEngine(StoryDb story, QuestDb quests, MapDb maps, Progress p, boolean replay) {
        this.story = story; this.quests = quests; this.maps = maps; this.p = p; this.replay = replay;
        if (quests.step(p.step) == null) throw new IllegalArgumentException("Step tidak dikenal: " + p.step);
    }

    public String route() { return p.route; }
    public QuestDb.Step step() { return quests.step(p.step); }
    public String chapter() { QuestDb.Step s = step(); return s == null ? "" : s.chapter; }

    // V473_BOTH_ROUTES_GATE: global progress is shared by both save routes, never faked by local flags.
    private GlobalProgress globalProgress;
    public void setGlobalProgress(GlobalProgress progress) { this.globalProgress = progress; }

    // ------------------------------------------------------------ kondisi
    /**
     * Kondisi data: flags (semua ada), notFlags (tidak ada), anyFlags (minimal satu), steps / notSteps,
     * chapters, minChapter, maxChapter, doneChapters, route, items, notItems, count {id: min}, countBelow {id: max}.
     * Map kosong = selalu benar.
     */
    public boolean check(Map<String, Object> c) {
        if (c == null || c.isEmpty()) return true;
        if (c.containsKey("bothRoutesCompleted") && Json.bool(c, "bothRoutesCompleted", false)
                != (globalProgress != null && globalProgress.bothCompleted("C06"))) return false;
        String eventRequired = Json.str(c, "worldEventReady", null);
        if (eventRequired != null && worldEventBlock(eventRequired, p.area) != null) return false;
        if (Json.num(c, "coinsAtLeast", 0) > p.coins) return false;
        if (c.containsKey("coinsBelow") && p.coins >= Json.num(c, "coinsBelow", 0)) return false;
        String ready = Json.str(c, "jobReady", null);
        if (ready != null && !jobReady(ready)) return false;
        if (Json.bool(c, "deliveryOpen", false) && !deliveryOpen()) return false;
        String address = Json.str(c, "deliveryNotDone", null);
        if (address != null && p.deliveryDays.getOrDefault(address, -1) == p.day) return false;
        List<Object> hrs = Json.list(c, "hours");   // ["17:00", "22:00"]: jam dunia di antara keduanya
        if (hrs.size() >= 2) { int a0 = WorldClock.parse(hrs.get(0), 0), a1 = WorldClock.parse(hrs.get(1), 24 * 60); if (p.minute < a0 || p.minute >= a1) return false; }
        List<String> wx = Json.strList(c, "weatherIs");
        if (!wx.isEmpty() && !wx.contains(weatherNow())) return false;
        for (String f : Json.strList(c, "flags")) if (!p.hasFlag(Routes.resolve(f, p.route))) return false;
        for (String f : Json.strList(c, "notFlags")) if (p.hasFlag(Routes.resolve(f, p.route))) return false;
        List<String> any = Json.strList(c, "anyFlags");
        if (!any.isEmpty()) {
            boolean ok = false;
            for (String f : any) if (p.hasFlag(Routes.resolve(f, p.route))) { ok = true; break; }
            if (!ok) return false;
        }
        List<String> st = Json.strList(c, "steps");
        if (!st.isEmpty() && !st.contains(p.step)) return false;
        if (Json.strList(c, "notSteps").contains(p.step)) return false;
        List<String> chs = Json.strList(c, "chapters");
        if (!chs.isEmpty() && !chs.contains(chapter())) return false;
        String min = Json.str(c, "minChapter", null);
        if (min != null && quests.chapterIndex(chapter()) < quests.chapterIndex(min)) return false;
        String max = Json.str(c, "maxChapter", null);
        if (max != null && quests.chapterIndex(chapter()) > quests.chapterIndex(max)) return false;
        for (String ch : Json.strList(c, "doneChapters")) if (!p.chapters.contains(ch)) return false;
        String r = Json.str(c, "route", null);
        if (r != null && !r.equals(p.route)) return false;
        for (String i : Json.strList(c, "items")) if (!p.hasItem(i)) return false;
        for (String i : Json.strList(c, "notItems")) if (p.hasItem(i)) return false;
        for (Map.Entry<String, Object> e : Json.obj(c, "count").entrySet())
            if (e.getValue() instanceof Number && p.count(e.getKey()) < ((Number) e.getValue()).intValue()) return false;
        for (Map.Entry<String, Object> e : Json.obj(c, "countBelow").entrySet())
            if (e.getValue() instanceof Number && p.count(e.getKey()) >= ((Number) e.getValue()).intValue()) return false;
        return true;
    }

    // ------------------------------------------------------------ Living World v2.7 (tanpa LibGDX)
    public QuestDb.WorldEvent worldEvent(String id) {
        for (QuestDb.WorldEvent event : quests.worldEvents) if (event.id.equals(id)) return event;
        return null;
    }

    /** Katalog event menghormati route, waktu, cuaca, pendamping, chapter, dan jatah harian. */
    public String worldEventBlock(String id, String area) {
        QuestDb.WorldEvent e = worldEvent(id);
        if (e == null) return "Event tidak ditemukan.";
        if (replay) return "Event dunia tidak tersedia saat replay.";
        if (!e.area.equals(area)) return "Datang ke lokasi event.";
        if (e.route != null && !e.route.equals(p.route)) return "Event untuk route lain.";
        int current = quests.chapterIndex(chapter()), required = quests.chapterIndex(e.minChapter);
        if (current < 0 || required < 0 || current < required) return "Event akan tersedia di chapter berikutnya.";
        if (e.companion && !p.companion) return "Ajak pasangan berjalan bersamamu dahulu.";
        if (p.minute < e.startMinute || p.minute >= e.endMinute) return "Belum masuk waktu event.";
        if (!e.weather.isEmpty() && !e.weather.contains(weatherNow())) return "Tunggu cuaca yang cocok.";
        if (p.worldEventDays.getOrDefault(id, -1) == p.day) return "Event ini sudah dilakukan hari ini.";
        if (e.affection < 0 || e.affection > 8 || e.coins < 0 || e.coins > 12 || e.scene(p.route) == null)
            return "Data event tidak valid.";
        if (p.coins > 1000000 - e.coins) return "Dompet sudah mencapai batas.";
        return null;
    }

    /** Aksi selesai hanya setelah dialog event dibaca; mencegah farming hadiah dengan ketukan berulang. */
    public String completeWorldEvent(String id, String area) {
        String blocked = worldEventBlock(id, area);
        if (blocked != null) return blocked;
        QuestDb.WorldEvent e = worldEvent(id);
        p.worldEventDays.put(id, p.day);
        p.worldEventCounts.put(id, Math.min(100000, p.worldEventCounts.getOrDefault(id, 0) + 1));
        p.flags.add("WORLD_EVENT_" + id.toUpperCase(java.util.Locale.ROOT) + "_ONCE");
        p.coins += e.coins;
        addAffection(e.affection);
        return "Momen dunia tersimpan! +" + e.affection + " hati" + (e.coins > 0 ? ", +" + e.coins + " koin." : ".");
    }

    // ------------------------------------------------------------ ekonomi (tanpa API grafis)
    public boolean jobReady(String job) { return p.jobDays.getOrDefault(job, -1) != p.day; }

    /** Pembelian atomik: cek toko, stok satu per item, dan saldo sebelum memotong koin. */
    public String purchase(String shopId, String itemId) {
        QuestDb.Shop shop = quests.shops.get(shopId);
        if (shop == null) return "Toko tidak ditemukan.";
        for (QuestDb.Good good : shop.goods) if (good.item.equals(itemId)) {
            if (good.price <= 0) return "Harga barang tidak valid.";
            if (p.hasItem(itemId)) return "Barang ini sudah ada di tas.";
            if (p.coins < good.price) return "Koin belum cukup. Butuh " + good.price + " koin.";
            p.coins -= good.price;
            p.items.add(itemId);
            return "Membeli " + good.name + " (-" + good.price + " koin).";
        }
        return "Barang tidak dijual di toko ini.";
    }

    /** Upah minigame: hanya setelah skor mencapai batas, maksimal satu kali per hari per job. */
    public String completeWork(String id, int score) {
        QuestDb.Job job = quests.jobs.get(id);
        if (job == null || job.minigame.isEmpty() || !jobReady(id) || score < 0) return "Shift tidak tersedia.";
        if (score < job.minScore) return "Belum memenuhi target. Coba shift ini lagi.";
        if (job.reward <= 0 || p.coins > 1000000 - job.reward) return "Upah tidak bisa diproses.";
        p.coins += job.reward; p.jobDays.put(id, p.day);
        p.flags.add("JOB_" + id.toUpperCase(java.util.Locale.ROOT) + "_ONCE");
        return "Shift selesai! +" + job.reward + " koin.";
    }

    public int deliveredToday() {
        QuestDb.Job job = quests.jobs.get("kurir");
        if (job == null) return 0;
        int count = 0;
        for (String place : job.stops) if (p.deliveryDays.getOrDefault(place, -1) == p.day) count++;
        return count;
    }

    public boolean deliveryOpen() {
        return p.deliveryStartDay == p.day && jobReady("kurir") && quests.jobs.containsKey("kurir");
    }

    public String startDelivery() {
        if (!jobReady("kurir")) return "Surat hari ini sudah diantar. Kembali besok.";
        if (deliveryOpen()) return "Antar 3 surat ke Plaza, Jalan Kota, dan Tepi Danau.";
        p.deliveryStartDay = p.day;
        return "Ambil 3 surat. Kunjungi Plaza, Jalan Kota, dan Tepi Danau!";
    }

    /** Setiap alamat sekali per hari; upah diberikan tepat setelah alamat ketiga. */
    public String deliver(String address) {
        if (!deliveryOpen()) return "Ambil surat baru dari Pak Pos terlebih dahulu.";
        QuestDb.Job job = quests.jobs.get("kurir");
        if (job == null || !job.stops.contains(address)) return "Alamat tidak dikenal.";
        if (p.deliveryDays.getOrDefault(address, -1) == p.day) return "Surat alamat ini sudah diantar.";
        p.deliveryDays.put(address, p.day);
        int count = 0;
        for (String place : job.stops) if (p.deliveryDays.getOrDefault(place, -1) == p.day) count++;
        if (count < job.stops.size()) return "Surat terkirim (" + count + "/" + job.stops.size() + ").";
        if (job.reward > 0 && p.coins <= 1000000 - job.reward) {
            p.coins += job.reward; p.jobDays.put("kurir", p.day); p.deliveryStartDay = -1;
            p.flags.add("JOB_KURIR_ONCE");
            return "Semua surat sampai! +" + job.reward + " koin.";
        }
        return "Surat terkirim, tetapi upah belum bisa diproses.";
    }

    // ------------------------------------------------------------ romansa (state murni + katalog data-driven)
    public boolean romanceReady() {
        return !replay && p.companion && quests.chapterIndex(chapter()) >= quests.chapterIndex("C02")
                && quests.chapterIndex(chapter()) >= 0;
    }

    public QuestDb.Gift gift(String itemId) {
        for (QuestDb.Gift g : quests.gifts) if (g.item.equals(itemId)) return g;
        return null;
    }

    public QuestDb.DateActivity date(String id) {
        for (QuestDb.DateActivity d : quests.dates) if (d.id.equals(id)) return d;
        return null;
    }

    private void addAffection(int n) {
        p.affection = Math.max(0, Math.min(100, p.affection + Math.max(0, n)));
        if (p.affection >= 20) p.flags.add("ROM_BOND_20");
        if (p.affection >= 50) p.flags.add("ROM_BOND_50");
        if (p.affection >= 80) p.flags.add("ROM_BOND_80");
    }

    /** Tidak menarik saldo saat hadiah gagal; barang hanya dikonsumsi setelah semua validasi. */
    public String giveGift(String itemId) {
        QuestDb.Gift gift = gift(itemId);
        if (!romanceReady()) return "Ajak pasangan menemanimu setelah Chapter 2.";
        if (gift == null || gift.affection <= 0) return "Barang ini tidak bisa dijadikan hadiah.";
        if (p.lastGiftDay == p.day) return "Kamu sudah memberi hadiah hari ini. Coba besok.";
        if (!p.hasItem(itemId)) return "Belum punya barang tersebut. Beli di toko dulu.";
        p.items.remove(itemId);
        p.lastGiftDay = p.day;
        addAffection(gift.affection);
        p.flags.add("ROM_GIFT_ONCE");
        return "Hadiah diberikan! +" + gift.affection + " kedekatan.";
    }

    /** Beri alasan yang sama ke UI dan validasi server-logika; tidak ada koin yang dipotong saat gagal. */
    public String dateBlock(String dateId, String area) {
        QuestDb.DateActivity d = date(dateId);
        if (d == null) return "Kencan tidak tersedia.";
        if (!romanceReady()) return "Ajak pasangan menemanimu setelah Chapter 2.";
        if (!d.area.equals(area)) return "Datang dahulu ke " + d.area.replace('_', ' ') + ".";
        if (p.minute < d.startMinute || p.minute >= d.endMinute) return "Belum masuk jam kencan.";
        if (p.lastDateDay == p.day) return "Hari ini sudah berkencan. Kembali besok.";
        if (d.cost < 0 || d.affection <= 0) return "Data kencan tidak valid.";
        if (p.coins < d.cost) return "Koin tidak cukup. Butuh " + d.cost + " koin.";
        return null;
    }

    public String startDate(String dateId, String area) {
        String blocked = dateBlock(dateId, area);
        if (blocked != null) return blocked;
        QuestDb.DateActivity d = date(dateId);
        p.coins -= d.cost;
        p.lastDateDay = p.day;
        p.dateCounts.put(d.id, Math.min(100000, p.dateCounts.getOrDefault(d.id, 0) + 1));
        addAffection(d.affection);
        p.flags.add("ROM_DATE_" + d.id.toUpperCase(java.util.Locale.ROOT) + "_ONCE");
        return "Kencan dimulai! -" + d.cost + " koin, +" + d.affection + " kedekatan.";
    }

    public QuestDb.MomentActivity moment(String id) {
        for (QuestDb.MomentActivity m : quests.moments) if (m.id.equals(id)) return m;
        return null;
    }

    /** Alasan ditampilkan langsung di menu; semua kondisi dicek ulang saat dipilih. */
    public String momentBlock(String id, String area) {
        QuestDb.MomentActivity m = moment(id);
        if (m == null) return "Momen tidak ditemukan.";
        if (!romanceReady()) return "Ajak pasangan menemanimu setelah Chapter 2.";
        if (!m.area.equals(area)) return "Temui pasangan di " + m.area.replace('_', ' ') + ".";
        if (p.lastMomentDay == p.day) return "Sudah punya momen berdua hari ini. Coba besok.";
        if (p.affection < m.minAffection) return "Butuh kedekatan " + m.minAffection + " hati.";
        if (p.minute < m.startMinute || p.minute >= m.endMinute) return "Momen ini hanya tersedia pada jam tertentu.";
        if (!m.weather.isEmpty() && !m.weather.contains(weatherNow())) return "Tunggu cuaca yang cocok.";
        if (m.affection <= 0 || m.affection > 20 || m.scene(p.route) == null) return "Data momen tidak valid.";
        return null;
    }

    /** Gratis, satu momen per hari. Save dan scene dipicu hanya setelah validasi berhasil. */
    public String startMoment(String id, String area) {
        String blocked = momentBlock(id, area);
        if (blocked != null) return blocked;
        QuestDb.MomentActivity m = moment(id);
        p.lastMomentDay = p.day;
        p.momentCounts.put(id, Math.min(100000, p.momentCounts.getOrDefault(id, 0) + 1));
        p.flags.add("ROM_MOM_" + id.toUpperCase(java.util.Locale.ROOT) + "_ONCE");
        addAffection(m.affection);
        return "Momen berdua! +" + m.affection + " kedekatan.";
    }

    public List<Map<String, Object>> momentActions(String id) {
        QuestDb.MomentActivity m = moment(id);
        return m == null || m.scene(p.route) == null ? Collections.<Map<String, Object>>emptyList()
                : romanceSceneActions(m.scene(p.route), true);
    }

    public QuestDb.RomanceGame romanceGame(String id) {
        for (QuestDb.RomanceGame g : quests.romanceGames) if (g.id.equals(id)) return g;
        return null;
    }
    public String romanceGameBlock(String id, String area) {
        QuestDb.RomanceGame g = romanceGame(id);
        if (g == null || g.affection <= 0 || g.affection > 10 || !quests.minigames.containsKey(g.minigame))
            return "Permainan tidak tersedia.";
        if (!romanceReady()) return "Bermain berdua tersedia setelah Chapter 2 bersama pasangan.";
        if (!g.areas.contains(area)) return "Kunjungi lokasi kegiatan ini dahulu.";
        return null;
    }
    /** Dipanggil SETELAH minigame selesai, bukan saat tombol ditekan. Dibatasi per game/hari. */
    public String completeRomanceGame(String id, String area, int score) {
        String blocked = romanceGameBlock(id, area);
        if (blocked != null) return blocked;
        if (score < 0) return "Permainan dibatalkan, tidak ada bonus.";
        QuestDb.RomanceGame g = romanceGame(id);
        p.addCount("last_romgame_" + id, score - p.count("last_romgame_" + id));
        if (score > p.count("best_romgame_" + id)) p.addCount("best_romgame_" + id, score - p.count("best_romgame_" + id));
        if (score < g.minScore) return "Belum berhasil. Coba lagi untuk mencatat kenangan.";
        if (p.count("day_romgame_" + id) == p.day) return "Main ulang selesai! Rekor tetap tersimpan, bonus hari ini sudah diambil.";
        p.addCount("day_romgame_" + id, p.day - p.count("day_romgame_" + id));
        p.addCount("total_romgame_" + id, 1);
        p.flags.add("ROM_GAME_" + id.toUpperCase(java.util.Locale.ROOT) + "_ONCE");
        addAffection(g.affection);
        return "Kenangan baru! +" + g.affection + " kedekatan.";
    }

    public QuestDb.CoupleAction coupleAction(String id) {
        for (QuestDb.CoupleAction a : quests.coupleActions) if (a.id.equals(id)) return a;
        return null;
    }

    /** Validasi UI dan transaksi menggunakan aturan identik: jam, lokasi, cuaca, hati dan daily lock. */
    public String coupleActionBlock(String id, String area) {
        QuestDb.CoupleAction a = coupleAction(id);
        if (a == null) return "Aksi berdua tidak dikenal.";
        if (!romanceReady()) return "Ajak pasangan menemanimu setelah Chapter 2.";
        if ("gandengan".equals(id) && p.holdingHands) return null; // boleh dilepas kapan pun
        if (!a.areas.isEmpty() && !a.areas.contains(area)) return "Kunjungi lokasi yang cocok untuk aksi ini.";
        if (p.affection < a.minAffection) return "Butuh kedekatan " + a.minAffection + " hati.";
        if (p.minute < a.startMinute || p.minute >= a.endMinute) return "Belum masuk jam aktivitas.";
        if (!a.weather.isEmpty() && !a.weather.contains(weatherNow())) return "Tunggu cuaca yang cocok.";
        if (!"gandengan".equals(id) && p.coupleActionDays.getOrDefault(id, -1) == p.day)
            return "Bonus aksi ini sudah diambil hari ini. Coba besok.";
        if (a.affection < 0 || a.affection > 10 || a.scene(p.route) == null) return "Data aksi tidak valid.";
        return null;
    }

    /** Transaksi atomik; aksi memeluk dll. tidak memakai kuota hadiah/kencan/momen. */
    public String startCoupleAction(String id, String area) {
        String blocked = coupleActionBlock(id, area);
        if (blocked != null) return blocked;
        if ("gandengan".equals(id) && p.holdingHands) {
            p.holdingHands = false;
            return "Berhenti bergandengan.";
        }
        QuestDb.CoupleAction a = coupleAction(id);
        if ("gandengan".equals(id) && p.coupleActionDays.getOrDefault(id, -1) == p.day) {
            p.holdingHands = true;
            return "Bergandengan lagi."; // re-enable tidak menggandakan bonus
        }
        p.coupleActionDays.put(id, p.day);
        p.coupleActionCounts.put(id, Math.min(100000, p.coupleActionCounts.getOrDefault(id, 0) + 1));
        p.flags.add("ROM_ACT_" + id.toUpperCase(java.util.Locale.ROOT) + "_ONCE");
        if ("gandengan".equals(id)) p.holdingHands = true;
        addAffection(a.affection);
        return "Aksi berdua! +" + a.affection + " kedekatan.";
    }

    /** Gerak dua sprite melalui satu cutscene; pose diputar serempak, bukan dialog-only. */
    public List<Map<String, Object>> coupleActionActions(String id) {
        QuestDb.CoupleAction a = coupleAction(id);
        if (a == null || a.scene(p.route) == null) return Collections.emptyList();
        List<Map<String, Object>> commands = new ArrayList<>();
        Map<String, Object> bars = new LinkedHashMap<>(); bars.put("c", "bars"); bars.put("on", true); bars.put("t", 0.35); commands.add(bars);
        Map<String, Object> cam = new LinkedHashMap<>(); cam.put("c", "cam"); cam.put("on", "player"); cam.put("zoom", 1.35); cam.put("t", 0.6); commands.add(cam);
        Map<String, Object> pair = new LinkedHashMap<>(); pair.put("c", "pair"); pair.put("kind", a.gesture); pair.put("t", 2.1); pair.put("block", true); commands.add(pair);
        Map<String, Object> fx = new LinkedHashMap<>(); fx.put("c", "fx"); fx.put("kind", "hearts"); fx.put("on", "player"); fx.put("t", 1.5); commands.add(fx);
        Map<String, Object> end = new LinkedHashMap<>(); end.put("c", "bars"); end.put("on", false); end.put("t", 0.45); commands.add(end);
        Map<String, Object> cine = new LinkedHashMap<>(); cine.put("do", "cine"); cine.put("cmds", commands);
        List<Map<String, Object>> acts = new ArrayList<>(); acts.add(cine);
        Map<String, Object> scene = new LinkedHashMap<>(); scene.put("do", "scene"); scene.put("id", a.scene(p.route)); acts.add(scene);
        for (int level : new int[]{20, 50, 80}) {
            String key = "ROM_BOND_" + level;
            if (!p.hasFlag(key) || p.hasFlag(key + "_SCENE")) continue;
            Map<String, Object> mem = new LinkedHashMap<>(); mem.put("do", "scene"); mem.put("id", "RM-BOND-" + level + "@" + p.route); acts.add(mem);
            Map<String, Object> flag = new LinkedHashMap<>(); flag.put("do", "flag"); flag.put("id", key + "_SCENE"); acts.add(flag);
        }
        return acts;
    }

    private List<Map<String, Object>> romanceSceneActions(String scene, boolean withCine) {
        List<Map<String, Object>> acts = new ArrayList<>();
        if (withCine) {
            List<Map<String, Object>> cmds = new ArrayList<>();
            Map<String, Object> face = new LinkedHashMap<>(); face.put("c", "face"); face.put("who", "player"); face.put("at", "partner"); cmds.add(face);
            Map<String, Object> hearts = new LinkedHashMap<>(); hearts.put("c", "fx"); hearts.put("kind", "hearts"); hearts.put("t", 1.2); hearts.put("block", true); cmds.add(hearts);
            Map<String, Object> cine = new LinkedHashMap<>(); cine.put("do", "cine"); cine.put("cmds", cmds); acts.add(cine);
        }
        Map<String, Object> emote = new LinkedHashMap<>(); emote.put("do", "emote");
        emote.put("who", "partner"); emote.put("e", "heart"); acts.add(emote);
        Map<String, Object> sc = new LinkedHashMap<>(); sc.put("do", "scene");
        sc.put("id", scene); acts.add(sc);
        // Momen milestone baru hanya diputar setelah transaksi berhasil dan hanya sekali.
        for (int level : new int[]{20, 50, 80}) {
            String key = "ROM_BOND_" + level;
            if (!p.hasFlag(key) || p.hasFlag(key + "_SCENE")) continue;
            Map<String, Object> moment = new LinkedHashMap<>();
            moment.put("do", "scene"); moment.put("id", "RM-BOND-" + level + "@" + p.route); acts.add(moment);
            Map<String, Object> seen = new LinkedHashMap<>();
            seen.put("do", "flag"); seen.put("id", key + "_SCENE"); acts.add(seen);
        }
        return acts;
    }

    public List<Map<String, Object>> giftActions(String item) {
        QuestDb.Gift g = gift(item);
        return g == null ? Collections.<Map<String, Object>>emptyList()
                : romanceSceneActions(Routes.resolve(g.scene + "@$ROUTE", p.route), false);
    }

    public List<Map<String, Object>> dateActions(String id) {
        QuestDb.DateActivity d = date(id);
        return d == null ? Collections.<Map<String, Object>>emptyList() : romanceSceneActions(d.scene(p.route), true);
    }

    // ------------------------------------------------------------ tampilan step
    public String objectiveText() {
        QuestDb.Step s = step();
        if (s == null) return "";
        String t = s.objective(p.route);
        if (s.counter != null && s.counterMax > 0) t += " (" + Math.min(p.count(s.counter), s.counterMax) + "/" + s.counterMax + ")";
        return t;
    }

    private boolean visible(QuestDb.Interactable it, String area) {
        if (!it.forRoute(p.route)) return false;
        if (!Routes.resolve(it.area, p.route).equals(area)) return false;
        if (it.hideIfFlag != null && p.hasFlag(Routes.resolve(it.hideIfFlag, p.route))) return false;
        return check(it.when);
    }

    /** Interaksi cerita utama (step aktif) di area ini. */
    public List<QuestDb.Interactable> interactables(String area) {
        QuestDb.Step s = step();
        if (s == null) return Collections.emptyList();
        List<QuestDb.Interactable> out = new ArrayList<>();
        for (QuestDb.Interactable it : s.interactables) if (visible(it, area)) out.add(it);
        return out;
    }

    /** Interaksi side quest / aktivitas bebas yang aktif di area ini. */
    public List<QuestDb.Interactable> sideInteractables(String area) {
        List<QuestDb.Interactable> out = new ArrayList<>();
        for (QuestDb.Interactable it : quests.side) if (visible(it, area)) out.add(it);
        return out;
    }

    public static final class NpcView {
        public final String who, dir, id, name; public final float x, y; public final boolean town;
        NpcView(String who, String dir, float x, float y, String id, String name, boolean town) {
            this.who = who; this.dir = dir; this.x = x; this.y = y; this.id = id; this.name = name; this.town = town;
        }
    }

    /** NPC pasangan dari step aktif. */
    public List<NpcView> npcs(String area) {
        QuestDb.Step s = step();
        List<NpcView> out = new ArrayList<>();
        if (s == null) return out;
        for (QuestDb.Npc n : s.npcs) if (Routes.resolve(n.area, p.route).equals(area))
            out.add(new NpcView(Routes.resolve(n.who, p.route), n.dir, n.x, n.y, null, null, false));
        return out;
    }

    /** NPC kota yang hadir di area ini. */
    public List<QuestDb.TownNpc> townNpcs(String area) {
        List<QuestDb.TownNpc> out = new ArrayList<>();
        for (QuestDb.TownNpc n : quests.townNpcs) if (n.area.equals(area) && check(n.when)) out.add(n);
        return out;
    }

    /** cuaca efektif: step cerita (mis. hujan Chapter 4) menimpa cuaca harian. */
    public String weatherNow() {
        QuestDb.Step s = step();
        if (s != null && s.weather != null) return "rain".equals(s.weather) ? WorldClock.HUJAN : s.weather;
        return WorldClock.weather(p.day);
    }

    /** Lokasi NPC saat ini {area, x, y, dir, wander}. NPC tetap di posisi rumah bila step aktif membutuhkannya di sana. */
    public Object[] npcPlace(QuestDb.TownNpc n) {
        Object[] home = {n.area, n.x, n.y, n.dir, n.wander};
        if (n.schedule.isEmpty() || neededByStep(n)) return home;
        String w = weatherNow();
        Map<String, Object> pick = null;
        for (Map<String, Object> e : n.schedule) {
            // Story-safe conditional NPC positions: a required scene may place
            // a named actor at a cafe/gallery even outside their routine hours.
            // Entries without 'when' retain their original scheduling semantics.
            if (!check(Json.obj(e, "when"))) continue;
            List<String> ws = Json.strList(e, "weather");
            if (!ws.isEmpty() && !ws.contains(w)) continue;
            if (WorldClock.parse(e.get("at"), 0) <= p.minute) pick = e;
        }
        if (pick == null) return home;
        if (Json.bool(pick, "hidden", false)) return null;
        return new Object[]{Json.str(pick, "area", n.area), Json.num(pick, "x", n.x), Json.num(pick, "y", n.y), Json.str(pick, "dir", n.dir), Json.num(pick, "wander", n.wander)};
    }

    private boolean neededByStep(QuestDb.TownNpc n) {
        QuestDb.Step s = step();
        if (s == null) return false;
        for (QuestDb.Interactable it : s.interactables)
            if (Routes.resolve(it.area, p.route).equals(n.area) && Math.abs(it.x - n.x) < 90 && Math.abs(it.y - n.y) < 90) return true;
        for (QuestDb.Npc np : s.npcs) if (Routes.resolve(np.who, p.route).equals(n.sprite)) return true;
        for (Map<String, Object> d : n.dialogs) if (Json.strList(Json.obj(d, "when"), "steps").contains(s.id)) return true; // dialog cerita aktif
        return false;
    }

    /** NPC yang sedang berada di area ini menurut jadwal (untuk tampilan). */
    public List<QuestDb.TownNpc> townNpcsNow(String area) {
        List<QuestDb.TownNpc> out = new ArrayList<>();
        for (QuestDb.TownNpc n : quests.townNpcs) {
            if (!check(n.when)) continue;
            Object[] pl = npcPlace(n);
            if (pl != null && area.equals(pl[0])) out.add(n);
        }
        return out;
    }

    /** Dialog NPC pertama yang kondisinya cocok (null bila tidak ada). */
    public Map<String, Object> npcDialog(QuestDb.TownNpc n) {
        for (Map<String, Object> d : n.dialogs) if (check(Json.obj(d, "when"))) return d;
        return null;
    }

    /** Percakapan pasangan yang tersedia di area ini (belum pernah diputar), atau null. */
    public QuestDb.Talk partnerTalk(String area) {
        for (QuestDb.Talk t : quests.talks)
            if ((t.area == null || t.area.equals(area)) && !p.hasFlag("TALK_" + t.id) && check(t.when)) return t;
        return null;
    }

    public List<Map<String, Object>> talkActions(QuestDb.Talk t) {
        List<Map<String, Object>> l = new ArrayList<>();
        Map<String, Object> sc = new LinkedHashMap<>(); sc.put("do", "scene"); sc.put("id", Routes.resolve(t.scene, p.route)); l.add(sc);
        Map<String, Object> f = new LinkedHashMap<>(); f.put("do", "flag"); f.put("id", "TALK_" + t.id); l.add(f);
        return l;
    }

    public List<MapDb.Examine> examine(MapDb.Area a) {
        List<MapDb.Examine> out = new ArrayList<>();
        for (MapDb.Examine e : a.examine) if (check(e.when) && !e.lines(p.route).isEmpty()) out.add(e);
        return out;
    }

    /** null bila pintu boleh dilewati; selain itu teks alasan terkunci. */
    public String doorLock(MapDb.Door d) {
        if (d.route != null && !d.route.equals(p.route)) return d.routeText;
        for (MapDb.Lock l : d.locks) {
            if (l.steps.contains(p.step)) return l.text(p.route);
            if (!l.when.isEmpty() && check(l.when)) return l.text(p.route);
        }
        return null;
    }

    /** Salinan aksi: filter route + resolusi token. */
    public List<Map<String, Object>> resolve(List<Map<String, Object>> actions) {
        List<Map<String, Object>> out = new ArrayList<>();
        for (Map<String, Object> a : actions) {
            String r = Json.str(a, "route", null);
            if (r != null && !r.equals(p.route)) continue;
            Map<String, Object> c = new LinkedHashMap<>();
            for (Map.Entry<String, Object> e : a.entrySet())
                c.put(e.getKey(), e.getValue() instanceof String ? Routes.resolve((String) e.getValue(), p.route) : e.getValue());
            out.add(c);
        }
        return out;
    }

    public List<Map<String, Object>> actionsFor(QuestDb.Interactable it) { return resolve(it.actions); }

    public List<Map<String, Object>> onEnterArea(String area) {
        QuestDb.Step s = step();
        if (s == null || s.enterArea == null) return Collections.emptyList();
        if (!Routes.resolve(s.enterArea, p.route).equals(area)) return Collections.emptyList();
        return resolve(s.enterActions);
    }

    /** Aksi penyelesaian step berbasis counter. Hanya sekali per step. */
    public List<Map<String, Object>> checkComplete() {
        QuestDb.Step s = step();
        if (s == null || s.completeCounter == null || s.completeCount <= 0) return Collections.emptyList();
        String done = "STEPDONE_" + s.id;
        if (p.count(s.completeCounter) >= s.completeCount && !p.hasFlag(done)) {
            p.flags.add(done);
            return resolve(s.completeActions);
        }
        return Collections.emptyList();
    }

    public void addFlags(List<String> flags) { for (String f : flags) if (f != null && !f.isEmpty()) p.flags.add(Routes.resolve(f, p.route)); }

    /** Terapkan aksi state. Mengembalikan true bila state berubah. */
    public boolean apply(Map<String, Object> a) {
        String d = Json.str(a, "do", "");
        switch (d) {
            case "flag": p.flags.add(Json.str(a, "id", "")); return true;
            case "unflag": return p.flags.remove(Json.str(a, "id", ""));
            case "item": {
                String id = Json.str(a, "id", "");
                if (!p.items.contains(id)) { p.items.add(id); return true; }
                return false;
            }
            case "removeItem": return p.items.remove(Json.str(a, "id", ""));
            case "shard": p.shards++; return true;
            case "count": p.addCount(Json.str(a, "id", ""), (int) Json.num(a, "add", 1)); return true;
            case "setCount": { String id = Json.str(a, "id", ""); p.addCount(id, (int) Json.num(a, "value", 0) - p.count(id)); return true; }
            case "companion": p.companion = Json.bool(a, "on", false); return true;
            case "step": {
                String id = Json.str(a, "id", "");
                if (quests.step(id) == null) throw new IllegalStateException("Step tidak ada: " + id);
                p.step = id;
                String ch = quests.chapterStartSteps.get(id);
                if (ch != null && !p.snapshots.containsKey(ch)) p.snapshot(ch);
                return true;
            }
            // Narrative date rescheduling: real next day, no save-schema mutation.
            // This action is invoked only by the one-off C02 postpone/decline quests,
            // immediately followed by a new step, so a resumed save cannot farm days.
            case "restUntilTomorrow": {
                if (p.day >= 1000000) return false;
                p.day++;
                p.minute = 7 * 60;
                p.companion = false;
                p.holdingHands = false;
                return true;
            }
            case "chapterEnd": return p.chapters.add(Json.str(a, "chapter", ""));
            default: return false;
        }
    }

    public QuestDb.Puzzle puzzle(String id) { return quests.puzzles.get(id); }
}
