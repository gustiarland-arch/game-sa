import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.game.DialogueHistoryOverlay;
import com.arlandsofia.olu.logic.DialogueHistory;
import com.arlandsofia.olu.ui.Ui;

public final class DialogueHistoryOverlaySmoke {
    private static int checks;
    private static void ok(boolean x) { checks++; if (!x) throw new AssertionError("UI test " + checks); }
    public static void main(String[] args) {
        DialogueHistory h = new DialogueHistory();
        DialogueHistoryOverlay ui = new DialogueHistoryOverlay(new Assets());
        ui.open(h);
        ok(ui.active());
        ui.draw(new Ui(), 1280, 720);
        ok(ui.active());
        for (int i = 0; i < 16; i++) h.add("Sofia", "senang", "Line " + i, "plaza", 1);
        ui.open(h); ui.draw(new Ui(), 1280, 720);
        ui.pageOlder(); ui.pageOlder();
        ui.draw(new Ui(), 1280, 720);
        ui.pageNewer();
        ui.draw(new Ui(), 1280, 720);
        // Mainkan tombol Tutup pada footer (viewport 1280x720, w-660 centered).
        float cx = (1280 - 660) / 2f + 451 + 50;
        float cy = 720 * .10f + 10 + 23;
        ok(ui.down(cx, cy, 1)); ok(ui.up(cx, cy, 1));
        ok(!ui.active());
        ui.open(h); ui.cancel(2); ui.close(); ok(!ui.active());
        System.out.println("DIALOGUE HISTORY OVERLAY SMOKE: " + checks + " assertions OK");
    }
}
