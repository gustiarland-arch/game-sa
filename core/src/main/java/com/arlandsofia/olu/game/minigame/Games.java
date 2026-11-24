package com.arlandsofia.olu.game.minigame;

import com.arlandsofia.olu.logic.Json;
import com.arlandsofia.olu.logic.EchoPatternV49;
import com.arlandsofia.olu.ui.Ui;
import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.math.MathUtils;
import com.badlogic.gdx.utils.Align;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Random;

/** Kumpulan minigame. Tidak ada kondisi gagal permanen: semua bisa diulang sampai selesai. */
public final class Games {
    private Games() {}

    public static Minigame create(String id) {
        switch (id) {
            case "v49_echo": return new MemoryEchoV49();
            case "bouquet": return new Bouquet();
            case "scrapbook": return new Scrapbook();
            case "photobooth": return new Photobooth();
            case "cooking": return new Cooking();
            case "lanterns": return new Lanterns();
            case "starmap": return new StarMap();
            case "pages":
            case "quiet_pages":
            case "v26_night_pages": return new Pages();
            case "claw": return new Claw();
            case "fishing": return new Fishing();
            case "starcatch": return new StarCatch();
            case "ringtoss": return new RingToss();
            case "pour": return new Pour();
            case "code":
            case "quiet_cipher":
            case "v26_night_compass": return new CodeLock();
            default: return new Photobooth();
        }
    }

    static final Color GREEN = new Color(0.45f, 0.78f, 0.5f, 1f), RED = new Color(0.9f, 0.45f, 0.5f, 1f);
    static final Color tmp = new Color();


    // ============================================================ v2.5 MERANGKAI BUKET
    /** Empat tangkai, tiga jenis bunga. Petunjuk dan susunan awal berbeda per POV. */
    static final class Bouquet extends Minigame {
        static final String[] FLOWERS = {"Mawar", "Tulip", "Melati"};
        static final Color[] COLORS = {new Color(.87f,.40f,.59f,1), new Color(.95f,.76f,.38f,1), new Color(.92f,.94f,.95f,1)};
        final int[] chosen = {0, 0, 0, 0};
        int[] pattern; String message = ""; float messageT;
        protected void start() {
            pattern = "sofia".equals(route) ? new int[]{2, 0, 1, 2} : new int[]{0, 1, 2, 0};
            for (int i=0;i<chosen.length;i++) chosen[i] = (pattern[i] + i + 1) % 3;
        }
        public void update(float dt) { super.update(dt); if (messageT > 0) messageT-=dt; }
        public void tap(float px, float py) {
            if (finished) return;
            float start=x+Math.max(18,(w-4*138)/2f), cy=y+h*.33f;
            for (int i=0;i<4;i++) if (in(px,py,start+i*138+8,cy,118,180)) {
                chosen[i]=(chosen[i]+1)%3; audio.sfx("flower_pick"); message="Bunga ke-"+(i+1)+": "+FLOWERS[chosen[i]];messageT=1.0f;return;
            }
            if (in(px,py,x+w/2-120,y+20,240,60)) submit();
        }
        void submit() {
            int matches=0; for (int i=0;i<4;i++) if (chosen[i]==pattern[i]) matches++;
            if (matches==4) { score=4; finished=true; resultText="Buket cocok! Dua tangan, satu rangkaian yang indah.";audio.sfx("quest_complete"); }
            else { message=matches+" dari 4 bunga cocok. Periksa kartu pesanan!";messageT=2.8f;audio.sfx("soft_wrong"); }
        }
        public void key(int index) {
            if (index==99) submit(); else if (index>=0 && index<4) {chosen[index]=(chosen[index]+1)%3;audio.sfx("page");}
        }
        public void draw(Ui ui) {
            StringBuilder hint=new StringBuilder("Pesanan: ");
            for (int k=0;k<pattern.length;k++) {if(k>0) hint.append(" • ");hint.append(FLOWERS[pattern[k]]);}
            ui.text(a.body,hint.toString(),x+10,y+h-22,Ui.INK,.83f,Align.center,w-20);
            float start=x+Math.max(18,(w-4*138)/2f),cy=y+h*.33f;
            for (int i=0;i<4;i++) {
                float cx=start+i*138+8;
                ui.panel(a.panel,cx,cy,118,180,1f);
                ui.rect(cx+52,cy+27,12,92,GREEN,.75f);
                for(int petal=0;petal<6;petal++) {
                    float ang=petal*6.28318f/6f;
                    ui.rect(cx+50+MathUtils.cos(ang)*17,cy+118+MathUtils.sin(ang)*17,17,17,COLORS[chosen[i]],1f);
                }
                ui.rect(cx+56,cy+124,9,9,Ui.GOLD,1f);
                ui.text(a.body,FLOWERS[chosen[i]],cx,cy+163,Ui.INK,.76f,Align.center,118);
            }
            ui.panel(a.button,x+w/2-120,y+20,240,60,1f);
            ui.text(a.body,"Cek buket",x+w/2-120,y+62,Ui.INK,.88f,Align.center,240);
            ui.text(a.body,messageT>0?message:"Ketuk satu bunga untuk mengganti jenisnya",x,y+114,Ui.LAVENDER,.77f,Align.center,w);
        }
    }

