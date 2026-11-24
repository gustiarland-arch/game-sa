package com.arlandsofia.olu;

import com.arlandsofia.olu.logic.MapDb;
import com.arlandsofia.olu.logic.SoundscapePlan;
import com.arlandsofia.olu.logic.WeatherFxV54;
import java.awt.image.BufferedImage;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import javax.imageio.ImageIO;

/**
 * v5.4 weather/water regression (headless): storm flash safety and thunder timing,
 * puddle placement on every outdoor map, wetness, flowing-water data and assets.
 * Does not replace an on-device look/listen check.
 */
public final class V54WeatherTest {
    private static int checks;
    private static final List<String> failures = new ArrayList<>();
    private static void yes(boolean ok, String msg) { checks++; if (!ok) failures.add(msg); }

    public static void main(String[] args) throws Exception {
        String root = args.length > 0 ? args[0] : "android/assets";
        MapDb db = new MapDb(new String(Files.readAllBytes(Paths.get(root, "data/maps.json")), StandardCharsets.UTF_8),
                new String(Files.readAllBytes(Paths.get(root, "data/props.json")), StandardCharsets.UTF_8));

        // ---- Storm: photosensitivity-safe flashes, thunder after every strike.
        float[] dts = {1f / 120f, 1f / 60f, 1f / 30f, 1f / 15f};
        for (float dt : dts) for (long seed = 1; seed <= 6; seed++) {
            WeatherFxV54.Storm s = new WeatherFxV54.Storm(seed * 7919L);
            List<Float> onsets = new ArrayList<>();
            List<Float> strikeTimes = new ArrayList<>();
            boolean lit = false; float maxA = 0f; int thunders = 0, lastStrikes = 0;
            float lastStrike = -1f;
            for (float t = 0f; t < 600f; t += dt) {
                s.update(dt, true);
                if (s.strikes() != lastStrikes) { lastStrikes = s.strikes(); strikeTimes.add(t); lastStrike = t; }
                float a = s.flashAlpha(2);
                maxA = Math.max(maxA, a);
                boolean on = a > 0.02f;
                if (on && !lit) onsets.add(t);
                lit = on;
                float th = s.consumeThunder();
                if (th > 0f) {
                    thunders++;
                    yes(th <= 1f && th >= 0.4f, "thunder volume in range " + th);
                    float delay = t - lastStrike;
                    yes(delay >= 0.3f && delay <= 2.4f, "thunder follows flash within 0.3-2.4 s (" + delay + ")");
                }
            }
            yes(maxA <= WeatherFxV54.FLASH_PEAK + 1e-4f, "flash peak capped (" + maxA + ")");
            yes(maxA > 0.1f, "flash visible at dt=" + dt);
            yes(strikeTimes.size() >= 600f / WeatherFxV54.MAX_GAP - 1 && strikeTimes.size() <= 600f / WeatherFxV54.MIN_GAP + 1,
                    "strike count plausible " + strikeTimes.size());
            yes(thunders == strikeTimes.size() || thunders == strikeTimes.size() - 1, "one thunder per strike " + thunders + "/" + strikeTimes.size());
            for (int i = 1; i < strikeTimes.size(); i++)
                yes(strikeTimes.get(i) - strikeTimes.get(i - 1) >= WeatherFxV54.MIN_GAP - dt, "strike spacing >= MIN_GAP");
            for (int i = 0; i < onsets.size(); i++) {
                int inWindow = 0;
                for (int j = i; j < onsets.size() && onsets.get(j) - onsets.get(i) < 1f; j++) inWindow++;
                yes(inWindow <= 3, "no more than 3 flashes per second (WCAG 2.3.1) at dt=" + dt);
            }
            // Inactive storms schedule nothing and leave no flash behind.
            WeatherFxV54.Storm quiet = new WeatherFxV54.Storm(seed);
            for (float t = 0f; t < 120f; t += dt) quiet.update(dt, false);
            yes(quiet.strikes() == 0 && quiet.flashAlpha(2) == 0f, "no lightning when inactive");
        }
        yes(WeatherFxV54.envelope(-1f) == 0f && WeatherFxV54.envelope(WeatherFxV54.FLASH_LEN + .01f) == 0f, "envelope bounded");
        yes(WeatherFxV54.envelope(0.2f) == 0f, "dark gap between the two pulses");
        yes(new WeatherFxV54.Storm(3).flashAlpha(0) <= new WeatherFxV54.Storm(3).flashAlpha(2), "quality 0 never brighter");

        // ---- Where storms happen.
        yes(WeatherFxV54.stormAllowed("riverside", true, false, false), "storm outdoors in rain");
        yes(!WeatherFxV54.stormAllowed("riverside", false, false, false), "no storm without rain");
        yes(!WeatherFxV54.stormAllowed("cafe", true, true, false), "no lightning indoors");
        yes(!WeatherFxV54.stormAllowed("memory_garden", true, false, true), "no lightning in memory realm");
        yes(!WeatherFxV54.stormAllowed("rain_garden", true, false, false), "rain garden stays calm");

        // ---- Wetness.
        float w = 0f;
        for (int i = 0; i < 60 * 60; i++) w = WeatherFxV54.wetness(w, 1f / 60f, true);
        yes(w == 1f, "ground soaks within a minute");
        for (int i = 0; i < 60 * 60; i++) w = WeatherFxV54.wetness(w, 1f / 60f, false);
        yes(w > 0f && w < 1f, "ground dries slowly");
        for (int i = 0; i < 60 * 120; i++) w = WeatherFxV54.wetness(w, 1f / 60f, false);
        yes(w == 0f, "ground fully dry after rain");

        // ---- Puddles on every map.
        int outdoor = 0, total = 0;
        for (MapDb.Area a : db.areas.values()) {
            List<float[]> p = WeatherFxV54.puddles(a);
            List<float[]> again = WeatherFxV54.puddles(a);
            if (a.indoor) { yes(p.isEmpty(), a.id + ": no puddles indoors"); continue; }
            outdoor++; total += p.size();
            yes(p.size() >= 3, a.id + ": at least 3 puddles (" + p.size() + ")");
            yes(p.size() <= 16, a.id + ": puddle budget");
            yes(p.size() == again.size(), a.id + ": deterministic layout");
            for (int i = 0; i < p.size(); i++) {
                float[] q = p.get(i);
                yes(q[0] == again.get(i)[0] && q[1] == again.get(i)[1], a.id + ": deterministic position");
                int[] sz = WeatherFxV54.PUDDLE_SIZES[(int) q[2]];
                for (float u = -1f; u <= 1f; u += .25f) for (float v = -1f; v <= 1f; v += .25f) {
                    if (u * u + v * v > 1f) continue;
                    float x = q[0] + u * sz[0], y = q[1] + v * sz[1];
                    yes(!a.blocked(x, y), a.id + ": puddle overlaps a collider at " + x + "," + y);
                    for (MapDb.Terrace t : a.terraces) yes(!t.top(x, y) && !t.stairs(x, y), a.id + ": puddle on terrace/stairs");
                    for (float[] wa : a.water) {
                        float dx = (x - wa[0]) / wa[2], dy = (y - wa[1]) / wa[3];
                        yes(dx * dx + dy * dy > 1f, a.id + ": puddle inside water");
                    }
                }
                yes(WeatherFxV54.inPuddle(p, q[0], q[1]), a.id + ": centre is inside its puddle");
            }
            yes(!WeatherFxV54.inPuddle(p, -500f, -500f), a.id + ": far point not in puddle");
        }
        yes(outdoor >= 15, "outdoor maps found " + outdoor);

        // ---- Flowing water data.
        MapDb.Area river = db.area("riverside"), dock = db.area("dermaga"), forest = db.area("hutan_bisik");
        yes(river != null && river.waterFlow.size() == 1, "riverside lake current");
        yes(dock != null && dock.waterFlow.size() == 1, "dermaga lake drift");
        yes(forest != null && forest.riverPaths.size() == 1, "forest river path");
        for (MapDb.Area a : db.areas.values()) {
            for (float[] f : a.waterFlow) {
                yes(f[0] >= 0 && f[1] >= 0 && f[0] + f[2] <= a.w + .5f && f[1] + f[3] <= a.h + .5f, a.id + ": flow band inside map");
                yes(f[5] > 0f && f[5] <= 80f, a.id + ": flow speed sane");
            }
            for (float[] r : a.riverPaths) {
                yes(r.length >= 6 && r[0] > 10f && r[1] > 0f, a.id + ": river definition");
                for (int i = 2; i + 1 < r.length; i += 2)
                    yes(r[i] >= 0 && r[i] <= a.w && r[i + 1] >= 0 && r[i + 1] <= a.h, a.id + ": river point inside map");
            }
        }
        // The forest river path must run over painted water (blue) in the map image.
        BufferedImage fmap = ImageIO.read(new File(root, "maps/hutan_bisik.png"));
        float[] fr = forest.riverPaths.get(0);
        int onWater = 0, samples = 0;
        for (int i = 2; i + 3 < fr.length; i += 2)
            for (float t = 0f; t < 1f; t += .1f) {
                int x = Math.round(fr[i] + (fr[i + 2] - fr[i]) * t), y = Math.round(fr[i + 1] + (fr[i + 3] - fr[i + 1]) * t);
                if (y >= fmap.getHeight()) continue;
                int rgb = fmap.getRGB(x, y), r = rgb >> 16 & 255, b = rgb & 255;
                samples++; if (b > r + 50 && b > 140) onWater++;
            }
        yes(onWater >= samples * 0.95f, "forest river path follows painted water " + onWater + "/" + samples);

        // ---- Assets.
        for (int i = 0; i < WeatherFxV54.PUDDLE_SIZES.length; i++) {
            BufferedImage img = ImageIO.read(new File(root, "fx/v54_puddle_" + i + ".png"));
            yes(img != null && img.getWidth() == WeatherFxV54.PUDDLE_SIZES[i][0] * 2 && img.getHeight() == WeatherFxV54.PUDDLE_SIZES[i][1] * 2,
                    "puddle texture " + i + " matches PUDDLE_SIZES");
        }
        for (String id : new String[]{"v54_thunder", "v54_step_puddle"}) {
            yes(SoundscapePlan.contains(SoundscapePlan.SFX, id), id + " registered");
            File f = new File(root, "audio/sfx/" + id + ".wav");
            yes(f.isFile() && f.length() > 2000, id + ".wav present");
        }

        if (!failures.isEmpty()) {
            for (String f : failures.subList(0, Math.min(40, failures.size()))) System.out.println("FAIL " + f);
            System.out.println(failures.size() + " of " + checks + " weather checks failed");
            System.exit(1);
        }
        System.out.println("V5.4 weather OK: " + outdoor + " outdoor maps, " + total + " puddles, " + checks + " checks");
    }
}
