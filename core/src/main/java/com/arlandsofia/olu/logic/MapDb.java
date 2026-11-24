package com.arlandsofia.olu.logic;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Metadata peta (data/maps.json + data/props.json) dan collision kaki karakter.
 * Semua koordinat dalam piksel gambar peta (y ke bawah).
 */
public final class MapDb {
    public static final float FOOT_W = 18f, FOOT_TOP = 6f, FOOT_BOTTOM = 2f;

    /** cek flag untuk gerbang dinamis (diisi GameScreen / simulasi). Tanpa java.util.function agar aman di API 21. */
    public interface FlagCheck { boolean has(String flag); }
    public static FlagCheck flags = new FlagCheck() { public boolean has(String f) { return false; } };

    /** area yang terhalang sampai flag tertentu aktif (mis. jembatan rusak), atau sebaliknya. */
    public static final class Gate {
        public final float[] rect; public final String openFlag, closeFlag;
        Gate(Map<String, Object> m) { rect = Json.floats(m.get("rect")); openFlag = Json.str(m, "openFlag", null); closeFlag = Json.str(m, "closeFlag", null); }
        public boolean solid() {
            if (openFlag != null) return !flags.has(openFlag);
            return closeFlag != null && flags.has(closeFlag);
        }
    }

    public static final class PropDef {
        public final String id, image, layer; public final float cw, ch;
        PropDef(String id, Map<String, Object> m) {
            this.id = id; image = Json.str(m, "image", ""); layer = Json.str(m, "layer", "sort");
            cw = Json.num(m, "cw", 0); ch = Json.num(m, "ch", 0);
        }
    }

    public static final class Prop {
        public final PropDef def; public final float x, y;
        /** Ganti gambar bila flag aktif (mis. lentera padam -> menyala). */
        public final PropDef alt; public final String altFlag;
        Prop(PropDef def, float x, float y, PropDef alt, String altFlag) { this.def = def; this.x = x; this.y = y; this.alt = alt; this.altFlag = altFlag; }
    }

    public static final class Lock {
        public final List<String> steps; public final Map<String, String> text = new HashMap<>(); public final String plainText;
        /** Terkunci selama kondisi ini benar (alternatif dari daftar steps). */
        public final Map<String, Object> when;
        Lock(Map<String, Object> m) {
            steps = Json.strList(m, "steps");
            when = Json.obj(m, "when");
            Object t = m.get("text");
            if (t instanceof Map) { for (Map.Entry<String, Object> e : Json.obj(m, "text").entrySet()) text.put(e.getKey(), String.valueOf(e.getValue())); plainText = null; }
            else plainText = t == null ? "Terkunci." : t.toString();
        }
        public String text(String route) { String s = text.get(route); return s != null ? s : (plainText != null ? plainText : "Terkunci."); }
    }

    public static final class Door {
        public final String id, label, to, dir, route, routeText;
        public final float x, y, w, h, tx, ty;
        public final List<Lock> locks = new ArrayList<>();
        Door(Map<String, Object> m) {
            id = Json.str(m, "id", "?"); label = Json.str(m, "label", ""); to = Json.str(m, "to", "");
            dir = Json.str(m, "dir", "down"); route = Json.str(m, "route", null); routeText = Json.str(m, "routeText", "Pintu ini terkunci.");
            float[] r = Json.floats(m.get("rect"));
            x = r.length > 0 ? r[0] : 0; y = r.length > 1 ? r[1] : 0; w = r.length > 2 ? r[2] : 0; h = r.length > 3 ? r[3] : 0;
            tx = Json.num(m, "tx", 0); ty = Json.num(m, "ty", 0);
            for (Map<String, Object> l : Json.objList(m, "locked")) locks.add(new Lock(l));
        }
        public boolean touches(float fx, float fy) {
            float x0 = fx - FOOT_W / 2, x1 = fx + FOOT_W / 2, y0 = fy - FOOT_TOP, y1 = fy + FOOT_BOTTOM;
            return x0 < x + w && x1 > x && y0 < y + h && y1 > y;
        }
        /** true bila titik kedatangan di area tujuan langsung menyentuh pintu lain (akan memantul bolak-balik). */
        public boolean touchesAnyDoor(Area to) {
            for (Door o : to.doors) if (o.touches(tx, ty)) return true;
            return false;
        }
        public float cx() { return x + w / 2; }
        public float cy() { return y + h / 2; }
    }

