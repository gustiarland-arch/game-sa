package com.arlandsofia.olu.game;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.logic.WorldAtmosphereV462;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.math.MathUtils;

/**
 * Partikel visual prosedural: jejak langkah, percikan hujan, hati kecil saat
 * companion dekat, kelopak foreground. Tidak menyimpan state gameplay.
 * Semua partikel memakai fixed pool agar tidak membuat objek setiap frame.
 */
public final class WorldFx {
    private static final int MAX = 48;
    private static final int DUST = 0, SPLASH = 1, HEART = 2;
    private final float[] px = new float[MAX], py = new float[MAX];
    private final float[] vx = new float[MAX], vy = new float[MAX];
    private final float[] life = new float[MAX], duration = new float[MAX];
    private final int[] type = new int[MAX];
    private final Texture dust, splash, heart, petal, ripple, vignette;
    private final Texture mist462, beam462, leaf462, blossom462, fly462, glint462, rain462;
    private float footTime, loveTime;
    private int next;

    public WorldFx(Assets assets) {
        dust = assets.tex("fx/dust.png");
        splash = assets.tex("fx/splash.png");
        heart = assets.tex("fx/heart.png");
        petal = assets.tex("fx/petal.png");
        ripple = assets.tex("fx/ripple.png");
        vignette = assets.tex("fx/vignette.png");
        mist462 = assets.tex("fx/v462_mist.png");
        beam462 = assets.tex("fx/v462_sunbeam.png");
        leaf462 = assets.tex("fx/v462_leaf.png");
        blossom462 = assets.tex("fx/v462_blossom.png");
        fly462 = assets.tex("fx/v462_firefly.png");
        glint462 = assets.tex("fx/v462_water_glint.png");
        rain462 = assets.tex("fx/v462_raindrop.png");
    }

    public void reset() {
        for (int i = 0; i < MAX; i++) life[i] = 0f;
        footTime = 0f;
        loveTime = 0f;
        next = 0;
    }

    private void emit(int which, float x, float y) {
        int i = next;
        next = (next + 1) % MAX;
        px[i] = x + MathUtils.random(-5f, 5f);
        py[i] = y + MathUtils.random(0f, 3f);
        vx[i] = MathUtils.random(-8f, 8f);
        vy[i] = which == HEART ? MathUtils.random(9f, 16f) : MathUtils.random(1f, 8f);
        type[i] = which;
        duration[i] = which == DUST ? 0.52f : which == SPLASH ? 0.37f : 1.2f;
        life[i] = duration[i];
    }

    public void update(float dt, float x, float y, boolean walking, boolean sprinting,
                       boolean raining, boolean indoors, float partnerX, float partnerY,
                       boolean together, int affection, int quality) {
        for (int i = 0; i < MAX; i++) {
            if (life[i] <= 0f) continue;
            life[i] = Math.max(0f, life[i] - dt);
            px[i] += vx[i] * dt;
            py[i] += vy[i] * dt;
        }
        if (walking) {
            footTime -= dt;
            if (footTime <= 0f) {
                if (quality > 0) emit(raining && !indoors ? SPLASH : DUST, x, y);
                footTime = sprinting ? 0.11f : 0.19f;
            }
        } else footTime = 0f;
        if (quality == 2 && together && affection >= 80 && !walking && !raining &&
                Math.abs(partnerX - x) < 68f && Math.abs(partnerY - y) < 55f) {
            loveTime -= dt;
            if (loveTime <= 0f) {
                emit(HEART, (x + partnerX) * 0.5f, (y + partnerY) * 0.5f + 43f);
                loveTime = 4.2f;
            }
        } else loveTime = 1.2f;
    }

    public void draw(SpriteBatch batch, int quality) {
        if (quality == 0) return;
        for (int i = 0; i < MAX; i++) {
            if (life[i] <= 0f) continue;
            float f = life[i] / duration[i];
            Texture texture = type[i] == DUST ? dust : type[i] == SPLASH ? splash : heart;
            float size = type[i] == DUST ? 16f : type[i] == SPLASH ? 19f : 13f;
            if (type[i] == DUST) batch.setColor(0.90f, 0.84f, 0.78f, f * 0.54f);
            else if (type[i] == SPLASH) batch.setColor(0.77f, 0.91f, 1f, f * 0.84f);
            else batch.setColor(1f, 1f, 1f, f * 0.70f);
            batch.draw(texture, px[i] - size * 0.5f, py[i], size, size);
        }
        batch.setColor(1f, 1f, 1f, 1f);
    }

