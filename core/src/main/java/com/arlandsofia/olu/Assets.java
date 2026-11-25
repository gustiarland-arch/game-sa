package com.arlandsofia.olu;

import com.arlandsofia.olu.logic.MapDb;
import com.arlandsofia.olu.logic.MemoryBookDb;
import com.arlandsofia.olu.logic.QuestDb;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.audio.Sound;
import com.badlogic.gdx.files.FileHandle;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.BitmapFont;
import com.badlogic.gdx.graphics.g2d.NinePatch;
import com.badlogic.gdx.graphics.g2d.TextureRegion;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Semua aset dimuat dari folder assets lokal di dalam APK (android/assets). Tidak ada unduhan.
 * Aset hilang tidak membuat crash: diganti tekstur cadangan dan dicatat di log + daftar missing.
 */
public final class Assets {
    public static final String[] CHARACTERS = {"arland", "sofia"};
    /** Urutan baris sprite sheet: depan, kiri, kanan, belakang. */
    public static final int DIR_DOWN = 0, DIR_LEFT = 1, DIR_RIGHT = 2, DIR_UP = 3;
    public static final int FRAME_W = 48, FRAME_H = 72, FRAMES = 3;

    private final Map<String, Texture> textures = new HashMap<>();
    private final Map<String, TextureRegion[][]> sheets = new HashMap<>();
    private final Map<String, Sound> sounds = new HashMap<>();
    private final List<Texture> owned = new ArrayList<>();
    public final List<String> missing = new ArrayList<>();

    public BitmapFont body, title, label;
    public NinePatch panel, panelDark, button, buttonDown, buttonAccent, buttonDisabled;
    public Texture pixel;

    public void loadCore() {
        pixel = tex("ui/pixel.png");
        body = font("fonts/font_body", 0.5f);
        title = font("fonts/font_title", 0.5f);
        label = font("fonts/font_label", 0.5f);
        panel = patch("ui/v32_panel.png");
        panelDark = patch("ui/v32_panel_dark.png");
        button = patch("ui/v32_button.png");
        buttonDown = patch("ui/v32_button_down.png");
        buttonAccent = patch("ui/v32_button_accent.png");
        buttonDisabled = patch("ui/v32_button_disabled.png");
        for (String c : CHARACTERS) sheet(c);
        // Efek baru dimuat saat dibutuhkan: tidak menghabiskan puluhan Sound pool di awal.
    }

    /** Preload aset inti dan ikon kecil; prop dunia dimuat per area untuk mengurangi startup. */
    public void preload(MapDb maps, QuestDb quests, MemoryBookDb book) {
        // v2.9: Jangan buat seluruh tekstur prop dari 22 area saat boot.
        // Props dimuat saat pemain masuk area (warmArea), lalu dicache.
        for (QuestDb.Step s : quests.steps.values())
            for (QuestDb.Interactable it : s.interactables) if (it.sprite != null) tex(it.sprite.image);
        for (MemoryBookDb.Entry e : book.entries) tex(e.icon);
        for (MemoryBookDb.Item i : book.items.values()) tex(i.icon);
    }

    /** Hangatkan prop area aktif sebelum frame dunia pertama; tidak memuat peta lain. */
    public void warmArea(MapDb.Area area) {
        if (area == null) return;
        for (MapDb.Terrace terrace : area.terraces) { tex(terrace.image); tex(terrace.front); }
        for (MapDb.Tile tile : area.tiles) tex(tile.image);
        for (MapDb.Prop prop : area.props) {
            tex(prop.def.image);
            if (prop.alt != null) tex(prop.alt.image);
        }
    }

    // ------------------------------------------------------------ loader
    public Texture tex(String path) {
        Texture t = textures.get(path);
        if (t != null) return t;
        try {
            FileHandle fh = Gdx.files.internal(path);
            if (!fh.exists()) throw new IllegalStateException("tidak ada");
            boolean hd = MapDb_hd(path);
            t = new Texture(fh, hd);
            // v6: HD art is drawn below 1 screen pixel per texel on some screens -> smooth mipmapped sampling
            if (hd) t.setFilter(Texture.TextureFilter.MipMapLinearLinear, Texture.TextureFilter.Linear);
            else t.setFilter(Texture.TextureFilter.Nearest, Texture.TextureFilter.Nearest);
            owned.add(t);
        } catch (Exception e) {
            if (!missing.contains(path)) missing.add(path);
            Gdx.app.error("OLU", "Aset hilang: " + path);
            t = pixel != null && !"ui/pixel.png".equals(path) ? pixel : fallback();
        }
        textures.put(path, t);
        return t;
    }

