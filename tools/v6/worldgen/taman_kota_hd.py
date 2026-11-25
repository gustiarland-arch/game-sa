"""Taman Kota, v6 HD rebuild (2400x1760 world, 2 texels per unit). Designed from scratch with the
v6 art kit; every quest point of the area stays where it is and is validated reachable.

Districts: koi lake with island + lookout deck (panorama point), stream to the south crossed by a
plank bridge exactly where the lake loop path meets it, gazebo rose court + Rain Garden arch,
picnic meadow, community garden, pine grove NW, cherry walk around the lake.
"""
import sys, json, hashlib
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from hdmap import HDMap, K, GRASS, PATH, STONE, WATER, DECK, SAND, SOIL, A   # noqa: E402
from paint import rgb                                                        # noqa: E402
from ground import dist_from                                                 # noqa: E402

AREA, W, H = 'taman_kota', 2400, 1760
SEED = int(hashlib.sha256(b'taman_kota_hd').hexdigest()[:8], 16)

LOOP = [(300, 560), (700, 470), (1150, 500), (1500, 640), (1720, 780), (1800, 980), (1700, 1250),
        (1600, 1450), (1300, 1450), (1050, 1480), (650, 1400), (380, 1250), (250, 950), (300, 560)]
NORTH = [(1200, 0), (1190, 260), (1150, 500)]
EAST = [(2400, 880), (2150, 880), (1960, 860), (1800, 980)]
GAZEBO_LINK = [(1960, 860), (1890, 740), (1875, 700)]
RAIN_LINK = [(1990, 600), (2094, 600)]
PICNIC_LINK = [(1700, 1250), (1860, 1290)]
GARDEN_LINK = [(1100, 1475), (1120, 1540)]
STREAM = [(1130, 1140), (1260, 1250), (1380, 1330), (1450, 1385), (1450, 1520), (1500, 1640), (1540, 1760)]
BRIDGE = (1402, 1414, 96, 72)      # x, y, w, h: deck across the straight stream reach, loop path runs left-right
LAKE = [(800, 950, 350, 188), (1075, 1075, 175, 112)]
ISLAND = (690, 930, 74, 40)
COURT = (1875, 590, 190, 120)
GARDEN = (930, 1545, 380, 130)
LOOKOUT = (970, 742, 60, 110)       # x, y, w, h deck from the north shore into the lake
VIEW_POINT = (1000, 820)


