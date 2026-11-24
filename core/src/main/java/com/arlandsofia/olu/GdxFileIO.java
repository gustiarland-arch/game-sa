package com.arlandsofia.olu;

import com.arlandsofia.olu.logic.FileIO;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.files.FileHandle;

/** File di penyimpanan privat aplikasi (Gdx.files.local = internal storage app di Android). */
public final class GdxFileIO implements FileIO {
    @Override
    public String read(String path) {
        try {
            FileHandle f = Gdx.files.local(path);
            return f.exists() ? f.readString("UTF-8") : null;
        } catch (Exception e) {
            if (Gdx.app != null) Gdx.app.error("OLU", "Gagal membaca file privat: " + path, e);
            return null;
        }
    }

    @Override
    public boolean writeAtomic(String path, String content) {
        try {
            FileHandle target = Gdx.files.local(path);
            target.parent().mkdirs();
            FileHandle tmp = Gdx.files.local(path + ".tmp");
            tmp.writeString(content, false, "UTF-8");
            // Kedua file ada di direktori dan filesystem yang sama. Android/Linux
            // mendukung atomic rename replacement; JANGAN fallback copy+delete target
            // (tulis parsial akan menghilangkan progres lama bila listrik mati).
            if (!tmp.file().renameTo(target.file())) {
                Gdx.app.error("OLU", "Rename save gagal; file asli dipertahankan: " + path);
                return false;
            }
            return true;
        } catch (Exception e) {
            Gdx.app.error("OLU", "Gagal menyimpan " + path, e);
            return false;
        }
    }

    @Override
    public boolean exists(String path) {
        try { return Gdx.files.local(path).exists(); } catch (Exception e) { return false; }
    }

    @Override
    public void delete(String path) {
        try { Gdx.files.local(path).delete(); } catch (Exception ignored) { }
    }
}
