"""Soundtrack orisinal v1.2 (sintesis numpy/scipy, bebas lisensi) -> OGG stereo.
Instrumen: electric piano (FM), pluck (Karplus-Strong), pad detune, bass, flute, bell, drum lembut; reverb Schroeder + chorus.
Pemakaian: python3 tools/gen_music2.py <out_dir>
"""
import sys, os, subprocess, tempfile
import numpy as np
from scipy.signal import lfilter, butter
from scipy.io import wavfile

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
SR = 32000
NOTES = {n: i for i, n in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])}
def midi(n):
    if isinstance(n, (int, float)): return n
    name, o = (n[:-1], int(n[-1])); return NOTES[name] + 12 * (o + 1)
def hz(m): return 440.0 * 2 ** ((midi(m) - 69) / 12)

def env_adsr(n, a, d, s, r, sr=SR):
    t = np.arange(n) / sr; dur = n / sr
    e = np.where(t < a, t / max(a, 1e-4), np.where(t < a + d, 1 - (1 - s) * (t - a) / max(d, 1e-4), s))
    rel = np.clip((dur - t) / max(r, 1e-4), 0, 1)
    return e * rel

def lowpass(x, fc, order=2):
    b, a = butter(order, min(0.99, fc / (SR / 2)))
    return lfilter(b, a, x)

# ---------------------------------------------------------------- instrumen
def ep(f, dur, vel=1.0):
    n = int(SR * dur); t = np.arange(n) / SR
    mod = np.sin(2 * np.pi * f * 1.0 * t) * (2.2 * np.exp(-t * 3))
    w = np.sin(2 * np.pi * f * t + mod) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6)
    return w * np.exp(-t * 1.6) * np.minimum(1, t * 300) * env_adsr(n, 0.003, 0.1, 1, 0.08) * vel

def pluck(f, dur, vel=1.0, bright=0.5):
    n = int(SR * dur); p = max(2, int(SR / f))
    rng = np.random.default_rng(int(f * 100) % 9999)
    buf = rng.uniform(-1, 1, p); buf = lowpass(buf, 2000 + 6000 * bright, 1)
    out = np.zeros(n); idx = 0
    b = buf.copy()
    for i in range(n):
        out[i] = b[idx]
        nxt = (idx + 1) % p
        b[idx] = 0.497 * (b[idx] + b[nxt])
        idx = nxt
    return out * vel * env_adsr(n, 0.001, 0.05, 1, 0.05)

def pluck_fast(f, dur, vel=1.0):
    """pluck sintetis cepat (tanpa loop python): harmonik dengan decay berbeda"""
    n = int(SR * dur); t = np.arange(n) / SR
    w = sum((0.6 ** k) * np.sin(2 * np.pi * f * (k + 1) * t) * np.exp(-t * (2.5 + 2.2 * k)) for k in range(6))
    return w * np.minimum(1, t * 500) * env_adsr(n, 0.001, 0.05, 1, 0.06) * vel

def pad(f, dur, vel=1.0, bright=1800):
    n = int(SR * dur); t = np.arange(n) / SR
    w = np.zeros(n)
    for dt_ in (-0.006, 0.0, 0.007):
        ph = 2 * np.pi * f * (1 + dt_) * t
        w += 2 * ((ph / (2 * np.pi)) % 1) - 1  # saw
    w = lowpass(w / 3, bright, 2)
    return w * env_adsr(n, min(0.6, dur * 0.3), 0.3, 0.85, min(0.8, dur * 0.3)) * vel

def bass(f, dur, vel=1.0):
    n = int(SR * dur); t = np.arange(n) / SR
    w = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) + 0.1 * np.sin(2 * np.pi * 3 * f * t)
    return w * env_adsr(n, 0.005, 0.2, 0.7, 0.06) * vel

def flute(f, dur, vel=1.0):
    n = int(SR * dur); t = np.arange(n) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t * 2)
    ph = 2 * np.cumsum(np.pi * f * vib / SR)
    w = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    breath = lowpass(np.random.default_rng(3).normal(0, 1, n), 3000) * 0.04
    return (w + breath) * env_adsr(n, 0.06, 0.1, 0.85, 0.08) * vel

def bell(f, dur, vel=1.0):
    n = int(SR * dur); t = np.arange(n) / SR
    w = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t * 3) + 0.2 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t * 6)
    return w * np.exp(-t * 2.2) * np.minimum(1, t * 400) * vel

