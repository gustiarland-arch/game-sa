#!/usr/bin/env bash
# Deterministic headless checks. This is NOT a replacement for a real Android APK build.
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
mkdir -p "$T/src/com/arlandsofia/olu/game" "$T/src/com/arlandsofia/olu" "$T/src/com/arlandsofia/olu/ui" \
         "$T/src/com/badlogic/gdx/graphics/g2d" "$T/src/com/badlogic/gdx/graphics" "$T/src/com/badlogic/gdx/math"
cat > "$T/src/com/arlandsofia/olu/game/Actor.java" <<'JAVA'
package com.arlandsofia.olu.game;
public class Actor {
 public float x,y,alpha=1f; public int dir; public boolean visible=true,walking,sprinting;
 public void face(float x,float y){} public void faceTo(Actor a){}
 public void setPose(String p,float t){} public void clearPose(){}
 public void showEmote(String s,float t){} public static int dirOf(String s){return 0;}
}
JAVA
cat > "$T/src/com/arlandsofia/olu/Assets.java" <<'JAVA'
package com.arlandsofia.olu;
import com.badlogic.gdx.graphics.Texture;
public class Assets {
 public final Texture pixel=new Texture();
 public final Object title=new Object(),body=new Object(),label=new Object();
 public static final int DIR_DOWN=0,DIR_LEFT=1,DIR_RIGHT=2;
 public Texture uiTex(String p){return new Texture();} public Texture tex(String p){return new Texture();}
}
JAVA
cat > "$T/src/com/arlandsofia/olu/ui/Ui.java" <<'JAVA'
package com.arlandsofia.olu.ui;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.Color;
public class Ui {
 public static final Color INK=new Color(), GOLD=new Color(), LAVENDER=new Color(), CREAM=new Color();
 public void rect(float x,float y,float w,float h,Color c,float a){}
 public void image(Texture t,float x,float y,float w,float h,float a){}
 public void text(Object f,String s,float x,float y,Color c,float size,int align,float width){}
 public void textCenter(Object f,String s,float x,float y,Color c,float size){}
}
JAVA
cat > "$T/src/com/badlogic/gdx/graphics/Color.java" <<'JAVA'
package com.badlogic.gdx.graphics;
public class Color {
 public float r,g,b,a;
 public Color(){}public Color(float r,float g,float b,float a){this.r=r;this.g=g;this.b=b;this.a=a;}
 public static Color valueOf(String s){return new Color(1,1,1,1);}
 public Color set(Color c){return set(c.r,c.g,c.b,c.a);}
 public Color set(float r,float g,float b,float a){this.r=r;this.g=g;this.b=b;this.a=a;return this;}
}
JAVA
cat > "$T/src/com/badlogic/gdx/math/MathUtils.java" <<'JAVA'
package com.badlogic.gdx.math;
public class MathUtils {
 public static final float PI=(float)Math.PI;
 public static float sin(float v){return (float)Math.sin(v);}
 public static float cos(float v){return (float)Math.cos(v);}
 public static float random(float a,float b){return (a+b)*.5f;}
}
JAVA
cat > "$T/src/CameraSmoke.java" <<'JAVA'
import java.util.*;
import com.arlandsofia.olu.Assets;
import com.arlandsofia.olu.game.*;
public class CameraSmoke {
 static int checks;
 static void check(boolean b,String s){checks++;if(!b)throw new AssertionError(s);}
 static Map<String,Object> command(Object... kv) {
  Map<String,Object> out=new HashMap<>();
  for(int i=0;i<kv.length;i+=2)out.put((String)kv[i],kv[i+1]);return out;
 }
 static final class HostImpl implements CutscenePlayer.Host {
  final Actor pl=new Actor(),partner=new Actor();
  HostImpl(){pl.x=100;pl.y=160;partner.x=220;partner.y=180;}
  public Actor actor(String w){return "partner".equals(w)?partner:pl;}
  public Actor spawn(String a,String s,float x,float y,int d){return new Actor();}
  public void despawn(String id){}
  public void showPartner(boolean b){}
  public void say(String scene,int from,int n,Runnable done){done.run();}
  public void line(String speaker,String emo,String txt,Runnable done){done.run();}
  public void sfx(String s){} public void music(String s){}
  public float camX(){return pl.x;}public float camY(){return pl.y;}
  public boolean canStand(float x,float y){return true;}
 }
 public static void main(String[] a){
  HostImpl h=new HostImpl();
  CutscenePlayer player=new CutscenePlayer(h,new Assets());
  player.start(Arrays.asList(command("c","shot","focus","couple","frame","intimate","t",.4f),
        command("c","wait","t",2f)),null);
  for(int i=0;i<38;i++)player.update(1/60f);
  check(player.camActive(),"cinema camera active");
  check(Math.abs(player.camX()-160f)<1.3f,"couple center x");
  check(Math.abs(player.camY()-140f)<1.3f,"couple center y");
  check(player.zoom()>1.10f,"intimate framing should zoom in, not out");
  player.drawUi(new com.arlandsofia.olu.ui.Ui(),1280,720);
  player.start(Arrays.asList(command("c","shot","focus","player","frame","wide","t",0f),
        command("c","wait","t",1f)),null);
  check(player.zoom()<1f,"wide frame zooms out");
  check(Math.abs(player.camX()-100f)<.01f,"single protagonist framing");
  player.start(Arrays.asList(command("c","move","who","player","to",Arrays.asList(10)),
        command("c","wait","t",1f)),null);
  player.update(.1f);
  check(player.active(),"invalid point should be ignored without crash");
  System.out.println("V4.6.3 cinematic runtime smoke PASS: "+checks);
 }
}
JAVA
javac --release 11 -encoding UTF-8 -d "$T" \
 "$T/src/com/arlandsofia/olu/game/Actor.java" "$T/src/com/arlandsofia/olu/Assets.java" \
 "$T/src/com/arlandsofia/olu/ui/Ui.java" "$T/src/com/badlogic/gdx/graphics/Color.java" \
 "$T/src/com/badlogic/gdx/math/MathUtils.java" \
 tools/stubs/logic/com/badlogic/gdx/graphics/Texture.java \
 tools/stubs/logic/com/badlogic/gdx/graphics/g2d/{TextureRegion,SpriteBatch}.java \
 tools/stubs/ui/com/badlogic/gdx/utils/Align.java \
 core/src/main/java/com/arlandsofia/olu/logic/{Json,CinematicMotionV463,PremiumLayoutV463}.java \
 core/src/main/java/com/arlandsofia/olu/game/CutscenePlayer.java \
 tools/tests/V463CinematicUiLogicTest.java "$T/src/CameraSmoke.java"
java -cp "$T" CameraSmoke
java -cp "$T" V463CinematicUiLogicTest
