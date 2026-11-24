package com.arlandsofia.olu.logic;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Data quest dari data/quests.json: step cerita, side quest, NPC kota, puzzle, minigame. */
public final class QuestDb {

    public static final class Sprite {
        public final String image; public final float x, y; public final boolean bob;
        Sprite(String image, float x, float y, boolean bob) { this.image = image; this.x = x; this.y = y; this.bob = bob; }
    }

    public static final class Interactable {
        public final String id, area, route, label, hideIfFlag;
        public final Map<String, String> labelByRoute;
        public final float x, y, r;
        public final Sprite sprite;
        public final List<Map<String, Object>> actions;
        public final Map<String, Object> when;
        public final boolean marker;
        Interactable(Map<String, Object> m) {
            id = Json.str(m, "id", "?"); area = Json.str(m, "area", ""); route = Json.str(m, "route", null);
            label = Json.str(m, "label", "Periksa"); hideIfFlag = Json.str(m, "hideIfFlag", null);
            labelByRoute = new HashMap<>();
            for (Map.Entry<String, Object> e : Json.obj(m, "labelByRoute").entrySet()) labelByRoute.put(e.getKey(), String.valueOf(e.getValue()));
            x = Json.num(m, "x", 0); y = Json.num(m, "y", 0); r = Json.num(m, "r", 64);
            Map<String, Object> s = Json.obj(m, "sprite");
            sprite = s.isEmpty() ? null : new Sprite(Json.str(s, "image", ""), Json.num(s, "x", x), Json.num(s, "y", y), Json.bool(s, "bob", false));
            actions = Json.objList(m, "actions");
            when = Json.obj(m, "when");
            marker = Json.bool(m, "marker", true);
        }
        public String label(String routeId) {
            String l = labelByRoute.get(routeId);
            return l != null ? l : label;
        }
        public boolean forRoute(String routeId) { return route == null || route.equals(routeId); }
    }

    public static final class Npc {
        public final String who, area, dir; public final float x, y;
        Npc(Map<String, Object> m) {
            who = Json.str(m, "who", "$PARTNER"); area = Json.str(m, "area", ""); dir = Json.str(m, "dir", "down");
            x = Json.num(m, "x", 0); y = Json.num(m, "y", 0);
        }
    }

    /** NPC kota: muncul bila 'when' terpenuhi; dialog pertama yang kondisinya cocok dipakai. */
    public static final class TownNpc {
        public final String id, name, sprite, area, dir;
        public final float x, y;
        public final Map<String, Object> when;
        public final List<Map<String, Object>> dialogs;
        /** jadwal harian: [{at, area, x, y, dir, wander, weather}] ; kosong = selalu di posisi rumah */
        public final List<Map<String, Object>> schedule;
        public final float wander;
        TownNpc(Map<String, Object> m) {
            id = Json.str(m, "id", "?"); name = Json.str(m, "name", id); sprite = Json.str(m, "sprite", id);
            area = Json.str(m, "area", ""); dir = Json.str(m, "dir", "down");
            x = Json.num(m, "x", 0); y = Json.num(m, "y", 0);
            when = Json.obj(m, "when"); dialogs = Json.objList(m, "dialogs");
            schedule = Json.objList(m, "schedule"); wander = Json.num(m, "wander", 0);
        }
    }

    /** Percakapan opsional dengan pasangan (companion). Sekali per id. */
    public static final class Talk {
        public final String id, area, scene; public final Map<String, Object> when;
        Talk(Map<String, Object> m) { id = Json.str(m, "id", "?"); area = Json.str(m, "area", null); scene = Json.str(m, "scene", ""); when = Json.obj(m, "when"); }
    }

