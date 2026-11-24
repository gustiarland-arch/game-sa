package com.badlogic.gdx.math;
public class MathUtils {
  private static final java.util.Random R = new java.util.Random(42);
  public static float random(float min,float max) {return min+(max-min)*R.nextFloat();}
  public static float random() {return R.nextFloat();}
  public static float sin(float a) {return (float)Math.sin(a);}
}
