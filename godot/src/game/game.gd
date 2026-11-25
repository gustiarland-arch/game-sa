class_name Game
extends Node
## One play session: world + quest engine + action runner + dialogue + cutscenes + interaction.
## Port of screens/GameScreen.java and PlayerController/TownDirector (story parts). Implements the
## ActionRunner presenter and the Cutscene host.

signal idle
signal quit_to_title
signal replay_requested(progress: Progress)

var p: Progress
var engine: QuestEngine
var runner: ActionRunner
var world: World
var cine: Cutscene
var dialog: DialogBox
var replay := false

var _ui: CanvasLayer
var _overlay: CutsceneOverlay
var _toast: Label
var _toast_time := 0.0
var hud: Hud
var controls: TouchControls
var pause: PauseMenu
var minigame: MinigameOverlay
var puzzle: PuzzleOverlay
var shop: ShopOverlay
var book: MemoryBook
var romance: RomanceOverlay
var _clock_acc := 0.0
var _prompt: PanelContainer
var _prompt_label: Label
var _card: Control
var _card_done: Callable
var _fade: ColorRect
var _target := {}                 # {kind, data, x, y, label}
var _spawned := {}                # cutscene extras
var _markers := {}                # interactable id -> Node2D
var _time := 0.0


func setup(progress: Progress, is_replay := false) -> Game:
	p = progress
	replay = is_replay
	return self


func _ready() -> void:
	engine = QuestEngine.new(p, replay)
	engine.both_routes_completed = SaveStore.both_completed("C06")
	runner = ActionRunner.new(engine, self)
	world = World.new()
	add_child(world)
	cine = Cutscene.new()
	cine.host = self
	world.add_child(cine)
	world.cine = cine
	world.door_touched.connect(_on_door)
	_build_ui()
	world.flags = p.flags
	world.start(p.route, p.area, Vector2(p.x, p.y), p.dir)
	world.partner_mode = 2 if p.companion else 0
	_after_enter(false)


func _build_ui() -> void:
	_ui = CanvasLayer.new()
	add_child(_ui)
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ui.add_child(root)
	_overlay = CutsceneOverlay.new()
	_overlay.cine = cine
	cine.overlay = _overlay
	root.add_child(_overlay)
	hud = Hud.new()
	root.add_child(hud)
	controls = TouchControls.new()
	root.add_child(controls)
	controls.action_pressed.connect(func():
		if dialog.active:
			dialog.advance()
		else:
			interact())
	controls.pause_pressed.connect(open_pause)
	controls.book_pressed.connect(open_book)
	# interaction prompt (bottom centre)
	_prompt = PanelContainer.new()
	var pp := UiTheme.panel(UiTheme.PINK_DEEP, Color("a8456a"), 20, 2, 8)
	pp.content_margin_left = 20; pp.content_margin_right = 20; pp.content_margin_top = 8; pp.content_margin_bottom = 9
	_prompt.add_theme_stylebox_override("panel", pp)
	_prompt_label = UiTheme.label("", 20, Color.WHITE, "bold")
	_prompt.add_child(_prompt_label)
	_prompt.visible = false
	root.add_child(_prompt)
	# toast
	_toast = UiTheme.label("", 21, UiTheme.CREAM, "bold")
	_toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_toast.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	_toast.add_theme_constant_override("shadow_offset_y", 2)
	_toast.add_theme_constant_override("shadow_outline_size", 6)
	_toast.set_anchors_preset(Control.PRESET_CENTER_TOP)
	root.add_child(_toast)
	# dialogue
	dialog = DialogBox.new()
	root.add_child(dialog)
	dialog.line_shown.connect(_on_line)
	dialog.choice_made.connect(_on_choice)
	minigame = MinigameOverlay.new()
	root.add_child(minigame)
	puzzle = PuzzleOverlay.new()
	root.add_child(puzzle)
	shop = ShopOverlay.new()
	shop.engine = engine
	root.add_child(shop)
	romance = RomanceOverlay.new()
	romance.engine = engine
	root.add_child(romance)
	book = MemoryBook.new()
	root.add_child(book)
	book.replay_requested.connect(func(ch: String):
		var rp := p.replay_from(ch)
		if rp == null:
			toast("Replay belum tersedia")
			return
		save_now()
		replay_requested.emit(rp))
	# fade + chapter card on top
	_fade = ColorRect.new(); _fade.color = Color(0.03, 0.02, 0.06, 0); _fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(_fade)
	_card = Control.new(); _card.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); _card.visible = false
	root.add_child(_card)
	pause = PauseMenu.new()
	root.add_child(pause)
	pause.resume.connect(func(): pause.visible = false; get_tree().paused = false)
	pause.save_requested.connect(func(): pause.set_status("Progress tersimpan" if save_now() else "Gagal menyimpan. Periksa ruang penyimpanan."))
	pause.quit_requested.connect(func():
		get_tree().paused = false
		if not replay:
			save_now()
		quit_to_title.emit())
	pause.process_mode = Node.PROCESS_MODE_ALWAYS
	pause.book_requested.connect(func():
		pause.visible = false
		get_tree().paused = false
		open_book())


