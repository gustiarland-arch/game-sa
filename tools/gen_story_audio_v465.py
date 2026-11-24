#!/usr/bin/env python3
"""Original instrumental 24-second loop for the second conversation after the storm.
Simple new synth motif, deterministic, no external recordings or copyrighted melody.
"""
from pathlib import Path
import subprocess, wave, math
import numpy as np
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'android/assets/audio/music/cinema_gallery_repair.ogg'
OUT.parent.mkdir(parents=True,exist_ok=True)
rate=22050; length=24
notes=[(0,0.6,262),(0.75,0.6,294),(1.5,1.3,349),(3,0.62,330),(3.75,0.62,294),
       (4.5,1.2,262),(6,0.65,220),(6.75,0.65,262),(7.5,1.1,330),
       (9,0.65,294),(9.75,0.65,349),(10.5,1.15,392),
       (12,0.65,349),(12.75,0.65,330),(13.5,1.25,294),
       (15,0.65,262),(15.75,0.65,294),(16.5,1.25,349),
       (18,0.65,392),(18.75,0.65,349),(19.5,1.2,330),
       (21,0.65,294),(21.75,0.65,262),(22.5,1.1,262)]
samples=np.zeros(rate*length,dtype=np.float64)
for start,duration,freq in notes:
 i=int(start*rate); n=min(int(duration*rate),len(samples)-i)
 t=np.arange(n,dtype=np.float64)/rate
 env=np.minimum(1,t/.035)*np.minimum(1,np.maximum(0,(duration-t)/.22))*np.exp(-.5*t)
 carrier=np.sin(t*2*math.pi*freq)+0.17*np.sin(t*2*math.pi*2*freq)
 samples[i:i+n]+=.12*env*carrier
for start,chord in [(0,(131,196,262)),(3,(147,220,294)),(6,(110,165,220)),(9,(147,196,294)),
                    (12,(131,196,262)),(15,(147,220,294)),(18,(110,165,220)),(21,(131,196,262))]:
 i=int(start*rate);n=min(int(2.95*rate),len(samples)-i);t=np.arange(n,dtype=np.float64)/rate
 env=np.minimum(1,t/.22)*np.exp(-.62*t)*np.minimum(1,np.maximum(0,(2.95-t)/.35))
 for freq in chord: samples[i:i+n]+=.012*env*np.sin(t*2*math.pi*freq)
 fade=int(.8*rate);samples[:fade]*=np.linspace(0,1,fade);samples[-fade:]*=np.linspace(1,0,fade)
samples=np.clip(samples,-.45,.45)
wav=OUT.with_suffix('.tmp.wav')
with wave.open(str(wav),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
 w.writeframes((samples*32767).astype('<i2').tobytes())
try:
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','3',str(OUT)],check=True,timeout=25)
finally:wav.unlink(missing_ok=True)
print('Generated original v4.6.5 reconciliation soundtrack:',OUT,OUT.stat().st_size,'bytes')