    private static boolean MapDb_hd(String path) { return com.arlandsofia.olu.logic.MapDb.Assets_hd(path); }

    private Texture fallbackTex;
    private Texture fallback() {
        if (fallbackTex == null) {
            com.badlogic.gdx.graphics.Pixmap pm = new com.badlogic.gdx.graphics.Pixmap(4, 4, com.badlogic.gdx.graphics.Pixmap.Format.RGBA8888);
            pm.setColor(1f, 1f, 1f, 1f);
            pm.fill();
            fallbackTex = new Texture(pm);
            pm.dispose();
            owned.add(fallbackTex);
        }
        return fallbackTex;
    }

    /** Tekstur peta dimuat saat masuk area dan dilepas saat keluar (peta bisa 2048 px). */
    public Texture mapTex(String path) { return tex(path); }

    public void unloadMap(String path) {
        Texture t = textures.remove(path);
        if (t != null && t != pixel && t != fallbackTex) { owned.remove(t); t.dispose(); }
    }

    public boolean has(String path) { Texture t = tex(path); return !missing.contains(path) && t != null; }

    private BitmapFont font(String base, float scale) {
        BitmapFont f;
        try {
            Texture t = new Texture(Gdx.files.internal(base + ".png"), true);
            t.setFilter(Texture.TextureFilter.MipMapLinearLinear, Texture.TextureFilter.Linear);
            owned.add(t);
            f = new BitmapFont(Gdx.files.internal(base + ".fnt"), new TextureRegion(t), false);
        } catch (Exception e) {
            missing.add(base + ".fnt");
            Gdx.app.error("OLU", "Font gagal dimuat, memakai font bawaan: " + base);
            f = new BitmapFont();
            scale = 1.4f;
        }
        f.getData().setScale(scale);
        f.setUseIntegerPositions(false);
        f.getData().markupEnabled = false;
        return f;
    }

    private NinePatch patch(String path) {
        Texture t = tex(path);
        t.setFilter(Texture.TextureFilter.Linear, Texture.TextureFilter.Linear);
        if (t.getWidth() < 40) return new NinePatch(t, 1, 1, 1, 1);
        return new NinePatch(t, 18, 18, 18, 18);
    }

    public Texture uiTex(String path) {
        Texture t = tex(path);
        t.setFilter(Texture.TextureFilter.Linear, Texture.TextureFilter.Linear);
        return t;
    }

    /** v6: an HD sheet (same layout, frames 2x larger) is used when "<name>@2x.png" exists. */
    private static String hd(String path) {
        String h = path.replace(".png", "@2x.png");
        return Gdx.files.internal(h).exists() ? h : path;
    }
    private static int k(String path) { return path.contains("@2x") ? 2 : 1; }

    private void sheet(String c) {
        String sp = hd("characters/" + c + "/walk.png"); Texture t = tex(sp); int k = k(sp);
        TextureRegion[][] r = new TextureRegion[4][FRAMES];
        boolean ok = t.getWidth() >= FRAME_W*k * FRAMES && t.getHeight() >= FRAME_H*k * 4;
        for (int d = 0; d < 4; d++)
            for (int f = 0; f < FRAMES; f++)
                r[d][f] = ok ? new TextureRegion(t, f * FRAME_W*k, d * FRAME_H*k, FRAME_W*k, FRAME_H*k) : new TextureRegion(t);
        sheets.put(c, r);
    }

    public TextureRegion frame(String character, int dir, int frame) {
        TextureRegion[][] r = sheets.get(character);
        if (r == null) { sheet(character); r = sheets.get(character); }
        return r[Math.max(0, Math.min(3, dir))][Math.max(0, Math.min(FRAMES - 1, frame))];
    }

    /** v3.7: 16-frame atlas (fallback v3.2/legacy) di-load hanya ketika terlihat. */
    private final Map<String, TextureRegion[][]> walkPlusSheets = new HashMap<>();

