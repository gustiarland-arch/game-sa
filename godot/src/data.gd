extends Node
## Game databases loaded once from the shared JSON content (same files the LibGDX build used).
## Coordinates are map pixels, y down - identical to Godot's 2D space, so no conversion.

const FOOT_W := 18.0
const FOOT_TOP := 6.0
const FOOT_BOTTOM := 2.0

var maps: Dictionary = {}        # area id -> area dictionary (raw JSON + cached colliders)
var props: Dictionary = {}       # prop id -> definition
var story: Dictionary = {}
var quests: Dictionary = {}
var memory_book: Dictionary = {}
var steps: Dictionary = {}               # step id -> step
var chapter_order: Array = []
var chapter_start_steps: Dictionary = {} # first step of a chapter (incl. per-route firsts) -> chapter
var first_step := ""


func _ready() -> void:
	props = _json("res://assets/data/props.json").get("props", {})
	maps = _json("res://assets/data/maps.json").get("areas", {})
	story = _json("res://assets/data/story.json")
	quests = _json("res://assets/data/quests.json")
	memory_book = _json("res://assets/data/memory_book.json")
	for id in maps:
		_prepare_area(id, maps[id])
	for st in quests.get("steps", []):
		steps[st.get("id", "?")] = st
	for c in quests.get("chapters", []):
		chapter_order.append(c.get("id", "?"))
		if c.get("firstStep", "") != "":
			chapter_start_steps[c.firstStep] = c.id
			if first_step == "":
				first_step = c.firstStep
	var rf: Dictionary = quests.get("chapterRouteFirst", {})
	for ch in rf:
		for stp in rf[ch]:
			chapter_start_steps[stp] = ch


func step(id: String) -> Dictionary:
	return steps.get(id, {})


func chapter_index(ch) -> int:
	return chapter_order.find(ch)


func scene(id: String) -> Dictionary:
	return story.get("scenes", {}).get(id, {})


func speaker(id: String) -> Dictionary:
	var s: Dictionary = story.get("speakers", {}).get(id, {})
	return s if not s.is_empty() else {"name": id}


func emotion(id: String) -> Dictionary:
	var e: Dictionary = story.get("emotions", {}).get(id, {})
	return e if not e.is_empty() else story.get("emotions", {}).get("neutral", {})


func chapter_title(id: String) -> String:
	for c in story.get("chapters", []):
		if c.get("id") == id:
			return c.get("title", id)
	return id


## Portrait texture with the emotion fallback chain (e.g. pikir -> serius -> normal).
var _portraits := {}
func portrait(character: String, emo: String) -> Texture2D:
	var key := character + "/" + emo
	if _portraits.has(key):
		return _portraits[key]
	var t: Texture2D = null
	for e in emotion(emo).get("portrait", ["normal"]) + ["normal"]:
		var p := "res://assets/characters/%s/portraits/%s.png" % [character, e]
		if ResourceLoader.exists(p):
			t = load(p)
			break
	_portraits[key] = t
	return t


func tex(path: String) -> Texture2D:
	var p := "res://assets/" + path
	return load(p) if ResourceLoader.exists(p) else null


func _json(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("missing data " + path)
		return {}
	var parsed = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


## Walls + prop foot boxes merged into one rectangle list, like MapDb.Area in the Java build.
func _prepare_area(id: String, a: Dictionary) -> void:
	var rects: Array[Rect2] = []
	for w in a.get("walls", []):
		if w.size() >= 4:
			rects.append(Rect2(w[0], w[1], w[2], w[3]))
	for p in a.get("props", []):
		var d: Dictionary = props.get(p.get("type", ""), {})
		var cw: float = d.get("cw", 0.0)
		var ch: float = d.get("ch", 0.0)
		if cw > 0 and ch > 0:
			rects.append(Rect2(p["x"] - cw / 2.0, p["y"] - ch, cw, ch))
	a["_rects"] = rects
	a["id"] = id


func area(id: String) -> Dictionary:
	return maps.get(id, {})


func prop_scale(def: Dictionary) -> float:
	if def.has("scale"):
		return float(def["scale"])
	return 0.5 if String(def.get("image", "")).contains("@2x") else 1.0


## True when the character's foot box at (x, y) hits a wall, prop, gate or the map edge.
func blocked(a: Dictionary, x: float, y: float, flags: Dictionary = {}) -> bool:
	var x0 := x - FOOT_W / 2.0
	var x1 := x + FOOT_W / 2.0
	var y0 := y - FOOT_TOP
	var y1 := y + FOOT_BOTTOM
	if x0 < 0 or y0 < 0 or x1 > a.get("w", 0) or y1 > a.get("h", 0):
		return true
	var foot := Rect2(x0, y0, x1 - x0, y1 - y0)
	for r in a["_rects"]:
		if foot.intersects(r):
			return true
	for g in a.get("gates", []):
		var r: Array = g.get("rect", [])
		if r.size() >= 4 and foot.intersects(Rect2(r[0], r[1], r[2], r[3])) and _gate_solid(g, flags):
			return true
	for e in a.get("ellipses", []):
		if e.size() >= 4:
			for pt in [Vector2(x0, y0), Vector2(x1, y0), Vector2(x0, y1), Vector2(x1, y1), Vector2(x, y)]:
				var dx: float = (pt.x - e[0]) / e[2]
				var dy: float = (pt.y - e[1]) / e[3]
				if dx * dx + dy * dy < 1.0:
					return true
	return false


func _gate_solid(g: Dictionary, flags: Dictionary) -> bool:
	if g.has("openFlag"):
		return not flags.has(g["openFlag"])
	return g.has("closeFlag") and flags.has(g["closeFlag"])


## Swept check so fast movement never tunnels through thin walls.
func clear_segment(a: Dictionary, x0: float, y0: float, x1: float, y1: float, flags: Dictionary = {}) -> bool:
	var dist := Vector2(x1 - x0, y1 - y0).length()
	var steps := maxi(1, int(ceil(dist / 4.0)))
	for i in range(1, steps + 1):
		var t := float(i) / steps
		if blocked(a, lerpf(x0, x1, t), lerpf(y0, y1, t), flags):
			return false
	return true
