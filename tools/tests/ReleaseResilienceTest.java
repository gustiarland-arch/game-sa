import com.arlandsofia.olu.logic.*;
import java.util.*;

/** Uji skenario rilis yang berisiko: file rusak, backup, I/O gagal, migrasi, dan achievement. */
public final class ReleaseResilienceTest {
    static int checks;
    static void ok(boolean b, String msg) { checks++; if (!b) throw new AssertionError(msg); }
    static class Store implements FileIO {
        final Map<String, String> files = new HashMap<>();
        String fail;
        @Override public String read(String path) { return files.get(path); }
        @Override public boolean exists(String path) { return files.containsKey(path); }
        @Override public void delete(String path) { files.remove(path); }
        @Override public boolean writeAtomic(String path, String contents) {
            if (path.equals(fail)) return false;
            files.put(path, contents); return true;
        }
    }
    static Progress sample(String route, int slot, int coins) {
        Progress p = new Progress();
        p.route = route; p.slot = slot; p.step = "PRO_001"; p.area = "plaza";
        p.x = 100; p.y = 200; p.coins = coins;
        return p;
    }
    static String raw(String route, int slot) { return SaveStore.slotPath(route, slot); }
    static String envelope(Map<String, Object> payload) {
        String bytes = Json.writeCompact(payload);
        java.util.zip.CRC32 c = new java.util.zip.CRC32();
        c.update(bytes.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        Map<String, Object> env = new LinkedHashMap<>();
        env.put("format", "olu-save"); env.put("crc", c.getValue()); env.put("payload", payload);
        return Json.write(env);
    }
    public static void main(String[] args) {
        Store mem = new Store(); SaveStore store = new SaveStore(mem);
        Progress p = sample("arland", 1, 12);
        ok(store.loadSlot("arland", 1).status == SaveStore.Status.MISSING, "slot kosong");
        ok(store.saveSlot(p), "save pertama");
        ok(p.savedAt > 0, "timestamp");
        ok(store.loadSlot("arland", 1).value.coins == 12, "roundtrip");
        p.coins = 30; ok(store.saveSlot(p), "save kedua");
        p.coins = 50; ok(store.saveSlot(p), "save ketiga");
        ok(mem.exists(raw("arland", 1) + ".bak2"), "dua backup");
        ok(store.loadSlot("arland", 1).value.coins == 50, "main terbaru");
        mem.files.put(raw("arland", 1), "{bad");
        ok(store.loadSlot("arland", 1).status == SaveStore.Status.RECOVERED, "recovery bak");
        ok(store.loadSlot("arland", 1).value.coins == 30, "bak terbaru");
        mem.files.put(raw("arland", 1) + ".bak", "{corrupt");
        ok(store.loadSlot("arland", 1).value.coins == 12, "bak2 valid");
        mem.files.put(raw("arland", 1) + ".bak2", "{corrupt");
        ok(store.loadSlot("arland", 1).status == SaveStore.Status.CORRUPT, "semua salinan rusak");
        // Tes fallback semantik: CRC benar, tetapi step kosong (dibuat via API save).
        Progress invalid = sample("arland", 1, 21); invalid.step = "";
        ok(!store.saveSlot(invalid), "save baru dengan step kosong ditolak");
        ok(store.loadSlot("arland", 1).status == SaveStore.Status.CORRUPT, "semua salinan sebelumnya tetap rusak");
        // Save valid -> backup normal -> simulasikan file utama dengan isi tidak valid tapi CRC valid.
        mem = new Store(); store = new SaveStore(mem);
        Progress valid = sample("arland", 1, 100);
        ok(store.saveSlot(valid), "valid base");
        Progress corrupt = sample("arland", 1, 101); corrupt.step = "";
        Progress second = sample("arland", 1, 99);
        ok(store.saveSlot(second), "backup semantik valid disiapkan");
        mem.files.put(raw("arland", 1), envelope(corrupt.toMap(true)));
        ok(store.loadSlot("arland", 1).value.coins == 100, "fallback semantik ke backup");
        ok(store.loadSlot("arland", 1).status == SaveStore.Status.RECOVERED, "status semantik pulih");
        ok(store.saveSlot(sample("arland", 1, 120)), "simpan baru setelah file utama korup");
        ok(store.loadSlot("arland", 1).value.coins == 120, "save baru valid");
        ok(mem.files.get(raw("arland", 1) + ".bak").equals(envelope(valid.toMap(true))), "backup valid tidak dirusak oleh main corrupt");
        // Byte .tmp dapat dipakai jika main dan backup hilang.
        String good = mem.files.get(raw("arland", 1) + ".bak");
        mem.files.clear(); mem.files.put(raw("arland", 1) + ".tmp", good);
        ok(store.loadSlot("arland", 1).status == SaveStore.Status.RECOVERED, "recovery tmp");
        ok(store.loadSlot("arland", 1).value.coins == 100, "tmp datanya benar");
        // I/O failure tidak menimpa save lama dan timestamp objek tetap sama.
        mem = new Store(); store = new SaveStore(mem);
        Progress first = sample("arland", 1, 17);
        ok(store.saveSlot(first), "save sebelum gagal");
        Progress next = sample("arland", 1, 99);
        next.savedAt = 555;
        mem.fail = raw("arland", 1) + ".bak";
        ok(!store.saveSlot(next), "backup gagal -> save gagal");
        ok(next.savedAt == 555, "timestamp restore saat gagal");
        ok(store.loadSlot("arland", 1).value.coins == 17, "save lama utuh");
        mem.fail = raw("arland", 1);
        ok(!store.saveSlot(next), "main write gagal");
        ok(store.loadSlot("arland", 1).value.coins == 17, "main utuh saat gagal");
        ok(!store.saveSlot(sample("wrong", 1, 1)), "invalid route ditolak");
        ok(!store.saveSlot(sample("arland", 3, 1)), "invalid slot ditolak");
        ok(store.loadSlot("arland", 3).status == SaveStore.Status.CORRUPT, "invalid slot load ditolak");
        // Tidak boleh menyatakan "kosong" jika file ada namun permission/disk gagal dibaca.
        Store inaccessible = new Store() {
            @Override public String read(String path) { return null; }
        };
        inaccessible.files.put(raw("arland", 1), "file pada storage privat");
        ok(new SaveStore(inaccessible).loadSlot("arland", 1).status == SaveStore.Status.CORRUPT,
                "berkas tidak dapat dibaca harus dianggap bermasalah, bukan kosong");
        // Slot salah tidak boleh terbaca sebagai slot lain.
        mem = new Store(); store = new SaveStore(mem);
        ok(store.saveSlot(sample("arland", 1, 7)), "file route benar");
        mem.files.put(raw("sofia", 1), mem.files.get(raw("arland", 1)));
        ok(store.loadSlot("sofia", 1).status == SaveStore.Status.CORRUPT, "route mismatch");
        // Simpan dari versi lebih baru tidak pernah diam-diam downgrade ke .bak.
        Progress future = sample("arland", 1, 55);
        Map<String, Object> futureMap = future.toMap(true);
        futureMap.put("schema", 999);
        // Buat envelope lewat SaveStore dengan item peta masa depan menggunakan helper test reflection-free:
        // salin payload legal, ganti dan hitung ulang amplop melalui API data map di bawah.
        String serialized = Json.writeCompact(futureMap);
        java.util.zip.CRC32 crc = new java.util.zip.CRC32();
        crc.update(serialized.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        Map<String, Object> env = new LinkedHashMap<>();
        env.put("format", "olu-save"); env.put("crc", crc.getValue()); env.put("payload", futureMap);
        mem.files.put(raw("arland", 1), Json.write(env));
        ok(store.loadSlot("arland", 1).status == SaveStore.Status.INCOMPATIBLE, "schema masa depan diblokir");
        String futureBytes = mem.files.get(raw("arland", 1));
        ok(!store.saveSlot(sample("arland", 1, 99)), "versi lama tidak menimpa save versi baru");
        ok(mem.files.get(raw("arland", 1)).equals(futureBytes), "save baru tidak berubah");
        // Achievements tetap global, migrasi global lama tetap aman.
        GlobalProgress global = new GlobalProgress();
        Progress a = sample("arland", 1, 250);
        a.playSeconds = 500; a.affection = 90; a.shards = 3;
        a.chapters.add("C01"); a.chapters.add("C02"); a.chapters.add("C03"); a.chapters.add("C04"); a.chapters.add("C06");
        a.petted.addAll(Arrays.asList("cat", "dog", "rabbit", "duck"));
        a.coupleActionCounts.put("hug", 1); a.coupleActionCounts.put("photo", 1); a.coupleActionCounts.put("lean", 1);
        a.momentCounts.put("moon", 1); a.momentCounts.put("tea", 1); a.momentCounts.put("stars", 1);
        a.worldEventCounts.put("w1", 1); a.worldEventCounts.put("w2", 1); a.worldEventCounts.put("w3", 1);
        a.worldEventCounts.put("w4", 1); a.worldEventCounts.put("w5", 1);
        a.dateCounts.put("date", 3);
        a.counters.put("total_romgame_fishing", 1); a.counters.put("total_romgame_cooking", 1);
        a.counters.put("total_romgame_photo", 1);
        global.absorb(a);
        ok(global.achievements.size() == Achievements.ALL.length - 1, "semua kecuali dua route terbuka");
        Progress b = sample("sofia", 1, 10); b.chapters.add("C06");
        global.absorb(b);
        ok(global.achievements.size() == Achievements.ALL.length, "keduanya membuka final achievement");
        ok(global.achievements.contains("both"), "dua sisi satu cerita");
        GlobalProgress restored = GlobalProgress.fromMap(global.toMap());
        ok(restored.achievements.equals(global.achievements), "persist lintas session");
        Map<String, Object> oldGlobal = new LinkedHashMap<>(global.toMap());
        oldGlobal.remove("achievements"); oldGlobal.put("schema", 1);
        ok(GlobalProgress.fromMap(oldGlobal).achievements.contains("both") && GlobalProgress.fromMap(oldGlobal).achievements.size() == 1, "migrasi global schema1");
        ok(global.achievements.size() == Achievements.ALL.length, "prestasi permanen");
        System.out.println("RELEASE RESILIENCE: " + checks + " assertions OK (save, CRC, backup, recovery, achievements)");
    }
}
