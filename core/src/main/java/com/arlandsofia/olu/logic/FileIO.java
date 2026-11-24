package com.arlandsofia.olu.logic;

/** Abstraksi file lokal privat aplikasi (implementasi: GdxFileIO di game, file biasa di test). */
public interface FileIO {
    /** null bila file tidak ada / gagal dibaca. */
    String read(String path);
    /** Tulis atomik: tulis ke file sementara lalu rename menimpa target. */
    boolean writeAtomic(String path, String content);
    boolean exists(String path);
    void delete(String path);
}
