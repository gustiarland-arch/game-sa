class_name MemoryBook
extends Control
## Our Memory Book (port of MemoryBookOverlay.java): Kenangan (two sides), Tas, Bab (status and
## replay), Misi, Prestasi, Jelajah. Emits replay_requested(chapter) after the player confirms.

signal replay_requested(chapter: String)
signal closed

const PER_PAGE := 6
const TABS := ["Kenangan", "Tas", "Bab", "Misi", "Prestasi", "Jelajah"]

var p: Progress
var g: Dictionary
var replay_mode := false
var tab := 0
var page := 0
var _tabs: Array = []
var _close: Button
var _prev: Button
var _next: Button
var _replay_btns: Array = []
var _replay_chapters: Array = []
var _confirm_ch := ""
var _confirm: Control
var _confirm_text: Label
var _cells: Array = []    # [icon, title, text, state]
var _pages := 1
var _panel := Rect2()


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	visible = false
	mouse_filter = Control.MOUSE_FILTER_STOP
	for i in TABS.size():
		var b := UiTheme.button(TABS[i], 19)
		b.pressed.connect(func(): tab = i; page = 0; _rebuild())
		add_child(b)
		_tabs.append(b)
	_close = UiTheme.button("Tutup", 19)
	_close.pressed.connect(close)
	add_child(_close)
	_prev = UiTheme.button("◀", 20)
	_prev.pressed.connect(func(): page = maxi(0, page - 1))
	add_child(_prev)
	_next = UiTheme.button("▶", 20)
	_next.pressed.connect(func(): page = mini(_pages - 1, page + 1))
	add_child(_next)
	_build_confirm()


func open(progress: Progress, replay: bool) -> void:
	p = progress
	g = SaveStore.load_global()
	replay_mode = replay
	tab = 0; page = 0; _confirm_ch = ""; _confirm.visible = false
	for b in _replay_btns:
		b.queue_free()
	_replay_btns = []; _replay_chapters = []
	for ch in Data.chapter_order:
		if ch == "EPI":
			continue
		_replay_chapters.append(ch)
		var b := UiTheme.button("Main ulang", 17)
		b.pressed.connect(func(): _ask_replay(ch))
		add_child(b)
		_replay_btns.append(b)
	move_child(_confirm, -1)
	# textures must be loaded before they are first drawn
	for e in Data.memory_book.get("entries", []):
		Data.tex(str(e.get("icon", "")))
	for it in Data.memory_book.get("items", {}).values():
		Data.tex(str(it.get("icon", "")))
	Data.tex(str(Data.memory_book.get("bonus", {}).get("icon", "")))
	_rebuild()
	visible = true
	_tabs[0].grab_focus.call_deferred()


func close() -> void:
	if visible:
		visible = false
		closed.emit()


func _chapter_now() -> String:
	return str(Data.step(p.step).get("chapter", "PRO")) if not Data.step(p.step).is_empty() else "PRO"


func _route_has_flag(route: String, flag: String) -> bool:
	return g.get("routeFlags", {}).get(route, []).has(flag)


func _both_completed(ch: String) -> bool:
	var c: Dictionary = g.get("completed", {})
	return c.get("arland", []).has(ch) and c.get("sofia", []).has(ch)


## Entry state as in MemoryBookDb.state: "UNLOCKED", "OTHER_SIDE" or "LOCKED".
func entry_state(e: Dictionary) -> String:
	var r := str(e.get("route", "shared"))
	if r == "shared" or r == p.route:
		return "UNLOCKED" if p.has_flag(str(e.get("unlock", ""))) else "LOCKED"
	if r == Routes.partner(p.route) and _route_has_flag(r, str(e.get("unlock", ""))):
		return "OTHER_SIDE"
	return "LOCKED"


