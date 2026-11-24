package com.arlandsofia.olu.screens;

import com.arlandsofia.olu.OluGame;
import com.arlandsofia.olu.logic.AdaptiveLayoutV43;
import com.arlandsofia.olu.ui.ConfirmBox;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Input;
import com.badlogic.gdx.InputAdapter;
import com.badlogic.gdx.Screen;
import com.badlogic.gdx.graphics.GL20;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.math.Vector2;
import com.badlogic.gdx.utils.viewport.ExtendViewport;

import java.util.ArrayList;
import java.util.List;

/**
 * Dasar layar menu: viewport UI 1280x720 (melebar mengikuti rasio layar, tanpa black bar),
 * daftar tombol dengan dukungan sentuh multi-pointer + navigasi keyboard/gamepad-keyboard.
 */
public abstract class BaseScreen extends InputAdapter implements Screen {
    protected final OluGame game;
    protected final Ui ui;
    protected final OrthographicCamera uiCam = new OrthographicCamera();
    protected final ExtendViewport uiView = new ExtendViewport(1280, 720, uiCam);
    protected final List<UiButton> buttons = new ArrayList<>();
    protected int focus = -1;
    private final Vector2 tmp = new Vector2();
    protected float time;
    /** Modal konfirmasi aktif (null bila tidak ada). */
    protected ConfirmBox confirm;

    protected BaseScreen(OluGame game) {
        this.game = game;
        this.ui = new Ui(game.assets, game.batch);
    }

    protected float uiW() { return uiView.getWorldWidth(); }
    protected float uiH() { return uiView.getWorldHeight(); }

    /** Inset aman (notch/cutout) dalam satuan UI. */
    protected float insetL() { return Gdx.graphics.getSafeInsetLeft() * uiW() / Math.max(1, Gdx.graphics.getWidth()); }
    protected float insetR() { return Gdx.graphics.getSafeInsetRight() * uiW() / Math.max(1, Gdx.graphics.getWidth()); }
    protected float insetT() { return Gdx.graphics.getSafeInsetTop() * uiH() / Math.max(1, Gdx.graphics.getHeight()); }
    protected float insetB() { return Gdx.graphics.getSafeInsetBottom() * uiH() / Math.max(1, Gdx.graphics.getHeight()); }

    protected AdaptiveLayoutV43.Metrics screenLayout() {
        return AdaptiveLayoutV43.of(uiW(), uiH(), insetL(), insetR(), insetT(), insetB());
    }

    protected Vector2 toUi(int sx, int sy) { return uiView.unproject(tmp.set(sx, sy)); }

    @Override public void show() { Gdx.input.setInputProcessor(this); }

    @Override
    public void render(float delta) {
        float dt = Math.min(delta, 1f / 20f);
        time += dt;
        game.audio.update(dt);
        update(dt);
        Gdx.gl.glClearColor(Ui.BG.r, Ui.BG.g, Ui.BG.b, 1f);
        Gdx.gl.glClear(GL20.GL_COLOR_BUFFER_BIT);
        drawWorld();
        uiView.apply();
        game.batch.setProjectionMatrix(uiCam.combined);
        game.batch.begin();
        drawUi();
        if (confirm != null) confirm.draw(ui, uiW(), uiH());
        // v4.6.3: non-blocking soft transition shared by title, route, slot and settings.
        if (game.settings.visualQuality > 0 && time < .2f) {
            float alpha = (1f - Math.min(1f,time/.2f));
            ui.rect(0,0,uiW(),uiH(),Ui.BG,alpha*.55f);
        }
        game.batch.end();
    }

    protected void update(float dt) {}
    protected void drawWorld() {}
    protected abstract void drawUi();
    /** Tombol kembali Android / Esc. */
    protected void onBack() {}
    protected void layout() {}

    protected void drawButtons() { for (UiButton b : buttons) ui.button(b); }

    @Override
    public void resize(int width, int height) {
        uiView.update(width, height, true);
        layout();
    }

    @Override public void pause() { game.audio.pauseAll(); }
    @Override public void resume() { game.audio.resumeAll(); }
    @Override public void hide() {}
    @Override public void dispose() {}

    // ------------------------------------------------------------ input
    @Override
    public boolean touchDown(int sx, int sy, int pointer, int button) {
        Vector2 v = toUi(sx, sy);
        if (confirm != null) { confirm.down(v.x, v.y, pointer); return true; }
        for (int i = buttons.size() - 1; i >= 0; i--) if (buttons.get(i).down(v.x, v.y, pointer)) return true;
        return false;
    }

    @Override
    public boolean touchUp(int sx, int sy, int pointer, int button) {
        Vector2 v = toUi(sx, sy);
        float x = v.x, y = v.y;
        if (confirm != null) { ConfirmBox c = confirm; if (c.up(x, y, pointer)) game.audio.sfx("menu_confirm", .55f); return true; }
        for (UiButton b : new ArrayList<>(buttons)) if (b.up(x, y, pointer)) { game.audio.sfx("menu_confirm", .55f); return true; }
        return false;
    }

    public boolean touchCancelled(int sx, int sy, int pointer, int button) {
        for (UiButton b : buttons) if (b.pointer == pointer) b.cancel();
        return false;
    }

    @Override
    public boolean keyDown(int keycode) {
        if (confirm != null) {
            if (keycode == Input.Keys.BACK || keycode == Input.Keys.ESCAPE) { if (confirm.no != null && confirm.no.onClick != null) confirm.no.onClick.run(); else confirm = null; }
            else if (keycode == Input.Keys.ENTER || keycode == Input.Keys.E) { if (confirm.yes.onClick != null) confirm.yes.onClick.run(); }
            return true;
        }
        if (keycode == Input.Keys.BACK || keycode == Input.Keys.ESCAPE) { onBack(); return true; }
        if (buttons.isEmpty()) return false;
        if (keycode == Input.Keys.DOWN || keycode == Input.Keys.RIGHT || keycode == Input.Keys.S || keycode == Input.Keys.D || keycode == Input.Keys.TAB) { moveFocus(1); return true; }
        if (keycode == Input.Keys.UP || keycode == Input.Keys.LEFT || keycode == Input.Keys.W || keycode == Input.Keys.A) { moveFocus(-1); return true; }
        if (keycode == Input.Keys.ENTER || keycode == Input.Keys.SPACE || keycode == Input.Keys.E) {
            if (focus >= 0 && focus < buttons.size()) {
                UiButton b = buttons.get(focus);
                if (b.enabled && b.visible && b.onClick != null) { game.audio.sfx("menu_confirm", .55f); b.onClick.run(); }
            }
            return true;
        }
        return false;
    }

    protected void moveFocus(int d) {
        int n = buttons.size();
        if (n == 0) return;
        for (int k = 0; k < n; k++) {
            focus = ((focus < 0 ? (d > 0 ? -1 : 0) : focus) + d + n) % n;
            UiButton b = buttons.get(focus);
            if (b.enabled && b.visible) break;
        }
        for (int i = 0; i < n; i++) buttons.get(i).focused = i == focus;
    }

    protected void clearFocus() { focus = -1; for (UiButton b : buttons) b.focused = false; }
}
