package com.arlandsofia.olu.logic;

/**
 * v5.4 pixel-perfect exploration camera. Map, prop and character art are authored
 * on a 1-world-unit texel grid and sampled with nearest filtering. When one world
 * unit covers a non-integer number of screen pixels (e.g. 2.52 px), neighbouring
 * texels render 2 or 3 px wide and the pattern crawls while the camera moves
 * ("shimmer"). This picks the closest zoom whose scale is a whole number of screen
 * pixels per world unit and snaps the camera to the screen-pixel grid.
 * Pure Java so it can be tested headless. Cutscene framing is not changed.
 */
public final class PixelPerfectV54 {
    private PixelPerfectV54() {}

    /** Whole screen pixels per world unit nearest to the requested framing. */
    public static int pixelsPerUnit(float framing, float viewportWorldH, float screenH) {
        if (!(framing > 0f) || !(viewportWorldH > 0f) || !(screenH > 0f)) return 1;
        float raw = screenH / (viewportWorldH * framing);
        return Math.max(1, Math.round(raw));
    }

    /** Camera zoom that yields exactly {@link #pixelsPerUnit} screen pixels per world unit. */
    public static float zoom(float framing, float viewportWorldH, float screenH) {
        if (!(framing > 0f) || !(viewportWorldH > 0f) || !(screenH > 0f)) return framing > 0f ? framing : 1f;
        int k = pixelsPerUnit(framing, viewportWorldH, screenH);
        return screenH / (viewportWorldH * k);
    }

    /** Snap a camera coordinate to the screen-pixel grid for a given pixels-per-unit. */
    public static float snap(float v, int pixelsPerUnit) {
        if (pixelsPerUnit <= 0 || !Float.isFinite(v)) return v;
        return Math.round(v * pixelsPerUnit) / (float) pixelsPerUnit;
    }
}