func _rebuild() -> void:
	_cells = []
	var mb := Data.memory_book
	if tab == 0:
		var bonus := _both_completed("C06")
		var b: Dictionary = mb.get("bonus", {})
		_cells.append([b.get("icon") if bonus else null, b.get("title", "Bonus") if bonus else "Bonus: Kenangan Dua Sisi",
			b.get("text", "") if bonus else "Tamatkan cerita di route Arland dan Sofia untuk membuka halaman ini.", 2 if bonus else 0])
		var mine := []
		var others := []
		for e in mb.get("entries", []):
			var r := str(e.get("route", "shared"))
			(mine if r == "shared" or r == p.route else others).append(e)
		for e in mine + others:
			var st := entry_state(e)
			var r := str(e.get("route", "shared"))
			if r != "shared" and r != p.route and st == "LOCKED":
				_cells.append([null, "Sisi lain (%s)" % Routes.display(r), "Mainkan route %s untuk melihat kenangan ini." % Routes.display(r), 0])
			elif st == "LOCKED":
				_cells.append([null, "◇ Belum ditemukan", "Bab " + Data.chapter_title(str(e.get("chapter", ""))), 0])
			else:
				var other := st == "OTHER_SIDE"
				_cells.append([e.get("icon"), str(e.get("title", "")) + ("  (sisi %s)" % Routes.display(r) if other else ""), str(e.get("text", "")), 1 if other else 2])
	elif tab == 1:
		if p.items.is_empty():
			_cells.append([null, "Tas masih kosong", "Item yang kamu temukan akan muncul di sini.", 0])
		for id in p.items:
			var it: Dictionary = mb.get("items", {}).get(id, {})
			if not it.is_empty():
				_cells.append([it.get("icon"), str(it.get("name", id)), str(it.get("desc", "")), 2])
	elif tab == 3:
		var now := Data.chapter_index(_chapter_now())
		for q in Data.quests.get("sideQuests", []):
			if q.get("route") != null and q.get("route") != p.route:
				continue
			var title := str(q.get("title", ""))
			if p.has_flag(str(q.get("doneFlag", ""))):
				_cells.append([null, "✓ " + title, str(q.get("desc", "")), 2])
			elif p.has_flag(str(q.get("startFlag", ""))):
				_cells.append([null, "♪ %s (aktif)" % title, str(q.get("desc", "")), 1])
			else:
				var avail := now >= Data.chapter_index(str(q.get("chapter", "")))
				_cells.append([null, "◇ Misi tersedia di kota" if avail else "◇ Belum tersedia",
					"Ajak bicara penduduk kota atau lihat papan pengumuman." if avail else "Lanjutkan cerita untuk membuka.", 0])
	elif tab == 4:
		var have: Array = g.get("achievements", [])
		for d in Achievements.ALL:
			var got := have.has(d[0])
			_cells.append([null, ("✓ " if got else "◇ ") + d[1], ("Terbuka • " + d[2]) if got else d[2], 2 if got else 0])
	elif tab == 5:
		for id in Data.maps:
			var place: Dictionary = Data.maps[id]
			var found: bool = p.visited_areas.has(id) or p.area == id
			var secret := {}
			for d in Data.quests.get("worldDiscoveries", []):
				if d.get("area") == id:
					secret = d
					break
			var secret_found := not secret.is_empty() and p.has_flag(str(secret.get("flag", "")))
			var has_view: bool = not place.get("elevationPlatforms", []).is_empty()
			var view_done: bool = has_view and p.has_flag("V50_VIEW_%s_DONE" % id.to_upper())
			var status := "Belum ada jejak tambahan." if secret.is_empty() else ("Jejak terungkap: " + str(secret.get("title", "")) if secret_found else "Jejak belum ditemukan — cari penanda bintang di area ini.")
			var vertical := (" • Panorama terbuka" if view_done else " • Cari tangga ke pelataran") if has_view else ""
			_cells.append([null, ("✓ " + str(place.get("name", id))) if found else "◇ Belum ditemukan",
				(status + vertical) if found else "Jelajahi kota dan ikuti cerita untuk menemukannya.",
				2 if (secret_found or view_done) else (1 if found else 0)])
	_pages = maxi(1, (_cells.size() + PER_PAGE - 1) / PER_PAGE)
	page = mini(page, _pages - 1)


func _subtitle() -> String:
	if tab == 5:
		var disc := 0
		for d in Data.quests.get("worldDiscoveries", []):
			if p.has_flag(str(d.get("flag", ""))):
				disc += 1
		return "%s • Jelajah %d/%d • Jejak %d/%d" % [Routes.display(p.route), p.visited_areas.size(), Data.maps.size(), disc, Data.quests.get("worldDiscoveries", []).size()]
	return "%s Route%s • %d/%d prestasi" % [Routes.display(p.route), " • REPLAY" if replay_mode else "", g.get("achievements", []).size(), Achievements.ALL.size()]


