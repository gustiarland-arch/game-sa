class_name RomanceOverlay
extends Control
## "Waktu Berdua": gifts, paid dates, daily moments, couple actions and the six shared games
## (port of RomanceOverlay.java). done(actions, message) runs after a successful choice.

const TABS := [["gift", "Berikan Hadiah"], ["date", "Ajak Kencan"], ["moment", "Momen Harian"], ["couple", "Aksi Berdua"], ["game", "Main Bareng"]]
const KIND := {"gift": "gifts", "date": "dates", "moment": "moments", "couple": "coupleActions", "game": "games"}

var engine: QuestEngine
var area := ""
var tab := "gift"
var page := 0
var status := ""
var _cb: Callable
var _tabs: Array = []
var _close: Button
var _prev: Button
var _next: Button
var _choices: Array = []
var _panel := Rect2()


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	visible = false
	mouse_filter = Control.MOUSE_FILTER_STOP
	for t in TABS:
		var b := UiTheme.button(t[1], 17)
		b.pressed.connect(func(): tab = t[0]; page = 0; status = ""; _rebuild())
		add_child(b)
		_tabs.append(b)
	_close = UiTheme.button("Selesai", 19)
	_close.pressed.connect(close)
	add_child(_close)
	_prev = UiTheme.button("<", 20)
	_prev.pressed.connect(func(): if page > 0: page -= 1; _rebuild())
	add_child(_prev)
	_next = UiTheme.button(">", 20)
	_next.pressed.connect(func(): if (page + 1) * 3 < _items().size(): page += 1; _rebuild())
	add_child(_next)


func open(at_area: String, done: Callable) -> void:
	area = at_area; _cb = done; tab = "gift"; page = 0
	status = "Hadiah, kencan, momen, aksi, dan enam permainan berdua."
	for g in _all("gifts"):
		Data.tex(_item(g.item).get("icon", ""))
	_rebuild()
	visible = true
	_tabs[0].grab_focus.call_deferred()


func close() -> void:
	visible = false
	_cb = Callable()


func _all(kind: String) -> Array:
	return Data.quests.get("romance", {}).get(kind, [])


func _items() -> Array:
	return _all(KIND[tab])


func _item(id: String) -> Dictionary:
	return Data.memory_book.get("items", {}).get(id, {})


func _finish(acts: Array, msg: String) -> void:
	var c := _cb
	close()
	if c.is_valid():
		c.call(acts, msg)


func _rebuild() -> void:
	for b in _choices:
		b.queue_free()
	_choices = []
	var items := _items()
	for i in range(page * 3, mini(items.size(), page * 3 + 3)):
		var e: Dictionary = items[i]
		var b := UiTheme.button("", 18)
		match tab:
			"gift":
				b.pressed.connect(func():
					var msg: String = engine.give_gift(e.item)
					if msg.begins_with("Hadiah diberikan!"): _finish(engine.gift_actions(e.item), msg)
					else: status = msg)
			"date":
				b.pressed.connect(func():
					var msg: String = engine.start_date(e.id, area)
					if msg.begins_with("Kencan dimulai!"): _finish(engine.date_actions(e.id), msg)
					else: status = msg)
			"moment":
				b.pressed.connect(func():
					var msg: String = engine.start_moment(e.id, area)
					if msg.begins_with("Momen berdua!"): _finish(engine.moment_actions(e.id), msg)
					else: status = msg)
			"game":
				b.pressed.connect(func():
					var reason: String = engine.romance_game_block(e.id, area)
					if reason != "": status = reason; return
					_finish([{"do": "romanceGame", "id": e.id, "area": area}], "Mulai " + str(e.get("title", ""))))
			_:
				b.pressed.connect(func():
					var msg: String = engine.start_couple_action(e.id, area)
					if msg.begins_with("Aksi berdua!") or msg.begins_with("Bergandengan lagi.") or msg.begins_with("Berhenti bergandengan."):
						_finish([] if msg.begins_with("Berhenti") else engine.couple_action_actions(e.id), msg)
					else: status = msg)
		add_child(b)
		_choices.append(b)


## Button label and enabled state for one entry, as in the Java layout().
func _state(e: Dictionary) -> Array:
	var p := engine.p
	match tab:
		"gift":
			var has := p.has_item(e.item)
			return [has and p.last_gift_day != p.day and engine.romance_ready(), "Belum punya" if not has else ("Besok lagi" if p.last_gift_day == p.day else "Berikan")]
		"date":
			var ok := engine.date_block(e.id, area) == ""
			return [ok, "Kencan • %d" % int(e.get("cost", 0)) if ok else "Belum bisa"]
		"moment":
			var ok := engine.moment_block(e.id, area) == ""
			return [ok, "Lakukan" if ok else "Belum bisa"]
		"game":
			return [engine.romance_game_block(e.id, area) == "", "Main"]
	var ok := engine.couple_action_block(e.id, area) == ""
	return [ok, ("Lepaskan" if e.id == "gandengan" and p.holding_hands else "Lakukan") if ok else "Belum bisa"]


