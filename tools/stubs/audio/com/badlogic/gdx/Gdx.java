package com.badlogic.gdx;
import com.badlogic.gdx.audio.Music;
import com.badlogic.gdx.files.FileHandle;
public final class Gdx {
    public static Audio audio;
    public static final Files files = new Files();
    public static App app;
    public interface Audio { Music newMusic(FileHandle f); }
    public interface App { void error(String tag, String text, Throwable ex); void error(String tag, String text); }
    public static final class Files { public FileHandle internal(String s) { return new FileHandle(s); } }
}
