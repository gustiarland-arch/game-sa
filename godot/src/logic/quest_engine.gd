class_name QuestEngine
extends RefCounted
## Pure quest logic (port of logic/QuestEngine.java): active step, conditions, side content,
## town NPC schedules, economy, romance rules and state actions. Reads the raw quests.json
## dictionaries held by the Data autoload.

var p: Progress
var replay := false
var both_routes_completed := false     # from global progress (both saves finished C06)


func _init(progress: Progress, is_replay := false) -> void:
	p = progress
	replay = is_replay
	if Data.step(p.step).is_empty():
		push_error("unknown step " + p.step)


func step() -> Dictionary:
	return Data.step(p.step)


func chapter() -> String:
	return step().get("chapter", "")


static func _strs(c: Dictionary, k: String) -> Array:
	var v = c.get(k)
	if v is Array:
		return v
	return []


func _r(s) -> String:
	return Routes.resolve(s, p.route)


# ------------------------------------------------------------ conditions
## flags, notFlags, anyFlags, steps, notSteps, chapters, minChapter, maxChapter, doneChapters, route,
## items, notItems, count {id: min}, countBelow {id: max}, hours, weatherIs, coins..., jobs. Empty = true.
func check(c) -> bool:
	if not (c is Dictionary) or c.is_empty():
		return true
	if c.has("bothRoutesCompleted") and bool(c.bothRoutesCompleted) != both_routes_completed:
		return false
	if c.has("worldEventReady") and world_event_block(c.worldEventReady, p.area) != "":
		return false
	if float(c.get("coinsAtLeast", 0)) > p.coins:
		return false
	if c.has("coinsBelow") and p.coins >= float(c.coinsBelow):
		return false
	if c.has("jobReady") and not job_ready(c.jobReady):
		return false
	if bool(c.get("deliveryOpen", false)) and not delivery_open():
		return false
	if c.has("deliveryNotDone") and int(p.delivery_days.get(c.deliveryNotDone, -1)) == p.day:
		return false
	var hrs: Array = _strs(c, "hours")
	if hrs.size() >= 2:
		var a0 := WorldClock.parse(hrs[0], 0)
		var a1 := WorldClock.parse(hrs[1], 24 * 60)
		if p.minute < a0 or p.minute >= a1:
			return false
	var wx: Array = _strs(c, "weatherIs")
	if not wx.is_empty() and not wx.has(weather_now()):
		return false
	for f in _strs(c, "flags"):
		if not p.has_flag(_r(f)):
			return false
	for f in _strs(c, "notFlags"):
		if p.has_flag(_r(f)):
			return false
	var any: Array = _strs(c, "anyFlags")
	if not any.is_empty():
		var ok := false
		for f in any:
			if p.has_flag(_r(f)):
				ok = true
				break
		if not ok:
			return false
	var st: Array = _strs(c, "steps")
	if not st.is_empty() and not st.has(p.step):
		return false
	if _strs(c, "notSteps").has(p.step):
		return false
	var chs: Array = _strs(c, "chapters")
	if not chs.is_empty() and not chs.has(chapter()):
		return false
	if c.has("minChapter") and Data.chapter_index(chapter()) < Data.chapter_index(c.minChapter):
		return false
	if c.has("maxChapter") and Data.chapter_index(chapter()) > Data.chapter_index(c.maxChapter):
		return false
	for ch in _strs(c, "doneChapters"):
		if not p.chapters.has(ch):
			return false
	if c.has("route") and c.route != null and c.route != p.route:
		return false
	for i in _strs(c, "items"):
		if not p.has_item(i):
			return false
	for i in _strs(c, "notItems"):
		if p.has_item(i):
			return false
	var cnt = c.get("count", {})
	if cnt is Dictionary:
		for k in cnt:
			if (cnt[k] is float or cnt[k] is int) and p.count(k) < int(cnt[k]):
				return false
	var below = c.get("countBelow", {})
	if below is Dictionary:
		for k in below:
			if (below[k] is float or below[k] is int) and p.count(k) >= int(below[k]):
				return false
	return true


# ------------------------------------------------------------ living world
func world_event(id: String) -> Dictionary:
	for e in Data.quests.get("worldEvents", []):
		if e.get("id") == id:
			return e
	return {}


