#!/usr/bin/env python3
"""Original emotional Chapter6 synthesised instrumental cues (offline, no copyrighted samples)."""
from pathlib import Path
import wave,tempfile,subprocess
import numpy as np
R=Path(__file__).resolve().parents[1];M=R/'android/assets/audio/music';S=R/'android/assets/audio/sfx';M.mkdir(parents=True,exist_ok=True);S.mkdir(parents=True,exist_ok=True)
SR=22050
def write(path,data):
 with wave.open(str(path),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes((np.clip(data,-.93,.93)*32767).astype('<i2').tobytes())
def render(name,melody,duration=30):
 length=int(SR*duration);out=np.zeros(length,np.float32)
 for i,(root,third,fifth) in enumerate(melody):
  start=int(i*3.4*SR);n=min(int(4.0*SR),length-start)
  if n<=0:continue
  t=np.arange(n,dtype=np.float32)/SR
  env=np.minimum(1,t/.22)*np.minimum(1,(4.0-t)/.75)*np.exp(-t*.055)
  chord=sum(np.sin(2*np.pi*f*t+0.05*np.sin(2*np.pi*4*t))*.016 for f in (root,third,fifth))
  music=chord+(.035*np.sin(2*np.pi*(2*root)*t)*np.exp(-t*1.1))+.010*np.sin(2*np.pi*root/2*t)
  out[start:start+n] += music*env
 t=np.arange(length,dtype=np.float32)/SR
 out*=np.minimum(1,t/1.1)*np.minimum(1,(duration-t)/1.7)
 with tempfile.TemporaryDirectory() as tmp:
  f=Path(tmp)/'input.wav';write(f,out)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(f),'-c:a','libvorbis','-q:a','3',str(M/(name+'.ogg'))],check=True)
 print('generated',name)
render('cinema_hall_v472',[(196,246.94,293.66),(174.61,220,261.63),(164.81,196,246.94),(196,246.94,293.66), (220,261.63,329.63),(196,246.94,293.66),(174.61,220,261.63),(164.81,196,246.94)])
render('cinema_unwritten_v472',[(261.63,329.63,392),(293.66,349.23,440),(329.63,392,493.88),(293.66,349.23,440),(261.63,329.63,392),(220,261.63,329.63),(261.63,329.63,392),(293.66,349.23,440)])
n=SR;t=np.arange(n,dtype=np.float32)/SR
sfx=(.055*np.sin(2*np.pi*587.33*t)+.031*np.sin(2*np.pi*880*t)+.013*np.sin(2*np.pi*1174.66*t))*np.exp(-5*t)
write(S/'v472_memory_glint.wav',sfx*np.minimum(1,t/.012));print('generated v472_memory_glint')
