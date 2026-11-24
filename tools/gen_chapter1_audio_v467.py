#!/usr/bin/env python3
"""Create original two-melody 20-second memory-book motif. Not copied music."""
from pathlib import Path
import math, wave, tempfile, subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'android/assets/audio/music/cinema_two_sides_v467.ogg'
RATE=22050
DURATION=22.4
N=int(RATE*DURATION)
y=np.zeros(N,dtype=np.float32)

def note(freq,at,hold,level,soft=False):
    start=int(at*RATE)
    length=max(0,min(N-start,int(RATE*hold)))
    if length<=0:return
    t=np.arange(length,dtype=np.float32)/RATE
    env=np.minimum(1.,t/.07)*np.minimum(1.,np.maximum(0.,(hold-t))/.38)
    env*=np.exp(-.9*t/max(.1,hold))
    sig=np.sin(2*np.pi*freq*t)
    sig+= (.16 if soft else .31)*np.sin(2*np.pi*freq*2*t)
    if not soft:sig+=.07*np.sin(2*np.pi*freq*3*t)
    y[start:start+length]+=sig*env*level

# Two short complementary *original* lines (low, high) that never quite
# overlap until the final two bars; this echoes the two narrative viewpoints.
bass=[174.61,196.0,164.81,220.0,174.61,196.0,146.83,174.61]
voice_a=[293.66,329.63,349.23,293.66,261.63,293.66,329.63,392.0]
voice_s=[392.0,349.23,329.63,293.66,349.23,392.0,440.0,392.0]
for bar in range(8):
    beat=bar*2.6
    note(bass[bar]/2,beat,2.4,.045,True)
    note(bass[bar],beat+.1,2.1,.025,True)
    for half in range(2):
        pitch=(voice_a if bar%2==0 else voice_s)[bar%8] * (1.0 if half==0 else 1.12246)
        note(pitch,beat+.22+half*1.15,1.6,.070 if bar<6 else .085)
    if bar>=6:
        note(voice_a[bar],beat+.66,1.8,.039,True)
        note(voice_s[bar],beat+.95,1.4,.039,True)

# Soft acoustic echo and fades, consistent with 100% offline LibGDX playback.
delay=int(.22*RATE)
y[delay:]+=.08*y[:-delay].copy()
y*=np.clip(np.arange(N)/(RATE*.8),0,1).astype(np.float32)
y*=np.clip((N-np.arange(N))/(RATE*1.4),0,1).astype(np.float32)
peak=float(np.max(np.abs(y)))
if peak>.80:y*=.80/peak
OUT.parent.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    wavfile=Path(tmp)/'motif.wav'
    with wave.open(str(wavfile),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE)
        w.writeframes((y*32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(wavfile),
                    '-c:a','libvorbis','-q:a','3',str(OUT)],check=True)
print('PASS:',OUT.name,OUT.stat().st_size,'bytes original music')