func _process(_dt: float) -> void:
	if not visible:
		return
	var w := minf(940, size.x - 36)
	var h := minf(628, size.y - 30)
	_panel = Rect2((size.x - w) / 2, (size.y - h) / 2, w, h)
	var o := _panel.position
	var tw := (w - 90) / 5.0
	for i in _tabs.size():
		_tabs[i].position = o + Vector2(25 + i * (tw + 10), 122); _tabs[i].size = Vector2(tw, 52)
		_set_accent(_tabs[i], TABS[i][0] == tab)
	_close.position = o + Vector2(w - 166, 24); _close.size = Vector2(141, 51)
	_prev.position = o + Vector2(32, h - 113); _prev.size = Vector2(66, 48)
	_next.position = o + Vector2(112, h - 113); _next.size = Vector2(66, 48)
	_prev.disabled = page <= 0
	_next.disabled = (page + 1) * 3 >= _items().size()
	var items := _items()
	for i in _choices.size():
		var st := _state(items[page * 3 + i])
		var b: Button = _choices[i]
		b.disabled = not st[0]; b.text = st[1]
		b.position = o + Vector2(w - 205, 196 + i * 101 + 16); b.size = Vector2(164, 55)
	queue_redraw()


var _accent_cache := {}
func _set_accent(b: Button, on: bool) -> void:
	if _accent_cache.get(b) == on:
		return
	_accent_cache[b] = on
	var fresh := UiTheme.button(b.text, 17, on)
	for s in ["normal", "hover", "pressed", "focus"]:
		b.add_theme_stylebox_override(s, fresh.get_theme_stylebox(s))
	for c in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		b.add_theme_color_override(c, fresh.get_theme_color(c))
	fresh.free()


func _unhandled_key_input(e: InputEvent) -> void:
	if visible and e.pressed and (e.keycode == KEY_ESCAPE or e.keycode == KEY_ENTER):
		close()
		get_viewport().set_input_as_handled()


func _draw() -> void:
	if engine == null:
		return
	var p := engine.p
	draw_rect(Rect2(Vector2.ZERO, size), Color(UiTheme.BG, 0.75))
	var pr := _panel
	var o := pr.position
	var w := pr.size.x
	UiTheme.panel(Color("2f2545"), Color("57476f"), 22, 3, 10).draw(get_canvas_item(), pr)
	UiTheme.draw_text(self, "Waktu Berdua ♥", o.x + 26, o.y + 20, 28, UiTheme.CREAM, "left", 0, "title")
	UiTheme.draw_text(self, "Kedekatan: %d/100   •   Koin: %d" % [p.affection, p.coins], o.x + 27, o.y + 78, 20, UiTheme.GOLD)
	var items := _items()
	for i in _choices.size():
		var e: Dictionary = items[page * 3 + i]
		var row := Rect2(o.x + 22, o.y + 196 + i * 101, w - 44, 87)
		UiTheme.panel(Color(1, 0.975, 0.965), Color("d9c6e0"), 14, 2, 0).draw(get_canvas_item(), row)
		var tx := row.position.x + 20
		var title := ""
		var desc := ""
		match tab:
			"gift":
				var it := _item(e.item)
				var t := Data.tex(str(it.get("icon", "")))
				draw_circle(row.position + Vector2(42, 43), 31, Color("f3e6ef"))
				if t:
					draw_texture_rect(t, Rect2(row.position.x + 15, row.position.y + 16, 54, 54), false)
				tx = row.position.x + 83
				title = "%s  •  +%d ♥" % [it.get("name", e.item), int(e.get("affection", 0))]
				desc = str(it.get("desc", ""))
			"date":
				title = "%s  •  %d koin  •  +%d ♥" % [e.get("title", ""), int(e.get("cost", 0)), int(e.get("affection", 0))]
				var r := engine.date_block(e.id, area)
				desc = str(e.get("desc", "")) if r == "" else r
			"moment":
				var hr: Array = e.get("hours", ["", ""])
				title = "%s  •  gratis  •  +%d ♥" % [e.get("title", ""), int(e.get("affection", 0))]
				var r := engine.moment_block(e.id, area)
				desc = ("%s-%s  •  %s" % [hr[0], hr[1] if hr.size() > 1 else "", e.get("desc", "")]) if r == "" else r
			"game":
				title = "%s  •  +%d hati/hari  •  Rekor %d" % [e.get("title", ""), int(e.get("affection", 0)), p.count("best_romgame_" + str(e.id))]
				var r := engine.romance_game_block(e.id, area)
				var detail := "Bisa main ulang; bonus kedekatan sudah diambil hari ini." if p.count("day_romgame_" + str(e.id)) == p.day else str(e.get("desc", ""))
				desc = detail if r == "" else r
			_:
				title = "%s  •  +%d ♥ / hari" % [e.get("title", ""), int(e.get("affection", 0))]
				var r := engine.couple_action_block(e.id, area)
				desc = ("Mode gandengan aktif • pilih Lepaskan" if e.id == "gandengan" and p.holding_hands else str(e.get("desc", ""))) if r == "" else r
		UiTheme.draw_text(self, title, tx, row.position.y + 14, 20, UiTheme.INK, "left", 0, "bold")
		var f := UiTheme.font("body")
		draw_multiline_string(f, Vector2(tx, row.position.y + 48 + f.get_ascent(16) * 0.82), desc, HORIZONTAL_ALIGNMENT_LEFT, row.position.x + row.size.x - 230 - tx, 16, 2, UiTheme.INK_SOFT)
	UiTheme.draw_text(self, "Halaman %d/%d" % [page + 1, maxi(1, (items.size() + 2) / 3)], o.x + 195, o.y + pr.size.y - 100, 17, UiTheme.CREAM)
	UiTheme.draw_text(self, status, o.x + 25, o.y + pr.size.y - 46, 17, UiTheme.GOLD, "left", w - 48)
