extends Node
## Boot. Title, slots and settings menus come in phase 3; for now a new Sofia game starts directly.
## Capture modes for automated QA (never used by players):
##   -- --shot  <route> <area> <x> <y> <frames> <out.png> [x:y;x:y waypoints]   free exploration
##   -- --story <route> <out_prefix> <frame,frame,...>                           new game, the story runs
##        by itself (dialogue advances every 50 frames, first choice taken) and a screenshot is saved
##        at each listed frame.

var game: Game
var _mode := ""
var _args := []
var _frame := 0
var _wp := 0
var _wps: Array = []
var _shots: Array = []


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var i := args.find("--shot")
	var j := args.find("--story")
	if i >= 0:
		_mode = "shot"
		_args = args.slice(i + 1)
		var p := Progress.new_game(_args[0], 1, Data.first_step, Data.area(_args[1]))
		p.area = _args[1]; p.x = float(_args[2]); p.y = float(_args[3]); p.companion = true
		if _args.size() > 6:
			for pt in _args[6].split(";", false):
				var xy: PackedStringArray = pt.split(":")
				_wps.append(Vector2(float(xy[0]), float(xy[1])))
		_start(p, false)
	elif args.has("--minigame"):
		_mode = "minigame"
		_args = args.slice(args.find("--minigame") + 1)   # id route out_prefix
		_start(Progress.new_game(_args[1], 1, Data.first_step, Data.area(Routes.room(_args[1]))), false)
	elif args.has("--title"):
		_mode = "title"
		_args = args.slice(args.find("--title") + 1)
		_title()
	elif j >= 0:
		_mode = "story"
		_args = args.slice(j + 1)
		for f in _args[2].split(",", false):
			_shots.append(int(f))
		_start(Progress.new_game(_args[0], 1, Data.first_step, Data.area(Routes.room(_args[0]))), true)
	else:
		_title()


var _title_node: TitleScreen


func _title() -> void:
	if game:
		game.queue_free()
		game = null
	var layer := CanvasLayer.new()
	add_child(layer)
	_title_node = TitleScreen.new()
	layer.add_child(_title_node)
	_title_node.start_game.connect(func(p: Progress, is_new: bool):
		layer.queue_free()
		_start(p, is_new))


func _start(p: Progress, new_game: bool) -> void:
	game = Game.new().setup(p)
	add_child(game)
	game.quit_to_title.connect(_title)
	if new_game:
		game.begin_new_game()
	else:
		game.resume_game()


func _process(_delta: float) -> void:
	if _mode == "":
		return
	_frame += 1
	if _mode == "title":
		match _frame:
			40: await _save_plain(_args[0] + "_judul.png"); _title_node.show_routes()
			80: await _save_plain(_args[0] + "_route.png"); _title_node.show_slots("sofia")
			120: await _save_plain(_args[0] + "_slot.png"); get_tree().quit()
		return
	if _mode == "minigame":
		var ov := game.minigame
		if _args[0].begins_with("puzzle:") or _args[0].begins_with("shop:"):
			var id: String = _args[0].get_slice(":", 1)
			match _frame:
				20:
					if _args[0].begins_with("shop:"):
						game.p.coins = 30
						game.open_shop(id, func(): print("SHOP CLOSED"))
					else:
						game.p.add_flag("C01_HINT_" + _args[1].to_upper())
						game.open_puzzle(id, func(ok): print("PUZZLE ", ok))
				60: await _save(_args[2] + "_a.png")
				61:
					if game.shop.visible:
						game.shop._buy[0].pressed.emit()
					else:
						var sy: Array = game.puzzle._pz.symbols
						var o: Array = game.puzzle._order
						game.puzzle._press(o[1]); game.puzzle._press(o[2]); game.puzzle._press(o[0])
				100: await _save(_args[2] + "_b.png"); get_tree().quit()
			return
		match _frame:
			20: game.open_minigame(_args[0], func(sc): print("MINIGAME SCORE ", sc))
			70: await _save(_args[2] + "_main.png")
			71:
				for k in 6:
					ov.game.key(k % 4); ov.game.tap(ov.game.x + ov.game.w * (0.2 + 0.15 * k), ov.game.y + ov.game.h * 0.45)
			110: await _save(_args[2] + "_main2.png")
			111: ov.game.finished = true; ov.game.result_text = ov.game.result_text if ov.game.result_text != "" else "(hasil uji otomatis)"
			140: await _save(_args[2] + "_hasil.png"); get_tree().quit()
		return
	if _mode == "shot":
		var w := game.world
		if _wp < _wps.size():
			var d: Vector2 = _wps[_wp] - w.player.position
			if d.length() < 8:
				_wp += 1
				game.controls.vec = Vector2.ZERO
			else:
				game.controls.vec = d.normalized()
		else:
			game.controls.vec = Vector2.ZERO
		if _frame == int(_args[4]):
			await _save(_args[5])
			get_tree().quit()
	else:
		_autoplay()
		if _frame % 50 == 0:
			if game.dialog.choosing():
				game.dialog.choose(0)
			elif game.dialog.active:
				game.dialog.advance()
				game.dialog.advance()
			elif game._card.visible:
				game._finish_card()
		if _shots.has(_frame):
			await _save("%s_%04d.png" % [_args[1], _frame])
		if _frame >= _shots.max():
			print("STEP ", game.p.step, " AREA ", game.p.area, " FLAGS ", game.p.flags.size())
			get_tree().quit()


## Story autopilot for captures: walk to the active step's marker (crossing doors when it is in
## another area) and use it.
func _autoplay() -> void:
	var w := game.world
	game.controls.vec = Vector2.ZERO
	if w.locked:
		return
	var its := game.engine.interactables(game.p.area)
	if not its.is_empty():
		var it: Dictionary = its[0]
		var t := Vector2(float(it.get("x", 0)), float(it.get("y", 0)))
		var d := t - w.player.position
		if d.length() <= float(it.get("r", 64)) * 0.7:
			game._find_target()
			game.interact()
		else:
			game.controls.vec = d.normalized()
		return
	var goal := _goal_area()
	if goal == "" or goal == game.p.area:
		return
	var door := _next_door(game.p.area, goal)
	if door.is_empty():
		return
	var r: Array = door.rect
	var c := Vector2(r[0] + r[2] / 2.0, r[1] + r[3] / 2.0)
	game.controls.vec = (c - w.player.position).normalized()


func _goal_area() -> String:
	var st := game.engine.step()
	for it in st.get("interactables", []):
		if it.get("route") == null or it.get("route") == game.p.route:
			return Routes.resolve(it.get("area", ""), game.p.route)
	var ea: Dictionary = st.get("enterArea", {})
	return Routes.resolve(ea.get("area", ""), game.p.route) if ea.get("area") != null else ""


func _next_door(from: String, goal: String) -> Dictionary:
	var prev := {from: null}
	var q := [from]
	while not q.is_empty():
		var a: String = q.pop_front()
		if a == goal:
			break
		for d in Data.area(a).get("doors", []):
			var to := str(d.get("to", ""))
			if not prev.has(to) and Data.maps.has(to) and game.engine.door_lock(d) == "":
				prev[to] = [a, d]
				q.append(to)
	if not prev.has(goal):
		return {}
	var cur := goal
	while prev[cur] != null and prev[cur][0] != from:
		cur = prev[cur][0]
	return prev[cur][1] if prev[cur] != null else {}


func _save_plain(path: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(path)
	print("SHOT ", path)


func _save(path: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(path)
	print("SHOT ", path, " step=", game.p.step, " area=", game.p.area, " at ", game.world.player.position)
