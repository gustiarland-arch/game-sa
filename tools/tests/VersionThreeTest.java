import com.arlandsofia.olu.logic.*;
import java.util.*;

/** Regresi baru v3.0: riwayat dialog, migrasi lama, keamanan data dan kompas. */
public final class VersionThreeTest {
    static int checks;
    static void ok(boolean b, String message) { checks++; if (!b) throw new AssertionError(message); }
    public static void main(String[] args) {
        DialogueHistory history = new DialogueHistory();
        history.add("Arland", "malu", "  Satu kalimat\nlagu  ", "plaza", 2);
        ok(history.size() == 1, "dialog masuk");
        ok(history.get(0).text.equals("Satu kalimat lagu"), "line breaks disanitasi");
        history.add("", "", "", "", 1);
        ok(history.size() == 1, "dialog kosong diabaikan");
        for (int i = 0; i < 100; i++) history.add("Sofia", "senang", "Baris-" + i, "taman", i + 1);
        ok(history.size() == DialogueHistory.LIMIT, "batas riwayat 72");
        ok(history.get(0).text.equals("Baris-28"), "entry tertua dibuang");
        ok(history.get(history.size() - 1).text.equals("Baris-99"), "entry terbaru di ujung");
        DialogueHistory restored = new DialogueHistory();
        restored.restore(history.toList());
        ok(restored.size() == history.size(), "jurnal restore");
        ok(restored.get(0).text.equals(history.get(0).text), "order restore");
        DialogueHistory veryLong = new DialogueHistory();
        char[] chars = new char[5000]; Arrays.fill(chars, 'x');
        veryLong.add("N", "e", new String(chars), "area", -1);
        ok(veryLong.get(0).text.length() == DialogueHistory.TEXT_LIMIT, "anti oversized entry");
        ok(veryLong.get(0).day == 1, "hari invalid dirapikan");
        Map<String, Object> corrupted = new LinkedHashMap<>();
        corrupted.put("speaker", "N"); corrupted.put("emotion", "ok");
        corrupted.put("text", "halo"); corrupted.put("area", "p"); corrupted.put("day", 1);
        List<Object> attack = new ArrayList<>(); attack.add(9); attack.add(corrupted);
        restored.restore(attack);
        ok(restored.size() == 1 && restored.get(0).text.equals("halo"), "salah tipe diskip");

        Progress p = new Progress();
        p.route = "arland"; p.slot = 1; p.step = "PRO_001"; p.area = "plaza";
        p.dialogueHistory.add("Sofia", "senang", "Halo, Arland!", "plaza", 3);
        Progress copy = Progress.fromMap(p.toMap(true));
        ok(copy.dialogueHistory.size() == 1, "schema7 menyimpan riwayat");
        ok(copy.dialogueHistory.get(0).text.equals("Halo, Arland!"), "riwayat schema7 identik");
        Map<String, Object> previous = p.toMap(true);
        previous.put("schema", 6); previous.remove("dialogueHistory");
        Progress old = Progress.fromMap(previous);
        ok(old.dialogueHistory.size() == 0 && old.step.equals(p.step), "migrasi schema6 tetap aman");
        boolean futureBlocked = false;
        try { Map<String, Object> future = p.toMap(true); future.put("schema", Progress.SCHEMA + 1); Progress.fromMap(future); }
        catch (IllegalArgumentException expected) { futureBlocked = true; }
        ok(futureBlocked, "save masa depan ditolak");
        ok("Utara-Timur".equals(QuestCompass.direction(100, -50)), "kompas timur laut");
        ok("Selatan-Barat".equals(QuestCompass.direction(-50, 100)), "kompas barat daya");
        ok("dekat".equals(QuestCompass.direction(3, 4)), "kompas jarak dekat");
        ok(QuestCompass.nearest(1, 1, Collections.<QuestDb.Interactable>emptyList(), "arland") == null, "kompas tanpa quest aman");
        System.out.println("VERSION 3.0: " + checks + " Java assertions OK");
    }
}