    public TextureRegion walkFrame(String character, int dir, int phase) {
        TextureRegion[][] all = walkPlusSheets.get(character);
        if (all == null) {
            String path = "characters/" + character + "/walk_v53.png";
            if (!Gdx.files.internal(path).exists()) path = "characters/" + character + "/walk_v37.png";
            if (!Gdx.files.internal(path).exists()) path = "characters/" + character + "/walk_v32.png";
            if (!Gdx.files.internal(path).exists()) path = "characters/" + character + "/walk_plus.png";
            if (!Gdx.files.internal(path).exists()) return frame(character, dir, phase % FRAMES);
            path = hd(path); Texture t = tex(path); int k = k(path);
            int phases = t.getWidth() / FRAME_W*k;
            if (phases < 3 || t.getHeight() < FRAME_H*k * 4)
                return frame(character, dir, phase % FRAMES);
            all = new TextureRegion[4][phases];
            for (int d = 0; d < 4; d++) for (int f = 0; f < phases; f++)
                all[d][f] = new TextureRegion(t, f * FRAME_W*k, d * FRAME_H*k, FRAME_W*k, FRAME_H*k);
            walkPlusSheets.put(character, all);
        }
        return all[Math.max(0, Math.min(3, dir))][Math.floorMod(phase, all[0].length)];
    }

    /** v4.6.2: eight-facing sprite sheets generated from the preserved v3.7 art.
     * Lazy-loaded only when actors actually appear; missing diagonal atlas falls
     * back to the original four-way frames without introducing broken textures. */
    private final Map<String, TextureRegion[][]> walk8Sheets = new HashMap<>();
    private final Map<String, TextureRegion[][]> idle8Sheets = new HashMap<>();
    private TextureRegion[][] eightSheet(String character, boolean idle) {
        Map<String, TextureRegion[][]> cache = idle ? idle8Sheets : walk8Sheets;
        if (cache.containsKey(character)) return cache.get(character);
        String path="characters/"+character+(idle ? "/idle_8dir_v53.png" : "/walk_8dir_v53.png");
        if (!Gdx.files.internal(path).exists())
            path="characters/"+character+(idle ? "/idle_8dir_v462.png" : "/walk_8dir_v462.png");
        TextureRegion[][] atlas=null;
        if (Gdx.files.internal(path).exists()) {
            path=hd(path); Texture t=tex(path); int k=k(path);
            int frames=t.getWidth()/FRAME_W*k;
            if (frames >= (idle?8:16) && t.getHeight()>=FRAME_H*k*8) {
                atlas=new TextureRegion[8][frames];
                for(int d=0;d<8;d++) for(int i=0;i<frames;i++)
                    atlas[d][i]=new TextureRegion(t,i*FRAME_W*k,d*FRAME_H*k,FRAME_W*k,FRAME_H*k);
            }
        }
        cache.put(character,atlas);
        return atlas;
    }
    public TextureRegion walkFrame8(String character,int dir8,int phase) {
        TextureRegion[][] atlas=eightSheet(character,false);
        if(atlas!=null) return atlas[Math.floorMod(dir8,8)][Math.floorMod(phase,atlas[0].length)];
        return walkFrame(character,dir8==2?DIR_LEFT:dir8==6?DIR_RIGHT:dir8>=3 && dir8<=5?DIR_UP:DIR_DOWN,phase);
    }
    public TextureRegion idleFrame8(String character,int dir8,int phase) {
        TextureRegion[][] atlas=eightSheet(character,true);
        if(atlas!=null) return atlas[Math.floorMod(dir8,8)][Math.floorMod(phase,atlas[0].length)];
        return idleFrame(character,dir8==2?DIR_LEFT:dir8==6?DIR_RIGHT:dir8>=3 && dir8<=5?DIR_UP:DIR_DOWN,phase);
    }

