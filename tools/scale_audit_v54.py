#!/usr/bin/env python3
"""v5.4 world-scale inventory. Measures every prop sprite's opaque bounds
against the rendered Arland/Sofia body (frame 48x72 * Actor.SCALE) and flags
furniture whose proportions fall outside a per-category band. Read-only: it
never edits assets. Output: docs/v54/SCALE_AUDIT_V54.json + .md"""
import json, re, sys
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parents[1]
A = R / 'android/assets'
import os
_actor = (R / 'core/src/main/java/com/arlandsofia/olu/game/Actor.java').read_text(encoding='utf-8')
ACTOR_SCALE = float(os.environ.get('OLU_ACTOR_SCALE') or re.search(r'SCALE = ([0-9.]+)f', _actor).group(1))

def body(char):
    im = Image.open(A / f'characters/{char}/walk_v53.png').convert('RGBA')
    hs, ws = [], []
    for c in range(0, im.width, 48):
        bb = im.crop((c, 0, c + 48, 72)).split()[3].getbbox()
        if bb: hs.append(bb[3] - bb[1]); ws.append(bb[2] - bb[0])
    return max(hs) * ACTOR_SCALE, max(ws) * ACTOR_SCALE

# Height bands relative to the rendered character body height (3/4 top-down view:
# sprite height includes the visible top surface, so tables read taller than real life).
BANDS = [
    (r'(^|_)(chair|stool|kursi)', 0.35, 0.85),
    (r'(^|_)(bench)', 0.30, 0.90),
    (r'(^|_)(table|meja)', 0.35, 1.00),
    (r'(^|_)(desk)', 0.45, 1.10),
    (r'(^|_)(sofa|couch)', 0.40, 1.00),
    (r'(^|_)(bed)', 0.70, 1.90),
    (r'(^|_)(door)', 1.05, 1.60),
    (r'(^|_)(lamp|lantern)(?!_post)', 0.25, 2.20),
    (r'(^|_)(counter)', 0.55, 1.30),
    (r'(^|_)(bookshelf|shelf|wardrobe|cabinet)', 0.90, 1.90),
    (r'(^|_)(plant|pot|vase)', 0.20, 1.30),
]

def band(name):
    for pat, lo, hi in BANDS:
        if re.search(pat, name): return pat.split('(')[2].split(')')[0], lo, hi
    return None

def main():
    defs = json.loads((A / 'data/props.json').read_text(encoding='utf-8'))['props']
    areas = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))['areas']
    used = {}
    for aid, a in areas.items():
        for p in a.get('props', []):
            used.setdefault(p['type'], set()).add(aid)
    ah, aw = body('arland'); sh, sw = body('sofia')
    ref = (ah + sh) / 2
    npc = {}
    for d in sorted((A / 'characters').iterdir()):
        if (d / 'walk_v53.png').exists(): npc[d.name] = round(body(d.name)[0] / ref, 3)
    rows = []
    for k, v in sorted(defs.items()):
        f = A / v['image']
        if not f.exists(): rows.append({'id': k, 'missing': True}); continue
        im = Image.open(f).convert('RGBA'); bb = im.split()[3].getbbox() or (0, 0, 0, 0)
        h, w = bb[3] - bb[1], bb[2] - bb[0]
        b = band(k)
        row = {'id': k, 'image': v['image'], 'px': [w, h], 'hRatio': round(h / ref, 2), 'wRatio': round(w / ref, 2),
               'collider': [v.get('cw', 0), v.get('ch', 0)], 'maps': sorted(used.get(k, []))}
        if b:
            row['category'], lo, hi = b
            row['band'] = [lo, hi]
            row['flag'] = 'too_big' if h / ref > hi else 'too_small' if h / ref < lo else 'ok'
        if v.get('cw', 0) > 0 and w > 0 and v['cw'] > w + 4:
            row['colliderWiderThanArt'] = True
        rows.append(row)
    out = {'referenceBodyPx': round(ref, 1), 'arland': [round(ah, 1), round(aw, 1)], 'sofia': [round(sh, 1), round(sw, 1)],
           'npcHeightVsLeads': npc, 'props': rows}
    od = Path(os.environ.get('OLU_AUDIT_OUT') or R / 'docs/v54'); od.mkdir(parents=True, exist_ok=True)
    (od / 'SCALE_AUDIT_V54.json').write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding='utf-8')
    flagged = [r for r in rows if r.get('flag') in ('too_big', 'too_small') and r['maps']]
    wide = [r for r in rows if r.get('colliderWiderThanArt') and r['maps']]
    md = ['# v5.4 World Scale Audit', '',
          f'Reference body (rendered, Arland/Sofia avg): **{ref:.1f} px** tall. '
          f'Arland {ah:.1f}x{aw:.1f}, Sofia {sh:.1f}x{sw:.1f} (opaque bounds x Actor.SCALE {ACTOR_SCALE}).', '',
          f'Props in props.json: {len(rows)}; categorised: {sum(1 for r in rows if "category" in r)}; '
          f'used in maps and outside band: **{len(flagged)}**; collider wider than art: {len(wide)}.', '',
          '## Out-of-band furniture used in maps', '', '| prop | category | px (w x h) | height / body | band | maps |', '|---|---|---|---|---|---|']
    for r in sorted(flagged, key=lambda r: -r['hRatio']):
        md.append(f"| {r['id']} | {r['category']} | {r['px'][0]}x{r['px'][1]} | {r['hRatio']} | {r['band'][0]}-{r['band'][1]} | {', '.join(r['maps'])} |")
    md += ['', '## Collider wider than visible art', '', '| prop | art w | collider w | maps |', '|---|---|---|---|']
    for r in wide: md.append(f"| {r['id']} | {r['px'][0]} | {r['collider'][0]} | {', '.join(r['maps'])} |")
    md += ['', '## NPC height relative to leads', '', '| character | ratio |', '|---|---|']
    for k, v in npc.items(): md.append(f'| {k} | {v} |')
    (od / 'SCALE_AUDIT_V54.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(f'scale audit: ref={ref:.1f}px flagged={len(flagged)} wideColliders={len(wide)}')

if __name__ == '__main__':
    main()
