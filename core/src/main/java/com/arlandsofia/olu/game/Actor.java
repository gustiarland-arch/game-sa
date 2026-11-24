package com.arlandsofia.olu.game;

import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.logic.AnimationMathV462;
import com.arlandsofia.olu.logic.MotionPersonalityV53;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.graphics.g2d.TextureRegion;
import com.badlogic.gdx.math.MathUtils;

/** Karakter di dunia (pemain / companion / NPC). Posisi = titik kaki dalam koordinat peta (y ke bawah).
 *  Mendukung pose dari lembar pose (duduk, melambai, memberi, gandengan, ...) dan gestur prosedural (tertawa, kaget, mengangguk, napas idle). */
public final class Actor {
    public static final float SCALE = 0.85f;

    public final String character;
    public final MotionPersonalityV53.Style motion;
    public float x, y;
    /** Temporary visual elevation from terrace ramp; never serialized. */
    public float terrainLift;
    public int dir = Assets.DIR_DOWN;
    public boolean walking, sprinting;
    public float anim;
    /** Eight-way facing is visual-only, old four-way dir remains compatible with save and poses. */
    public int facing8=AnimationMathV462.DOWN;
    private float motionBlend;
    private float turnImpulse;
    public String emote;
    public float emoteTime;
    public boolean visible = true;
    /** Pose atlas plus gestures: laugh/surprised/nod/shake/jump/shy/excited/ponder. */
    public String pose;
    public float poseTime, poseDur; // poseDur <= 0: tahan sampai dihapus
    public float alpha = 1f;
    private float life = MathUtils.random(0f, 10f);

    public Actor(String character) {
        this.character = character;
        this.motion = MotionPersonalityV53.forCharacter(character);
    }

    public void face(float dx, float dy) {
        int nextFacing=AnimationMathV462.facing(dx,dy,facing8);
        if (nextFacing != facing8) turnImpulse = Math.min(.9f,turnImpulse + .35f);
        facing8=nextFacing;
        if (Math.abs(dx) > Math.abs(dy)) dir = dx < 0 ? Assets.DIR_LEFT : Assets.DIR_RIGHT;
        else if (dy != 0) dir = dy < 0 ? Assets.DIR_UP : Assets.DIR_DOWN;
    }

    public void faceTo(Actor o) { if (o != null) face(o.x - x, o.y - y); }

    public void update(float dt) {
        float safeDt=Math.max(0f,Math.min(dt,.08f));
        life += safeDt;
        // v5.3: 24 real movement frames and individualized cadence. Foot hitbox
        // and physical coordinates remain independent from animation.
        motionBlend=AnimationMathV462.blend(motionBlend,walking?1f:0f,safeDt,
                walking?12f:9.5f);
        turnImpulse=Math.max(0f,turnImpulse-safeDt*3.8f);
        if (walking) {
            anim=(anim+safeDt*(sprinting?32f:24f)*motion.cadence)%24f;
        }
        if (emoteTime > 0) { emoteTime -= dt; if (emoteTime <= 0) emote = null; }
        if (pose != null) {
            poseTime += dt;
            if (walking && !"hold_l".equals(pose) && !"hold_r".equals(pose)) clearPose();
            else if (poseDur > 0 && poseTime >= poseDur) clearPose();
        }
    }

    public void setPose(String p, float seconds) { pose = p; poseTime = 0; poseDur = seconds; }
    public void clearPose() { pose = null; poseTime = 0; poseDur = 0; }

    public void showEmote(String e, float seconds) { emote = e; emoteTime = seconds; }

    public static int dirOf(String s) {
        if ("left".equals(s)) return Assets.DIR_LEFT;
        if ("right".equals(s)) return Assets.DIR_RIGHT;
        if ("up".equals(s)) return Assets.DIR_UP;
        return Assets.DIR_DOWN;
    }

    public static String dirName(int d) {
        switch (d) { case Assets.DIR_LEFT: return "left"; case Assets.DIR_RIGHT: return "right"; case Assets.DIR_UP: return "up"; default: return "down"; }
    }

    public float drawHeight() { return Assets.FRAME_H * SCALE * motion.visualScale; }