static func _hours(e: Dictionary, def0: int, def1: int) -> Array:
	var h: Array = e.get("hours", [])
	return [WorldClock.parse(h[0], def0) if h.size() > 0 else def0, WorldClock.parse(h[1], def1) if h.size() > 1 else def1]


## "" when the event can run now, otherwise the reason shown to the player.
func world_event_block(id: String, at_area: String) -> String:
	var e := world_event(id)
	if e.is_empty():
		return "Event tidak ditemukan."
	if replay:
		return "Event dunia tidak tersedia saat replay."
	if e.get("area", "") != at_area:
		return "Datang ke lokasi event."
	if e.get("route") != null and e.get("route") != p.route:
		return "Event untuk route lain."
	var current := Data.chapter_index(chapter())
	var required := Data.chapter_index(e.get("minChapter", "C02"))
	if current < 0 or required < 0 or current < required:
		return "Event akan tersedia di chapter berikutnya."
	if bool(e.get("companion", true)) and not p.companion:
		return "Ajak pasangan berjalan bersamamu dahulu."
	var hr := _hours(e, WorldClock.DAY_START, WorldClock.DAY_END)
	if p.minute < hr[0] or p.minute >= hr[1]:
		return "Belum masuk waktu event."
	var w: Array = e.get("weather", [])
	if not w.is_empty() and not w.has(weather_now()):
		return "Tunggu cuaca yang cocok."
	if int(p.world_event_days.get(id, -1)) == p.day:
		return "Event ini sudah dilakukan hari ini."
	var aff := int(e.get("affection", 0))
	var coins := int(e.get("coins", 0))
	if aff < 0 or aff > 8 or coins < 0 or coins > 12 or not e.get("scenes", {}).has(p.route):
		return "Data event tidak valid."
	if p.coins > 1000000 - coins:
		return "Dompet sudah mencapai batas."
	return ""


func complete_world_event(id: String, at_area: String) -> String:
	var blocked := world_event_block(id, at_area)
	if blocked != "":
		return blocked
	var e := world_event(id)
	p.world_event_days[id] = p.day
	p.world_event_counts[id] = mini(100000, int(p.world_event_counts.get(id, 0)) + 1)
	p.add_flag("WORLD_EVENT_" + id.to_upper() + "_ONCE")
	var coins := int(e.get("coins", 0))
	var aff := int(e.get("affection", 0))
	p.coins += coins
	_add_affection(aff)
	return "Momen dunia tersimpan! +%d hati%s" % [aff, (", +%d koin." % coins) if coins > 0 else "."]


# ------------------------------------------------------------ economy
func job_ready(job: String) -> bool:
	return int(p.job_days.get(job, -1)) != p.day


func purchase(shop_id: String, item_id: String) -> String:
	var shop: Dictionary = Data.quests.get("shops", {}).get(shop_id, {})
	if shop.is_empty():
		return "Toko tidak ditemukan."
	for good in shop.get("goods", []):
		if good.get("item") == item_id:
			var price := int(good.get("price", 0))
			if price <= 0:
				return "Harga barang tidak valid."
			if p.has_item(item_id):
				return "Barang ini sudah ada di tas."
			if p.coins < price:
				return "Koin belum cukup. Butuh %d koin." % price
			p.coins -= price
			p.items.append(item_id)
			return "Membeli %s (-%d koin)." % [good.get("name", item_id), price]
	return "Barang tidak dijual di toko ini."


func complete_work(id: String, score: int) -> String:
	var job: Dictionary = Data.quests.get("jobs", {}).get(id, {})
	if job.is_empty() or job.get("minigame", "") == "" or not job_ready(id) or score < 0:
		return "Shift tidak tersedia."
	if score < int(job.get("minScore", 1)):
		return "Belum memenuhi target. Coba shift ini lagi."
	var reward := int(job.get("reward", 0))
	if reward <= 0 or p.coins > 1000000 - reward:
		return "Upah tidak bisa diproses."
	p.coins += reward
	p.job_days[id] = p.day
	p.add_flag("JOB_" + id.to_upper() + "_ONCE")
	return "Shift selesai! +%d koin." % reward


