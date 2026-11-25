package com.arlandsofia.olu.logic;

/**
 * Peta soundtrack 100% offline. Murni Java, sehingga pemilihan track dapat diuji tanpa Android/LibGDX.
 * ID lama tidak dihapus: dapat dipakai cutscene dan opsi musik klasik.
 */
public final class SoundscapePlan {
    private SoundscapePlan() {}
    public static final String[] LEGACY = {"town", "memory", "cafe", "rain", "night", "star", "tender", "game"};
    public static final String[] MUSIC = {
        "menu_theme", "home_morning", "home_evening", "city_morning", "city_evening", "city_night",
        "park_blossom", "park_sunset", "lake_breeze", "lake_moon", "flower_shop", "cafe_waltz",
        "library_whisper", "arcade_neon", "neighborhood_day", "memory_bloom", "lantern_glow",
        "whisper_woods", "archive_mystery", "star_road", "star_village", "hill_stars",
        "crystal_echo", "eternal_promise", "rain_lullaby"
    };
    /** Scene-only tracks: dipilih melalui perintah cutscene, bukan shuffle lokasi. */
    public static final String[] CINEMATIC = {
        "cinema_first_meet", "cinema_memory_portal", "cinema_rain_conflict", "cinema_reconciliation",
        "cinema_quiet", "cinema_lantern_finale", "cinema_our_tomorrow", "cinema_gallery_empty", "cinema_gallery_repair",
        "cinema_letter_tomorrow", "cinema_two_sides_v467", "cinema_date_choices_v468", "cinema_small_things_v469", "cinema_gallery_promise_v469", "cinema_empty_seat_v470", "cinema_rain_five_lights_v470", "cinema_listen_again_v470", "cinema_clockwork_v471", "cinema_two_sides_v471", "cinema_quiet_reveal_v471", "cinema_hall_v472", "cinema_unwritten_v472", "cinema_homecoming_v473", "cinema_dual_letters_v473", "cinema_prologue_promise_v474", "cinema_prologue_memory_v474", "score_empty_chair_v480", "score_rain_resolve_v480", "score_quiet_truth_v480", "score_open_page_v480", "score_lake_coda_v480",
        "v50_plaza_ascent", "v50_rain_reflections", "v50_starlit_steps", "v50_tomorrow_horizon", "v50_cafe_highlight"
    };
    public static final String[] AMBIENTS = {
        "birds_morning", "city_day", "wind_leaves", "park_birds", "lake_water", "cafe_room",
        "library_room", "rain_outdoor", "rain_window", "night_crickets", "forest_wind",
        "magic_chimes", "cave_drips", "arcade_hum", "v50_highland_breeze", "v50_memory_air"
    };
    public static final String[] SFX = {
        "page", "sparkle", "soft_wrong", "step_grass", "step_stone", "step_wood", "door_open",
        "door_close", "bell_shop", "coin", "gift", "heart", "hug", "selfie", "highfive",
        "quest_complete", "scene_transition", "notification", "splash", "bird_chirp",
        "cat_meow", "dog_bark", "duck_quack", "wind_gust", "rain_drop", "lantern",
        "page_turn", "menu_confirm", "flower_pick", "paper_fold", "cinema_heartbeat", "cinema_whoosh", "photo_lantern_v468", "v469_pencil", "v470_paper_note", "v471_memory_chime", "v472_memory_glint", "v473_letter_fold", "v50_stair_foot", "v50_stair_enter", "v50_view_wind", "v50_memory_shimmer", "v50_panoramic_reveal", "v54_thunder", "v54_step_puddle"
    };
    public static boolean contains(String[] array, String id) {
        if (id == null) return false;
        for (String value : array) if (value.equals(id)) return true;
        return false;
    }
    public static String musicPath(String id) {
        if (contains(MUSIC, id) || contains(CINEMATIC, id)) return "audio/music/" + id + ".ogg";
        if (contains(LEGACY, id)) return "audio/music/" + id + "_theme.ogg";
        return null;
    }
    public static String ambientPath(String id) {
        return contains(AMBIENTS, id) ? "audio/ambience/" + id + ".ogg" : null;
    }

