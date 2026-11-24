#!/usr/bin/env python3
"""Original procedural background cues and SFX for OLU v5.0.
Build-only tool; produces offline OGG/WAV assets. Requires numpy/scipy/ffmpeg.
All melodies are original algorithmic phrases, not samples from existing music.
"""
import math,subprocess,tempfile,random,wave
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt
R=Path(__file__).resolve().parents[1]
BASE=R/'android/assets/audio'
SR=22050

def hz(m):return 440.*2**((m-69)/12)
def tone(m,dur,kind='bell'):
    n=max(1,int(SR*dur));t=np.arange(n,dtype=np.float32)/SR;freq=hz(m)
    if kind=='bell':
        x=np.sin(2*np.pi*freq*t)*np.exp(-2.4*t)
        x+=.21*np.sin(2*np.pi*(freq*2.006)*t)*np.exp(-5.2*t)
        x+=.12*np.sin(2*np.pi*(freq*3.011)*t)*np.exp(-8.0*t)
    elif kind=='pad':
        x=(.58*np.sin(2*np.pi*freq*t)+.22*np.sin(2*np.pi*freq*1.0037*t)
           +.12*np.sin(2*np.pi*freq*2*t))
        x*=np.minimum(1,t/.95)*np.minimum(1,(dur-t)/1.1)
    else:
        x=np.sin(2*np.pi*freq*t)*np.exp(-3*t)
    fade=min(int(SR*.02),n//2)
    if fade>0:x[:fade]*=np.linspace(0,1,fade);x[-fade:]*=np.linspace(1,0,fade)
    return x.astype(np.float32)

def write_wav(path,data):
    samples=np.int16(np.clip(data,-1,1)*32767)
    with wave.open(str(path),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes(samples.tobytes())

def ogg(id,chords,melody,bpm=82,barcount=16):
    beat=60/bpm;bar=beat*4;total=int(bar*barcount*SR)
    out=np.zeros(total,dtype=np.float32)
    def add(note,start,duration,gain,kind):
        if start>=total/SR:return
        part=tone(note,duration,kind);a=int(start*SR);b=min(total,a+len(part))
        out[a:b]+=gain*part[:b-a]
    for k in range(barcount):
        ch=chords[k%len(chords)];ts=k*bar
        for note in ch: add(note-12,ts,bar*.95,.048,'pad')
        for i,n in enumerate(ch):add(n,ts+i*beat*.5,beat*1.5,.095,'bell')
        # distinct companion melody in upper register
        for j in range(4):
            idx=(k+j*3)%len(melody)
            if (k+j)%5 != 0:add(melody[idx],ts+j*beat,beat*.8,.072,'bell')
    # subtle wide-tap delay and mild diffusion without extra runtime complexity
    out0=out.copy()
    for delay,gain in ((.22,.15),(.43,.12),(.71,.07)):
        d=int(delay*SR);out[d:]+=out0[:-d]*gain
    tail=np.minimum(1,np.arange(total)/float(SR*1.4))*np.minimum(1,np.arange(total)[::-1]/float(SR*1.8))
    out*=tail.astype(np.float32)
    out/=max(1,np.max(np.abs(out))/.76)
    with tempfile.TemporaryDirectory() as temp:
        tmp=Path(temp)/'mix.wav';write_wav(tmp,out)
        target=BASE/'music'/f'{id}.ogg'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-c:a','libvorbis','-q:a','5',str(target)],check=True)
    return str(target)

def atmosphere(id,seed=1):
    r=np.random.default_rng(seed)
    t=np.arange(SR*25,dtype=np.float32)/SR
    noise=r.normal(0,.33,len(t)).astype(np.float32)
    low=sosfilt(butter(3,650,fs=SR,output='sos'),noise).astype(np.float32)
    out=.28*low*(.62+.38*np.sin(t*.26)**2)
    for j in range(11):
        start=1+j*2.12
        n=r.integers(74,85);idx=int(start*SR)
        a=tone(int(n),1.9,'bell')*.035
        if idx+len(a)<len(out):out[idx:idx+len(a)]+=a
    out*=np.minimum(1,t/1.5)*np.minimum(1,t[::-1]/1.5)
    with tempfile.TemporaryDirectory() as temp:
        tmp=Path(temp)/'ambient.wav';write_wav(tmp,out)
        target=BASE/'ambience'/f'{id}.ogg'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(tmp),'-c:a','libvorbis','-q:a','4',str(target)],check=True)
    return str(target)

def sfx(id,typ,seed):
    r=np.random.default_rng(seed)
    length={'foot':.22,'step':.6,'wind':1.7,'chime':1.25,'reveal':1.6}[typ]
    n=int(SR*length); t=np.arange(n,dtype=np.float32)/SR
    if typ=='foot':
        noise=r.normal(0,.28,n).astype(np.float32)
        out=sosfilt(butter(2,1500,fs=SR,output='sos'),noise)*np.exp(-t*27)
        out+=.035*np.sin(2*np.pi*126*t)*np.exp(-t*38)
    elif typ=='step':
        out=.16*np.sin(2*np.pi*(265-110*t)*t)*np.exp(-t*9)
        out+=.07*np.sin(2*np.pi*440*t)*np.exp(-t*14)
    elif typ=='wind':
        noise=r.normal(0,.20,n).astype(np.float32)
        out=sosfilt(butter(2,750,fs=SR,output='sos'),noise)*np.sin(t*2.2)**2
    elif typ=='chime':
        out=tone(82,length,'bell')*.42+tone(89,length,'bell')*.14
    else:
        out=np.zeros(n,dtype=np.float32)
        for note,start in ((74,0),(78,.18),(81,.39),(86,.64)):
            idx=int(SR*start);part=tone(note,length-start,'bell')*.3;out[idx:idx+len(part)]+=part
    out*=np.minimum(1,t/.015)*np.minimum(1,t[::-1]/.07)
    target=BASE/'sfx'/f'{id}.wav';write_wav(target,out);return str(target)

def main():
    (BASE/'music').mkdir(parents=True,exist_ok=True)
    pieces={
      'v50_plaza_ascent': ([[60,64,67,71],[57,60,64,69],[53,57,60,64],[55,60,62,67]],[72,74,76,79,77,76,74,72],82),
      'v50_rain_reflections': ([[62,65,69,72],[58,62,65,69],[53,57,60,64],[60,64,67,74]],[74,72,69,67,65,69,72,74],73),
      'v50_starlit_steps': ([[64,68,71,76],[59,64,66,71],[61,64,68,73],[57,61,64,69]],[76,78,80,83,85,83,80,78],78),
      'v50_tomorrow_horizon': ([[55,59,62,66],[54,57,62,66],[52,55,59,64],[48,52,55,59]],[74,71,69,67,69,71,74,76],75),
      'v50_cafe_highlight': ([[65,69,72,76],[60,64,67,72],[62,65,69,74],[58,62,65,69]],[77,76,72,69,72,74,76,77],90),
    }
    for id,(ch,notes,bpm) in pieces.items():print('SCORE',ogg(id,ch,notes,bpm))
    for name,seed in [('v50_highland_breeze',5),('v50_memory_air',11)]:print('AMBIENCE',atmosphere(name,seed))
    for id,kind,seed in [('v50_stair_foot','foot',1),('v50_stair_enter','step',4),('v50_view_wind','wind',6),('v50_memory_shimmer','chime',8),('v50_panoramic_reveal','reveal',3)]:print('SFX',sfx(id,kind,seed))
if __name__=='__main__':main()