func delivery_open() -> bool:
	return p.delivery_start_day == p.day and job_ready("kurir") and Data.quests.get("jobs", {}).has("kurir")


func start_delivery() -> String:
	if not job_ready("kurir"):
		return "Surat hari ini sudah diantar. Kembali besok."
	if delivery_open():
		return "Antar 3 surat ke Plaza, Jalan Kota, dan Tepi Danau."
	p.delivery_start_day = p.day
	return "Ambil 3 surat. Kunjungi Plaza, Jalan Kota, dan Tepi Danau!"


func deliver(address: String) -> String:
	if not delivery_open():
		return "Ambil surat baru dari Pak Pos terlebih dahulu."
	var job: Dictionary = Data.quests.get("jobs", {}).get("kurir", {})
	var stops: Array = job.get("stops", [])
	if job.is_empty() or not stops.has(address):
		return "Alamat tidak dikenal."
	if int(p.delivery_days.get(address, -1)) == p.day:
		return "Surat alamat ini sudah diantar."
	p.delivery_days[address] = p.day
	var n := 0
	for place in stops:
		if int(p.delivery_days.get(place, -1)) == p.day:
			n += 1
	if n < stops.size():
		return "Surat terkirim (%d/%d)." % [n, stops.size()]
	var reward := int(job.get("reward", 0))
	if reward > 0 and p.coins <= 1000000 - reward:
		p.coins += reward
		p.job_days["kurir"] = p.day
		p.delivery_start_day = -1
		p.add_flag("JOB_KURIR_ONCE")
		return "Semua surat sampai! +%d koin." % reward
	return "Surat terkirim, tetapi upah belum bisa diproses."


# ------------------------------------------------------------ romance (gifts, dates, moments, couple actions, games)
func romance_ready() -> bool:
	return not replay and p.companion and Data.chapter_index(chapter()) >= Data.chapter_index("C02") and Data.chapter_index(chapter()) >= 0


func _add_affection(n: int) -> void:
	p.affection = clampi(p.affection + maxi(0, n), 0, 100)
	for lvl in [20, 50, 80]:
		if p.affection >= lvl:
			p.add_flag("ROM_BOND_%d" % lvl)


func romance_game(id: String) -> Dictionary:
	for g in Data.quests.get("romance", {}).get("games", []):
		if g.get("id") == id:
			return g
	return {}


func romance_game_block(id: String, at_area: String) -> String:
	var g := romance_game(id)
	var aff := int(g.get("affection", 0))
	if g.is_empty() or aff <= 0 or aff > 10 or not Data.quests.get("minigames", {}).has(g.get("minigame", "")):
		return "Permainan tidak tersedia."
	if not romance_ready():
		return "Bermain berdua tersedia setelah Chapter 2 bersama pasangan."
	if not g.get("areas", []).has(at_area):
		return "Kunjungi lokasi kegiatan ini dahulu."
	return ""


func complete_romance_game(id: String, at_area: String, score: int) -> String:
	var blocked := romance_game_block(id, at_area)
	if blocked != "":
		return blocked
	if score < 0:
		return "Permainan dibatalkan, tidak ada bonus."
	var g := romance_game(id)
	p.add_count("last_romgame_" + id, score - p.count("last_romgame_" + id))
	if score > p.count("best_romgame_" + id):
		p.add_count("best_romgame_" + id, score - p.count("best_romgame_" + id))
	if score < int(g.get("minScore", 1)):
		return "Belum berhasil. Coba lagi untuk mencatat kenangan."
	if p.count("day_romgame_" + id) == p.day:
		return "Main ulang selesai! Rekor tetap tersimpan, bonus hari ini sudah diambil."
	p.add_count("day_romgame_" + id, p.day - p.count("day_romgame_" + id))
	p.add_count("total_romgame_" + id, 1)
	p.add_flag("ROM_GAME_" + id.to_upper() + "_ONCE")
	_add_affection(int(g.get("affection", 0)))
	return "Kenangan baru! +%d kedekatan." % int(g.get("affection", 0))


func _rom(kind: String, id: String, key := "id") -> Dictionary:
	for e in Data.quests.get("romance", {}).get(kind, []):
		if str(e.get(key, "")) == id:
			return e
	return {}


