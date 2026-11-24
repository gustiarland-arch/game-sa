package com.arlandsofia.olu.ui;

import com.arlandsofia.olu.Assets;
import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.BitmapFont;
import com.badlogic.gdx.graphics.g2d.GlyphLayout;
import com.badlogic.gdx.graphics.g2d.NinePatch;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.utils.Align;

/** Helper gambar UI immediate-mode (tanpa scene2d agar ringan dan mudah diubah). */
public final class Ui {
    public static final Color INK = new Color(0x3b3049ff);
    public static final Color INK_SOFT = new Color(0x6a5a80ff);
    public static final Color CREAM = new Color(0xfbf3eeff);
    public static final Color PINK = new Color(0xe89cb4ff);
    public static final Color PINK_DEEP = new Color(0xc4567eff);
    public static final Color LAVENDER = new Color(0x9b8ab8ff);
    public static final Color GOLD = new Color(0xffd678ff);
    public static final Color BG = new Color(0x2c2240ff);
    public static final Color WHITE = new Color(1, 1, 1, 1);

    public final Assets a;
    public final SpriteBatch batch;
    private final GlyphLayout layout = new GlyphLayout();
    private final Color tmp = new Color();

    public Ui(Assets a, SpriteBatch batch) { this.a = a; this.batch = batch; }

    public void rect(float x, float y, float w, float h, Color c, float alpha) {
        batch.setColor(c.r, c.g, c.b, c.a * alpha);
        batch.draw(a.pixel, x, y, w, h);
        batch.setColor(1, 1, 1, 1);
    }

    public void panel(NinePatch p, float x, float y, float w, float h, float alpha) {
        batch.setColor(1, 1, 1, alpha);
        p.draw(batch, x, y, Math.max(w, 40), Math.max(h, 40));
        batch.setColor(1, 1, 1, 1);
    }

    public void image(Texture t, float x, float y, float w, float h, float alpha) {
        batch.setColor(1, 1, 1, alpha);
        batch.draw(t, x, y, w, h);
        batch.setColor(1, 1, 1, 1);
    }

    /** Preserve pixel-art source proportions: crop sides/top to fill landscape/tablet aspect ratios. */
    public void imageCover(Texture t, float x, float y, float w, float h, float alpha) {
        float scale = Math.max(w / t.getWidth(), h / t.getHeight());
        float iw = t.getWidth() * scale, ih = t.getHeight() * scale;
        image(t, x + (w - iw) / 2f, y + (h - ih) / 2f, iw, ih, alpha);
    }

    /** Teks satu baris; y = garis atas teks. Mengembalikan lebar. */
    public float text(BitmapFont f, String s, float x, float y, Color c, float scaleMul, int align, float width) {
        float base = f.getData().scaleX;
        f.getData().setScale(base * scaleMul);
        f.setColor(c);
        layout.setText(f, s, c, width, align, false);
        f.draw(batch, layout, x, y);
        float w = layout.width;
        f.getData().setScale(base);
        f.setColor(1, 1, 1, 1);
        return w;
    }

    public float text(BitmapFont f, String s, float x, float y, Color c) { return text(f, s, x, y, c, 1f, Align.left, 0); }

    public void textCenter(BitmapFont f, String s, float cx, float y, Color c, float scaleMul) {
        text(f, s, cx - 2000, y, c, scaleMul, Align.center, 4000);
    }

    /** Teks dengan wrap; mengembalikan tinggi. */
    public float wrap(BitmapFont f, String s, float x, float y, float width, Color c, float scaleMul, int align) {
        float base = f.getData().scaleX;
        f.getData().setScale(base * scaleMul);
        f.setColor(c);
        layout.setText(f, s, c, width, align, true);
        f.draw(batch, layout, x, y);
        float h = layout.height;
        f.getData().setScale(base);
        f.setColor(1, 1, 1, 1);
        return h;
    }

    public float measure(BitmapFont f, String s, float scaleMul) {
        float base = f.getData().scaleX;
        f.getData().setScale(base * scaleMul);
        layout.setText(f, s);
        float w = layout.width;
        f.getData().setScale(base);
        return w;
    }

    public float lineHeight(BitmapFont f, float scaleMul) { return f.getLineHeight() * scaleMul; }

    public void button(UiButton b) {
        if (!b.visible) return;
        NinePatch p = !b.enabled ? a.buttonDisabled : (b.pressed ? a.buttonDown : (b.accent ? a.buttonAccent : a.button));
        float off = b.pressed ? -2f : 0f;
        // Subtle shadow and edge highlight: retains original editable nine-patch textures.
        if(b.enabled && !b.pressed) rect(b.x+3,b.y-4,b.w,b.h,INK,.22f);
        panel(p, b.x, b.y + off, b.w, b.h, 1f);
        if(b.accent && b.enabled) rect(b.x+14,b.y+off+b.h-5,b.w-28,2,GOLD,.45f);
        if (b.focused) {
            tmp.set(GOLD);
            rect(b.x + 14, b.y + off + 6, b.w - 28, 3, tmp, 1f);
        }
        Color c = b.enabled ? INK : INK_SOFT;
        float textW = b.w - 20;
        float x = b.x + 10;
        if (b.icon != null) {
            float s = Math.min(b.h - 20, 40);
            image(b.icon, b.x + 16, b.y + off + (b.h - s) / 2f, s, s, b.enabled ? 1f : 0.5f);
            x = b.x + 16 + s + 6; textW = b.w - (x - b.x) - 10;
        }
        float fitScale=b.textScale;
        float measured=measure(a.body,b.label,fitScale);
        if(measured>textW && measured>0) fitScale=Math.max(.55f,fitScale*textW/measured);
        float lh=a.body.getCapHeight()*fitScale;
        text(a.body,b.label,x,b.y+off+b.h/2f+lh/2f,c,fitScale,
                b.icon!=null?Align.left:Align.center,textW);
    }
}