def design(m, P):
    c = m.c
    grass = c.grass(('#4f9157', '#57995d', '#5fa163', '#68a869', '#72b06f', '#7db876'))
    c.put(np.ones((c.h, c.w), bool), grass, GRASS)
    meadow = m.ellipse(1890, 1290, 280, 170, 8, 2)
    c.img[meadow] = np.clip(c.img[meadow] * 1.06 + 5, 0, 255)
    # ---- water
    lake = m.ellipse(*LAKE[0], wob=4, salt=1) | m.ellipse(*LAKE[1], wob=4, salt=2)
    stream = m.path(STREAM, 58, wob=3, salt=3)
    water = (lake | stream)
    for px, py, _ in m.points:          # every quest/event point stays on dry land (shore bulge)
        if px is not None:
            water &= ~m.ellipse(px, py, 40, 34)
    island = m.ellipse(*ISLAND, wob=3, salt=4)
    shore = (dist_from(water, 30) < 22) & ~water
    c.put(shore, c.dirt(('#c7b089', '#d0ba94', '#d9c49f', '#e1ceaa')), SAND)
    w_only = water & ~island
    c.put(w_only, c.water(w_only, ('#1f5378', '#27638a', '#30759c', '#3d89ae', '#57a0c2')), WATER)
    c.put(island, grass, GRASS)
    isl_edge = island & (dist_from(~island, 12) < 10)
    c.img[isl_edge] = c.img[isl_edge] * 0.45 + rgb('#d0ba94') * 0.55
    dl = dist_from(~w_only, 6)
    for i, f in ((1, 0.65), (2, 0.35), (3, 0.15)):
        sel = w_only & (dl == i)
        c.img[sel] = c.img[sel] * (1 - f) + rgb('#dcf0f6') * f
    # ---- paths
    allp = (m.path(LOOP, 58, 2, 5) | m.path(NORTH, 62, 2, 6) | m.path(EAST, 64, 2, 7) | m.path(GAZEBO_LINK, 50, 2, 8)
            | m.path(RAIN_LINK, 50, 2, 9) | m.path(PICNIC_LINK, 44, 2, 10) | m.path(GARDEN_LINK, 44, 2, 11))
    allp &= ~w_only
    gravel = c.dirt(('#b49b74', '#bfa77f', '#c9b28a', '#d4be97'))
    c.put(allp, gravel, PATH)
    # ---- gazebo rose court (radial stone)
    gx, gy, grx, gry = COURT
    court = m.ellipse(gx, gy, grx, gry)
    rad, r, th, ri = c.radial(gx * K, gy * K, gry / grx, ('#d4c7b4', '#dcd0be', '#e4d9c8', '#ebe2d3'), 20, 36, salt=4, mortar='#a99a85')
    c.put(court, rad, STONE)
    c.img[court & (r > (grx - 8) * K)] = rgb('#9d8b74')
    # ---- plank bridge across the straight reach of the stream; the loop path runs straight over it
    bx, by, bw, bh = BRIDGE
    deck = m.rect(bx, by, bw, bh)
    c.put(deck, c.planks(('#8b5d3c', '#996a46', '#a5754f', '#b07f57'), 14, salt=5, vertical=True), 5)
    for ry in (by, by + bh - 8):                      # rails (top lit, bottom in shade)
        c.img[m.rect(bx - 4, ry, bw + 8, 8)] = rgb('#a5754f')
        c.img[m.rect(bx - 4, ry, bw + 8, 2)] = rgb('#c99a6a')
        c.img[m.rect(bx - 4, ry + 6, bw + 8, 2)] = rgb('#5e3b27')
        for px in range(bx - 4, bx + bw + 4, 24):
            c.img[m.rect(px, ry - 4, 6, 14)] = rgb('#6e4630')
    c.img[m.rect(bx, by + bh, bw, 6) & w_only] *= 0.55   # deck shadow on the water
    m.walk_over |= m.rect(bx, by + 10, bw, bh - 20)
    m.bridge = BRIDGE
    # ---- lookout deck into the lake (panorama point)
    lx, ly, lw, lh = LOOKOUT
    look = m.rect(lx, ly, lw, lh)
    c.put(look, c.planks(('#8b5d3c', '#996a46', '#a5754f', '#b07f57'), 16, salt=6, vertical=False), 5)
    lrail = look & (dist_from(~look, 6) <= 3) & ~m.rect(lx + 6, ly - 2, lw - 12, 10)
    c.img[lrail] = rgb('#5e3b27')
    c.img[m.rect(lx, ly + lh, lw, 6) & w_only] *= 0.6
    m.walk_over |= look & ~lrail
    # ---- community garden beds
    gx0, gy0, gw0, gh0 = GARDEN
    soil = c.dirt(('#6e5038', '#7a5a3f', '#866447', '#916f50'))
    for k in range(4):
        bed = m.rect(gx0 + k * 96, gy0, 80, gh0) & ~w_only
        c.put(bed, soil, 9)
        rows = bed & (((c.yy // K) - gy0) % 16 < 3)
        c.img[rows] *= 0.75
        crop = bed & (((c.yy // K) - gy0) % 16 == 8) & (((c.xx // K) - gx0) % 12 < 6)
        c.img[crop] = rgb(('#5c9a4a', '#6aa84f', '#e06a5a', '#e7c04a')[k])
        frame = m.rect(gx0 + k * 96 - 3, gy0 - 3, 86, gh0 + 6) & ~bed
        c.img[frame] = rgb('#7a5236')
    # ---- edges
    gm = c.mat == GRASS
    c.rim(np.isin(c.mat, [PATH]), gm, dark='#86704f', ao=(0.9, 0.95))
    c.overhang(c.mat == PATH, gm, 0.25, 1)
    c.rim(np.isin(c.mat, [STONE, 5]), gm | (c.mat == PATH))
    m.water_mask = w_only

    # ---------------------------------------------------------------- props
    pr = m.prop
    pr('hd_gazebo', gx, gy + 60)
    for x, y in ((1650, 500), (2100, 470), (1650, 700)):
        pr('hd_bush_rose', x, y)
    # Rain Garden arch at the door, framed by hedges
    pr('hd_arch', 2094, 622)
    for x in (2010, 2178):
        pr('hd_bush_a', x, 626)
    # lamps along the loop and entrances (every ~260 units, alongside the path)
    pts = np.array(LOOP, float)
    seg = np.cumsum([0] + [np.hypot(*(pts[i + 1] - pts[i])) for i in range(len(pts) - 1)])
    for s in np.arange(130, seg[-1], 270):
        i = np.searchsorted(seg, s) - 1
        t = (s - seg[i]) / (seg[i + 1] - seg[i])
        x, y = pts[i] + t * (pts[i + 1] - pts[i])
        d = pts[i + 1] - pts[i]; nrm = np.array([-d[1], d[0]]) / np.hypot(*d)
        lx_, ly_ = (x, y) + nrm * 42
        near_water = m.water_mask[max(0, int(ly_ - 40) * K):int(ly_ + 20) * K, max(0, int(lx_ - 30) * K):int(lx_ + 30) * K].any()
        near_bench = any(abs(lx_ - bx_) < 90 and abs(ly_ - by_) < 60 for bx_, by_ in ((560, 560), (1250, 590), (420, 1220), (1180, 1420)))
        if not near_water and not near_bench:
            pr('hd_lamp', lx_, ly_)
    for x, y in ((1250, 260), (2250, 840), (2250, 925), (1150, 120)):
        pr('hd_lamp', x, y)
    # benches facing the lake on the inner side of the loop, with bins
    for x, y in ((560, 560), (1250, 590), (420, 1220), (1180, 1420)):
        pr('hd_bench', x, y); pr('hd_bin', x + 46, y + 4)
    pr('hd_signpost', 1235, 520); pr('hd_signpost', 1985, 905); pr('hd_signpost', 1745, 1225)
    # picnic meadow
    for x, y in ((1960, 1330), (1800, 1360), (2080, 1240)):
        pr('hd_picnic', x, y)
    pr('hd_tree_blossom', 2160, 1380)
    # garden: fence + scarecrow-ish bushes
    pr('hd_fence_h', 1020, 1525); pr('hd_fence_h', 1215, 1525)
    pr('hd_bush_yellow', 900, 1700); pr('hd_bush_rose', 1330, 1700)
    # lake decor
    rng = np.random.default_rng(SEED)
    ys, xs = np.nonzero(m.water_mask[::K, ::K] & (dist_from(~m.water_mask[::K, ::K], 40) > 18) & ~m.walk_over[::K, ::K]
                        & ~m.rect(LOOKOUT[0] - 40, LOOKOUT[1], LOOKOUT[2] + 80, LOOKOUT[3] + 60)[::K, ::K])
    for i in rng.integers(0, len(ys), 40):
        pr('hd_lily_a' if i % 2 else 'hd_lily_b', xs[i], ys[i])
    pr('hd_rowboat', 860, 1040)
    for x, y in ((470, 1050), (1180, 1180), (560, 800), (1280, 980), (1210, 1300)):
        pr('hd_reeds', x, y)
    pr('hd_tree_cherry_a', 690, 940); pr('hd_rock_a', 735, 948)
    # flowers along paths (floor layer)
    for x, y in ((640, 520), (900, 470), (1380, 600), (1640, 760), (1760, 1120), (820, 1450), (480, 1330),
                 (320, 760), (1540, 1340), (2300, 830), (1140, 400), (1240, 380)):
        pr(('hd_flowers_pink', 'hd_flowers_yellow', 'hd_flowers_violet', 'hd_flowers_white')[(x + y) % 4], x, y)

    # ---- planting: groves avoid water, paths, decks, points
    blocked = (m.c.mat != GRASS) | (dist_from(m.c.mat != GRASS, 40 * K) < 30 * K)
    for x, y, r in m.points:
        m.keep_out.append((x, y, r))
    m.scatter(['hd_tree_pine_a', 'hd_tree_pine_b', 'hd_tree_oak_c'], [5, 5, 2], 26, (40, 60, 520, 440), blocked, 22, P)
    m.scatter(['hd_tree_oak_a', 'hd_tree_oak_b', 'hd_tree_autumn_a', 'hd_tree_autumn_b'], [4, 4, 3, 3], 22, (1350, 60, 1000, 420), blocked, 22, P)
    m.scatter(['hd_tree_cherry_a', 'hd_tree_cherry_b'], [1, 1], 18, (200, 380, 1700, 1180), blocked, 22, P)
    m.scatter(['hd_tree_oak_a', 'hd_tree_oak_b', 'hd_tree_oak_c', 'hd_tree_blossom'], [4, 4, 3, 2], 30, (40, 1150, 900, 600), blocked, 22, P)
    m.scatter(['hd_tree_oak_a', 'hd_tree_autumn_a', 'hd_tree_cherry_b'], [3, 2, 2], 18, (1650, 1450, 740, 300), blocked, 22, P)
    m.scatter(['hd_tree_oak_b', 'hd_tree_oak_c'], [1, 1], 10, (2150, 950, 240, 500), blocked, 22, P)
    m.scatter(['hd_bush_a', 'hd_bush_b', 'hd_bush_rose', 'hd_rock_a', 'hd_rock_b', 'hd_stump'], [5, 5, 2, 2, 1, 1], 60, (30, 60, 2340, 1680), blocked, 18, P)
    m.scatter(['hd_flowers_pink', 'hd_flowers_yellow', 'hd_flowers_violet', 'hd_flowers_white'], [1, 1, 1, 1], 70, (30, 60, 2340, 1680), blocked, 10, P)
    # north border hedge, gap for the forest path
    for x in range(60, 2400, 70):
        if abs(x - 1200) > 110:
            pr(('hd_bush_a', 'hd_bush_b')[x // 70 % 2], x, 40)


def main():
    P = json.loads((A / 'data/props.json').read_text(encoding='utf-8'))['props']
    Q = json.loads((A / 'data/quests.json').read_text(encoding='utf-8'))
    M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
    base = M['areas'][AREA]
    import common
    m = HDMap(AREA, W, H, SEED)
    m.points = [(p[3], p[4], 46) for p in common.migrate_quests(json.loads(json.dumps(Q)), AREA, lambda x, y: (x, y))]
    m.points += [(e['x'], e['y'], 46) for e in base.get('examine', [])]
    m.points += [(d['tx'], d['ty'], 50) for b in M['areas'].values() for d in b.get('doors', []) if d.get('to') == AREA]
    for d in base['doors']:
        x, y, w, h = d['rect']; m.points.append((x + w / 2, y + h / 2, max(w, h) / 2 + 40))
    m.points.append((*VIEW_POINT, 60))
    design(m, P)
    m.bake_shadows(P)
    extra = dict(water=[dict(cx=800, cy=950, rx=350, ry=188), dict(cx=1075, cy=1075, rx=175, ry=112)],
                 v6Layout=dict(version=2, generator='tools/v6/worldgen/taman_kota_hd.py', hd=True,
                               districts=['koi lake + island + lookout deck', 'stream + plank bridge on the loop path',
                                          'gazebo rose court + Rain Garden gate', 'picnic meadow', 'community garden',
                                          'pine grove', 'cherry walk']))
    # the panorama point now stands on the lookout deck
    import re
    moved = 0
    for side in Q.get('side', []):
        if isinstance(side, dict) and side.get('id') == 'V50_VIEW_TAMAN_KOTA':
            side['x'], side['y'] = VIEW_POINT; side['label'] = '✦ Panorama: Dek Pandang Kolam'; moved += 1
    prev = sys.argv[sys.argv.index('--preview') + 1] if '--preview' in sys.argv else None
    bad = m.write(base, extra, P, Q, apply='--apply' in sys.argv, preview=prev)
    if '--apply' in sys.argv and not bad:
        (A / 'data/quests.json').write_text(json.dumps(Q, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('panorama point moved', moved)


if __name__ == '__main__':
    main()
