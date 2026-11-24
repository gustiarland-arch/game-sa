package com.arlandsofia.olu;

import com.arlandsofia.olu.logic.Settings;
import com.arlandsofia.olu.logic.SoundscapePlan;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.audio.Music;
import com.badlogic.gdx.audio.Sound;

/**
 * Dua stream OGG terpisah (BGM + ambience), crossfade, ducking dialog dan efek suara WAV.
 * Semua file offline; hanya membuka stream yang sedang aktif untuk menjaga memori Android.
 */
public final class AudioManager {
    private final Assets assets;
    private final Settings settings;
    private final Bus bgm = new Bus(false), ambience = new Bus(true);
    private float duckLevel = 1f;
    private boolean ducking;
    private boolean paused;

    private static final class Bus {
        Music active, outgoing;
        String id;
        float in = 1f, out;
        final boolean environmental;
        Bus(boolean environment) { environmental = environment; }
    }

    public AudioManager(Assets assets, Settings settings) { this.assets = assets; this.settings = settings; }

    /** Optional observer for automated capture/QA (null in the shipped game). */
    public interface Tap { void heard(String bus, String id, float volume); }
    public static volatile Tap tap;

    public void music(String id) { if (tap != null) tap.heard("music", id, settings.music); change(bgm, id, SoundscapePlan.musicPath(id)); }
    public void ambience(String id) { if (tap != null) tap.heard("ambience", id, settings.ambience * 0.55f); change(ambience, id, SoundscapePlan.ambientPath(id)); }

    private void change(Bus bus, String id, String path) {
        if (id == null || path == null) {
            if (bus.id == null && bus.active == null) return;
            discard(bus.outgoing); bus.outgoing = bus.active; bus.out = 1f;
            bus.active = null; bus.id = null; bus.in = 0f;
            return;
        }
        if (id.equals(bus.id)) return;
        Music next;
        try {
            next = Gdx.audio.newMusic(Gdx.files.internal(path));
            next.setLooping(true);
            next.setVolume(0f);
            if (!paused) next.play();
        } catch (Exception e) {
            if (Gdx.app != null) Gdx.app.error("OLU-AUDIO", "Gagal memuat " + path, e);
            return; // pertahankan stream lama jika aset baru gagal
        }
        discard(bus.outgoing);
        bus.outgoing = bus.active; bus.out = bus.in;
        bus.active = next; bus.id = id; bus.in = 0f;
    }

    private static void discard(Music m) {
        if (m == null) return;
        try { m.stop(); } finally { m.dispose(); }
    }

    /** Gerakan slider volume langsung memengaruhi audio, tanpa restart lagu. */
    public void update(float dt) {
        duckLevel += ((ducking ? .62f : 1f) - duckLevel) * Math.min(1f, Math.max(0f, dt) * 3.0f);
        advance(bgm, dt, settings.music * duckLevel);
        advance(ambience, dt, settings.ambience * 0.55f * (0.8f + 0.2f * duckLevel));
    }

    private void advance(Bus bus, float dt, float level) {
        float rate = bus.environmental ? 0.45f : 0.75f;
        if (bus.active != null) {
            bus.in = Math.min(1f, bus.in + Math.max(0, dt) * rate);
            bus.active.setVolume(paused ? 0f : Math.min(1f, level * bus.in));
        }
        if (bus.outgoing != null) {
            bus.out -= Math.max(0, dt) * rate;
            if (bus.out <= 0f) { discard(bus.outgoing); bus.outgoing = null; bus.out = 0; }
            else bus.outgoing.setVolume(paused ? 0f : Math.min(1f, level * bus.out));
        }
    }
    public void duck(boolean speech) { ducking = speech; }

    public void sfx(String id) { sfx(id, 1f); }
    public void sfx(String id, float multiplier) {
        if (!SoundscapePlan.contains(SoundscapePlan.SFX, id) || multiplier <= 0f || settings.sfx <= 0.005f) return;
        Sound s = assets.sfxSound(id);
        if (tap != null) tap.heard("sfx", id, Math.min(1f, settings.sfx * multiplier));
        if (s != null) s.play(Math.min(1f, settings.sfx * multiplier));
    }

    /** Jangan biarkan soundscape terus berjalan saat aplikasi berada di background. */
    public void pauseAll() {
        paused = true;
        for (Bus b : new Bus[]{bgm, ambience}) {
            if (b.active != null) b.active.pause();
            if (b.outgoing != null) b.outgoing.pause();
        }
    }
    public void resumeAll() {
        paused = false;
        for (Bus b : new Bus[]{bgm, ambience}) {
            if (b.active != null) b.active.play();
            if (b.outgoing != null) b.outgoing.play();
        }
    }
    public void stopAll() { close(bgm); close(ambience); ducking = false; }
    private void close(Bus b) {
        discard(b.active); discard(b.outgoing);
        b.active = null; b.outgoing = null; b.id = null; b.in = 0f; b.out = 0f;
    }
    public void dispose() { stopAll(); }
}
