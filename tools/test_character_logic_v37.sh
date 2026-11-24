#!/usr/bin/env bash
# Character renderer and time-dependent shadow arithmetic typechecked using minimal LibGDX stubs.
# Does NOT replace a real APK/LibGDX build.
set -euo pipefail
cd "$(dirname "$0")/.."
D=$(mktemp -d);trap 'rm -rf "$D"' EXIT
mkdir -p "$D/src/com/arlandsofia/olu"
cat > "$D/src/com/arlandsofia/olu/Assets.java" <<'JAVA'
package com.arlandsofia.olu;
import com.badlogic.gdx.graphics.g2d.TextureRegion;
public final class Assets {
 public static final int FRAME_W=48,FRAME_H=72,DIR_LEFT=1,DIR_RIGHT=2,DIR_UP=3,DIR_DOWN=0;
 public static int poseIndex(String s){return 0;}
 public TextureRegion poseFrame(String s,int p,int d,int f){return new TextureRegion(new com.badlogic.gdx.graphics.Texture(),0,0,48,72);}
 public TextureRegion walkFrame8(String s,int d,int f){return new TextureRegion(new com.badlogic.gdx.graphics.Texture(),0,0,48,72);}
 public TextureRegion idleFrame8(String s,int d,int f){return new TextureRegion(new com.badlogic.gdx.graphics.Texture(),0,0,48,72);}
 public TextureRegion walkFrame(String s,int d,int f){return new TextureRegion(new com.badlogic.gdx.graphics.Texture(),0,0,48,72);}
 public TextureRegion idleFrame(String s,int d,int f){return new TextureRegion(new com.badlogic.gdx.graphics.Texture(),0,0,48,72);}
}
JAVA
mkdir -p "$D/src/com/badlogic/gdx/math"
cat > "$D/src/com/badlogic/gdx/math/MathUtils.java" <<'JAVA'
package com.badlogic.gdx.math;
public class MathUtils {
 public static final float PI = (float) Math.PI;
 public static float random(float a,float b) {return (a+b)/2f;}
 public static float sin(float v) {return (float)Math.sin(v);}
}
JAVA
javac --release 11 -encoding UTF-8 -d "$D/out" \
  tools/stubs/logic/com/badlogic/gdx/graphics/Texture.java \
  tools/stubs/logic/com/badlogic/gdx/graphics/g2d/{TextureRegion,SpriteBatch}.java \
  "$D/src/com/badlogic/gdx/math/MathUtils.java" \
  "$D/src/com/arlandsofia/olu/Assets.java" \
  core/src/main/java/com/arlandsofia/olu/game/Actor.java \
  core/src/main/java/com/arlandsofia/olu/logic/{AnimationMathV462,MotionPersonalityV53,WorldClock,WorldLightingV37}.java
cat > "$D/src/Smoke.java" <<'JAVA'
import com.arlandsofia.olu.game.Actor;
import com.arlandsofia.olu.logic.WorldLightingV37;
import com.arlandsofia.olu.Assets;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
public class Smoke {
 static void ok(boolean v,String why){if(!v)throw new AssertionError(why);}
 public static void main(String[] args){
  Actor a=new Actor("arland");a.x=100;a.y=100;
  a.walking=true;a.sprinting=false;
  for(int i=0;i<240;i++){a.update(1f/120f);a.draw(new SpriteBatch(),new Assets(),1400,new Texture());}
  ok(a.anim>=0&&a.anim<24,"normal walk should stay in 24-phase cycle");
  a.sprinting=true;
  for(int i=0;i<300;i++){a.update(1f/120f);a.draw(new SpriteBatch(),new Assets(),1400,new Texture());}
  ok(a.anim>=0&&a.anim<24,"sprint animation remains bounded");
  a.walking=false;a.setPose("hug",2f);
  for(int i=0;i<125;i++){a.update(1f/60f);a.draw(new SpriteBatch(),new Assets(),1400,new Texture());}
  ok(a.pose==null,"timed pose resets");
  ok(WorldLightingV37.shadowOffsetX(8*60,false,false,2)>0,"AM sun direction");
  ok(WorldLightingV37.shadowOffsetX(17*60,false,false,2)<0,"PM sun direction");
  ok(WorldLightingV37.shadowOffsetX(23*60,false,false,2)==0,"night no direct sunlight");
  ok(WorldLightingV37.shadowOffsetX(17*60,true,false,2)==0,"indoors no directional sun");
  ok(WorldLightingV37.contactOpacity(20*60,false,false,0)==0,"hemat disables prop contact shadows");
  ok(WorldLightingV37.contactOpacity(20*60,false,false,2)>0,"cinematic contact shadows");
  ok(WorldLightingV37.width(200)<=110,"contact size bounded");
  System.out.println("V3.7 Actor+Lighting headless JAVA TYPECHECK/SMOKE OK");
 }
}
JAVA
javac --release 11 -cp "$D/out" -d "$D/out" "$D/src/Smoke.java"
java -cp "$D/out" Smoke
