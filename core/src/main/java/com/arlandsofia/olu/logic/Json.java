package com.arlandsofia.olu.logic;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Parser/penulis JSON kecil tanpa dependensi (agar logika cerita bisa diuji tanpa LibGDX).
 * Objek -> LinkedHashMap, array -> ArrayList, angka -> Double, string, Boolean, null.
 */
public final class Json {
    private final String s;
    private int i;

    private Json(String s) { this.s = s; }

    public static Object parse(String text) {
        if (text == null) throw new IllegalArgumentException("JSON null");
        Json p = new Json(text);
        p.ws();
        Object v = p.value();
        p.ws();
        if (p.i != p.s.length()) throw p.err("Karakter berlebih");
        return v;
    }

    @SuppressWarnings("unchecked")
    public static Map<String, Object> parseObject(String text) {
        Object o = parse(text);
        if (!(o instanceof Map)) throw new IllegalArgumentException("JSON bukan objek");
        return (Map<String, Object>) o;
    }

    private RuntimeException err(String m) { return new IllegalArgumentException(m + " @" + i); }

    private void ws() {
        while (i < s.length()) {
            char c = s.charAt(i);
            if (c == ' ' || c == '\n' || c == '\r' || c == '\t') i++; else break;
        }
    }

    private Object value() {
        if (i >= s.length()) throw err("JSON terpotong");
        char c = s.charAt(i);
        if (c == '{') return obj();
        if (c == '[') return arr();
        if (c == '"') return str();
        if (c == 't' && s.startsWith("true", i)) { i += 4; return Boolean.TRUE; }
        if (c == 'f' && s.startsWith("false", i)) { i += 5; return Boolean.FALSE; }
        if (c == 'n' && s.startsWith("null", i)) { i += 4; return null; }
        return num();
    }

    private Map<String, Object> obj() {
        Map<String, Object> m = new LinkedHashMap<>();
        i++; ws();
        if (i < s.length() && s.charAt(i) == '}') { i++; return m; }
        while (true) {
            ws();
            if (i >= s.length() || s.charAt(i) != '"') throw err("Kunci harus string");
            String k = str();
            ws();
            if (i >= s.length() || s.charAt(i) != ':') throw err("Butuh ':'");
            i++; ws();
            m.put(k, value());
            ws();
            if (i >= s.length()) throw err("Objek tidak ditutup");
            char c = s.charAt(i++);
            if (c == '}') return m;
            if (c != ',') throw err("Butuh ',' atau '}'");
        }
    }

    private List<Object> arr() {
        List<Object> l = new ArrayList<>();
        i++; ws();
        if (i < s.length() && s.charAt(i) == ']') { i++; return l; }
        while (true) {
            ws();
            l.add(value());
            ws();
            if (i >= s.length()) throw err("Array tidak ditutup");
            char c = s.charAt(i++);
            if (c == ']') return l;
            if (c != ',') throw err("Butuh ',' atau ']'");
        }
    }

    private String str() {
        StringBuilder b = new StringBuilder();
        i++;
        while (true) {
            if (i >= s.length()) throw err("String tidak ditutup");
            char c = s.charAt(i++);
            if (c == '"') return b.toString();
            if (c == '\\') {
                if (i >= s.length()) throw err("Escape terpotong");
                char e = s.charAt(i++);
                switch (e) {
                    case '"': b.append('"'); break;
                    case '\\': b.append('\\'); break;
                    case '/': b.append('/'); break;
                    case 'b': b.append('\b'); break;
                    case 'f': b.append('\f'); break;
                    case 'n': b.append('\n'); break;
                    case 'r': b.append('\r'); break;
                    case 't': b.append('\t'); break;
                    case 'u':
                        if (i + 4 > s.length()) throw err("Escape unicode terpotong");
                        b.append((char) Integer.parseInt(s.substring(i, i + 4), 16));
                        i += 4;
                        break;
                    default: throw err("Escape tidak dikenal");
                }
            } else b.append(c);
        }
    }

    private Double num() {
        int st = i;
        while (i < s.length() && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0) i++;
        if (st == i) throw err("Nilai tidak dikenal");
        try { return Double.valueOf(s.substring(st, i)); } catch (NumberFormatException ex) { throw err("Angka salah"); }
    }

