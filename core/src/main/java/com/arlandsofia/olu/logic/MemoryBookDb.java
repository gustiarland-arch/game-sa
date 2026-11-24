package com.arlandsofia.olu.logic;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Data Memory Book & item dari data/memory_book.json. */
public final class MemoryBookDb {

    public static final class Item {
        public final String id, name, icon, desc;
        Item(String id, Map<String, Object> m) { this.id = id; name = Json.str(m, "name", id); icon = Json.str(m, "icon", ""); desc = Json.str(m, "desc", ""); }
    }

    public static final class Entry {
        public final String id, chapter, route, type, unlock, icon, title, text;
        Entry(Map<String, Object> m) {
            id = Json.str(m, "id", "?"); chapter = Json.str(m, "chapter", ""); route = Json.str(m, "route", "shared");
            type = Json.str(m, "type", "fictional_memory"); unlock = Json.str(m, "unlock", ""); icon = Json.str(m, "icon", "");
            title = Json.str(m, "title", ""); text = Json.str(m, "text", "");
        }
    }

    public final Map<String, Item> items = new LinkedHashMap<>();
    public final List<Entry> entries = new ArrayList<>();
    public final String bonusTitle, bonusText, bonusIcon;

    public MemoryBookDb(String json) {
        Map<String, Object> root = Json.parseObject(json);
        Map<String, Object> it = Json.obj(root, "items");
        for (String k : it.keySet()) items.put(k, new Item(k, Json.obj(it, k)));
        for (Map<String, Object> e : Json.objList(root, "entries")) entries.add(new Entry(e));
        Map<String, Object> b = Json.obj(root, "bonus");
        bonusTitle = Json.str(b, "title", "Bonus"); bonusText = Json.str(b, "text", ""); bonusIcon = Json.str(b, "icon", "");
    }

    public Item item(String id) { return items.get(id); }

    /** Status satu entri untuk route aktif. */
    public enum State { UNLOCKED, OTHER_SIDE, LOCKED }

    public State state(Entry e, Progress p, GlobalProgress g) {
        String other = Routes.partner(p.route);
        if (e.route.equals("shared") || e.route.equals(p.route)) {
            if (p.hasFlag(e.unlock)) return State.UNLOCKED;
            return State.LOCKED;
        }
        if (e.route.equals(other) && g != null && g.routeHasFlag(other, e.unlock)) return State.OTHER_SIDE;
        return State.LOCKED;
    }

    /** Entri yang relevan untuk route ini: shared + milik route + milik route lain (ditampilkan sebagai sisi lain/terkunci). */
    public List<Entry> entriesFor(String route) {
        List<Entry> out = new ArrayList<>();
        for (Entry e : entries) if (e.route.equals("shared") || e.route.equals(route)) out.add(e);
        for (Entry e : entries) if (!e.route.equals("shared") && !e.route.equals(route)) out.add(e);
        return out;
    }
}
