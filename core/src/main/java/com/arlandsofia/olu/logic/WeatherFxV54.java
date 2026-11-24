package com.arlandsofia.olu.logic;

import java.util.ArrayList;
import java.util.List;

/**
 * v5.4 weather polish, pure Java (no GDX) so it is testable headlessly.
 *
 * <ul>
 *   <li>{@link Storm}: lightning scheduler with a soft, photosensitivity-safe flash
 *       envelope (at most two pulses per strike, strikes 9 s or more apart, so never
 *       more than three flashes in any one-second window) and a delayed thunder cue.</li>
 *   <li>{@link #puddles}: deterministic rain puddles on walkable ground only (never
 *       inside colliders, water, terraces or stairs). Cosmetic: collision unchanged.</li>
 *   <li>{@link #wetness}: ground wetness that rises while it rains and slowly dries.</li>
 * </ul>
 */
public final class WeatherFxV54 {
    private WeatherFxV54() {}

    /** Peak alpha of the full-screen lightning wash. Kept soft on purpose. */
    public static final float FLASH_PEAK = 0.24f;
    /** Strike spacing in seconds. Long gaps keep storms atmospheric, not strobing. */
    public static final float MIN_GAP = 9f, MAX_GAP = 22f;
    /** Flash envelope: main pulse, short dark gap, softer after-pulse. */
    public static final float FLASH_LEN = 0.46f;

    /** Areas where rain is part of a calm set piece; no thunder there. */
    public static boolean stormAllowed(String areaId, boolean raining, boolean indoor, boolean realm) {
        if (!raining || indoor || realm || areaId == null) return false;
        return !"rain_garden".equals(areaId) && !areaId.startsWith("memory") && !areaId.contains("star");
    }

    public static final class Storm {
        private long seed;
        private float wait, flash = -1f, thunderIn = -1f, thunderVolume;
        private boolean thunderReady;
        private int strikes;

        public Storm(long seed) { this.seed = seed == 0 ? 0x9E3779B97F4A7C15L : seed; reset(); }

        /** Called on area change so a strike does not land mid-transition. */
        public void reset() {
            flash = -1f; thunderIn = -1f; thunderReady = false;
            wait = 4f + rnd() * 5f;
        }

        public int strikes() { return strikes; }

        /** Advances the storm. {@code active} false lets an in-flight flash fade but schedules nothing new. */
        public void update(float dt, boolean active) {
            if (dt <= 0f) return;
            if (flash >= 0f) { flash += dt; if (flash > FLASH_LEN) flash = -1f; }
            if (thunderIn >= 0f) { thunderIn -= dt; if (thunderIn < 0f) thunderReady = true; }
            if (!active) { if (wait < 3f) wait = 3f; return; }
            wait -= dt;
            if (wait <= 0f) {
                strikes++;
                flash = 0f;
                float distance = rnd();                       // 0 = overhead, 1 = far away
                thunderIn = 0.35f + distance * 1.9f;           // light travels faster than sound
                thunderVolume = 1f - distance * 0.55f;
                wait = MIN_GAP + rnd() * (MAX_GAP - MIN_GAP);
            }
        }

        /** Full-screen wash alpha for this frame, 0 when no flash is showing. */
        public float flashAlpha(int quality) {
            if (flash < 0f) return 0f;
            float a = envelope(flash);
            return a * FLASH_PEAK * (quality == 0 ? 0.6f : 1f);
        }

        /** Returns the thunder volume (0..1) exactly once when the rumble should start, else 0. */
        public float consumeThunder() {
            if (!thunderReady) return 0f;
            thunderReady = false;
            return thunderVolume;
        }

        private float rnd() {
            seed ^= seed << 13; seed ^= seed >>> 7; seed ^= seed << 17;
            return (float) ((seed >>> 11) * 0x1.0p-53);
        }
    }

    /** Two smooth pulses: 0..0.16 s main, 0.24..0.46 s after-glow (two flashes per strike). */
    public static float envelope(float t) {
        if (t < 0f || t > FLASH_LEN) return 0f;
        if (t < 0.16f) return (float) Math.sin(Math.PI * t / 0.16f);
        if (t < 0.24f) return 0f;
        return 0.55f * (float) Math.sin(Math.PI * (t - 0.24f) / (FLASH_LEN - 0.24f));
    }

    /** Wetness 0..1: about 45 s to soak, 120 s to dry. */
    public static float wetness(float current, float dt, boolean raining) {
        float next = raining ? current + dt / 45f : current - dt / 120f;
        return Math.max(0f, Math.min(1f, next));
    }

    /** Puddle size presets {halfWidth, halfHeight} in world px; must match WorldFx textures. */
    public static final int[][] PUDDLE_SIZES = {{20, 7}, {30, 10}, {42, 13}};

