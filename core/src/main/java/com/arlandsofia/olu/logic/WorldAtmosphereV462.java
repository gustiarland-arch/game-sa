package com.arlandsofia.olu.logic;

/**
 * Non-invasive rendering plan for the original 22 areas plus new story maps. Pure Java, no textures,
 * no collision changes, no quest or save changes. Quality 0 skips extra passes.
 */
public final class WorldAtmosphereV462 {
    public static final int HOME=0, CITY=1, GARDEN=2, WATER=3, STAR=4, CAVE=5;
    private static final String[] IDS={
        "arland_room","sofia_room","plaza","jalan_kota","taman_kota",
        "riverside","cafe","dapur","toko_bunga","arcade","memory_garden",
        "lantern_field","star_path","starfall_village","eternal_garden",
        "perumahan","perpustakaan","ruang_arsip","galeri_komunitas","dermaga",
        "hutan_bisik","bukit_bintang","gua_kristal","rain_garden",
        "clockwork_station","moonlight_lake","memory_bridge","hall_of_tomorrow","ruang_dua_surat"
    };
    private static final int[] TYPES={
        HOME,HOME,CITY,CITY,GARDEN,WATER,HOME,HOME,HOME,HOME,GARDEN,
        STAR,STAR,STAR,GARDEN,CITY,HOME,HOME,HOME,WATER,GARDEN,STAR,CAVE,GARDEN,
        STAR,WATER,STAR,STAR,HOME
    };
    private WorldAtmosphereV462() {}
    public static int count() { return IDS.length; }
    public static String areaId(int i) { return IDS[i]; }
    public static int type(String areaId) {
        if(areaId==null)return CITY;
        for(int i=0;i<IDS.length;i++)if(IDS[i].equals(areaId))return TYPES[i];
        return CITY;
    }
    public static boolean isMapped(String areaId) {
        if(areaId==null)return false;
        for(String id:IDS)if(id.equals(areaId))return true;
        return false;
    }
    public static int particleCount(int quality,boolean indoors,int type) {
        if(quality<=0)return 0;
        int max=quality==2?22:9;
        if(indoors||type==HOME||type==CAVE)max/=2;
        return max;
    }
    public static boolean fireflies(int type,boolean indoor,boolean rainy,int minute) {
        return !indoor&&!rainy && WorldClock.isNight(minute) &&
                (type==GARDEN||type==STAR||type==WATER);
    }
    public static float mistAlpha(int type,boolean indoor,boolean rainy,int minute) {
        if(indoor||type==HOME||type==CAVE)return 0f;
        int h=WorldClock.hour(minute);
        boolean dawn=(h>=5&&h<=8);
        if(type==WATER||type==GARDEN)return rainy?0.30f:dawn?0.24f:0.07f;
        if(type==STAR)return rainy?0.20f:dawn?0.13f:0f;
        return rainy?0.19f:dawn?0.08f:0f;
    }
    public static float sunbeamAlpha(int type,boolean indoor,boolean rainy,int minute) {
        if(indoor||rainy||type==HOME||type==CAVE||WorldClock.isNight(minute))return 0f;
        int hour=WorldClock.hour(minute);
        float hourBias=(hour>=6&&hour<=9)||(hour>=16&&hour<=18)?1f:0.4f;
        return (type==GARDEN||type==WATER?0.28f:0.16f)*hourBias;
    }
    /** Hash without Random allocation. Used to keep particles deterministic. */
    public static float frac(int index,int salt) {
        int n=index*0x1f123bb5+salt*0x749a4b2b;
        n^=(n>>>15); n*=0x2c1b3c6d; n^=(n>>>12);
        return (n & 0x7fffffff)/2147483648f;
    }
}
