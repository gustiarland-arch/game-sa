package com.arlandsofia.olu.screens;

import com.arlandsofia.olu.OluGame;
import com.arlandsofia.olu.ui.SettingsPanel;

/** Pengaturan dari layar judul. */
public final class SettingsScreen extends BaseScreen {
    private final SettingsPanel panel;

    public SettingsScreen(final OluGame game) {
        super(game);
        panel = new SettingsPanel(game, new Runnable() { public void run() { game.switchScreen(new TitleScreen(game)); } });
        buttons.addAll(panel.buttons);
    }

    @Override protected void layout() { panel.safeInsets(insetL(),insetR(),insetT(),insetB()); panel.layout(uiW(), uiH()); }
    @Override protected void drawUi() { panel.draw(ui, uiW(), uiH()); }
    @Override protected void onBack() { game.saveSettings(); game.switchScreen(new TitleScreen(game)); }
}
