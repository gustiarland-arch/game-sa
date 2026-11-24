package com.arlandsofia.olu;
import com.arlandsofia.olu.logic.Settings;
/** Test-only controller, not Android launcher. */
public final class OluGame {
    public final Settings settings=new Settings();
    public final AudioManager audio=new AudioManager();
    public int saves;
    public void saveSettings(){saves++;}
}