    public static final class Good {
        public final String item, name, desc; public final int price;
        Good(Map<String, Object> m) {
            item = Json.str(m, "item", ""); name = Json.str(m, "name", item);
            desc = Json.str(m, "desc", ""); price = (int) Json.num(m, "price", 0);
        }
    }
    public static final class Shop {
        public final String id, title, keeper;
        public final List<Good> goods = new ArrayList<>();
        Shop(String id, Map<String, Object> m) {
            this.id = id; title = Json.str(m, "title", id); keeper = Json.str(m, "keeper", "");
            for (Map<String, Object> a : Json.objList(m, "goods")) goods.add(new Good(a));
        }
    }
    public static final class Job {
        public final String id, title, minigame; public final int reward, minScore;
        public final List<String> stops;
        Job(String id, Map<String, Object> m) {
            this.id = id; title = Json.str(m, "title", id); minigame = Json.str(m, "minigame", "");
            reward = (int) Json.num(m, "reward", 0); minScore = (int) Json.num(m, "minScore", 1);
            stops = Json.strList(m, "stops");
        }
    }

    /** Hadiah dibeli pada katalog ekonomi dan diberikan secara konsumtif. */
    public static final class Gift {
        public final String item, scene; public final int affection;
        Gift(Map<String, Object> m) {
            item = Json.str(m, "item", ""); scene = Json.str(m, "scene", "");
            affection = (int) Json.num(m, "affection", 0);
        }
    }
    public static final class DateActivity {
        public final String id, title, area, desc; public final int cost, affection;
        public final int startMinute, endMinute;
        public final Map<String, String> scenes = new LinkedHashMap<>();
        DateActivity(Map<String, Object> m) {
            id = Json.str(m, "id", ""); title = Json.str(m, "title", id);
            area = Json.str(m, "area", ""); desc = Json.str(m, "desc", "");
            cost = (int) Json.num(m, "cost", 0); affection = (int) Json.num(m, "affection", 0);
            List<Object> h = Json.list(m, "hours");
            startMinute = h.size() > 0 ? WorldClock.parse(h.get(0), 0) : 0;
            endMinute = h.size() > 1 ? WorldClock.parse(h.get(1), 26 * 60) : 26 * 60;
            for (Map.Entry<String, Object> e : Json.obj(m, "scene").entrySet())
                scenes.put(e.getKey(), String.valueOf(e.getValue()));
        }
        public String scene(String route) { return scenes.get(route); }
    }

    /** Konteks lokasi, waktu, cuaca dan ambang kedekatan berasal dari JSON generator. */
    public static final class MomentActivity {
        public final String id, title, area, desc;
        public final int startMinute, endMinute, minAffection, affection;
        public final List<String> weather;
        public final Map<String, String> scenes = new LinkedHashMap<>();
        MomentActivity(Map<String, Object> m) {
            id = Json.str(m, "id", ""); title = Json.str(m, "title", id);
            area = Json.str(m, "area", ""); desc = Json.str(m, "desc", "");
            minAffection = (int) Json.num(m, "minAffection", 0);
            affection = (int) Json.num(m, "affection", 0);
            List<Object> h = Json.list(m, "hours");
            startMinute = h.size() > 0 ? WorldClock.parse(h.get(0), 0) : 0;
            endMinute = h.size() > 1 ? WorldClock.parse(h.get(1), WorldClock.DAY_END) : WorldClock.DAY_END;
            weather = Json.strList(m, "weather");
            for (Map.Entry<String, Object> e : Json.obj(m, "scene").entrySet())
                scenes.put(e.getKey(), String.valueOf(e.getValue()));
        }
        public String scene(String route) { return scenes.get(route); }
    }

    /** Interaksi pasangan v2.2, bisa dijalankan ulang esok hari; animasi dan dialog khusus tiap route. */
    public static final class CoupleAction {
        public final String id, title, desc, gesture;
        public final List<String> areas, weather;
        public final int startMinute, endMinute, minAffection, affection;
        public final Map<String, String> scenes = new LinkedHashMap<>();
        CoupleAction(Map<String, Object> m) {
            id = Json.str(m, "id", ""); title = Json.str(m, "title", id);
            desc = Json.str(m, "desc", ""); gesture = Json.str(m, "gesture", "highfive");
            areas = Json.strList(m, "areas"); weather = Json.strList(m, "weather");
            minAffection = (int) Json.num(m, "minAffection", 0);
            affection = (int) Json.num(m, "affection", 0);
            List<Object> hrs = Json.list(m, "hours");
            startMinute = hrs.size() > 0 ? WorldClock.parse(hrs.get(0), WorldClock.DAY_START) : WorldClock.DAY_START;
            endMinute = hrs.size() > 1 ? WorldClock.parse(hrs.get(1), WorldClock.DAY_END) : WorldClock.DAY_END;
            for (Map.Entry<String, Object> e : Json.obj(m, "scene").entrySet()) scenes.put(e.getKey(), String.valueOf(e.getValue()));
        }
        public String scene(String route) { return scenes.get(route); }
    }

