package com.arlandsofia.olu;

import com.arlandsofia.olu.logic.ElevationV50;
import com.arlandsofia.olu.logic.MapDb;
import com.arlandsofia.olu.logic.QuestPathV52;
import com.arlandsofia.olu.logic.WorldNavigationV52;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

/**
 * v5.4 stair and elevation regression. Simulates the exact axis-separated movement
 * rule used by GameScreen.move() (swept foot collision + ElevationV50.canStep) on
 * every real terrace in maps.json: ascend, descend, stop/turn midway, side railings,
 * cliff edges, varied frame delta, A* routing up/down, and terrain lift continuity.
 * Headless: does not replace an on-device playtest.
 */
public final class V54StairTraversalTest {
    private static int checks;
    private static final List<String> failures = new ArrayList<>();
    private static void yes(boolean ok, String msg) { checks++; if (!ok) failures.add(msg); }

    static final float WALK = 112f;
    static final float[] DTS = {1f / 120f, 1f / 60f, 1f / 30f, 1f / 20f};

    /** Mirrors GameScreen.move(): x then y, each swept and elevation-checked. */
    static float[] step(MapDb.Area a, WorldNavigationV52.Collision c, float x, float y, float dx, float dy, float dt) {
        float len = (float) Math.sqrt(dx * dx + dy * dy);
        if (len < 0.01f) return new float[]{x, y};
        dx /= len; dy /= len;
        float speed = WALK * dt * ElevationV50.speedFactor(a.terraces, x, y);
        float nx = x + dx * speed;
        if (WorldNavigationV52.clearSegment(c, x, y, nx, y) && ElevationV50.canStep(a.terraces, x, y, nx, y)) x = nx;
        float ny = y + dy * speed;
        if (WorldNavigationV52.clearSegment(c, x, y, x, ny) && ElevationV50.canStep(a.terraces, x, y, x, ny)) y = ny;
        return new float[]{x, y};
    }

    static float[] walk(MapDb.Area a, WorldNavigationV52.Collision c, float x, float y, float dx, float dy, float dt, float seconds) {
        float[] p = {x, y};
        for (float t = 0; t < seconds; t += dt) p = step(a, c, p[0], p[1], dx, dy, dt);
        return p;
    }

    static boolean onLevel(MapDb.Terrace t, float x, float y) { return t.top(x, y) && !t.stairs(x, y); }

