package com.arlandsofia.olu.logic;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** State progres satu route di satu slot (flags lokal per route + per save, sesuai Story Bible). */
public final class Progress {
    public static final int SCHEMA = 8;

    public String route;
    public int slot = 1;
    public String step;
    public String area;
    public float x, y;
    public String dir = "down";
    public final Set<String> flags = new LinkedHashSet<>();
    public final List<String> items = new ArrayList<>();
    public int shards;
    /** Counter generik (keping, tiket, kelopak, dll.). "shards" disinkronkan dengan field shards. */
    public final Map<String, Integer> counters = new LinkedHashMap<>();
    public boolean companion;
    public final Set<String> chapters = new LinkedHashSet<>();   // chapter yang sudah tamat
    public float playSeconds;
    /** jam dunia: hari ke-n (mulai 1) dan menit sejak 00:00 (06:00 = 360, boleh sampai 26*60) */
    public int day = 1, minute = 7 * 60;
    /** Ekonomi offline. Route dan slot memiliki dompet terpisah. */
    public int coins = 12;
    /** v1.6: kedekatan pasangan dari aktivitas sampingan, 0–100. */
    public int affection = 0;
    /** Maksimal satu hadiah dan satu kencan per hari game. */
    public int lastGiftDay = -1, lastDateDay = -1;
    /** Jumlah kenangan per aktivitas; kalender terpisah dari alur cerita. */
    public final Map<String, Integer> dateCounts = new LinkedHashMap<>();
    /** v1.7: momen gratis, maksimal satu jenis apa pun per hari; histori per slot/route. */
    public int lastMomentDay = -1;
    public final Map<String, Integer> momentCounts = new LinkedHashMap<>();
    /** v2.2: bonus aksi berdua satu kali per jenis per hari; tidak mengganggu gift/date/moment. */
    public final Map<String, Integer> coupleActionDays = new LinkedHashMap<>();
    public final Map<String, Integer> coupleActionCounts = new LinkedHashMap<>();
    /** v2.7: world event hanya sekali per event per hari game; memori pertama tetap permanen. */
    public final Map<String, Integer> worldEventDays = new LinkedHashMap<>();
    public final Map<String, Integer> worldEventCounts = new LinkedHashMap<>();
    /** Mode bergandengan saat eksplorasi: tetap tersimpan per route/slot. */
    public boolean holdingHands;
    /** Hari terakhir menerima upah, per pekerjaan. */
    public final Map<String, Integer> jobDays = new LinkedHashMap<>();
    /** Hari ketika tugas surat dimulai; -1 = tidak sedang aktif. */
    public int deliveryStartDay = -1;
    /** Hari terakhir tiap alamat sudah menerima surat. */
    public final Map<String, Integer> deliveryDays = new LinkedHashMap<>();
    /** hewan & warga yang pernah disapa (untuk Memory Book) */
    public final Set<String> petted = new LinkedHashSet<>();
    /** v3.0: Riwayat dialog offline; otomatis dibatasi 72 baris per slot. */
    public final DialogueHistory dialogueHistory = new DialogueHistory();
    /** v3.0: lokasi yang pernah dikunjungi; tidak membuka area atau pintu secara otomatis. */
    public final Set<String> visitedAreas = new LinkedHashSet<>();
    public long savedAt;
    /** Snapshot state pada awal tiap chapter -> dipakai mode replay tanpa merusak progres. */
    public final Map<String, Object> snapshots = new LinkedHashMap<>();

    public static Progress newGame(String route, int slot, String firstStep, MapDb.Area room) {
        Progress p = new Progress();
        p.route = route; p.slot = slot; p.step = firstStep; p.area = room.id;
        p.x = room.spawnX; p.y = room.spawnY; p.dir = "down";
        return p;
    }

    public boolean hasFlag(String f) { return f != null && flags.contains(f); }

    public int count(String id) {
        if ("shards".equals(id)) return shards;
        Integer v = counters.get(id);
        return v == null ? 0 : v;
    }

    public void addCount(String id, int n) {
        if ("shards".equals(id)) { shards = Math.max(0, shards + n); return; }
        counters.put(id, Math.max(0, count(id) + n));
    }
    public boolean hasItem(String i) { return items.contains(i); }