    public static final class SideQuest {
        public final String id, title, desc, startFlag, doneFlag, chapter, route;
        SideQuest(Map<String, Object> m) {
            id = Json.str(m, "id", "?"); title = Json.str(m, "title", ""); desc = Json.str(m, "desc", "");
            startFlag = Json.str(m, "startFlag", ""); doneFlag = Json.str(m, "doneFlag", ""); chapter = Json.str(m, "chapter", "");
            route = Json.str(m, "route", null);
        }
        public boolean forRoute(String currentRoute) { return route == null || route.equals(currentRoute); }
    }

    public static final class Step {
        public final String id, chapter, quest;
        public final Map<String, String> objective = new HashMap<>();
        public final List<Interactable> interactables = new ArrayList<>();
        public final List<Npc> npcs = new ArrayList<>();
        public final String enterArea;
        public final List<Map<String, Object>> enterActions;
        /** aksi yang dijalankan saat step ini dimulai (mis. cutscene pembuka) */
        public final List<Map<String, Object>> onStart;
        /** musik khusus step (opsional), dibatasi ke area tertentu bila musicAreas tidak kosong */
        public final String music; public final List<String> musicAreas;
        public final int completeShards;
        public final String completeCounter;
        public final int completeCount;
        public final List<Map<String, Object>> completeActions;
        public final String counter; public final int counterMax;
        public final boolean isFinal;
        public final String weather, tint;
        public final float tintAlpha;
        Step(Map<String, Object> m) {
            id = Json.str(m, "id", "?"); chapter = Json.str(m, "chapter", ""); quest = Json.str(m, "quest", "");
            for (Map.Entry<String, Object> e : Json.obj(m, "objective").entrySet()) objective.put(e.getKey(), String.valueOf(e.getValue()));
            for (Map<String, Object> it : Json.objList(m, "interactables")) interactables.add(new Interactable(it));
            for (Map<String, Object> n : Json.objList(m, "npcs")) npcs.add(new Npc(n));
            Map<String, Object> ea = Json.obj(m, "enterArea");
            enterArea = Json.str(ea, "area", null); enterActions = Json.objList(ea, "actions");
            Map<String, Object> c = Json.obj(m, "complete");
            completeShards = (int) Json.num(c, "shards", 0);
            completeCounter = Json.str(c, "counter", completeShards > 0 ? "shards" : null);
            completeCount = (int) Json.num(c, "count", completeShards);
            completeActions = Json.objList(c, "actions");
            counter = Json.str(m, "counter", null); counterMax = (int) Json.num(m, "counterMax", 0);
            isFinal = Json.bool(m, "final", false);
            onStart = Json.objList(m, "onStart");
            music = Json.str(m, "music", null); musicAreas = Json.strList(m, "musicAreas");
            weather = Json.str(m, "weather", null);
            tint = Json.str(m, "tint", null);
            tintAlpha = Json.num(m, "tintAlpha", 0.18f);
        }
        public String objective(String route) {
            String o = objective.get(route);
            return o != null ? o : "Jelajahi cerita";
        }
    }

    public static final class Puzzle {
        public final String id, title; public final List<String> symbols;
        public final Map<String, List<String>> order = new HashMap<>();
        public final Map<String, String> hintFlag = new HashMap<>();
        public final int hintAfterFails;
        Puzzle(String id, Map<String, Object> m) {
            this.id = id; title = Json.str(m, "title", "Puzzle"); symbols = Json.strList(m, "symbols");
            Map<String, Object> o = Json.obj(m, "order");
            for (String k : o.keySet()) order.put(k, Json.strList(o, k));
            for (Map.Entry<String, Object> e : Json.obj(m, "hintFlag").entrySet()) hintFlag.put(e.getKey(), String.valueOf(e.getValue()));
            hintAfterFails = (int) Json.num(m, "hintAfterFails", 2);
        }
        public List<String> order(String route) {
            List<String> l = order.get(route);
            return l != null ? l : symbols;
        }
    }

