package com.arlandsofia.olu.logic;

/** v5.2: camera distance is a gameplay preference; cutscene framing remains authored. */
public final class CameraFramingV52 {
    private CameraFramingV52() {}
    public static float gameplayScale(int preset, boolean indoor) {
        float scale = preset <= 0 ? 1.02f : preset >= 2 ? 1.40f : 1.20f;
        return scale * (indoor ? 1.045f : 1f);
    }
    public static String presetName(int preset) {
        return preset <= 0 ? "Dekat" : preset >= 2 ? "Lebar" : "Seimbang";
    }
}
