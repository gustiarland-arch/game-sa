package com.arlandsofia.olu.logic;

/**
 * Per-character visual movement. NPC physical collision remains unchanged:
 * visualScale affects the sprite only, stride and cadence affect animation only.
 * No new save data is required.
 */
public final class MotionPersonalityV53 {
    private MotionPersonalityV53() {}

    public static final class Style {
        public final float walkSpeed, cadence, bounce, sway, visualScale;
        public final float breathing, phase;
        public final String daytimePose, eveningPose;
        private Style(float walkSpeed,float cadence,float bounce,float sway,float visualScale,
                      float breathing,float phase,String daytimePose,String eveningPose) {
            this.walkSpeed=walkSpeed;this.cadence=cadence;this.bounce=bounce;this.sway=sway;
            this.visualScale=visualScale;this.breathing=breathing;this.phase=phase;
            this.daytimePose=daytimePose;this.eveningPose=eveningPose;
        }
    }

    /** Named NPC characteristics: readable differences without rewriting quest logic. */
    public static Style forCharacter(String id) {
        if (id == null) id="";
        switch(id) {
            case "arland": return new Style(1f,1.06f,1.15f,.95f,1f,1f,.7f,"ponder","wave");
            case "sofia":  return new Style(1f,.96f,.82f,.72f,1f,.85f,2.2f,"read","wave");
            case "raka":   return new Style(1.02f,1.03f,.74f,.75f,1.03f,.92f,1.0f,"give","read");
            case "rini":   return new Style(1.03f,1.08f,.86f,.83f,1.00f,.80f,3.5f,"give","wave");
            case "sari":   return new Style(.70f,.80f,.34f,.36f,.95f,.63f,5.0f,"read","sit");
            case "melati": return new Style(.88f,.92f,.65f,.60f,1.02f,.80f,2.1f,"water","read");
            case "tigor":  return new Style(1.08f,.92f,.53f,.57f,1.10f,1f,4.8f,"reach","sit");
            case "laras":  return new Style(.86f,.92f,.45f,.45f,.99f,.62f,1.7f,"read","read");
            case "dito":   return new Style(1.22f,1.23f,1.50f,1.19f,.98f,1.15f,2.5f,"cheer","wave");
            case "wulan":  return new Style(.90f,.88f,.60f,.55f,1f,.70f,4.2f,"read","sit");
            case "juna":   return new Style(1.10f,1.13f,1.17f,1.00f,1.04f,1.10f,1.3f,"wave","cheer");
            case "bimo":   return new Style(1.14f,1.15f,1.32f,1.21f,1f,1.18f,3.0f,"cheer","wave");
            case "tika":   return new Style(1.12f,1.14f,1.19f,.87f,.98f,.92f,2.9f,"wave","read");
            case "darto":  return new Style(.93f,.87f,.42f,.46f,1.08f,.72f,3.8f,"sweep","reach");
            case "harun":  return new Style(.83f,.89f,.59f,.56f,1.03f,.81f,1.6f,"water","sit");
            case "ujang":  return new Style(1.18f,1.16f,1.15f,1.14f,1.02f,1.06f,5.2f,"reach","wave");
            case "ina":    return new Style(.96f,.98f,.77f,.73f,.99f,.91f,1.9f,"give","sit");
            case "pos":    return new Style(1.14f,1.09f,1.10f,.94f,1.04f,.98f,4.5f,"give","wave");
            case "nara":   return new Style(.94f,.94f,.71f,.68f,1.00f,.83f,3.7f,"read","wave");
            case "bayu":   return new Style(1.16f,1.12f,1.25f,1.08f,1.03f,1.12f,1.5f,"reach","wave");
            case "eko":    return new Style(.98f,1.00f,.79f,.80f,1.06f,.93f,4.0f,"sweep","sit");
            case "darmo":  return new Style(.74f,.77f,.35f,.38f,.99f,.62f,5.1f,"read","sit");
            case "rara":   return new Style(1.18f,1.20f,1.33f,1.10f,.97f,1.08f,2.4f,"cheer","wave");
            case "udin":   return new Style(.91f,.87f,.67f,.65f,1.02f,.91f,3.3f,"water","sit");
            case "lumi":   return new Style(1.06f,1.11f,1.60f,.82f,.95f,1.38f,0f,"wave","wave");
            default: {
                int h=id.hashCode() & Integer.MAX_VALUE;
                return new Style(.92f+(h%21)*.01f,.92f+((h/7)%17)*.01f,
                    .75f+((h/13)%31)*.01f,.7f,1f,1f,(h%60)*.1f,"wave","sit");
            }
        }
    }

    /** Group-specific routines that vary by hour while preserving existing NPC schedules. */
    public static String idlePose(String id,int hour,String weather,boolean indoor,int day) {
        Style profile=forCharacter(id);
        if (!indoor && ("hujan".equals(weather)||"rain".equals(weather))) {
            if ("sari".equals(id)||"darmo".equals(id)) return "read";
            return ((id.hashCode()+day)&1)==0 ? "sit" : "ponder";
        }
        if (hour>=20 || hour<6) return profile.eveningPose;
        // Secondary gesture varies daily to avoid synchronized identically-looped crowds.
        if ((Math.floorMod(day + id.hashCode(),5)==0) && hour>=11 && hour<=16)
            return "wave";
        return profile.daytimePose;
    }

    public static float pauseSeconds(String id,int day,int minute) {
        int hash= id==null ? 0 : id.hashCode() & Integer.MAX_VALUE;
        float base=2.4f + (hash%23)*.14f;
        float fluctuation=Math.floorMod(day*31+minute/15+hash,11)*.19f;
        return base+fluctuation;
    }
}
