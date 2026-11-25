class_name Progress
extends RefCounted
## Progress of one route in one slot (port of logic/Progress.java). Save schema 8, field-for-field,
## so saves written by the LibGDX build load here and the other way around.

const SCHEMA := 8
const MAP_LAYOUT_VERSION := 5      # MapLayoutV54.VERSION
const HISTORY_LIMIT := 72
const HISTORY_TEXT_LIMIT := 480

var route := ""
var slot := 1
var step := ""
var area := ""
var x := 0.0
var y := 0.0
var dir := "down"
var flags := {}                  # ordered set: flag -> true
var items: Array[String] = []
var shards := 0
var counters := {}
var companion := false
var chapters := {}               # ordered set
var play_seconds := 0.0
var day := 1
var minute := 7 * 60
var coins := 12
var affection := 0
var last_gift_day := -1
var last_date_day := -1
var date_counts := {}
var last_moment_day := -1
var moment_counts := {}
var couple_action_days := {}
var couple_action_counts := {}
var world_event_days := {}
var world_event_counts := {}
var holding_hands := false
var job_days := {}
var delivery_start_day := -1
var delivery_days := {}
var petted := {}
var dialogue_history: Array = []  # [{speaker, emotion, text, area, day}]
var visited_areas := {}
var saved_at := 0
var snapshots := {}


static func new_game(r: String, s: int, first_step: String, room: Dictionary) -> Progress:
	var p := Progress.new()
	p.route = r; p.slot = s; p.step = first_step; p.area = room.get("id", Routes.room(r))
	p.x = room.spawn[0]; p.y = room.spawn[1]; p.dir = "down"
	return p


func has_flag(f) -> bool:
	return f != null and flags.has(f)


func add_flag(f: String) -> void:
	if f != "":
		flags[f] = true


func count(id: String) -> int:
	if id == "shards":
		return shards
	return int(counters.get(id, 0))


func add_count(id: String, n: int) -> void:
	if id == "shards":
		shards = maxi(0, shards + n)
		return
	counters[id] = maxi(0, count(id) + n)


func has_item(i: String) -> bool:
	return items.has(i)


func add_history(speaker: String, emotion: String, text: String, at_area: String, at_day: int) -> void:
	var t := _safe(text, HISTORY_TEXT_LIMIT)
	if t == "":
		return
	dialogue_history.append({"speaker": _safe(speaker, 64), "emotion": _safe(emotion, 32), "text": t,
			"area": _safe(at_area, 64), "day": maxi(1, at_day)})
	if dialogue_history.size() > HISTORY_LIMIT:
		dialogue_history.pop_front()


static func _safe(t, limit: int) -> String:
	if t == null:
		return ""
	var s: String = str(t).replace("\r", " ").replace("\n", " ").strip_edges()
	return s.substr(0, limit) if s.length() > limit else s


func to_dict(with_snapshots: bool) -> Dictionary:
	var m := {}
	m["schema"] = SCHEMA
	m["mapLayoutVersion"] = MAP_LAYOUT_VERSION
	m["route"] = route; m["slot"] = slot; m["step"] = step; m["area"] = area
	m["x"] = roundi(x); m["y"] = roundi(y); m["dir"] = dir
	m["flags"] = flags.keys(); m["items"] = items.duplicate(); m["shards"] = shards
	m["counters"] = counters.duplicate(); m["companion"] = companion; m["chapters"] = chapters.keys()
	m["playSeconds"] = roundi(play_seconds)
	m["day"] = day; m["minute"] = minute; m["petted"] = petted.keys()
	m["coins"] = coins; m["affection"] = affection
	m["lastGiftDay"] = last_gift_day; m["lastDateDay"] = last_date_day
	m["dateCounts"] = date_counts.duplicate(); m["lastMomentDay"] = last_moment_day
	m["momentCounts"] = moment_counts.duplicate()
	m["coupleActionDays"] = couple_action_days.duplicate(); m["coupleActionCounts"] = couple_action_counts.duplicate()
	m["holdingHands"] = holding_hands
	m["worldEventDays"] = world_event_days.duplicate(); m["worldEventCounts"] = world_event_counts.duplicate()
	m["jobDays"] = job_days.duplicate(); m["deliveryStartDay"] = delivery_start_day
	m["deliveryDays"] = delivery_days.duplicate()
	m["dialogueHistory"] = dialogue_history.duplicate(true)
	m["visitedAreas"] = visited_areas.keys()
	m["savedAt"] = saved_at
	if with_snapshots:
		m["snapshots"] = snapshots.duplicate(true)
	return m


static func _num(m: Dictionary, k: String, def: float) -> float:
	var v = m.get(k)
	return float(v) if (v is float or v is int) else def


static func _strs(m: Dictionary, k: String) -> Array:
	var v = m.get(k)
	var out := []
	if v is Array:
		for e in v:
			if e != null:
				out.append(str(e))
	return out


static func _int_map(m: Dictionary, k: String, lo: int, hi: int) -> Dictionary:
	var out := {}
	var v = m.get(k)
	if v is Dictionary:
		for key in v:
			if v[key] is float or v[key] is int:
				out[key] = clampi(int(v[key]), lo, hi)
	return out


