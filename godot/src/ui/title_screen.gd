class_name TitleScreen
extends Control
## Title -> route choice -> save slot (port of TitleScreen/RouteSelectScreen/SlotScreen).
## Emits start_game(progress, is_new).

signal start_game(progress: Progress, is_new: bool)

var _far: TextureRect
var _near: TextureRect
var _page: Control
var _t := 0.0


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new(); bg.color = Color(0.953, 0.725, 0.702); bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)  # shows through the translucent moon of the far layer
	add_child(bg)
	_far = _layer("ui/v32_menu_far.png")
	_near = _layer("ui/v32_menu_near.png")
	_page = Control.new(); _page.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_page)
	Audio.music("title")
	show_title()


func _layer(path: String) -> TextureRect:
	var r := TextureRect.new()
	r.texture = Data.tex(path)
	r.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	r.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	r.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	r.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(r)
	return r


func _process(delta: float) -> void:
	_t += delta
	_far.position.x = sin(_t * 0.05) * 10.0 - 10.0
	_near.position.x = sin(_t * 0.05) * 22.0 - 22.0
	_far.size = size + Vector2(20, 0)
	_near.size = size + Vector2(44, 0)


func _clear() -> VBoxContainer:
	for c in _page.get_children():
		c.queue_free()
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_page.add_child(center)
	var box := VBoxContainer.new()
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_theme_constant_override("separation", 16)
	center.add_child(box)
	return box


func show_title() -> void:
	var box := _clear()
	var banner := TextureRect.new()
	banner.texture = Data.tex("ui/title_banner.png")
	banner.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	banner.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	banner.custom_minimum_size = Vector2(660, 219)
	banner.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	box.add_child(banner)
	var gap := Control.new(); gap.custom_minimum_size = Vector2(0, 12); box.add_child(gap)
	var play := UiTheme.button("Mulai Cerita", 26, true)
	play.custom_minimum_size = Vector2(340, 64)
	play.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	play.pressed.connect(show_routes)
	box.add_child(play)
	var g := SaveStore.load_global()
	if g.get("lastRoute") != null and int(g.get("lastSlot", 0)) > 0:
		var r: String = g.lastRoute
		var s := int(g.lastSlot)
		var ld := SaveStore.load_slot(r, s)
		if ld.value != null:
			var cont := UiTheme.button("Lanjutkan  ·  %s, slot %d" % [Routes.display(r), s], 22)
			cont.custom_minimum_size = Vector2(340, 56)
			cont.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
			cont.pressed.connect(func(): start_game.emit(ld.value, false))
			box.add_child(cont)
	play.grab_focus.call_deferred()
	var ver := UiTheme.label("Versi Godot · pratinjau", 15, Color(UiTheme.CREAM, 0.6), "body")
	ver.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(ver)


func show_routes() -> void:
	var box := _clear()
	var head := UiTheme.label("Pilih sudut pandang", 38, UiTheme.CREAM, "title")
	head.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	head.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.5))
	head.add_theme_constant_override("shadow_offset_y", 3)
	box.add_child(head)
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 48)
	box.add_child(row)
	for r in [Routes.ARLAND, Routes.SOFIA]:
		var col := VBoxContainer.new()
		col.add_theme_constant_override("separation", 12)
		var card := TextureButton.new()
		card.texture_normal = Data.tex("ui/card_%s.png" % r)
		card.ignore_texture_size = true
		card.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT_CENTERED
		card.custom_minimum_size = Vector2(189, 300)
		card.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		card.pressed.connect(show_slots.bind(r))
		col.add_child(card)
		var b := UiTheme.button("Route " + Routes.display(r), 22, r == Routes.SOFIA)
		b.custom_minimum_size = Vector2(220, 54)
		b.pressed.connect(show_slots.bind(r))
		col.add_child(b)
		row.add_child(col)
	var back := UiTheme.button("Kembali", 18)
	back.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	back.pressed.connect(show_title)
	box.add_child(back)


func show_slots(route: String) -> void:
	var box := _clear()
	var head := UiTheme.label("Route %s  ·  pilih slot" % Routes.display(route), 34, UiTheme.CREAM, "title")
	head.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	head.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.5))
	head.add_theme_constant_override("shadow_offset_y", 3)
	box.add_child(head)
	for s in range(1, SaveStore.SLOTS + 1):
		var ld := SaveStore.load_slot(route, s)
		var panel := PanelContainer.new()
		var st := UiTheme.panel(Color(1, 0.975, 0.965, 0.95))
		st.content_margin_left = 22; st.content_margin_right = 22; st.content_margin_top = 14; st.content_margin_bottom = 14
		panel.add_theme_stylebox_override("panel", st)
		panel.custom_minimum_size = Vector2(640, 0)
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 16)
		panel.add_child(row)
		var info := VBoxContainer.new()
		info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(info)
		info.add_child(UiTheme.label("Slot %d" % s, 24, UiTheme.INK, "bold"))
		var p: Progress = ld.value
		var desc := "Kosong"
		if p != null:
			var ch := Data.chapter_title(Data.step(p.step).get("chapter", ""))
			desc = "%s  ·  Hari %d, %s  ·  %d menit bermain" % [ch, p.day, WorldClock.hhmm(p.minute), int(p.play_seconds / 60)]
			if ld.status == "RECOVERED":
				desc += "  ·  dipulihkan dari cadangan"
		elif ld.status == "CORRUPT":
			desc = "Save rusak: " + str(ld.error)
		elif ld.status == "INCOMPATIBLE":
			desc = str(ld.error)
		info.add_child(UiTheme.label(desc, 17, UiTheme.INK_SOFT, "body"))
		if p != null:
			var go := UiTheme.button("Lanjutkan", 20, true)
			go.pressed.connect(func(): start_game.emit(p, false))
			row.add_child(go)
			var del := UiTheme.button("Hapus", 18)
			del.pressed.connect(func():
				SaveStore.delete_slot(route, s)
				show_slots(route))
			row.add_child(del)
		elif ld.status != "INCOMPATIBLE":
			var nw := UiTheme.button("Cerita Baru", 20, true)
			nw.pressed.connect(func():
				start_game.emit(Progress.new_game(route, s, Data.first_step, Data.area(Routes.room(route))), true))
			row.add_child(nw)
		box.add_child(panel)
	var back := UiTheme.button("Kembali", 18)
	back.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	back.pressed.connect(show_routes)
	box.add_child(back)