func _ask_replay(ch: String) -> void:
	if p.replay_from(ch) == null:
		return
	_confirm_ch = ch
	_confirm_text.text = "Memainkan ulang %s. Progres utama tetap aman dan tidak berubah." % Data.chapter_title(ch)
	_confirm.visible = true


func _build_confirm() -> void:
	_confirm = Control.new()
	_confirm.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_confirm.visible = false
	add_child(_confirm)
	var dim := ColorRect.new(); dim.color = Color(UiTheme.BG, 0.55); dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_confirm.add_child(dim)
	var center := CenterContainer.new(); center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_confirm.add_child(center)
	var pc := PanelContainer.new()
	var st := UiTheme.panel()
	st.content_margin_left = 30; st.content_margin_right = 30; st.content_margin_top = 24; st.content_margin_bottom = 24
	pc.add_theme_stylebox_override("panel", st)
	center.add_child(pc)
	var v := VBoxContainer.new(); v.add_theme_constant_override("separation", 14)
	pc.add_child(v)
	v.add_child(UiTheme.label("Main ulang?", 28, UiTheme.INK, "title"))
	var t := UiTheme.label("", 19, UiTheme.INK_SOFT)
	_confirm_text = t
	t.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	t.custom_minimum_size = Vector2(480, 0)
	v.add_child(t)
	var row := HBoxContainer.new(); row.alignment = BoxContainer.ALIGNMENT_END; row.add_theme_constant_override("separation", 12)
	v.add_child(row)
	var no := UiTheme.button("Batal", 20)
	no.pressed.connect(func(): _confirm.visible = false)
	row.add_child(no)
	var yes := UiTheme.button("Main ulang", 20, true)
	yes.pressed.connect(func():
		_confirm.visible = false
		var ch := _confirm_ch
		visible = false
		replay_requested.emit(ch))
	row.add_child(yes)


func _process(_dt: float) -> void:
	if not visible:
		return
	var w := minf(1080, size.x - 60)
	var h := minf(640, size.y - 40)
	_panel = Rect2((size.x - w) / 2, (size.y - h) / 2, w, h)
	var o := _panel.position
	var tw := minf(126, (w - 245) / 6.0 - 9)
	for i in _tabs.size():
		_tabs[i].position = o + Vector2(20 + i * (tw + 8), 62); _tabs[i].size = Vector2(tw, 50)
		_set_accent(_tabs[i], tab == i)
	_close.position = o + Vector2(w - 152, 62); _close.size = Vector2(128, 50)
	_prev.position = o + Vector2(w - 250, h - 70); _prev.size = Vector2(90, 50)
	_next.position = o + Vector2(w - 130, h - 70); _next.size = Vector2(90, 50)
	_prev.visible = tab != 2 and _pages > 1; _next.visible = _prev.visible
	_prev.disabled = page <= 0; _next.disabled = page >= _pages - 1
	var col_w := (w - 60) / 2.0
	for i in _replay_btns.size():
		var b: Button = _replay_btns[i]
		var ch: String = _replay_chapters[i]
		b.visible = tab == 2 and p.chapters.has(ch) and not replay_mode and p.snapshots.has(ch)
		b.position = o + Vector2(30 + (i / 4) * col_w + col_w - 220, 152 + (i % 4) * 104); b.size = Vector2(196, 50)
	queue_redraw()


var _accent_cache := {}
func _set_accent(b: Button, on: bool) -> void:
	if _accent_cache.get(b) == on:
		return
	_accent_cache[b] = on
	var fresh := UiTheme.button(b.text, 19, on)
	for s in ["normal", "hover", "pressed", "focus"]:
		b.add_theme_stylebox_override(s, fresh.get_theme_stylebox(s))
	for c in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		b.add_theme_color_override(c, fresh.get_theme_color(c))
	fresh.free()


func _unhandled_key_input(e: InputEvent) -> void:
	if visible and e.pressed and (e.keycode == KEY_ESCAPE or e.keycode == KEY_M):
		if _confirm.visible:
			_confirm.visible = false
		else:
			close()
		get_viewport().set_input_as_handled()