    /**
     * World polish v2.3: palette-aware, low-cost moving dust, soft sun flecks, and
     * celestial sparks. Rendered BEHIND actors/props. Screen-local deterministic
     * coordinates prevent new per-frame allocations or extra map textures.
     */
    public void drawSceneAtmosphere(SpriteBatch batch, Texture pixel, Texture bloom, Texture sparkle,
                                    String areaId, boolean indoor, float mapHeight,
                                    float cameraX, float cameraY, float vw, float vh,
                                    float time, int quality, boolean night) {
        if (quality == 0 || areaId == null) return;
        boolean cave = "gua_kristal".equals(areaId);
        boolean library = "perpustakaan".equals(areaId) || "ruang_arsip".equals(areaId);
        boolean starRealm = areaId.contains("star") || "bukit_bintang".equals(areaId);
        boolean garden = areaId.contains("garden") || areaId.contains("taman") || areaId.contains("hutan");
        float left = cameraX - vw * 0.5f, bottom = cameraY - vh * 0.5f;
        int n = quality == 2 ? 18 : 8;
        float seed = Math.abs(areaId.hashCode() % 1637);
        if (!cave && !indoor && quality == 2) {
            // Slow moving diffuse light patches: intensity depends on night and area mood.
            for (int i = 0; i < 3; i++) {
                float u = ((i * 0.318f + seed * 0.001f + time * 0.004f) % 1f);
                float v = ((i * 0.481f + seed * 0.002f) % 1f);
                float size = garden ? 76f : 52f;
                if (starRealm || night) batch.setColor(0.63f, 0.78f, 1f, 0.075f);
                else batch.setColor(1f, 0.94f, 0.69f, 0.11f);
                batch.draw(bloom, left + u * vw - size / 2f, bottom + v * vh - size / 2f, size, size);
            }
        }
        for (int i = 0; i < n; i++) {
            float u = (i * 0.618034f + seed * 0.0071f + time * (indoor ? 0.006f : 0.013f) * (1 + i % 3)) % 1f;
            float v = (i * 0.381966f + seed * 0.0037f + MathUtils.sin(time * 0.31f + i) * 0.045f) % 1f;
            if (u < 0f) u += 1f; if (v < 0f) v += 1f;
            float a = 0.25f + 0.35f * (0.5f + 0.5f * MathUtils.sin(time * 1.4f + i * 2f));
            if (cave) batch.setColor(0.59f, 0.85f, 1f, a);
            else if (starRealm || library) batch.setColor(0.94f, 0.87f, 1f, a);
            else if (garden) batch.setColor(1f, 0.89f, 0.72f, a * 0.65f);
            else batch.setColor(1f, 0.97f, 0.88f, a * 0.43f);
            float size = i % 5 == 0 ? 5.5f : 2.8f;
            batch.draw(i % 5 == 0 ? sparkle : pixel, left + u * vw, bottom + v * vh, size, size);
        }
        batch.setColor(1f, 1f, 1f, 1f);
    }

    /** Foreground parallax di ruang bintang/bunga; tidak dipakai pada preset Hemat. */
    public void drawForeground(SpriteBatch batch, float left, float bottom, float width, float height,
                               String ambient, float time, int quality) {
        if (quality == 0 || !"petals".equals(ambient)) return;
        int n = quality == 2 ? 11 : 4;
        for (int i = 0; i < n; i++) {
            float x = ((i * 0.618034f + time * (0.016f + i % 3 * 0.003f)) % 1f) * (width + 40f) - 20f;
            float y = ((i * 0.379f - time * (0.018f + i % 4 * 0.003f)) % 1f + 1f) % 1f * height;
            float size = (i % 3 == 0 ? 22f : 13f);
            batch.setColor(1f, 1f, 1f, 0.46f + 0.17f * MathUtils.sin(time * 1.2f + i));
            batch.draw(petal, left + x, bottom + y, size, size * 0.75f);
        }
        batch.setColor(1f, 1f, 1f, 1f);
    }

    /** Riap kecil berulang di permukaan air; koordinat dipasok dari peta. */
    public void drawRipples(SpriteBatch batch, float cx, float cy, float rx, float ry,
                            float time, int quality, boolean rain) {
        if (quality == 0) return;
        int n = rain ? (quality == 2 ? 13 : 7) : (quality == 2 ? 5 : 2);
        for (int i = 0; i < n; i++) {
            float phase = ((time * (rain ? 0.65f : 0.26f) + i * 0.317f) % 1f + 1f) % 1f;
            float u = ((i * 0.61803f) % 1f) * 1.6f - 0.8f;
            float v = ((i * 0.38197f) % 1f) * 1.6f - 0.8f;
            if (u * u + v * v > 0.75f) continue;
            float s = 0.55f + phase * 0.9f;
            batch.setColor(0.78f, 0.95f, 1f, (1f - phase) * (rain ? 0.58f : 0.30f));
            batch.draw(ripple, cx + u * rx - 18f * s, cy + v * ry - 6f * s, 36f * s, 12f * s);
        }
        batch.setColor(1f, 1f, 1f, 1f);
    }

