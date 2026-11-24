#!/usr/bin/env bash
# Verifikasi parsabilitas Java + integrasi WorldFx terhadap stub API headless.
# Tidak membuktikan rendering OpenGL, performa HP, ataupun build APK.
set -euo pipefail
cd "$(dirname "$0")/.."
DIR=$(mktemp -d)
trap 'rm -rf "$DIR"' EXIT
javac --release 11 -d "$DIR" tools/JavaSyntaxCheck.java
java -cp "$DIR" JavaSyntaxCheck core/src/main/java core/src/test/java android/src/main/java
javac --release 11 -d "$DIR" \
  $(find tools/stubs/logic -name '*.java' | sort) \
  core/src/main/java/com/arlandsofia/olu/logic/{WorldClock,WorldAtmosphereV462}.java \
  core/src/main/java/com/arlandsofia/olu/game/WorldFx.java
cat > "$DIR/VisualFxSmoke.java" <<'JAVA'
import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.game.WorldFx;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
public class VisualFxSmoke {
  public static void main(String[] args) {
    WorldFx fx = new WorldFx(new Assets());
    SpriteBatch batch = new SpriteBatch();
    for(int quality=0;quality<=2;quality++) {
      fx.reset();
      for(int frame=0;frame<90;frame++) {
        fx.update(1f/60f, 100f + frame, 400f, true, frame%2==0, frame%3==0,
             false, 108f, 405f, true, 100, quality);
        fx.draw(batch, quality);
        fx.drawForeground(batch, 0f, 0f, 640f, 360f, "petals", frame/60f, quality);
        fx.drawRipples(batch, 230f, 105f, 40f, 25f, frame/60f, quality, frame%3==0);
        fx.drawVignette(batch, 0f, 0f, 640f, 360f, quality);
        fx.drawWorldBackdropV462(batch,"hutan_bisik",false,frame%2==0,7*60,
            320f,400f,640f,360f,frame/60f,quality);
        fx.drawWorldForegroundV462(batch,"taman_kota",false,frame%2==0,true,19*60,
            320f,400f,640f,360f,frame/60f,quality);
        fx.drawWaterGlintsV462(batch,230f,105f,40f,25f,frame/60f,quality,frame%3==0);
        com.badlogic.gdx.graphics.Texture px = new com.badlogic.gdx.graphics.Texture();
        fx.drawFlowV54(batch, px, 0f, 0f, 1920f, 346f, 1f, 14f, frame/60f, quality, frame%2==0, 300f, 0f, 640f, 360f);
        fx.drawRiverV54(batch, px, new float[]{58f, 46f, 1896f, 112f, 1885f, 240f, 1880f, 360f}, 1920f, frame/60f, quality, true, 1600f, 1500f, 640f, 360f);
        fx.drawPropWaterV54(batch, px, "props/v43_v41_fountain_fountain.png", 845f, 650f, frame/60f, quality);
        fx.drawPropWaterV54(batch, px, "props/v41_waterfall_hb_waterfall.png", 1862f, 1920f, frame/60f, quality);
        java.util.List<float[]> pd = new java.util.ArrayList<>(); pd.add(new float[]{320f, 300f, quality});
        fx.drawPuddlesV54(batch, pd, 1280f, 1f, frame%2==0, frame/60f, quality, frame%5==0 ? .2f : 0f, 0f, 0f, 640f, 1280f);
        fx.drawLightningV54(batch, px, 0f, 0f, 640f, 360f, .2f);
        fx.splashAt(100f, 100f, quality);
        fx.drawSceneAtmosphere(batch, new com.badlogic.gdx.graphics.Texture(), new com.badlogic.gdx.graphics.Texture(),
            new com.badlogic.gdx.graphics.Texture(), "plaza", false, 1408f, 320f, 400f, 640f, 360f,
            frame/60f, quality, frame%2==0);
        fx.drawSceneAtmosphere(batch, new com.badlogic.gdx.graphics.Texture(), new com.badlogic.gdx.graphics.Texture(),
            new com.badlogic.gdx.graphics.Texture(), "gua_kristal", false, 960f, 320f, 400f, 640f, 360f,
            frame/60f, quality, true);
      }
    }
    System.out.println("WorldFx headless smoke OK: tiga preset, pool partikel & render methods");
  }
}
JAVA
javac --release 11 -cp "$DIR" -d "$DIR" "$DIR/VisualFxSmoke.java"
java -cp "$DIR" VisualFxSmoke