    // ============================================================ v2.5 SCRAPBOOK KENANGAN
    /** Ketuk dua kartu untuk menukarnya, lalu cek susunan. Murni input, tanpa random reward. */
    static final class Scrapbook extends Minigame {
        static final String[] MOMENTS={"Plaza", "Memory Garden", "Kafe Senja", "Festival"};
        static final String[] ICONS={"items/postcard.png", "items/memory_page.png", "items/letter_two_sides.png", "items/lantern_paper.png"};
        final int[] order = {2,0,3,1};
        int selected=-1, moves; String message="Susun kenangan dari paling awal ke paling akhir.";
        protected void start() { if("sofia".equals(route)){order[0]=1;order[1]=3;order[2]=0;order[3]=2;} }
        void select(int pos) {
            if(selected<0) {selected=pos;audio.sfx("page");return;}
            if(selected!=pos) {int tmp=order[selected];order[selected]=order[pos];order[pos]=tmp;moves++;audio.sfx("paper_fold");}
            selected=-1;
        }
        void submit() {
            int good=0;for(int i=0;i<4;i++) if(order[i]==i)good++;
            if(good==4) {score=Math.max(1,12-moves);finished=true;resultText="Album tersusun! " + moves + " kali menukar halaman.";audio.sfx("quest_complete");}
            else {message=good+" dari 4 halaman sudah benar. Coba urutkan lagi.";audio.sfx("soft_wrong");}
        }
        public void tap(float px,float py) {
            if(finished)return;
            float start=x+Math.max(20,(w-4*148)/2f),by=y+h*.34f;
            for(int i=0;i<4;i++) if(in(px,py,start+i*148,by,136,172)){select(i);return;}
            if(in(px,py,x+w/2-118,y+22,236,56))submit();
        }
        public void key(int i) {if(i==99)submit();else if(i>=0&&i<4)select(i);}
        public void draw(Ui ui) {
            ui.text(a.body,"Urutan: Plaza → Memory Garden → Kafe Senja → Festival",x,y+h-16,Ui.INK,.79f,Align.center,w);
            float start=x+Math.max(20,(w-4*148)/2f),by=y+h*.34f;
            for(int i=0;i<4;i++) {
                float bx=start+i*148;
                ui.panel(selected==i?a.button:a.panel,bx,by,136,172,1f);
                ui.image(a.tex(ICONS[order[i]]),bx+38,by+60,60,76,1f);
                ui.text(a.body,MOMENTS[order[i]],bx+3,by+38,Ui.INK,.72f,Align.center,130);
                ui.text(a.body,""+(i+1)+(selected==i?" • dipilih":""),bx+3,by+156,Ui.GOLD,.7f,Align.center,130);
            }
            ui.panel(a.button,x+w/2-118,y+22,236,56,1f);
            ui.text(a.body,"Simpan album",x+w/2-118,y+62,Ui.INK,.85f,Align.center,236);
            ui.text(a.body,message,x,y+120,Ui.LAVENDER,.75f,Align.center,w);
        }
    }

    // ============================================================ PHOTOBOOTH
    static final class Photobooth extends Minigame {
        int shots, total = 3; float cursor, dir = 1, flash, cool;
        final List<Integer> quality = new ArrayList<>();
        protected void start() { total = (int) Json.num(cfg, "shots", 3); }
        public void update(float dt) {
            super.update(dt);
            if (flash > 0) flash -= dt;
            if (cool > 0) { cool -= dt; return; }
            if (shots >= total) return;
            cursor += dir * dt * (0.75f + shots * 0.18f);
            if (cursor > 1) { cursor = 1; dir = -1; } else if (cursor < 0) { cursor = 0; dir = 1; }
        }
        public void tap(float px, float py) {
            if (shots >= total || cool > 0) return;
            float d = Math.abs(cursor - 0.5f);
            int q = d < 0.06f ? 3 : d < 0.16f ? 2 : 1;
            quality.add(q); score += q; shots++; flash = 0.35f; cool = 0.7f;
            audio.sfx(q == 3 ? "sparkle" : "page");
            if (shots >= total) { finished = true; resultText = score >= 8 ? "Foto sempurna! Kalian kompak sekali." : score >= 5 ? "Fotonya manis!" : "Fotonya lucu-lucu. Kenangan tetap kenangan!"; }
        }
        public void key(int i) { tap(0, 0); }
        public void draw(Ui ui) {
            float fw = 150, fh = 120, gap = 20, fx0 = x + (w - (fw * total + gap * (total - 1))) / 2, fy = y + h - fh - 20;
            for (int i = 0; i < total; i++) {
                float fx = fx0 + i * (fw + gap);
                ui.panel(a.panelDark, fx - 6, fy - 6, fw + 12, fh + 12, 1f);
                if (i < quality.size()) {
                    int q = quality.get(i);
                    String ea = q == 3 ? "senang" : q == 2 ? "normal" : "kaget";
                    String es = q == 3 ? "tertawa" : q == 2 ? "senang" : "kaget";
                    ui.rect(fx, fy, fw, fh, tmp.set(1f, 0.93f, 0.95f, 1f), 1f);
                    Texture ta = a.portrait("arland", Arrays.asList(ea, "normal")), ts = a.portrait("sofia", Arrays.asList(es, "normal"));
                    float ph = fh - 8, pw = ph * ta.getWidth() / ta.getHeight();
                    ui.image(ta, fx + 4, fy + 4, pw * 0.92f, ph, 1f); ui.image(ts, fx + fw - pw * 0.92f - 4, fy + 4, pw * 0.92f, ph, 1f);
                    ui.text(a.body, q == 3 ? "★★★" : q == 2 ? "★★" : "★", fx, fy + 22, Ui.GOLD, 0.8f, Align.center, fw);
                } else ui.text(a.body, "Foto " + (i + 1), fx, fy + fh / 2 + 10, Ui.CREAM, 0.9f, Align.center, fw);
            }
            float bx = x + 60, bw = w - 120, by = y + 120, bh = 34;
            ui.rect(bx, by, bw, bh, tmp.set(0.3f, 0.25f, 0.4f, 1f), 1f);
            ui.rect(bx + bw * 0.34f, by, bw * 0.32f, bh, GREEN, 0.55f);
            ui.rect(bx + bw * 0.44f, by, bw * 0.12f, bh, Ui.GOLD, 0.9f);
            ui.image(a.uiTex("ui/icon_heart.png"), bx + bw * cursor - 22, by - 6, 44, 44, 1f);
            ui.text(a.body, shots < total ? "Ketuk saat hati di tengah! (" + (shots + 1) + "/" + total + ")" : "Selesai!", x, by + 80, Ui.INK, 0.95f, Align.center, w);
            if (flash > 0) ui.rect(x - 400, y - 400, w + 800, h + 800, Ui.WHITE, flash * 2f);
        }
    }