## Called right after the game node enters the tree for a new game.
func begin_new_game() -> void:
	var l: Array = [{"do": "chapterCard", "chapter": engine.chapter()}]
	l.append_array(engine.resolve(engine.step().get("onStart", [])))
	runner.run(l)


func resume_game() -> void:
	toast(("Mode replay: progres tidak disimpan" if replay else "Cerita %s dimuat" % Routes.display(p.route)))
	runner.run(engine.on_enter_area(p.area))


# ------------------------------------------------------------------ frame
func _process(delta: float) -> void:
	_time += delta
	var busy := dialog.active or minigame.visible or puzzle.visible or shop.visible or book.visible or romance.visible or cine.active or runner.busy() or _card.visible or _fade.color.a > 0.02
	world.locked = busy
	world.input_vec = controls.vec if not busy else Vector2.ZERO
	world.sprint_held = controls.sprint
	controls.visible = not cine.letterboxed()
	if not busy:
		_tick_clock(delta)
	world.talking_to = _target.get("npc_id", "") if dialog.active else ""
	p.x = world.player.position.x; p.y = world.player.position.y
	p.dir = world.player.dir_name()
	if not replay:
		p.play_seconds += delta
	if not busy:
		_find_target()
	_update_hud(delta, busy)
	for id in _markers:
		var m: Node2D = _markers[id]
		if m.has_meta("bob"):
			var bob := sin(_time * 2.4 + m.position.x) * 2.5
			for c in m.get_children():
				c.position.y = c.get_meta("y0", 0.0) + bob


## 1 real second = 1 game minute while exploring (WorldClock). The day ends at 02:00.
func _tick_clock(delta: float) -> void:
	_clock_acc += delta
	while _clock_acc >= 1.0:
		_clock_acc -= 1.0
		if p.minute < WorldClock.DAY_END:
			p.minute += 1
			if p.minute % 15 == 0:
				refresh_npcs()


func _update_hud(delta: float, busy: bool) -> void:
	hud.refresh(engine, cine.letterboxed())
	_toast_time = maxf(0, _toast_time - delta)
	_toast.modulate.a = clampf(_toast_time * 2.0, 0, 1)
	_toast.position = Vector2(_ui.get_viewport().get_visible_rect().size.x / 2 - _toast.size.x / 2, 82)
	var show := not busy and not _target.is_empty()
	_prompt.visible = show
	if show:
		_prompt_label.text = "E / Ketuk  ·  " + str(_target.get("label", "Periksa"))
		var vs := _ui.get_viewport().get_visible_rect().size
		_prompt.position = Vector2(vs.x / 2 - _prompt.size.x / 2, vs.y - 92)


func _unhandled_input(event: InputEvent) -> void:
	if dialog.active:
		return
	if cine.active and event is InputEventKey:
		cine.fast = event.pressed and event.keycode == KEY_SPACE
		return
	if _card.visible and (event.is_action_pressed("ui_accept") or (event is InputEventMouseButton and event.pressed)):
		_finish_card()
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("ui_cancel") and not world.locked:
		open_pause()
		get_viewport().set_input_as_handled()
		return
	if event is InputEventKey and event.pressed and event.keycode == KEY_M and not world.locked:
		open_book()
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("ui_accept") or (event is InputEventKey and event.pressed and event.keycode == KEY_E):
		interact()
		get_viewport().set_input_as_handled()


