package com.arlandsofia.olu.ui;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.Color;
import com.arlandsofia.olu.Assets;
/** Tidak menggambar apa pun; hanya untuk verifikasi event tombol. */
public class Ui {
    public final Assets a = new Assets();
    public static final Color BG = new Color(), CREAM = new Color(), GOLD = new Color(),
            INK = new Color(), INK_SOFT = new Color(), PINK = new Color(), PINK_DEEP = new Color(),
            LAVENDER = new Color(), WHITE = new Color();
    public void rect(float x, float y, float w, float h, Object color, float alpha) {}
    public void panel(Object panel, float x, float y, float w, float h, float alpha) {}
    public void image(Texture t, float x, float y, float w, float h, float alpha) {}
    public float text(Object font, String text, float x, float y, Object color, float scale, int align, float width) { return 0f; }
    public float measure(Object f, String text, float scale) { return text.length() * 8f * scale; }
    public float wrap(Object f, String text, float x, float y, float width, Object color, float scale, int align) {return 40f;}
    public void textCenter(Object font, String value, float x, float y, Object color, float scale) {}
    public void button(UiButton b) {}
}
