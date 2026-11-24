package com.arlandsofia.olu.logic;

/**
 * Rasio-aware layout rules for phones, landscape tablets and desktop-sized windows.
 * Pure Java, so every supported aspect can be tested without OpenGL/Android.
 * Values are in the existing 1280x720 ExtendViewport coordinate system.
 */
public final class AdaptiveLayoutV43 {
    private AdaptiveLayoutV43() {}
    public static final float DESIGN_W = 1280f, DESIGN_H = 720f;
    public static final float TAP_MIN = 60f;

    public static final class Metrics {
        public final float w, h, insetL, insetR, insetT, insetB;
        public final boolean tabletRatio;
        public final float centerX, centerY, contentLeft, contentRight, contentBottom, contentTop;
        private Metrics(float w, float h, float l, float r, float t, float b) {
            this.w = w; this.h = h;
            insetL = l; insetR = r; insetT = t; insetB = b;
            tabletRatio = w / h < 1.72f;
            centerX = w / 2f; centerY = h / 2f;
            contentLeft = l + 24f; contentRight = w - r - 24f;
            contentBottom = b + 20f; contentTop = h - t - 20f;
        }
    }
    public static Metrics of(float w, float h, float inL, float inR, float inT, float inB) {
        w = Math.max(320f, w); h = Math.max(180f, h);
        float l = clamp(inL, 0f, w / 4f), r = clamp(inR, 0f, w / 4f);
        float t = clamp(inT, 0f, h / 4f), b = clamp(inB, 0f, h / 4f);
        return new Metrics(w, h, l, r, t, b);
    }
    public static float clamp(float value,float min,float max) { return Math.max(min,Math.min(max,value)); }

    /** Center two route cards within the safe region, leaving room for heading/footer. */
    public static float cardBottom(Metrics m, float cardHeight) {
        float freeLow = m.contentBottom + 72f;
        float freeHigh = m.contentTop - 106f - cardHeight;
        return freeHigh >= freeLow ? (freeLow + freeHigh) / 2f : freeLow;
    }
    /** Dialog/menu rows must stay inside the physical viewport on 16:9 and 4:3. */
    public static float stackedMenuTop(Metrics m, int count, float rowHeight, float gap) {
        float total = count * rowHeight + Math.max(0, count - 1) * gap;
        float centered = m.centerY + total / 2f;
        return Math.min(m.contentTop - 90f, Math.max(m.contentBottom + total + 20f, centered));
    }
    public static float menuWidth(Metrics m, float target) {
        return Math.max(220f, Math.min(target, m.contentRight - m.contentLeft - 16f));
    }
    /** Interactive thumb controls should remain within safe borders, even with large scale. */
    public static float controlScale(Metrics m, float userScale) {
        float available = m.contentRight - m.contentLeft;
        return clamp(Math.min(userScale, available / 900f * 1.15f), .70f, 1.60f);
    }
}