## Read + migrate + validate. Returns null when the data is not a valid save.
static func from_dict(m: Dictionary) -> Progress:
	var schema := int(_num(m, "schema", 0))
	if schema <= 0 or schema > SCHEMA:
		push_warning("save schema not supported: %d" % schema)
		return null
	var p := Progress.new()
	p.route = str(m.get("route", ""))
	if not Routes.valid(p.route):
		return null
	p.slot = int(_num(m, "slot", 1))
	p.step = str(m.get("step", ""))
	if p.step == "" or m.get("step") == null:
		return null
	p.area = str(m.get("area", Routes.room(p.route)))
	p.x = _num(m, "x", NAN); p.y = _num(m, "y", NAN)
	if is_nan(p.x) or is_nan(p.y) or is_inf(p.x) or is_inf(p.y):
		return null
	var layout := _num(m, "mapLayoutVersion", 0)
	if layout < 4:      # MapLayoutV4.fromLegacy
		var wh: Array = {"jalan_kota": [2048, 1024], "perumahan": [2048, 1152], "perpustakaan": [1280, 768],
				"arcade": [960, 640], "toko_bunga": [960, 640], "arland_room": [960, 640], "sofia_room": [960, 640],
				"dapur": [960, 640], "ruang_arsip": [800, 560]}.get(p.area, [])
		if wh.size() == 2:
			p.x = clampf(p.x * 1200.0 / wh[0], 12, 1187); p.y = clampf(p.y * 896.0 / wh[1], 12, 883)
	if layout < 5 and p.area in ["arland_room", "sofia_room", "dapur", "ruang_arsip"]:   # MapLayoutV54.fromV4
		p.x *= 0.5; p.y *= 0.5
	p.dir = str(m.get("dir", "down"))
	for f in _strs(m, "flags"):
		p.flags[f] = true
	for i in _strs(m, "items"):
		p.items.append(i)
	p.shards = maxi(0, int(_num(m, "shards", 0)))
	p.counters = _int_map(m, "counters", 0, 2147483647)
	p.companion = bool(m.get("companion", false))
	for c in _strs(m, "chapters"):
		p.chapters[c] = true
	p.play_seconds = maxf(0, _num(m, "playSeconds", 0))
	p.day = maxi(1, int(_num(m, "day", 1)))
	p.minute = clampi(int(_num(m, "minute", 7 * 60)), WorldClock.DAY_START, WorldClock.DAY_END)
	for a in _strs(m, "petted"):
		p.petted[a] = true
	p.coins = clampi(int(_num(m, "coins", 12)), 0, 1000000) if schema >= 2 else 12
	if schema >= 3:
		p.affection = clampi(int(_num(m, "affection", 0)), 0, 100)
		p.last_gift_day = maxi(-1, int(_num(m, "lastGiftDay", -1)))
		p.last_date_day = maxi(-1, int(_num(m, "lastDateDay", -1)))
		p.date_counts = _int_map(m, "dateCounts", 0, 100000)
	if schema >= 4:
		p.last_moment_day = maxi(-1, int(_num(m, "lastMomentDay", -1)))
		p.moment_counts = _int_map(m, "momentCounts", 0, 100000)
	if schema >= 5:
		p.couple_action_days = _int_map(m, "coupleActionDays", -1, 1000000)
		p.couple_action_counts = _int_map(m, "coupleActionCounts", 0, 100000)
		p.holding_hands = bool(m.get("holdingHands", false)) and p.companion
	if schema >= 6:
		p.world_event_days = _int_map(m, "worldEventDays", -1, 1000000)
		p.world_event_counts = _int_map(m, "worldEventCounts", 0, 100000)
	p.delivery_start_day = int(_num(m, "deliveryStartDay", -1)) if schema >= 2 else -1
	p.job_days = _int_map(m, "jobDays", 0, 2147483647)
	p.delivery_days = _int_map(m, "deliveryDays", 0, 2147483647)
	if schema >= 7:
		var raw = m.get("dialogueHistory")
		if raw is Array:
			for i in range(maxi(0, raw.size() - HISTORY_LIMIT), raw.size()):
				var e = raw[i]
				if e is Dictionary:
					p.add_history(str(e.get("speaker", "?")), str(e.get("emotion", "neutral")), str(e.get("text", "")),
							str(e.get("area", "")), int(_num(e, "day", 1)))
		for a in _strs(m, "visitedAreas"):
			if a.length() <= 64 and p.visited_areas.size() < 256:
				p.visited_areas[a] = true
	var sa = m.get("savedAt")
	p.saved_at = int(sa) if (sa is float or sa is int) else 0
	if m.get("snapshots") is Dictionary:
		p.snapshots = m["snapshots"].duplicate(true)
	return p


func copy() -> Progress:
	return from_dict(to_dict(true))


func snapshot(chapter: String) -> void:
	snapshots[chapter] = to_dict(false)


func replay_from(chapter: String) -> Progress:
	var s = snapshots.get(chapter)
	return from_dict(s) if s is Dictionary else null
