package com.arlandsofia.olu.logic;

/** Konstanta & helper route. */
public final class Routes {
    public static final String ARLAND = "arland";
    public static final String SOFIA = "sofia";
    public static final String[] ALL = {ARLAND, SOFIA};

    private Routes() {}

    public static boolean valid(String r) { return ARLAND.equals(r) || SOFIA.equals(r); }
    public static String partner(String r) { return ARLAND.equals(r) ? SOFIA : ARLAND; }
    public static String room(String r) { return r + "_room"; }
    public static String display(String r) { return ARLAND.equals(r) ? "Arland" : "Sofia"; }
    public static String upper(String r) { return r.toUpperCase(java.util.Locale.ROOT); }

    /** Ganti token $ROOM, $PARTNER, $RU, $ROUTE pada string data. */
    public static String resolve(String s, String route) {
        if (s == null || s.indexOf('$') < 0) return s;
        return s.replace("$ROOM", room(route)).replace("$PARTNER", partner(route))
                .replace("$RU", upper(route)).replace("$ROUTE", route);
    }
}
