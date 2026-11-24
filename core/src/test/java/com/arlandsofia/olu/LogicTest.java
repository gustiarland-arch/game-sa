package com.arlandsofia.olu;

import org.junit.Test;

import java.io.File;

/** JUnit: menjalankan LogicSelfTest (kedua route Prologue + Chapter 1, save, puzzle, data). */
public class LogicTest {
    @Test
    public void storyQuestSaveLogic() throws Exception {
        String dir = System.getProperty("olu.assets", "../android/assets");
        LogicSelfTest.runAll(new File(dir));
        System.out.println("LogicSelfTest: " + LogicSelfTest.checks + " pemeriksaan lulus");
    }
}
