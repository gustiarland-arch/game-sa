class_name MinigameOverlay
extends Control
## Minigame frame: title, hint, quit button, result screen (port of MinigameOverlay.java).
## Calls done(score) with -1 when the player quits.

var game: Minigame
var _cb: Callable
var _title := ""
var _desc := ""
var _result := false
var _quit: Button
var _done: Button
var px := 0.0
var py := 0.0
var pw := 0.0
var ph := 0.0


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	visible = false
	mouse_filter = Control.MOUSE_FILTER_STOP
	_quit = UiTheme.button("Keluar", 19)
	_quit.pressed.connect(func(): _finish(-1))
	add_child(_quit)
	_done = UiTheme.button("Lanjut", 24, true)
	_done.pressed.connect(func(): _finish(game.score))
	add_child(_done)


func active() -> bool:
	return visible


func open(id: String, cfg: Dictionary, route: String, done: Callable) -> void:
	_cb = done
	game = Games.create(str(cfg.get("type", id)))
	game.init(cfg, route)
	_title = str(cfg.get("title", "Minigame"))
	_desc = str(cfg.get("desc", ""))
	_result = false
	visible = true
	_layout()


func _finish(score: int) -> void:
	visible = false
	var c := _cb
	_cb = Callable()
	if c.is_valid():
		c.call(score)


func _layout() -> void:
	var W := size.x
	var H := size.y
	pw = minf(980, W - 40); ph = minf(640, H - 40); px = (W - pw) / 2; py = (H - ph) / 2
	game.x = px + 24; game.y = py + 24; game.w = pw - 48; game.h = ph - 150
	game.screen_h = H
	# Java y-up rects -> Godot y-down
	_quit.position = Vector2(px + pw - 160, H - (py + ph - 76) - 56); _quit.size = Vector2(140, 56)
	_done.position = Vector2(px + (pw - 260) / 2, H - (py + 30) - 66); _done.size = Vector2(260, 66)
	_quit.visible = not _result
	_done.visible = _result


func _process(dt: float) -> void:
	if not visible or game == null:
		return
	game.update(dt)
	if game.finished and not _result:
		_result = true
		_done.grab_focus.call_deferred()
	_layout()
	queue_redraw()


func _gui_input(e: InputEvent) -> void:
	if _result:
		return
	var pos = null
	if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
		pos = e.position
	elif e is InputEventScreenTouch and e.pressed:
		pos = e.position
	if pos != null:
		game.tap(pos.x, size.y - pos.y)
		accept_event()


func _unhandled_key_input(e: InputEvent) -> void:
	if not visible or not (e is InputEventKey) or not e.pressed:
		return
	var k: int = e.keycode
	if k >= KEY_1 and k <= KEY_9:
		if not _result:
			game.key(k - KEY_1)
	elif k == KEY_SPACE or k == KEY_ENTER:
		if _result:
			_finish(game.score)
		else:
			game.key(99)
	elif k == KEY_ESCAPE and not _result:
		_finish(-1)
	get_viewport().set_input_as_handled()


func _draw() -> void:
	if game == null:
		return
	var H := size.y
	draw_rect(Rect2(Vector2.ZERO, size), Color(UiTheme.BG, 0.7))
	UiTheme.panel(Color("2f2545"), Color("57476f"), 22, 3, 10).draw(get_canvas_item(), Rect2(px, H - py - ph, pw, ph))
	game.canvas = self
	game.text(_title, px + 28, py + ph - 24, UiTheme.CREAM, 0.55, "left", 0, "title")
	game.text(_desc, px + 28, py + ph - 84, UiTheme.LAVENDER, 0.75, "left", pw - 220)
	if _result:
		game.text("★ " + game.result_text, px, py + ph / 2 + 40, UiTheme.GOLD, 0.45, "center", pw, "title")
	else:
		game.draw()
