"""Mix the game's own audio files following the cue log the running game produced."""
import subprocess, sys, numpy as np, collections
A=sys.argv[4] if len(sys.argv) > 4 else "android/assets/"
SR=44100; FPS=30
log=[l.rstrip('\n').split('\t') for l in open(sys.argv[1])]
total=float(sys.argv[3])
out=np.zeros(int(total*SR)+SR)
cache={}
def load(path):
    if path not in cache:
        raw=subprocess.run(['ffmpeg','-v','error','-i',A.rstrip('/')+'/'+path,'-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True,check=True).stdout
        cache[path]=np.frombuffer(raw,dtype=np.float32).astype(np.float64)
    return cache[path]
LEG={'town','memory','cafe','rain','night','star','tender','game'}
def music_path(i): return 'audio/music/%s%s.ogg'%(i,'_theme' if i in LEG else '')
segs=[(int(f),n) for f,b,n,v in log if b=='segment']
bounds=[f for f,_ in segs]+[int(total*FPS)]
for si,(f0,name) in enumerate(segs):
    f1=bounds[si+1]
    cues=[r for r in log if f0<=int(r[0])<f1]
    for bus,rate in (('music',0.75),('ambience',0.45)):
        ids=[r for r in cues if r[1]==bus and r[2] not in ('null','')]
        if not ids: continue
        i,vol=ids[-1][2],float(ids[-1][3])
        src=load(music_path(i) if bus=='music' else 'audio/ambience/%s.ogg'%i)
        n=int((f1-f0)/FPS*SR); a=int(f0/FPS*SR)
        loop=np.resize(src,n)
        t=np.arange(n)/SR
        env=np.minimum(1,t*rate)*np.minimum(1,(n/SR-t)/0.25)
        out[a:a+n]+=loop*env*vol
        print(name,bus,i,vol)
    for f,bus,i,v in cues:
        if bus!='sfx': continue
        s=load('audio/sfx/%s.wav'%i)*float(v); a=int(int(f)/FPS*SR)
        out[a:a+len(s)]+=s[:len(out)-a]
out=out[:int(total*SR)]
peak=np.max(np.abs(out)); print('peak',peak)
out=np.tanh(out*1.1)/np.tanh(1.1) if peak>0.95 else out
open(sys.argv[2],'wb').write(out.astype(np.float32).tobytes())