    public static final class Examine {
        public final String id, label; public final float x, y, r;
        public final Map<String, List<StoryDb.Line>> lines = new HashMap<>();
        public final Map<String, Object> when;
        Examine(Map<String, Object> m) {
            id = Json.str(m, "id", "?"); label = Json.str(m, "label", "Periksa");
            when = Json.obj(m, "when");
            x = Json.num(m, "x", 0); y = Json.num(m, "y", 0); r = Json.num(m, "r", 56);
            Map<String, Object> l = Json.obj(m, "lines");
            for (String k : l.keySet()) lines.put(k, StoryDb.lines(l, k));
        }
        public List<StoryDb.Line> lines(String route) { List<StoryDb.Line> l = lines.get(route); return l == null ? new ArrayList<StoryDb.Line>() : l; }
    }

    /** 2.5D terrace footprint and one physically traversable stair ramp.
     * All values use existing y-down map coordinates. Texture is decorative;
     * walkability comes from ElevationV50 and is not a PNG collision mask.
     */
    public static final class Terrace {
        public final String id, image, front, style;
        public final float x, y, w, h, rise, stairWidth, stairLength;
        public Terrace(Map<String,Object> m) {
            id=Json.str(m,"id","");
            x=Json.num(m,"x",0); y=Json.num(m,"y",0);
            w=Json.num(m,"w",0); h=Json.num(m,"h",0);
            rise=Json.num(m,"rise",0);
            stairWidth=Json.num(m,"stairWidth",58);
            stairLength=Json.num(m,"stairLength",90);
            image=Json.str(m,"image","");front=Json.str(m,"front","");
            style=Json.str(m,"style","city");
            if(x<0||y<0||w<60||h<50||rise<1||rise>80||stairLength<35||stairWidth<28
                    ||stairWidth>w*.65f||image.isEmpty()||front.isEmpty())
                throw new IllegalArgumentException("Invalid terrace: "+id);
        }
        public float stairX() {return x+(w-stairWidth)*.5f;}
        public float stairStart() {return y+h-6f;}
        public float stairEnd() {return y+h+stairLength;}
        public boolean top(float px,float py) {return px>=x&&px<=x+w&&py>=y&&py<=y+h;}
        public boolean stairs(float px,float py) {
            return px>=stairX()&&px<=stairX()+stairWidth
                    &&py>=stairStart()&&py<=stairEnd();
        }
    }

