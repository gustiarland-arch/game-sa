package com.arlandsofia.olu.logic;

/** Pure math for eight-facing motion and frame-independent blend. No game state. */
public final class AnimationMathV462 {
    // Row order in eight-direction sheets: down, down-left, left, up-left,
    // up, up-right, right, down-right.
    public static final int DOWN=0, DOWN_LEFT=1, LEFT=2, UP_LEFT=3,
            UP=4, UP_RIGHT=5, RIGHT=6, DOWN_RIGHT=7;
    private AnimationMathV462() {}

    public static int facing(float dx, float dy, int previous) {
        if (Math.abs(dx)+Math.abs(dy) < 0.0001f) return previous;
        // atan2 uses screen-down y, clockwise 0=down and steps of 45 degrees.
        double angle = Math.atan2(-dx, dy);
        return Math.floorMod((int)Math.round(angle / (Math.PI/4)), 8);
    }
    public static float blend(float oldValue, float target, float dt, float speed) {
        if (dt<=0) return oldValue;
        float step = 1f-(float)Math.exp(-Math.min(0.1f,dt)*Math.max(0f,speed));
        return Math.max(0f,Math.min(1f,oldValue+(target-oldValue)*step));
    }
    public static int phase16(float clock, boolean sprint) {
        return Math.floorMod((int)(clock*(sprint?21.5f:15.6f)),16);
    }
    public static float diagonalLean(int facing) {
        switch(facing) {
            case DOWN_LEFT: case UP_LEFT:return -1.6f;
            case DOWN_RIGHT: case UP_RIGHT:return 1.6f;
            default:return 0f;
        }
    }
}