    public static void main(String[] args) throws Exception {
        String root = args.length > 0 ? args[0] : "android/assets";
        String maps = new String(Files.readAllBytes(Paths.get(root, "data/maps.json")), StandardCharsets.UTF_8);
        String props = new String(Files.readAllBytes(Paths.get(root, "data/props.json")), StandardCharsets.UTF_8);
        MapDb db = new MapDb(maps, props);
        int terraces = 0;
        for (final MapDb.Area a : db.areas.values()) {
            WorldNavigationV52.Collision c = new WorldNavigationV52.Collision() {
                public boolean blocked(float x, float y) { return a.blocked(x, y); }
            };
            for (MapDb.Terrace t : a.terraces) {
                terraces++;
                String id = a.id + "/" + t.id;
                float cx = t.stairX() + t.stairWidth * .5f;
                float bottomY = t.stairEnd() + 18f;
                float topY = t.y + t.h * .5f;
                yes(!a.blocked(cx, bottomY), id + ": stair foot approach blocked by collision");
                yes(!a.blocked(cx, topY), id + ": platform centre blocked by collision");
                // Whole stair corridor and platform must be free of ground-level colliders.
                for (float sy = t.stairStart() + 2; sy <= t.stairEnd(); sy += 6)
                    yes(!a.blocked(cx, sy), id + ": ground collider inside stair corridor at y=" + sy);

                // 1-2,7: ascend/descend across the full stair width, with varied frame delta.
                for (float dt : DTS) {
                    for (float off = 3f; off <= t.stairWidth - 3f; off += 4f) {
                        float sx = t.stairX() + off;
                        if (a.blocked(sx, bottomY)) continue;
                        float[] up = walk(a, c, sx, bottomY, 0, -1, dt, 4f);
                        yes(onLevel(t, up[0], up[1]), id + ": ascend stuck from x+" + off + " dt=" + dt + " at " + up[0] + "," + up[1]);
                        float[] down = walk(a, c, up[0], up[1], 0, 1, dt, 4f);
                        yes(down[1] > t.stairEnd(), id + ": descend stuck from x+" + off + " dt=" + dt + " at " + down[0] + "," + down[1]);
                    }
                    // Descend starting anywhere along the platform lip that is inside the stair mouth.
                    for (float off = 1f; off <= t.stairWidth - 1f; off += 3f) {
                        float sx = t.stairX() + off;
                        float[] down = walk(a, c, sx, t.y + t.h - 14f, 0, 1, dt, 4f);
                        yes(down[1] > t.stairEnd(), id + ": descend from lip stuck at x+" + off + " dt=" + dt + " -> " + down[0] + "," + down[1]);
                    }
                }
                // 3-4: stop midway and turn around.
                float[] mid = walk(a, c, cx, bottomY, 0, -1, 1f / 60f, (bottomY - (t.stairStart() + t.stairLength * .5f)) / WALK);
                yes(t.stairs(mid[0], mid[1]), id + ": midway stop not on stairs");
                float[] back = walk(a, c, mid[0], mid[1], 0, 1, 1f / 60f, 3f);
                yes(back[1] > t.stairEnd(), id + ": turn back from midway failed");
                // 5: railings — pushing sideways at mid height must not leave the stair.
                float[] sideL = walk(a, c, mid[0], mid[1], -1, 0, 1f / 60f, 2f);
                float[] sideR = walk(a, c, mid[0], mid[1], 1, 0, 1f / 60f, 2f);
                yes(t.stairs(sideL[0], sideL[1]) && t.stairs(sideR[0], sideR[1]), id + ": walked through stair railing");
                // Diagonal touch input should still climb (touch joystick rarely points straight up).
                float[] diag = walk(a, c, cx - 10f, bottomY, .35f, -1f, 1f / 60f, 4f);
                yes(onLevel(t, diag[0], diag[1]) || t.top(diag[0], diag[1]), id + ": diagonal ascend failed " + diag[0] + "," + diag[1]);
                // Cliff: walking off the platform edge away from the stair must be blocked.
                float edgeX = t.x + 8f;
                float[] cliff = walk(a, c, edgeX, topY, 0, 1, 1f / 60f, 3f);
                yes(t.top(cliff[0], cliff[1]), id + ": fell off platform south edge");
                float[] west = walk(a, c, t.x + t.w * .5f, topY, -1, 0, 1f / 60f, 4f);
                yes(t.top(west[0], west[1]), id + ": walked off platform west edge");
                float[] north = walk(a, c, t.x + t.w * .5f, topY, 0, -1, 1f / 60f, 4f);
                yes(t.top(north[0], north[1]), id + ": walked off platform north edge");
                // Lift must be monotone up the stairs and continuous at the lip (no pop).
                float prev = -1f;
                for (float sy = t.stairEnd(); sy >= t.y + t.h - 12f; sy -= 1f) {
                    float hgt = ElevationV50.heightAt(a.terraces, cx, sy);
                    yes(hgt + 0.001f >= prev, id + ": lift not monotone at y=" + sy);
                    yes(prev < 0 || hgt - prev <= t.rise / 20f + .01f, id + ": lift pops at y=" + sy + " (" + prev + "->" + hgt + ")");
                    prev = hgt;
                }
                // A*: routes up and down through the stair.
                QuestPathV52.Result r1 = QuestPathV52.route(a, cx, bottomY, t.x + t.w * .5f, topY, 24f);
                yes(r1.found, id + ": A* cannot route to platform");
                QuestPathV52.Result r2 = QuestPathV52.route(a, t.x + t.w * .5f, topY, cx, bottomY, 24f);
                yes(r2.found, id + ": A* cannot route down from platform");
            }
        }
        yes(terraces == 0, "v6 removed the stair platforms; found " + terraces);
        // Stair pace: slower on stairs, unchanged on flat ground.
        yes(ElevationV50.STAIR_SPEED_FACTOR > .6f && ElevationV50.STAIR_SPEED_FACTOR < 1f, "stair pace factor sane");
        // Pixel-perfect camera: whole pixels per world unit, nearest to requested framing.
        float[][] screens = {{2400, 1080}, {1920, 1080}, {1600, 720}, {2560, 1600}, {1280, 800}, {854, 480}, {3200, 1440}};
        for (float[] sc : screens) for (float framing : new float[]{1.02f, 1.2f, 1.254f, 1.4f, 1.463f}) {
            float worldH = 428f;
            int k = com.arlandsofia.olu.logic.PixelPerfectV54.pixelsPerUnit(framing, worldH, sc[1]);
            float z = com.arlandsofia.olu.logic.PixelPerfectV54.zoom(framing, worldH, sc[1]);
            float ppu = sc[1] / (worldH * z);
            yes(k >= 1 && Math.abs(ppu - k) < 1e-3f, "integer pixels per unit " + sc[1] + " framing " + framing + " -> " + ppu);
            float raw = sc[1] / (worldH * framing);
            yes(Math.abs(k - raw) <= .5001f || k == 1, "nearest integer scale " + raw + " -> " + k);
            float snapped = com.arlandsofia.olu.logic.PixelPerfectV54.snap(1234.567f, k);
            yes(Math.abs(snapped * k - Math.round(snapped * k)) < 1e-3f, "camera on screen-pixel grid");
        }
        yes(com.arlandsofia.olu.logic.PixelPerfectV54.zoom(0f, 428f, 1080f) == 1f, "degenerate framing safe");
        com.arlandsofia.olu.logic.Settings fresh = new com.arlandsofia.olu.logic.Settings();
        yes(fresh.pixelPerfect, "pixel-perfect default on");
        java.util.Map<String, Object> legacy = new java.util.HashMap<>();
        yes(com.arlandsofia.olu.logic.Settings.fromMap(legacy).pixelPerfect, "older settings migrate to pixel-perfect on");
        fresh.pixelPerfect = false;
        yes(!com.arlandsofia.olu.logic.Settings.fromMap(fresh.toMap()).pixelPerfect, "pixel-perfect off persists");
        if (!failures.isEmpty()) {
            for (String f : failures.subList(0, failures.size())) System.out.println("FAIL " + f);
            System.out.println(failures.size() + " of " + checks + " stair checks failed");
            System.exit(1);
        }
        System.out.println("V5.4 stair traversal OK: " + terraces + " terraces, " + checks + " checks");
    }
}
