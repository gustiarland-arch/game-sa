#!/usr/bin/env python3
"""Original HD town NPCs for the Godot build.

Draws every town character from a parametric description (body, age, hair, face, clothes,
accessories) instead of recolouring Arland and Sofia, so each NPC has their own silhouette.
Writes @2x sheets next to the old ones (the old files stay; the Godot Actor prefers @2x):

  characters/<id>/walk_v53@2x.png   24 frames x 4 directions (down, left, right, up)
  characters/<id>/idle_v53@2x.png   12 frames x 4 directions
  characters/<id>/poses_v53@2x.png  16 poses x (4 directions x 2 frames)
  characters/<id>/portraits/<emotion>.png  176x220 dialogue portraits

Frame size is 48x72 base units (96x144 px at @2x); feet sit at y=70. Shapes are rendered at
8x and downsampled for clean anti-aliased edges.

Usage: python3 tools/godot/npc_gen.py [assets_dir] [--only id,id] [--sheet out.png]
"""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFilter

FW, FH = 48, 72
SS = 8              # supersampling: base unit -> px while drawing
OUT_K = 2           # @2x output
OUTLINE = (52, 38, 58, 255)
BODY_SCALE = 1.22
POSES = ["sit", "wave", "give", "reach", "bow", "hold_l", "hold_r", "cheer",
         "hug", "lean", "photo", "highfive", "dance", "read", "water", "sweep"]


def rgb(h, a=255):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (c[3],)


# ----------------------------------------------------------------------------- characters
SKIN = {"light": "#f6d7c3", "warm": "#eec4a3", "tan": "#d9a27c", "brown": "#b77b57", "deep": "#8d5a3f"}

NPCS = {
    "raka": dict(h=1.0, build=1.0, skin="warm", hair=("undercut", "#3b2a22"), face=dict(brows="soft"),
                 top=("shirt", "#f4f1ea"), over=("apron", "#7a4b33"), sleeves="rolled", bottom=("pants", "#2d2b33"),
                 shoes="#4a3328"),
    "melati": dict(h=0.97, build=1.05, skin="warm", hair=("hijab", "#8fb39a"), face=dict(blush=True),
                   top=("dress", "#e9a9b9"), pattern="flowers", over=("apron", "#5e8a6c"), shoes="#7a5a48", acc=["flower_pin"]),
    "juna": dict(h=1.02, build=0.95, skin="light", hair=("spiky", "#2fb3a6"), face=dict(brows="sharp"),
                 top=("hoodie", "#6a4c9c"), bottom=("cargo", "#5b6070"), shoes="#f2f2f2", acc=["headphones"]),
    "sari": dict(h=0.86, build=0.95, skin="light", age="elder", hair=("bun", "#cfcbd3"), face=dict(glasses="round", eyes="smile"),
                 top=("cardigan", "#b7a3d6"), inner="#f3ece2", bottom=("longskirt", "#8a5a44"), pattern_bottom="batik",
                 shoes="#5a4636", acc=["cane"], stoop=1.5),
    "dito": dict(h=0.74, build=0.95, skin="tan", age="child", hair=("spiky", "#1f1b24"), face=dict(blush=True),
                 top=("tee", "#f5c842"), bottom=("shorts", "#d9534f"), shoes="#3a7bd5", acc=["backpack"]),
    "udin": dict(h=0.98, build=1.08, skin="deep", hair=("short", "#2a211d"), face=dict(moustache=True),
                 top=("shirt", "#dfe7ee"), pattern="stripes", over=("vest", "#7d8450"), bottom=("pants", "#6b5a45"),
                 shoes="#3d3a35", hat=("bucket", "#c8b48a")),
    "pos": dict(h=1.0, build=1.0, skin="tan", hair=("short", "#2b2320"), face=dict(),
                top=("uniform", "#f08a2c"), bottom=("pants", "#283a5e"), shoes="#222",
                hat=("postcap", "#f08a2c"), acc=["satchel"]),
    "laras": dict(h=0.98, build=0.92, skin="light", hair=("long", "#1d1820"), face=dict(glasses="square", brows="soft"),
                  top=("blouse", "#8e3b4f"), bottom=("longskirt", "#2f3a5c"), shoes="#3a2b2b", acc=["hairclip", "book"]),
    "bayu": dict(h=1.04, build=1.18, skin="tan", hair=("short", "#2a1e18"), face=dict(brows="sharp"),
                 top=("tank", "#f2f4f7"), pattern="stripes_blue", bottom=("shorts", "#3a6ea5"), shoes="#6b4a35",
                 hat=("bandana", "#d1453b")),
    "nara": dict(h=0.99, build=0.92, skin="light", hair=("wavy", "#3a2b4f"), face=dict(blush=True),
                 top=("coat", "#26345e"), inner="#e9e4f2", bottom=("pants", "#1f2440"), shoes="#2b2b33",
                 hat=("beret", "#b44a6a"), acc=["star_scarf"]),
    "rini": dict(h=0.95, build=1.22, skin="tan", hair=("hijab", "#8e2f3d"), face=dict(),
                 top=("blouse", "#e88a3a"), pattern="batik", bottom=("longskirt", "#5c4330"), shoes="#3b2c22"),
    "harun": dict(h=1.0, build=1.05, skin="tan", age="older", hair=("short", "#9b958f"), face=dict(beard="short"),
                  top=("shirt", "#5f8a4a"), sleeves="rolled", bottom=("pants", "#6a5038"), shoes="#3a2c20",
                  hat=("straw", "#e6c77a"), acc=["gloves"]),
    "tika": dict(h=0.70, build=0.92, skin="light", age="child", hair=("pigtails", "#5a3524"), face=dict(blush=True),
                 top=("dress", "#f59ac0"), shoes="#c2405e", acc=["ribbons"]),
    "eko": dict(h=1.01, build=0.88, skin="brown", hair=("short", "#1f1a18"), face=dict(),
                top=("polo", "#c8423b"), bottom=("pants", "#4a6489"), shoes="#ececec", hat=("cap_back", "#2c3e66")),
    "wulan": dict(h=0.96, build=1.05, skin="warm", hair=("hijab", "#f2b48f"), face=dict(blush=True),
                  top=("cardigan", "#3f9a96"), inner="#fbf3e6", bottom=("longskirt", "#7c7f8a"), shoes="#5a4a40",
                  acc=["basket"]),
    "darmo": dict(h=0.9, build=0.95, skin="brown", age="elder", hair=("bald_sides", "#ecebe8"), face=dict(moustache="white", eyes="smile"),
                  top=("shirt", "#f4f1ea"), bottom=("sarong", "#3e6b5a"), pattern_bottom="plaid", shoes="#6b4a35",
                  hat=("peci", "#1e1b22"), stoop=1.8),
    "darto": dict(h=0.98, build=1.32, skin="tan", age="older", hair=("balding", "#2a2422"), face=dict(moustache=True),
                  top=("shirt", "#8a5a2e"), pattern="batik", bottom=("pants", "#2a2a30"), shoes="#1f1f22"),
    "rara": dict(h=0.88, build=0.9, skin="light", age="teen", hair=("bob", "#2b1d1a"), face=dict(blush=True),
                 top=("cardigan", "#f2cf4a"), inner="#ffffff", bottom=("skirt", "#3c4f86"), pattern_bottom="plaid",
                 shoes="#5a3a2e", acc=["headband"]),
    "bimo": dict(h=0.87, build=1.0, skin="brown", age="teen", hair=("curly", "#1e1814"), face=dict(),
                 top=("hoodie", "#3f8f5a"), bottom=("shorts", "#4b4f5e"), shoes="#e25b3c"),
    "ujang": dict(h=1.05, build=0.86, skin="tan", hair=("short", "#2a2320"), face=dict(moustache=True),
                  top=("jacket", "#7a5a3c"), inner="#e6dccb", bottom=("pants", "#3a3d45"), shoes="#2a2a2a",
                  hat=("beanie", "#8b8f96"), acc=["towel"]),
    "ina": dict(h=0.88, build=1.0, skin="light", age="elder", hair=("curly_short", "#f3f1f4"), face=dict(glasses="round", eyes="smile", blush=True),
                top=("dress", "#6f8fd0"), pattern="flowers", over=("shawl", "#e9d8c4"), shoes="#6b5446",
                acc=["pearls"], stoop=1.2),
    "tigor": dict(h=1.07, build=1.3, skin="tan", hair=("buzz", "#1a1616"), face=dict(beard="full", brows="sharp"),
                  top=("tee", "#b8312f"), over=("vest", "#26211f"), bottom=("pants", "#34507a"), shoes="#2a211c"),
}