func _rom_hours(e: Dictionary) -> Vector2i:
	var h: Array = e.get("hours", [])
	return Vector2i(WorldClock.parse(h[0], 0) if h.size() > 0 else 0, WorldClock.parse(h[1], 26 * 60) if h.size() > 1 else 26 * 60)


func _scene_for(e: Dictionary):
	var sc = e.get("scene", {})
	return sc.get(p.route) if sc is Dictionary else null


## Gifts: the item is only consumed after every check passed.
func give_gift(item_id: String) -> String:
	var g := _rom("gifts", item_id, "item")
	if not romance_ready():
		return "Ajak pasangan menemanimu setelah Chapter 2."
	if g.is_empty() or int(g.get("affection", 0)) <= 0:
		return "Barang ini tidak bisa dijadikan hadiah."
	if p.last_gift_day == p.day:
		return "Kamu sudah memberi hadiah hari ini. Coba besok."
	if not p.has_item(item_id):
		return "Belum punya barang tersebut. Beli di toko dulu."
	p.items.erase(item_id)
	p.last_gift_day = p.day
	_add_affection(int(g.affection))
	p.add_flag("ROM_GIFT_ONCE")
	return "Hadiah diberikan! +%d kedekatan." % int(g.affection)


func date_block(id: String, at_area: String) -> String:
	var d := _rom("dates", id)
	if d.is_empty():
		return "Kencan tidak tersedia."
	if not romance_ready():
		return "Ajak pasangan menemanimu setelah Chapter 2."
	if str(d.get("area", "")) != at_area:
		return "Datang dahulu ke %s." % str(d.get("area", "")).replace("_", " ")
	var hr := _rom_hours(d)
	if p.minute < hr.x or p.minute >= hr.y:
		return "Belum masuk jam kencan."
	if p.last_date_day == p.day:
		return "Hari ini sudah berkencan. Kembali besok."
	if int(d.get("cost", 0)) < 0 or int(d.get("affection", 0)) <= 0:
		return "Data kencan tidak valid."
	if p.coins < int(d.get("cost", 0)):
		return "Koin tidak cukup. Butuh %d koin." % int(d.cost)
	return ""


func start_date(id: String, at_area: String) -> String:
	var blocked := date_block(id, at_area)
	if blocked != "":
		return blocked
	var d := _rom("dates", id)
	p.coins -= int(d.cost)
	p.last_date_day = p.day
	p.date_counts[id] = mini(100000, int(p.date_counts.get(id, 0)) + 1)
	_add_affection(int(d.affection))
	p.add_flag("ROM_DATE_%s_ONCE" % id.to_upper())
	return "Kencan dimulai! -%d koin, +%d kedekatan." % [int(d.cost), int(d.affection)]


func moment_block(id: String, at_area: String) -> String:
	var m := _rom("moments", id)
	if m.is_empty():
		return "Momen tidak ditemukan."
	if not romance_ready():
		return "Ajak pasangan menemanimu setelah Chapter 2."
	if str(m.get("area", "")) != at_area:
		return "Temui pasangan di %s." % str(m.get("area", "")).replace("_", " ")
	if p.last_moment_day == p.day:
		return "Sudah punya momen berdua hari ini. Coba besok."
	if p.affection < int(m.get("minAffection", 0)):
		return "Butuh kedekatan %d hati." % int(m.minAffection)
	var hr := _rom_hours(m)
	if p.minute < hr.x or p.minute >= hr.y:
		return "Momen ini hanya tersedia pada jam tertentu."
	var w: Array = m.get("weather", [])
	if not w.is_empty() and not w.has(weather_now()):
		return "Tunggu cuaca yang cocok."
	var aff := int(m.get("affection", 0))
	if aff <= 0 or aff > 20 or _scene_for(m) == null:
		return "Data momen tidak valid."
	return ""


func start_moment(id: String, at_area: String) -> String:
	var blocked := moment_block(id, at_area)
	if blocked != "":
		return blocked
	var m := _rom("moments", id)
	p.last_moment_day = p.day
	p.moment_counts[id] = mini(100000, int(p.moment_counts.get(id, 0)) + 1)
	p.add_flag("ROM_MOM_%s_ONCE" % id.to_upper())
	_add_affection(int(m.affection))
	return "Momen berdua! +%d kedekatan." % int(m.affection)


