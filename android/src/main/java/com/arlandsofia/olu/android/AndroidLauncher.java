package com.arlandsofia.olu.android;

import android.os.Build;
import android.os.Bundle;
import android.view.WindowManager;

import com.arlandsofia.olu.OluGame;
import com.badlogic.gdx.backends.android.AndroidApplication;
import com.badlogic.gdx.backends.android.AndroidApplicationConfiguration;

/** Launcher Android native (OpenGL ES via LibGDX). Tanpa WebView, tanpa izin internet. */
public class AndroidLauncher extends AndroidApplication {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (Build.VERSION.SDK_INT >= 28) {
            // gambar sampai area notch; UI memakai safe inset dari LibGDX
            WindowManager.LayoutParams lp = getWindow().getAttributes();
            lp.layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
            getWindow().setAttributes(lp);
        }
        AndroidApplicationConfiguration config = new AndroidApplicationConfiguration();
        config.useImmersiveMode = true;      // sembunyikan bar sistem; swipe tepi tetap memunculkan navigasi
        config.useAccelerometer = false;
        config.useCompass = false;
        config.useGyroscope = false;
        config.useWakelock = false;
        config.numSamples = 0;
        initialize(new OluGame(), config);
    }
}
