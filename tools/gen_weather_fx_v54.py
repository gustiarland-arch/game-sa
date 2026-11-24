"""v5.4 weather & water assets, generated offline (no external licensed material).

Usage: python3 tools/gen_weather_fx_v54.py android/assets

Outputs
  fx/v54_puddle_0.png .. fx/v54_puddle_2.png  pixel-art rain puddles (sizes match
                                              WeatherFxV54.PUDDLE_SIZES)
  audio/sfx/v54_thunder.wav                   rolling thunder, 22.05 kHz mono 16-bit
  audio/sfx/v54_step_puddle.wav               foot splash in a puddle
Runtime never needs Python. Deterministic: same seed, same bytes.
"""
from pathlib import Path
import sys
import wave
import numpy as np
from PIL import Image

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'android/assets')
RNG = np.random.default_rng(54)
SR = 22050

# ---------------------------------------------------------------- puddles
SIZES = [(20, 7), (30, 10), (42, 13)]  # half width, half height (world px)


def puddle(rx, ry, seed):
    rng = np.random.default_rng(seed)
    w, h = rx * 2, ry * 2
    img = np.zeros((h, w, 4), dtype=np.uint8)
    # Irregular outline: radius wobble along the angle, quantised to whole pixels.
    k = rng.uniform(0, 6.28, 3)
    for y in range(h):
        for x in range(w):
            dx = (x + 0.5 - rx) / rx
            dy = (y + 0.5 - ry) / ry
            ang = np.arctan2(dy, dx)
            wob = 0.86 + 0.07 * np.sin(2 * ang + k[0]) + 0.05 * np.sin(3 * ang + k[1]) + 0.03 * np.sin(5 * ang + k[2])
            d = np.sqrt(dx * dx + dy * dy)
            if d > wob:
                continue
            edge = d > wob - (1.6 / min(rx, ry)) * 1.2
            # Body: dark slate water reflecting a grey-blue sky.
            shade = 0.90 + 0.10 * (y / h)
            c = (int(92 * shade), int(122 * shade), int(160 * shade), 170)
            if edge:
                c = (58, 72, 96, 165) if dy > -0.2 else (168, 190, 214, 175)
            img[y, x] = c
    # Sky reflection streaks (two short light rows near the top).
    for i in range(2 + rx // 16):
        yy = int(ry * (0.55 + 0.25 * i / 3))
        x0 = int(rx * (0.45 + 0.5 * rng.random()))
        ln = max(3, int(rx * (0.25 + 0.25 * rng.random())))
        for x in range(x0, min(w - 2, x0 + ln)):
            if img[yy, x, 3] and img[yy, x, 0] not in (58, 168):
                img[yy, x] = (196, 216, 238, 190)
    return Image.fromarray(img, 'RGBA')


fx = ROOT / 'fx'
fx.mkdir(parents=True, exist_ok=True)
for i, (rx, ry) in enumerate(SIZES):
    puddle(rx, ry, 540 + i).save(fx / f'v54_puddle_{i}.png')

# ---------------------------------------------------------------- audio


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def write(name, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.86
    pcm = (x * 32767).astype('<i2')
    path = ROOT / 'audio' / 'sfx' / name
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# Thunder: crack (bright, short) into a long low rumble with slow amplitude rolls.
dur = 3.4
n = int(SR * dur)
t = np.arange(n) / SR
noise = RNG.standard_normal(n)
rumble = lowpass(lowpass(noise, 140.0), 110.0)
rolls = 0.55 + 0.45 * np.sin(2 * np.pi * 1.3 * t + 0.4) * np.sin(2 * np.pi * 0.47 * t + 1.1)
env = np.minimum(1.0, t / 0.09) * np.exp(-t / 1.25)
crack = lowpass(noise, 1800.0) * np.exp(-t / 0.10) * 0.55
thunder = rumble * rolls * env * 3.2 + crack
fade = np.minimum(1.0, (dur - t) / 0.35)
write('v54_thunder.wav', thunder * fade)

# Puddle step: short filtered noise burst + a few droplet blips.
dur = 0.22
n = int(SR * dur)
t = np.arange(n) / SR
burst = lowpass(RNG.standard_normal(n), 2600.0) * np.exp(-t / 0.045)
drops = np.zeros(n)
for f0, at in ((1450, 0.035), (1900, 0.07), (1250, 0.11)):
    tt = np.clip(t - at, 0, None)
    drops += np.sin(2 * np.pi * (f0 + 900 * tt) * tt) * np.exp(-tt / 0.018) * (t >= at) * 0.35
write('v54_step_puddle.wav', burst + drops)
print('v5.4 weather fx: 3 puddles, thunder, puddle step')
