import com.arlandsofia.olu.OluGame;
import com.arlandsofia.olu.ui.SettingsPanel;
import com.arlandsofia.olu.ui.Ui;
import com.arlandsofia.olu.ui.UiButton;
import com.arlandsofia.olu.logic.Settings;
import java.util.Map;

public final class SettingsPanelSmoke {
    static int checks;
    static void check(boolean ok,String msg){checks++;if(!ok)throw new AssertionError(msg);}
    static void click(UiButton b){check(b.visible&&b.down(b.x+b.w/2,b.y+b.h/2,2),"down "+b.label);check(b.up(b.x+b.w/2,b.y+b.h/2,2),"up "+b.label);}
    public static void main(String[] args){
        OluGame game=new OluGame();SettingsPanel panel=new SettingsPanel(game,()->{});
        Ui ui=new Ui();
        check(panel.buttons.size()==34,"15 pairs + three tabs + done");
        for(int page=0;page<3;page++){
            if(page>0){click(panel.buttons.get(30+page));}
            panel.draw(ui,1280,720);
            int count=0;
            for(int row=0;row<15;row++){
                UiButton minus=panel.buttons.get(row*2),plus=panel.buttons.get(row*2+1);
                check(minus.visible==plus.visible,"pair symmetry");
                if(!minus.visible)continue;
                count++;
                check(minus.y>=0&&minus.y+minus.h<=720,"row in bounds "+row);
                check(plus.y>=0&&plus.y+plus.h<=720,"plus in bounds "+row);
                check(minus.w>=48&&minus.h>=44,"touch target size "+row);
            }
            check(count<=5,"maximum five visible settings rows");
            for(int j=0;j<3;j++)check(panel.buttons.get(30+j).visible,"tab visible");
        }
        // Audio: ambiance independent from music, footsteps toggle.
        click(panel.buttons.get(30));panel.draw(ui,1280,720);
        float before=game.settings.ambience;click(panel.buttons.get(2*2+1));check(game.settings.ambience>before,"ambience volume");
        boolean steps=game.settings.footsteps;click(panel.buttons.get(5*2));check(game.settings.footsteps!=steps,"footsteps toggle");
        // Controls: handedness, floating/fixed and sensitivity.
        click(panel.buttons.get(32));panel.draw(ui,1280,720);
        click(panel.buttons.get(11*2+1));check(game.settings.leftHanded,"left handed toggle");
        click(panel.buttons.get(12*2+1));check(!game.settings.floatingJoystick,"fixed stick toggle");
        float sense=game.settings.joystickSensitivity;click(panel.buttons.get(13*2+1));check(game.settings.joystickSensitivity>sense,"sensitivity");
        click(panel.buttons.get(31));panel.draw(ui,1280,720);
        int oldDistance=game.settings.cameraDistance;
        click(panel.buttons.get(14*2+1));
        check(game.settings.cameraDistance>oldDistance,"camera distance option works");
        Map<String,Object> saved=game.settings.toMap();
        Settings restored=Settings.fromMap(saved);
        check(restored.leftHanded&&!restored.floatingJoystick,"settings roundtrip handedness");
        check(restored.cameraDistance==2,"camera distance preserved");
        check(Math.abs(restored.joystickSensitivity-game.settings.joystickSensitivity)<.01f,"settings roundtrip sensitivity");
        Settings legacy=Settings.fromMap(new java.util.LinkedHashMap<String,Object>());
        check(!legacy.leftHanded&&legacy.floatingJoystick&&legacy.joystickSensitivity==1f,"old settings fallback");
        click(panel.buttons.get(33));check(game.saves==1,"save settings");
        System.out.println("ANDROID SETTINGS UI OK: "+checks+" layout/input/compat checks");
    }
}
