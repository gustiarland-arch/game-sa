#!/usr/bin/env python3
"""Idempotent native registration: bonus global-route gate, music, FX, map climate."""
from pathlib import Path
R=Path(__file__).resolve().parents[1];base=R/'core/src/main/java/com/arlandsofia/olu'
qe=base/'logic/QuestEngine.java';s=qe.read_text()
if 'V473_BOTH_ROUTES_GATE' not in s:
 mark='    // ------------------------------------------------------------ kondisi\n'
 assert mark in s
 s=s.replace(mark,'    // V473_BOTH_ROUTES_GATE: global progress is shared by both save routes, never faked by local flags.\n    private GlobalProgress globalProgress;\n    public void setGlobalProgress(GlobalProgress progress) { this.globalProgress = progress; }\n\n'+mark)
 mark='        if (c == null || c.isEmpty()) return true;'
 assert mark in s
 s=s.replace(mark,mark+'\n        if (c.containsKey("bothRoutesCompleted") && Json.bool(c, "bothRoutesCompleted", false)\n                != (globalProgress != null && globalProgress.bothCompleted("C06"))) return false;')
 qe.write_text(s)
gs=base/'screens/GameScreen.java';s=gs.read_text()
mark='        this.engine = new QuestEngine(game.story, game.quests, game.maps, p, replay); // melempar bila step tidak dikenal'
if 'this.engine.setGlobalProgress(game.global);' not in s:
 assert mark in s
 s=s.replace(mark,mark+'\n        this.engine.setGlobalProgress(game.global);')
 gs.write_text(s)
snd=base/'logic/SoundscapePlan.java';s=snd.read_text()
if '"cinema_homecoming_v473"' not in s:
 s=s.replace('"cinema_hall_v472", "cinema_unwritten_v472"','"cinema_hall_v472", "cinema_unwritten_v472", "cinema_homecoming_v473", "cinema_dual_letters_v473"')
if '"v473_letter_fold"' not in s:s=s.replace('"v472_memory_glint"','"v472_memory_glint", "v473_letter_fold"')
if 'if ("ruang_dua_surat".equals(area)) return "library_whisper";' not in s:
 s=s.replace('if ("perpustakaan".equals(area)) return "library_whisper";',
             'if ("perpustakaan".equals(area)) return "library_whisper";\n        if ("ruang_dua_surat".equals(area)) return "library_whisper";')
if 'if ("ruang_dua_surat".equals(area)) return "library_room";' not in s:
 s=s.replace('if ("perpustakaan".equals(area) || "ruang_arsip".equals(area)) return rainy ? "rain_window" : "library_room";',
             'if ("ruang_dua_surat".equals(area)) return "library_room";\n        if ("perpustakaan".equals(area) || "ruang_arsip".equals(area)) return rainy ? "rain_window" : "library_room";')
s=s.replace('|| "galeri_komunitas".equals(area) || "clockwork_station".equals(area) || "hall_of_tomorrow".equals(area)) return "step_wood";',
            '|| "galeri_komunitas".equals(area) || "clockwork_station".equals(area) || "hall_of_tomorrow".equals(area) || "ruang_dua_surat".equals(area)) return "step_wood";')
snd.write_text(s)
world=base/'logic/WorldAtmosphereV462.java';s=world.read_text()
if '"ruang_dua_surat"' not in s:
 s=s.replace('"clockwork_station","moonlight_lake","memory_bridge","hall_of_tomorrow"',
             '"clockwork_station","moonlight_lake","memory_bridge","hall_of_tomorrow","ruang_dua_surat"')
 s=s.replace('STAR,WATER,STAR,STAR\n    };','STAR,WATER,STAR,STAR,HOME\n    };')
 world.write_text(s)
assert all(token in snd.read_text() for token in ('"cinema_homecoming_v473"','"cinema_dual_letters_v473"','"v473_letter_fold"'))
assert 'V473_BOTH_ROUTES_GATE' in qe.read_text() and 'this.engine.setGlobalProgress(game.global);' in gs.read_text()
print('PASS: global chapter-completion gate and native audio/environment registered')