func couple_action_block(id: String, at_area: String) -> String:
	var a := _rom("coupleActions", id)
	if a.is_empty():
		return "Aksi berdua tidak dikenal."
	if not romance_ready():
		return "Ajak pasangan menemanimu setelah Chapter 2."
	if id == "gandengan" and p.holding_hands:
		return ""
	var areas: Array = a.get("areas", [])
	if not areas.is_empty() and not areas.has(at_area):
		return "Kunjungi lokasi yang cocok untuk aksi ini."
	if p.affection < int(a.get("minAffection", 0)):
		return "Butuh kedekatan %d hati." % int(a.minAffection)
	var hr := _rom_hours(a)
	if p.minute < hr.x or p.minute >= hr.y:
		return "Belum masuk jam aktivitas."
	var w: Array = a.get("weather", [])
	if not w.is_empty() and not w.has(weather_now()):
		return "Tunggu cuaca yang cocok."
	if id != "gandengan" and int(p.couple_action_days.get(id, -1)) == p.day:
		return "Bonus aksi ini sudah diambil hari ini. Coba besok."
	var aff := int(a.get("affection", 0))
	if aff < 0 or aff > 10 or _scene_for(a) == null:
		return "Data aksi tidak valid."
	return ""


func start_couple_action(id: String, at_area: String) -> String:
	var blocked := couple_action_block(id, at_area)
	if blocked != "":
		return blocked
	if id == "gandengan" and p.holding_hands:
		p.holding_hands = false
		return "Berhenti bergandengan."
	var a := _rom("coupleActions", id)
	if id == "gandengan" and int(p.couple_action_days.get(id, -1)) == p.day:
		p.holding_hands = true
		return "Bergandengan lagi."
	p.couple_action_days[id] = p.day
	p.couple_action_counts[id] = mini(100000, int(p.couple_action_counts.get(id, 0)) + 1)
	p.add_flag("ROM_ACT_%s_ONCE" % id.to_upper())
	if id == "gandengan":
		p.holding_hands = true
	_add_affection(int(a.affection))
	return "Aksi berdua! +%d kedekatan." % int(a.affection)


func _bond_scenes(acts: Array) -> void:
	for level in [20, 50, 80]:
		var key := "ROM_BOND_%d" % level
		if not p.has_flag(key) or p.has_flag(key + "_SCENE"):
			continue
		acts.append({"do": "scene", "id": "RM-BOND-%d@%s" % [level, p.route]})
		acts.append({"do": "flag", "id": key + "_SCENE"})


func couple_action_actions(id: String) -> Array:
	var a := _rom("coupleActions", id)
	if a.is_empty() or _scene_for(a) == null:
		return []
	var cmds := [{"c": "bars", "on": true, "t": 0.35}, {"c": "cam", "on": "player", "zoom": 1.35, "t": 0.6},
		{"c": "pair", "kind": str(a.get("gesture", "highfive")), "t": 2.1, "block": true},
		{"c": "fx", "kind": "hearts", "on": "player", "t": 1.5}, {"c": "bars", "on": false, "t": 0.45}]
	var acts := [{"do": "cine", "cmds": cmds}, {"do": "scene", "id": _scene_for(a)}]
	_bond_scenes(acts)
	return acts


func _romance_scene_actions(scene: String, with_cine: bool) -> Array:
	var acts := []
	if with_cine:
		acts.append({"do": "cine", "cmds": [{"c": "face", "who": "player", "at": "partner"}, {"c": "fx", "kind": "hearts", "t": 1.2, "block": true}]})
	acts.append({"do": "emote", "who": "partner", "e": "heart"})
	acts.append({"do": "scene", "id": scene})
	_bond_scenes(acts)
	return acts


func gift_actions(item: String) -> Array:
	var g := _rom("gifts", item, "item")
	return [] if g.is_empty() else _romance_scene_actions(Routes.resolve(str(g.get("scene", "")) + "@$ROUTE", p.route), false)