    // ============================================================ COOKING
    static final class Cooking extends Minigame {
        List<String> steps; int idx; float needle, speed = 1.1f, zone = 0.5f, zoneW = 0.22f, msgT; String msg = "";
        final List<Boolean> results = new ArrayList<>(); final Random rng = new Random(7);
        protected void start() { steps = Json.strList(cfg, "steps"); if (steps.isEmpty()) steps = Arrays.asList("Potong", "Oles", "Tata"); newZone(); }
        void newZone() { zone = 0.25f + rng.nextFloat() * 0.5f; zoneW = Math.max(0.12f, 0.24f - idx * 0.02f); speed = 0.9f + idx * 0.15f; }
        public void update(float dt) {
            super.update(dt);
            if (msgT > 0) msgT -= dt;
            if (finished) return;
            needle = (MathUtils.sin(t * speed * 2.6f) + 1f) / 2f;
        }
        public void tap(float px, float py) {
            if (finished || msgT > 0.6f) return;
            boolean ok = Math.abs(needle - zone) <= zoneW / 2;
            results.add(ok); if (ok) score++;
            audio.sfx(ok ? "sparkle" : "soft_wrong");
            msg = ok ? "Pas sekali!" : "Sedikit meleset, tidak apa-apa!"; msgT = 0.9f;
            idx++;
            if (idx >= steps.size()) { finished = true; resultText = score == steps.size() ? "Sempurna! Wangi madu ke mana-mana." : score >= steps.size() / 2 ? "Enak! Sedikit berantakan, tapi enak." : "Agak gosong... tapi dibuat bareng, jadi tetap spesial."; }
            else newZone();
        }
        public void key(int i) { tap(0, 0); }
        public void draw(Ui ui) {
            float ly = y + h - 40;
            for (int i = 0; i < steps.size(); i++) {
                Color c = i < results.size() ? (results.get(i) ? GREEN : RED) : (i == idx ? Ui.GOLD : Ui.CREAM);
                ui.text(a.body, (i < results.size() ? (results.get(i) ? "✓ " : "✕ ") : (i == idx ? "▶ " : "• ")) + steps.get(i), x + 40, ly - i * 34, c, 0.9f, Align.left, 0);
            }
            String[] icons = {"items/sandwich.png", "items/honey.png", "items/strawberry.png", "items/mint.png", "items/sandwich.png"};
            if (idx < steps.size()) ui.image(a.tex(icons[idx % icons.length]), x + w - 200, y + h - 200, 140, 140, 1f);
            float gx = x + 60, gw = w - 120, gy = y + 110, gh = 36;
            ui.rect(gx, gy, gw, gh, tmp.set(0.3f, 0.25f, 0.4f, 1f), 1f);
            if (!finished) ui.rect(gx + gw * (zone - zoneW / 2), gy, gw * zoneW, gh, GREEN, 0.85f);
            ui.rect(gx + gw * needle - 3, gy - 10, 6, gh + 20, Ui.WHITE, 1f);
            ui.text(a.body, finished ? "Selesai!" : (msgT > 0 ? msg : "Ketuk saat jarum di zona hijau"), x, gy + 80, Ui.CREAM, 0.95f, Align.center, w);
        }
    }

    // ============================================================ LANTERNS (lights out)
    static final class Lanterns extends Minigame {
        int n = 3; boolean[] on; int moves, totalMoves, board; float solvedT = -1;
        List<List<String>> boards = new ArrayList<>();
        protected void start() {
            if (boards.isEmpty()) {
                for (Object o : Json.list(cfg, "boards")) if (o instanceof List) { List<String> b = new ArrayList<>(); for (Object v : (List<?>) o) b.add(String.valueOf(v)); boards.add(b); }
                if (boards.isEmpty()) boards.add(Json.strList(cfg, "start"));
            }
            List<String> s = boards.get(Math.min(board, boards.size() - 1));
            n = Math.max(2, (int) Math.round(Math.sqrt(s.size())));
            on = new boolean[n * n];
            for (int i = 0; i < on.length && i < s.size(); i++) on[i] = s.get(i).startsWith("1");
        }
        float cell() { return Math.min((h - 120) / n, 120); }
        float gx() { return x + (w - cell() * n) / 2; }
        float gy() { return y + 80; }
        public void tap(float px, float py) {
            if (finished || solvedT >= 0) return;
            float c = cell();
            if (in(px, py, x + w - 190, y + 10, 170, 56)) { start(); moves = 0; audio.sfx("page"); return; }
            int cx = (int) ((px - gx()) / c), cy = (int) ((py - gy()) / c);
            if (px < gx() || py < gy() || cx < 0 || cy < 0 || cx >= n || cy >= n) return;
            toggle(cx, cy); toggle(cx - 1, cy); toggle(cx + 1, cy); toggle(cx, cy - 1); toggle(cx, cy + 1);
            moves++; audio.sfx("page");
            boolean all = true; for (boolean b : on) all &= b;
            if (all) { solvedT = 0.8f; audio.sfx("sparkle"); }
        }
        void toggle(int cx, int cy) { if (cx >= 0 && cy >= 0 && cx < n && cy < n) on[cy * n + cx] = !on[cy * n + cx]; }
        public void key(int i) { if (i >= 0 && i < 3) tap(gx() + cell() * (i + 0.5f), gy() + cell() * 1.5f); }
        public void update(float dt) {
            super.update(dt);
            if (solvedT >= 0) {
                solvedT -= dt;
                if (solvedT < 0) {
                    totalMoves += moves; board++;
                    if (board >= boards.size()) { finished = true; score = Math.max(1, 60 - totalMoves); resultText = "Semua lentera menyala dalam " + totalMoves + " langkah."; }
                    else { moves = 0; start(); }
                }
            }
        }
        public void draw(Ui ui) {
            float c = cell();
            for (int i = 0; i < n * n; i++) {
                float cx = gx() + (i % n) * c, cy = gy() + (i / n) * c;
                ui.panel(a.panelDark, cx + 6, cy + 6, c - 12, c - 12, 1f);
                Texture t = a.tex(on[i] ? "props/lantern_post.png" : "props/lantern_off.png");
                float th = c - 26, tw = th * t.getWidth() / t.getHeight();
                if (on[i]) ui.rect(cx + 14, cy + 14, c - 28, c - 28, Ui.GOLD, 0.25f + 0.1f * MathUtils.sin(t2(i)));
                ui.image(t, cx + (c - tw) / 2, cy + 13, tw, th, 1f);
            }
            ui.panel(a.button, x + w - 190, y + 10, 170, 56, 1f);
            ui.text(a.body, "Ulang", x + w - 190, y + 48, Ui.INK, 0.9f, Align.center, 170);
            ui.text(a.body, "Altar " + (board + 1) + "/" + boards.size() + "   •   Langkah: " + moves, x + 20, y + 48, Ui.CREAM, 0.9f, Align.left, 0);
        }
        float t2(int i) { return t * 3 + i; }
    }

