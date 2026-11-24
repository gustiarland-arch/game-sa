package com.arlandsofia.olu.logic.romance;

import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Preferences;
import com.badlogic.gdx.utils.Json;

/** Isolated saved relationship state: does not edit the original JSON / CRC save slots. */
public final class RomanceSaveV45 {
    private RomanceSaveV45() {}

    public static RomanceEngineV45 load(String route,int slot,int worldDay) {
        Preferences pref=Gdx.app.getPreferences(RomanceSlotKeysV45.namespace(route,slot));
        String raw=pref.getString("snapshot","");
        RomanceEngineV45 engine=new RomanceEngineV45(route);
        if(!raw.isEmpty()) {
            try {
                Json json=new Json();json.setIgnoreUnknownFields(true);
                RomanceEngineV45.Snapshot saved=json.fromJson(RomanceEngineV45.Snapshot.class,raw);
                if(RomanceSavePolicyV45.acceptsExisting(route,saved))engine=new RomanceEngineV45(route,saved);
                else Gdx.app.error("RomanceV45","Unsupported romance save kept intact");
            } catch(Exception e) {
                Gdx.app.error("RomanceV45","Corrupt romance save kept intact",e);
            }
        }
        engine.syncWorldDay(worldDay);
        return engine;
    }
    public static boolean save(RomanceEngineV45 engine,int slot) {
        if(engine==null)throw new IllegalArgumentException("Engine null");
        Preferences pref=Gdx.app.getPreferences(RomanceSlotKeysV45.namespace(engine.route(),slot));
        Json json=new Json();json.setIgnoreUnknownFields(true);
        String old=pref.getString("snapshot","");
        if(!old.isEmpty()) {
            try {
                RomanceEngineV45.Snapshot previous=json.fromJson(RomanceEngineV45.Snapshot.class,old);
                if(!RomanceSavePolicyV45.acceptsExisting(engine.route(),previous))return false;
            } catch(Exception e) {Gdx.app.error("RomanceV45","Refuse to overwrite unreadable save",e);return false;}
        }
        pref.putString("snapshot",json.toJson(engine.snapshot()));
        try{pref.flush();return true;}
        catch(Exception e){Gdx.app.error("RomanceV45","Romance save write failed",e);return false;}
    }
    /** Called ONLY after main SaveStore successfully creates a new slot or deletes it. */
    public static boolean resetSlot(String route,int slot){
        try {
            Preferences pref=Gdx.app.getPreferences(RomanceSlotKeysV45.namespace(route,slot));
            pref.clear();pref.flush();
            return true;
        } catch (Exception e) {
            Gdx.app.error("RomanceV45","Romance slot reset failed",e);
            return false;
        }
    }
}
