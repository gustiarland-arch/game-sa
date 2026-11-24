package com.arlandsofia.olu.logic;

import java.util.List;
import java.util.Map;

/** v4.9 memory echoes: validated, deterministic per-route note sequences. No rendering dependency. */
public final class EchoPatternV49 {
    private EchoPatternV49() {}

    public static int[][] fromConfig(Map<String, Object> config, String route) {
        Object raw = Json.obj(config, "patterns").get(route);
        if (!(raw instanceof List)) throw new IllegalArgumentException("Pola echo tidak ada untuk " + route);
        @SuppressWarnings("unchecked") List<Object> stages = (List<Object>) raw;
        if (stages.size() < 2 || stages.size() > 5)
            throw new IllegalArgumentException("Jumlah tahap echo tidak valid");
        int[][] result = new int[stages.size()][];
        for (int i = 0; i < stages.size(); i++) {
            if (!(stages.get(i) instanceof List)) throw new IllegalArgumentException("Tahap echo harus berupa daftar");
            @SuppressWarnings("unchecked") List<Object> notes = (List<Object>) stages.get(i);
            if (notes.size() < 2 || notes.size() > 8)
                throw new IllegalArgumentException("Jumlah nada echo tidak valid: " + i);
            result[i] = new int[notes.size()];
            for (int j = 0; j < notes.size(); j++) {
                if (!(notes.get(j) instanceof Number)) throw new IllegalArgumentException("Nada harus angka");
                int n = ((Number) notes.get(j)).intValue();
                if (n < 0 || n > 3) throw new IllegalArgumentException("Nada echo di luar 0..3");
                result[i][j] = n;
            }
        }
        return result;
    }

    /** Player mistake only restarts the current pattern; progress cannot softlock. */
    public static boolean matches(int[][] patterns, int stage, int index, int button) {
        return patterns != null && stage >= 0 && stage < patterns.length
                && index >= 0 && index < patterns[stage].length && button == patterns[stage][index];
    }
}
