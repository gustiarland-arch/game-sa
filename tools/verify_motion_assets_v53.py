#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import json, hashlib
ROOT=Path(__file__).resolve().parent.parent
a=ROOT/"android/assets/characters"
data=json.loads((ROOT/"docs/MOTION_NPC_V53_ASSET_MANIFEST.json").read_text())
names=data["sprites"]
assert len(names)==25 and len(data["styles"])==22
n=0
for name in names:
    base=a/name
    for typ,shape in [("walk_v53.png",(24*48,4*72)),
                      ("idle_v53.png",(12*48,4*72))]:
        atlas=Image.open(base/typ).convert("RGBA")
        assert atlas.size==shape,(name,typ,atlas.size)
        assert atlas.getbbox(),name
        phases=shape[0]//48
        for d in range(4):
            frames=[atlas.crop((i*48,d*72,(i+1)*48,(d+1)*72))
                  for i in range(phases)]
            hashes={hashlib.sha256(x.tobytes()).hexdigest() for x in frames}
            assert len(hashes) >= (8 if typ.startswith("walk") else 6),(name,typ,d,len(hashes))
            assert all(x.getbbox() for x in frames),(name,typ,d,"blank")
            n+=3
    if name in data["styles"]:
        pose=Image.open(base/"poses_v53.png")
        assert pose.size==(384,1152),(name,pose.size)
        # Original textures are never overwritten.
        assert (base/"poses.png").is_file()
        n+=2
    if name in ("arland","sofia"):
        for typ,shape in [("walk_8dir_v53.png",(24*48,8*72)),
                          ("idle_8dir_v53.png",(12*48,8*72))]:
            im=Image.open(base/typ)
            assert im.size==shape,(name,typ,im.size)
            n+=8
print("V5.3 Sprite atlas structure:",n,"checks OK across",len(names),"characters.")