    /** Deterministic puddle layout: {x, y (y-down), sizeIndex}. Empty for indoor areas. */
    public static List<float[]> puddles(MapDb.Area a) {
        if (a == null || a.indoor) return java.util.Collections.emptyList();
        synchronized (CACHE) {
            List<float[]> hit = CACHE.get(a);
            if (hit == null) { hit = java.util.Collections.unmodifiableList(layout(a)); CACHE.put(a, hit); }
            return hit;
        }
    }

    /** Layout is pure in the map data, so each area is solved once per session. */
    private static final java.util.Map<MapDb.Area, List<float[]>> CACHE = new java.util.WeakHashMap<>();

    private static List<float[]> layout(MapDb.Area a) {
        List<float[]> out = new ArrayList<>();
        int target = Math.max(6, Math.min(16, Math.round(a.w * a.h / 150000f)));
        long s = a.id.hashCode() * 0x9E3779B97F4A7C15L + 0x632BE59BD9B4E019L;
        int tries = 0;
        while (out.size() < target && tries++ < target * 120) {
            s ^= s << 13; s ^= s >>> 7; s ^= s << 17;
            float u = (float) ((s >>> 11) * 0x1.0p-53);
            s ^= s << 13; s ^= s >>> 7; s ^= s << 17;
            float v = (float) ((s >>> 11) * 0x1.0p-53);
            int size = (int) ((s >>> 5) & 0x7fffffff) % PUDDLE_SIZES.length;
            float rx = PUDDLE_SIZES[size][0], ry = PUDDLE_SIZES[size][1];
            float x = 60f + u * (a.w - 120f), y = 80f + v * (a.h - 140f);
            if (!clearGround(a, x, y, rx + 6f, ry + 6f)) continue;
            boolean overlap = false;
            for (float[] q : out) {
                float qx = PUDDLE_SIZES[(int) q[2]][0], qy = PUDDLE_SIZES[(int) q[2]][1];
                if (Math.abs(q[0] - x) < qx + rx + 24f && Math.abs(q[1] - y) < qy + ry + 20f) { overlap = true; break; }
            }
            if (!overlap) out.add(new float[]{x, y, size});
        }
        return out;
    }

    static boolean clearGround(MapDb.Area a, float x, float y, float rx, float ry) {
        // Dense sample of the padded ellipse so small colliders between points are caught too.
        List<float[]> pts = new ArrayList<>();
        for (float u = -1f; u <= 1.001f; u += 0.125f)
            for (float v = -1f; v <= 1.001f; v += 0.125f)
                if (u * u + v * v <= 1.001f) pts.add(new float[]{u * rx, v * ry});
        for (float[] p : pts) {
            float px = x + p[0], py = y + p[1];
            if (px < 0 || py < 0 || px > a.w || py > a.h) return false;
            if (a.blocked(px, py)) return false;
            for (float[] w : a.water) {
                float dx = (px - w[0]) / (w[2] + 30f), dy = (py - w[1]) / (w[3] + 30f);
                if (dx * dx + dy * dy <= 1f) return false;
            }
            for (float[] f : a.waterFlow)
                if (px >= f[0] - 20f && px <= f[0] + f[2] + 20f && py >= f[1] - 20f && py <= f[1] + f[3] + 20f) return false;
            for (float[] r : a.riverPaths)
                if (nearPath(r, px, py, r[0] * 0.5f + 22f)) return false;
            for (MapDb.Terrace t : a.terraces)
                if (t.top(px, py) || t.stairs(px, py) || (px >= t.x - 12 && px <= t.x + t.w + 12 && py >= t.y - 12 && py <= t.stairEnd() + 12)) return false;
        }
        return true;
    }

    /** Distance test from a point to a river centre line {width, speed, x0, y0, ...}. */
    static boolean nearPath(float[] r, float x, float y, float d) {
        for (int i = 2; i + 3 < r.length; i += 2) {
            float ax = r[i], ay = r[i + 1], bx = r[i + 2], by = r[i + 3];
            float vx = bx - ax, vy = by - ay, l2 = vx * vx + vy * vy;
            float t = l2 <= 0f ? 0f : Math.max(0f, Math.min(1f, ((x - ax) * vx + (y - ay) * vy) / l2));
            float qx = ax + vx * t - x, qy = ay + vy * t - y;
            if (qx * qx + qy * qy <= d * d) return true;
        }
        return false;
    }

    /** True when a foot position stands inside any puddle (used for splash steps). */
    public static boolean inPuddle(List<float[]> puddles, float x, float y) {
        for (float[] q : puddles) {
            float rx = PUDDLE_SIZES[(int) q[2]][0], ry = PUDDLE_SIZES[(int) q[2]][1];
            float dx = (x - q[0]) / rx, dy = (y - q[1]) / ry;
            if (dx * dx + dy * dy <= 1f) return true;
        }
        return false;
    }
}
