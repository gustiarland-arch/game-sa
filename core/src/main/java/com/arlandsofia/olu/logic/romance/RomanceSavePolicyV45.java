package com.arlandsofia.olu.logic.romance;

/** Reject incompatible, future-version, or cross-route saved states. */
public final class RomanceSavePolicyV45 {
    private RomanceSavePolicyV45() {}
    public static boolean acceptsExisting(String route,RomanceEngineV45.Snapshot saved) {
        return saved!=null&&saved.schema>=1&&saved.schema<=RomanceEngineV45.SCHEMA
                &&route!=null&&route.equals(saved.route);
    }
}
