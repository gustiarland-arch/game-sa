package com.arlandsofia.olu.logic;

import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.zip.CRC32;

/**
 * Penyimpanan lokal: slot per route (arland_slot_01/02, sofia_slot_01/02) + global.json + settings.json.
 * Format: amplop {format, crc, payload}; CRC32 memvalidasi isi; file .bak sebagai cadangan; tulis atomik.
 * Tidak ada jaringan sama sekali. Save web v0.4 (localStorage) TIDAK dibaca otomatis.
 */
public final class SaveStore {
    public static final int SLOTS = 2;
    public static final String DIR = "saves/";

    public enum Status { OK, MISSING, RECOVERED, CORRUPT, INCOMPATIBLE }

    public static final class Loaded<T> {
        public final T value; public final Status status; public final String error;
        Loaded(T value, Status status, String error) { this.value = value; this.status = status; this.error = error; }
    }

    private final FileIO io;

    public SaveStore(FileIO io) { this.io = io; }

    public static String slotPath(String route, int slot) {
        return DIR + route + String.format(Locale.ROOT, "_slot_%02d.json", slot);
    }

    // ------------------------------------------------------------ amplop
    static long crc(String s) {
        CRC32 c = new CRC32();
        c.update(s.getBytes(StandardCharsets.UTF_8));
        return c.getValue();
    }

    static String wrap(Map<String, Object> payload) {
        Map<String, Object> env = new LinkedHashMap<>();
        env.put("format", "olu-save");
        env.put("crc", crc(Json.writeCompact(payload)));
        env.put("payload", payload);
        return Json.write(env);
    }

    @SuppressWarnings("unchecked")
    static Map<String, Object> unwrap(String text) {
        if (text == null) return null;
        Map<String, Object> env = Json.parseObject(text);
        if (!"olu-save".equals(Json.str(env, "format", ""))) throw new IllegalArgumentException("Bukan file save game ini");
        Object p = env.get("payload");
        if (!(p instanceof Map)) throw new IllegalArgumentException("Payload hilang");
        Object c = env.get("crc");
        long want = c instanceof Number ? ((Number) c).longValue() : -1;
        if (want != crc(Json.writeCompact(p))) throw new IllegalArgumentException("Checksum tidak cocok (file rusak)");
        return (Map<String, Object>) p;
    }

    /** Tulis aman dengan dua cadangan. Hanya file utama yang valid secara semantik boleh dirotasi. */
    boolean writeWithBackup(String path, Map<String, Object> payload) {
        return writeWithBackup(path, payload, false);
    }

    boolean writeWithBackup(String path, Map<String, Object> payload, boolean progressSlot) {
        String old = io.read(path);
        if (old != null) {
            try {
                Map<String, Object> oldPayload = unwrap(old);
                // Jangan timpa data dari versi aplikasi yang lebih baru.
                if (progressSlot && Json.num(oldPayload, "schema", 0) > Progress.SCHEMA) return false;
                if (progressSlot) validateStoredProgress(path, oldPayload);
                String prev = io.read(path + ".bak");
                if (prev != null) {
                    try {
                        Map<String, Object> oldBackup = unwrap(prev);
                        if (progressSlot) validateStoredProgress(path, oldBackup);
                        if (!io.writeAtomic(path + ".bak2", prev)) return false;
                    } catch (RuntimeException ignored) { /* backup rusak tidak dirotasi */ }
                }
                if (!io.writeAtomic(path + ".bak", old)) return false;
            } catch (RuntimeException ignored) { /* file utama rusak: jangan hapus backup valid */ }
        }
        return io.writeAtomic(path, wrap(payload));
    }

    /** Pastikan backup berasal dari slot yang sama, dan progres benar-benar bisa dibaca. */
    private static void validateStoredProgress(String path, Map<String, Object> data) {
        Progress p = Progress.fromMap(data);
        if (!slotPath(p.route, p.slot).equals(path))
            throw new IllegalArgumentException("Backup milik slot lain");
    }

    private static final String[] SOURCES = {"", ".tmp", ".bak", ".bak2"};

