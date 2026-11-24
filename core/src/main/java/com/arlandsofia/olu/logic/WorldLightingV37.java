package com.arlandsofia.olu.logic;

/**
 * Pure, deterministic map-space contact shadow parameters. No GL allocations.
 * Does not affect collision, height sorting, interaction or save state.
 */
public final class WorldLightingV37 {
    private WorldLightingV37() {}

    /** Horizontal sunlight projected shadow (map units) with gentle sunrise/sunset bias. */
    public static float shadowOffsetX(int minute, boolean indoors, boolean rainy, int quality) {
        if (quality <= 0 || indoors || rainy || WorldClock.isNight(minute)) return 0f;
        int hour = WorldClock.hour(minute);
        return (12f - hour) * 1.6f;
    }

    /** The floor contact halo should remain understated, never obscure quest markers. */
    public static float contactOpacity(int minute, boolean indoors, boolean rainy, int quality) {
        if (quality <= 0) return 0f;
        if (indoors) return quality == 2 ? 0.38f : 0.28f;
        if (rainy) return quality == 2 ? 0.30f : 0.22f;
        if (WorldClock.isNight(minute)) return quality == 2 ? 0.44f : 0.30f;
        return quality == 2 ? 0.50f : 0.36f;
    }

    public static float width(float collisionWidth) {
        return Math.max(22f, Math.min(110f, collisionWidth * 1.3f));
    }
}
