package com.arlandsofia.olu.logic;

/**
 * v5.4 interior scale rebalance. Four handcrafted interiors were painted at about
 * twice the character scale, so their world space was halved (tools/room_scale_v54.py).
 * Saves written before layout version 5 store positions in the old 1200x896 space;
 * this maps them into the new space. Pure Java, headless-testable.
 */
public final class MapLayoutV54 {
    public static final int VERSION = 5;
    public static final float ROOM_SCALE = 0.5f;
    private MapLayoutV54() {}

    public static boolean scaledRoom(String area) {
        return "arland_room".equals(area) || "sofia_room".equals(area)
                || "dapur".equals(area) || "ruang_arsip".equals(area);
    }

    public static float[] fromV4(String area, float x, float y) {
        if (!scaledRoom(area)) return new float[]{x, y};
        return new float[]{x * ROOM_SCALE, y * ROOM_SCALE};
    }
}
