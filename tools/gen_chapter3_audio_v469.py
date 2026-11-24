#!/usr/bin/env python3
"""Small original C03 cinematic scores + soft pencil SFX. Generated offline."""
import wave,tempfile,subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'android/assets/audio';SR=22050

def melody(file,notes,duration=24.4):
    n=int(SR*duration);a=np.zeros(n,np.float32)
    for i,(freq,bass) in enumerate(notes):
        start=int(i*3.1*SR);length=min(int(3.0*SR),n-start)
        if length<1:continue
        t=np.arange(length,dtype=np.float32)/SR
        envelope=np.minimum(1,t/.11)*np.minimum(1,(3-t)/.8)*np.exp(-t/6)
        for f,amp in ((freq,.068),(freq*1.5,.017),(bass,.05),(bass/2,.024)):
            a[start:start+length]+=amp*np.sin(2*np.pi*f*t)*envelope
    # short original, not a recording or imitation of any commercial soundtrack
    fade=np.minimum(1,np.arange(n,dtype=np.float32)/(SR*.6))*np.minimum(1,(n-np.arange(n,dtype=np.float32))/(SR*1.7))
    a*=fade
    with tempfile.TemporaryDirectory() as temp:
        wav=Path(temp)/'track.wav'
        with wave.open(str(wav),'wb') as w:
            w.setframerate(SR);w.setnchannels(1);w.setsampwidth(2)
            w.writeframes((np.clip(a,-.85,.85)*32767).astype('<i2').tobytes())
        out=OUT/'music'/(file+'.ogg');out.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(wav),'-c:a','libvorbis','-q:a','3',str(out)],check=True)
    return out

melody('cinema_small_things_v469',[(293.66,146.83),(349.23,174.61),(329.63,164.81),(261.63,130.81),
(293.66,146.83),(392.0,196.0),(349.23,174.61),(329.63,164.81)])
melody('cinema_gallery_promise_v469',[(261.63,130.81),(329.63,164.81),(349.23,174.61),(440.0,220.0),
(392.0,196.0),(329.63,164.81),(293.66,146.83),(261.63,130.81)])
n=int(.65*SR);t=np.arange(n,dtype=np.float32)/SR
scratch=.04*np.sin(2*np.pi*(810*t+90*t*t))*np.exp(-t*8)+.018*np.sin(2*np.pi*420*t)*np.exp(-t*11)
scratch*=np.minimum(1,t/.015)
out=OUT/'sfx/v469_pencil.wav';out.parent.mkdir(parents=True,exist_ok=True)
with wave.open(str(out),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
 w.writeframes((np.clip(scratch,-1,1)*32767).astype('<i2').tobytes())
print('PASS: 2 original OGG/Vorbis themes + 1 mono pencil SFX')
