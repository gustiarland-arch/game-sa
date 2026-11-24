package com.arlandsofia.olu.logic;

import java.util.ArrayList;
import java.util.List;

/** Logika puzzle urutan simbol (tanpa UI). Salah -> ulang dari awal; petunjuk muncul setelah N kali gagal. */
public final class PuzzleLogic {
    public enum Result { CORRECT, WRONG, SOLVED }

    public final List<String> order;
    public final List<String> entered = new ArrayList<>();
    public final int hintAfterFails;
    public int fails;

    public PuzzleLogic(List<String> order, int hintAfterFails) {
        this.order = new ArrayList<>(order);
        this.hintAfterFails = hintAfterFails;
    }

    public Result input(String symbol) {
        if (solved()) return Result.SOLVED;
        if (order.get(entered.size()).equals(symbol)) {
            entered.add(symbol);
            return solved() ? Result.SOLVED : Result.CORRECT;
        }
        entered.clear();
        fails++;
        return Result.WRONG;
    }

    public boolean solved() { return entered.size() >= order.size(); }
    public boolean hintVisible() { return fails >= hintAfterFails; }
}