    public static final class Area {
        public final String id, name, image, music, ambient;
        public final List<float[]> water = new ArrayList<>();
        /** v5.4 flowing water bands {x, y, w, h, dirX, speed} (y-down, cosmetic only). */
        public final List<float[]> waterFlow = new ArrayList<>();
        /** v5.4 rivers following a centre line: {width, speed, x0, y0, x1, y1, ...} (y-down, cosmetic). */
        public final List<float[]> riverPaths = new ArrayList<>();
        public final boolean indoor;
        public final float w, h, spawnX, spawnY;
        /** Bed spot for sleeping in the route's own room; NaN where the map has none. */
        public final float bedX, bedY;
        public final List<float[]> walls = new ArrayList<>();
        public final List<float[]> ellipses = new ArrayList<>();
        public final List<Prop> props = new ArrayList<>();
        public final List<Door> doors = new ArrayList<>();
        public final List<Gate> gates = new ArrayList<>();
        /** hewan ambient: [{type, n, region:[x,y,w,h] | water:[cx,cy,rx,ry], day}] */
        public final List<Map<String, Object>> animals = new ArrayList<>();
        public final List<Examine> examine = new ArrayList<>();
        public final List<Terrace> terraces = new ArrayList<>();
        Area(String id, Map<String, Object> m, Map<String, PropDef> defs) {
            this.id = id; name = Json.str(m, "name", id); image = Json.str(m, "image", ""); music = Json.str(m, "music", "town");
            ambient = Json.str(m, "ambient", null);
            indoor = Json.bool(m, "indoor", false);
            for (Map<String, Object> w : Json.objList(m, "water"))
                water.add(new float[]{Json.num(w, "cx", 0), Json.num(w, "cy", 0), Json.num(w, "rx", 10), Json.num(w, "ry", 10)});
            for (Map<String, Object> f : Json.objList(m, "waterFlow")) {
                if (f.containsKey("path")) {
                    List<Object> pts = Json.list(f, "path");
                    float[] r = new float[2 + pts.size() * 2];
                    r[0] = Math.max(4f, Json.num(f, "width", 40)); r[1] = Math.max(0f, Math.min(120f, Json.num(f, "speed", 30)));
                    for (int i = 0; i < pts.size(); i++) { float[] xy = Json.floats(pts.get(i)); r[2 + i * 2] = xy[0]; r[3 + i * 2] = xy[1]; }
                    if (pts.size() >= 2) riverPaths.add(r);
                    continue;
                }
                waterFlow.add(new float[]{Json.num(f, "x", 0), Json.num(f, "y", 0), Json.num(f, "w", 0), Json.num(f, "h", 0),
                        Json.num(f, "dx", 1) < 0 ? -1f : 1f, Math.max(0f, Math.min(80f, Json.num(f, "speed", 20)))});
            }
            w = Json.num(m, "w", 960); h = Json.num(m, "h", 640);
            float[] sp = Json.floats(m.get("spawn"));
            spawnX = sp.length > 1 ? sp[0] : w / 2; spawnY = sp.length > 1 ? sp[1] : h / 2;
            float[] bed = Json.floats(m.get("bed"));
            bedX = bed.length > 1 ? bed[0] : Float.NaN; bedY = bed.length > 1 ? bed[1] : Float.NaN;
            for (Object o : Json.list(m, "walls")) walls.add(Json.floats(o));
            for (Object o : Json.list(m, "ellipses")) ellipses.add(Json.floats(o));
            for (Map<String, Object> p : Json.objList(m, "props")) {
                PropDef d = defs.get(Json.str(p, "type", ""));
                PropDef alt = defs.get(Json.str(p, "alt", ""));
                if (d != null) props.add(new Prop(d, Json.num(p, "x", 0), Json.num(p, "y", 0), alt, Json.str(p, "altFlag", null)));
            }
            for (Map<String, Object> d : Json.objList(m, "doors")) doors.add(new Door(d));
            for (Map<String, Object> g : Json.objList(m, "gates")) gates.add(new Gate(g));
            animals.addAll(Json.objList(m, "animals"));
            for (Map<String, Object> e : Json.objList(m, "examine")) examine.add(new Examine(e));
            for (Map<String, Object> v : Json.objList(m, "elevationPlatforms")) terraces.add(new Terrace(v));
            for (Prop p : props) if (p.def.cw > 0 && p.def.ch > 0) walls.add(new float[]{p.x - p.def.cw / 2, p.y - p.def.ch, p.def.cw, p.def.ch});
        }

        /** true bila kotak kaki di (x,y) menabrak dinding/prop/tepi peta. */
        public boolean blocked(float x, float y) {
            float x0 = x - FOOT_W / 2, x1 = x + FOOT_W / 2, y0 = y - FOOT_TOP, y1 = y + FOOT_BOTTOM;
            if (x0 < 0 || y0 < 0 || x1 > w || y1 > h) return true;
            for (float[] r : walls) {
                if (r.length < 4) continue;
                if (x0 < r[0] + r[2] && x1 > r[0] && y0 < r[1] + r[3] && y1 > r[1]) return true;
            }
            for (Gate g : gates) {
                float[] r = g.rect;
                if (r.length >= 4 && x0 < r[0] + r[2] && x1 > r[0] && y0 < r[1] + r[3] && y1 > r[1] && g.solid()) return true;
            }
            for (float[] e : ellipses) {
                if (e.length < 4) continue;
                if (inEllipse(x0, y0, e) || inEllipse(x1, y0, e) || inEllipse(x0, y1, e) || inEllipse(x1, y1, e) || inEllipse(x, y, e)) return true;
            }
            return false;
        }

        private static boolean inEllipse(float px, float py, float[] e) {
            float dx = (px - e[0]) / e[2], dy = (py - e[1]) / e[3];
            return dx * dx + dy * dy < 1f;
        }
    }

    public final Map<String, Area> areas = new LinkedHashMap<>();
    public final Map<String, PropDef> propDefs = new HashMap<>();

    public MapDb(String mapsJson, String propsJson) {
        Map<String, Object> pr = Json.obj(Json.parseObject(propsJson), "props");
        for (String k : pr.keySet()) propDefs.put(k, new PropDef(k, Json.obj(pr, k)));
        Map<String, Object> ar = Json.obj(Json.parseObject(mapsJson), "areas");
        for (String k : ar.keySet()) areas.put(k, new Area(k, Json.obj(ar, k), propDefs));
    }

    public Area area(String id) { return areas.get(id); }
}
