# Rekaman gameplay desktop (v5.4)

Harness ini menjalankan `OluGame`/`GameScreen` asli di desktop (LWJGL3) dengan langkah waktu tetap
30 fps, menggerakkan joystick melayang lewat InputProcessor milik layar, lalu mengirim setiap frame
ke `ffmpeg`. Rute jalan dihitung dengan A* game (`QuestPathV52`). Semua suara yang dimainkan game
dicatat lewat `AudioManager.tap` ke `audio.tsv`.

Bukan bagian dari APK dan bukan pengganti uji di HP.

```bash
# 1) Rekam (perlu ffmpeg; di server tanpa layar pakai xvfb-run)
cd android/assets
xvfb-run -a -s "-screen 0 1600x720x24" gradle -p ../../tools/capture_v54 run --args="/tmp/out C05_FREE 4"
# 2) Campur audio dari file audio game sesuai log, lalu gabungkan
python3 tools/capture_v54/mix_audio.py /tmp/out/audio.tsv /tmp/out/mix.f32 60 android/assets/
ffmpeg -i /tmp/out/video.mp4 -f f32le -ar 44100 -ac 1 -i /tmp/out/mix.f32 -c:v copy -c:a aac -shortest gameplay.mp4
```

Hari 4 adalah hari hujan (`WorldClock.weather`). Argumen ke-4 `stills` menyimpan PNG, bukan video.
Mixdown memakai volume default game; crossfade musik antar-adegan disederhanakan.
