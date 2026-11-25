"""Builds the v6 HD art kit into android/assets/props/hd/*@2x.png and registers each sprite in
props.json (cw/ch collider in world units; scale 0.5 is implied by the @2x name).

Usage: python3 tools/v6/artkit/registry.py
"""
import sys, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kit, nature, built   # noqa: E402

ROOT = HERE.parents[2]
A = ROOT / 'android' / 'assets'
OUT = A / 'props' / 'hd'

# id: (factory, cw, ch, layer)   colliders are the foot/base area in world units
KIT = {
    'hd_tree_oak_a': (lambda: nature.broadleaf(kit.LEAF, 1), 16, 9, 'sort'),
    'hd_tree_oak_b': (lambda: nature.broadleaf(kit.LEAF, 11), 16, 9, 'sort'),
    'hd_tree_oak_c': (lambda: nature.broadleaf(kit.LEAF_DARK, 21), 16, 9, 'sort'),
    'hd_tree_blossom': (lambda: nature.broadleaf(kit.LEAF, 4, blossoms=kit.FLOWERS[3]), 16, 9, 'sort'),
    'hd_tree_cherry_a': (lambda: nature.broadleaf(kit.CHERRY, 2), 16, 9, 'sort'),
    'hd_tree_cherry_b': (lambda: nature.broadleaf(kit.CHERRY, 12), 16, 9, 'sort'),
    'hd_tree_autumn_a': (lambda: nature.broadleaf(kit.AUTUMN, 3), 16, 9, 'sort'),
    'hd_tree_autumn_b': (lambda: nature.broadleaf(kit.AUTUMN, 13), 16, 9, 'sort'),
    'hd_tree_pine_a': (lambda: nature.pine(5), 14, 8, 'sort'),
    'hd_tree_pine_b': (lambda: nature.pine(15), 14, 8, 'sort'),
    'hd_bush_a': (lambda: nature.bush(6), 36, 10, 'sort'),
    'hd_bush_b': (lambda: nature.bush(16), 36, 10, 'sort'),
    'hd_bush_rose': (lambda: nature.bush(7, flowers=kit.FLOWERS[0]), 36, 10, 'sort'),
    'hd_bush_yellow': (lambda: nature.bush(17, flowers=kit.FLOWERS[1]), 36, 10, 'sort'),
    'hd_rock_a': (lambda: nature.rock(8), 26, 9, 'sort'),
    'hd_rock_b': (lambda: nature.rock(18, w=90, h=58), 38, 12, 'sort'),
    'hd_flowers_pink': (lambda: nature.flower_clump(0, 5), 0, 0, 'floor'),
    'hd_flowers_yellow': (lambda: nature.flower_clump(1, 6), 0, 0, 'floor'),
    'hd_flowers_violet': (lambda: nature.flower_clump(2, 7), 0, 0, 'floor'),
    'hd_flowers_white': (lambda: nature.flower_clump(3, 8), 0, 0, 'floor'),
    'hd_reeds': (lambda: nature.reeds(6), 0, 0, 'sort'),
    'hd_stump': (lambda: nature.stump(7), 26, 9, 'sort'),
    'hd_cottage_blue': (lambda: built.cottage(kit.ROOF_BLUE, seed=1), 160, 40, 'sort'),
    'hd_cottage_red': (lambda: built.cottage(kit.ROOF_RED, seed=2), 160, 40, 'sort'),
    'hd_cottage_green': (lambda: built.cottage(kit.ROOF_GREEN, kit.BRICK, seed=3), 160, 40, 'sort'),
    'hd_gazebo': (lambda: built.gazebo(), 150, 30, 'sort'),
    'hd_stall_red': (lambda: built.market_stall(), 100, 20, 'sort'),
    'hd_stall_blue': (lambda: built.market_stall(('#4c6fa8', '#eef0f2')), 100, 20, 'sort'),
    'hd_fountain': (lambda: built.fountain(), 110, 40, 'sort'),
    'hd_well': (lambda: built.well(), 56, 26, 'sort'),
    'hd_bench': (lambda: built.bench(), 54, 9, 'sort'),
    'hd_lamp': (lambda: built.lamp_post(), 8, 6, 'sort'),
    'hd_fence_h': (lambda: built.fence(192), 96, 6, 'sort'),
    'hd_fence_v': (lambda: built.fence(192, vertical=True), 8, 96, 'sort'),
    'hd_signpost': (lambda: built.signpost(), 8, 6, 'sort'),
    'hd_bin': (lambda: built.trash_bin(), 16, 8, 'sort'),
    'hd_picnic': (lambda: built.picnic_blanket(), 0, 0, 'floor'),
    'hd_lily_a': (lambda: built.lily_pad(1), 0, 0, 'floor'),
    'hd_lily_b': (lambda: built.lily_pad(3), 0, 0, 'floor'),
    'hd_arch': (lambda: built.flower_arch(), 0, 0, 'sort'),
    'hd_rowboat': (lambda: built.rowboat(), 0, 0, 'floor'),
}


def build(only=None):
    OUT.mkdir(parents=True, exist_ok=True)
    pj = A / 'data/props.json'
    data = json.loads(pj.read_text(encoding='utf-8'))
    for pid, (fn, cw, ch, layer) in KIT.items():
        if only and pid not in only:
            continue
        img = fn().image()
        rel = 'props/hd/%s@2x.png' % pid
        img.save(A / rel, optimize=True)
        e = {'image': rel, 'cw': cw, 'ch': ch, 'layer': layer}
        data['props'][pid] = e
        print(pid, img.size)
    pj.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    build(set(sys.argv[1:]) or None)
