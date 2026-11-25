class_name ActionRunner
extends RefCounted
## Runs action lists in order (port of logic/ActionRunner.java). Presentation actions (scene, lines,
## puzzle, minigame, warp, cards, credits, cine) wait for the presenter's callback; state actions are
## applied to the QuestEngine; "if" branches on a condition.
##
## The presenter is the Game node and must provide:
##   play_scene(id, done), play_lines(lines, name, done), open_puzzle(id, done(ok)), open_minigame(id, done(score)),
##   open_shop(id, done), warp(area, x, y, dir, done), chapter_card(ch, done), chapter_end(ch, done), credits(done),
##   cine_play(cmds, done), toast(text), sfx(id), music(id), emote(who, e), companion_changed(on), step_changed(), on_idle()

var engine: QuestEngine
var presenter: Object
var queue: Array = []
var waiting := false
var _pumping := false


func _init(e: QuestEngine, pres: Object) -> void:
	engine = e
	presenter = pres


func busy() -> bool:
	return waiting or not queue.is_empty()


func run(actions: Array) -> void:
	queue.append_array(actions)
	_pump()


func clear() -> void:
	queue.clear()


func _resume() -> void:
	waiting = false
	_pump()


func _push_front(actions: Array) -> void:
	for i in range(actions.size() - 1, -1, -1):
		queue.push_front(actions[i])


func _pump() -> void:
	if _pumping:
		return
	_pumping = true
	while not waiting:
		if queue.is_empty():
			var more := engine.check_complete()
			if more.is_empty():
				break
			queue.append_array(more)
			continue
		_execute(queue.pop_front())
	_pumping = false
	if not waiting and queue.is_empty():
		presenter.on_idle()


func _execute(a: Dictionary) -> void:
	var d := str(a.get("do", ""))
	var p := engine.p
	match d:
		"scene":
			var sc := Data.scene(str(a.get("id", "")))
			if sc.is_empty():
				return     # missing scene: skip, never softlock
			waiting = true
			presenter.play_scene(str(a.get("id")), func():
				engine.add_flags(sc.get("flags", []))
				_resume())
		"lines":
			var lines: Array = a.get("lines", [])
			if lines.is_empty():
				return
			waiting = true
			presenter.play_lines(lines, a.get("name"), _resume)
		"if":
			var ok := engine.check(a.get("when", {}))
			_push_front(engine.resolve(a.get("then" if ok else "else", [])))
		"puzzle":
			waiting = true
			presenter.open_puzzle(str(a.get("id", "")), func(ok: bool):
				if not ok:
					queue.clear()
				_resume())
		"minigame":
			var id := str(a.get("id", ""))
			waiting = true
			presenter.open_minigame(id, func(score: int):
				if score < 0:
					queue.clear()
					_resume()
					return
				p.add_flag("MG_" + id.to_upper() + "_DONE")
				p.add_count("last_" + id, score - p.count("last_" + id))
				if score > p.count("best_" + id):
					p.add_count("best_" + id, score - p.count("best_" + id))
				_resume())
		"romanceGame":
			var id := str(a.get("id", ""))
			var rg := engine.romance_game(id)
			var area := str(a.get("area", p.area))
			if rg.is_empty() or engine.romance_game_block(id, area) != "":
				presenter.toast("Kegiatan berdua tidak tersedia di sini.")
				return
			waiting = true
			presenter.open_minigame(rg.get("minigame", ""), func(score: int):
				if score < 0:
					presenter.toast("Permainan dibatalkan.")
					_resume()
					return
				var first := not p.has_flag("ROM_GAME_" + id.to_upper() + "_ONCE")
				var result := engine.complete_romance_game(id, area, score)
				presenter.toast(result)
				if first and score >= int(rg.get("minScore", 1)) and result.begins_with("Kenangan baru!"):
					var sid := str(rg.get("scene", "")) + "@" + p.route
					if not Data.scene(sid).is_empty():
						presenter.play_scene(sid, _resume)
						return
				_resume())
		"shop":
			var id := str(a.get("id", ""))
			if not Data.quests.get("shops", {}).has(id):
				presenter.toast("Toko tidak tersedia.")
				return
			waiting = true
			presenter.open_shop(id, _resume)
		"work":
			var job_id := str(a.get("id", ""))
			var job: Dictionary = Data.quests.get("jobs", {}).get(job_id, {})
			if job.is_empty() or job.get("minigame", "") == "" or not engine.job_ready(job_id):
				presenter.toast("Shift hari ini tidak tersedia.")
				return
			waiting = true
			presenter.open_minigame(job.minigame, func(score: int):
				if score >= 0:
					p.add_count("last_" + job.minigame, score - p.count("last_" + job.minigame))
					presenter.toast(engine.complete_work(job_id, score))
				_resume())
		"worldEvent":
			presenter.toast(engine.complete_world_event(str(a.get("id", "")), p.area))
		"deliveryStart":
			presenter.toast(engine.start_delivery())
		"deliveryDrop":
			presenter.toast(engine.deliver(str(a.get("address", ""))))
		"warp":
			waiting = true
			presenter.warp(str(a.get("area", "")), float(a.get("x", 0)), float(a.get("y", 0)), str(a.get("dir", "down")), _resume)
		"chapterCard":
			waiting = true
			presenter.chapter_card(str(a.get("chapter", "")), _resume)
		"chapterEnd":
			engine.apply(a)
			waiting = true
			presenter.chapter_end(str(a.get("chapter", "")), _resume)
		"credits":
			waiting = true
			presenter.credits(_resume)
		"cine":
			var cmds := engine.resolve(a.get("cmds", []))
			waiting = true
			presenter.cine_play(cmds, func():
				for c in cmds:
					if c.get("c") == "say":
						engine.add_flags(Data.scene(str(c.get("scene", ""))).get("flags", []))
				_resume())
		"toast":
			presenter.toast(str(a.get("text", "")))
		"sfx":
			presenter.sfx(str(a.get("id", "")))
		"music":
			presenter.music(str(a.get("id", "")))
		"emote":
			presenter.emote(str(a.get("who", "")), str(a.get("e", "heart")))
		"companion":
			engine.apply(a)
			presenter.companion_changed(p.companion)
		"step":
			engine.apply(a)
			presenter.step_changed()
			var ns := engine.step()
			if not ns.get("onStart", []).is_empty():
				_push_front(engine.resolve(ns.onStart))
		_:
			engine.apply(a)