    private Loaded<Map<String, Object>> readWithBackup(String path) {
        boolean seen = false;
        String err = null;
        for (String suffix : SOURCES) {
            String raw = io.read(path + suffix);
            if (raw == null) {
                if (io.exists(path + suffix)) { seen = true; if (err == null) err = "File ada tetapi gagal dibaca"; }
                continue;
            }
            seen = true;
            try { return new Loaded<>(unwrap(raw), suffix.isEmpty() ? Status.OK : Status.RECOVERED, err); }
            catch (RuntimeException ex) { if (err == null) err = ex.getMessage(); }
        }
        return new Loaded<>(null, seen ? Status.CORRUPT : Status.MISSING, err);
    }

    /** Validasi schema, route dan slot dari setiap kandidat sebelum menerima recovery. */
    private Loaded<Progress> readProgress(String route, int slot) {
        String path = slotPath(route, slot);
        boolean seen = false;
        String firstError = null;
        for (String suffix : SOURCES) {
            String raw = io.read(path + suffix);
            if (raw == null) {
                if (io.exists(path + suffix)) { seen = true; if (firstError == null) firstError = "File ada tetapi gagal dibaca"; }
                continue;
            }
            seen = true;
            try {
                Map<String, Object> map = unwrap(raw);
                int schema = (int) Json.num(map, "schema", 0);
                if (schema > Progress.SCHEMA && suffix.isEmpty())
                    return new Loaded<>(null, Status.INCOMPATIBLE, "Save berasal dari versi game lebih baru (schema " + schema + ")");
                Progress progress = Progress.fromMap(map);
                if (!route.equals(progress.route)) throw new IllegalArgumentException("Route di file tidak cocok");
                if (progress.slot != slot) throw new IllegalArgumentException("Nomor slot di file tidak cocok");
                return new Loaded<>(progress, suffix.isEmpty() ? Status.OK : Status.RECOVERED, firstError);
            } catch (RuntimeException ex) {
                if (firstError == null) firstError = ex.getMessage();
            }
        }
        return new Loaded<>(null, seen ? Status.CORRUPT : Status.MISSING, firstError);
    }

    // ------------------------------------------------------------ slot
    public boolean saveSlot(Progress p) {
        if (p == null || !Routes.valid(p.route) || p.slot < 1 || p.slot > SLOTS || p.step == null || p.step.isEmpty()) return false;
        long previousTime = p.savedAt;
        p.savedAt = System.currentTimeMillis();
        boolean success = writeWithBackup(slotPath(p.route, p.slot), p.toMap(true), true);
        if (!success) p.savedAt = previousTime;
        return success;
    }

    public Loaded<Progress> loadSlot(String route, int slot) {
        if (!Routes.valid(route) || slot < 1 || slot > SLOTS)
            return new Loaded<>(null, Status.CORRUPT, "Route atau nomor slot tidak valid");
        return readProgress(route, slot);
    }

    public void deleteSlot(String route, int slot) {
        io.delete(slotPath(route, slot));
        io.delete(slotPath(route, slot) + ".bak");
        io.delete(slotPath(route, slot) + ".bak2");
        io.delete(slotPath(route, slot) + ".tmp");
    }

    // ------------------------------------------------------------ global & settings
    public GlobalProgress loadGlobal() {
        Loaded<Map<String, Object>> raw = readWithBackup(DIR + "global.json");
        if (raw.value == null) return new GlobalProgress();
        try { return GlobalProgress.fromMap(raw.value); } catch (RuntimeException e) { return new GlobalProgress(); }
    }

    public boolean saveGlobal(GlobalProgress g) { return writeWithBackup(DIR + "global.json", g.toMap()); }

    public Settings loadSettings() {
        Loaded<Map<String, Object>> raw = readWithBackup("settings.json");
        if (raw.value == null) return new Settings();
        try { return Settings.fromMap(raw.value); } catch (RuntimeException e) { return new Settings(); }
    }

    public boolean saveSettings(Settings s) { return writeWithBackup("settings.json", s.toMap()); }
}