    // ============================================================ STAR MAP
    static final class StarMap extends Minigame {
        static final String[] DIRS = {"utara", "timur", "selatan", "barat", "timur laut", "barat daya", "barat laut", "tenggara"};
        static final float[][] POS = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}, {0.72f, 0.72f}, {-0.72f, -0.72f}, {-0.72f, 0.72f}, {0.72f, -0.72f}};
        static final String[] COLS = {"ungu", "emas", "biru", "merah muda"};
        final List<String[]> stars = new ArrayList<>(); final List<String[]> order = new ArrayList<>();
        int step, mistakes; float wrongT, doneT = -1; final List<Integer> lit = new ArrayList<>();
        protected void start() {
            for (Object o : Json.list(cfg, "order")) if (o instanceof List && ((List<?>) o).size() >= 2) order.add(new String[]{String.valueOf(((List<?>) o).get(0)), String.valueOf(((List<?>) o).get(1))});
            if (order.isEmpty()) { order.add(new String[]{"timur", "ungu"}); order.add(new String[]{"utara", "emas"}); order.add(new String[]{"barat", "biru"}); }
            // setiap arah punya dua bintang berwarna berbeda: satu benar/pengecoh
            Random r = new Random(5);
            for (int d = 0; d < DIRS.length; d++) {
                String correct = null;
                for (String[] o : order) if (o[0].equals(DIRS[d])) correct = o[1];
                List<String> cols = new ArrayList<>(Arrays.asList(COLS));
                Collections.shuffle(cols, r);
                String c1 = correct != null ? correct : cols.get(0), c2 = cols.get(0).equals(c1) ? cols.get(1) : cols.get(0);
                stars.add(new String[]{DIRS[d], c1, "0"}); stars.add(new String[]{DIRS[d], c2, "1"});
            }
        }
        float[] pos(int i) {
            String[] s = stars.get(i); int d = Arrays.asList(DIRS).indexOf(s[0]);
            float cx = x + w / 2, cy = y + h / 2 + 10, R = Math.min(w, h) * 0.36f;
            float k = s[2].equals("0") ? 1f : 0.62f;
            return new float[]{cx + POS[d][0] * R * k, cy + POS[d][1] * R * k};
        }
        Color col(String c) {
            switch (c) { case "ungu": return tmp.set(0.72f, 0.55f, 1f, 1f); case "emas": return tmp.set(1f, 0.84f, 0.4f, 1f);
                case "biru": return tmp.set(0.45f, 0.7f, 1f, 1f); default: return tmp.set(1f, 0.6f, 0.75f, 1f); }
        }
        public void tap(float px, float py) {
            if (finished || doneT >= 0) return;
            for (int i = 0; i < stars.size(); i++) {
                float[] p = pos(i);
                if ((px - p[0]) * (px - p[0]) + (py - p[1]) * (py - p[1]) < 30 * 30) {
                    String[] s = stars.get(i), want = order.get(step);
                    if (s[0].equals(want[0]) && s[1].equals(want[1])) {
                        lit.add(i); step++; audio.sfx("sparkle");
                        if (step >= order.size()) doneT = 1f;
                    } else { mistakes++; step = 0; lit.clear(); wrongT = 0.8f; audio.sfx("soft_wrong"); }
                    return;
                }
            }
        }
        public void update(float dt) {
            super.update(dt);
            if (wrongT > 0) wrongT -= dt;
            if (doneT >= 0) { doneT -= dt; if (doneT < 0) { finished = true; score = Math.max(1, 3 - mistakes); resultText = "Rasi kecil terbentuk di langit desa."; } }
        }
        public void draw(Ui ui) {
            ui.rect(x, y, w, h, tmp.set(0.1f, 0.12f, 0.26f, 1f), 1f);
            float cx = x + w / 2, cy = y + h / 2 + 10, R = Math.min(w, h) * 0.36f;
            String[] lab = {"U", "T", "S", "B"};
            for (int d = 0; d < 4; d++) ui.text(a.body, lab[d], cx + POS[d][0] * (R + 34) - 20, cy + POS[d][1] * (R + 34) + 10, Ui.LAVENDER, 0.9f, Align.center, 40);
            for (int i = 0; i < lit.size() - 1; i++) {
                float[] p0 = pos(lit.get(i)), p1 = pos(lit.get(i + 1));
                for (int k = 0; k <= 20; k++) { float f = k / 20f; ui.rect(p0[0] + (p1[0] - p0[0]) * f - 2, p0[1] + (p1[1] - p0[1]) * f - 2, 4, 4, Ui.GOLD, 0.9f); }
            }
            Texture st = a.tex("ui/sparkle.png");
            for (int i = 0; i < stars.size(); i++) {
                float[] p = pos(i);
                float s = lit.contains(i) ? 44 : 30 + 4 * MathUtils.sin(t * 2 + i);
                Color c = col(stars.get(i)[1]);
                ui.rect(p[0] - s / 4, p[1] - s / 4, s / 2, s / 2, c, lit.contains(i) ? 1f : 0.8f);
                ui.image(st, p[0] - s / 2, p[1] - s / 2, s, s, 1f);
            }
            ui.text(a.body, wrongT > 0 ? "Belum tepat. Ulangi dari bintang pertama." : "Kompas: timur → utara → barat   •   Lentera: ungu → emas → biru",
                    x, y + 40, wrongT > 0 ? RED : Ui.CREAM, 0.8f, Align.center, w);
        }
    }

    // ============================================================ PAGES (urutkan kenangan)
    static final class Pages extends Minigame {
        List<String> correct; final List<String> deck = new ArrayList<>(); final List<String> placed = new ArrayList<>(); float wrongT, doneT = -1; int mistakes;
        protected void start() {
            correct = Json.strList(cfg, "pages");
            if (correct.isEmpty()) correct = Arrays.asList("Satu", "Dua", "Tiga");
            deck.addAll(correct); Collections.shuffle(deck, new Random(3));
        }
        float cw() { return (w - 60) / 3f; }
        int rows() { return (correct.size() + 2) / 3; }
        float cardY(int i) { return y + 20 + (rows() - 1 - i / 3) * 62; }
        public void tap(float px, float py) {
            if (finished || doneT >= 0) return;
            for (int i = 0; i < deck.size(); i++) {
                float bx = x + 20 + (i % 3) * (cw() + 10), by = cardY(i);
                if (in(px, py, bx, by, cw(), 54)) {
                    String p = deck.get(i);
                    if (p.equals(correct.get(placed.size()))) { placed.add(p); deck.remove(i); audio.sfx("page"); if (placed.size() == correct.size()) { doneT = 0.8f; audio.sfx("sparkle"); } }
                    else { wrongT = 0.7f; mistakes++; audio.sfx("soft_wrong"); }
                    return;
                }
            }
        }
        public void update(float dt) {
            super.update(dt);
            if (wrongT > 0) wrongT -= dt;
            if (doneT >= 0) { doneT -= dt; if (doneT < 0) { finished = true; score = Math.max(1, 6 - mistakes); resultText = "Semua halaman kembali ke tempatnya."; } }
        }
        public void draw(Ui ui) {
            float sy = y + h - 56;
            for (int i = 0; i < correct.size(); i++) {
                float sx = x + 20 + (i % 3) * (cw() + 10), syy = sy - (i / 3) * 48;
                ui.panel(a.panelDark, sx, syy, cw(), 44, 1f);
                ui.text(a.body, (i + 1) + ". " + (i < placed.size() ? placed.get(i) : "..."), sx + 14, syy + 32, i < placed.size() ? Ui.GOLD : Ui.LAVENDER, 0.72f, Align.left, cw() - 20);
            }
            float off = wrongT > 0 ? MathUtils.sin(wrongT * 50) * 6 : 0;
            for (int i = 0; i < deck.size(); i++) {
                float bx = x + 20 + (i % 3) * (cw() + 10) + off, by = cardY(i);
                ui.panel(a.button, bx, by, cw(), 54, 1f);
                ui.text(a.body, deck.get(i), bx + 8, by + 38, Ui.INK, 0.74f, Align.center, cw() - 16);
            }
            ui.text(a.body, "Pilih halaman berikutnya sesuai urutan kenangan", x, y + 30 + rows() * 62 + 34, Ui.CREAM, 0.85f, Align.center, w);
        }
    }

    // ============================================================ CLAW
    static final class Claw extends Minigame {
        float clawX = 0.1f, dir = 1, drop = -1, plushX; boolean won; final Random rng = new Random();
        protected void start() { plushX = 0.2f + rng.nextFloat() * 0.6f; }
        public void update(float dt) {
            super.update(dt);
            if (finished) return;
            if (drop < 0) { clawX += dir * dt * 0.55f; if (clawX > 0.95f) { clawX = 0.95f; dir = -1; } if (clawX < 0.05f) { clawX = 0.05f; dir = 1; } }
            else { drop += dt; if (drop > 1.3f) { finished = true; score = won ? 1 : 0; resultText = won ? "Dapat boneka!" : "Bonekanya lepas... coba lagi lain kali."; } }
        }
        public void tap(float px, float py) {
            if (drop >= 0 || finished) return;
            drop = 0; won = Math.abs(clawX - plushX) < 0.06f; audio.sfx(won ? "sparkle" : "page");
        }
        public void key(int i) { tap(0, 0); }
        public void draw(Ui ui) {
            float bx = x + 60, bw = w - 120, top = y + h - 30, floor = y + 70;
            ui.rect(bx, floor, bw, top - floor, tmp.set(0.8f, 0.92f, 0.98f, 1f), 0.35f);
            float cxp = bx + bw * clawX, depth = drop < 0 ? 0 : Math.min(1f, drop / 0.6f) * (top - floor - 70);
            if (drop > 0.6f && won) depth = (top - floor - 70) * Math.max(0f, 1f - (drop - 0.6f) / 0.7f);
            ui.rect(cxp - 2, top - 20 - depth, 4, 20 + depth, Ui.INK, 1f);
            ui.rect(cxp - 18, top - 34 - depth, 36, 14, Ui.LAVENDER, 1f);
            float pyy = (won && drop > 0.6f) ? top - 34 - depth - 44 : floor;
            ui.image(a.tex("items/cat_plush.png"), bx + bw * plushX - 28, pyy, 56, 56, 1f);
            ui.text(a.body, drop < 0 ? "Ketuk saat capit tepat di atas boneka" : (won ? "Kena!" : "..."), x, y + 50, Ui.CREAM, 0.9f, Align.center, w);
        }
    }

    // ============================================================ FISHING
    static final class Fishing extends Minigame {
        static final String[] NAMES = {"Ikan Mas", "Nila", "Mujair", "Lele", "Gurami", "Koi Danau", "Ikan Pelangi", "Ikan Bintang"};
        static final float[] WEIGHT = {22, 20, 18, 14, 11, 8, 5, 2};
        int phase; float wait, bite, fish = 0.5f, fdir = 1, fspeed, hookW = 0.18f; int species; final Random rng = new Random();
        protected void start() {
            float r = rng.nextFloat() * 100, acc = 0;
            for (int i = 0; i < NAMES.length; i++) { acc += WEIGHT[i]; if (r <= acc) { species = i; break; } }
            fspeed = 0.45f + species * 0.12f; hookW = Math.max(0.1f, 0.22f - species * 0.015f);
            wait = 1.2f + rng.nextFloat() * 2.2f;
        }
        public void update(float dt) {
            super.update(dt);
            if (finished) return;
            if (phase == 0) { wait -= dt; if (wait <= 0) { phase = 1; bite = 0.9f; audio.sfx("page"); } }
            else if (phase == 1) { bite -= dt; if (bite <= 0) { phase = 0; wait = 1f + rng.nextFloat() * 2f; } }
            else if (phase == 2) {
                fish += fdir * fspeed * dt * (1f + 0.4f * MathUtils.sin(t * 3f));
                if (fish > 0.97f) { fish = 0.97f; fdir = -1; } if (fish < 0.03f) { fish = 0.03f; fdir = 1; }
                if (rng.nextFloat() < dt * 0.8f) fdir = -fdir;
            }
        }
        public void tap(float px, float py) {
            if (finished) return;
            if (phase == 0) { audio.sfx("soft_wrong"); wait += 0.6f; return; }
            if (phase == 1) { phase = 2; return; }
            boolean ok = Math.abs(fish - 0.5f) < hookW / 2;
            finished = true; score = ok ? species + 1 : 0;
            audio.sfx(ok ? "sparkle" : "soft_wrong");
            resultText = ok ? "Dapat " + NAMES[species] + "!" + (species >= 6 ? " Langka sekali!" : "") : "Ikannya lepas. Sabar, coba lagi.";
        }
        public void key(int i) { tap(0, 0); }
        public void draw(Ui ui) {
            ui.rect(x, y, w, h * 0.55f, tmp.set(0.35f, 0.6f, 0.78f, 1f), 1f);
            for (int i = 0; i < 18; i++) { float wx = x + ((i * 0.37f + t * 0.03f) % 1f) * w; ui.rect(wx, y + 30 + (i * 41) % (int) (h * 0.5f), 18, 2, Ui.WHITE, 0.4f); }
            float bx = x + w / 2, by = y + h * 0.42f + (phase == 1 ? MathUtils.sin(t * 30) * 6 : MathUtils.sin(t * 2) * 3);
            ui.rect(bx - 1, by + 16, 2, h * 0.55f - (by - y) + 40, Ui.INK, 0.8f);
            ui.rect(bx - 8, by, 16, 16, RED, 1f); ui.rect(bx - 8, by + 8, 16, 8, Ui.WHITE, 1f);
            if (phase == 2) {
                float gx = x + 60, gw = w - 120, gy = y + h * 0.62f, gh = 34;
                ui.rect(gx, gy, gw, gh, tmp.set(0.3f, 0.25f, 0.4f, 1f), 1f);
                ui.rect(gx + gw * (0.5f - hookW / 2), gy, gw * hookW, gh, GREEN, 0.85f);
                ui.rect(gx + gw * fish - 14, gy + 6, 28, gh - 12, Ui.GOLD, 1f);
            }
            String msg = phase == 0 ? "Tunggu pelampungnya bergerak..." : phase == 1 ? "Ada yang menarik! KETUK sekarang!" : "Ketuk saat ikan (kuning) di zona hijau!";
            ui.text(a.body, msg, x, y + h - 20, phase == 1 ? Ui.GOLD : Ui.CREAM, 1f, Align.center, w);
        }
    }

    // ============================================================ HUJAN BINTANG (tangkap bintang jatuh)
    static final class StarCatch extends Minigame {
        static final class Star { float x, y, v; boolean gold; }
        final List<Star> stars = new ArrayList<>(); final Random rng = new Random();
        float basket = 0.5f, target = 0.5f, spawn, time = 20f; int caught, missed;
        protected void start() { time = (float) Json.num(cfg, "seconds", 20); }
        public void update(float dt) {
            super.update(dt);
            if (finished) return;
            time -= dt;
            if (time <= 0) {
                finished = true; score = caught;
                resultText = caught >= 25 ? "Hujan bintang milikmu! " + caught + " bintang." : caught >= 15 ? "Tangkapan bagus: " + caught + " bintang." : caught + " bintang tertangkap. Lumayan!";
                return;
            }
            float d = target - basket; basket += Math.signum(d) * Math.min(Math.abs(d), dt * 1.6f);
            spawn -= dt;
            if (spawn <= 0) {
                Star s = new Star(); s.x = 0.05f + rng.nextFloat() * 0.9f; s.y = 1f; s.v = 0.32f + rng.nextFloat() * 0.25f + (20f - time) * 0.012f;
                s.gold = rng.nextFloat() < 0.12f; stars.add(s); spawn = 0.45f + rng.nextFloat() * 0.35f;
            }
            for (int i = stars.size() - 1; i >= 0; i--) {
                Star s = stars.get(i); s.y -= s.v * dt;
                if (s.y < 0.1f && s.y > 0.02f && Math.abs(s.x - basket) < 0.08f) { caught += s.gold ? 3 : 1; audio.sfx(s.gold ? "sparkle" : "page"); stars.remove(i); }
                else if (s.y < 0) { missed++; stars.remove(i); }
            }
        }
        public void tap(float px, float py) { if (w > 0) target = MathUtils.clamp((px - x - 40) / (w - 80), 0.04f, 0.96f); }
        public void key(int i) { target = MathUtils.clamp(i == 0 ? basket - 0.25f : i == 2 ? basket + 0.25f : basket, 0.04f, 0.96f); }
        public void draw(Ui ui) {
            float bx = x + 40, bw = w - 80, by = y + 30, bh = h - 70;
            ui.rect(bx, by, bw, bh, tmp.set(0.12f, 0.14f, 0.32f, 1f), 1f);
            for (int i = 0; i < 26; i++) ui.rect(bx + ((i * 0.618f) % 1f) * bw, by + ((i * 0.377f + 0.2f) % 1f) * bh, 2, 2, Ui.WHITE, 0.25f + 0.25f * MathUtils.sin(t * 2 + i));
            Texture st = a.tex("props/spark.png");
            for (Star s : stars) { float sz = s.gold ? 38 : 28; ui.image(st, bx + bw * s.x - sz / 2, by + bh * s.y - sz / 2, sz, sz, 1f); if (s.gold) ui.rect(bx + bw * s.x - 3, by + bh * s.y - 3, 6, 6, Ui.GOLD, 1f); }
            float cx = bx + bw * basket;
            ui.rect(cx - bw * 0.08f, by + 6, bw * 0.16f, 22, Ui.LAVENDER, 1f); ui.rect(cx - bw * 0.08f, by + 24, bw * 0.16f, 5, Ui.GOLD, 1f);
            ui.text(a.body, "Bintang: " + caught + "   Waktu: " + (int) Math.ceil(Math.max(0, time)), x, y + h - 6, Ui.CREAM, 0.95f, Align.center, w);
            ui.text(a.body, "Ketuk kiri/kanan layar untuk menggeser keranjang (tombol 1 / 3)", x, y + 22, Ui.LAVENDER, 0.7f, Align.center, w);
        }
    }

    // ============================================================ LEMPAR GELANG
    static final class RingToss extends Minigame {
        int throwsLeft = 5, hits, bottle; float power, dir = 1, anim = -1; boolean lastHit; final Random rng = new Random();
        final float[] zone = {0.25f, 0.5f, 0.75f};
        protected void start() { throwsLeft = (int) Json.num(cfg, "throws", 5); bottle = rng.nextInt(3); }
        public void update(float dt) {
            super.update(dt);
            if (finished) return;
            if (anim >= 0) {
                anim += dt;
                if (anim > 0.9f) {
                    anim = -1; if (throwsLeft <= 0) { finished = true; score = hits; resultText = hits >= 4 ? "Jago! " + hits + " gelang masuk." : hits >= 2 ? hits + " gelang masuk. Dapat hadiah!" : hits + " gelang masuk. Masih dapat hadiah hiburan!"; }
                    else bottle = rng.nextInt(3);
                }
                return;
            }
            power += dir * dt * (0.8f + (5 - throwsLeft) * 0.1f);
            if (power > 1) { power = 1; dir = -1; } else if (power < 0) { power = 0; dir = 1; }
        }
        public void tap(float px, float py) {
            if (finished || anim >= 0 || throwsLeft <= 0) return;
            lastHit = Math.abs(power - zone[bottle]) < 0.07f; if (lastHit) hits++;
            throwsLeft--; anim = 0; audio.sfx(lastHit ? "sparkle" : "soft_wrong");
        }
        public void key(int i) { tap(0, 0); }
        public void draw(Ui ui) {
            float bx = x + 60, bw = w - 120, gy = y + 70;
            for (int i = 0; i < 3; i++) {
                float cx = bx + bw * zone[i];
                ui.rect(cx - 14, gy + 70, 28, 90, i == bottle ? tmp.set(0.55f, 0.85f, 0.7f, 1f) : tmp.set(0.5f, 0.6f, 0.7f, 1f), i == bottle ? 1f : 0.5f);
                ui.rect(cx - 6, gy + 160, 12, 26, i == bottle ? GREEN : Ui.LAVENDER, 0.8f);
            }
            ui.rect(bx, gy, bw, 30, tmp.set(0.3f, 0.25f, 0.4f, 1f), 1f);
            ui.rect(bx + bw * (zone[bottle] - 0.07f), gy, bw * 0.14f, 30, GREEN, 0.8f);
            ui.rect(bx + bw * power - 4, gy - 6, 8, 42, Ui.GOLD, 1f);
            if (anim >= 0) ui.text(a.title, lastHit ? "Masuk!" : "Meleset!", x, y + h - 60, lastHit ? Ui.GOLD : Ui.CREAM, 0.5f, Align.center, w);
            ui.text(a.body, "Gelang: " + throwsLeft + "   Masuk: " + hits + "   (ketuk saat garis emas di zona hijau)", x, y + h - 8, Ui.CREAM, 0.85f, Align.center, w);
        }
    }

    // ============================================================ TUANG TEH
    static final class Pour extends Minigame {
        int cups = 3, cup; float fill, speed, line; boolean pouring = true; float pause = -1; int total;
        final List<Integer> marks = new ArrayList<>(); final Random rng = new Random();
        protected void start() { cups = (int) Json.num(cfg, "cups", 3); next(); }
        void next() { fill = 0; line = 0.6f + rng.nextFloat() * 0.25f; speed = 0.35f + cup * 0.12f; pouring = true; }
        public void update(float dt) {
            super.update(dt);
            if (finished) return;
            if (pause >= 0) { pause += dt; if (pause > 0.8f) { pause = -1; cup++; if (cup >= cups) { finished = true; score = total; resultText = total >= cups * 3 - 1 ? "Tuangan sempurna, seperti barista!" : total >= cups * 2 ? "Tehnya pas dan hangat." : "Agak tumpah sedikit, tapi tetap enak."; } else next(); } return; }
            if (pouring) { fill += dt * speed; if (fill >= 1f) { fill = 1f; stop(); } }
        }
        void stop() {
            pouring = false; float d = Math.abs(fill - line); int q = d < 0.03f ? 3 : d < 0.08f ? 2 : 1;
            marks.add(q); total += q; pause = 0; audio.sfx(q == 3 ? "sparkle" : "page");
        }
        public void tap(float px, float py) { if (!finished && pouring && pause < 0) stop(); }
        public void key(int i) { tap(0, 0); }
        public void draw(Ui ui) {
            float cw = 140, ch = 200, cx = x + (w - cw) / 2, cy = y + 50;
            ui.rect(cx - 8, cy - 8, cw + 16, ch + 16, Ui.CREAM, 0.9f);
            ui.rect(cx, cy, cw, ch, tmp.set(0.95f, 0.95f, 0.98f, 1f), 1f);
            ui.rect(cx, cy, cw, ch * fill, tmp.set(0.78f, 0.5f, 0.25f, 1f), 1f);
            ui.rect(cx - 16, cy + ch * line - 2, cw + 32, 4, RED, 1f);
            if (pouring) ui.rect(cx + cw / 2 - 4, cy + ch * fill, 8, ch * (1f - fill) + 40, tmp.set(0.78f, 0.5f, 0.25f, 1f), 0.9f);
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < cups; i++) sb.append(i < marks.size() ? (marks.get(i) == 3 ? "★★★ " : marks.get(i) == 2 ? "★★ " : "★ ") : "○ ");
            ui.text(a.body, "Gelas " + Math.min(cups, cup + 1) + "/" + cups + "   " + sb, x, y + h - 8, Ui.GOLD, 0.9f, Align.center, w);
            ui.text(a.body, "Ketuk untuk berhenti menuang tepat di garis merah", x, y + 24, Ui.CREAM, 0.8f, Align.center, w);
        }
    }

    // ============================================================ PETI KATA SANDI (kunci simbol)
    static final class CodeLock extends Minigame {
        static final String[] ICONS = {"items/symbol_flower.png", "items/symbol_book.png", "items/symbol_star.png", "items/symbol_moon.png"};
        static final String[] NAMES = {"Bunga", "Buku", "Bintang", "Bulan"};
        int[] dial, answer; int tries; float shake = 0, okT = -1; String msg = "";
        protected void start() {
            List<Object> ans = Json.list(cfg, "answer");
            answer = new int[ans.size()];
            for (int i = 0; i < answer.length; i++) answer[i] = ((Number) ans.get(i)).intValue();
            dial = new int[answer.length];
        }
        float dialX(int i) { float dw = 130, gap = 26, tot = dial.length * dw + (dial.length - 1) * gap; return x + (w - tot) / 2 + i * (dw + gap); }
        public void update(float dt) {
            super.update(dt);
            if (shake > 0) shake -= dt;
            if (okT >= 0) { okT += dt; if (okT > 1.1f) { finished = true; score = 1; resultText = "Klik! Peti terbuka."; } }
        }
        public void tap(float px, float py) {
            if (finished || okT >= 0) return;
            float dy = y + h * 0.42f;
            for (int i = 0; i < dial.length; i++)
                if (in(px, py, dialX(i), dy, 130, 150)) { dial[i] = (dial[i] + 1) % ICONS.length; audio.sfx("page"); return; }
            if (in(px, py, x + w / 2 - 110, y + 40, 220, 70)) check();
        }
        public void key(int i) { if (i >= 0 && i < dial.length) { dial[i] = (dial[i] + 1) % ICONS.length; audio.sfx("page"); } else check(); }
        void check() {
            boolean ok = true;
            for (int i = 0; i < dial.length; i++) ok &= dial[i] == answer[i];
            if (ok) { okT = 0; audio.sfx("sparkle"); msg = "Benar!"; }
            else { tries++; shake = 0.4f; audio.sfx("soft_wrong"); msg = tries >= 3 ? "Belum tepat. Petunjuknya terukir di batu-batu sekitar sini." : "Belum tepat."; }
        }
        public void draw(Ui ui) {
            float dy = y + h * 0.42f, off = shake > 0 ? MathUtils.sin(shake * 60) * 6 : 0;
            ui.text(a.body, Json.str(cfg, "hint", "Putar simbol, lalu tekan Buka."), x, y + h - 20, Ui.LAVENDER, 0.8f, Align.center, w);
            for (int i = 0; i < dial.length; i++) {
                float dx = dialX(i) + off;
                ui.rect(dx, dy, 130, 150, okT >= 0 ? GREEN : tmp.set(0.32f, 0.26f, 0.44f, 1f), 1f);
                ui.rect(dx + 6, dy + 6, 118, 138, tmp.set(0.96f, 0.92f, 0.86f, 1f), 1f);
                ui.image(a.tex(ICONS[dial[i]]), dx + 33, dy + 46, 64, 64, 1f);
                ui.text(a.body, NAMES[dial[i]], dx, dy + 36, Ui.INK, 0.75f, Align.center, 130);
                ui.text(a.label, "▲ ketuk", dx, dy + 172, Ui.CREAM, 0.7f, Align.center, 130);
            }
            ui.rect(x + w / 2 - 110, y + 40, 220, 70, Ui.PINK, 1f);
            ui.text(a.body, "Buka", x + w / 2 - 110, y + 88, Ui.CREAM, 1f, Align.center, 220);
            if (msg.length() > 0) ui.text(a.body, msg, x, y + 150, okT >= 0 ? Ui.GOLD : Ui.CREAM, 0.85f, Align.center, w);
        }
    }


    // ============================================================ v4.9 MEMORY ECHO — gameplay asli, dua pola route.
    /**
     * 3 tahap mendengarkan urutan empat simbol. Preview tampil bergantian,
     * kemudian pemain mengulang. Jawaban salah mengulang tahap berjalan,
     * bukan memblokir cerita; ketuk layar atau angka 1-4 di keyboard.
     */
    static final class MemoryEchoV49 extends Minigame {
        private static final String[] SYMBOLS = {"Bunga", "Buku", "Bintang", "Bulan"};
        private static final String[] ICONS = {
                "items/symbol_flower.png", "items/symbol_book.png",
                "items/symbol_star.png", "items/symbol_moon.png"
        };
        private int[][] patterns;
        private int stage, index, errors;
        private float previewTime;
        private boolean preview;
        private String feedback = "";

        @Override protected void start() {
            patterns = EchoPatternV49.fromConfig(cfg, route);
            stage = 0; index = 0; errors = 0;
            beginPreview();
        }
        private void beginPreview() {
            preview = true; previewTime = 0f; index = 0;
            feedback = "Amati cahaya yang menyala, lalu ulangi urutannya.";
        }
        @Override public void update(float dt) {
            super.update(dt);
            if (preview) {
                previewTime += Math.max(0f, Math.min(dt, .10f));
                if (previewTime >= patterns[stage].length * .8f + .7f) {
                    preview = false;
                    feedback = "Giliranmu: pilih simbol sesuai urutan.";
                }
            }
        }
        private int litIndex() {
            if (!preview || previewTime < .3f) return -1;
            float t = previewTime - .3f;
            int n = (int)(t / .8f);
            if (n < 0 || n >= patterns[stage].length || (t % .8f) > .56f) return -1;
            return patterns[stage][n];
        }
        private float btnX(int n) {
            float size = Math.min(138f, (w - 90f) / 4f);
            float gap = Math.min(26f, (w - size * 4f) / 5f);
            return x + (w - 4f * size - 3f * gap) / 2f + n * (size + gap);
        }
        private float btnSize() { return Math.min(138f, (w - 90f) / 4f); }
        private void choose(int button) {
            if (finished || preview || button < 0 || button > 3) return;
            if (!EchoPatternV49.matches(patterns, stage, index, button)) {
                errors++;
                audio.sfx("soft_wrong", .6f);
                feedback = "Belum tepat. Coba dengarkan urutannya lagi.";
                beginPreview();
                return;
            }
            audio.sfx("page", .5f);
            index++;
            if (index == patterns[stage].length) {
                stage++;
                if (stage >= patterns.length) {
                    finished = true;
                    score = Math.max(1, 5 - errors);
                    resultText = errors == 0 ? "Semua gema selaras! Kenangan baru terbuka."
                            : "Gema tersambung! Kalian menemukan ritme kenangan.";
                    audio.sfx("sparkle", .7f);
                } else beginPreview();
            } else feedback = "Bagus! " + index + "/" + patterns[stage].length + " nada.";
        }
        @Override public void tap(float px, float py) {
            float size = btnSize(), by = y + h * .36f;
            for (int i=0;i<4;i++) if (in(px,py,btnX(i),by,size,size+15)) {
                choose(i); return;
            }
        }
        @Override public void key(int button) { choose(button); }
        @Override public void draw(Ui ui) {
            ui.text(a.body, "TAHAP " + (stage + 1) + "/" + patterns.length
                    + (preview ? "  •  DENGARKAN" : "  •  ULANGI"),
                    x, y + h - 28, Ui.GOLD, .95f, Align.center, w);
            ui.text(a.body, feedback, x, y + h - 85, Ui.CREAM, .78f, Align.center, w);
            float size=btnSize(), by=y+h*.36f;
            int lit=litIndex();
            for(int i=0;i<4;i++) {
                float bx=btnX(i);
                ui.rect(bx,by,size,size+15,
                        lit == i ? Ui.GOLD : tmp.set(.34f,.28f,.45f,1f), 1f);
                ui.rect(bx+5,by+5,size-10,size+5,tmp.set(.95f,.92f,.90f,1f),1f);
                ui.image(a.tex(ICONS[i]), bx+(size-66)/2f,by+38,66,66,1f);
                ui.text(a.body, (i+1)+". "+SYMBOLS[i],bx,by+23,Ui.INK,.65f,Align.center,size);
            }
            ui.text(a.body, preview
                    ? "Perhatikan setiap cahaya. Tunggu sampai giliranmu."
                    : "Ketuk simbol atau gunakan tombol 1–4.",
                    x,y+75,Ui.LAVENDER,.72f,Align.center,w);
            if(errors>0) ui.text(a.body,"Mengulang: "+errors,x,y+37,Ui.GOLD,.65f,Align.center,w);
        }
    }
}