def piano(f, dur, vel=1.0):
    n = int(SR * dur); t = np.arange(n) / SR
    w = sum((0.55 ** k) * np.sin(2 * np.pi * f * (k + 1) * (1 + 0.0004 * k * k) * t) * np.exp(-t * (1.1 + 0.9 * k)) for k in range(7))
    return w * np.minimum(1, t * 600) * env_adsr(n, 0.002, 0.1, 1, 0.12) * vel

_rng = np.random.default_rng(7)
def kick(vel=1.0):
    n = int(SR * 0.3); t = np.arange(n) / SR
    f = 110 * np.exp(-t * 18) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) * vel
def snare(vel=1.0):
    n = int(SR * 0.2); t = np.arange(n) / SR
    nz = lowpass(_rng.normal(0, 1, n), 5000) * np.exp(-t * 22)
    return (nz * 0.8 + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)) * vel
def hat(vel=1.0, open_=False):
    n = int(SR * (0.18 if open_ else 0.05)); t = np.arange(n) / SR
    nz = _rng.normal(0, 1, n); b, a = butter(2, 7000 / (SR / 2), 'high'); nz = lfilter(b, a, nz)
    return nz * np.exp(-t * (14 if open_ else 70)) * vel * 0.5
def shaker(vel=1.0):
    n = int(SR * 0.08); t = np.arange(n) / SR
    nz = _rng.normal(0, 1, n); b, a = butter(2, [4000 / (SR / 2), 9000 / (SR / 2)], 'band'); nz = lfilter(b, a, nz)
    return nz * np.sin(np.pi * t / 0.08) * vel * 0.4

