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
    private final Texture[] puddle54 = new Texture[3];
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
        for (int i = 0; i < puddle54.length; i++) puddle54[i] = assets.tex("fx/v54_puddle_" + i + ".png");
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

    /** v5.4: a stronger splash when a foot lands in a puddle. */
    public void splashAt(float x, float y, int quality) {
        if (quality == 0) return;
        for (int k = 0; k < (quality == 2 ? 3 : 2); k++) emit(SPLASH, x, y);
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

    // ------------------------------------------------------------------ v5.4 water & storm

    private static float hash(int a, int b) {
        int h = a * 374761393 + b * 668265263;
        h = (h ^ (h >>> 13)) * 1274126177;
        return ((h ^ (h >>> 16)) & 0xffffff) / (float) 0x1000000;
    }

    /**
     * v5.4 surface current on lakes/rivers: world-anchored light streaks drift along the
     * flow and fade at both ends of their cycle, plus a lapping foam line at the shore.
     * Rect is y-up world space; only cells inside the view are touched.
     */
    public void drawFlowV54(SpriteBatch batch, Texture pixel, float x, float bottom, float w, float h,
                            float dir, float speed, float time, int quality, boolean rain,
                            float viewL, float viewB, float viewW, float viewH) {
        if (speed <= 0f || w <= 0f || h <= 0f) return;
        final float CW = 96f, CH = 30f;
        int per = quality == 2 ? 3 : quality == 1 ? 2 : 1;
        int c0 = (int) Math.floor((Math.max(x, viewL - CW) - x) / CW), c1 = (int) Math.floor((Math.min(x + w, viewL + viewW + CW) - x) / CW);
        int r0 = (int) Math.floor((Math.max(bottom, viewB - CH) - bottom) / CH), r1 = (int) Math.floor((Math.min(bottom + h, viewB + viewH + CH) - bottom) / CH);
        float rainDim = rain ? 0.7f : 1f;
        for (int cy = Math.max(0, r0); cy <= r1; cy++) {
            for (int cx = Math.max(0, c0); cx <= c1; cx++) {
                for (int j = 0; j < per; j++) {
                    float a = hash(cx * 7 + j, cy), b = hash(cy * 13 + j, cx + 101), c = hash(cx + j * 31, cy * 17 + 7);
                    float sp = speed * (0.7f + 0.6f * c);
                    float f = ((a + time * sp / CW) % 1f + 1f) % 1f;
                    if (dir < 0) f = 1f - f;
                    float sx = x + cx * CW + f * CW, sy = bottom + cy * CH + b * CH;
                    if (sy > bottom + h - 4f || sx > x + w) continue;
                    float len = Math.round(6f + c * 12f);
                    float alpha = MathUtils.sin(f * 3.1415927f) * (0.20f + 0.22f * c) * rainDim;
                    if (quality == 2) {
                        batch.setColor(0.10f, 0.30f, 0.50f, alpha * 0.55f);
                        batch.draw(pixel, Math.round(sx), Math.round(sy) - 1, len, 1);
                    }
                    batch.setColor(0.86f, 0.95f, 1f, alpha);
                    batch.draw(pixel, Math.round(sx), Math.round(sy), len, 1);
                }
            }
        }
        // Lapping foam along the shore (top edge of the band in y-up space).
        float shore = bottom + h;
        if (shore >= viewB - 8f && shore <= viewB + viewH + 8f) {
            int i0 = (int) Math.floor(Math.max(x, viewL) / 22f), i1 = (int) Math.floor(Math.min(x + w, viewL + viewW) / 22f);
            for (int i = i0; i <= i1; i++) {
                float wave = MathUtils.sin(time * 1.5f + i * 0.73f);
                float fy = shore - 4f - (1f + wave) * 2.5f;
                float al = 0.30f + 0.22f * wave;
                batch.setColor(0.93f, 0.98f, 1f, al);
                batch.draw(pixel, i * 22f + Math.round(hash(i, 5) * 8f), Math.round(fy), 6 + Math.round(hash(i, 9) * 6f), 1);
            }
        }
        batch.setColor(1f, 1f, 1f, 1f);
    }

    /**
     * v5.4 river current along a centre line {width, speed, x0, y0, ...} (y-down map
     * coordinates). Streaks are world-anchored per 40 px of river length, slide
     * downstream and fade at both ends of their cycle; only visible stretches draw.
     */
    public void drawRiverV54(SpriteBatch batch, Texture pixel, float[] r, float mapH, float time, int quality,
                             boolean rain, float viewL, float viewB, float viewW, float viewH) {
        if (r == null || r.length < 6 || r[1] <= 0f) return;
        final float CL = 40f;
        float width = r[0], speed = r[1];
        int per = quality == 2 ? 4 : quality == 1 ? 3 : 1;
        float rainDim = rain ? 0.75f : 1f;
        int seg = 0;
        for (int i = 2; i + 3 < r.length; i += 2, seg++) {
            float x0 = r[i], y0 = mapH - r[i + 1], x1 = r[i + 2], y1 = mapH - r[i + 3];
            float minX = Math.min(x0, x1) - width, maxX = Math.max(x0, x1) + width;
            float minY = Math.min(y0, y1) - width, maxY = Math.max(y0, y1) + width;
            if (maxX < viewL || minX > viewL + viewW || maxY < viewB || minY > viewB + viewH) continue;
            float dx = x1 - x0, dy = y1 - y0, len = (float) Math.sqrt(dx * dx + dy * dy);
            if (len < 1f) continue;
            float ux = dx / len, uy = dy / len, nx = -uy, ny = ux;
            boolean vertical = Math.abs(uy) > Math.abs(ux);
            int cells = (int) Math.ceil(len / CL);
            for (int c = 0; c < cells; c++) {
                for (int j = 0; j < per; j++) {
                    float a = hash(seg * 131 + c, j), b = hash(c + 17, seg * 7 + j), k = hash(seg + j * 29, c * 3 + 1);
                    float f = ((a + time * speed * (0.75f + 0.5f * k) / CL) % 1f + 1f) % 1f;
                    float along = c * CL + f * CL;
                    if (along > len) continue;
                    float lat = (b - 0.5f) * width * 0.78f;
                    float sx = x0 + ux * along + nx * lat, sy = y0 + uy * along + ny * lat;
                    float sl = Math.round(5f + k * 9f);
                    float alpha = MathUtils.sin(f * 3.1415927f) * (0.26f + 0.24f * k) * rainDim;
                    batch.setColor(0.88f, 0.96f, 1f, alpha);
                    if (vertical) batch.draw(pixel, Math.round(sx), Math.round(sy), 1, sl);
                    else batch.draw(pixel, Math.round(sx), Math.round(sy), sl, 1);
                }
            }
            // Bank foam: tiny white flecks drifting on both edges.
            if (quality > 0) {
                for (int c = 0; c < cells; c++) {
                    float f = ((hash(c, seg + 3) + time * speed * 0.5f / CL) % 1f + 1f) % 1f;
                    float along = Math.min(len, c * CL + f * CL);
                    for (int side = -1; side <= 1; side += 2) {
                        float bx = x0 + ux * along + nx * side * width * 0.47f, by = y0 + uy * along + ny * side * width * 0.47f;
                        batch.setColor(0.95f, 0.99f, 1f, 0.35f * MathUtils.sin(f * 3.1415927f));
                        batch.draw(pixel, Math.round(bx), Math.round(by), vertical ? 1 : 3, vertical ? 3 : 1);
                    }
                }
            }
        }
        batch.setColor(1f, 1f, 1f, 1f);
    }

    /* Stream tables in prop-image pixels (origin top-left): {x0, y0, x1, y1}. */
    private static final float[][] FOUNTAIN_BIG = {{93, 14, 92, 48}, {118, 10, 118, 44}, {142, 14, 143, 48},
            {77, 40, 73, 92}, {160, 40, 163, 92}, {180, 38, 185, 88}};
    private static final float[] FOUNTAIN_BIG_JET = {118, 10, 14}, FOUNTAIN_BIG_POOL = {122, 90, 58, 9};
    private static final float[][] FOUNTAIN_TIER = {{56, 14, 24, 50}, {64, 14, 96, 50}};
    private static final float[] FOUNTAIN_TIER_JET = {60, 12, 9};
    private static final float[][] WATERFALL = {{37, 18, 37, 92}, {40, 16, 40, 92}, {43, 18, 43, 92}};
    private static final float[] WATERFALL_POOL = {40, 101, 20, 6};

    /** True when a prop image has an animated water overlay. */
    public static boolean animatedWater(String image) {
        return image != null && (image.contains("fountain_fountain") || image.contains("fountain_tiered") || image.contains("waterfall"));
    }

    /**
     * v5.4 moving water on fountain and waterfall props: droplets fall along the painted
     * streams with gravity, a scrolling sheen runs down each stream, splashes hop at the
     * basin and ripples spread in the pool. left/top are the prop image's world corner (y-up).
     */
    public void drawPropWaterV54(SpriteBatch batch, Texture pixel, String image, float left, float top,
                                 float time, int quality) {
        if (image == null) return;
        boolean fall = image.contains("waterfall");
        float[][] streams = fall ? WATERFALL : image.contains("fountain_tiered") ? FOUNTAIN_TIER : FOUNTAIN_BIG;
        float[] jet = fall ? null : image.contains("fountain_tiered") ? FOUNTAIN_TIER_JET : FOUNTAIN_BIG_JET;
        float[] pool = fall ? WATERFALL_POOL : image.contains("fountain_tiered") ? null : FOUNTAIN_BIG_POOL;
        int drops = quality == 2 ? 6 : quality == 1 ? 4 : 2;
        float rate = fall ? 1.7f : 1.15f;
        for (int s = 0; s < streams.length; s++) {
            float[] st = streams[s];
            // Scrolling sheen: short bright dashes sliding down the stream.
            if (quality > 0) {
                for (float iy = st[1]; iy < st[3]; iy += 4f) {
                    float p = (iy - st[1]) / (st[3] - st[1]);
                    float ix = st[0] + (st[2] - st[0]) * p * p;
                    float al = 0.18f + 0.18f * MathUtils.sin((iy - time * (fall ? 120f : 70f)) * 0.42f + s);
                    batch.setColor(0.90f, 0.97f, 1f, Math.max(0f, al));
                    batch.draw(pixel, Math.round(left + ix), Math.round(top - iy), fall ? 2 : 1, 3);
                }
            }
            for (int k = 0; k < drops; k++) {
                float p = ((time * rate + k / (float) drops + s * 0.137f) % 1f);
                float ix = st[0] + (st[2] - st[0]) * p, iy = st[1] + (st[3] - st[1]) * p * p;
                batch.setColor(0.86f, 0.96f, 1f, 0.85f - p * 0.25f);
                batch.draw(pixel, Math.round(left + ix), Math.round(top - iy), 2, fall ? 4 : 2);
            }
            // Splash hop where the stream lands.
            float hop = Math.abs(MathUtils.sin(time * 7f + s * 1.9f)) * 3f;
            batch.setColor(0.92f, 0.98f, 1f, 0.55f);
            batch.draw(pixel, Math.round(left + st[2] - 2), Math.round(top - st[3] + hop), 1, 1);
            batch.draw(pixel, Math.round(left + st[2] + 2), Math.round(top - st[3] + hop * 0.6f), 1, 1);
        }
        if (jet != null) {
            float h = jet[2] * (0.85f + 0.15f * MathUtils.sin(time * 9f));
            for (float d = 0; d < h; d += 2f) {
                batch.setColor(0.90f, 0.97f, 1f, 0.65f - d / h * 0.4f);
                batch.draw(pixel, Math.round(left + jet[0] - 1), Math.round(top - jet[1] + d), 2, 2);
            }
        }
        if (pool != null && quality > 0) {
            int n = quality == 2 ? 4 : 2;
            for (int i = 0; i < n; i++) {
                float ph = ((time * 0.55f + i / (float) n) % 1f);
                float u = hash(i, 77) * 1.4f - 0.7f, v = hash(i, 91) * 1.2f - 0.6f;
                float sc = 0.35f + ph * 0.45f;
                batch.setColor(0.85f, 0.96f, 1f, (1f - ph) * 0.5f);
                batch.draw(ripple, left + pool[0] + u * pool[2] - 18f * sc, top - pool[1] - v * pool[3] - 6f * sc, 36f * sc, 12f * sc);
            }
        }
        if (fall && quality > 0) { // mist at the foot of the fall
            float al = 0.18f + 0.06f * MathUtils.sin(time * 2.1f);
            batch.setColor(0.92f, 0.97f, 1f, al);
            batch.draw(mist462, left + WATERFALL_POOL[0] - 34f, top - WATERFALL_POOL[1] - 4f, 68f, 18f);
        }
        batch.setColor(1f, 1f, 1f, 1f);
    }

    /**
     * v5.4 rain puddles: {x, yDown, sizeIndex}. Alpha follows ground wetness; while it
     * rains, small rings bloom inside each puddle. Cosmetic floor layer only.
     */
    public void drawPuddlesV54(SpriteBatch batch, java.util.List<float[]> puddles, float mapH, float wet,
                               boolean rain, float time, int quality, float flash,
                               float viewL, float viewB, float viewW, float viewH) {
        if (wet <= 0.01f || puddles == null) return;
        for (int i = 0; i < puddles.size(); i++) {
            float[] q = puddles.get(i);
            int sz = (int) q[2];
            Texture t = puddle54[sz];
            float w = t.getWidth(), h = t.getHeight();
            float x = Math.round(q[0] - w / 2f), y = Math.round(mapH - q[1] - h / 2f);
            if (x > viewL + viewW || x + w < viewL || y > viewB + viewH || y + h < viewB) continue;
            float al = Math.min(1f, wet * 1.15f);
            batch.setColor(1f, 1f, 1f, al);
            batch.draw(t, x, y, w, h);
            if (flash > 0f) { // the sky's flash mirrors in standing water
                batch.setColor(0.9f, 0.95f, 1f, Math.min(0.8f, flash * 2.4f) * al);
                batch.draw(t, x, y, w, h);
            }
            if (rain && quality > 0) {
                int n = quality == 2 ? 3 : 2;
                for (int k = 0; k < n; k++) {
                    float tt = time * 0.9f + k / (float) n + hash(i, k);
                    int cycle = (int) Math.floor(tt);
                    float ph = tt - cycle;
                    float u = hash(i * 3 + k, cycle) * 1.2f - 0.6f;
                    float v = hash(i * 5 + k, cycle + 9) * 0.8f - 0.4f;
                    float sc = (0.18f + ph * 0.22f) * (sz + 1);
                    batch.setColor(0.86f, 0.95f, 1f, (1f - ph) * 0.6f * al);
                    batch.draw(ripple, q[0] + u * w * 0.5f - 18f * sc, mapH - q[1] + v * h * 0.5f - 6f * sc, 36f * sc, 12f * sc);
                }
            }
        }
        batch.setColor(1f, 1f, 1f, 1f);
    }

    /** v5.4 lightning wash over the visible world; alpha already shaped by WeatherFxV54. */
    public void drawLightningV54(SpriteBatch batch, Texture pixel, float left, float bottom, float w, float h, float alpha) {
        if (alpha <= 0f) return;
        batch.setColor(0.86f, 0.91f, 1f, alpha);
        batch.draw(pixel, left - 10f, bottom - 10f, w + 20f, h + 20f);
        batch.setColor(1f, 1f, 1f, 1f);
    }

    public void drawVignette(SpriteBatch batch, float left, float bottom, float width, float height, int quality) {
        if (quality < 2) return;
        batch.setColor(1f, 1f, 1f, 0.68f);
        batch.draw(vignette, left, bottom, width, height);
        batch.setColor(1f, 1f, 1f, 1f);
    }
}
