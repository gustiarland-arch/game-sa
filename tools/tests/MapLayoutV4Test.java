package com.arlandsofia.olu.logic;

import java.util.Map;

/** Headless regression: v3 saves migrate spatial coordinates, not story/inventory. */
public final class MapLayoutV4Test {
    private static int checks;
    private static void ok(boolean b, String why) {
        ++checks; if (!b) throw new IllegalStateException("V4 save migration: " + why);
    }
    public static void main(String[] args) {
        String[] areas = {"jalan_kota","perumahan","perpustakaan","arcade","toko_bunga",
                          "arland_room","sofia_room","dapur","ruang_arsip"};
        float[][] oldSize = {{2048,1024},{2048,1152},{1280,768},{960,640},{960,640},
                             {960,640},{960,640},{960,640},{800,560}};
        for (int i=0;i<areas.length;i++) {
            float[] xy = MapLayoutV4.fromLegacy(areas[i],oldSize[i][0]/2f,oldSize[i][1]/2f);
            ok(Math.abs(xy[0]-600f)<0.01f && Math.abs(xy[1]-448f)<0.01f,areas[i]);
            Progress p = new Progress();p.route="arland";p.slot=1;p.step="PRO_PHONE";p.area=areas[i];
            p.x=oldSize[i][0]/2f;p.y=oldSize[i][1]/2f;p.coins=42;p.flags.add("SAMPLE");
            Map<String,Object> legacy=p.toMap(false);
            legacy.put("schema",7);legacy.remove("mapLayoutVersion");
            Progress loaded=Progress.fromMap(legacy);
            // v5.4: rescaled interiors continue through MapLayoutV54 (x0.5).
            float ex=MapLayoutV54.scaledRoom(areas[i])?300f:600f, ey=MapLayoutV54.scaledRoom(areas[i])?224f:448f;
            ok(Math.abs(loaded.x-ex)<0.01f && Math.abs(loaded.y-ey)<0.01f,"migrated "+areas[i]);
            ok(loaded.coins==42 && loaded.flags.contains("SAMPLE"),"state preserved "+areas[i]);
            Progress saved=Progress.fromMap(loaded.toMap(false));
            ok(Math.abs(saved.x-loaded.x)<0.01f && Math.abs(saved.y-loaded.y)<0.01f,"no double migration "+areas[i]);
        }
        float[] unchanged=MapLayoutV4.fromLegacy("plaza",560f,620f);
        ok(unchanged[0]==560f && unchanged[1]==620f,"unaffected maps unchanged");
        ok(Progress.SCHEMA==8,"schema8");
        // v4-layout saves (mapLayoutVersion 4) inside rescaled rooms move by exactly 0.5.
        Progress v4=new Progress();v4.route="sofia";v4.slot=2;v4.step="PRO_PHONE";v4.area="sofia_room";v4.x=609;v4.y=783;
        Map<String,Object> m4=v4.toMap(false);m4.put("mapLayoutVersion",4);
        Progress l4=Progress.fromMap(m4);
        ok(Math.abs(l4.x-304.5f)<0.01f && Math.abs(l4.y-391.5f)<0.01f,"v4 room save to v5.4");
        Map<String,Object> m4p=v4.toMap(false);m4p.put("mapLayoutVersion",4);m4p.put("area","plaza");
        Progress lp=Progress.fromMap(m4p);
        ok(lp.x==609f && lp.y==783f,"v4 outdoor save unchanged");
        System.out.println("V4 SAVE MIGRATION PASSED: "+checks+" assertions");
    }
}
