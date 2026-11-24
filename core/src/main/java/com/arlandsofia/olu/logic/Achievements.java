package com.arlandsofia.olu.logic;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/** Pencapaian offline, permanen lintas save; penghargaan kosmetik, bukan pay-to-win. */
public final class Achievements {
    private Achievements() { }

    public static final class Def {
        public final String id, name, hint;
        Def(String id, String name, String hint) { this.id = id; this.name = name; this.hint = hint; }
    }

    public static final Def[] ALL = {
        new Def("start", "Langkah Pertama", "Mainkan cerita setidaknya 2 menit."),
        new Def("chapter", "Satu Bab Bersama", "Tamatkan satu chapter utama."),
        new Def("chapters", "Penjelajah Kenangan", "Tamatkan lima chapter di satu route."),
        new Def("friend", "Teman Dunia Kecil", "Elus empat hewan berbeda."),
        new Def("couple", "Hari Kita", "Selesaikan tiga jenis aksi berdua."),
        new Def("minigames", "Main Bareng", "Mainkan tiga jenis minigame bersama."),
        new Def("world", "Dunia yang Bergerak", "Ikuti lima jenis event dunia."),
        new Def("moments", "Momen Kecil", "Nikmati tiga jenis momen harian."),
        new Def("dates", "Hari yang Istimewa", "Jalani tiga kencan."),
        new Def("heart", "Semakin Dekat", "Capai kedekatan 75."),
        new Def("shards", "Tiga Keping Kenangan", "Kumpulkan tiga keping kenangan."),
        new Def("both", "Dua Sisi, Satu Cerita", "Tamatkan Chapter 6 dengan Arland dan Sofia.")
    };

    private static int types(Map<String, Integer> counts) {
        int total = 0;
        for (Integer count : counts.values()) if (count != null && count > 0) total++;
        return total;
    }

    private static int total(Map<String, Integer> counts) {
        int sum = 0;
        for (Integer count : counts.values()) if (count != null && count > 0) sum += Math.min(1000, count);
        return sum;
    }

    /** Catat unlock setelah save slot sukses; yang lama tidak pernah dicabut. */
    public static List<String> unlock(Progress p, GlobalProgress g) {
        List<String> added = new ArrayList<>();
        boolean[] conditions = {
            p.playSeconds >= 120, p.chapters.size() >= 1, p.chapters.size() >= 5,
            p.petted.size() >= 4, types(p.coupleActionCounts) >= 3,
            false, // dihitung dari total_romgame_ di bawah
            types(p.worldEventCounts) >= 5, types(p.momentCounts) >= 3,
            total(p.dateCounts) >= 3, p.affection >= 75, p.shards >= 3,
            g.bothCompleted("C06")
        };
        // Selesai minigame romansa dicatat oleh QuestEngine sebagai total_romgame_<id>.
        int mini = 0;
        for (Map.Entry<String, Integer> e : p.counters.entrySet()) {
            String key = e.getKey();
            if (e.getValue() != null && e.getValue() > 0 &&
                key.startsWith("total_romgame_")) mini++;
        }
        conditions[5] = mini >= 3;
        for (int i = 0; i < ALL.length; i++)
            if (conditions[i] && g.achievements.add(ALL[i].id)) added.add(ALL[i].id);
        return added;
    }

    public static Def find(String id) {
        for (Def def : ALL) if (def.id.equals(id)) return def;
        return null;
    }
}
