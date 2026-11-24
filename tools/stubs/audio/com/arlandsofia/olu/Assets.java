package com.arlandsofia.olu;
import com.badlogic.gdx.audio.Sound;
public final class Assets {
    public final Sound sound=new Sound() { public long play(float volume) { return 1; } };
    public Sound sfxSound(String id) { return sound; }
}
