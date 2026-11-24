package com.arlandsofia.olu.logic;

/**
 * Kamera 2D tanpa dependensi grafis agar gerakan bisa diuji secara headless.
 * Posisi langsung disetel saat teleport/cutscene, sedangkan eksplorasi memakai
 * smoothing eksponensial independen framerate (tidak bergantung pada FPS).
 */
public final class CameraRig {
    private float x, y;
    private boolean initialized;

    public float x() { return x; }
    public float y() { return y; }
    public boolean ready() { return initialized; }
    public void reset() { initialized = false; }

    public void snap(float targetX, float targetY) {
        x = targetX;
        y = targetY;
        initialized = true;
    }

    public void follow(float targetX, float targetY, float dt, boolean smooth) {
        if (!initialized || !smooth || (Float.isNaN(dt) || Float.isInfinite(dt))) {
            snap(targetX, targetY);
            return;
        }
        float elapsed = Math.max(0f, Math.min(dt, 0.08f));
        float alpha = 1f - (float) Math.exp(-9.5f * elapsed);
        x += (targetX - x) * alpha;
        y += (targetY - y) * alpha;
        if (Math.abs(x - targetX) < 0.04f) x = targetX;
        if (Math.abs(y - targetY) < 0.04f) y = targetY;
    }
}