    /** mapH = tinggi peta untuk konversi y ke koordinat LibGDX (y ke atas). */
    public void draw(SpriteBatch batch, Assets a, float mapH, Texture shadow) {
        if (!visible || alpha <= 0f) return;
        float gy = mapH - y + terrainLift;
        float w = Assets.FRAME_W * SCALE * motion.visualScale;
        float h = Assets.FRAME_H * SCALE * motion.visualScale;
        float lift = 0f, dx = 0f, extraW = 0f, extraH = 0f;
        TextureRegion r = null;
        int pi = pose == null ? -1 : Assets.poseIndex(pose);
        if (pi >= 0) {
            int f = ("wave".equals(pose) || "cheer".equals(pose) || "hug".equals(pose) || "lean".equals(pose)
                    || "photo".equals(pose) || "highfive".equals(pose) || "dance".equals(pose)
                    || "read".equals(pose) || "water".equals(pose) || "sweep".equals(pose)
                    || (("hold_l".equals(pose) || "hold_r".equals(pose)) && walking)) ? ((int) ((walking ? anim : poseTime) * 4f)) & 1 : 0;
            r = a.poseFrame(character, pi, dir, f);
        } else if (pose != null) {
            float t = poseTime;
            if ("laugh".equals(pose)) lift = Math.abs(MathUtils.sin(t * 12f)) * 2.5f;
            else if ("surprised".equals(pose)) lift = t < 0.35f ? MathUtils.sin(t / 0.35f * MathUtils.PI) * 7f : 0f;
            else if ("jump".equals(pose)) lift = Math.abs(MathUtils.sin(t * 6f)) * 8f;
            else if ("nod".equals(pose)) lift = -Math.abs(MathUtils.sin(t * 9f)) * 1.5f;
            else if ("shake".equals(pose)) dx = MathUtils.sin(t * 30f) * 1.5f * Math.max(0f, 1f - t);
            else if ("shy".equals(pose)) { dx = MathUtils.sin(t*3.5f)*0.85f; lift = -1.0f; }
            else if ("excited".equals(pose)) lift = Math.abs(MathUtils.sin(t*11f))*4.8f;
            else if ("ponder".equals(pose)) { dx = MathUtils.sin(t*1.9f)*0.7f; lift = MathUtils.sin(t*2.2f)*0.45f; }
        }
        if (("hold_l".equals(pose) || "hold_r".equals(pose)) && walking) {
            lift += Math.abs(MathUtils.sin(anim * 1.65f)) * 1.6f;
        }
        // bayangan mengecil saat melompat
        float sk = 1f - Math.min(0.4f, lift / 20f);
        batch.setColor(1, 1, 1, alpha);
        batch.draw(shadow, x - 13 * sk, gy - 5, 26 * sk, 10);
        if (r == null) {
            // Dedicated eight-facing atlas keeps original four-facing pose sheets untouched.
            boolean eightWay = "arland".equals(character) || "sofia".equals(character);
            // Direct cardinal assignments from cutscenes/area entry take precedence
            // unless the actor currently faces a genuine diagonal.
            int visualDir8 = (facing8 & 1) == 0
                    ? (dir == Assets.DIR_LEFT ? 2 : dir == Assets.DIR_RIGHT ? 6
                    : dir == Assets.DIR_UP ? 4 : 0) : facing8;
            r = walking ? (eightWay ? a.walkFrame8(character,visualDir8,(int)anim)
                    : a.walkFrame(character,dir,(int)anim))
                    : (eightWay ? a.idleFrame8(character,visualDir8,(int)((life+motion.phase)*3.0f))
                    : a.idleFrame(character,dir,(int)((life+motion.phase)*3.0f)));
            // Dua langkah per siklus 16 fase. Hindari getaran terlalu cepat.
            float gait = MathUtils.sin(anim * MathUtils.PI / 6f);
            if (walking) {
                lift += Math.abs(gait) * (sprinting ? 2.2f : 1.4f) * motionBlend * motion.bounce;
                dx += gait * (dir == Assets.DIR_LEFT ? -0.8f : dir == Assets.DIR_RIGHT ? 0.8f : 0f)
                        * motionBlend * motion.sway;
                dx += AnimationMathV462.diagonalLean(facing8)*motionBlend;
                extraW = -Math.abs(gait) * .8f * motion.sway;
                extraH = Math.abs(gait) * 1.2f;
            }
            if (walking && ((int) anim % 12 == 3 || (int) anim % 12 == 9)) lift += .5f;
            if (walking && sprinting) dx += dir == Assets.DIR_LEFT ? -1f : dir == Assets.DIR_RIGHT ? 1f : 0f;
        }
        float breathe = (!walking && pose == null)
                ? Math.max(0f, MathUtils.sin((life+motion.phase)*2.12f*motion.breathing)) : 0f;
        lift += breathe * .65f * motion.bounce;
        if (pose==null) dx += MathUtils.sin(life*5f+motion.phase)*turnImpulse*1.5f;
        // Subtle idle listening/head reaction, no extra overdraw or sprite duplication.
        if (!walking && pose==null && emoteTime>0f) lift += MathUtils.sin(life*4f)*0.45f;
        float dw = w + extraW, dh = h + extraH;
        float px = Math.round(x - dw / 2 + dx), py = Math.round(gy - 1 + lift);
        // v3.7: gambar sprite tepat satu kali. Versi lama menggambar kepala dua kali
        // pada idle dan menghasilkan ghosting semi-transparan di tepi rambut/wajah.
        // Gerakan napas sekarang sudah ada pada 8 fase atlas idle; hitbox kaki tetap.
        batch.draw(r, px, py, dw, dh);
        batch.setColor(1, 1, 1, 1);
    }
}
