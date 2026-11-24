#!/usr/bin/env python3
"""Composed, synthesized original soundtrack loops for five story milestones.
Reproducible audio source (no external recordings, CC samples, internet, or fonts).
Output Vorbis stereo/44.1kHz. See art_source/story_v480/scorebook.json.
"""
from pathlib import Path
import json, math, numpy as np, subprocess
R=Path(__file__).resolve().parents[1]
OUT=R/'android/assets/audio/music';OUT.mkdir(parents=True,exist_ok=True)
F=44100
SCORES={
 'score_empty_chair_v480':{'bpm':72,'chords':[[62,65,69],[58,62,65],[60,64,67],[60,64,67]],'melody':[74,72,69,67,69,72,74,69,70,69,65,62,65,69,67,65],'texture':'felt','title':'Kursi Yang Menunggu'},
 'score_rain_resolve_v480':{'bpm':68,'chords':[[55,58,62],[56,60,63],[58,62,65],[53,57,60]],'melody':[70,67,65,62,65,67,70,72,74,72,70,67,69,70,72,74],'texture':'rain','title':'Kita Belajar Mendengar'},
 'score_quiet_truth_v480':{'bpm':76,'chords':[[52,55,59],[48,52,55],[55,59,62],[50,54,57]],'melody':[76,74,71,67,71,74,76,79,77,74,71,69,71,74,79,76],'texture':'bells','title':'Dua Suara Di Jembatan'},
 'score_open_page_v480':{'bpm':70,'chords':[[60,64,67],[55,59,62],[57,60,64],[53,57,60]],'melody':[72,76,79,76,74,72,76,79,81,79,76,74,72,74,76,79],'texture':'future','title':'Halaman Yang Belum Tertulis'},
 'score_lake_coda_v480':{'bpm':66,'chords':[[53,57,60],[60,64,67],[57,60,64],[58,62,65]],'melody':[77,76,72,69,72,76,77,79,81,79,77,76,74,72,76,77],'texture':'warm','title':'Masih Banyak Hari'},
}
def hz(note):return 440.0*2**((note-69)/12)
def make_tone(n,dur,mode):
 t=np.arange(max(1,int(dur*F)),dtype=np.float32)/F
 f=hz(n)
 if mode=='pad':
  sig=.68*np.sin(2*np.pi*f*t)+.20*np.sin(2*np.pi*2*f*t)+.08*np.sin(2*np.pi*3*f*t)
  a=np.minimum(1,t/.65)
  rel=np.minimum(1,(dur-t)/.6)
  env=(a*rel).clip(0,1)
 elif mode=='bell':
  sig=np.sin(2*np.pi*f*t)+.30*np.sin(2*np.pi*2.02*f*t)+.16*np.sin(2*np.pi*3.94*f*t)
  env=np.minimum(1,t/.024)*np.exp(-t/(dur*.60+.15))
 else:
  sig=np.sin(2*np.pi*f*t)+.23*np.sin(2*np.pi*2*f*t)+.1*np.sin(2*np.pi*3*f*t)
  env=np.minimum(1,t/.012)*np.exp(-t/(dur*.62+.3))
  env*=np.minimum(1,(dur-t)/.16).clip(0,1)
 return sig*env

def make(name,cfg):
 beats=60/cfg['bpm'];bar=4*beats;duration=bar*24
 n=int(duration*F);L=np.zeros(n,dtype=np.float32); Rr=np.zeros(n,dtype=np.float32)
 def note(midi,start,dur,amp=.1,kind='felt',pan=0.0):
  a=int(start*F)
  if a>=n:return
  tone=make_tone(midi,min(dur,duration-start),kind)*amp
  end=min(a+len(tone),n);tone=tone[:end-a]
  L[a:end]+=tone*np.sqrt((1-pan)/2);Rr[a:end]+=tone*np.sqrt((1+pan)/2)
 for baridx in range(24):
  root=cfg['chords'][baridx%4]
  for j,num in enumerate(root):note(num-12,baridx*bar,bar*.95,.053,'pad',(-.40+j*.40))
  # Low plucked bass and delayed felt arpeggios, unique foreground motif.
  note(root[0]-24,baridx*bar,bar*.6,.14,'felt',-.17)
  for sub in range(8):
   midi=root[sub%3] + (12 if sub in (2,6) else 0)
   note(midi,baridx*bar+sub*beats*.5,beats*.76,.067,'bell' if cfg['texture'] in ('bells','future') else 'felt',-.43 if sub%2 else .41)
  phrase=cfg['melody']
  for j in range(4):
   if baridx%2==0 and j==3 and cfg['texture']=='felt':continue
   m=phrase[(baridx*4+j)%len(phrase)]
   note(m,baridx*bar+j*beats,beats*1.18,.078,'bell' if cfg['texture'] in ('bells','future') else 'felt',.10)
  if cfg['texture']=='rain':
   # gentle sparse notes evoke water without a potentially irritating noise loop
   for j in (1,3):note(root[0]+24,baridx*bar+j*beats,beats*.8,.026,'bell',.52)
 # in-memory room reverb / soft reflections
 for delay,atten in ((.19,.18),(.41,.13),(.66,.08)):
  sh=int(delay*F)
  L[sh:]+=Rr[:-sh]*atten;Rr[sh:]+=L[:-sh]*atten*.85
 # Very short endpoint fades avoid audible clicks in the offline loop.
 fadein=int(F*.1);fadeout=int(F*.8)
 L[:fadein]*=np.linspace(0,1,fadein);Rr[:fadein]*=np.linspace(0,1,fadein)
 L[-fadeout:]*=np.linspace(1,0,fadeout);Rr[-fadeout:]*=np.linspace(1,0,fadeout)
 peak=max(np.max(np.abs(L)),np.max(np.abs(Rr)),1e-6)
 aud=np.column_stack((L,Rr))*min(1,.81/peak)
 proc=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','f32le','-ar',str(F),'-ac','2','-i','pipe:0','-c:a','libvorbis','-qscale:a','5',str(OUT/(name+'.ogg'))],input=aud.astype('<f4',copy=False).tobytes(),capture_output=True)
 if proc.returncode:raise RuntimeError(proc.stderr.decode()[:500])
 return round(duration,1)

def main():
 for name,cfg in SCORES.items():
  dur=make(name,cfg);print('AUDIO',name, 'seconds',dur, 'bytes',(OUT/(name+'.ogg')).stat().st_size,flush=True)
 src=R/'art_source/story_v480';src.mkdir(exist_ok=True,parents=True)
 (src/'scorebook.json').write_text(json.dumps({'note':'Original synthesized soundtrack; modify tools/gen_cinematic_scores_v480.py to edit melody, tempo or instruments.','scores':SCORES},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