    /** v3.7: delapan fase idle dari atlas baru, fallback enam fase v3.2/asli. */
    private final Map<String, TextureRegion[][]> idleV32Sheets = new HashMap<>();
    public TextureRegion idleFrame(String character, int dir, int phase) {
        TextureRegion[][] all = idleV32Sheets.get(character);
        if (all == null) {
            String path = "characters/" + character + "/idle_v53.png";
            if (!Gdx.files.internal(path).exists()) path = "characters/" + character + "/idle_v37.png";
            if (!Gdx.files.internal(path).exists()) path = "characters/" + character + "/idle_v32.png";
            if (!Gdx.files.internal(path).exists()) return frame(character, dir, 0);
            path = hd(path); Texture t = tex(path); int k = k(path);
            int phases = t.getWidth() / FRAME_W*k;
            if (phases < 6 || t.getHeight() < FRAME_H*k * 4) return frame(character, dir, 0);
            all = new TextureRegion[4][phases];
            for (int d = 0; d < 4; d++) for (int f = 0; f < phases; f++)
                all[d][f] = new TextureRegion(t, f * FRAME_W*k, d * FRAME_H*k, FRAME_W*k, FRAME_H*k);
            idleV32Sheets.put(character, all);
        }
        return all[Math.max(0, Math.min(3, dir))][Math.floorMod(phase, all[0].length)];
    }

    /** Pose dari characters/<c>/poses.png (dibuat tools/gen_poses.py). Urutan baris harus sama dengan POSES di skrip. */
    public static final String[] POSES = {"sit", "wave", "give", "reach", "bow", "hold_l", "hold_r", "cheer",
            "hug", "lean", "photo", "highfive", "dance", "read", "water", "sweep"};
    private final Map<String, TextureRegion[][]> poseSheets = new HashMap<>();

    public static int poseIndex(String pose) {
        for (int i = 0; i < POSES.length; i++) if (POSES[i].equals(pose)) return i;
        return -1;
    }

    /** null bila karakter tidak punya lembar pose. */
    public TextureRegion poseFrame(String character, int pose, int dir, int frame) {
        TextureRegion[][] r = poseSheets.get(character);
        if (r == null && !poseSheets.containsKey(character)) {
            String path = "characters/" + character + "/poses_v53.png";
            if (!Gdx.files.internal(path).exists()) path = "characters/" + character + "/poses.png";
            if (Gdx.files.internal(path).exists()) {
                path = hd(path); Texture t = tex(path); int k = k(path);
                int rows = t.getHeight() / FRAME_H*k;
                r = new TextureRegion[rows][8];
                for (int i = 0; i < rows; i++) for (int c = 0; c < 8; c++) r[i][c] = new TextureRegion(t, c * FRAME_W*k, i * FRAME_H*k, FRAME_W*k, FRAME_H*k);
            }
            poseSheets.put(character, r);
        }
        if (r == null || pose < 0 || pose >= r.length) return null;
        return r[pose][Math.max(0, Math.min(3, dir)) * 2 + (frame & 1)];
    }

    /** Potret ekspresi dengan rantai fallback (mis. pikir -> serius -> normal). */
    private final Map<String, Texture> portraitCache = new HashMap<>();

    public Texture portrait(String character, List<String> expressions) {
        String key = character + "|" + expressions;
        Texture cached = portraitCache.get(key);
        if (cached != null) return cached;
        Texture t = null;
        if (expressions != null)
            for (String e : expressions) {
                String p = "characters/" + character + "/portraits/" + e + ".png";
                if (Gdx.files.internal(p).exists()) { t = uiTex(p); break; }
            }
        if (t == null) t = uiTex("characters/" + character + "/portraits/normal.png");
        portraitCache.put(key, t);
        return t;
    }

    /** Lazy-loading SFX: cache keberhasilan dan kegagalan, tidak mencoba file hilang setiap frame. */
    public Sound sfxSound(String id) {
        if (!com.arlandsofia.olu.logic.SoundscapePlan.contains(com.arlandsofia.olu.logic.SoundscapePlan.SFX, id)) return null;
        if (sounds.containsKey(id)) return sounds.get(id);
        String path = "audio/sfx/" + id + ".wav";
        try {
            sounds.put(id, Gdx.audio.newSound(Gdx.files.internal(path)));
        } catch (Exception e) {
            sounds.put(id, null);
            if (!missing.contains(path)) missing.add(path);
            if (Gdx.app != null) Gdx.app.error("OLU-AUDIO", "Efek suara hilang: " + path);
        }
        return sounds.get(id);
    }

    public void dispose() {
        for (Texture t : owned) t.dispose();
        owned.clear(); textures.clear(); walkPlusSheets.clear(); sheets.clear(); poseSheets.clear(); portraitCache.clear();
        for (Sound s : sounds.values()) if (s != null) s.dispose();
        sounds.clear();
        if (body != null) body.dispose();
        if (title != null) title.dispose();
        if (label != null) label.dispose();
    }
}