# ----------------------------------------------------------------------------- drawing
class Pen:
    """Draws in base units (48x72 frame) onto a supersampled RGBA image."""

    def __init__(self, w=FW, h=FH, ox=0.0, oy=0.0):
        self.im = Image.new("RGBA", (int(w * SS), int(h * SS)), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.ox, self.oy = ox, oy
        self.ow = 1.0      # outline width in base units
        self.g = BODY_SCALE  # whole-figure scale around the feet, so NPCs stand as tall as Arland and Sofia

    def p(self, x, y):
        x = FW / 2 + (x - FW / 2) * self.g
        y = 70.0 + (y - 70.0) * self.g
        return ((x + self.ox) * SS, (y + self.oy) * SS)

    def ellipse(self, cx, cy, rx, ry, fill, outline=True):
        x0, y0 = self.p(cx - rx, cy - ry)
        x1, y1 = self.p(cx + rx, cy + ry)
        if outline:
            o = self.ow * SS * self.g
            self.d.ellipse((x0 - o, y0 - o, x1 + o, y1 + o), fill=OUTLINE)
        self.d.ellipse((x0, y0, x1, y1), fill=fill)

    def poly(self, pts, fill, outline=True):
        sp = [self.p(x, y) for x, y in pts]
        if outline:
            self.d.line(sp + [sp[0]], fill=OUTLINE, width=int(self.ow * SS * self.g * 2), joint="curve")
            for q in sp:
                r = self.ow * SS * self.g
                self.d.ellipse((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=OUTLINE)
        self.d.polygon(sp, fill=fill)

    def rrect(self, x0, y0, x1, y1, r, fill, outline=True):
        a, b = self.p(x0, y0)
        c, d = self.p(x1, y1)
        if outline:
            o = self.ow * SS * self.g
            self.d.rounded_rectangle((a - o, b - o, c + o, d + o), radius=r * SS * self.g + o, fill=OUTLINE)
        self.d.rounded_rectangle((a, b, c, d), radius=r * SS * self.g, fill=fill)

    def limb(self, x0, y0, x1, y1, w, fill, outline=True):
        a, b = self.p(x0, y0)
        c, d = self.p(x1, y1)
        if outline:
            ww = (w + 2 * self.ow) * SS * self.g
            self.d.line((a, b, c, d), fill=OUTLINE, width=int(ww))
            for q in ((a, b), (c, d)):
                r = ww / 2
                self.d.ellipse((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=OUTLINE)
        self.d.line((a, b, c, d), fill=fill, width=int(w * SS * self.g))
        for q in ((a, b), (c, d)):
            r = w * SS * self.g / 2
            self.d.ellipse((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=fill)

    def line(self, x0, y0, x1, y1, w, fill):
        a, b = self.p(x0, y0)
        c, d = self.p(x1, y1)
        self.d.line((a, b, c, d), fill=fill, width=max(1, int(w * SS * self.g)))

    def dot(self, cx, cy, r, fill):
        x0, y0 = self.p(cx - r, cy - r)
        x1, y1 = self.p(cx + r, cy + r)
        self.d.ellipse((x0, y0, x1, y1), fill=fill)

    def arc(self, cx, cy, rx, ry, a0, a1, w, fill):
        x0, y0 = self.p(cx - rx, cy - ry)
        x1, y1 = self.p(cx + rx, cy + ry)
        self.d.arc((x0, y0, x1, y1), a0, a1, fill=fill, width=max(1, int(w * SS * self.g)))

    def pieslice(self, cx, cy, rx, ry, a0, a1, fill, outline=True):
        x0, y0 = self.p(cx - rx, cy - ry)
        x1, y1 = self.p(cx + rx, cy + ry)
        if outline:
            o = self.ow * SS * self.g
            self.d.pieslice((x0 - o, y0 - o, x1 + o, y1 + o), a0, a1, fill=OUTLINE)
        self.d.pieslice((x0, y0, x1, y1), a0, a1, fill=fill)

    def out(self, w=FW * OUT_K, h=FH * OUT_K):
        return self.im.resize((w, h), Image.LANCZOS)


class Figure:
    """One character's proportions and palette."""

    def __init__(self, spec):
        self.s = spec
        self.k = spec.get("h", 1.0)                  # overall height
        self.b = spec.get("build", 1.0)              # body width
        self.age = spec.get("age", "adult")
        self.skin = rgb(SKIN[spec.get("skin", "warm")])
        self.hair_style, hc = spec.get("hair", ("short", "#333333"))
        self.hair = rgb(hc)
        self.top_kind, tc = spec.get("top", ("tee", "#888888"))
        self.top = rgb(tc)
        self.inner = rgb(spec.get("inner", "#f4f1ea"))
        self.over = spec.get("over")
        bk = spec.get("bottom")
        self.bottom_kind, self.bottom = (bk[0], rgb(bk[1])) if bk else ("none", self.top)
        self.shoes = rgb(spec.get("shoes", "#333333"))
        self.hat = spec.get("hat")
        self.acc = spec.get("acc", [])
        self.face = spec.get("face", {})
        self.stoop = spec.get("stoop", 0.0)
        # vertical layout (feet at y=70). Children and teens get bigger heads relative to body.
        k = self.k
        child = self.age == "child"
        self.head_r = (10.2 if child else 9.6 if self.age == "teen" else 9.4) * (0.96 + 0.04 * k)
        self.foot_y = 70.0
        self.leg_len = 13.0 * k * (0.86 if child else 1.0)
        self.hip_y = self.foot_y - self.leg_len
        self.torso_h = 17.5 * k * (0.84 if child else 1.0)
        self.shoulder_y = self.hip_y - self.torso_h
        self.neck_y = self.shoulder_y - 1.0
        self.head_cy = self.neck_y - self.head_r * 0.86 + self.stoop * 0.6
        self.cx = 24.0
        self.half_w = 7.4 * self.b * (0.86 if child else 1.0)
        self.arm_w = 3.3 * (0.9 + 0.15 * (self.b - 1)) * (0.9 if child else 1.0)
        self.leg_w = 3.8 * (0.9 + 0.2 * (self.b - 1)) * (0.92 if child else 1.0)
        self.arm_len = self.torso_h * 0.92

    # ------------------------------------------------------------------ parts
    def sleeve_color(self):
        if self.over and self.over[0] in ("jacket", "coat", "cardigan"):
            return rgb(self.over[1])
        if self.top_kind in ("tank",):
            return self.skin
        return self.top

    def legs(self, pen, view, phase, pose):
        cx, hip, foot = self.cx, self.hip_y, self.foot_y
        s = math.sin(phase)
        sit = pose == "sit"
        long_bottom = self.bottom_kind in ("longskirt", "sarong") or self.top_kind == "dress" and self.bottom_kind == "none" and False
        lc = self.bottom if self.bottom_kind not in ("shorts", "skirt", "none") else self.skin
        if self.top_kind == "dress":
            lc = self.skin
        for side in (-1, 1):
            if view == "side":
                swing = s * side * 5.0
                fx, fy = cx + swing, foot - max(0.0, -s * side) * 2.2
                hx = cx + side * 0.6
            else:
                lift = max(0.0, s * side) * 2.6
                fx, fy = cx + side * (self.half_w * 0.42), foot - lift
                hx = cx + side * (self.half_w * 0.4)
            if sit:
                fy = foot - 3
                fx = cx + side * self.half_w * 0.5 + (5 if view == "side" else 0)
            # upper leg in bottom colour, lower in skin for shorts/skirt
            if self.bottom_kind in ("shorts", "skirt"):
                mid_y = hip + (fy - hip) * 0.45
                pen.limb(hx, hip, fx, fy - 2, self.leg_w * 0.86, self.skin)
                pen.limb(hx, hip, hx + (fx - hx) * 0.45, mid_y, self.leg_w * 1.05, self.bottom)
            else:
                pen.limb(hx, hip, fx, fy - 2, self.leg_w, lc)
            # shoe
            if view == "side":
                pen.ellipse(fx + 1.3, fy - 0.9, 3.0, 1.9, self.shoes)
            elif view == "back":
                pen.ellipse(fx, fy - 1.0, 2.5, 1.7, self.shoes)
            else:
                pen.ellipse(fx, fy - 1.0, 2.6, 1.9, self.shoes)

    def long_bottom(self, pen, view, phase):
        """Long skirts, sarongs and dresses cover the legs down to the ankles."""
        cx, hip = self.cx, self.hip_y
        sway = math.sin(phase) * (1.3 if view == "side" else 0.6)
        hw = self.half_w * (0.98 if view != "side" else 0.7)
        bottom = self.foot_y - 2.6
        if self.top_kind == "dress":
            top_y, col = self.shoulder_y + self.torso_h * 0.55, self.top
            bottom = self.foot_y - (5.0 if self.age != "elder" else 3.0)
        else:
            top_y, col = hip - 1.5, self.bottom
        pts = [(cx - hw, top_y), (cx + hw, top_y), (cx + hw * 1.22 + sway, bottom), (cx - hw * 1.22 + sway, bottom)]
        pen.poly(pts, col)
        pat = self.s.get("pattern_bottom") if self.top_kind != "dress" else self.s.get("pattern")
        self.pattern(pen, pat, cx - hw * 1.1, top_y + 1, cx + hw * 1.1, bottom - 0.5, col)
        if self.bottom_kind == "sarong":
            pen.line(cx - hw * 0.4, top_y + 1, cx - hw * 0.1 + sway, bottom - 1, 0.6, shade(col, 0.7))

    def pattern(self, pen, kind, x0, y0, x1, y1, base):
        if not kind:
            return
        if kind == "stripes":
            y = y0 + 1.2
            while y < y1:
                pen.line(x0 + 0.6, y, x1 - 0.6, y, 0.7, shade(base, 0.72))
                y += 2.2
        elif kind == "stripes_blue":
            y = y0 + 1.2
            while y < y1:
                pen.line(x0 + 0.6, y, x1 - 0.6, y, 0.9, rgb("#3a6ea5"))
                y += 2.6
        elif kind == "plaid":
            y = y0 + 1.5
            while y < y1:
                pen.line(x0 + 0.5, y, x1 - 0.5, y, 0.5, shade(base, 0.68))
                y += 2.6
            x = x0 + 1.5
            while x < x1:
                pen.line(x, y0 + 0.5, x, y1 - 0.5, 0.5, shade(base, 1.25))
                x += 2.6
        elif kind == "batik":
            y = y0 + 1.6
            row = 0
            while y < y1 - 0.5:
                x = x0 + 1.5 + (1.3 if row % 2 else 0)
                while x < x1 - 0.8:
                    pen.dot(x, y, 0.65, shade(base, 0.62))
                    pen.dot(x, y, 0.25, rgb("#f3d38a"))
                    x += 2.6
                y += 2.4
                row += 1
        elif kind == "flowers":
            y = y0 + 1.8
            row = 0
            while y < y1 - 0.5:
                x = x0 + 1.6 + (1.5 if row % 2 else 0)
                while x < x1 - 0.8:
                    for a in range(5):
                        pen.dot(x + math.cos(a * 1.256) * 0.55, y + math.sin(a * 1.256) * 0.55, 0.42, (255, 250, 245, 255))
                    pen.dot(x, y, 0.3, rgb("#f3c04a"))
                    x += 3.1
                y += 2.9
                row += 1

    def torso(self, pen, view, phase):
        cx, sy, hy = self.cx, self.shoulder_y, self.hip_y
        hw = self.half_w * (0.62 if view == "side" else 1.0)
        top = self.top
        kind = self.top_kind
        lean = self.stoop * (0.8 if view == "side" else 0)
        # main shape: shoulders slightly rounder than hips
        bot_y = hy + (2.0 if kind in ("coat", "dress", "hoodie", "jacket", "cardigan", "uniform") else 0.6)
        if kind == "dress":
            bot_y = hy + 1
        pts = [(cx - hw + 1.2 + lean, sy), (cx + hw - 1.2 + lean, sy), (cx + hw * 1.02, bot_y), (cx - hw * 1.02, bot_y)]
        base = top if kind not in ("jacket", "cardigan", "coat") else self.inner
        if kind in ("jacket", "cardigan", "coat"):
            base = self.inner
        pen.poly(pts, base)
        pen.ellipse(cx - hw + 1.6 + lean, sy + 1.5, 2.0, 2.0, base, outline=False)
        pen.ellipse(cx + hw - 1.6 + lean, sy + 1.5, 2.0, 2.0, base, outline=False)
        self.pattern(pen, self.s.get("pattern") if kind != "dress" or True else None,
                     cx - hw + 1.2, sy + 1.5, cx + hw - 1.2, bot_y - 0.6, base)
        if kind in ("jacket", "cardigan", "coat"):
            # open front: two panels over the inner shirt
            col = top
            if view == "back":
                pen.poly(pts, col)
            elif view == "side":
                pen.poly([(cx - hw + 1.2 + lean, sy), (cx + hw * 0.3 + lean, sy), (cx + hw * 0.45, bot_y + (1.5 if kind == "coat" else 0)),
                          (cx - hw * 1.02, bot_y + (1.5 if kind == "coat" else 0))], col)
            else:
                gap = 1.8
                pen.poly([(cx - hw + 1.2, sy), (cx - gap, sy + 0.5), (cx - gap * 0.6, bot_y + (2 if kind == "coat" else 0)),
                          (cx - hw * 1.04, bot_y + (2 if kind == "coat" else 0))], col)
                pen.poly([(cx + gap, sy + 0.5), (cx + hw - 1.2, sy), (cx + hw * 1.04, bot_y + (2 if kind == "coat" else 0)),
                          (cx + gap * 0.6, bot_y + (2 if kind == "coat" else 0))], col)
                if kind == "coat":
                    for i in range(3):
                        pen.dot(cx - gap - 1.2, sy + 4 + i * 4, 0.55, shade(col, 1.5))
        if kind == "hoodie" and view != "back":
            pen.line(cx - 1.2, sy + 1, cx - 1.4, sy + 6, 0.45, (240, 240, 240, 255))
            pen.line(cx + 1.2, sy + 1, cx + 1.4, sy + 6, 0.45, (240, 240, 240, 255))
            if view == "front":
                pen.rrect(cx - hw * 0.55, hy - 5.5, cx + hw * 0.55, hy - 1.2, 1.2, shade(top, 0.86))
        if kind == "hoodie" and view == "back":
            pen.ellipse(cx, sy + 2.2, hw * 0.7, 3.0, shade(top, 0.9))
        if kind in ("shirt", "uniform", "polo", "blouse") and view == "front":
            collar = (255, 255, 255, 255) if kind != "blouse" else shade(top, 1.2)
            if kind == "polo":
                collar = shade(top, 1.25)
            pen.poly([(cx - 3.2, sy - 0.2), (cx, sy + 2.4), (cx - 0.6, sy + 3.2), (cx - 3.6, sy + 1.2)], collar)
            pen.poly([(cx + 3.2, sy - 0.2), (cx, sy + 2.4), (cx + 0.6, sy + 3.2), (cx + 3.6, sy + 1.2)], collar)
            if kind in ("shirt", "uniform"):
                for i in range(3):
                    pen.dot(cx, sy + 4.2 + i * 3.6, 0.42, shade(top, 0.6))
        if kind == "uniform" and view == "front":
            pen.rrect(cx + 1.8, sy + 3.5, cx + 4.6, sy + 6.0, 0.4, rgb("#f6e27a"))
            pen.line(cx - hw + 1.4, hy - 1.4, cx + hw - 1.4, hy - 1.4, 1.1, rgb("#283a5e"))
        if kind == "tank" and view != "back":
            pen.pieslice(cx, sy - 0.8, 3.2, 3.2, 0, 180, self.skin, outline=False)
        # belt line where top meets trousers
        if self.bottom_kind in ("pants", "cargo", "shorts") and kind in ("shirt", "tee", "polo", "uniform", "tank"):
            pen.line(cx - hw + 0.5, hy - 0.2, cx + hw - 0.5, hy - 0.2, 0.9, shade(self.bottom, 0.7))
        if self.bottom_kind == "cargo" and view != "back":
            for sd in (-1, 1):
                pen.rrect(cx + sd * hw * 0.9 - 1.4, hy + 3, cx + sd * hw * 0.9 + 1.4, hy + 6, 0.4, shade(self.bottom, 0.85))

    def over_layer(self, pen, view):
        if not self.over:
            return
        kind, col = self.over[0], rgb(self.over[1])
        cx, sy, hy = self.cx, self.shoulder_y, self.hip_y
        hw = self.half_w * (0.62 if view == "side" else 1.0)
        if kind == "apron":
            if view == "back":
                pen.line(cx - hw + 1.5, sy + 7, cx + hw - 1.5, sy + 7, 0.9, col)
                pen.line(cx - 0.8, sy + 7, cx - 2, sy + 10, 0.8, col)
                pen.line(cx + 0.8, sy + 7, cx + 2, sy + 10, 0.8, col)
                return
            w0 = hw * (0.72 if view == "front" else 0.9)
            x = cx + (1.2 if view == "side" else 0)
            pen.rrect(x - w0 * 0.75, sy + 1.2, x + w0 * 0.75, sy + 7.5, 1.0, col)
            pen.poly([(x - w0, sy + 6.5), (x + w0, sy + 6.5), (x + w0 * 1.08, hy + 6.5), (x - w0 * 1.08, hy + 6.5)], col)
            if view == "front":
                pen.rrect(x - w0 * 0.55, hy - 0.5, x + w0 * 0.55, hy + 3.2, 0.6, shade(col, 0.85))
                pen.line(cx - 2.4, sy + 1.2, cx - 3.6, sy - 0.6, 0.6, col)
                pen.line(cx + 2.4, sy + 1.2, cx + 3.6, sy - 0.6, 0.6, col)
        elif kind == "vest":
            if view == "back":
                pen.poly([(cx - hw + 1.0, sy + 0.2), (cx + hw - 1.0, sy + 0.2), (cx + hw * 1.03, hy + 0.5), (cx - hw * 1.03, hy + 0.5)], col)
            elif view == "side":
                pen.poly([(cx - hw + 1.0, sy + 0.2), (cx + hw * 0.4, sy + 0.2), (cx + hw * 0.55, hy + 0.5), (cx - hw * 1.03, hy + 0.5)], col)
            else:
                pen.poly([(cx - hw + 1.0, sy + 0.2), (cx - 2.2, sy + 0.8), (cx - 1.6, hy + 0.5), (cx - hw * 1.04, hy + 0.5)], col)
                pen.poly([(cx + 2.2, sy + 0.8), (cx + hw - 1.0, sy + 0.2), (cx + hw * 1.04, hy + 0.5), (cx + 1.6, hy + 0.5)], col)
                for sd in (-1, 1):
                    pen.rrect(cx + sd * (hw * 0.62) - 1.4, hy - 5, cx + sd * (hw * 0.62) + 1.4, hy - 2.6, 0.3, shade(col, 0.8))
        elif kind == "shawl":
            if view == "back":
                pen.poly([(cx - hw - 0.5, sy - 0.5), (cx + hw + 0.5, sy - 0.5), (cx, sy + 9)], col)
            else:
                pen.poly([(cx - hw - 0.8, sy - 0.2), (cx + hw + 0.8, sy - 0.2), (cx + hw * 0.6, sy + 5.5), (cx, sy + 7.5), (cx - hw * 0.6, sy + 5.5)], col)
                pen.dot(cx, sy + 3.2, 0.9, rgb("#c9a35a"))

    def arm(self, pen, side, view, sh_ang, el_ang, front=True, hold=None):
        """sh_ang: shoulder angle from straight down (deg, + = forward/outward); el_ang: elbow bend."""
        cx = self.cx
        hw = self.half_w * (0.62 if view == "side" else 1.0)
        sx = cx + (side * (hw - 0.6) if view != "side" else side * 0.8)
        sy = self.shoulder_y + 1.6
        up = self.arm_len * 0.52
        lo = self.arm_len * 0.48
        if view == "side":
            a1 = math.radians(sh_ang)
            ex, ey = sx + math.sin(a1) * up, sy + math.cos(a1) * up
            a2 = math.radians(sh_ang + el_ang)
            hx, hy = ex + math.sin(a2) * lo, ey + math.cos(a2) * lo
        else:
            a1 = math.radians(sh_ang)
            ex, ey = sx + side * math.sin(a1) * up * 0.9, sy + math.cos(a1) * up
            a2 = math.radians(sh_ang + el_ang)
            hx, hy = ex + side * math.sin(a2) * lo * 0.9, ey + math.cos(a2) * lo
        sc = self.sleeve_color()
        short = self.top_kind in ("tee", "polo", "tank") or self.s.get("sleeves") == "rolled"
        if short:
            pen.limb(sx, sy, ex, ey, self.arm_w, self.skin)
            pen.limb(ex, ey, hx, hy, self.arm_w * 0.92, self.skin)
            if self.top_kind != "tank":
                mx, my = sx + (ex - sx) * (0.55 if self.s.get("sleeves") != "rolled" else 0.85), sy + (ey - sy) * (0.55 if self.s.get("sleeves") != "rolled" else 0.85)
                pen.limb(sx, sy, mx, my, self.arm_w * 1.12, sc)
        else:
            pen.limb(sx, sy, ex, ey, self.arm_w * 1.05, sc)
            pen.limb(ex, ey, hx, hy, self.arm_w, sc)
        hand = rgb("#e9e2d0") if "gloves" in self.acc else self.skin
        pen.ellipse(hx, hy + 0.4, self.arm_w * 0.62, self.arm_w * 0.62, hand)
        if hold:
            self.held(pen, hold, hx, hy, view, side)
        return hx, hy

    def held(self, pen, what, hx, hy, view, side):
        if what == "book":
            pen.rrect(hx - 3.0, hy - 3.2, hx + 3.0, hy + 1.2, 0.4, rgb("#3b6aa0"))
            pen.line(hx, hy - 3.0, hx, hy + 1.0, 0.4, rgb("#f3efe4"))
        elif what == "can":
            pen.rrect(hx - 1.8, hy - 2.5, hx + 2.6, hy + 2, 0.8, rgb("#5f9ec2"))
            pen.line(hx + 2.6, hy - 1, hx + 5.5, hy - 2.6, 0.7, rgb("#5f9ec2"))
        elif what == "broom":
            pen.line(hx, hy - 9, hx + side * 1.5, hy + 9, 0.9, rgb("#8a5a2e"))
            pen.poly([(hx + side * 1.5 - 2.4, hy + 8), (hx + side * 1.5 + 2.4, hy + 8), (hx + side * 1.5 + 3.4, hy + 12), (hx + side * 1.5 - 3.4, hy + 12)], rgb("#d8b860"))
        elif what == "phone":
            pen.rrect(hx - 1.4, hy - 2.6, hx + 1.4, hy + 0.8, 0.4, rgb("#2b2b35"))
        elif what == "gift":
            pen.rrect(hx - 2.4, hy - 2.6, hx + 2.4, hy + 1.6, 0.4, rgb("#e88aa8"))
            pen.line(hx, hy - 2.6, hx, hy + 1.6, 0.6, rgb("#f6e27a"))
        elif what == "basket":
            pen.pieslice(hx, hy, 3.6, 3.0, 0, 180, rgb("#c99a5b"))
            pen.arc(hx, hy, 3.0, 3.6, 180, 360, 0.6, rgb("#8a6236"))
            pen.dot(hx - 1.2, hy + 0.2, 0.9, rgb("#e2564e"))
            pen.dot(hx + 1.0, hy + 0.1, 0.9, rgb("#8fc65a"))

    # ------------------------------------------------------------------ head
    def head(self, pen, view, blink=False, expr="normal", bob=0.0, tilt=0.0):
        cx = self.cx + tilt
        cy = self.head_cy + bob
        r = self.head_r
        hs, hcol = self.hair_style, self.hair
        hijab = hs == "hijab"
        # neck
        if not hijab:
            pen.rrect(cx - 1.6, min(cy + r * 0.7, self.shoulder_y), cx + 1.6, self.shoulder_y + 1.0, 0.8, shade(self.skin, 0.92))
        # back hair layers
        if view != "side" or True:
            self.hair_back(pen, view, cx, cy, r)
        if hijab:
            self.hijab(pen, view, cx, cy, r)
            return
        # face
        if view == "side":
            pen.ellipse(cx + 0.8, cy, r * 0.94, r * 0.98, self.skin)
            pen.ellipse(cx - r * 0.12, cy + 1.0, r * 0.17, r * 0.22, shade(self.skin, 0.94), outline=False)     # ear
            pen.arc(cx - r * 0.12, cy + 1.0, r * 0.12, r * 0.16, 100, 260, 0.4, shade(self.skin, 0.72))
        else:
            pen.ellipse(cx, cy, r, r * 0.98, self.skin)
            if view == "front":
                for sd in (-1, 1):
                    pen.ellipse(cx + sd * r * 0.98, cy + 1.2, r * 0.16, r * 0.24, self.skin)
        if view != "back":
            self.face_features(pen, view, cx, cy, r, blink, expr)
        self.hair_front(pen, view, cx, cy, r)
        self.headwear(pen, view, cx, cy, r)

    def face_features(self, pen, view, cx, cy, r, blink, expr):
        f = self.face
        ink = rgb("#2b2030")
        eye_y = cy + r * 0.18
        if view == "side":
            xs = [cx + r * 0.58]
        else:
            xs = [cx - r * 0.38, cx + r * 0.38]
        smile_eyes = f.get("eyes") == "smile" or expr in ("senang", "tertawa", "tersenyum")
        for ex in xs:
            if blink or smile_eyes:
                pen.arc(ex, eye_y + 0.4, 1.5, 1.2, 200, 340, 0.55, ink)
            elif expr == "kaget":
                pen.dot(ex, eye_y, 1.45, (255, 255, 255, 255))
                pen.dot(ex, eye_y, 0.9, ink)
            else:
                pen.dot(ex, eye_y, 1.25, ink)
                pen.dot(ex + 0.45, eye_y - 0.5, 0.42, (255, 255, 255, 255))
            brow = f.get("brows", "normal")
            by = eye_y - 2.6 - (0.6 if expr == "kaget" else 0)
            bcol = shade(self.hair, 0.8) if self.hair_style not in ("hijab",) else ink
            if self.age == "elder" or self.hair_style in ("bald_sides",):
                bcol = rgb("#b9b5b0")
            if brow == "sharp":
                pen.line(ex - 1.4, by + 0.3, ex + 1.4, by - 0.3 if ex < cx else by + 0.3, 0.55, bcol)
            elif expr == "sedih":
                pen.line(ex - 1.3, by - (0.5 if ex < cx else -0.3), ex + 1.3, by + (0.3 if ex < cx else -0.5), 0.5, bcol)
            else:
                pen.arc(ex, by + 0.8, 1.4, 0.9, 200, 340, 0.45, bcol)
        if f.get("blush") or expr in ("malu", "senang"):
            for ex in xs:
                pen.dot(ex + (-0.4 if ex < cx else 0.4), eye_y + 2.4, 1.15, (240, 130, 140, 110))
        if self.age in ("elder",):
            for ex in xs:
                pen.arc(ex + (1.8 if ex >= cx else -1.8), eye_y + 0.2, 0.8, 0.6, 270, 90 if ex >= cx else 270, 0.3, shade(self.skin, 0.75))
        # glasses
        g = f.get("glasses")
        if g:
            gc = rgb("#4a3b38") if g == "square" else rgb("#8a6a3f")
            for ex in xs:
                if g == "round":
                    pen.arc(ex, eye_y, 2.1, 2.1, 0, 360, 0.42, gc)
                else:
                    a, b = pen.p(ex - 2.2, eye_y - 1.7)
                    c, d = pen.p(ex + 2.2, eye_y + 1.6)
                    pen.d.rounded_rectangle((a, b, c, d), radius=SS * 0.5 * pen.g, outline=gc, width=int(0.42 * SS * pen.g))
            if view != "side":
                pen.line(xs[0] + 2.0, eye_y - 0.2, xs[1] - 2.0, eye_y - 0.2, 0.36, gc)
        # mouth
        my = cy + r * 0.56
        mx = cx + (r * 0.5 if view == "side" else 0)
        if expr == "kaget":
            pen.ellipse(mx, my + 0.2, 0.9, 1.1, rgb("#8a3b45"), outline=False)
        elif expr in ("senang", "tertawa"):
            pen.pieslice(mx, my - 0.4, 1.7, 1.5, 0, 180, rgb("#9b3d4a"), outline=False)
        elif expr == "sedih":
            pen.arc(mx, my + 1.0, 1.3, 0.8, 200, 340, 0.45, ink)
        else:
            pen.arc(mx, my - 0.5, 1.3, 0.9, 20, 160, 0.45, ink)
        # facial hair
        m = f.get("moustache")
        if m:
            mc = rgb("#f2f0ec") if m == "white" else shade(self.hair, 0.9)
            if view == "side":
                pen.ellipse(mx + 0.2, my - 1.0, 1.4, 0.6, mc, outline=False)
            else:
                pen.ellipse(mx - 1.2, my - 1.1, 1.4, 0.65, mc, outline=False)
                pen.ellipse(mx + 1.2, my - 1.1, 1.4, 0.65, mc, outline=False)
        bd = f.get("beard")
        if bd:
            bc = shade(self.hair, 0.95)
            if view == "side":
                pen.pieslice(cx + 1.6, cy + r * 0.45, r * 0.68, r * 0.55 if bd == "full" else r * 0.4, 0, 180, bc, outline=False)
            else:
                pen.pieslice(cx, cy + r * 0.42, r * 0.8, r * 0.6 if bd == "full" else r * 0.42, 0, 180, bc, outline=False)
                pen.ellipse(mx, my - 0.1, 1.2, 0.5, self.skin, outline=False)

    def hair_back(self, pen, view, cx, cy, r):
        hs, c = self.hair_style, self.hair
        if hs == "long":
            pen.rrect(cx - r * 1.02, cy - r * 0.3, cx + r * 1.02, cy + r * 1.75, r * 0.4, c)
        elif hs == "wavy":
            for i in range(5):
                x = cx - r * 0.95 + i * r * 0.475
                pen.ellipse(x, cy + r * 1.05, r * 0.32, r * 0.62, c)
            pen.rrect(cx - r * 1.0, cy - r * 0.2, cx + r * 1.0, cy + r * 1.05, r * 0.5, c)
        elif hs == "bob":
            pen.rrect(cx - r * 1.08, cy - r * 0.4, cx + r * 1.08, cy + r * 0.78, r * 0.45, c)
        elif hs == "pigtails" and view != "side":
            for sd in (-1, 1):
                pen.ellipse(cx + sd * r * 1.12, cy + r * 0.55, r * 0.34, r * 0.62, c)
        elif hs == "pigtails" and view == "side":
            pen.ellipse(cx - r * 0.95, cy + r * 0.5, r * 0.34, r * 0.62, c)
        elif hs == "bun" and view in ("back", "side"):
            pen.ellipse(cx - (r * 0.75 if view == "side" else 0), cy - r * (0.55 if view == "side" else 0.25), r * 0.45, r * 0.42, c)

    def hair_front(self, pen, view, cx, cy, r):
        hs, c = self.hair_style, self.hair
        hi = shade(c, 1.28)
        if hs in ("bald_sides",):
            if view != "front":
                pen.pieslice(cx - (r * 0.2 if view == "side" else 0), cy + r * 0.2, r * 0.98, r * 0.6, 0, 180, c, outline=False)
            else:
                for sd in (-1, 1):
                    pen.ellipse(cx + sd * r * 0.9, cy - r * 0.12, r * 0.14, r * 0.26, c, outline=False)
            pen.dot(cx - r * 0.3, cy - r * 0.55, r * 0.18, (255, 255, 255, 90))
            return
        if hs == "balding":
            if view == "back":
                pen.pieslice(cx, cy + r * 0.05, r * 1.0, r * 0.95, 0, 180, c, outline=False)
            elif view == "side":
                pen.pieslice(cx - r * 0.25, cy + r * 0.05, r * 0.85, r * 0.85, 90, 250, c, outline=False)
            else:
                for sd in (-1, 1):
                    pen.ellipse(cx + sd * r * 0.9, cy - r * 0.15, r * 0.14, r * 0.3, c, outline=False)
            pen.dot(cx - r * 0.3, cy - r * 0.6, r * 0.2, (255, 255, 255, 80))
            return
        if hs == "buzz":
            bc = tuple(int(c[i] * 0.55 + self.skin[i] * 0.45) for i in range(3)) + (255,)
            if view == "back":
                pen.ellipse(cx, cy - r * 0.05, r * 1.0, r * 0.95, bc, outline=False)
                pen.arc(cx, cy - r * 0.3, r * 0.6, r * 0.4, 200, 320, 0.5, shade(bc, 1.25))
            else:
                pen.pieslice(cx + (-r * 0.15 if view == "side" else 0), cy - r * 0.15, r * 1.0, r * 0.9, 180, 360, bc, outline=False)
            return
        if view == "back":
            top = {"long": 1.0, "wavy": 1.0, "bob": 0.8}.get(hs, 0.62)
            pen.ellipse(cx, cy - r * 0.05, r * 1.04, r * (0.96 + top * 0.08), c)
            if hs == "ponytail":
                pen.ellipse(cx, cy + r * 0.8, r * 0.3, r * 0.7, c)
            if hs == "bun":
                pen.ellipse(cx, cy - r * 0.5, r * 0.45, r * 0.42, c)
            if hs == "undercut":
                pen.pieslice(cx, cy + r * 0.25, r * 0.98, r * 0.7, 0, 180, shade(c, 0.7), outline=False)
            pen.arc(cx - r * 0.15, cy - r * 0.35, r * 0.55, r * 0.35, 200, 300, 0.7, hi)
            return
        side = view == "side"
        ox = -r * 0.18 if side else 0.0
        # skull cap
        pen.pieslice(cx + ox, cy - r * 0.02, r * 1.06, r * 1.04, 180, 360, c)
        if hs in ("short", "undercut", "curly", "curly_short", "spiky", "bun", "long", "wavy", "bob", "pigtails"):
            # fringe
            if hs == "spiky":
                for i in range(6):
                    x = cx + ox - r * 0.95 + i * r * 0.38
                    pen.poly([(x - r * 0.24, cy - r * 0.2), (x + r * 0.05, cy - r * 1.28 - (i % 2) * 1.0), (x + r * 0.3, cy - r * 0.15)], c, outline=False)
                pen.poly([(cx + ox - r, cy - r * 0.1), (cx + ox + r, cy - r * 0.1), (cx + ox + r * 0.6, cy + r * 0.22), (cx + ox - r * 0.7, cy + r * 0.26)], c, outline=False)
            elif hs in ("curly", "curly_short"):
                n = 7 if hs == "curly" else 6
                for i in range(n):
                    a = math.pi * (1.05 + i * 0.9 / (n - 1))
                    pen.ellipse(cx + ox + math.cos(a) * r * 0.92, cy + math.sin(a) * r * 0.86 - 0.4, r * 0.36, r * 0.36, c)
                pen.ellipse(cx + ox, cy - r * 0.7, r * 0.5, r * 0.4, c, outline=False)
            elif hs == "undercut":
                pen.poly([(cx + ox - r * 1.0, cy - r * 0.2), (cx + ox - r * 0.2, cy - r * 1.15), (cx + ox + r * 1.05, cy - r * 0.55),
                          (cx + ox + r * 0.9, cy - r * 0.05), (cx + ox + r * 0.1, cy - r * 0.45), (cx + ox - r * 0.6, cy + r * 0.05)], c)
                if not side:
                    for sd in (-1, 1):
                        pen.rrect(cx + sd * r * 0.9 - 0.4, cy - r * 0.25, cx + sd * r * 0.9 + 0.4, cy + r * 0.1, 0.3, shade(c, 0.85), outline=False)
            elif hs == "bob":
                pen.rrect(cx + ox - r * 1.0, cy - r * 0.62, cx + ox + r * 1.0, cy - r * 0.15, r * 0.2, c, outline=False)
                if not side:
                    for sd in (-1, 1):
                        pen.rrect(cx + sd * r * 0.82 - r * 0.28, cy - r * 0.3, cx + sd * r * 0.82 + r * 0.28, cy + r * 0.78, r * 0.25, c)
            elif hs in ("long", "wavy"):
                pen.poly([(cx + ox - r * 1.0, cy - r * 0.2), (cx + ox - r * 0.1, cy - r * 0.95), (cx + ox + r * 0.2, cy - r * 0.35), (cx + ox + r * 1.0, cy - r * 0.15),
                          (cx + ox + r * 0.9, cy - r * 0.8), (cx + ox - r * 0.9, cy - r * 0.8)], c, outline=False)
                if not side:
                    for sd in (-1, 1):
                        pen.rrect(cx + sd * r * 0.9 - r * 0.22, cy - r * 0.3, cx + sd * r * 0.9 + r * 0.22, cy + r * 1.1, r * 0.2, c)
            else:
                pen.poly([(cx + ox - r * 1.02, cy - r * 0.05), (cx + ox - r * 0.6, cy - r * 0.62), (cx + ox + r * 0.3, cy - r * 0.42),
                          (cx + ox + r * 1.02, cy - r * 0.1), (cx + ox + r * 0.9, cy - r * 0.8), (cx + ox - r * 0.9, cy - r * 0.8)], c, outline=False)
                if hs == "pigtails" and not side:
                    for sd in (-1, 1):
                        pen.ellipse(cx + sd * r * 0.9, cy - r * 0.5, r * 0.22, r * 0.2, rgb("#f05a8a"))
            if hs == "bun" and view == "front":
                pen.ellipse(cx, cy - r * 0.98, r * 0.42, r * 0.36, c)
                pen.line(cx - r * 0.5, cy - r * 1.05, cx + r * 0.45, cy - r * 0.92, 0.45, rgb("#c99a5b"))
            # highlight
            pen.arc(cx + ox - r * 0.2, cy - r * 0.55, r * 0.5, r * 0.25, 200, 300, 0.6, hi)
        if hs == "ponytail" and side:
            pen.ellipse(cx - r * 1.05, cy + r * 0.2, r * 0.3, r * 0.75, c)

    def hijab(self, pen, view, cx, cy, r):
        c = self.hair
        dark = shade(c, 0.82)
        # drape over shoulders and chest
        pen.poly([(cx - r * 1.15, cy + r * 0.3), (cx + r * 1.15, cy + r * 0.3), (cx + r * 1.0, self.shoulder_y + 5.5),
                  (cx, self.shoulder_y + 7.2), (cx - r * 1.0, self.shoulder_y + 5.5)], c)
        pen.ellipse(cx, cy - r * 0.05, r * 1.12, r * 1.08, c)
        if view == "back":
            pen.arc(cx, cy + r * 0.3, r * 0.8, r * 0.7, 30, 150, 0.5, dark)
            return
        ox = r * 0.22 if view == "side" else 0
        # face opening
        pen.ellipse(cx + ox, cy + r * 0.12, r * 0.78, r * 0.82, self.skin, outline=False)
        pen.arc(cx + ox, cy + r * 0.12, r * 0.8, r * 0.84, 0, 360, 0.5, dark)
        self.face_features(pen, view, cx + ox * 0.5, cy + r * 0.05, r * 0.86, False, "normal")
        # folds
        pen.arc(cx, self.shoulder_y + 2.0, r * 0.9, 2.2, 20, 160, 0.45, dark)
        if "flower_pin" in self.acc:
            pen.dot(cx + r * 0.75, cy + r * 0.62, 1.1, rgb("#f07aa0"))
            pen.dot(cx + r * 0.75, cy + r * 0.62, 0.45, rgb("#f6e27a"))

    def headwear(self, pen, view, cx, cy, r):
        if not self.hat:
            if "headband" in self.acc and view != "back":
                pen.arc(cx, cy + r * 0.1, r * 1.0, r * 0.98, 200, 340, 0.9, rgb("#e4508a"))
            if "hairclip" in self.acc and view != "back":
                pen.rrect(cx + r * 0.35, cy - r * 0.62, cx + r * 0.85, cy - r * 0.45, 0.2, rgb("#e8c35a"))
            if "headphones" in self.acc:
                pass
            return
        kind, col = self.hat[0], rgb(self.hat[1])
        dark = shade(col, 0.8)
        if kind == "bucket":
            pen.ellipse(cx, cy - r * 0.45, r * 1.35, r * 0.38, dark)
            pen.rrect(cx - r * 0.85, cy - r * 1.2, cx + r * 0.85, cy - r * 0.42, r * 0.35, col)
        elif kind == "straw":
            pen.ellipse(cx, cy - r * 0.48, r * 1.6, r * 0.42, col)
            pen.rrect(cx - r * 0.75, cy - r * 1.18, cx + r * 0.75, cy - r * 0.5, r * 0.3, col)
            pen.line(cx - r * 0.75, cy - r * 0.62, cx + r * 0.75, cy - r * 0.62, 0.8, rgb("#9b3d3a"))
        elif kind in ("postcap", "cap_back"):
            pen.pieslice(cx, cy - r * 0.32, r * 1.02, r * 0.86, 180, 360, col)
            if kind == "postcap":
                if view == "front":
                    pen.ellipse(cx, cy - r * 0.34, r * 0.95, r * 0.2, dark)
                    pen.dot(cx, cy - r * 0.75, 1.0, rgb("#f6e27a"))
                elif view == "side":
                    pen.ellipse(cx + r * 0.85, cy - r * 0.36, r * 0.55, r * 0.16, dark)
            else:
                if view == "back":
                    pen.ellipse(cx, cy - r * 0.36, r * 0.75, r * 0.18, dark)
                elif view == "side":
                    pen.ellipse(cx - r * 0.95, cy - r * 0.38, r * 0.5, r * 0.15, dark)
                pen.dot(cx, cy - r * 1.05, 0.7, dark)
        elif kind == "bandana":
            pen.pieslice(cx, cy - r * 0.18, r * 1.06, r * 0.92, 180, 360, col)
            for i in range(4):
                pen.dot(cx - r * 0.6 + i * r * 0.4, cy - r * 0.55, 0.5, (255, 255, 255, 220))
            if view in ("back", "side"):
                bx = cx - (r * 0.9 if view == "side" else 0)
                pen.poly([(bx, cy - r * 0.3), (bx - 2.6, cy + r * 0.4), (bx - 0.6, cy + r * 0.5)], col)
        elif kind == "beret":
            pen.ellipse(cx + r * 0.18, cy - r * 0.68, r * 1.02, r * 0.45, col)
            pen.dot(cx + r * 0.2, cy - r * 1.12, 0.6, dark)
        elif kind == "peci":
            pen.rrect(cx - r * 0.86, cy - r * 1.12, cx + r * 0.86, cy - r * 0.45, r * 0.12, col)
        elif kind == "beanie":
            pen.pieslice(cx, cy - r * 0.25, r * 1.04, r * 0.98, 180, 360, col)
            pen.rrect(cx - r * 1.02, cy - r * 0.45, cx + r * 1.02, cy - r * 0.18, r * 0.12, dark)
            pen.dot(cx, cy - r * 1.22, 1.2, shade(col, 1.15))

    # ------------------------------------------------------------------ accessories
    def back_acc(self, pen, view):
        cx, sy = self.cx, self.shoulder_y
        hw = self.half_w
        if "backpack" in self.acc:
            col = rgb("#3a7bd5")
            if view == "back":
                pen.rrect(cx - hw * 0.8, sy + 1, cx + hw * 0.8, sy + self.torso_h * 0.85, 2.0, col)
                pen.rrect(cx - hw * 0.5, sy + self.torso_h * 0.45, cx + hw * 0.5, sy + self.torso_h * 0.75, 1.0, shade(col, 0.85))
            elif view == "side":
                pen.rrect(cx - hw * 0.62 - 3.6, sy + 1.2, cx - hw * 0.62 + 0.6, sy + self.torso_h * 0.82, 1.5, col)

    def front_acc(self, pen, view, phase):
        cx, sy, hy = self.cx, self.shoulder_y, self.hip_y
        hw = self.half_w * (0.62 if view == "side" else 1.0)
        if "backpack" in self.acc and view == "front":
            for sd in (-1, 1):
                pen.line(cx + sd * (hw - 2.0), sy + 0.5, cx + sd * (hw - 2.4), sy + 7, 1.0, rgb("#2c5ea6"))
        if "satchel" in self.acc:
            col = rgb("#8a5a2e")
            if view != "back":
                pen.line(cx - hw + 1.5, sy + 0.5, cx + hw - 1.0, hy - 2, 1.0, shade(col, 0.8))
            bx = cx + (hw - 0.5 if view != "side" else 1.5)
            if view != "back" or True:
                pen.rrect(bx - 3.2, hy - 3.5, bx + 2.6, hy + 2.5, 0.8, col)
                pen.rrect(bx - 3.2, hy - 3.5, bx + 2.6, hy - 1.4, 0.5, shade(col, 0.85))
        if "headphones" in self.acc:
            pen.arc(cx, sy + 0.2, 4.4, 2.6, 0, 180, 1.1, rgb("#2a2a33"))
            if view != "back":
                for sd in (-1, 1):
                    pen.ellipse(cx + sd * 4.2, sy + 0.8, 1.5, 1.8, rgb("#3b3b48"))
        if "star_scarf" in self.acc:
            col = rgb("#f0d36b")
            pen.rrect(cx - hw * 0.9, sy - 1.2, cx + hw * 0.9, sy + 1.6, 1.2, col)
            if view == "front":
                pen.rrect(cx + 1.0, sy + 1, cx + 3.4, sy + 8, 0.8, col)
                pen.dot(cx + 2.2, sy + 5.5, 0.7, rgb("#26345e"))
            elif view == "back":
                pen.rrect(cx - 1.4, sy + 1, cx + 1.2, sy + 6.5, 0.8, col)
        if "towel" in self.acc and view != "back":
            pen.rrect(cx + hw * 0.2, sy - 1, cx + hw + 0.6, sy + 4.5, 0.8, rgb("#f2f2f2"))
            pen.line(cx + hw * 0.2, sy + 2.4, cx + hw + 0.6, sy + 2.4, 0.5, rgb("#d1453b"))
        if "pearls" in self.acc and view == "front":
            for i in range(7):
                a = math.pi * (0.15 + i * 0.7 / 6)
                pen.dot(cx + math.cos(a) * 3.6, sy + 0.6 + math.sin(a) * 2.6, 0.5, (250, 248, 240, 255))
        if "ribbons" in self.acc and view == "back":
            for sd in (-1, 1):
                pen.dot(self.cx + sd * self.head_r * 0.9, self.head_cy - self.head_r * 0.5, 1.2, rgb("#f05a8a"))

    def cane(self, pen, view, side_x, hy):
        if "cane" not in self.acc:
            return
        pen.line(side_x, hy - 1, side_x + 0.6, self.foot_y - 0.5, 1.0, rgb("#7a5233"))
        pen.arc(side_x - 1.2, hy - 1, 1.4, 1.3, 180, 360, 1.0, rgb("#7a5233"))

    # ------------------------------------------------------------------ whole frame
    def frame(self, view, phase=0.0, walking=False, pose=None, f=0, blink=False):
        """view: front/back/side (side faces right)."""
        pen = Pen()
        sp = math.sin(phase) if walking else 0.0
        bob = -abs(sp) * 0.6 if walking else 0.0
        # arm angles per pose: (left sh, left el, right sh, right el, hold_l, hold_r)
        swing = sp * 26 if walking else 0.0
        la, le, ra, re = -swing + 6, 8, swing + 6, 8
        hold_l = hold_r = None
        if view == "side":
            la, le, ra, re = -swing, 12, swing, 12
        if "cane" in self.acc and not pose:
            ra, re = (10, 22) if view != "side" else (20 + swing * 0.3, 20)
        if "basket" in self.acc and not pose:
            la, le, hold_l = 4, 82, "basket"
        if "book" in self.acc and not pose:
            la, le, hold_l = 6, 95, "book"
        if pose:
            wave = (12 if f else -12)
            P = {
                "sit": (10, 40, 10, 40), "wave": (8, 8, 160 + wave * 0.5, 25 + wave), "give": (8, 8, 70, 10),
                "reach": (8, 8, 125, 5), "bow": (-10, 10, -10, 10), "hold_l": (5, 85, 8, 8), "hold_r": (8, 8, 5, 85),
                "cheer": (150 + wave * 0.6, 15, 150 - wave * 0.6, 15), "hug": (65, 55, 65, 55), "lean": (25, 30, 8, 8),
                "photo": (50, 125, 50, 125), "highfive": (8, 8, 150, 8), "dance": (90 + wave * 2, 30, 90 - wave * 2, 30),
                "read": (35, 95, 35, 95), "water": (8, 8, 60, 20), "sweep": (30 + wave, 45, 20 - wave, 50),
            }
            la, le, ra, re = P.get(pose, (la, le, ra, re))
            hold_l = {"hold_l": "gift", "read": "book"}.get(pose)
            hold_r = {"hold_r": "gift", "water": "can", "sweep": "broom", "photo": "phone"}.get(pose)
        sit = pose == "sit"
        bow = pose == "bow"
        oy = 4.0 if sit else 0.0
        pen.oy = oy
        tilt = 1.5 if bow else 0.0
        long = self.bottom_kind in ("longskirt", "sarong") or self.top_kind == "dress"
        if view == "back":
            self.arm(pen, -1, view, la, le)
            self.arm(pen, 1, view, ra, re)
            if long:
                self.long_bottom(pen, view, phase if walking else 0)
                self.legs_feet_only(pen, view, phase if walking else 0)
            else:
                self.legs(pen, view, phase if walking else 0, pose)
            self.torso(pen, view, phase)
            self.over_layer(pen, view)
            self.back_acc(pen, view)
            self.front_acc(pen, view, phase)
            self.head(pen, view, bob=bob + (2 if bow else 0))
        elif view == "side":
            self.back_acc(pen, view)
            # far arm behind the body
            self.arm(pen, -1, view, -la if not pose else la, le)
            if long:
                self.legs_feet_only(pen, view, phase if walking else 0)
                self.long_bottom(pen, view, phase if walking else 0)
            else:
                self.legs(pen, view, phase if walking else 0, pose)
            self.torso(pen, view, phase)
            self.over_layer(pen, view)
            self.front_acc(pen, view, phase)
            self.head(pen, view, blink, bob=bob + (2.5 if bow else 0), tilt=tilt * 1.5)
            hx, hy = self.arm(pen, 1, view, ra, re, hold=hold_r or hold_l)
            self.cane(pen, view, hx, hy)
        else:
            if long:
                self.legs_feet_only(pen, view, phase if walking else 0)
                self.long_bottom(pen, view, phase if walking else 0)
            else:
                self.legs(pen, view, phase if walking else 0, pose)
            self.back_acc(pen, view)
            self.torso(pen, view, phase)
            self.over_layer(pen, view)
            self.front_acc(pen, view, phase)
            hxl, hyl = self.arm(pen, -1, view, la, le, hold=hold_l)
            hxr, hyr = self.arm(pen, 1, view, ra, re, hold=hold_r)
            self.cane(pen, view, hxr, hyr)
            self.head(pen, view, blink, bob=bob + (2.5 if bow else 0))
        return pen.out()

    def legs_feet_only(self, pen, view, phase):
        s = math.sin(phase)
        for side in (-1, 1):
            if view == "side":
                fx = self.cx + s * side * 3.0
                pen.ellipse(fx + 1.3, self.foot_y - 0.9, 2.8, 1.8, self.shoes)
            else:
                fx = self.cx + side * self.half_w * 0.42
                pen.ellipse(fx, self.foot_y - 1.0 - max(0, s * side) * 1.2, 2.5, 1.8, self.shoes)


# ----------------------------------------------------------------------------- sheets
VIEWS = [("front", False), ("side", True), ("side", False), ("back", False)]   # down, left, right, up


def sheet(fig, cols, fn):
    w, h = FW * OUT_K, FH * OUT_K
    im = Image.new("RGBA", (cols * w, 4 * h), (0, 0, 0, 0))
    for row, (view, mirror) in enumerate(VIEWS):
        for col in range(cols):
            fr = fn(view, col)
            if mirror:
                fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
            im.alpha_composite(fr, (col * w, row * h))
    return im


def build(fig):
    walk = sheet(fig, 24, lambda v, c: fig.frame(v, phase=c / 24 * math.tau, walking=True))
    idle = sheet(fig, 12, lambda v, c: fig.frame(v, blink=(c == 7)))
    w, h = FW * OUT_K, FH * OUT_K
    poses = Image.new("RGBA", (8 * w, len(POSES) * h), (0, 0, 0, 0))
    cache = {}
    for pi, pose in enumerate(POSES):
        for d, (view, mirror) in enumerate(VIEWS):
            for f in (0, 1):
                key = (pose, view, f)
                if key not in cache:
                    cache[key] = fig.frame(view, pose=pose, f=f)
                fr = cache[key]
                if mirror:
                    fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
                poses.alpha_composite(fr, ((d * 2 + f) * w, pi * h))
    return walk, idle, poses


PORTRAIT_EMOS = {"normal": "normal", "senang": "senang", "tersenyum": "tersenyum", "tertawa": "tertawa", "kaget": "kaget",
                 "sedih": "sedih", "khawatir": "sedih", "malu": "malu"}


def portrait(fig, expr):
    """Head-and-shoulders card in the style of the main portraits (176x220)."""
    W, H = 176, 220
    scale = 5.6   # base units -> portrait px
    pen = Pen(w=W / scale * 1.0, h=H / scale * 1.0)
    # place the head centre at the upper middle of the card
    pen.ox = (W / scale) / 2 - fig.cx
    pen.oy = (H / scale) * 0.38 - fig.head_cy
    pen.ow = 0.55
    pen.g = 1.0
    fig_torso_view = "front"
    fig.torso(pen, fig_torso_view, 0)
    fig.over_layer(pen, fig_torso_view)
    fig.front_acc(pen, fig_torso_view, 0)
    fig.head(pen, "front", expr=expr)
    img = pen.im.resize((W, H), Image.LANCZOS)
    # background card
    bg = Image.new("RGBA", (W, H), (251, 231, 213, 255))
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        t = y / H
        gd.line((0, y, W, y), fill=(int(253 - 12 * t), int(236 - 22 * t), int(222 - 6 * t), 255))
    bg.alpha_composite(grad)
    bd = ImageDraw.Draw(bg)
    bd.ellipse((W * 0.12, H * 0.08, W * 0.88, H * 0.7), fill=(255, 245, 236, 255))
    shadow = img.split()[3].filter(ImageFilter.GaussianBlur(4))
    sh = Image.new("RGBA", (W, H), (120, 80, 90, 0))
    sh.putalpha(shadow.point(lambda a: a * 0.25))
    bg.alpha_composite(sh, (3, 4))
    bg.alpha_composite(img)
    ImageDraw.Draw(bg).rectangle((0, 0, W - 1, H - 1), outline=(214, 170, 180, 255), width=2)
    return bg


def main():
    args = sys.argv[1:]
    assets = "android/assets"
    only = None
    sheet_out = None
    i = 0
    while i < len(args):
        if args[i] == "--only":
            only = set(args[i + 1].split(",")); i += 2
        elif args[i] == "--sheet":
            sheet_out = args[i + 1]; i += 2
        else:
            assets = args[i]; i += 1
    ids = [k for k in NPCS if only is None or k in only]
    previews = []
    for cid in ids:
        fig = Figure(NPCS[cid])
        d = os.path.join(assets, "characters", cid)
        os.makedirs(os.path.join(d, "portraits"), exist_ok=True)
        walk, idle, poses = build(fig)
        walk.save(os.path.join(d, "walk_v53@2x.png"), optimize=True)
        idle.save(os.path.join(d, "idle_v53@2x.png"), optimize=True)
        poses.save(os.path.join(d, "poses_v53@2x.png"), optimize=True)
        for emo, expr in PORTRAIT_EMOS.items():
            portrait(fig, expr).save(os.path.join(d, "portraits", emo + ".png"), optimize=True)
        previews.append((cid, idle.crop((0, 0, FW * OUT_K, FH * OUT_K)), walk, fig))
        print("built", cid)
    if sheet_out:
        w, h = FW * OUT_K, FH * OUT_K
        out = Image.new("RGBA", (len(previews) * w, h * 4 + 24), (58, 46, 82, 255))
        dd = ImageDraw.Draw(out)
        for i, (cid, fr, walk, fig) in enumerate(previews):
            for r in range(4):
                out.alpha_composite(walk.crop((6 * w, r * h, 7 * w, (r + 1) * h)), (i * w, r * h))
            dd.text((i * w + 6, h * 4 + 6), cid, fill=(255, 255, 255, 255))
        out.save(sheet_out)


if __name__ == "__main__":
    main()