    /** Aktivitas romantis yang dapat dimainkan ulang tanpa menduplikasi bonus harian. */
    public static final class RomanceGame {
        public final String id, title, minigame, desc, scene;
        public final List<String> areas;
        public final int affection, minScore;
        RomanceGame(Map<String, Object> m) {
            id = Json.str(m, "id", ""); title = Json.str(m, "title", "");
            minigame = Json.str(m, "minigame", ""); desc = Json.str(m, "desc", "");
            scene = Json.str(m, "scene", ""); areas = Json.strList(m, "areas");
            affection = (int) Json.num(m, "affection", 0);
            minScore = (int) Json.num(m, "minScore", 1);
        }
        public String scene(String route) { return scene + "@" + route; }
    }

    /** v2.7: Aktivitas dunia data-driven, memiliki konteks jam/cuaca/route dan cerita tiap POV. */
    public static final class WorldEvent {
        public final String id, title, area, route, minChapter;
        public final float x, y, radius;
        public final int startMinute, endMinute, affection, coins;
        public final boolean companion;
        public final List<String> weather;
        public final Map<String, String> scenes = new LinkedHashMap<>();
        WorldEvent(Map<String, Object> m) {
            id = Json.str(m, "id", ""); title = Json.str(m, "title", id);
            area = Json.str(m, "area", ""); route = Json.str(m, "route", null);
            minChapter = Json.str(m, "minChapter", "C02");
            x = Json.num(m, "x", 0); y = Json.num(m, "y", 0); radius = Json.num(m, "r", 62);
            List<Object> hours = Json.list(m, "hours");
            startMinute = hours.size() > 0 ? WorldClock.parse(hours.get(0), WorldClock.DAY_START) : WorldClock.DAY_START;
            endMinute = hours.size() > 1 ? WorldClock.parse(hours.get(1), WorldClock.DAY_END) : WorldClock.DAY_END;
            affection = (int) Json.num(m, "affection", 0);
            coins = (int) Json.num(m, "coins", 0);
            companion = Json.bool(m, "companion", true);
            weather = Json.strList(m, "weather");
            for (Map.Entry<String, Object> e : Json.obj(m, "scenes").entrySet())
                scenes.put(e.getKey(), String.valueOf(e.getValue()));
        }
        public String scene(String routeName) { return scenes.get(routeName); }
    }

    /** v4.9 optional world secrets: once per save, separate from canon quest flags. */
    public static final class Discovery {
        public final String id, area, title, hint, minChapter, flag, minigame;
        Discovery(Map<String, Object> m) {
            id=Json.str(m,"id","");
            area=Json.str(m,"area","");
            title=Json.str(m,"title",id);
            hint=Json.str(m,"hint","");
            minChapter=Json.str(m,"minChapter","C02");
            flag=Json.str(m,"flag","");
            minigame=Json.str(m,"minigame","");
        }
    }

    public final Map<String, Step> steps = new LinkedHashMap<>();
    public final Map<String, String> chapterFirstStep = new LinkedHashMap<>();
    public final List<String> chapterOrder = new ArrayList<>();
    public final Map<String, Puzzle> puzzles = new HashMap<>();
    public final List<Interactable> side = new ArrayList<>();
    public final List<TownNpc> townNpcs = new ArrayList<>();
    public final List<WorldEvent> worldEvents = new ArrayList<>();
    public final List<Discovery> discoveries = new ArrayList<>();
    public final List<SideQuest> sideQuests = new ArrayList<>();
    public final List<Talk> talks = new ArrayList<>();
    public final Map<String, Map<String, Object>> minigames = new HashMap<>();
    public final Map<String, Shop> shops = new LinkedHashMap<>();
    public final Map<String, Job> jobs = new LinkedHashMap<>();
    public final List<Gift> gifts = new ArrayList<>();
    public final List<DateActivity> dates = new ArrayList<>();
    public final List<MomentActivity> moments = new ArrayList<>();
    public final List<CoupleAction> coupleActions = new ArrayList<>();
    public final List<RomanceGame> romanceGames = new ArrayList<>();
    public final List<String> credits = new ArrayList<>();
    /** komentar companion: area -> route pemain -> kalimat (diucapkan pasangan) */
    public final Map<String, Map<String, List<String>>> comments = new LinkedHashMap<>();
    /** step id -> chapter: step pertama chapter (termasuk yang berbeda per route) untuk snapshot replay. */
    public final Map<String, String> chapterStartSteps = new HashMap<>();

