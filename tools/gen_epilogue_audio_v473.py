#!/usr/bin/env python3
"""Two original royalty-free instrumental stems and paper foley, generated without samples."""
from pathlib import Path
import wave,subprocess,tempfile
import numpy as np
R=Path(__file__).resolve().parents[1];M=R/'android/assets/audio/music';S=R/'android/assets/audio/sfx';M.mkdir(parents=True,exist_ok=True);S.mkdir(parents=True,exist_ok=True)
SR=22050
def wav(path,s):
 with wave.open(str(path),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(s,-.90,.90)*32767).astype('<i2').tobytes())
def score(name,progression,dur=32):
 out=np.zeros(int(dur*SR),np.float32)
 for i,(f,g,h) in enumerate(progression):
  a=int(i*3.75*SR);n=min(int(5.3*SR),len(out)-a)
  if n<1:break
  t=np.arange(n,dtype=np.float32)/SR;env=np.minimum(1,t/.30)*np.minimum(1,(5.3-t)/.94)*np.exp(-t*.16)
  chord=sum(.019*np.sin(2*np.pi*v*t+0.042*np.sin(2*np.pi*3*t)) for v in (f,g,h))
  bell=.014*np.sin(2*np.pi*(2*h)*t)*np.exp(-t*1.6)
  out[a:a+n]+=(chord+bell+.007*np.sin(2*np.pi*f/2*t))*env
 t=np.arange(len(out))/SR;out*=np.minimum(1,t/1.6)*np.minimum(1,(dur-t)/2.0)
 with tempfile.TemporaryDirectory() as tmp:
  f=Path(tmp)/'src.wav';wav(f,out)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(f),'-c:a','libvorbis','-q:a','3',str(M/(name+'.ogg'))],check=True)
 print('generated',name)
score('cinema_homecoming_v473',[(196,246.94,293.66),(174.61,220,261.63),(164.81,196,246.94),(174.61,220,261.63),(196,246.94,293.66),(220,261.63,329.63),(196,246.94,293.66),(174.61,220,261.63)])
score('cinema_dual_letters_v473',[(261.63,329.63,392),(293.66,349.23,440),(329.63,392,493.88),(293.66,349.23,440),(261.63,329.63,392),(246.94,293.66,369.99),(220,261.63,329.63),(261.63,329.63,392)])
t=np.arange(SR)/SR;foley=.013*np.sin(2*np.pi*(110+350*t)*t)*np.exp(-8*t)+.011*np.sin(2*np.pi*170*t)*np.exp(-13*t)
wav(S/'v473_letter_fold.wav',foley*np.minimum(1,t/.005))
print('PASS: 2 original OGG tracks and paper SFX')
