#!/usr/bin/env python3
"""Original procedural soundtrack / ambience / SFX for Arland & Sofia v2.4.
Deterministic, synthesised from scratch; no third-party samples, no API, no copyrighted songs.
This generator intentionally DOES NOT alter v1.2's eight existing *_theme.ogg files.
Requires numpy, ffmpeg; run: python3 tools/gen_soundscape_v24.py android/assets/audio
"""
from pathlib import Path
import json, math, subprocess, sys, tempfile, wave, zlib
import numpy as np

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else 'android/assets/audio')
for d in ('music','ambience','sfx'): (ROOT/d).mkdir(parents=True,exist_ok=True)
SR=22050
TAU=2*np.pi

# Named cues each get their own tempo, scale, instrument palette, phrase and chord progression.
# Styles: 0 music-box, 1 felt piano, 2 chiptune, 3 guitar/pluck, 4 dream pad, 5 bell/flute.
CUES = [
 ('menu_theme',84,0,0,2,'C4'),('home_morning',102,3,0,0,'F3'),('home_evening',77,1,0,1,'D3'),
 ('city_morning',112,3,0,2,'G3'),('city_evening',91,1,0,3,'A3'),('city_night',79,4,1,4,'E3'),
 ('park_blossom',97,5,0,5,'D3'),('park_sunset',76,1,0,6,'F3'),('lake_breeze',88,3,0,7,'C3'),
 ('lake_moon',70,4,1,8,'A3'),('flower_shop',107,0,0,9,'F3'),('cafe_waltz',92,1,0,10,'A3'),
 ('library_whisper',74,1,0,11,'C3'),('arcade_neon',136,2,0,12,'G3'),('neighborhood_day',109,3,0,13,'D3'),
 ('memory_bloom',78,0,1,14,'C3'),('lantern_glow',83,5,0,15,'F3'),('whisper_woods',69,4,1,16,'D3'),
 ('archive_mystery',72,4,1,17,'E3'),('star_road',96,5,0,18,'G3'),('star_village',87,0,0,19,'D3'),
 ('hill_stars',73,4,0,20,'C3'),('crystal_echo',82,5,1,21,'A3'),('eternal_promise',67,1,0,22,'F3'),
 ('rain_lullaby',76,1,1,23,'D3')]

AMBIENTS = [
 'birds_morning','city_day','wind_leaves','park_birds','lake_water','cafe_room','library_room',
 'rain_outdoor','rain_window','night_crickets','forest_wind','magic_chimes','cave_drips','arcade_hum']
SFX = ['step_grass','step_stone','step_wood','door_open','door_close','bell_shop','coin','gift','heart',
       'hug','selfie','highfive','quest_complete','scene_transition','notification','splash','bird_chirp',
       'cat_meow','dog_bark','duck_quack','wind_gust','rain_drop','lantern','page_turn','menu_confirm']

