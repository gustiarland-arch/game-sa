package com.arlandsofia.olu.logic;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Jurnal dialog offline per slot/route. Terbatas agar ukuran save tetap ringan. */
public final class DialogueHistory {
    public static final int LIMIT = 72;
    public static final int TEXT_LIMIT = 480;
    private final List<Entry> lines = new ArrayList<>();

    public static final class Entry {
        public final String speaker, emotion, text, area;
        public final int day;
        Entry(String speaker, String emotion, String text, String area, int day) {
            this.speaker = speaker; this.emotion = emotion; this.text = text; this.area = area; this.day = day;
        }
        public Map<String, Object> toMap() {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("speaker", speaker); m.put("emotion", emotion); m.put("text", text);
            m.put("area", area); m.put("day", day);
            return m;
        }
    }

    private static String safe(String text, int limit) {
        if (text == null) return "";
        String s = text.replace('\r', ' ').replace('\n', ' ').trim();
        return s.length() > limit ? s.substring(0, limit) : s;
    }

    public void add(String speaker, String emotion, String text, String area, int day) {
        String t = safe(text, TEXT_LIMIT);
        if (t.isEmpty()) return;
        lines.add(new Entry(safe(speaker, 64), safe(emotion, 32), t, safe(area, 64), Math.max(1, day)));
        if (lines.size() > LIMIT) lines.remove(0);
    }

    public int size() { return lines.size(); }
    public Entry get(int index) { return lines.get(index); }

    public List<Object> toList() {
        List<Object> out = new ArrayList<>(lines.size());
        for (Entry line : lines) out.add(line.toMap());
        return out;
    }

    public void restore(Object raw) {
        lines.clear();
        if (!(raw instanceof List)) return;
        List<?> records = (List<?>) raw;
        int start = Math.max(0, records.size() - LIMIT);
        for (int i = start; i < records.size(); i++) {
            Object value = records.get(i);
            if (!(value instanceof Map)) continue;
            @SuppressWarnings("unchecked") Map<String, Object> m = (Map<String, Object>) value;
            add(Json.str(m, "speaker", "?"), Json.str(m, "emotion", "neutral"),
                Json.str(m, "text", ""), Json.str(m, "area", ""),
                (int) Json.num(m, "day", 1));
        }
    }
}
