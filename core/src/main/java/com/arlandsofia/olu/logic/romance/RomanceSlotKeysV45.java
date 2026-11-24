package com.arlandsofia.olu.logic.romance;

/** One isolated romance save per route + actual slot from the v4.4 SaveStore. */
public final class RomanceSlotKeysV45 {
    private RomanceSlotKeysV45() {}
    public static String namespace(String route,int slot) {
        if(!"arland".equals(route)&&!"sofia".equals(route))throw new IllegalArgumentException("Invalid route");
        if(slot<1||slot>2)throw new IllegalArgumentException("Invalid slot");
        return "olu-romance-v45-"+route+(slot==1?"":"-slot-"+slot);
    }
}
