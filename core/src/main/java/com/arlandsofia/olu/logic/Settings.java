package com.arlandsofia.olu.logic;

import java.util.LinkedHashMap;
import java.util.Map;

/** Pengaturan pemain (disimpan lokal di settings.json). */
public final class Settings {
    /** 0 = langsung, 1 = cepat, 2 = normal, 3 = lambat. */
    public int textSpeed = 2;
    public float music = 0.6f, ambience = 0.30f, sfx = 0.8f;
    /** Pilih soundtrack dinamis v2.4 atau delapan track klasik. */
    public boolean variedMusic = true;
    public boolean footsteps = true;
    /** skala kontrol sentuh: 0.85 / 1.0 / 1.2 / 1.4 */
    public float controlScale = 1.0f;
    public float controlOpacity = 0.85f;
    public boolean showHints = true;
    /** 0 = Hemat, 1 = Seimbang, 2 = Sinematik. Tidak memengaruhi quest/save permainan. */
    public int visualQuality = 1;
    public boolean smoothCamera = true;
    /** 0 dekat, 1 seimbang, 2 lebar; pengaturan terpisah dari zoom cutscene. */
    public int cameraDistance = 1;
    /** v2.8: kendali dapat dicerminkan untuk pemain kidal. */
    public boolean leftHanded = false;
    /** true = joystick mengikuti posisi jari; false = joystick tetap. */
    public boolean floatingJoystick = true;
    public float joystickSensitivity = 1f;

    public static String visualQualityName(int value) {
        return value <= 0 ? "Hemat" : value >= 2 ? "Sinematik" : "Seimbang";
    }

    public float charsPerSecond() {
        switch (textSpeed) {
            case 0: return 100000f;
            case 1: return 90f;
            case 3: return 28f;
            default: return 50f;
        }
    }

    public static String textSpeedName(int s) {
        switch (s) { case 0: return "Langsung"; case 1: return "Cepat"; case 3: return "Lambat"; default: return "Normal"; }
    }

    public Map<String, Object> toMap() {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("schema", 3); m.put("textSpeed", textSpeed); m.put("music", music); m.put("ambience", ambience); m.put("sfx", sfx);
        m.put("variedMusic", variedMusic); m.put("footsteps", footsteps);
        m.put("controlScale", controlScale); m.put("controlOpacity", controlOpacity); m.put("showHints", showHints);
        m.put("visualQuality", visualQuality); m.put("smoothCamera", smoothCamera); m.put("cameraDistance", cameraDistance);
        m.put("leftHanded", leftHanded); m.put("floatingJoystick", floatingJoystick);
        m.put("joystickSensitivity", joystickSensitivity);
        return m;
    }

    public static Settings fromMap(Map<String, Object> m) {
        Settings s = new Settings();
        s.textSpeed = clampI((int) Json.num(m, "textSpeed", 2), 0, 3);
        s.music = clamp(Json.num(m, "music", 0.6f), 0, 1);
        s.sfx = clamp(Json.num(m, "sfx", 0.8f), 0, 1);
        s.ambience = clamp(Json.num(m, "ambience", 0.30f), 0, 1);
        s.variedMusic = Json.bool(m, "variedMusic", true);
        s.footsteps = Json.bool(m, "footsteps", true);
        s.controlScale = clamp(Json.num(m, "controlScale", 1f), 0.7f, 1.6f);
        s.controlOpacity = clamp(Json.num(m, "controlOpacity", 0.85f), 0.3f, 1f);
        s.showHints = Json.bool(m, "showHints", true);
        s.visualQuality = clampI((int) Json.num(m, "visualQuality", 1), 0, 2);
        s.smoothCamera = Json.bool(m, "smoothCamera", true);
        s.cameraDistance = clampI((int) Json.num(m, "cameraDistance", 1), 0, 2);
        s.leftHanded = Json.bool(m, "leftHanded", false);
        s.floatingJoystick = Json.bool(m, "floatingJoystick", true);
        s.joystickSensitivity = clamp(Json.num(m, "joystickSensitivity", 1f), 0.7f, 1.5f);
        return s;
    }

    static float clamp(float v, float a, float b) { return Float.isNaN(v) ? a : Math.max(a, Math.min(b, v)); }
    static int clampI(int v, int a, int b) { return Math.max(a, Math.min(b, v)); }
}
