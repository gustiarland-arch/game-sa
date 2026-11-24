package com.arlandsofia.olu.logic;

import java.util.List;

/** Petunjuk arah jarak dekat untuk interaksi quest yang sudah aktif, tanpa pathfinding palsu. */
public final class QuestCompass {
    private QuestCompass() {}
    public static final class Hint {
        public final String direction;
        public final int distance;
        public final String label;
        public final boolean reachable, detour;
        Hint(String direction, int distance, String label, boolean reachable) {
            this(direction,distance,label,reachable,false);
        }
        Hint(String direction, int distance, String label, boolean reachable, boolean detour) {
            this.direction = direction; this.distance = distance; this.label = label;
            this.reachable = reachable; this.detour = detour;
        }
        public String text() {
            return reachable ? "✦ Siap: " + label : detour
                    ? "✦ Jalur " + direction + " • " + distance + " langkah • " + label
                    : "✦ Arah " + direction + " • " + distance + " langkah • " + label;
        }
    }
    public static Hint nearest(float x, float y, List<QuestDb.Interactable> candidates, String route) {
        QuestDb.Interactable best = null;
        float bestSq = Float.POSITIVE_INFINITY;
        if (candidates == null) return null;
        for (QuestDb.Interactable candidate : candidates) {
            if (candidate == null || !candidate.forRoute(route)) continue;
            float dx = candidate.x - x, dy = candidate.y - y;
            float sq = dx * dx + dy * dy;
            if (sq < bestSq) { best = candidate; bestSq = sq; }
        }
        if (best == null) return null;
        float dx = best.x - x, dy = best.y - y;
        float dist = (float) Math.sqrt(bestSq);
        String direction = direction(dx, dy);
        // Dunia diukur dalam pixel; satu langkah perkiraan = 16 pixel.
        return new Hint(direction, Math.max(0, Math.round(dist / 16f)), best.label(route), dist <= best.r);
    }
    public static String direction(float dx, float dy) {
        if (Math.abs(dx) < 12f && Math.abs(dy) < 12f) return "dekat";
        String vertical = dy < -12f ? "Utara" : dy > 12f ? "Selatan" : "";
        String horizontal = dx > 12f ? "Timur" : dx < -12f ? "Barat" : "";
        if (!vertical.isEmpty() && !horizontal.isEmpty()) return vertical + "-" + horizontal;
        return !vertical.isEmpty() ? vertical : horizontal;
    }
}