func open_romance() -> void:
	var pl := world.player
	pl.face_to(world.partner); world.partner.face_to(pl)
	controls.reset()
	romance.open(p.area, func(acts: Array, msg: String):
		save_now()
		toast(msg)
		if msg.begins_with("Hadiah"): sfx("gift", 0.7)
		elif msg.begins_with("Kencan"): sfx("heart", 0.7)
		elif msg.begins_with("Aksi berdua"): sfx("hug", 0.6)
		runner.run(acts))


func open_book() -> void:
	if world.locked:
		return
	controls.reset()
	book.open(p, replay)


func open_pause() -> void:
	if world.locked or pause.visible:
		return
	controls.reset()
	pause.open(p.dialogue_history)
	get_tree().paused = true


## Save the slot and fold its progress into global.json. Replays never save.
func save_now() -> bool:
	if replay:
		return false
	if not SaveStore.save_slot(p):
		toast("Gagal menyimpan! Periksa ruang penyimpanan.")
		return false
	var added = SaveStore.absorb_global(p)
	if added is Array:
		for id in added:
			toast("Prestasi terbuka: " + Achievements.name_of(id))
			Audio.sfx("sparkle", 0.6)
	return true


# ------------------------------------------------------------------ areas
func _on_door(d: Dictionary, old: Vector2) -> void:
	if world.locked:
		return
	var lock := engine.door_lock(d)
	if lock != "":
		toast(lock)
		sfx("soft_wrong")
		world.player.position = old
		world.door_cooldown = 1.2
		return
	_fade_through(func():
		_enter(str(d.get("to", "")), Vector2(float(d.get("tx", 0)), float(d.get("ty", 0))), str(d.get("dir", "down")), true),
		func(): runner.run(engine.on_enter_area(p.area)))


func _enter(area_id: String, pos: Vector2, facing: String, announce: bool) -> void:
	if Data.area(area_id).is_empty():
		area_id = Routes.room(p.route)
	if announce:
		sfx("door_open", 0.45)
	world.enter_area(area_id, pos, facing)
	p.area = area_id
	p.visited_areas[area_id] = true
	_after_enter(announce)


func _after_enter(_announce: bool) -> void:
	_spawned.clear()
	refresh_npcs()
	_build_markers()


## Town NPCs by schedule, and the partner when the active step places them in this area.
func refresh_npcs() -> void:
	var keep := {}
	for n in engine.town_npcs_now(p.area):
		var pl := engine.npc_place(n)
		var id: String = n.get("id", "?")
		keep[id] = true
		if not world.npcs.has(id):
			world.add_npc(id, n.get("sprite", id), Vector2(pl.x, pl.y), pl.dir, pl.wander)
		else:
			var b: Dictionary = world.npc_brain[id]
			b.home = world.nearest_open(Vector2(pl.x, pl.y)); b.target = b.home; b.radius = pl.wander
	for id in world.npcs.keys():
		if not keep.has(id) and not _spawned.has(id):
			world.remove_npc(id)
	if world.partner_mode != 2:
		world.partner_mode = 0
		for n in engine.npcs(p.area):
			if n.who == world.partner.character:
				world.partner_mode = 1
				world.partner.position = Vector2(n.x, n.y)
				world.partner.dir = Actor.dir_of(n.dir)
				world.partner.facing8 = [0, 2, 6, 4][world.partner.dir]
				world.partner.walking = false
	world.partner.visible = world.partner_mode != 0