func date_actions(id: String) -> Array:
	var d := _rom("dates", id)
	return [] if d.is_empty() or _scene_for(d) == null else _romance_scene_actions(_scene_for(d), true)


func moment_actions(id: String) -> Array:
	var m := _rom("moments", id)
	return [] if m.is_empty() or _scene_for(m) == null else _romance_scene_actions(_scene_for(m), true)


# ------------------------------------------------------------ step view
func objective_text() -> String:
	var s := step()
	if s.is_empty():
		return ""
	var t: String = s.get("objective", {}).get(p.route, "Jelajahi cerita")
	var counter = s.get("counter")
	var mx := int(s.get("counterMax", 0))
	if counter != null and mx > 0:
		t += " (%d/%d)" % [mini(p.count(counter), mx), mx]
	return t


func _visible(it: Dictionary, at_area: String) -> bool:
	if it.get("route") != null and it.get("route") != p.route:
		return false
	if _r(it.get("area", "")) != at_area:
		return false
	if it.get("hideIfFlag") != null and p.has_flag(_r(it.hideIfFlag)):
		return false
	return check(it.get("when", {}))


func interactables(at_area: String) -> Array:
	var out := []
	for it in step().get("interactables", []):
		if _visible(it, at_area):
			out.append(it)
	return out


func side_interactables(at_area: String) -> Array:
	var out := []
	for it in Data.quests.get("side", []):
		if _visible(it, at_area):
			out.append(it)
	return out


## Partner placed by the active step: [{who, dir, x, y}]
func npcs(at_area: String) -> Array:
	var out := []
	for n in step().get("npcs", []):
		if _r(n.get("area", "")) == at_area:
			out.append({"who": _r(n.get("who", "$PARTNER")), "dir": n.get("dir", "down"), "x": float(n.get("x", 0)), "y": float(n.get("y", 0))})
	return out


func weather_now() -> String:
	var w = step().get("weather")
	if w != null:
		return WorldClock.HUJAN if w == "rain" else w
	return WorldClock.weather(p.day)


## Where a town NPC is now: {area, x, y, dir, wander} or {} when hidden.
func npc_place(n: Dictionary) -> Dictionary:
	var home := {"area": n.get("area", ""), "x": float(n.get("x", 0)), "y": float(n.get("y", 0)), "dir": n.get("dir", "down"), "wander": float(n.get("wander", 0))}
	var sched: Array = n.get("schedule", [])
	if sched.is_empty() or _needed_by_step(n):
		return home
	var w := weather_now()
	var pick = null
	for e in sched:
		if not check(e.get("when", {})):
			continue
		var ws: Array = e.get("weather", [])
		if not ws.is_empty() and not ws.has(w):
			continue
		if WorldClock.parse(e.get("at"), 0) <= p.minute:
			pick = e
	if pick == null:
		return home
	if bool(pick.get("hidden", false)):
		return {}
	return {"area": pick.get("area", home.area), "x": float(pick.get("x", home.x)), "y": float(pick.get("y", home.y)),
			"dir": pick.get("dir", home.dir), "wander": float(pick.get("wander", home.wander))}


func _needed_by_step(n: Dictionary) -> bool:
	var s := step()
	if s.is_empty():
		return false
	for it in s.get("interactables", []):
		if _r(it.get("area", "")) == n.get("area", "") and absf(float(it.get("x", 0)) - float(n.get("x", 0))) < 90 and absf(float(it.get("y", 0)) - float(n.get("y", 0))) < 90:
			return true
	for np in s.get("npcs", []):
		if _r(np.get("who", "$PARTNER")) == n.get("sprite", n.get("id")):
			return true
	for d in n.get("dialogs", []):
		if _strs(d.get("when", {}), "steps").has(s.get("id")):
			return true
	return false


func town_npcs_now(at_area: String) -> Array:
	var out := []
	for n in Data.quests.get("townNpcs", []):
		if not check(n.get("when", {})):
			continue
		var pl := npc_place(n)
		if not pl.is_empty() and pl.area == at_area:
			out.append(n)
	return out


func npc_dialog(n: Dictionary) -> Dictionary:
	for d in n.get("dialogs", []):
		if check(d.get("when", {})):
			return d
	return {}