    /** Prioritaskan musik cerita; jangan menimpa musik khusus cutscene/quest. */
    public static String musicFor(String area, String base, String weather, boolean indoor,
                                  int minute, int day, boolean variety, String questMusic) {
        if (questMusic != null && !questMusic.isEmpty()) return questMusic;
        boolean rainy = "rain".equals(weather) || "hujan".equals(weather);
        boolean night = WorldClock.isNight(minute);
        boolean dusk = WorldClock.hour(minute) >= 16;
        if (!variety) {
            if ("town".equals(base) && !indoor && rainy) return "rain";
            if ("town".equals(base) && !indoor && night) return "night";
            return base == null ? "town" : base;
        }
        if ("arland_room".equals(area) || "sofia_room".equals(area)) return dusk || night ? "home_evening" : "home_morning";
        if ("cafe".equals(area) || "dapur".equals(area) || "galeri_komunitas".equals(area)) return "cafe_waltz";
        if ("perpustakaan".equals(area)) return "library_whisper";
        if ("ruang_dua_surat".equals(area)) return "library_whisper";
        if ("toko_bunga".equals(area)) return "flower_shop";
        if ("arcade".equals(area)) return "arcade_neon";
        if ("memory_garden".equals(area)) return "memory_bloom";
        if ("lantern_field".equals(area) || "rain_garden".equals(area)) return "lantern_glow";
        if ("star_path".equals(area)) return "star_road";
        if ("starfall_village".equals(area)) return "star_village";
        if ("clockwork_station".equals(area)) return "archive_mystery";
        if ("moonlight_lake".equals(area)) return "lake_moon";
        if ("memory_bridge".equals(area)) return "star_road";
        if ("bukit_bintang".equals(area)) return "hill_stars";
        if ("eternal_garden".equals(area)) return "eternal_promise";
        if ("hall_of_tomorrow".equals(area)) return "eternal_promise";
        if ("ruang_arsip".equals(area)) return "archive_mystery";
        if ("hutan_bisik".equals(area)) return "whisper_woods";
        if ("gua_kristal".equals(area)) return "crystal_echo";
        if (rainy && !indoor) return "rain_lullaby";
        if ("riverside".equals(area) || "dermaga".equals(area)) return night ? "lake_moon" : "lake_breeze";
        if ("taman_kota".equals(area)) return dusk || night ? "park_sunset" : "park_blossom";
        if ("perumahan".equals(area)) return night ? "city_night" : "neighborhood_day";
        if ("plaza".equals(area) || "jalan_kota".equals(area)) {
            if (night) return "city_night";
            if (dusk) return "city_evening";
            return "city_morning";
        }
        return base == null ? "town" : base;
    }

    /** Ambience diputar di channel terpisah dari musik; bisa dimatikan dari Pengaturan. */
    public static String ambienceFor(String area, String weather, boolean indoor, int minute) {
        boolean rainy = "rain".equals(weather) || "hujan".equals(weather);
        if ("rain_garden".equals(area)) return "rain_outdoor";
        if ("star_path".equals(area) || "bukit_bintang".equals(area)) return "v50_highland_breeze";
        if ("memory_garden".equals(area) || "eternal_garden".equals(area)) return "v50_memory_air";
        if ("hall_of_tomorrow".equals(area)) return "magic_chimes";
        if ("clockwork_station".equals(area) || "memory_bridge".equals(area)) return "magic_chimes";
        if ("moonlight_lake".equals(area)) return "lake_water";
        if ("arcade".equals(area)) return "arcade_hum";
        if ("cafe".equals(area) || "dapur".equals(area) || "galeri_komunitas".equals(area)) return rainy ? "rain_window" : "cafe_room";
        if ("ruang_dua_surat".equals(area)) return "library_room";
        if ("perpustakaan".equals(area) || "ruang_arsip".equals(area)) return rainy ? "rain_window" : "library_room";
        if ("gua_kristal".equals(area)) return "cave_drips";
        if ("memory_garden".equals(area) || "lantern_field".equals(area) || "star_path".equals(area)
                || "starfall_village".equals(area) || "eternal_garden".equals(area) || "bukit_bintang".equals(area)) return "magic_chimes";
        if (indoor) return rainy ? "rain_window" : null;
        if (rainy) return "rain_outdoor";
        if ("riverside".equals(area) || "dermaga".equals(area)) return "lake_water";
        if ("hutan_bisik".equals(area)) return "forest_wind";
        if (WorldClock.isNight(minute)) return "night_crickets";
        if ("taman_kota".equals(area) || "toko_bunga".equals(area)) return "park_birds";
        if ("perumahan".equals(area)) return "wind_leaves";
        if (WorldClock.hour(minute) < 10) return "birds_morning";
        return "city_day";
    }

    public static String footstepFor(String area) {
        if ("taman_kota".equals(area) || "hutan_bisik".equals(area) || "memory_garden".equals(area) || "eternal_garden".equals(area) || "rain_garden".equals(area)) return "step_grass";
        if ("cafe".equals(area) || "dapur".equals(area) || "arland_room".equals(area) || "sofia_room".equals(area)
                || "perpustakaan".equals(area) || "ruang_arsip".equals(area) || "galeri_komunitas".equals(area) || "clockwork_station".equals(area) || "hall_of_tomorrow".equals(area) || "ruang_dua_surat".equals(area)) return "step_wood";
        return "step_stone";
    }
}
