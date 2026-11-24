package com.arlandsofia.olu.logic;

/** Frame-rate-independent cinematic interpolation. Pure Java for deterministic tests. */
public final class CinematicMotionV463 {
    private CinematicMotionV463() {}
    public static float clamp(float v, float lo, float hi) {
        if (Float.isNaN(v)) return lo;
        return Math.max(lo, Math.min(hi, v));
    }
    public static float progress(float elapsed, float duration) {
        return duration <= 0f ? 1f : clamp(elapsed / duration, 0f, 1f);
    }
    /** Gentle start and end, suitable for quiet dialogue camera movement. */
    public static float ease(float k) {
        float t = clamp(k, 0f, 1f);
        return t * t * (3f - 2f * t);
    }
    public static float lerp(float from, float to, float k) {
        return from + (to - from) * clamp(k, 0f, 1f);
    }
    /** Consistent camera damping on low and high refresh-rate devices. */
    public static float damp(float speed, float dt) {
        return clamp(1f - (float)Math.exp(-Math.max(0f, speed) * clamp(dt, 0f, .1f)), 0f, 1f);
    }
    public static float presetZoom(String frame) {
        if ("close".equals(frame)) return 1.42f;
        if ("wide".equals(frame)) return .91f;
        if ("intimate".equals(frame)) return 1.18f;
        return 1.0f;
    }
    /** Clamp zoom to avoid framing outside map/cutscene and prevent NaN. */
    public static float safeZoom(float zoom) {
        return clamp(zoom, .67f, 1.5f);
    }
    public static float midpoint(float first, float second) {
        return first + (second - first) * .5f;
    }
}
