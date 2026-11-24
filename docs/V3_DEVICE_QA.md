# QA Android v3.0 — Daftar Pengujian Manual yang Belum Diverifikasi

Isi kolom perangkat/tanggal/Hasil untuk setiap tes saat APK sudah berhasil dikompilasi. Tidak ada hasil "Lulus" yang diisi tanpa eksekusi di Android nyata.

| ID | Perangkat/area | Skenario | Status |
|---|---|---|---|
| A01 | Instalasi | `assembleDebug` dan instal APK dari source v3.0 | BELUM DIUJI |
| A02 | Distribusi | Signed AAB dibuat dan diverifikasi | BELUM DIUJI |
| A03 | Native | ELF arm64/x86_64 & ZIP 16 KB alignment | BELUM DIUJI |
| A04 | Native | Emulator/perangkat 16 KB page size | BELUM DIUJI |
| A05 | Runtime | Masuk judul → route Arland → slot 1 | BELUM DIUJI |
| A06 | Runtime | Masuk judul → route Sofia → slot 2 | BELUM DIUJI |
| A07 | Render | 22 area, tak ada sprite hilang / tekstur error | BELUM DIUJI |
| A08 | Audio | Transisi 40 BGM, tidak menumpuk saat pause/resume | BELUM DIUJI |
| A09 | Audio | 14 ambience dan 32 efek pada speaker/headset | BELUM DIUJI |
| A10 | Audio | Kabel/headset Bluetooth terputus saat bermain | BELUM DIUJI |
| A11 | Save | Update dari 2.9 tanpa uninstall, load schema 6 | BELUM DIUJI |
| A12 | Save | Simpan schema 7, quit, cold restart, data utuh | BELUM DIUJI |
| A13 | Save | Simulasi utama korup, pulih `.bak` tanpa menimpa cadangan | BELUM DIUJI |
| A14 | Save | Storage hampir penuh, pesan gagal tidak menipu | BELUM DIUJI |
| A15 | Dialog | Tombol Riwayat, 72 baris, pilihan, paginasi | BELUM DIUJI |
| A16 | Dialog | Buka Riwayat saat cutscene; lanjut dan tidak softlock | BELUM DIUJI |
| A17 | Jelajah | Perjalanan ke 22 area tercatat per route | BELUM DIUJI |
| A18 | Kompas | Tunjuk marker quest terdekat dengan akurat | BELUM DIUJI |
| A19 | Joystick | Tiga jari; lari+aksi+gerak, kidal/tangan kanan | BELUM DIUJI |
| A20 | UI | Landscape, notch/inset, tablet, resolusi 16:9 & 20:9 | BELUM DIUJI |
| A21 | Cerita | Route Arland sampai epilog, semua misi penting | BELUM DIUJI |
| A22 | Cerita | Route Sofia sampai epilog, semua misi penting | BELUM DIUJI |
| A23 | Romansa | 8 aksi bersama, 6 minigame, anti-farming bonus | BELUM DIUJI |
| A24 | Dunia | 14 event waktu/cuaca, jadwal NPC dan hewan | BELUM DIUJI |
| A25 | Baterai | Main 30–60 menit, catat frame time, RAM, suhu | BELUM DIUJI |
| A26 | Recovery | Home/panggilan masuk/force-close saat dialog & puzzle | BELUM DIUJI |
| A27 | Accessibility | Teks lambat, volume, font, area tap, fokus keyboard | BELUM DIUJI |
| A28 | Performance | Kelas RAM rendah/menengah/tinggi, stress peta besar | BELUM DIUJI |
| A29 | Privacy | Manifest merged tanpa permission network | BELUM DIUJI |
| A30 | Play | Internal/closed testing, store listing, data safety | BELUM DIUJI |

## Exit criteria

Tidak ada crash atau softlock pada kedua route; semua save lama dapat dibaca tanpa uninstall, tidak ada kehilangan progres; audio dan grafis stabil pada 3 kelas perangkat; APK signed lolos pemeriksaan native 16 KB; hak aset dan kebutuhan Google Play sudah dipenuhi. Baru setelah itu tandai build sebagai Release Candidate terverifikasi.