## Quest item sprites (bobbing) and ✦ markers for interactables in this area.
func _build_markers() -> void:
	for c in world.extras.get_children():
		c.queue_free()
	_markers.clear()
	var marker_tex := Data.tex("ui/marker.png")
	for it in engine.interactables(p.area) + engine.side_interactables(p.area):
		var n := Node2D.new()
		n.position = Vector2(float(it.get("x", 0)), float(it.get("y", 0)))
		var spr: Dictionary = it.get("sprite", {})
		if not spr.is_empty():
			var t := Data.tex(spr.get("image", ""))
			if t:
				n.position = Vector2(float(spr.get("x", n.position.x)), float(spr.get("y", n.position.y)))
				var s := Sprite2D.new()
				s.texture = t
				s.offset = Vector2(0, -t.get_height() / 2.0)
				# quest items are painted large (up to 192 px); show them at a readable world size
				var k := minf(1.0, 34.0 / maxf(t.get_width(), t.get_height()))
				s.scale = Vector2(k, k)
				s.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS if k < 1.0 else CanvasItem.TEXTURE_FILTER_NEAREST
				n.add_child(s)
				if bool(spr.get("bob", false)):
					n.set_meta("bob", true); n.set_meta("base", 0.0)
		if bool(it.get("marker", true)) and marker_tex and engine.interactables(p.area).has(it):
			var m := Sprite2D.new()
			m.texture = marker_tex
			var top := -40.0 if n.get_child_count() > 0 else -34.0
			m.position = Vector2(0, top)
			m.set_meta("y0", top)
			var iid := str(it.get("id", ""))
			m.modulate = Color(1, 0.85, 0.45) if (iid.begins_with("shard") or iid.begins_with("WE27_") or iid.begins_with("V50_")) else Color(0.97, 0.7, 0.83)
			n.add_child(m)
			if not n.has_meta("bob"):
				n.set_meta("bob", true); n.set_meta("base", top)
		if n.get_child_count() > 0:
			world.extras.add_child(n)
			_markers[str(it.get("id", ""))] = n
		else:
			n.free()


# ------------------------------------------------------------------ interaction
func _d(x: float, y: float) -> float:
	return world.player.position.distance_to(Vector2(x, y))


func _find_target() -> void:
	_target = {}
	var best := INF
	for it in engine.interactables(p.area):
		var d := _d(float(it.get("x", 0)), float(it.get("y", 0)))
		if d <= float(it.get("r", 64)) and d < best:
			best = d
			_target = {"kind": "quest", "data": it, "label": _label(it)}
	if not _target.is_empty():
		return
	best = INF
	for it in engine.side_interactables(p.area):
		var d := _d(float(it.get("x", 0)), float(it.get("y", 0)))
		if d <= float(it.get("r", 64)) and d < best:
			best = d
			_target = {"kind": "side", "data": it, "label": _label(it)}
	for n in engine.town_npcs_now(p.area):
		var a: Actor = world.npcs.get(n.get("id"))
		if a == null:
			continue
		var d := _d(a.position.x, a.position.y)
		if d <= 64 and d < best and not engine.npc_dialog(n).is_empty():
			best = d
			_target = {"kind": "npc", "data": n, "npc_id": n.get("id"), "label": "Bicara dengan " + str(n.get("name", n.get("id")))}
	if not _target.is_empty():
		return
	if world.partner_mode == 2 and _d(world.partner.position.x, world.partner.position.y) <= 58:
		var t := engine.partner_talk(p.area)
		if not t.is_empty():
			_target = {"kind": "talk", "data": t, "label": "Ngobrol dengan " + Routes.display(world.partner.character)}
			return
		if engine.romance_ready():
			_target = {"kind": "romance", "label": "Waktu berdua dengan " + Routes.display(world.partner.character)}
			return
	best = INF
	for e in engine.examine(world.area):
		var d := _d(float(e.get("x", 0)), float(e.get("y", 0)))
		if d <= float(e.get("r", 56)) and d < best:
			best = d
			_target = {"kind": "examine", "data": e, "label": e.get("label", "Periksa")}


func _label(it: Dictionary) -> String:
	return str(it.get("labelByRoute", {}).get(p.route, it.get("label", "Periksa")))


func interact() -> void:
	if world.locked:
		return
	var pl := world.player
	match _target.get("kind", ""):
		"quest", "side":
			var it: Dictionary = _target.data
			pl.face(float(it.get("x", 0)) - pl.position.x, float(it.get("y", 0)) - pl.position.y)
			runner.run(engine.resolve(it.get("actions", [])))
		"npc":
			var a: Actor = world.npcs.get(_target.npc_id)
			if a:
				pl.face_to(a); a.face_to(pl)
			runner.run(engine.resolve(engine.npc_dialog(_target.data).get("actions", [])))
		"talk":
			pl.face_to(world.partner); world.partner.face_to(pl)
			runner.run(engine.talk_actions(_target.data))
		"romance":
			open_romance()
		"examine":
			var e: Dictionary = _target.data
			pl.face(float(e.get("x", 0)) - pl.position.x, float(e.get("y", 0)) - pl.position.y)
			sfx("page_turn", 0.42)
			dialog.start(e.get("lines", {}).get(p.route, []), null, p.route)
		_:
			toast("Dekati penanda ✦ untuk berinteraksi")