    // ------------------------------------------------------------ menulis
    public static String write(Object v) { StringBuilder b = new StringBuilder(); write(b, v, 0, true); return b.toString(); }
    public static String writeCompact(Object v) { StringBuilder b = new StringBuilder(); write(b, v, 0, false); return b.toString(); }

    @SuppressWarnings("unchecked")
    private static void write(StringBuilder b, Object v, int ind, boolean pretty) {
        if (v == null) b.append("null");
        else if (v instanceof String) quote(b, (String) v);
        else if (v instanceof Boolean) b.append(v.toString());
        else if (v instanceof Number) {
            double d = ((Number) v).doubleValue();
            if (d == Math.rint(d) && Math.abs(d) < 1e15) b.append((long) d); else b.append(d);
        } else if (v instanceof Map) {
            Map<String, Object> m = (Map<String, Object>) v;
            b.append('{');
            int n = 0;
            for (Map.Entry<String, Object> e : m.entrySet()) {
                if (n++ > 0) b.append(',');
                if (pretty) { b.append('\n'); pad(b, ind + 1); }
                quote(b, e.getKey());
                b.append(pretty ? ": " : ":");
                write(b, e.getValue(), ind + 1, pretty);
            }
            if (pretty && n > 0) { b.append('\n'); pad(b, ind); }
            b.append('}');
        } else if (v instanceof List) {
            List<Object> l = (List<Object>) v;
            b.append('[');
            for (int k = 0; k < l.size(); k++) {
                if (k > 0) b.append(pretty ? ", " : ",");
                write(b, l.get(k), ind + 1, pretty);
            }
            b.append(']');
        } else quote(b, v.toString());
    }

    private static void pad(StringBuilder b, int n) { for (int k = 0; k < n; k++) b.append("  "); }

    private static void quote(StringBuilder b, String s) {
        b.append('"');
        for (int k = 0; k < s.length(); k++) {
            char c = s.charAt(k);
            switch (c) {
                case '"': b.append("\\\""); break;
                case '\\': b.append("\\\\"); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                default:
                    if (c < 0x20) b.append(String.format("\\u%04x", (int) c)); else b.append(c);
            }
        }
        b.append('"');
    }

    // ------------------------------------------------------------ akses aman
    @SuppressWarnings("unchecked")
    public static Map<String, Object> obj(Map<String, Object> m, String k) {
        Object o = m == null ? null : m.get(k);
        return o instanceof Map ? (Map<String, Object>) o : Collections.<String, Object>emptyMap();
    }

    @SuppressWarnings("unchecked")
    public static List<Object> list(Map<String, Object> m, String k) {
        Object o = m == null ? null : m.get(k);
        return o instanceof List ? (List<Object>) o : Collections.emptyList();
    }

    public static String str(Map<String, Object> m, String k, String def) {
        Object o = m == null ? null : m.get(k);
        return o instanceof String ? (String) o : (o == null ? def : o.toString());
    }

    public static float num(Map<String, Object> m, String k, float def) {
        Object o = m == null ? null : m.get(k);
        return o instanceof Number ? ((Number) o).floatValue() : def;
    }

    public static boolean bool(Map<String, Object> m, String k, boolean def) {
        Object o = m == null ? null : m.get(k);
        return o instanceof Boolean ? (Boolean) o : def;
    }

    public static List<String> strList(Map<String, Object> m, String k) {
        List<String> out = new ArrayList<>();
        Object o = m == null ? null : m.get(k);
        if (o instanceof String) out.add((String) o);
        else if (o instanceof List) for (Object x : (List<?>) o) if (x != null) out.add(x.toString());
        return out;
    }

    public static float[] floats(Object o) {
        if (!(o instanceof List)) return new float[0];
        List<?> l = (List<?>) o;
        float[] f = new float[l.size()];
        for (int k = 0; k < f.length; k++) f[k] = l.get(k) instanceof Number ? ((Number) l.get(k)).floatValue() : 0f;
        return f;
    }

    @SuppressWarnings("unchecked")
    public static List<Map<String, Object>> objList(Map<String, Object> m, String k) {
        List<Map<String, Object>> out = new ArrayList<>();
        for (Object o : list(m, k)) if (o instanceof Map) out.add((Map<String, Object>) o);
        return out;
    }
}
