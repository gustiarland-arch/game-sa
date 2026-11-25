class_name PuzzleOverlay
extends Control
## Three-symbol order puzzle (port of PuzzleOverlay.java + PuzzleLogic). No permanent fail state;
## the mural hint shows after a few wrong tries if the player has found it.

var _pz: Dictionary
var _order: Array = []
var _entered: Array = []
var _fails := 0
var _hint_after := 2
var _has_hint := false
var _cb: Callable
var _shake := 0.0
var _solved_t := -1.0
var _msg := ""
var _sym_buttons: Array = []
var _cancel: Button
var _panel := Rect2()


static func icon_path(symbol: String) -> String:
	match symbol:
		"BUNGA": return "items/symbol_flower.png"
		"BUKU": return "items/symbol_book.png"
	return "items/symbol_star.png"


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	visible = false
	mouse_filter = Control.MOUSE_FILTER_STOP
	_cancel = UiTheme.button("Nanti saja", 22)
	_cancel.pressed.connect(func(): _close(false))
	add_child(_cancel)


func open(pz: Dictionary, route: String, has_hint: bool, done: Callable) -> void:
	_pz = pz; _cb = done; _has_hint = has_hint
	_order = pz.get("order", {}).get(route, pz.get("symbols", []))
	_hint_after = int(pz.get("hintAfterFails", 2))
	_entered = []; _fails = 0; _solved_t = -1; _shake = 0
	for b in _sym_buttons:
		b.queue_free()
	_sym_buttons = []
	var i := 0
	for s in pz.get("symbols", []):
		var b := UiTheme.icon_button(s, Data.tex(icon_path(s)), 22)
		b.pressed.connect(_press.bind(s))
		add_child(b)
		_sym_buttons.append(b)
		i += 1
	_msg = "Ingat petunjuk mural yang kamu lihat di plaza."
	visible = true
	if not _sym_buttons.is_empty():
		_sym_buttons[0].grab_focus.call_deferred()


func hint_visible() -> bool:
	return _fails >= _hint_after


## Same results as PuzzleLogic.input: "CORRECT", "WRONG" or "SOLVED".
func input(s: String) -> String:
	if _entered.size() >= _order.size():
		return "SOLVED"
	if _order[_entered.size()] == s:
		_entered.append(s)
		return "SOLVED" if _entered.size() >= _order.size() else "CORRECT"
	_entered.clear(); _fails += 1
	return "WRONG"


func _press(s: String) -> void:
	if _solved_t >= 0:
		return
	match input(s):
		"WRONG":
			Audio.sfx("soft_wrong"); _shake = 0.4
			_msg = "Urutannya belum tepat. Coba lagi dari awal, pelan-pelan saja."
		"SOLVED":
			Audio.sfx("sparkle"); _solved_t = 0.9; _msg = "Simbol-simbolnya menyala!"
		_:
			Audio.sfx("page"); _msg = "Simbol ke-%d menyala..." % _entered.size()


func _close(ok: bool) -> void:
	visible = false
	var c := _cb
	_cb = Callable()
	if c.is_valid():
		c.call(ok)


func _process(dt: float) -> void:
	if not visible:
		return
	if _shake > 0:
		_shake -= dt
	if _solved_t >= 0:
		_solved_t -= dt
		if _solved_t < 0:
			_close(true)
			return
	var w := minf(860, size.x - 60)
	var h := minf(560, size.y - 60)
	var sx := sin(_shake * 60.0) * 8.0 if _shake > 0 else 0.0
	_panel = Rect2((size.x - w) / 2 + sx, (size.y - h) / 2, w, h)
	var bw := (w - 120) / 3.0
	for i in _sym_buttons.size():
		_sym_buttons[i].position = _panel.position + Vector2(30 + i * (bw + 30), h - 184)
		_sym_buttons[i].size = Vector2(bw, 84)
	_cancel.position = _panel.position + Vector2((w - 240) / 2, h - 88)
	_cancel.size = Vector2(240, 64)
	queue_redraw()


func _unhandled_key_input(e: InputEvent) -> void:
	if not visible or not e.pressed:
		return
	var k: int = e.keycode
	if k >= KEY_1 and k <= KEY_3 and k - KEY_1 < _sym_buttons.size():
		_press(_pz.symbols[k - KEY_1])
	elif k == KEY_ESCAPE:
		_close(false)
	get_viewport().set_input_as_handled()


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color(UiTheme.BG, 0.6))
	var p := _panel
	UiTheme.panel().draw(get_canvas_item(), p)
	UiTheme.draw_text(self, str(_pz.get("title", "Puzzle")), p.position.x + 36, p.position.y + 26, 30, UiTheme.INK, "left", 0, "title")
	UiTheme.draw_text(self, "Susun tiga simbol di meja sesuai urutan petunjukmu.", p.position.x + 36, p.position.y + 82, 20, UiTheme.INK_SOFT, "left", p.size.x - 72)
	var slot := 96.0
	var gap := 34.0
	var x0 := p.position.x + (p.size.x - (slot * 3 + gap * 2)) / 2
	var sy := p.position.y + 154
	for i in _order.size():
		var r := Rect2(x0 + i * (slot + gap), sy, slot, slot)
		UiTheme.panel(Color("3a2e52"), Color("57476f"), 14, 2, 0).draw(get_canvas_item(), r)
		if i < _entered.size():
			draw_texture_rect(Data.tex(icon_path(_entered[i])), r.grow(-12), false)
		else:
			UiTheme.draw_text(self, str(i + 1), r.position.x, r.position.y + 30, 26, UiTheme.CREAM, "center", slot)
	UiTheme.draw_text(self, _msg, p.position.x + 30, p.position.y + 268, 20, UiTheme.INK, "center", p.size.x - 60)
	if hint_visible() and _has_hint:
		UiTheme.draw_text(self, "Petunjuk mural: " + " → ".join(_order), p.position.x + 30, p.position.y + 300, 20, UiTheme.PINK_DEEP, "center", p.size.x - 60)