func _draw() -> void:
	if p == null:
		return
	draw_rect(Rect2(Vector2.ZERO, size), Color(UiTheme.BG, 0.6))
	var pr := _panel
	var o := pr.position
	UiTheme.panel().draw(get_canvas_item(), pr)
	UiTheme.draw_text(self, "Our Memory Book", o.x + 30, o.y + 16, 28, UiTheme.INK, "left", 0, "title")
	UiTheme.draw_text(self, _subtitle(), o.x + pr.size.x - 540, o.y + 24, 17, UiTheme.INK_SOFT, "right", 510)
	var left := o.x + 30
	var top := o.y + 128
	if tab == 2:
		_draw_chapters(left, top)
		return
	var cw := (pr.size.x - 80) / 2.0
	var chh := 112.0
	for i in range(page * PER_PAGE, mini(_cells.size(), (page + 1) * PER_PAGE)):
		var k := i - page * PER_PAGE
		var c: Array = _cells[i]
		_entry(Rect2(left + (k % 2) * (cw + 20), top + (k / 2) * (chh + 12), cw, chh), c[0], c[1], c[2], c[3])
	if _pages > 1:
		UiTheme.draw_text(self, "Hal. %d/%d" % [page + 1, _pages], o.x + 30, o.y + pr.size.y - 56, 19, UiTheme.INK_SOFT)


## state 0 = locked, 1 = other side, 2 = open.
func _entry(r: Rect2, icon, title: String, text: String, state: int) -> void:
	var bg := Color(0.92, 0.9, 0.93) if state == 0 else (Color(1, 0.94, 1) if state == 1 else Color(1, 0.97, 1))
	draw_rect(r, bg)
	draw_rect(Rect2(r.position, Vector2(6, r.size.y)), UiTheme.PINK if state == 2 else (UiTheme.LAVENDER if state == 1 else UiTheme.INK_SOFT))
	var tx := r.position.x + 20
	var t: Texture2D = Data.tex(str(icon)) if icon != null and str(icon) != "" else null
	if t:
		draw_texture_rect(t, Rect2(r.position.x + 18, r.position.y + (r.size.y - 64) / 2, 64, 64), false)
		tx = r.position.x + 96
	var tw := r.position.x + r.size.x - tx - 14
	UiTheme.draw_text(self, title, tx, r.position.y + 12, 20, UiTheme.INK_SOFT if state == 0 else UiTheme.INK, "left", 0, "bold")
	var f := UiTheme.font("body")
	draw_multiline_string(f, Vector2(tx, r.position.y + 46 + f.get_ascent(16) * 0.82), text, HORIZONTAL_ALIGNMENT_LEFT, tw, 16, 3, UiTheme.INK_SOFT)


func _draw_chapters(left: float, top: float) -> void:
	var col_w := (_panel.size.x - 60) / 2.0
	var now := _chapter_now()
	for i in _replay_chapters.size():
		var ch: String = _replay_chapters[i]
		var r := Rect2(left + (i / 4) * col_w, top + (i % 4) * 104, col_w - 12, 94)
		var done := p.chapters.has(ch)
		var playing := now == ch and not done
		draw_rect(r, Color(1, 0.97, 1))
		draw_rect(Rect2(r.position, Vector2(6, r.size.y)), UiTheme.PINK if done else (UiTheme.LAVENDER if playing else UiTheme.INK_SOFT))
		var has_btn: bool = _replay_btns[i].visible
		UiTheme.draw_text(self, Data.chapter_title(ch), r.position.x + 18, r.position.y + 12, 17, UiTheme.INK, "left", col_w - (250 if has_btn else 50), "bold")
		UiTheme.draw_text(self, "✓ Tamat" if done else ("Sedang dimainkan" if playing else "Belum dibuka"), r.position.x + 18, r.position.y + 64, 16, UiTheme.PINK_DEEP if done else UiTheme.INK_SOFT)
	UiTheme.draw_text(self, "Main ulang memakai salinan progres di awal chapter: progres utama dan save-mu tidak berubah.",
		left, _panel.position.y + _panel.size.y - 58, 16, UiTheme.INK_SOFT, "left", _panel.size.x - 300)