NOTE={'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
def midi(s): return 12*(int(s[-1])+1)+NOTE[s[:-1]]
def freq(n): return 440.0*2**((n-69)/12)
def fade_edges(x,rate=.025):
    k=max(12,int(SR*rate)); k=min(k,len(x)//4)
    if k:
        x[:k]*=np.linspace(0,1,k); x[-k:]*=np.linspace(1,0,k)
    return x

def tone(hz,dur,style,velocity=1.):
    n=max(16,int(dur*SR)); t=np.arange(n,dtype=np.float32)/SR
    phase=TAU*hz*t
    if style==0: # translucent music box
        w=np.sin(phase)+.35*np.sin(phase*2.005)+.15*np.sin(phase*3.95)
        env=np.exp(-3.1*t)*(1-np.exp(-t*260))
    elif style==1: # warm felt piano
        w=np.sin(phase)+.30*np.sin(phase*2.001)+.16*np.sin(phase*3.001)
        env=np.exp(-2.2*t)*(1-np.exp(-t*480))
    elif style==2: # quiet rounded square wave
        w=np.sin(phase)+.27*np.sin(phase*3)+.12*np.sin(phase*5)
        env=np.exp(-1.6*t)*(1-np.exp(-t*250))
    elif style==3: # picked string, layered harmonics
        w=np.sin(phase)+.35*np.sin(phase*2)+.20*np.sin(phase*3)+.11*np.sin(phase*4)
        env=np.exp(-4.0*t)*(1-np.exp(-t*700))
    elif style==4: # breathy glass pad
        vib=1+.002*np.sin(TAU*3.7*t); w=np.sin(phase*vib)+.28*np.sin(phase*1.997)+.10*np.sin(phase*2.99)
        env=np.minimum(1,t*4.0)*np.minimum(1,(dur-t)*3.0)
    else: # flute and bell layers
        vib=.004*np.sin(TAU*5.3*t); w=np.sin(phase+vib)+.17*np.sin(phase*2.76)*np.exp(-t*4)
        env=np.minimum(1,t*27)*np.exp(-1.9*t)
    env*=np.clip((dur-t)/max(.03,min(.2,dur*.2)),0,1)
    return (w*env*velocity).astype(np.float32)

def put(stereo,signal,at,pan=0):
    i=max(0,int(at*SR)); count=min(len(signal),len(stereo)-i)
    if count<=0: return
    l=math.cos((pan+1)*math.pi/4);r=math.sin((pan+1)*math.pi/4)
    stereo[i:i+count,0]+=signal[:count]*l
    stereo[i:i+count,1]+=signal[:count]*r

def encode_ogg(arr,path,quality=2):
    arr=np.asarray(arr,dtype=np.float32)
    maximum=max(.001,float(np.max(np.abs(arr))))
    arr=np.tanh(arr*(0.65/maximum)).astype(np.float32)
    with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
        with wave.open(tmp.name,'wb') as wf:
            wf.setnchannels(2 if arr.ndim==2 else 1);wf.setsampwidth(2);wf.setframerate(SR)
            wf.writeframes((np.clip(arr,-1,1)*32767).astype('<i2').tobytes())
        subprocess.run(['ffmpeg','-y','-nostdin','-loglevel','error','-i',tmp.name,
                        '-c:a','libvorbis','-q:a',str(quality),str(path)],check=True)

def make_song(name,bpm,style,minor,seed,key):
    rng=np.random.default_rng(seed+2400); beat=60.0/bpm
    measures=16; length=measures*4*beat
    buf=np.zeros((int(SR*length),2),dtype=np.float32)
    root=midi(key)
    # Modes and chord movements keep harmonic identity stable while phrase contours vary.
    progression=[0,5,3,4] if not minor else [0,3,5,4]
    degree=[0,2,4,5,7,9,11] if not minor else [0,2,3,5,7,8,10]
    # Shared 4-bar motif changes on the second and final repeats.
    motif=rng.integers(0,7,16)
    for bar in range(measures):
        start=bar*4*beat
        base=root+progression[bar%4]
        third=3 if minor else 4
        chord=[base,base+third,base+7,base+12]
        # Left hand: changing chord voicings & a rolling pattern.
        for b in (0,1.5,2.5):
            index=(int(b*2)+bar)%3
            vel=.12 if style!=4 else .10
            put(buf,tone(freq(chord[index]+12),min(2.3*beat,length-start-b*beat-.01),1,vel),start+b*beat,-.40)
        put(buf,tone(freq(base-12),min(2.5*beat,length-start-.01),4 if style==4 else 1,.27),start,-.48)
        if style in (0,3,5):
            for q in range(8):
                note=chord[(q+bar)%len(chord)]+12
                put(buf,tone(freq(note),.48*beat,3 if style==3 else 0,.10),start+q*.5*beat,.48)
        for tick in range(8):
            if (tick+bar)%4==3 and seed%3!=0: continue
            if bar%4==3 and tick>=6: continue
            pos=start+tick*.5*beat
            # Deliberate variation in every four-bar phrase.
            d=int(motif[(bar%4)*4+(tick//2)%4])
            if (bar//4)%2: d=(d+1)%7
            note=root+degree[d]+12+(12 if (seed+tick)%13==0 else 0)
            dur=.33*beat if tick%2 else .68*beat
            put(buf,tone(freq(note),dur,style,.18 if tick%2 else .26),pos,.33)
        if style==2:  # arcade beat: synth bass + soft percussive chiptune
            for k in (0,2):
                put(buf,tone(58,0.12,2,.18),start+k*beat,0)
            for k in (1,3):
                t=np.arange(int(.09*SR))/SR
                v=rng.normal(0,1,len(t)).astype(np.float32)*np.exp(-t*50)*.06
                put(buf,v,start+k*beat,-.2)
        elif style==3 and bar%2==0:
            for k in range(4): put(buf,tone(freq(root+12+degree[(k+bar)%7]),.20*beat,3,.08),start+(k+.5)*beat,.55)
    # A small stereo echo gives width without large libraries or third-party impulse responses.
    delay=int(.16*SR); buf[delay:,0]+=.085*buf[:-delay,1];buf[delay:,1]+=.085*buf[:-delay,0]
    # Crossfade edges to reduce loop click; original harmony recurs on first bar.
    edge=int(.11*SR);buf[:edge]*=np.linspace(0,1,edge)[:,None];buf[-edge:]*=np.linspace(1,0,edge)[:,None]
    encode_ogg(buf,ROOT/'music'/f'{name}.ogg')
    return round(length,2)

def smooth_noise(rng,n,window):
    raw=rng.normal(0,1,n).astype(np.float32)
    for width in (max(1,window//3),max(1,window//2),max(1,window)):
        raw=(raw+np.roll(raw,width)+np.roll(raw,-width))/3
    return raw

def ambience(name,seed):
    rng=np.random.default_rng(8510+seed);length=12; n=SR*length;t=np.arange(n,dtype=np.float32)/SR
    noise=rng.normal(0,.13,n).astype(np.float32)
    low=smooth_noise(rng,n,150)
    if name in ('rain_outdoor','rain_window'):
        v=(noise*.6+low*.9)*(.65 if name=='rain_window' else 1)
        for q in range(50):
            at=int(rng.uniform(0,length)*SR);L=min(n-at,170)
            if L>0:v[at:at+L]+=(rng.normal(0,.10,L)*np.linspace(1,0,L))
    elif name in ('lake_water','wind_leaves','forest_wind'):
        wave=np.sin(TAU*(.24 if name=='lake_water' else .14)*t)**2
        v=(low*.65+noise*.15)*(0.35+.65*wave)
    elif name in ('city_day','arcade_hum','cafe_room','library_room'):
        hum={'city_day':82,'arcade_hum':124,'cafe_room':106,'library_room':66}[name]
        v=.012*np.sin(TAU*hum*t)+noise*.06+low*.12
        for q in range(20 if name=='arcade_hum' else 5):
            start=int(rng.uniform(0,length)*SR);L=min(n-start,int(.16*SR))
            if L>0:
                a=np.arange(L)/SR
                v[start:start+L]+=.016*np.sin(TAU*rng.uniform(550,2100)*a)*np.exp(-a*22)
    elif name in ('night_crickets','park_birds','birds_morning'):
        v=noise*.035+low*.08
        for q in range(36 if name=='night_crickets' else 16):
            start=int(rng.uniform(0,length)*SR);L=min(n-start,int(rng.uniform(.07,.30)*SR))
            if L>0:
                a=np.arange(L)/SR; pitch=rng.uniform(2400,4600) if name=='night_crickets' else rng.uniform(850,2900)
                chirp=np.sin(TAU*(pitch*a+1750*a*a))*np.sin(np.pi*np.arange(L)/max(1,L))**2*.021
                v[start:start+L]+=chirp
    elif name in ('magic_chimes','cave_drips'):
        v=low*.10+noise*.018
        for q in range(18 if name=='magic_chimes' else 11):
            start=int(rng.uniform(0,length)*SR);L=min(n-start,int(.52*SR))
            if L>0:
                a=np.arange(L)/SR; pitch=rng.uniform(420,1150) if name=='magic_chimes' else rng.uniform(170,660)
                v[start:start+L]+=np.sin(TAU*pitch*a)*np.exp(-a*15)*.042
    else: v=(noise*.11+low*.45)*(.7+.3*np.sin(TAU*.18*t))
    # Periodic ambience seamless wrap, remove offset and blend endpoints.
    v=v-np.mean(v)
    xfade=int(.35*SR)
    v[:xfade]=(v[:xfade]*np.linspace(0,1,xfade)+v[-xfade:]*np.linspace(1,0,xfade))
    v[-xfade:]=v[:xfade]
    pair=np.column_stack((v,np.roll(v,113)*.96))
    encode_ogg(pair,ROOT/'ambience'/f'{name}.ogg',quality=1)
    return length

def make_sfx(name,seed):
    rng=np.random.default_rng(500+seed)
    lengths={'door_open':.53,'door_close':.36,'quest_complete':1.4,'scene_transition':1.0,'wind_gust':1.0,
             'bird_chirp':.48,'cat_meow':.54,'dog_bark':.39,'duck_quack':.38,'lantern':.80,'heart':.74}
    d=lengths.get(name,.32); n=int(SR*d);t=np.arange(n,dtype=np.float32)/SR
    envelope=np.sin(np.pi*np.clip(t/d,0,1))**1.7
    nv=rng.normal(0,1,n).astype(np.float32)
    if name.startswith('step_'):
        pitch={'step_stone':140,'step_wood':110,'step_grass':85}[name]
        sig=(np.sin(TAU*pitch*t)*np.exp(-t*28)+nv*np.exp(-t*34)*(.19 if name=='step_grass' else .30))*.33
    elif name in ('cat_meow','dog_bark','duck_quack','bird_chirp'):
        f={'cat_meow':530,'dog_bark':205,'duck_quack':320,'bird_chirp':1550}[name]
        phase=TAU*(f*t+(55 if name=='cat_meow' else -60)*t*t)
        sig=(np.sin(phase)+.17*np.sin(phase*2))*envelope*.42
        if name=='dog_bark':sig+=.12*nv*envelope
    elif name in ('wind_gust','splash','rain_drop','door_open','door_close'):
        sig=(nv*.23+np.sin(TAU*(100+seed*3)*t)*.08)*envelope
    else:
        f={'bell_shop':970,'coin':1240,'gift':530,'heart':760,'hug':290,'selfie':930,
           'highfive':480,'quest_complete':610,'scene_transition':350,'notification':850,
           'lantern':1150,'page_turn':200,'menu_confirm':620}.get(name,500)
        osc=np.sin(TAU*f*t)+.35*np.sin(TAU*f*1.5*t)
        if name=='highfive':osc+=nv*.36
        if name=='selfie':osc+=nv*.12
        sig=osc*envelope*.29
        if name in ('quest_complete','gift','heart','lantern'):
            sig+=.17*np.sin(TAU*f*1.26*t)*np.exp(-t*4)
    sig=fade_edges(sig)
    dest=ROOT/'sfx'/f'{name}.wav'
    with wave.open(str(dest),'wb') as wf:
        wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(SR)
        wf.writeframes((np.clip(sig,-.9,.9)*32767).astype('<i2').tobytes())
    return round(d,2)

def main():
    print('Making original audio: 25 BGM, 14 ambience loops, 25 SFX')
    catalog={'schema':1,'license':'Original procedural synthesis; no external samples or copyrighted melodies', 'music':[],'ambience':[],'sfx':[]}
    for i,cfg in enumerate(CUES):
        duration=make_song(*cfg)
        catalog['music'].append({'id':cfg[0],'path':'audio/music/'+cfg[0]+'.ogg','seconds':duration,'bpm':cfg[1],'instrument':cfg[2]})
        print('BGM',i+1,cfg[0],duration,'s',flush=True)
    for i,name in enumerate(AMBIENTS):
        catalog['ambience'].append({'id':name,'path':'audio/ambience/'+name+'.ogg','seconds':ambience(name,i)})
    for i,name in enumerate(SFX):
        catalog['sfx'].append({'id':name,'path':'audio/sfx/'+name+'.wav','seconds':make_sfx(name,i)})
    (ROOT/'soundscape_v24.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print('AUDIO FINISHED',len(catalog['music']),'new BGM',len(catalog['ambience']),'ambience',len(catalog['sfx']),'SFX',flush=True)
if __name__=='__main__':main()
