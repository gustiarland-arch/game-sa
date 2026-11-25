package shot;

import com.arlandsofia.olu.AudioManager;
import com.arlandsofia.olu.OluGame;
import com.arlandsofia.olu.game.Actor;
import com.arlandsofia.olu.logic.Progress;
import com.arlandsofia.olu.screens.GameScreen;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.InputProcessor;
import com.badlogic.gdx.backends.lwjgl3.Lwjgl3Application;
import com.badlogic.gdx.backends.lwjgl3.Lwjgl3ApplicationConfiguration;
import com.badlogic.gdx.graphics.Pixmap;
import com.badlogic.gdx.graphics.PixmapIO;
import com.badlogic.gdx.utils.ScreenUtils;
import java.io.*;
import java.lang.reflect.Field;
import java.util.*;

/**
 * Desktop capture harness (not shipped): runs the real OluGame/GameScreen at a fixed
 * 30 fps timestep, drives the floating joystick through the screen's own InputProcessor
 * toward waypoints, pipes every frame to ffmpeg and logs every audio cue the game plays.
 */
public final class DeskVideo extends OluGame {
    static final int FPS = 30;
    static String OUT; static int DAY; static String STEP; static boolean STILLS, GOLDEN;
    // name, route, area, x, y, minute, seconds, waypoints "x:y;x:y"
    static String[][] SEGS;
    OutputStream ff; PrintWriter alog;
    int frame, seg = -1, segFrame, wp; float[][] pts; boolean touching;
    Field playerF; float[] aim; int stuck, onWp; float lastX, lastY;

    @Override public void create() {
        super.create();
        try {
            alog = new PrintWriter(new FileWriter(OUT + "/audio.tsv"));
            AudioManager.tap = (bus, id, v) -> alog.println(frame + "\t" + bus + "\t" + id + "\t" + v);
            if (!STILLS) {
                ProcessBuilder pb = new ProcessBuilder("ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
                        "-s", Gdx.graphics.getBackBufferWidth() + "x" + Gdx.graphics.getBackBufferHeight(), "-r", "" + FPS, "-i", "-",
                        "-vf", "vflip,scale=1280:-2:flags=neighbor", "-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
                        "-pix_fmt", "yuv420p", OUT + "/video.mp4");
                pb.redirectErrorStream(true); pb.redirectOutput(ProcessBuilder.Redirect.INHERIT);
                ff = new BufferedOutputStream(pb.start().getOutputStream(), 1 << 22);
            }
            playerF = GameScreen.class.getDeclaredField("player"); playerF.setAccessible(true);
        } catch (Exception e) { throw new RuntimeException(e); }
        next();
    }

    void next() {
        seg++; segFrame = 0; wp = 0; touching = false; aim = null; stuck = 0;
        if (seg >= SEGS.length) { finish(); return; }
        String[] s = SEGS[seg];
        alog.println(frame + "\tsegment\t" + s[0] + "\t0");
        Progress p = Progress.newGame(s[1], 1, STEP, maps.area(s[2]));
        com.arlandsofia.olu.logic.MapDb.Area ar = maps.area(s[2]);
        p.area = s[2]; p.x = s[3].equals("-") ? ar.spawnX : Float.parseFloat(s[3]); p.y = s[4].equals("-") ? ar.spawnY : Float.parseFloat(s[4]);
        p.minute = Integer.parseInt(s[5]); p.day = s.length > 8 ? Integer.parseInt(s[8]) : DAY; p.dir = "right"; p.companion = true;
        String[] w = s[7].isEmpty() ? new String[0] : s[7].split(";");
        pts = new float[w.length][];
        for (int i = 0; i < w.length; i++) { String[] xy = w[i].split(":"); pts[i] = new float[]{Float.parseFloat(xy[0]), Float.parseFloat(xy[1])}; }
        if (pts.length > 1) {
            java.util.List<float[]> pd = com.arlandsofia.olu.logic.WeatherFxV54.puddles(maps.area(s[2]));
            float[] best = null; float bd = 1e9f;
            for (float[] q : pd) { float d = Math.abs(q[0] - pts[0][0]) + Math.abs(q[1] - pts[0][1]); if (d < bd) { bd = d; best = q; } }
            if (best != null && bd < 700f) {
                float[][] np = new float[pts.length + 1][];
                np[0] = pts[0]; np[1] = new float[]{best[0], best[1]};
                System.arraycopy(pts, 1, np, 2, pts.length - 1); pts = np;
                System.out.println("PUDDLE " + s[0] + " " + best[0] + "," + best[1]);
            }
        }
        com.badlogic.gdx.math.MathUtils.random.setSeed(4242L + seg);
        switchScreen(new GameScreen(this, p, false, false));
    }

