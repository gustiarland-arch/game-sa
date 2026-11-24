package com.arlandsofia.olu.logic;

/**
 * Coordinate-space migration from v3.7 (and older) to the native 1200x896
 * handcrafted map set. Does not depend on Android or LibGDX; save upgrades can
 * run headlessly. Walkability snap is delegated to GameScreen after MapDb loads.
 */
public final class MapLayoutV4 {
    public static final int VERSION = 4;
    private MapLayoutV4() { }

    public static float[] fromLegacy(String area, float x, float y) {
        int w = 0, h = 0;
        if ("jalan_kota".equals(area)) { w = 2048; h = 1024; }
        else if ("perumahan".equals(area)) { w = 2048; h = 1152; }
        else if ("perpustakaan".equals(area)) { w = 1280; h = 768; }
        else if ("arcade".equals(area) || "toko_bunga".equals(area) ||
                 "arland_room".equals(area) || "sofia_room".equals(area) ||
                 "dapur".equals(area)) { w = 960; h = 640; }
        else if ("ruang_arsip".equals(area)) { w = 800; h = 560; }
        if (w == 0) return new float[] { x, y };
        return new float[] { Math.max(12f, Math.min(1187f, x * 1200f / w)),
                             Math.max(12f, Math.min(883f, y * 896f / h)) };
    }
}
