#!/usr/bin/env python3
"""Generate two original, royalty-free instrumental motifs for Prologue 4.7.4.
Only additive. No third-party recordings or samples. PCM generated in pure code.
"""
from pathlib import Path
import numpy as np,wave,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'android/assets/audio/music';OUT.mkdir(parents=True,exist_ok=True)
RATE=22050

def render(name,bass,melody,seconds,wind=False):
 n=int(RATE*seconds);mix=np.zeros(n,dtype=np.float64)
 def tone(hz,start,duration,amp,velvet=False):
  i=int(start*RATE);m=min(n-i,int(duration*RATE))
  if m<=0:return
  t=np.arange(m)/RATE
  shape=np.minimum(1,t/.08)*np.minimum(1,np.maximum(0,(duration-t))/.46)
  shape*=np.exp(-.33*t)
  sig=np.sin(2*np.pi*hz*t+.003*np.sin(2*np.pi*2.1*t))
  sig+= (.10 if velvet else .24)*np.sin(2*np.pi*2*hz*t)
  mix[i:i+m]+=sig*shape*amp
 for bar in range(8):
  at=bar*2.72
  tone(bass[bar]/2,at,2.5,.056,True)
  tone(bass[bar],at+.05,2.3,.021,True)
  for i in range(3):
   note=melody[(bar*2+i)%len(melody)]*(1.0 if i<2 else 0.74915)
   tone(note,at+.15+i*.73,1.11,.071 if not wind else .053)
  if bar in (2,6):tone(melody[(bar+2)%len(melody)],at+.53,1.9,.035,True)
 # Intricate but quiet delayed echo of the original signal
 delay=int(.17*RATE);mix[delay:]+=.07*mix[:-delay].copy()
 mix*=np.clip(np.arange(n)/(RATE*.7),0,1)*np.clip((n-np.arange(n))/(RATE*1.5),0,1)
 peak=np.max(np.abs(mix));mix=np.clip(mix/max(1,peak/.70),-.95,.95)
 with tempfile.TemporaryDirectory() as tmp:
  file=Path(tmp)/'original.wav'
  with wave.open(str(file),'wb') as w:
   w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes((mix*32767).astype('<i2').tobytes())
  subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(file),'-c:a','libvorbis','-q:a','3',str(OUT/(name+'.ogg'))],check=True)
 print('PASS',name,'original',seconds,'seconds')
render('cinema_prologue_promise_v474',[174.61,196,220,196,174.61,164.81,196,174.61],
 [261.63,293.66,329.63,392.0,349.23,329.63,293.66,261.63,329.63,349.23,392.0,440.0,392.0,329.63,293.66,261.63],23.8)
render('cinema_prologue_memory_v474',[164.81,146.83,174.61,164.81,196,174.61,146.83,164.81],
 [329.63,392.0,349.23,440.0,392.0,349.23,293.66,329.63,349.23,392.0,493.88,440.0,392.0,349.23,329.63,293.66],23.8,True)
