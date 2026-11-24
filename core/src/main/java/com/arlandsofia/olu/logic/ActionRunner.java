package com.arlandsofia.olu.logic;

import java.util.ArrayDeque;
import java.util.List;
import java.util.ListIterator;
import java.util.Map;

/**
 * Menjalankan daftar aksi secara berurutan. Aksi presentasi (scene, lines, puzzle, minigame, warp, kartu, kredit)
 * menunggu callback dari Presenter; aksi state diterapkan ke QuestEngine; "if" bercabang sesuai kondisi.
 */
public final class ActionRunner {

    public interface BoolCallback { void done(boolean ok); }
    public interface IntCallback { void done(int score); }

    public interface Presenter {
        void playScene(String sceneId, Runnable done);
        /** Dialog ad-hoc (NPC, side quest). */
        void playLines(List<StoryDb.Line> lines, String speakerName, Runnable done);
        void openPuzzle(String puzzleId, BoolCallback done);
        void openMinigame(String id, IntCallback done);
        void openShop(String shopId, Runnable done);
        void warp(String area, float x, float y, String dir, Runnable done);
        void chapterCard(String chapter, Runnable done);
        void chapterEnd(String chapter, Runnable done);
        void credits(Runnable done);
        /** Cutscene sinematik: daftar perintah kamera/aktor/efek/dialog (lihat CutscenePlayer). */
        void cine(List<Map<String, Object>> cmds, Runnable done);
        void toast(String text);
        void sfx(String id);
        void music(String id);
        void emote(String who, String emote);
        void companionChanged(boolean on);
        void stepChanged();
        /** Antrian kosong -> tempat autosave. */
        void onIdle();
    }

    private final QuestEngine engine;
    private final Presenter presenter;
    private final ArrayDeque<Map<String, Object>> queue = new ArrayDeque<>();
    private boolean waiting, pumping;

    public ActionRunner(QuestEngine engine, Presenter presenter) { this.engine = engine; this.presenter = presenter; }

    public boolean busy() { return waiting || !queue.isEmpty(); }

    public void run(List<Map<String, Object>> actions) {
        queue.addAll(actions);
        pump();
    }

    private void resume() { waiting = false; pump(); }

    private void pushFront(List<Map<String, Object>> actions) {
        ListIterator<Map<String, Object>> it = actions.listIterator(actions.size());
        while (it.hasPrevious()) queue.addFirst(it.previous());
    }

    private void pump() {
        if (pumping) return;
        pumping = true;
        try {
            while (!waiting) {
                if (queue.isEmpty()) {
                    List<Map<String, Object>> more = engine.checkComplete();
                    if (more.isEmpty()) break;
                    queue.addAll(more);
                    continue;
                }
                execute(queue.poll());
            }
        } finally {
            pumping = false;
        }
        if (!waiting && queue.isEmpty()) presenter.onIdle();
    }

