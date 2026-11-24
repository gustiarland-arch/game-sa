#!/usr/bin/env python3
"""Original, simple instrumental cue for The Empty Seat. No borrowed melody or samples.
Generated deterministically as raw WAV then encoded to Ogg Vorbis offline via ffmpeg.
"""
from pathlib import Path
import math, wave, subprocess
import numpy as np

OUT=Path(__file__).resolve().parents[1]/'android/assets/audio/music/cinema_gallery_empty.ogg'
RATE=22050
DURATION=24
count=RATE*DURATION
t=np.arange(count,dtype=np.float32)/RATE
samples=np.zeros(count,dtype=np.float32)
# Original 24-second, 3/4 timing. A simple wistful motif on an electric piano-like tone.
melody=[(0,0.66,330),(.75,.62,392),(1.5,1.1,440),(3.0,.66,392),
        (3.75,.62,330),(4.5,1.1,294),(6.0,.66,262),(6.75,.62,330),
        (7.5,1.1,392),(9.0,.66,349),(9.75,.62,294),(10.5,1.1,262),
        (12.0,.66,330),(12.75,.62,392),(13.5,1.1,523),(15.0,.66,440),
        (15.75,.62,392),(16.5,1.1,330),(18.0,.66,294),(18.75,.62,330),
        (19.5,1.1,392),(21.0,.66,349),(21.75,.62,330),(22.5,.9,262)]
# Authentic synthesized tones; no loops of copyrighted or public samples.
for start,length,freq in melody:
    i=int(start*RATE); n=min(int(length*RATE),count-i)
    tt=np.arange(n,dtype=np.float32)/RATE
    attack=np.minimum(1.0,tt/.018)
    release=np.minimum(1.,(length-tt)/.19)
    envelope=attack*np.maximum(0,release)*np.exp(-tt*.65)
    tone=(np.sin(2*np.pi*freq*tt)+.22*np.sin(2*np.pi*freq*2*tt)+.08*np.sin(2*np.pi*freq*3*tt))
    samples[i:i+n]+=0.10*envelope*tone
# Arpeggiated chords under melody in low register, intentional room for narrative silence.
chords=[(0,(196,247,294)),(3,(175,220,262)),(6,(164,196,262)),(9,(147,196,247)),
        (12,(196,247,294)),(15,(175,220,262)),(18,(164,220,262)),(21,(147,196,262))]
for start,freqs in chords:
 for freq in freqs:
  i=int(start*RATE);n=min(int(2.8*RATE),count-i)
  tt=np.arange(n,dtype=np.float32)/RATE
  env=np.minimum(1.0,tt/.2)*np.exp(-tt*.64)*np.maximum(0,np.minimum(1.0,(2.8-tt)/.24))
  samples[i:i+n]+=.013*env*np.sin(2*np.pi*freq*tt)
# Subtle breath of atmosphere, not synthetic percussion.
rng=np.random.default_rng(464)
noise=rng.normal(0,.0009,count).astype(np.float32)
noise=np.convolve(noise,np.ones(64)/64,mode='same')
samples+=noise
# Equal-power-ish smooth beginning/end for non-jarring looping.
fades=int(.95*RATE)
samples[:fades]*=np.linspace(0,1,fades,dtype=np.float32)
samples[-fades:]*=np.linspace(1,0,fades,dtype=np.float32)
samples=np.clip(samples,-.45,.45)
tmp=OUT.with_suffix('.tmp.wav')
OUT.parent.mkdir(parents=True,exist_ok=True)
with wave.open(str(tmp),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE)
 w.writeframes((samples*32767).astype('<i2').tobytes())
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-c:a','libvorbis','-q:a','3',str(OUT)]
try:
    subprocess.run(cmd,check=True,timeout=30)
finally:
    tmp.unlink(missing_ok=True)
print('Original gallery cinematic music:',OUT,OUT.stat().st_size,'bytes')
