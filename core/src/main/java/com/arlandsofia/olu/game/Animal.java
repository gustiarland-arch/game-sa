package com.arlandsofia.olu.game;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.logic.MapDb;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.graphics.g2d.TextureRegion;
import com.badlogic.gdx.math.MathUtils;

/**
 * Hewan ambient dengan AI sederhana. Lembar sprite: animals/&lt;type&gt;.png, 4 frame menyamping (jalan kanan x2, diam, istirahat).
 * Perilaku: walk (kucing/anjing/ayam), swim (bebek, di dalam region air), flee (burung terbang menjauh, kelinci/tupai berlari).
 */
public final class Animal {
    public final String type, behavior; public final boolean pettable;
    public float x, y; private float tx, ty, timer, anim, lift, alpha = 1f; private boolean moving, faceLeft, flying, resting;
    private final float[] region; public float hearts;
    private final int fw, fh;

    public Animal(String type, float x, float y, float[] region) {
        this.type = type; this.x = x; this.y = y; this.region = region; tx = x; ty = y;
        behavior = type.equals("duck") ? "swim" : (type.equals("bird") || type.equals("rabbit") || type.equals("squirrel")) ? "flee" : "walk";
        pettable = type.startsWith("cat") || type.equals("dog") || type.equals("duck") || type.equals("chicken") || type.equals("rabbit");
        fw = type.equals("dog") ? 30 : type.equals("bird") ? 16 : type.equals("squirrel") ? 18 : 24; fh = type.equals("bird") ? 14 : 22;
        timer = MathUtils.random(0.5f, 3f);
    }

    public boolean gone() { return flying && alpha <= 0f; }

    public void update(float dt, MapDb.Area area, float px, float py) {
        anim += dt; if (hearts > 0) hearts -= dt;
        float dpx = px - x, dpy = py - y, dp = (float) Math.sqrt(dpx * dpx + dpy * dpy);
        if (flying) { // burung terbang menjauh lalu menghilang
            x += (faceLeft ? -1 : 1) * 70 * dt; lift += 55 * dt; alpha -= dt * 0.5f; return;
        }
        if (behavior.equals("flee") && dp < (type.equals("bird") ? 70 : 90)) {
            if (type.equals("bird")) { flying = true; faceLeft = dpx > 0; return; }
            float nx = x - dpx / dp * 40, ny = y - dpy / dp * 40;
            if (!area.blocked(nx, ny) && inRegion(nx, ny)) { tx = nx; ty = ny; moving = true; resting = false; }
        }
        if (moving) {
            float dx = tx - x, dy = ty - y, d = (float) Math.sqrt(dx * dx + dy * dy);
            float sp = behavior.equals("flee") ? 110 : type.equals("dog") ? 55 : behavior.equals("swim") ? 18 : 26;
            if (d < 2) { moving = false; timer = MathUtils.random(1.5f, 5f); resting = MathUtils.random() < 0.25f; }
            else {
                float nx = x + dx / d * sp * dt, ny = y + dy / d * sp * dt;
                if (behavior.equals("swim") || !area.blocked(nx, ny)) { x = nx; y = ny; faceLeft = dx < 0; }
                else { moving = false; timer = 0.5f; }
            }
        } else {
            timer -= dt;
            if (timer <= 0) {
                for (int k = 0; k < 6; k++) {
                    float nx = x + MathUtils.random(-80f, 80f), ny = y + MathUtils.random(-50f, 50f);
                    if (!inRegion(nx, ny)) continue;
                    if (!behavior.equals("swim") && area.blocked(nx, ny)) continue;
                    tx = nx; ty = ny; moving = true; resting = false; break;
                }
                if (!moving) timer = 1f;
            }
        }
    }

    private boolean inRegion(float nx, float ny) {
        if (region == null || region.length < 4) return true;
        if (behavior.equals("swim")) { // elips air
            float ex = (nx - region[0]) / region[2], ey = (ny - region[1]) / region[3];
            return ex * ex + ey * ey < 0.8f;
        }
        return nx > region[0] && nx < region[0] + region[2] && ny > region[1] && ny < region[1] + region[3];
    }

    public void pet() { hearts = 1.6f; moving = false; timer = 2.5f; resting = false; }

    public void draw(SpriteBatch b, Assets a, float mapH, Texture shadow) {
        if (alpha <= 0) return;
        Texture t = a.tex("animals/" + type + ".png");
        int frame = flying ? (((int) (anim * 10)) & 1) : moving ? (((int) (anim * 8)) & 1) : resting ? 3 : 2;
        if (behavior.equals("swim")) frame = ((int) (anim * 2)) & 1;
        TextureRegion r = new TextureRegion(t, frame * fw, 0, fw, fh);
        float gy = mapH - y;
        b.setColor(1, 1, 1, 0.6f * alpha);
        if (!behavior.equals("swim")) b.draw(shadow, x - fw * 0.35f, gy - 3, fw * 0.7f, 6);
        b.setColor(1, 1, 1, alpha);
        float bob = behavior.equals("swim") ? MathUtils.sin(anim * 2f) * 0.8f : 0f;
        // Reaksi elusan: loncat kecil dan menatap pemain, lalu kembali berjalan normal.
        if (hearts > 0) bob += Math.max(0f, MathUtils.sin((1.6f - hearts) * 7f)) * 3.8f;
        if (faceLeft) b.draw(r, Math.round(x + fw / 2f), Math.round(gy - 1 + lift + bob), -fw, fh);
        else b.draw(r, Math.round(x - fw / 2f), Math.round(gy - 1 + lift + bob), fw, fh);
        if (hearts > 0) {
            Texture h = a.tex("ui/emote_heart.png");
            b.draw(h, x - 6, gy + fh + 2 + (1.6f - hearts) * 10, 12, 12);
        }
        b.setColor(1, 1, 1, 1);
    }

    public float y() { return y; }
}