# ---------------------------------------------------------------- mixer
class Track:
    def __init__(s, bpm, bars, beats=4):
        s.bpm = bpm; s.beat = 60 / bpm; s.len = bars * beats * s.beat
        s.n = int(SR * (s.len + 4)); s.L = np.zeros(s.n); s.R = np.zeros(s.n); s.bars = bars; s.beats = beats
        s.send = np.zeros(s.n)
    def put(s, sig, at_beat, pan=0.0, gain=1.0, rev=0.3, swing=0.0):
        b = at_beat
        if swing and (b * 2) % 2 == 1: b += swing
        i = int(SR * b * s.beat)
        if i >= s.n: return
        sig = sig[: s.n - i] * gain
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        s.L[i:i + len(sig)] += sig * l; s.R[i:i + len(sig)] += sig * r
        s.send[i:i + len(sig)] += sig * rev
    def render(s, name, tail_fold=True, room=0.82, master=0.9):
        rv = reverb(s.send, room)
        L = s.L + rv[0]; R = s.R + rv[1]
        # lipat ekor ke awal agar loop mulus
        loopN = int(SR * s.len)
        if tail_fold:
            tail = len(L) - loopN
            L[:tail] += L[loopN:]; R[:tail] += R[loopN:]
        L, R = L[:loopN], R[:loopN]
        st = np.stack([L, R], 1)
        st = np.tanh(st * 1.2 / max(1e-6, np.max(np.abs(st)))) * master
        st = st / np.max(np.abs(st)) * 0.89
        tmp = tempfile.mktemp(suffix='.wav')
        wavfile.write(tmp, SR, (st * 32767).astype(np.int16))
        out = os.path.join(OUT, name + '.ogg')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-c:a', 'libvorbis', '-q:a', '3', out], check=True)
        os.remove(tmp)
        print(name, '%.1fs' % s.len, os.path.getsize(out) // 1024, 'KB')

def reverb(x, room=0.82):
    outs = []
    for side, combs in ((0, (1116, 1188, 1277, 1356)), (1, (1139, 1211, 1300, 1379))):
        y = np.zeros_like(x)
        for d in combs:
            d = int(d * SR / 44100)
            a = np.zeros(d + 1); a[0] = 1; a[-1] = -room
            y += lfilter([1], a, lowpass(x, 5000, 1))
        for d in (556, 441):
            d = int(d * SR / 44100) + side * 7
            b = np.zeros(d + 1); b[0] = -0.5; b[-1] = 1
            a = np.zeros(d + 1); a[0] = 1; a[-1] = -0.5
            y = lfilter(b, a, y)
        outs.append(y * 0.12)
    return outs

def chord_notes(root, kind):
    iv = {'maj': [0, 4, 7], 'min': [0, 3, 7], 'maj7': [0, 4, 7, 11], 'min7': [0, 3, 7, 10], 'dom7': [0, 4, 7, 10], 'sus2': [0, 2, 7], 'add9': [0, 4, 7, 14], 'min9': [0, 3, 7, 10, 14]}[kind]
    r = midi(root); return [r + i for i in iv]

def melody_from(scale, chords, bars, beats, seed, density=0.6, rng_oct=(0, 12), motif_len=2):
    """melodi berbasis motif: motif 2 bar diulang/variasi, nada akor di ketukan kuat."""
    rng = np.random.default_rng(seed)
    motif = []
    for b in range(motif_len * beats * 2):  # per setengah ketukan
        if rng.random() < density: motif.append((b / 2, rng.integers(0, 5), 0.5 if rng.random() < 0.6 else 1.0))
    out = []
    for bar in range(bars):
        root, kind = chords[bar % len(chords)]
        tones = chord_notes(root, kind)
        var = (bar // motif_len) % 4
        for (pos, deg, dur) in motif:
            if int(pos) // beats != bar % motif_len: continue
            p = pos - (bar % motif_len) * beats
            if var == 3 and rng.random() < 0.3: continue
            strong = abs(p - round(p)) < 1e-6 and int(p) % 2 == 0
            if strong: note = tones[(deg + var) % len(tones)] + 12
            else:
                base = tones[0] + 12; cands = [base + s for s in scale]
                note = cands[(deg * 2 + var) % len(cands)]
            out.append((bar * beats + p, note, dur))
    return out

# ---------------------------------------------------------------- lagu
def song_town():
    T = Track(96, 32)
    prog = [('F3', 'maj7'), ('D3', 'min7'), ('A#2', 'maj7'), ('C3', 'dom7'), ('F3', 'maj7'), ('A2', 'min7'), ('A#2', 'maj7'), ('C3', 'sus2')]
    for bar in range(32):
        root, kind = prog[bar % 8]; ns = chord_notes(root, kind)
        for k, b in enumerate([0, 1.5, 2, 3]):  # EP comping
            for m in ns[1:]: T.put(ep(hz(m + 12), 0.5, 0.18), bar * 4 + b, pan=-0.2, rev=0.25)
        T.put(bass(hz(midi(root) - 12), 1.4, 0.55), bar * 4); T.put(bass(hz(midi(root) - 12 + 7), 0.9, 0.4), bar * 4 + 2.5)
        if bar >= 4:
            T.put(kick(0.55), bar * 4); T.put(kick(0.4), bar * 4 + 2.5)
            T.put(snare(0.25), bar * 4 + 1); T.put(snare(0.25), bar * 4 + 3)
            for h in range(8): T.put(shaker(0.5 if h % 2 else 0.3), bar * 4 + h / 2, pan=0.3, rev=0.05)
    mel = melody_from([0, 2, 4, 7, 9, 12, 14], prog, 32, 4, 11, 0.55)
    for b, m, d in mel:
        if b >= 16: T.put(pluck_fast(hz(m), d * T.beat * 1.6, 0.42), b, pan=0.25, rev=0.35)
    for b, m, d in melody_from([0, 2, 4, 7, 9, 12], prog, 32, 4, 23, 0.3):
        if b >= 64: T.put(bell(hz(m + 12), 1.2, 0.12), b, pan=-0.4, rev=0.5)
    T.render('town_theme')

def song_memory():
    T = Track(70, 24)
    prog = [('D3', 'add9'), ('G3', 'maj7'), ('B2', 'min9'), ('A2', 'sus2'), ('G2', 'maj7'), ('D3', 'add9'), ('E3', 'min7'), ('A2', 'sus2')]
    for bar in range(24):
        root, kind = prog[bar % 8]; ns = chord_notes(root, kind)
        for m in ns: T.put(pad(hz(m), T.beat * 4.2, 0.13, 1400), bar * 4, pan=0.0, rev=0.6)
        for k in range(8): T.put(bell(hz(ns[k % len(ns)] + 24), 1.4, 0.10), bar * 4 + k / 2, pan=(-0.5 if k % 2 else 0.5), rev=0.7)
        T.put(bass(hz(midi(root) - 12), T.beat * 3.5, 0.35), bar * 4)
    for b, m, d in melody_from([0, 2, 4, 6, 7, 9, 11], prog, 24, 4, 5, 0.35):
        if b >= 32: T.put(flute(hz(m), d * T.beat * 2.2, 0.22), b, pan=0.1, rev=0.6)
    T.render('memory_theme', room=0.86)

def song_cafe():
    T = Track(84, 32)
    prog = [('D3', 'min9'), ('G3', 'dom7'), ('C3', 'maj7'), ('A2', 'dom7'), ('D3', 'min7'), ('G3', 'dom7'), ('E3', 'min7'), ('A2', 'dom7')]
    for bar in range(32):
        root, kind = prog[bar % 8]; ns = chord_notes(root, kind)
        for b in (0, 2.5):
            for m in ns[1:]: T.put(ep(hz(m + 12), 0.9, 0.17), bar * 4 + b, pan=-0.15, rev=0.3)
        for k, b in enumerate([0, 1, 2, 3]):  # walking bass
            step_ = [0, 4, 7, 9][k] if k < 3 else 10
            T.put(bass(hz(midi(root) - 12 + step_), T.beat * 0.95, 0.45), bar * 4 + b)
        T.put(kick(0.4), bar * 4); T.put(kick(0.3), bar * 4 + 2.75)
        T.put(snare(0.18), bar * 4 + 1); T.put(snare(0.2), bar * 4 + 3)
        for h in range(8): T.put(hat(0.5 if h % 2 == 0 else 0.3), bar * 4 + h / 2 + (0.08 if h % 2 else 0), pan=0.35, rev=0.05)
    for b, m, d in melody_from([0, 2, 3, 5, 7, 9, 10], prog, 32, 4, 31, 0.45):
        if 8 <= b < 120: T.put(piano(hz(m + 12), d * T.beat * 1.8, 0.3), b, pan=0.2, rev=0.35)
    # crackle vinyl
    T.put(lowpass(np.random.default_rng(9).normal(0, 1, int(SR * T.len)) * (np.random.default_rng(10).random(int(SR * T.len)) > 0.9993) * 0.5, 4000), 0, rev=0)
    T.render('cafe_theme')

def song_rain():
    T = Track(66, 24)
    prog = [('A2', 'min9'), ('F2', 'maj7'), ('C3', 'add9'), ('G2', 'sus2'), ('A2', 'min7'), ('D3', 'min7'), ('F2', 'maj7'), ('E2', 'min7')]
    for bar in range(24):
        root, kind = prog[bar % 8]; ns = chord_notes(root, kind)
        for k, m in enumerate(ns + [ns[1] + 12]):
            T.put(piano(hz(m + 12), T.beat * 3, 0.16), bar * 4 + k * 0.5, pan=-0.3 + 0.12 * k, rev=0.55)
        T.put(pad(hz(midi(root)), T.beat * 4, 0.08, 900), bar * 4, rev=0.5)
        T.put(bass(hz(midi(root) - 12), T.beat * 3.6, 0.3), bar * 4)
    for b, m, d in melody_from([0, 2, 3, 5, 7, 8, 10], prog, 24, 4, 41, 0.3):
        if b >= 16: T.put(piano(hz(m + 12), d * T.beat * 2.5, 0.28), b, pan=0.15, rev=0.5)
    nz = lowpass(np.random.default_rng(2).normal(0, 1, int(SR * T.len)), 2500) * 0.05
    T.put(nz, 0, rev=0.1)
    T.render('rain_theme', room=0.85)

def song_night():
    T = Track(100, 32)
    prog = [('G2', 'maj'), ('E2', 'min'), ('C3', 'maj'), ('D3', 'sus2'), ('G2', 'maj'), ('B2', 'min'), ('C3', 'maj'), ('D3', 'maj')]
    for bar in range(32):
        root, kind = prog[bar % 8]; ns = chord_notes(root, kind)
        for k in range(8): T.put(pluck_fast(hz(ns[[0, 1, 2, 1][k % 4]] + 12), 0.4, 0.22), bar * 4 + k / 2, pan=-0.35, rev=0.3)
        for m in ns: T.put(pad(hz(m + 12), T.beat * 4, 0.07, 1600), bar * 4, rev=0.5)
        T.put(bass(hz(midi(root) - 12), 1.0, 0.5), bar * 4); T.put(bass(hz(midi(root) - 12), 0.5, 0.35), bar * 4 + 2)
        if bar >= 8:
            T.put(kick(0.45), bar * 4); T.put(kick(0.35), bar * 4 + 2)
            for h in range(4): T.put(shaker(0.5), bar * 4 + h + 0.5, pan=0.4, rev=0.05)
            T.put(snare(0.15), bar * 4 + 3.5)
    for b, m, d in melody_from([0, 2, 4, 7, 9, 12, 14], prog, 32, 4, 51, 0.5):
        if b >= 32: T.put(flute(hz(m + 12), d * T.beat * 1.5, 0.25), b, pan=0.2, rev=0.45)
    T.render('night_theme')

def song_star():
    T = Track(78, 24)
    prog = [('E3', 'add9'), ('C3', 'maj7'), ('G3', 'add9'), ('D3', 'sus2'), ('A2', 'min9'), ('C3', 'maj7'), ('D3', 'sus2'), ('B2', 'min7')]
    for bar in range(24):
        root, kind = prog[bar % 8]; ns = chord_notes(root, kind)
        for k in range(16): T.put(pluck_fast(hz(ns[k % len(ns)] + 24), 0.3, 0.13), bar * 4 + k / 4, pan=np.sin(k) * 0.6, rev=0.6)
        for m in ns: T.put(pad(hz(m), T.beat * 4.3, 0.12, 2200), bar * 4, rev=0.7)
        T.put(bass(hz(midi(root) - 12), T.beat * 3.8, 0.4), bar * 4)
    for b, m, d in melody_from([0, 2, 4, 7, 9, 11, 14], prog, 24, 4, 61, 0.35):
        if b >= 32: T.put(bell(hz(m + 12), 1.6, 0.2), b, pan=-0.1, rev=0.7)
    T.render('star_theme', room=0.88)

def song_tender():
    T = Track(68, 24)
    prog = [('C3', 'add9'), ('G2', 'maj'), ('A2', 'min7'), ('F2', 'maj7'), ('C3', 'maj'), ('E2', 'min7'), ('F2', 'maj7'), ('G2', 'sus2')]
    for bar in range(24):
        root, kind = prog[bar % 8]; ns = chord_notes(root, kind)
        T.put(piano(hz(midi(root) - 12), T.beat * 4, 0.3), bar * 4, pan=-0.2, rev=0.45)
        for k, b in enumerate([1, 1.5, 2, 3, 3.5]): T.put(piano(hz(ns[(k + 1) % len(ns)] + 12), T.beat * 1.5, 0.14), bar * 4 + b, pan=-0.1, rev=0.45)
        if bar >= 8:
            for m in ns: T.put(pad(hz(m + 12), T.beat * 4, 0.06, 1200), bar * 4, rev=0.6)
    for b, m, d in melody_from([0, 2, 4, 5, 7, 9, 11], prog, 24, 4, 71, 0.4):
        if b >= 16: T.put(piano(hz(m + 12), d * T.beat * 2.2, 0.3), b, pan=0.15, rev=0.5)
    T.render('tender_theme', room=0.86)

def song_game():
    T = Track(124, 16)
    prog = [('C3', 'maj'), ('A2', 'min'), ('F2', 'maj'), ('G2', 'maj')]
    for bar in range(16):
        root, kind = prog[bar % 4]; ns = chord_notes(root, kind)
        for k in range(8): T.put(pluck_fast(hz(ns[k % 3] + 12 + (12 if k % 4 == 3 else 0)), 0.25, 0.25), bar * 4 + k / 2, pan=-0.3, rev=0.2)
        for k in range(4): T.put(bass(hz(midi(root) - 12), 0.4, 0.5), bar * 4 + k)
        T.put(kick(0.6), bar * 4); T.put(kick(0.6), bar * 4 + 2); T.put(snare(0.35), bar * 4 + 1); T.put(snare(0.35), bar * 4 + 3)
        for h in range(8): T.put(hat(0.45), bar * 4 + h / 2, pan=0.35, rev=0.03)
    for b, m, d in melody_from([0, 2, 4, 7, 9, 12], prog, 16, 4, 81, 0.6):
        if b >= 16: T.put(bell(hz(m + 12), 0.5, 0.22), b, pan=0.2, rev=0.25)
    T.render('game_theme')

if __name__ == '__main__':
    only = sys.argv[2:]
    for fn in [song_town, song_memory, song_cafe, song_rain, song_night, song_star, song_tender, song_game]:
        if not only or fn.__name__[5:] in only: fn()
