package com.arlandsofia.olu.logic;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Data dialog dari data/story.json. */
public final class StoryDb {

    public static final class Line {
        public final String speaker, emotion, text;
        public Line(String speaker, String emotion, String text) { this.speaker = speaker; this.emotion = emotion; this.text = text; }
    }

    public static final class Choice {
        public final String text;
        public final List<String> flags;
        public final Map<String, List<Line>> byRoute;
        Choice(String text, List<String> flags, Map<String, List<Line>> byRoute) { this.text = text; this.flags = flags; this.byRoute = byRoute; }
        public List<Line> response(String route) {
            List<Line> l = byRoute.get(route);
            return l == null ? new ArrayList<Line>() : l;
        }
    }

    public static final class Scene {
        public final String id, title, route, chapter, location;
        public final List<Line> lines;
        public final List<Choice> choices;
        public final List<String> flags;
        Scene(String id, String title, String route, String chapter, String location, List<Line> lines, List<Choice> choices, List<String> flags) {
            this.id = id; this.title = title; this.route = route; this.chapter = chapter; this.location = location;
            this.lines = lines; this.choices = choices; this.flags = flags;
        }
    }

    public static final class Speaker {
        public final String name, portrait, sprite; public final boolean message, npc;
        Speaker(String name, String portrait, boolean message, boolean npc, String sprite) {
            this.name = name; this.portrait = portrait; this.message = message; this.npc = npc; this.sprite = sprite;
        }
    }

    public static final class Emotion {
        public final List<String> portraits; public final String emote;
        Emotion(List<String> portraits, String emote) { this.portraits = portraits; this.emote = emote; }
    }

    public final Map<String, Scene> scenes = new LinkedHashMap<>();
    public final Map<String, Speaker> speakers = new HashMap<>();
    public final Map<String, Emotion> emotions = new HashMap<>();
    public final Map<String, String> chapterTitles = new LinkedHashMap<>();
    public final Map<String, List<String>> puzzleOrders = new HashMap<>();

    public StoryDb(String json) {
        Map<String, Object> root = Json.parseObject(json);
        for (Map.Entry<String, Object> e : Json.obj(root, "speakers").entrySet()) {
            @SuppressWarnings("unchecked") Map<String, Object> m = (Map<String, Object>) e.getValue();
            String style = Json.str(m, "style", "");
            speakers.put(e.getKey(), new Speaker(Json.str(m, "name", e.getKey()), Json.str(m, "portrait", null), "message".equals(style), "npc".equals(style), Json.str(m, "sprite", null)));
        }
        for (Map.Entry<String, Object> e : Json.obj(root, "emotions").entrySet()) {
            @SuppressWarnings("unchecked") Map<String, Object> m = (Map<String, Object>) e.getValue();
            emotions.put(e.getKey(), new Emotion(Json.strList(m, "portrait"), Json.str(m, "emote", null)));
        }
        for (Map<String, Object> c : Json.objList(root, "chapters")) chapterTitles.put(Json.str(c, "id", "?"), Json.str(c, "title", "?"));
        for (Map.Entry<String, Object> e : Json.obj(root, "puzzle_orders").entrySet()) puzzleOrders.put(e.getKey(), Json.strList(Json.obj(root, "puzzle_orders"), e.getKey()));
        for (Map.Entry<String, Object> e : Json.obj(root, "scenes").entrySet()) {
            @SuppressWarnings("unchecked") Map<String, Object> m = (Map<String, Object>) e.getValue();
            List<Choice> choices = new ArrayList<>();
            for (Map<String, Object> c : Json.objList(m, "choices")) {
                Map<String, List<Line>> by = new HashMap<>();
                for (Map.Entry<String, Object> r : Json.obj(c, "byRoute").entrySet()) by.put(r.getKey(), lines(Json.obj(c, "byRoute"), r.getKey()));
                choices.add(new Choice(Json.str(c, "text", ""), Json.strList(c, "flags"), by));
            }
            scenes.put(e.getKey(), new Scene(e.getKey(), Json.str(m, "title", ""), Json.str(m, "route", "shared"), Json.str(m, "chapter", ""),
                    Json.str(m, "location", ""), lines(m, "lines"), choices, Json.strList(m, "flags")));
        }
    }

    public static List<Line> lines(Map<String, Object> m, String key) {
        List<Line> out = new ArrayList<>();
        for (Map<String, Object> l : Json.objList(m, key))
            out.add(new Line(Json.str(l, "s", "narrator"), Json.str(l, "e", "neutral"), Json.str(l, "t", "")));
        return out;
    }

    public Scene scene(String id) { return scenes.get(id); }

    public Speaker speaker(String id) {
        Speaker s = speakers.get(id);
        return s != null ? s : new Speaker(id, null, false, false, null);
    }

    public Emotion emotion(String id) {
        Emotion e = emotions.get(id);
        return e != null ? e : emotions.get("neutral");
    }

    public String chapterTitle(String id) {
        String t = chapterTitles.get(id);
        return t == null ? id : t;
    }
}
