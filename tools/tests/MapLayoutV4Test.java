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
            ok(Math.abs(loaded.x-600f)<0.01f && Math.abs(loaded.y-448f)<0.01f,"migrated "+areas[i]);
            ok(loaded.coins==42 && loaded.flags.contains("SAMPLE"),"state preserved "+areas[i]);
            Progress saved=Progress.fromMap(loaded.toMap(false));
            ok(Math.abs(saved.x-loaded.x)<0.01f && Math.abs(saved.y-loaded.y)<0.01f,"no double migration "+areas[i]);
        }
        float[] unchanged=MapLayoutV4.fromLegacy("plaza",560f,620f);
        ok(unchanged[0]==560f && unchanged[1]==620f,"unaffected maps unchanged");
        ok(Progress.SCHEMA==8,"schema8");
        System.out.println("V4 SAVE MIGRATION PASSED: "+checks+" assertions");
    }
}