    void finish() {
        try { alog.close(); if (ff != null) ff.close(); } catch (IOException ignored) {}
        Gdx.app.exit();
    }

    void drive() {
        InputProcessor in = Gdx.input.getInputProcessor();
        if (in == null || !(getScreen() instanceof GameScreen)) return;
        Actor pl;
        try { pl = (Actor) playerF.get(getScreen()); } catch (Exception e) { return; }
        if (segFrame % 30 == 0) System.out.println("POS " + SEGS[seg][0] + " f" + segFrame + " wp" + wp + " " + (int) pl.x + "," + (int) pl.y);
        int H = Gdx.graphics.getHeight();
        float jx = 230, jy = H - 190;
        if (segFrame < 20 || wp >= pts.length) { if (touching) { in.touchUp((int) jx, (int) jy, 0, 0); touching = false; } return; }
        float tx = pts[wp][0], ty = pts[wp][1];
        float gx = tx - pl.x, gy = ty - pl.y;
        if (gx * gx + gy * gy < 10f * 10f || ++onWp > 150) { wp++; stuck = 0; onWp = 0; return; }
        if (segFrame % 6 == 0 || aim == null) {
            com.arlandsofia.olu.logic.QuestPathV52.Result r = com.arlandsofia.olu.logic.QuestPathV52.route(maps.area(SEGS[seg][2]), pl.x, pl.y, tx, ty, 14f);
            aim = r.found ? new float[]{r.nextX, r.nextY} : new float[]{tx, ty};
        }
        float dx = aim[0] - pl.x, dy = aim[1] - pl.y, d = (float) Math.sqrt(dx * dx + dy * dy);
        if (d < 2f) { dx = gx; dy = gy; d = (float) Math.sqrt(dx * dx + dy * dy); }
        if (Math.abs(pl.x - lastX) + Math.abs(pl.y - lastY) < 0.2f) { if (++stuck > 75) { wp++; stuck = 0; } } else stuck = 0;
        lastX = pl.x; lastY = pl.y;
        if (!touching) { in.touchDown((int) jx, (int) jy, 0, 0); touching = true; }
        in.touchDragged((int) (jx + dx / d * 70f), (int) (jy + dy / d * 70f), 0);
    }

