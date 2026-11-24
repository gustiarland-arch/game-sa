#!/usr/bin/env python3
"""Completely original subdued cinematic themes and one soft paper sound, offline."""
from pathlib import Path
import numpy as np, wave, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1];MUSIC=ROOT/'android/assets/audio/music';SFX=ROOT/'android/assets/audio/sfx'
MUSIC.mkdir(parents=True,exist_ok=True);SFX.mkdir(parents=True,exist_ok=True)
SR=22050
def write_wav(path,signal):
 with wave.open(str(path),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR)
  f.writeframes((np.clip(signal,-.88,.88)*32767).astype('<i2').tobytes())
def compose(name,roots,mins=28):
 length=SR*mins; signal=np.zeros(length,np.float32)
 for i,(top,bass) in enumerate(roots):
  st=int(i*3.55*SR); n=min(int(3.85*SR),length-st)
  if n<=0:break
  t=np.arange(n,dtype=np.float32)/SR
  attack=np.minimum(1,t/.25);release=np.minimum(1,(3.85-t)/1.6)
  envelope=attack*release*np.exp(-t/9)
  # slow, unfussy original harmony; acoustic-like partials, no borrowed melody.
  for freq,amp in [(top,.054),(top*2,.006),(top*1.5,.012),(bass,.033),(bass/2,.020)]:
   signal[st:st+n]+=np.sin(2*np.pi*freq*t).astype(np.float32)*amp*envelope
 fade=np.minimum(1,np.arange(length,dtype=np.float32)/(SR*1.2))*np.minimum(1,(length-np.arange(length,dtype=np.float32))/(SR*2.3))
 signal*=fade
 with tempfile.TemporaryDirectory() as td:
  tmp=Path(td)/'input.wav';write_wav(tmp,signal)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-c:a','libvorbis','-q:a','3',str(MUSIC/(name+'.ogg'))],check=True)
compose('cinema_empty_seat_v470',[(220,110),(246.94,123.47),(196,98),(174.61,87.31),(220,110),(164.81,82.41),(196,98),(146.83,73.42)])
compose('cinema_rain_five_lights_v470',[(196,98),(261.63,130.81),(293.66,146.83),(246.94,123.47),(329.63,164.81),(293.66,146.83),(392,196),(329.63,164.81)])
compose('cinema_listen_again_v470',[(261.63,130.81),(329.63,164.81),(349.23,174.61),(293.66,146.83),(392,196),(349.23,174.61),(329.63,164.81),(261.63,130.81)])
n=SR; t=np.arange(n,dtype=np.float32)/SR
v=.03*np.sin(2*np.pi*(360*t+130*t*t))*np.exp(-8*t)+.012*np.sin(2*np.pi*670*t)*np.exp(-11*t)
write_wav(SFX/'v470_paper_note.wav',v*np.minimum(1,t/.02))
print('PASS: 3 original Vorbis OGG tracks (28s each) + 1 original WAV sound')