# ------------------------------------------------------------------ dialogue hooks
func _on_line(line: Dictionary) -> void:
	var spk := str(line.get("s", "narrator"))
	var sp := Data.speaker(spk)
	p.add_history(sp.get("name", spk), str(line.get("e", "neutral")), str(line.get("t", "")), p.area, p.day)
	var e := Data.emotion(str(line.get("e", "neutral")))
	var who: Actor = null
	if spk == world.player.character:
		who = world.player
	elif spk == world.partner.character and world.partner_mode != 0:
		who = world.partner
	else:
		for id in world.npcs:
			if world.npcs[id].character == sp.get("sprite", ""):
				who = world.npcs[id]
	if who and e.get("emote") != null:
		who.show_emote(e.emote, 1.8)
	if line.get("e") == "jatuh_cinta":
		sfx("cinema_heartbeat", 0.18)


func _on_choice(c: Dictionary) -> void:
	p.add_history("Pilihanmu", "neutral", str(c.get("text", "")), p.area, p.day)
	engine.add_flags(c.get("flags", []))


# ------------------------------------------------------------------ presenter (ActionRunner)
func play_scene(id: String, done: Callable) -> void:
	var sc := Data.scene(id)
	if sc.is_empty():
		done.call()
		return
	if world.partner_mode != 0 and not cine.active:
		world.partner.face_to(world.player)
		if world.partner_mode == 1:
			world.player.face_to(world.partner)
	dialog.start(sc.get("lines", []), sc.get("choices", []), p.route, done)


func play_scene_part(id: String, from: int, n: int, done: Callable) -> void:
	var sc := Data.scene(id)
	if sc.is_empty():
		done.call()
		return
	var lines: Array = sc.get("lines", [])
	var a := clampi(from, 0, lines.size())
	var b := lines.size() if n <= 0 else mini(lines.size(), a + n)
	dialog.start(lines.slice(a, b), sc.get("choices", []) if b >= lines.size() else null, p.route, done)


func play_lines(lines: Array, _name, done: Callable) -> void:
	dialog.start(lines, null, p.route, done)


func open_puzzle(id: String, done: Callable) -> void:
	var pz: Dictionary = Data.quests.get("puzzles", {}).get(id, {})
	if pz.is_empty():
		done.call(true)
		return
	controls.reset()
	puzzle.open(pz, p.route, p.has_flag(str(pz.get("hintFlag", {}).get(p.route, ""))), done)


func open_minigame(id: String, done: Callable) -> void:
	var mg: Dictionary = Data.quests.get("minigames", {}).get(id, {})
	controls.reset()
	minigame.open(id, mg, p.route, done)


func open_shop(id: String, done: Callable) -> void:
	controls.reset()
	shop.open(id, done, func(): save_now())


func warp(area_id: String, x: float, y: float, facing: String, done: Callable) -> void:
	_fade_through(func(): _enter(area_id, Vector2(x, y), facing, true), done)


func chapter_card(chapter: String, done: Callable) -> void:
	_show_card(Data.chapter_title(chapter), p.route.to_upper() + " ROUTE", done)


func chapter_end(chapter: String, done: Callable) -> void:
	var sub := "Progress tersimpan. Memory Book diperbarui."
	if replay:
		sub = "Replay selesai. Kembali ke menu utama."
	_show_card("✦ " + Data.chapter_title(chapter) + " — selesai ✦", sub, done)


func credits(done: Callable) -> void:
	music("cinema_our_tomorrow")
	_show_card("Arland & Sofia", "\n".join(Data.quests.get("credits", [])), done)


func cine_play(cmds: Array, done: Callable) -> void:
	cine.start(cmds, func():
		for a in [world.player, world.partner]:
			a.clear_pose(); a.alpha = 1.0
		for id in world.npcs:
			world.npcs[id].clear_pose()
		world.partner.visible = world.partner_mode != 0
		if world.partner_mode == 2 and world.partner.position.distance_to(world.player.position) > 200:
			world.place_partner_beside()
		done.call())


