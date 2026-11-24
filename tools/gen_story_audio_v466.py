#!/usr/bin/env python3
"""Generate an original gentle instrumental cue for the optional final letters.

No recorded commercial music or third-party samples. Requires NumPy and ffmpeg
at authoring time; the shipped Android APK just reads the generated .ogg asset.
"""
from pathlib import Path
import numpy as np, tempfile, wave, subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'android/assets/audio/music/cinema_letter_tomorrow.ogg'
OUT.parent.mkdir(parents=True,exist_ok=True)
RATE=24000
SEC=28.8
N=int(RATE*SEC)
y=np.zeros(N,dtype=np.float32)

# Original four-chord sequence, with distinct melodic contour and bell-like decay.
chords=[(220.0,261.6256,329.6276),(174.6141,220.0,293.6648),
        (196.0,246.9417,293.6648),(164.8138,220.0,261.6256)]
melody=[329.63,349.23,392.0,329.63,293.66,261.63,293.66,329.63,
        440.0,392.0,349.23,329.63,293.66,261.63,246.94,261.63]

def add_note(freq,start,dur,volume,kind='bell'):
    i=int(start*RATE); length=min(int(dur*RATE),N-i)
    if length<=0:return
    t=np.arange(length,dtype=np.float32)/RATE
    attack=np.minimum(1,t/0.06)
    release=np.minimum(1,np.maximum(0,(dur-t))/0.23)
    decay=np.exp(-1.5*t/max(0.1,dur))
    envelope=attack*release*decay
    if kind=='bell':
        tone=np.sin(2*np.pi*freq*t)+.25*np.sin(2*np.pi*freq*2*t)+.10*np.sin(2*np.pi*freq*3*t)
    else:
        tone=np.sin(2*np.pi*freq*t)+.12*np.sin(2*np.pi*freq*2*t)
    y[i:i+length]+=envelope*tone*volume

for bar,ch in enumerate(chords*2):
    t0=bar*3.6
    for f in ch:
        add_note(f/2,t0,3.4,.038,'pad')
        add_note(f,t0+.12,2.5,.025,'pad')
    for k in range(2):
        f=melody[(2*bar+k)%len(melody)]
        add_note(f,t0+.25+k*1.7,1.9,.076)

# Intentional quiet pauses, small stereo-compatible room echo, and gentle ending.
delay=int(.20*RATE)
y[delay:]+=.10*y[:-delay].copy()
fadein=np.clip(np.arange(N,dtype=np.float32)/(RATE*.8),0,1)
fadeout=np.clip((N-np.arange(N,dtype=np.float32))/(RATE*1.4),0,1)
y*=fadein*fadeout
peak=float(np.max(np.abs(y)))
if peak>.72:y*=.72/peak
with tempfile.TemporaryDirectory() as t:
    wavfile=Path(t)/'original.wav'
    with wave.open(str(wavfile),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE)
        f.writeframes((y*32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wavfile),
                    '-c:a','libvorbis','-q:a','3',str(OUT)],check=True)
print('Created original story cue:',OUT,OUT.stat().st_size,'bytes')
