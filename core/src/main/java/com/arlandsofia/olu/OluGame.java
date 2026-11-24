package com.arlandsofia.olu;

import com.arlandsofia.olu.logic.GlobalProgress;
import com.arlandsofia.olu.logic.MapDb;
import com.arlandsofia.olu.logic.MemoryBookDb;
import com.arlandsofia.olu.logic.QuestDb;
import com.arlandsofia.olu.logic.SaveStore;
import com.arlandsofia.olu.logic.Settings;
import com.arlandsofia.olu.logic.StoryDb;
import com.arlandsofia.olu.screens.ErrorScreen;
import com.arlandsofia.olu.screens.TitleScreen;
import com.arlandsofia.olu.screens.RomanceV45Screen;
import com.badlogic.gdx.Game;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Input;
import com.badlogic.gdx.Screen;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;

/**
 * Arland & Sofia: Our Little Universe — entry point LibGDX (dipakai launcher Android).
 * 100% offline: semua data dibaca dari assets lokal, save di penyimpanan privat aplikasi.
 */
public class OluGame extends Game {
    public static final String VERSION = "5.4.0";

    public Assets assets;
    public AudioManager audio;
    public SaveStore store;
    public Settings settings;
    public GlobalProgress global;
    public StoryDb story;
    public QuestDb quests;
    public MapDb maps;
    public MemoryBookDb book;
    public SpriteBatch batch;

    @Override
    public void create() {
        Gdx.input.setCatchKey(Input.Keys.BACK, true);
        batch = new SpriteBatch();
        assets = new Assets();
        store = new SaveStore(new GdxFileIO());
        settings = store.loadSettings();
        global = store.loadGlobal();
        audio = new AudioManager(assets, settings);
        try {
            assets.loadCore();
            story = new StoryDb(read("data/story.json"));
            quests = new QuestDb(read("data/quests.json"));
            maps = new MapDb(read("data/maps.json"), read("data/props.json"));
            book = new MemoryBookDb(read("data/memory_book.json"));
            assets.preload(maps, quests, book);
        } catch (Exception e) {
            Gdx.app.error("OLU", "Data game gagal dimuat", e);
            setScreen(new ErrorScreen(this, "Data game gagal dimuat:\n" + e.getMessage()));
            return;
        }
        if (!assets.missing.isEmpty()) Gdx.app.error("OLU", "Aset hilang: " + assets.missing);
        setScreen(new TitleScreen(this));
    }

    private static String read(String path) { return Gdx.files.internal(path).readString("UTF-8"); }

    /** Ganti layar dan buang layar lama. */
    public void switchScreen(Screen next) {
        Screen old = getScreen();
        setScreen(next);
        if (old != null) old.dispose();
    }

    /** Open romance in the currently selected route/slot; keep the original screen alive. */
    public void openRomanceSimulationV45(String route,int slot,int worldDay) {
        if (getScreen() instanceof RomanceV45Screen) return;
        Screen previous = getScreen();
        setScreen(new RomanceV45Screen(this,route,slot,worldDay,previous));
    }

    public void saveSettings() { store.saveSettings(settings); }

    @Override
    public void dispose() {
        Screen s = getScreen();
        if (s != null) s.dispose();
        if (audio != null) audio.dispose();
        if (assets != null) assets.dispose();
        if (batch != null) batch.dispose();
    }
}