    public Map<String, Object> toMap(boolean withSnapshots) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("schema", SCHEMA);
        m.put("mapLayoutVersion", MapLayoutV54.VERSION);
        m.put("route", route);
        m.put("slot", slot);
        m.put("step", step);
        m.put("area", area);
        m.put("x", Math.round(x));
        m.put("y", Math.round(y));
        m.put("dir", dir);
        m.put("flags", new ArrayList<Object>(flags));
        m.put("items", new ArrayList<Object>(items));
        m.put("shards", shards);
        m.put("counters", new LinkedHashMap<String, Object>(counters));
        m.put("companion", companion);
        m.put("chapters", new ArrayList<Object>(chapters));
        m.put("playSeconds", Math.round(playSeconds));
        m.put("day", day); m.put("minute", minute); m.put("petted", new ArrayList<Object>(petted));
        m.put("coins", coins);
        m.put("affection", affection);
        m.put("lastGiftDay", lastGiftDay);
        m.put("lastDateDay", lastDateDay);
        m.put("dateCounts", new LinkedHashMap<String, Object>(dateCounts));
        m.put("lastMomentDay", lastMomentDay);
        m.put("momentCounts", new LinkedHashMap<String, Object>(momentCounts));
        m.put("coupleActionDays", new LinkedHashMap<String, Object>(coupleActionDays));
        m.put("coupleActionCounts", new LinkedHashMap<String, Object>(coupleActionCounts));
        m.put("holdingHands", holdingHands);
        m.put("worldEventDays", new LinkedHashMap<String, Object>(worldEventDays));
        m.put("worldEventCounts", new LinkedHashMap<String, Object>(worldEventCounts));
        m.put("jobDays", new LinkedHashMap<String, Object>(jobDays));
        m.put("deliveryStartDay", deliveryStartDay);
        m.put("deliveryDays", new LinkedHashMap<String, Object>(deliveryDays));
        m.put("dialogueHistory", dialogueHistory.toList());
        m.put("visitedAreas", new ArrayList<Object>(visitedAreas));
        m.put("savedAt", savedAt);
        if (withSnapshots) m.put("snapshots", new LinkedHashMap<String, Object>(snapshots));
        return m;
    }

    /** Membaca + memigrasi + memvalidasi. Melempar IllegalArgumentException bila data tidak valid. */
    @SuppressWarnings("unchecked")
    public static Progress fromMap(Map<String, Object> m) {
        int schema = (int) Json.num(m, "schema", 0);
        if (schema <= 0 || schema > SCHEMA) throw new IllegalArgumentException("Versi save tidak didukung: " + schema);
        // Save schema 1 tidak punya ekonomi; migrasi memberi modal awal yang sama dengan New Game.
        Progress p = new Progress();
        p.route = Json.str(m, "route", null);
        if (!Routes.valid(p.route)) throw new IllegalArgumentException("Route tidak valid");
        p.slot = (int) Json.num(m, "slot", 1);
        p.step = Json.str(m, "step", null);
        if (p.step == null || p.step.isEmpty()) throw new IllegalArgumentException("Step kosong");
        p.area = Json.str(m, "area", Routes.room(p.route));
        p.x = Json.num(m, "x", Float.NaN); p.y = Json.num(m, "y", Float.NaN);
        if (Float.isNaN(p.x) || Float.isNaN(p.y) || Float.isInfinite(p.x) || Float.isInfinite(p.y)) throw new IllegalArgumentException("Posisi rusak");
        // Save v3.x stores coordinates in old map dimensions. Do not overwrite
        // the user's inventory or quest state; only move the player position.
        if (Json.num(m, "mapLayoutVersion", 0) < MapLayoutV4.VERSION) {
            float[] mapped = MapLayoutV4.fromLegacy(p.area, p.x, p.y);
            p.x = mapped[0]; p.y = mapped[1];
        }
        // v5.4: four interiors were rescaled by 0.5; move only the saved position.
        if (Json.num(m, "mapLayoutVersion", 0) < MapLayoutV54.VERSION) {
            float[] mapped = MapLayoutV54.fromV4(p.area, p.x, p.y);
            p.x = mapped[0]; p.y = mapped[1];
        }
        p.dir = Json.str(m, "dir", "down");
        p.flags.addAll(Json.strList(m, "flags"));
        p.items.addAll(Json.strList(m, "items"));
        p.shards = Math.max(0, (int) Json.num(m, "shards", 0));
        for (Map.Entry<String, Object> e : Json.obj(m, "counters").entrySet())
            if (e.getValue() instanceof Number) p.counters.put(e.getKey(), Math.max(0, ((Number) e.getValue()).intValue()));
        p.companion = Json.bool(m, "companion", false);
        p.chapters.addAll(Json.strList(m, "chapters"));
        p.playSeconds = Math.max(0, Json.num(m, "playSeconds", 0));
        p.day = Math.max(1, (int) Json.num(m, "day", 1)); p.minute = Math.max(WorldClock.DAY_START, Math.min(WorldClock.DAY_END, (int) Json.num(m, "minute", 7 * 60)));
        p.petted.addAll(Json.strList(m, "petted"));
        p.coins = schema >= 2 ? Math.max(0, Math.min(1000000, (int) Json.num(m, "coins", 12))) : 12;
        // Save schema 1/2 mendapat state relasi default tanpa menghapus cerita dan dompet.
        p.affection = schema >= 3 ? Math.max(0, Math.min(100, (int) Json.num(m, "affection", 0))) : 0;
        p.lastGiftDay = schema >= 3 ? Math.max(-1, (int) Json.num(m, "lastGiftDay", -1)) : -1;
        p.lastDateDay = schema >= 3 ? Math.max(-1, (int) Json.num(m, "lastDateDay", -1)) : -1;
        if (schema >= 3) for (Map.Entry<String, Object> e : Json.obj(m, "dateCounts").entrySet())
            if (e.getValue() instanceof Number) p.dateCounts.put(e.getKey(), Math.max(0, Math.min(100000, ((Number) e.getValue()).intValue())));
        p.lastMomentDay = schema >= 4 ? Math.max(-1, (int) Json.num(m, "lastMomentDay", -1)) : -1;
        if (schema >= 4) for (Map.Entry<String, Object> e : Json.obj(m, "momentCounts").entrySet())
            if (e.getValue() instanceof Number) p.momentCounts.put(e.getKey(), Math.max(0, Math.min(100000, ((Number) e.getValue()).intValue())));
        if (schema >= 5) {
            for (Map.Entry<String, Object> e : Json.obj(m, "coupleActionDays").entrySet())
                if (e.getValue() instanceof Number) p.coupleActionDays.put(e.getKey(), Math.max(-1, Math.min(1000000, ((Number) e.getValue()).intValue())));
            for (Map.Entry<String, Object> e : Json.obj(m, "coupleActionCounts").entrySet())
                if (e.getValue() instanceof Number) p.coupleActionCounts.put(e.getKey(), Math.max(0, Math.min(100000, ((Number) e.getValue()).intValue())));
            p.holdingHands = Json.bool(m, "holdingHands", false) && p.companion;
        }
        if (schema >= 6) {
            for (Map.Entry<String, Object> e : Json.obj(m, "worldEventDays").entrySet())
                if (e.getValue() instanceof Number) p.worldEventDays.put(e.getKey(), Math.max(-1, Math.min(1000000, ((Number) e.getValue()).intValue())));
            for (Map.Entry<String, Object> e : Json.obj(m, "worldEventCounts").entrySet())
                if (e.getValue() instanceof Number) p.worldEventCounts.put(e.getKey(), Math.max(0, Math.min(100000, ((Number) e.getValue()).intValue())));
        }
        p.deliveryStartDay = schema >= 2 ? (int) Json.num(m, "deliveryStartDay", -1) : -1;
        for (Map.Entry<String, Object> e : Json.obj(m, "jobDays").entrySet())
            if (e.getValue() instanceof Number) p.jobDays.put(e.getKey(), Math.max(0, ((Number) e.getValue()).intValue()));
        for (Map.Entry<String, Object> e : Json.obj(m, "deliveryDays").entrySet())
            if (e.getValue() instanceof Number) p.deliveryDays.put(e.getKey(), Math.max(0, ((Number) e.getValue()).intValue()));
        if (schema >= 7) {
            p.dialogueHistory.restore(m.get("dialogueHistory"));
            for (String a : Json.strList(m, "visitedAreas")) if (a != null && a.length() <= 64) p.visitedAreas.add(a);
            if (p.visitedAreas.size() > 256) {
                Set<String> recent = new LinkedHashSet<>();
                for (String a : p.visitedAreas) { recent.add(a); if (recent.size() == 256) break; }
                p.visitedAreas.clear(); p.visitedAreas.addAll(recent);
            }
        }
        Object sa = m.get("savedAt");
        p.savedAt = sa instanceof Number ? ((Number) sa).longValue() : 0L;
        Object snaps = m.get("snapshots");
        if (snaps instanceof Map) p.snapshots.putAll((Map<String, Object>) snaps);
        return p;
    }

    public Progress copy() {
        Progress p = fromMap(toMap(true));
        return p;
    }

    /** Simpan snapshot awal chapter (tanpa snapshot bersarang). */
    public void snapshot(String chapter) { snapshots.put(chapter, toMap(false)); }

    @SuppressWarnings("unchecked")
    public Progress replayFrom(String chapter) {
        Object s = snapshots.get(chapter);
        if (!(s instanceof Map)) return null;
        return fromMap((Map<String, Object>) s);
    }
}
