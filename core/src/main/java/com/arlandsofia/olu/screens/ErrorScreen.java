package com.arlandsofia.olu.screens;

import com.arlandsofia.olu.OluGame;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.utils.Align;

/** Ditampilkan bila data inti gagal dimuat — mencegah layar hitam tanpa penjelasan. */
public final class ErrorScreen extends BaseScreen {
    private final String message;

    public ErrorScreen(OluGame game, String message) {
        super(game);
        this.message = message;
        buttons.add(new UiButton("Tutup game", new Runnable() { public void run() { Gdx.app.exit(); } }));
    }

    @Override protected void layout() { buttons.get(0).set(uiW() / 2 - 150, 80, 300, 76); }

    @Override
    protected void drawUi() {
        ui.panel(game.assets.panel, 120, 190, uiW() - 240, uiH() - 300, 1f);
        ui.text(game.assets.title, "Ups, ada masalah", 160, uiH() - 150, Ui.INK, 0.8f, Align.left, 0);
        ui.wrap(game.assets.body, message + "\n\nTutup dan buka kembali aplikasi. Jangan hapus data atau uninstall: save lokal dapat hilang. Laporkan pesan ini bila tetap terjadi.", 160, uiH() - 230, uiW() - 320, Ui.INK, 1f, Align.left);
        drawButtons();
    }

    @Override protected void onBack() { Gdx.app.exit(); }
}
