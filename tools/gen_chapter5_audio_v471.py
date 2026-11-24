#!/usr/bin/env python3
"""Three self-composed quiet original cue beds and one original chime, offline OGG/WAV."""
from pathlib import Path
import numpy as np, tempfile, wave, subprocess
R=Path(__file__).resolve().parents[1];M=R/'android/assets/audio/music';S=R/'android/assets/audio/sfx';M.mkdir(parents=True,exist_ok=True);S.mkdir(parents=True,exist_ok=True)
SR=22050
def write_wav(path,data):
 with wave.open(str(path),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes((np.clip(data,-.8,.8)*32767).astype('<i2').tobytes())
def score(id,notes):
 L=SR*26;out=np.zeros(L,np.float32)
 for j,(f,low) in enumerate(notes):
  st=int(j*3.2*SR); n=min(int(3.8*SR),L-st)
  t=np.arange(n,dtype=np.float32)/SR;env=np.minimum(1,t/.28)*np.minimum(1,(3.8-t)/.9)*np.exp(-t*.1)
  tone=(np.sin(2*np.pi*f*t)*.043+np.sin(2*np.pi*1.5*f*t)*.010+np.sin(2*np.pi*low*t)*.032+np.sin(2*np.pi*.5*low*t)*.017)
  out[st:st+n]+=tone*env
 t=np.arange(L,dtype=np.float32)/SR
 out*=np.minimum(1,t/.8)*np.minimum(1,(26-t)/2)
 with tempfile.TemporaryDirectory() as td:
  f=Path(td)/'in.wav';write_wav(f,out)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(f),'-c:a','libvorbis','-q:a','3',str(M/(id+'.ogg'))],check=True)
 print('generated',id+'.ogg')
score('cinema_clockwork_v471',[(196,98),(220,110),(246.94,123.47),(293.66,146.83),(261.63,130.81),(220,110),(196,98),(174.61,87.3)])
score('cinema_two_sides_v471',[(261.63,130.81),(329.63,164.81),(293.66,146.83),(392,196),(349.23,174.61),(329.63,164.81),(293.66,146.83),(261.63,130.81)])
score('cinema_quiet_reveal_v471',[(174.61,87.3),(196,98),(220,110),(261.63,130.81),(293.66,146.83),(329.63,164.81),(349.23,174.61),(392,196)])
n=SR;t=np.arange(n,dtype=np.float32)/SR
chime=(.044*np.sin(2*np.pi*740*t)+.023*np.sin(2*np.pi*1111*t))*np.exp(-7*t)
write_wav(S/'v471_memory_chime.wav',chime*np.minimum(1,t/.015))
print('generated v471_memory_chime.wav')
