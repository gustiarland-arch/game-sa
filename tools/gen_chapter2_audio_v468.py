#!/usr/bin/env python3
"""Generate original instrumental and photo mystery click, all 100% offline."""
import numpy as np, math, wave, tempfile, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUD=ROOT/'android/assets/audio'
SR=22050; DURATION=27.6; total=int(SR*DURATION)
signal=np.zeros(total,dtype=np.float32)

def add(freq,at,dur,amp):
 start=int(at*SR)
 if start>=total:return
 count=min(int(dur*SR),total-start)
 t=np.arange(count)/SR
 env=np.minimum(t/.07,1)*np.minimum((dur-t)/.46,1)*np.exp(-t/(dur*1.5))
 tone=np.sin(t*2*np.pi*freq)+.15*np.sin(t*2*np.pi*freq*2)+.04*np.sin(t*2*np.pi*freq*3)
 signal[start:start+count]+=amp*env*tone

# 8-bar original soft duet, the same melody with a different delayed answer.
mel=[329.63,392.00,440.00,392.00,349.23,329.63,293.66,261.63]
bass=[164.81,196.00,220.00,196.00,174.61,164.81,146.83,130.81]
for bar in range(8):
 at=bar*3.2
 add(bass[bar]/2,at,3.0,.05)
 add(bass[bar],at+.1,2.65,.027)
 add(mel[bar],at+.24,1.65,.07)
 add(mel[bar]*.74915,at+1.7,1.35,.049)
 if bar>=5:add(mel[bar]*1.4983,at+2.35,.67,.026)
signal[int(.18*SR):]+=.07*signal[:-int(.18*SR)].copy()
signal*=np.minimum(np.arange(total)/(SR*.8),1).astype(np.float32)
signal*=np.minimum((total-np.arange(total))/(SR*1.55),1).astype(np.float32)
maxlevel=float(np.max(np.abs(signal)))
if maxlevel>.83:signal*=.83/maxlevel
with tempfile.TemporaryDirectory() as tmp:
 wav=Path(tmp)/'date.wav'
 with wave.open(str(wav),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes((signal*32767).astype('<i2').tobytes())
 out=AUD/'music/cinema_date_choices_v468.ogg'
 out.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(wav),'-c:a','libvorbis','-q:a','3',str(out)],check=True)
# Soft photobooth hum / glimmer, original synth waveform.
samples=int(SR*1.1)
t=np.arange(samples,dtype=np.float32)/SR
fx=.10*np.sin(2*np.pi*(650*t+300*t*t))*np.exp(-t*6)
fx+=.04*np.sin(2*np.pi*(1050*t-130*t*t))*np.exp(-t*9)
fx*=np.minimum(t/.015,1)
fxout=AUD/'sfx/photo_lantern_v468.wav'
with wave.open(str(fxout),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
 w.writeframes((np.clip(fx,-1,1)*32767).astype('<i2').tobytes())
print('PASS: 27.6s original OGG and 1.1s original SFX WAV',out.stat().st_size,fxout.stat().st_size)