    /** v4.6.2 living world: distant time-of-day sunbeams and ground mist,
     *  rendered behind actors. Texture tint never mutates gameplay geometry.
     */
    public void drawWorldBackdropV462(SpriteBatch batch, String areaId, boolean indoors,
            boolean rainy, int minute, float cx,float cy,float vw,float vh,
            float time,int quality) {
        if(quality<=0)return;
        int kind=WorldAtmosphereV462.type(areaId);
        float fog=WorldAtmosphereV462.mistAlpha(kind,indoors,rainy,minute);
        float rays=WorldAtmosphereV462.sunbeamAlpha(kind,indoors,rainy,minute);
        float left=cx-vw*0.5f,bottom=cy-vh*0.5f;
        if(fog>0) {
            int bands=quality==2?5:2;
            for(int i=0;i<bands;i++) {
                float drift=MathUtils.sin(time*0.13f+i*2.9f)*28f;
                float x=left+(i+0.2f)*vw/bands-125f+drift;
                float y=bottom+30f+(i%3)*45f;
                batch.setColor(0.78f,0.90f,1f,Math.min(0.34f,fog*(0.80f+0.2f*MathUtils.sin(time*0.6f+i))));
                batch.draw(mist462,x,y,256f,64f);
            }
        }
        if(rays>0 && quality==2) {
            for(int i=0;i<3;i++) {
                float x=left+vw*(0.15f+i*0.33f);
                batch.setColor(1f,0.95f,0.76f,rays*(0.83f+MathUtils.sin(time*0.32f+i)*0.16f));
                batch.draw(beam462,x,bottom+vh*0.25f,64f,vh*0.78f);
            }
        }
        batch.setColor(1,1,1,1);
    }

    /** Foreground weather and landmark mood: fireflies, leaves, blossom drift
     * and bright raindrops. Fixed draw budget; no per-frame allocations.
     * Runtime overlays apply to all 22 area IDs without repainting source maps. */
    public void drawWorldForegroundV462(SpriteBatch batch, String areaId, boolean indoors,
            boolean rainy, boolean windy, int minute, float cx,float cy,float vw,float vh,
            float time,int quality) {
        if(quality<=0)return;
        int kind=WorldAtmosphereV462.type(areaId);
        int particles=WorldAtmosphereV462.particleCount(quality,indoors,kind);
        float left=cx-vw*0.5f,bottom=cy-vh*0.5f;
        int salt=areaId==null?0:areaId.hashCode();
        boolean twinkle=WorldAtmosphereV462.fireflies(kind,indoors,rainy,minute);
        boolean petals=(kind==WorldAtmosphereV462.GARDEN||kind==WorldAtmosphereV462.STAR);
        if(indoors && !twinkle)particles=Math.min(6,particles);
        for(int i=0;i<particles;i++) {
            float u=WorldAtmosphereV462.frac(i,salt);
            float v=WorldAtmosphereV462.frac(i+109,salt);
            float x=left+((u+time*(windy?0.025f:0.008f)*(1+i%3))%1f)*vw;
            float y=bottom+((v-time*(windy?0.013f:0.006f)*(1+i%2))%1f+1f)%1f*vh;
            if(twinkle) {
                float alpha=0.45f+0.45f*MathUtils.sin(time*1.5f+i*1.7f);
                batch.setColor(1f,1f,0.84f,alpha);
                float sz=i%4==0?15f:10f;
                batch.draw(fly462,x,y,sz,sz);
            } else if(!indoors && windy) {
                batch.setColor(1f,1f,1f,0.55f+0.18f*MathUtils.sin(time*2f+i));
                float sz=petals?12f:10f;
                batch.draw(petals?blossom462:leaf462,x,y,sz,sz);
            } else if(!indoors && petals && !rainy) {
                batch.setColor(1f,0.94f,0.95f,0.30f);
                batch.draw(blossom462,x,y,8f,8f);
            } else if(!indoors && rainy) {
                batch.setColor(0.86f,0.94f,1f,quality==2?0.62f:0.45f);
                batch.draw(rain462,x,y,4f,17f);
            } else if(indoors && i%2==0) {
                batch.setColor(1f,0.89f,0.72f,0.15f);
                batch.draw(blossom462,x,y,4f,4f);
            }
        }
        batch.setColor(1,1,1,1);
    }

    /** Tiny water glints overlay existing animated ripples, not collision water polygons. */
    public void drawWaterGlintsV462(SpriteBatch batch,float cx,float cy,float rx,float ry,
            float time,int quality,boolean rainy) {
        if(quality<=0)return;
        int n=quality==2?9:3;
        for(int i=0;i<n;i++) {
            float u=WorldAtmosphereV462.frac(i,13)*2f-1f;
            float v=WorldAtmosphereV462.frac(i+17,31)*2f-1f;
            if(u*u+v*v>0.84f)continue;
            float pulse=0.25f+0.5f*Math.abs(MathUtils.sin(time*1.5f+i*2f));
            batch.setColor(0.85f,0.95f,1f,rainy?pulse*0.25f:pulse*0.65f);
            batch.draw(glint462,cx+u*rx-10f,cy+v*ry-4f,20f,10f);
        }
        batch.setColor(1,1,1,1);
    }

    public void drawVignette(SpriteBatch batch, float left, float bottom, float width, float height, int quality) {
        if (quality < 2) return;
        batch.setColor(1f, 1f, 1f, 0.68f);
        batch.draw(vignette, left, bottom, width, height);
        batch.setColor(1f, 1f, 1f, 1f);
    }
}