func partner_talk(at_area: String) -> Dictionary:
	for t in Data.quests.get("talks", []):
		if (t.get("area") == null or t.get("area") == at_area) and not p.has_flag("TALK_" + str(t.get("id"))) and check(t.get("when", {})):
			return t
	return {}


func talk_actions(t: Dictionary) -> Array:
	return [{"do": "scene", "id": _r(t.get("scene", ""))}, {"do": "flag", "id": "TALK_" + str(t.get("id"))}]


func examine(a: Dictionary) -> Array:
	var out := []
	for e in a.get("examine", []):
		if check(e.get("when", {})) and not e.get("lines", {}).get(p.route, []).is_empty():
			out.append(e)
	return out


## "" when the door can be used, otherwise the locked text.
func door_lock(d: Dictionary) -> String:
	if d.get("route") != null and d.get("route") != p.route:
		return d.get("routeText", "Pintu ini terkunci.")
	for l in d.get("locked", []):
		if _strs(l, "steps").has(p.step) or (not l.get("when", {}).is_empty() and check(l.get("when", {}))):
			var t = l.get("text", "Terkunci.")
			if t is Dictionary:
				return t.get(p.route, "Terkunci.")
			return str(t) if t != null else "Terkunci."
	return ""


## Copy of an action list: drop other-route entries and resolve $TOKENS in string values.
func resolve(actions) -> Array:
	var out := []
	if not (actions is Array):
		return out
	for a in actions:
		if not (a is Dictionary):
			continue
		if a.get("route") != null and a.get("route") != p.route:
			continue
		var c := {}
		for k in a:
			c[k] = _r(a[k]) if a[k] is String else a[k]
		out.append(c)
	return out


func on_enter_area(at_area: String) -> Array:
	var ea: Dictionary = step().get("enterArea", {})
	if ea.is_empty() or ea.get("area") == null or _r(ea.area) != at_area:
		return []
	return resolve(ea.get("actions", []))


## Counter-based step completion, once per step.
func check_complete() -> Array:
	var s := step()
	var c: Dictionary = s.get("complete", {})
	var shards_n := int(c.get("shards", 0))
	var counter = c.get("counter", "shards" if shards_n > 0 else null)
	var need := int(c.get("count", shards_n))
	if counter == null or need <= 0:
		return []
	var done := "STEPDONE_" + str(s.get("id"))
	if p.count(counter) >= need and not p.has_flag(done):
		p.add_flag(done)
		return resolve(c.get("actions", []))
	return []


func add_flags(list) -> void:
	if list is Array:
		for f in list:
			if f != null and str(f) != "":
				p.add_flag(_r(str(f)))


## Apply a state action. Returns true when state changed.
func apply(a: Dictionary) -> bool:
	match str(a.get("do", "")):
		"flag":
			p.add_flag(str(a.get("id", ""))); return true
		"unflag":
			return p.flags.erase(str(a.get("id", "")))
		"item":
			var id := str(a.get("id", ""))
			if not p.items.has(id):
				p.items.append(id); return true
			return false
		"removeItem":
			var id := str(a.get("id", ""))
			if p.items.has(id):
				p.items.erase(id); return true
			return false
		"shard":
			p.shards += 1; return true
		"count":
			p.add_count(str(a.get("id", "")), int(a.get("add", 1))); return true
		"setCount":
			var id := str(a.get("id", ""))
			p.add_count(id, int(a.get("value", 0)) - p.count(id)); return true
		"companion":
			p.companion = bool(a.get("on", false)); return true
		"step":
			var id := str(a.get("id", ""))
			if Data.step(id).is_empty():
				push_error("step missing: " + id)
				return false
			p.step = id
			var ch = Data.chapter_start_steps.get(id)
			if ch != null and not p.snapshots.has(ch):
				p.snapshot(ch)
			return true
		"restUntilTomorrow":
			if p.day >= 1000000:
				return false
			p.day += 1; p.minute = 7 * 60; p.companion = false; p.holding_hands = false
			return true
		"chapterEnd":
			var ch := str(a.get("chapter", ""))
			if p.chapters.has(ch):
				return false
			p.chapters[ch] = true
			return true
	return false