func toast(text: String) -> void:
	_toast.text = text
	_toast.reset_size()
	_toast_time = 2.6


func sfx(id: String, mult := 1.0) -> void:
	Audio.sfx(id, mult)


func music(id: String) -> void:
	Audio.music(id)


func emote(who: String, e: String) -> void:
	var a := actor(who)
	if a:
		a.show_emote(e, 1.8)


func companion_changed(on: bool) -> void:
	if on:
		if world.partner_mode != 1:
			world.place_partner_beside()
		world.partner_mode = 2
	else:
		world.partner_mode = 0
		p.holding_hands = false
	refresh_npcs()


func step_changed() -> void:
	refresh_npcs()
	_build_markers()
	hud.flash_objective()
	sfx("quest_complete", 0.22)


func on_idle() -> void:
	_build_markers()
	if not replay and is_inside_tree():
		save_now()        # autosave whenever the story queue settles
	idle.emit()


# ------------------------------------------------------------------ cutscene host
func actor(who: String) -> Actor:
	match who:
		"player", world.player.character:
			return world.player
		"partner", world.partner.character:
			return world.partner
	if world.npcs.has(who):
		return world.npcs[who]
	for id in world.npcs:
		if world.npcs[id].character == who:
			return world.npcs[id]
	return null


func spawn(id: String, sprite: String, x: float, y: float, d: int) -> void:
	var a := world.add_npc(id, sprite, Vector2(x, y), ["down", "left", "right", "up"][d], 0)
	a.position = Vector2(x, y)
	_spawned[id] = true


func despawn(id: String) -> void:
	world.remove_npc(id)
	_spawned.erase(id)


func show_partner(on: bool) -> void:
	world.partner.visible = on


func say(scene_id: String, from: int, n: int, done: Callable) -> void:
	play_scene_part(scene_id, from, n, done)


func line(s: String, e: String, t: String, done: Callable) -> void:
	dialog.start([{"s": s, "e": e, "t": t}], null, p.route, done)


func cam_center() -> Vector2:
	return world.camera.get_screen_center_position()


func can_stand(x: float, y: float) -> bool:
	return world.can_stand(x, y)


# ------------------------------------------------------------------ fade & cards
func _fade_through(mid: Callable, end: Callable) -> void:
	var tw := create_tween()
	tw.tween_property(_fade, "color:a", 1.0, 0.25)
	tw.tween_callback(mid)
	tw.tween_property(_fade, "color:a", 0.0, 0.31)
	tw.tween_callback(func():
		if end.is_valid():
			end.call())


func _show_card(title: String, sub: String, done: Callable) -> void:
	for c in _card.get_children():
		c.queue_free()
	var bg := ColorRect.new(); bg.color = Color(UiTheme.BG, 0.94); bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_card.add_child(bg)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_card.add_child(center)
	var box := VBoxContainer.new()
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_theme_constant_override("separation", 14)
	var t := UiTheme.label(title, 46, UiTheme.CREAM, "title")
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var line_r := ColorRect.new(); line_r.color = Color(UiTheme.GOLD, 0.7); line_r.custom_minimum_size = Vector2(220, 2)
	line_r.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	var s := UiTheme.label(sub, 22, UiTheme.GOLD, "body")
	s.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var hint := UiTheme.label("Ketuk untuk lanjut", 16, Color(UiTheme.LAVENDER, 0.85), "body")
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	for c in [t, line_r, s, hint]:
		box.add_child(c)
	center.add_child(box)
	_card.modulate.a = 0
	_card.visible = true
	_card_done = done
	create_tween().tween_property(_card, "modulate:a", 1.0, 0.35)
	get_tree().create_timer(3.2).timeout.connect(func():
		if _card.visible and _card_done == done:
			_finish_card())


func _finish_card() -> void:
	if not _card.visible:
		return
	var d := _card_done
	_card_done = Callable()
	var tw := create_tween()
	tw.tween_property(_card, "modulate:a", 0.0, 0.3)
	tw.tween_callback(func():
		_card.visible = false
		if d.is_valid():
			d.call())
