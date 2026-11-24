package com.arlandsofia.olu.screens;

import com.arlandsofia.olu.OluGame;
import com.arlandsofia.olu.logic.AdaptiveLayoutV43;
import com.arlandsofia.olu.logic.Routes;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.math.MathUtils;
import com.badlogic.gdx.utils.Align;

/** Pilih ARLAND ROUTE atau SOFIA ROUTE. */
public final class RouteSelectScreen extends BaseScreen {
    private final Texture cardA, cardS, glow, skyline, foreground;
    private final UiButton pickA, pickS, back;
    private float cardW, cardH, ax, sx, cy;
    private final com.badlogic.gdx.graphics.Color sky = new com.badlogic.gdx.graphics.Color();

    public RouteSelectScreen(final OluGame game) {
        super(game);
        cardA = game.assets.uiTex("ui/card_arland.png");
        cardS = game.assets.uiTex("ui/card_sofia.png");
        glow = game.assets.uiTex("ui/soft_glow.png");
        skyline = game.assets.tex("ui/v32_menu_far.png");
        foreground = game.assets.tex("ui/v32_menu_near.png");
        pickA = new UiButton("Main sebagai Arland", new Runnable() { public void run() { pick(Routes.ARLAND); } });
        pickS = new UiButton("Main sebagai Sofia", new Runnable() { public void run() { pick(Routes.SOFIA); } });
        pickA.accent = true; pickS.accent = true;
        back = new UiButton("Kembali", new Runnable() { public void run() { onBack(); } });
        buttons.add(pickA); buttons.add(pickS); buttons.add(back);
    }

    private void pick(String route) { game.switchScreen(new SlotScreen(game, route, true)); }

    @Override
    protected void layout() {
        cardW = Math.min(560, (uiW() - 140 - insetL() - insetR()) / 2); cardH = 470;
        ax = uiW() / 2 - cardW - 20; sx = uiW() / 2 + 20;
        cy = AdaptiveLayoutV43.cardBottom(screenLayout(), cardH);
        pickA.set(ax + 30, cy + 22, cardW - 60, 70);
        pickS.set(sx + 30, cy + 22, cardW - 60, 70);
        back.set(30 + insetL(), 26, 220, 64);
    }

    @Override
    protected void drawUi() {
        ui.imageCover(skyline, 0, 0, uiW(), uiH(), 1f);
        float drift = game.settings.visualQuality == 0 ? 0f : MathUtils.sin(time * 0.16f) * 9f;
        ui.imageCover(foreground, drift - 12, -4, uiW() + 24, uiH() + 8, 0.75f);
        ui.rect(0, 0, uiW(), uiH(), sky.set(0.08f, 0.05f, 0.16f, 1f), 0.26f);
        if (game.settings.visualQuality > 0) {
            ui.image(glow, ax - 30, cy + 160, 220, 220, 0.22f);
            ui.image(glow, sx + cardW - 160, cy + 160, 220, 220, 0.22f);
        }
        ui.textCenter(game.assets.title, "Pilih Route", uiW() / 2, uiH() - 36, Ui.CREAM, 0.72f);
        ui.textCenter(game.assets.body, "Dua sudut pandang, dua nuansa visual, satu canon ending yang sama.", uiW() / 2, uiH() - 84, Ui.LAVENDER, 0.8f);
        card(ax, cardA, "ARLAND ROUTE", "Tenang, perhatian, rasional, tapi romantis.",
                "Pagi biasa, sebuah pesan, dan bunga kertas buatan sendiri.", Ui.LAVENDER);
        card(sx, cardS, "SOFIA ROUTE", "Lembut, ceria, hangat, peka, dan penyayang.",
                "Mimpi tentang buku bercahaya, lalu kartu pos kecil untuk Arland.", Ui.PINK);
        drawButtons();
        ui.textCenter(game.assets.body, "Dua sudut pandang, satu kisah. Progress tiap route disimpan terpisah.", uiW() / 2, 60, Ui.CREAM, 0.8f);
    }

    private void card(float x, Texture img, String title, String trait, String hook, com.badlogic.gdx.graphics.Color tag) {
        ui.panel(game.assets.panel, x, cy, cardW, cardH, 1f);
        float iw = 189, ih = 300;
        ui.image(img, x + 26, cy + cardH - ih - 26, iw, ih, 1f);
        float tx = x + 26 + iw + 20, tw = cardW - (tx - x) - 24;
        // Hierarchy and edge accents use the existing editable nine-patch cards.
        ui.rect(x+16,cy+cardH-8,cardW-32,3,tag,.65f);
        ui.rect(tx, cy + cardH - 66, Math.min(tw, 230), 40, tag, 1f);
        ui.text(game.assets.body, title, tx + 12, cy + cardH - 36, Ui.WHITE, 0.95f, Align.left, 0);
        float h = ui.wrap(game.assets.body, trait, tx, cy + cardH - 90, tw, Ui.INK, 0.85f, Align.left);
        ui.wrap(game.assets.body, hook, tx, cy + cardH - 110 - h, tw, Ui.INK_SOFT, 0.8f, Align.left);
        ui.rect(x+22,cy+108,cardW-44,2,tag,.20f);
    }

    @Override protected void onBack() { game.switchScreen(new TitleScreen(game)); }
}