    @Override public void render() {
        if (seg >= SEGS.length) return;
        drive();
        if (segFrame == 20 && SEGS[seg].length > 9 && !SEGS[seg][9].isEmpty() && getScreen() instanceof GameScreen) {
            String[] sp = SEGS[seg][9].split("@"); // optional 10th column: SCENE_ID@lineIndex shows that dialogue line
            try {
                java.lang.reflect.Method m = GameScreen.class.getDeclaredMethod("playScenePart", String.class, int.class, int.class, Runnable.class);
                m.setAccessible(true); m.invoke(getScreen(), sp[0], sp.length > 1 ? Integer.parseInt(sp[1]) : 0, 1, null);
            } catch (Exception e) { throw new RuntimeException(e); }
        }
        if (getScreen() != null) getScreen().render(1f / FPS);
        int w = Gdx.graphics.getBackBufferWidth(), h = Gdx.graphics.getBackBufferHeight();
        if (!STILLS && segFrame >= 6) { // skip the first frames of a fresh scene (loading)
            byte[] px = ScreenUtils.getFrameBufferPixels(0, 0, w, h, false);
            try { ff.write(px); } catch (IOException e) { throw new RuntimeException(e); }
            frame++;
        }
        if (STILLS && (GOLDEN ? (segFrame == 45 || segFrame == 150 || segFrame == 300) : (segFrame == 90 || segFrame == 200))) {
            Pixmap pm = Pixmap.createFromFrameBuffer(0, 0, w, h);
            Pixmap fl = new Pixmap(w, h, Pixmap.Format.RGBA8888);
            for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) fl.drawPixel(x, h - 1 - y, pm.getPixel(x, y) | 0xff);
            PixmapIO.writePNG(Gdx.files.absolute(OUT + "/" + SEGS[seg][0] + "_" + segFrame + ".png"), fl);
            pm.dispose(); fl.dispose();
        }
        segFrame++;
        if (segFrame >= Float.parseFloat(SEGS[seg][6]) * FPS + 6) next();
    }

    public static void main(String[] a) {
        OUT = a[0]; STEP = a[1]; DAY = Integer.parseInt(a[2]); STILLS = a.length > 3 && ("stills".equals(a[3]) || "golden".equals(a[3])); GOLDEN = a.length > 3 && "golden".equals(a[3]);
        SEGS = new String[][]{
            {"tepi_danau", "sofia", "riverside", "260", "640", "1050", "17", "600:700;1000:700;1400:690"},
            {"plaza", "sofia", "plaza", "700", "930", "990", "15", "830:900;1100:900;1180:780;1100:700"},
            {"hutan_air_terjun", "arland", "hutan_bisik", "1700", "330", "960", "13", "1830:250;1820:520;1840:800"},
            {"dermaga", "arland", "dermaga", "200", "440", "1080", "15", "700:470;979:380;979:300"},
        };
        if (a.length > 4 && ("tour".equals(a[3]) || "video".equals(a[3]))) {
            STILLS = !"video".equals(a[3]); GOLDEN = STILLS; // "video": same segment file, encoded to video.mp4
            try {
                java.util.List<String[]> rows = new java.util.ArrayList<>();
                for (String ln : java.nio.file.Files.readAllLines(java.nio.file.Paths.get(a[4]))) if (!ln.isBlank()) rows.add(ln.split("\\|", -1));
                SEGS = rows.toArray(new String[0][]);
            } catch (java.io.IOException e) { throw new RuntimeException(e); }
        } else if (GOLDEN) {
            String[][] extra = {
                {"g_kamar_arland", "arland", "arland_room", "-", "-", "540", "11", "", "3"},
                {"g_kamar_sofia", "sofia", "sofia_room", "-", "-", "1260", "11", "", "3"},
                {"g_cafe", "sofia", "cafe", "-", "-", "600", "11", "", "3"},
                {"g_gua", "arland", "gua_kristal", "-", "-", "800", "11", "", "3"},
                {"g_bukit_malam", "sofia", "bukit_bintang", "-", "-", "1290", "11", "", "3"},
                {"g_taman_cerah", "arland", "taman_kota", "-", "-", "600", "11", "", "3"},
            };
            String[][] all = new String[SEGS.length + extra.length][];
            System.arraycopy(SEGS, 0, all, 0, SEGS.length); System.arraycopy(extra, 0, all, SEGS.length, extra.length);
            SEGS = all;
        }
        Lwjgl3ApplicationConfiguration c = new Lwjgl3ApplicationConfiguration();
        c.setTitle("olu-video"); c.setWindowedMode(1600, 720); c.useVsync(false); c.setForegroundFPS(0);
        c.disableAudio(true);
        new Lwjgl3Application(new DeskVideo(), c);
    }
}