    private void execute(Map<String, Object> a) {
        String d = Json.str(a, "do", "");
        switch (d) {
            case "scene": {
                final StoryDb.Scene sc = engine.story.scene(Json.str(a, "id", ""));
                if (sc == null) return; // scene hilang: lewati, jangan softlock
                waiting = true;
                presenter.playScene(sc.id, new Runnable() { public void run() { engine.addFlags(sc.flags); resume(); } });
                return;
            }
            case "lines": {
                List<StoryDb.Line> lines = StoryDb.lines(a, "lines");
                if (lines.isEmpty()) return;
                waiting = true;
                presenter.playLines(lines, Json.str(a, "name", null), new Runnable() { public void run() { resume(); } });
                return;
            }
            case "if": {
                boolean ok = engine.check(Json.obj(a, "when"));
                pushFront(engine.resolve(Json.objList(a, ok ? "then" : "else")));
                return;
            }
            case "puzzle":
                waiting = true;
                presenter.openPuzzle(Json.str(a, "id", ""), new BoolCallback() {
                    public void done(boolean ok) { if (!ok) queue.clear(); resume(); }
                });
                return;
            case "minigame": {
                final String id = Json.str(a, "id", "");
                waiting = true;
                presenter.openMinigame(id, new IntCallback() {
                    public void done(int score) {
                        if (score < 0) { queue.clear(); resume(); return; }   // batal
                        engine.p.flags.add("MG_" + id.toUpperCase(java.util.Locale.ROOT) + "_DONE");
                        engine.p.addCount("last_" + id, score - engine.p.count("last_" + id));
                        int best = engine.p.count("best_" + id);
                        if (score > best) engine.p.addCount("best_" + id, score - best);
                        resume();
                    }
                });
                return;
            }
            case "romanceGame": {
                final String id = Json.str(a, "id", "");
                final QuestDb.RomanceGame rg = engine.romanceGame(id);
                final String area = Json.str(a, "area", engine.p.area);
                if (rg == null || engine.romanceGameBlock(id, area) != null) {
                    presenter.toast("Kegiatan berdua tidak tersedia di sini."); return;
                }
                waiting = true;
                presenter.openMinigame(rg.minigame, new IntCallback() {
                    public void done(int score) {
                        if (score < 0) { presenter.toast("Permainan dibatalkan."); resume(); return; }
                        boolean first = !engine.p.hasFlag("ROM_GAME_" + id.toUpperCase(java.util.Locale.ROOT) + "_ONCE");
                        String result = engine.completeRomanceGame(id, area, score);
                        presenter.toast(result);
                        if (first && score >= rg.minScore && result.startsWith("Kenangan baru!")) {
                            StoryDb.Scene sc = engine.story.scene(rg.scene(engine.p.route));
                            if (sc != null) { presenter.playScene(sc.id, new Runnable() { public void run() { resume(); } }); return; }
                        }
                        resume();
                    }
                });
                return;
            }
            case "shop": {
                String id = Json.str(a, "id", "");
                if (!engine.quests.shops.containsKey(id)) { presenter.toast("Toko tidak tersedia."); return; }
                waiting = true;
                presenter.openShop(id, new Runnable() { public void run() { resume(); } });
                return;
            }
            case "work": {
                final String jobId = Json.str(a, "id", "");
                final QuestDb.Job job = engine.quests.jobs.get(jobId);
                if (job == null || job.minigame.isEmpty() || !engine.jobReady(jobId)) {
                    presenter.toast("Shift hari ini tidak tersedia."); return;
                }
                waiting = true;
                presenter.openMinigame(job.minigame, new IntCallback() {
                    public void done(int score) {
                        if (score >= 0) {
                            engine.p.addCount("last_" + job.minigame, score - engine.p.count("last_" + job.minigame));
                            presenter.toast(engine.completeWork(jobId, score));
                        }
                        resume();
                    }
                });
                return;
            }
            case "worldEvent": {
                String id = Json.str(a, "id", "");
                presenter.toast(engine.completeWorldEvent(id, engine.p.area));
                return;
            }
            case "deliveryStart": presenter.toast(engine.startDelivery()); return;
            case "deliveryDrop": presenter.toast(engine.deliver(Json.str(a, "address", ""))); return;
            case "warp":
                waiting = true;
                presenter.warp(Json.str(a, "area", ""), Json.num(a, "x", 0), Json.num(a, "y", 0), Json.str(a, "dir", "down"),
                        new Runnable() { public void run() { resume(); } });
                return;
            case "chapterCard":
                waiting = true;
                presenter.chapterCard(Json.str(a, "chapter", ""), new Runnable() { public void run() { resume(); } });
                return;
            case "chapterEnd":
                engine.apply(a);
                waiting = true;
                presenter.chapterEnd(Json.str(a, "chapter", ""), new Runnable() { public void run() { resume(); } });
                return;
            case "credits":
                waiting = true;
                presenter.credits(new Runnable() { public void run() { resume(); } });
                return;
            case "cine": {
                final List<Map<String, Object>> cmds = engine.resolve(Json.objList(a, "cmds"));
                waiting = true;
                presenter.cine(cmds, new Runnable() { public void run() {
                    for (Map<String, Object> c : cmds)
                        if ("say".equals(Json.str(c, "c", ""))) { StoryDb.Scene sc = engine.story.scene(Json.str(c, "scene", "")); if (sc != null) engine.addFlags(sc.flags); }
                    resume();
                } });
                return;
            }
            case "toast": presenter.toast(Json.str(a, "text", "")); return;
            case "sfx": presenter.sfx(Json.str(a, "id", "")); return;
            case "music": presenter.music(Json.str(a, "id", "")); return;
            case "emote": presenter.emote(Json.str(a, "who", ""), Json.str(a, "e", "heart")); return;
            case "companion": engine.apply(a); presenter.companionChanged(engine.p.companion); return;
            case "step": {
                engine.apply(a); presenter.stepChanged();
                QuestDb.Step ns = engine.step();
                if (ns != null && !ns.onStart.isEmpty()) pushFront(engine.resolve(ns.onStart));
                return;
            }
            default: engine.apply(a);
        }
    }
}