    public QuestDb(String json) {
        Map<String, Object> root = Json.parseObject(json);
        for (Map<String, Object> s : Json.objList(root, "steps")) { Step st = new Step(s); steps.put(st.id, st); }
        for (Map<String, Object> c : Json.objList(root, "chapters")) {
            String id = Json.str(c, "id", "?");
            chapterOrder.add(id);
            String first = Json.str(c, "firstStep", "");
            if (!first.isEmpty()) chapterFirstStep.put(id, first);
        }
        Map<String, Object> pz = Json.obj(root, "puzzles");
        for (String k : pz.keySet()) puzzles.put(k, new Puzzle(k, Json.obj(pz, k)));
        for (Map<String, Object> m : Json.objList(root, "side")) side.add(new Interactable(m));
        for (Map<String, Object> m : Json.objList(root, "townNpcs")) townNpcs.add(new TownNpc(m));
        for (Map<String, Object> m : Json.objList(root, "worldEvents")) worldEvents.add(new WorldEvent(m));
        for (Map<String, Object> m : Json.objList(root, "worldDiscoveries")) discoveries.add(new Discovery(m));
        for (Map<String, Object> m : Json.objList(root, "sideQuests")) sideQuests.add(new SideQuest(m));
        for (Map<String, Object> m : Json.objList(root, "talks")) talks.add(new Talk(m));
        Map<String, Object> mg = Json.obj(root, "minigames");
        for (String k : mg.keySet()) minigames.put(k, Json.obj(mg, k));
        for (String k : Json.obj(root, "shops").keySet()) shops.put(k, new Shop(k, Json.obj(Json.obj(root, "shops"), k)));
        for (String k : Json.obj(root, "jobs").keySet()) jobs.put(k, new Job(k, Json.obj(Json.obj(root, "jobs"), k)));
        Map<String, Object> romance = Json.obj(root, "romance");
        for (Map<String, Object> a : Json.objList(romance, "gifts")) gifts.add(new Gift(a));
        for (Map<String, Object> a : Json.objList(romance, "dates")) dates.add(new DateActivity(a));
        for (Map<String, Object> a : Json.objList(romance, "moments")) moments.add(new MomentActivity(a));
        for (Map<String, Object> a : Json.objList(romance, "coupleActions")) coupleActions.add(new CoupleAction(a));
        for (Map<String, Object> a : Json.objList(romance, "games")) romanceGames.add(new RomanceGame(a));
        credits.addAll(Json.strList(root, "credits"));
        for (Map.Entry<String, Object> e : Json.obj(root, "comments").entrySet()) {
            Map<String, List<String>> byRoute = new LinkedHashMap<>();
            @SuppressWarnings("unchecked") Map<String, Object> m = (Map<String, Object>) e.getValue();
            for (String r : m.keySet()) byRoute.put(r, Json.strList(m, r));
            comments.put(e.getKey(), byRoute);
        }
        for (Map.Entry<String, String> e : chapterFirstStep.entrySet()) chapterStartSteps.put(e.getValue(), e.getKey());
        Map<String, Object> rf = Json.obj(root, "chapterRouteFirst");
        for (String ch : rf.keySet()) for (String stp : Json.strList(rf, ch)) chapterStartSteps.put(stp, ch);
    }

    public Step step(String id) { return steps.get(id); }
    public String firstStep() { return chapterFirstStep.isEmpty() ? null : chapterFirstStep.values().iterator().next(); }
    public int chapterIndex(String ch) { return chapterOrder.indexOf(ch); }
    public Map<String, Object> minigame(String id) { Map<String, Object> m = minigames.get(id); return m == null ? Collections.<String, Object>emptyMap() : m; }
}
