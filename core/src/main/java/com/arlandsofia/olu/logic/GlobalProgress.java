package com.arlandsofia.olu.logic;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;

/** Pencapaian global (terpisah dari slot): chapter tamat per route, flag kenangan per route, slot terakhir. */
public final class GlobalProgress {
    public static final int SCHEMA = 2;
    public final Map<String, Set<String>> completed = new LinkedHashMap<>();
    public final Map<String, Set<String>> routeFlags = new LinkedHashMap<>();
    public final Set<String> achievements = new LinkedHashSet<>();
    public String lastRoute;
    public int lastSlot;

    public GlobalProgress() {
        for (String r : Routes.ALL) { completed.put(r, new LinkedHashSet<String>()); routeFlags.put(r, new LinkedHashSet<String>()); }
    }

    public boolean routeHasFlag(String route, String flag) { Set<String> s = routeFlags.get(route); return s != null && s.contains(flag); }
    public boolean routeCompleted(String route, String chapter) { Set<String> s = completed.get(route); return s != null && s.contains(chapter); }
    public boolean bothCompleted(String chapter) { return routeCompleted(Routes.ARLAND, chapter) && routeCompleted(Routes.SOFIA, chapter); }

    /** Gabungkan progres sebuah slot ke data global (dipanggil saat menyimpan, bukan saat replay). */
    public void absorb(Progress p) {
        if (!Routes.valid(p.route)) return;
        routeFlags.get(p.route).addAll(p.flags);
        completed.get(p.route).addAll(p.chapters);
        lastRoute = p.route; lastSlot = p.slot;
        Achievements.unlock(p, this);
    }

    public Map<String, Object> toMap() {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("schema", SCHEMA);
        Map<String, Object> c = new LinkedHashMap<>(), f = new LinkedHashMap<>();
        for (String r : Routes.ALL) { c.put(r, new ArrayList<Object>(completed.get(r))); f.put(r, new ArrayList<Object>(routeFlags.get(r))); }
        m.put("completed", c); m.put("routeFlags", f);
        m.put("achievements", new ArrayList<Object>(achievements));
        m.put("lastRoute", lastRoute); m.put("lastSlot", lastSlot);
        return m;
    }

    public static GlobalProgress fromMap(Map<String, Object> m) {
        GlobalProgress g = new GlobalProgress();
        Map<String, Object> c = Json.obj(m, "completed"), f = Json.obj(m, "routeFlags");
        for (String r : Routes.ALL) { g.completed.get(r).addAll(Json.strList(c, r)); g.routeFlags.get(r).addAll(Json.strList(f, r)); }
        for (String id : Json.strList(m, "achievements")) if (Achievements.find(id) != null) g.achievements.add(id);
        g.lastRoute = Json.str(m, "lastRoute", null);
        g.lastSlot = (int) Json.num(m, "lastSlot", 0);
        if (g.bothCompleted("C06")) g.achievements.add("both"); // migrasi schema1
        return g;
    }
}
