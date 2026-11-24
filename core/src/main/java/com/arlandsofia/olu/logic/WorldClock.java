package com.arlandsofia.olu.logic;

/**
 * Jam dunia (logika murni, tanpa gdx). Hari berjalan 06:00 - 02:00 (1 detik nyata = 1 menit game saat bebas bermain).
 * Cuaca harian ditentukan dari nomor hari (deterministik, sama untuk save yang sama). Step cerita boleh menimpa cuaca & cahaya.
 */
public final class WorldClock {
    public static final int DAY_START = 6 * 60, DAY_END = 26 * 60;
    public static final String CERAH = "cerah", BERAWAN = "berawan", HUJAN = "hujan", BERANGIN = "berangin";
    private static final String[] DAYS = {"Sabtu", "Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat"};

    private WorldClock() {}

    public static String dayName(int day) { return DAYS[Math.floorMod(day - 1, 7)]; }

    public static String hhmm(int minute) {
        int m = Math.floorMod(minute, 24 * 60);
        return String.format(java.util.Locale.ROOT, "%02d:%02d", m / 60, m % 60);
    }

    public static int hour(int minute) { return Math.floorMod(minute, 24 * 60) / 60; }

    /** cuaca harian; hari 1-2 selalu cerah (awal cerita). */
    public static String weather(int day) {
        if (day <= 2) return CERAH;
        long h = (day * 2654435761L) ^ 0x5bd1e995L; h ^= (h >>> 13); h *= 0x5bd1e995L; h ^= (h >>> 15);
        int r = (int) Math.floorMod(h, 100);
        if (r < 14) return HUJAN;
        if (r < 34) return BERAWAN;
        if (r < 44) return BERANGIN;
        return CERAH;
    }

    /** tint cahaya {r,g,b,alpha} dari jam (menit sejak tengah malam, boleh > 24*60). alpha 0 = siang biasa. */
    public static float[] light(int minute) {
        float m = minute;
        if (m < 7 * 60) return mix(new float[]{1f, 0.72f, 0.55f, 0.14f}, new float[]{1f, 0.85f, 0.7f, 0f}, (m - 5 * 60) / 120f);
        if (m < 16 * 60) return new float[]{1f, 1f, 1f, 0f};
        if (m < 18 * 60) return mix(new float[]{1f, 0.78f, 0.5f, 0f}, new float[]{1f, 0.6f, 0.32f, 0.18f}, (m - 16 * 60) / 120f);
        if (m < 19.5f * 60) return mix(new float[]{1f, 0.6f, 0.32f, 0.18f}, new float[]{0.18f, 0.2f, 0.42f, 0.3f}, (m - 18 * 60) / 90f);
        if (m < 23 * 60) return new float[]{0.11f, 0.14f, 0.32f, 0.32f};
        return mix(new float[]{0.11f, 0.14f, 0.32f, 0.32f}, new float[]{0.06f, 0.07f, 0.2f, 0.42f}, (m - 23 * 60) / 120f);
    }

    public static boolean isNight(int minute) { int h = hour(minute); return h >= 19 || h < 5; }

    private static float[] mix(float[] a, float[] b, float t) {
        t = Math.max(0f, Math.min(1f, t));
        return new float[]{a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t, a[3] + (b[3] - a[3]) * t};
    }

    /** "08:30" atau angka menit -> menit. */
    public static int parse(Object o, int def) {
        if (o instanceof Number) return ((Number) o).intValue();
        if (o instanceof String) {
            String s = (String) o; int i = s.indexOf(':');
            try { return i > 0 ? Integer.parseInt(s.substring(0, i)) * 60 + Integer.parseInt(s.substring(i + 1)) : Integer.parseInt(s); } catch (NumberFormatException e) { return def; }
        }
        return def;
    }
}
