class_name DialogBox
extends Control
## Dialogue box with expression portraits, typewriter text, skip, history hook and choices
## (port of game/DialogBox.java, redrawn as a crisp HD panel).

signal line_shown(line: Dictionary)
signal choice_made(choice: Dictionary)

var chars_per_second := 60.0
var route := "sofia"
var active := false

var _queue: Array = []
var _choices: Array = []
var _done: Callable
var _line: Dictionary = {}
var _shown := 0.0
var _appear := 0.0
var _blink := 0.0

var _panel: Panel
var _portrait_frame: Panel
var _portrait: TextureRect
var _name_tag: Panel
var _name: Label
var _text: RichTextLabel
var _arrow: Label
var _progress_bg: ColorRect
var _progress: ColorRect
var _skip: Button
var _choice_layer: Control
var _choice_box: VBoxContainer
var _dim: ColorRect


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	visible = false
	_dim = ColorRect.new(); _dim.color = Color(UiTheme.BG, 0.0); _dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_dim)
	_panel = Panel.new()
	_panel.add_theme_stylebox_override("panel", UiTheme.panel(Color(1, 0.975, 0.965, 0.97)))
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_panel)
	_portrait_frame = Panel.new()
	_portrait_frame.add_theme_stylebox_override("panel", UiTheme.panel(Color("efe3f1"), Color("d9c6e0"), 14, 2, 0))
	_portrait_frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.add_child(_portrait_frame)
	_portrait = TextureRect.new()
	_portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_portrait.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	_portrait_frame.add_child(_portrait)
	_name_tag = Panel.new()
	_name_tag.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.add_child(_name_tag)
	_name = UiTheme.label("", 24, Color.WHITE, "bold")
	_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_name.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_name_tag.add_child(_name)
	_text = RichTextLabel.new()
	_text.bbcode_enabled = false
	_text.scroll_active = false
	_text.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_text.add_theme_font_override("normal_font", UiTheme.font("body"))
	_text.add_theme_font_size_override("normal_font_size", 25)
	_text.add_theme_color_override("default_color", UiTheme.INK)
	_text.add_theme_constant_override("line_separation", 6)
	_panel.add_child(_text)
	_arrow = UiTheme.label("▼", 20, UiTheme.PINK_DEEP, "bold")
	_panel.add_child(_arrow)
	_progress_bg = ColorRect.new(); _progress_bg.color = Color(UiTheme.LAVENDER, 0.22); _panel.add_child(_progress_bg)
	_progress = ColorRect.new(); _progress.color = Color(UiTheme.PINK_DEEP, 0.85); _panel.add_child(_progress)
	_skip = UiTheme.button("Lewati  ▶", 18)
	_skip.pressed.connect(skip_all)
	add_child(_skip)
	_choice_layer = Control.new(); _choice_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT); _choice_layer.visible = false
	add_child(_choice_layer)
	var head := UiTheme.label("Pilihanmu menentukan momen berikutnya", 26, UiTheme.CREAM, "title")
	head.name = "Head"
	head.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	head.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.45))
	head.add_theme_constant_override("shadow_offset_y", 2)
	_choice_layer.add_child(head)
	_choice_box = VBoxContainer.new()
	_choice_box.add_theme_constant_override("separation", 14)
	_choice_layer.add_child(_choice_box)
	resized.connect(_layout)


func start(lines: Array, choices, r: String, done: Callable = Callable()) -> void:
	_queue = lines.duplicate()
	_choices = (choices if choices is Array else []).duplicate()
	route = r
	_done = done
	active = true
	visible = true
	_choice_layer.visible = false
	_next()


func _next() -> void:
	_line = _queue.pop_front() if not _queue.is_empty() else {}
	_shown = 0.0
	_appear = 0.0
	if not _line.is_empty():
		_show_line()
		line_shown.emit(_line)
		return
	if not _choices.is_empty():
		_build_choices()
		return
	_finish()


func _finish() -> void:
	active = false
	visible = false
	_line = {}
	var d := _done
	_done = Callable()
	if d.is_valid():
		d.call()


func _show_line() -> void:
	_panel.visible = true
	_skip.visible = true
	var spk := str(_line.get("s", "narrator"))
	var sp := Data.speaker(spk)
	var portrait = sp.get("portrait")
	var narrator: bool = portrait == null and sp.get("style", "") != "npc"
	_portrait_frame.visible = portrait != null
	if portrait != null:
		_portrait.texture = Data.portrait(portrait, str(_line.get("e", "neutral")))
	var tag := UiTheme.INK_SOFT if narrator else (UiTheme.NPC_TAG if sp.get("style", "") == "npc" else (UiTheme.PINK_DEEP if spk.begins_with("sofia") else UiTheme.LAVENDER))
	var st := UiTheme.panel(tag, tag.darkened(0.15), 12, 2, 4)
	_name_tag.add_theme_stylebox_override("panel", st)
	_name.text = sp.get("name", spk)
	var t := str(_line.get("t", ""))
	if sp.get("style", "") == "message":
		t = "✉  " + t
	_text.text = t
	_text.visible_characters = 0
	_text.add_theme_color_override("default_color", UiTheme.INK_SOFT if narrator else UiTheme.INK)
	_layout()


func _build_choices() -> void:
	_panel.visible = false
	_skip.visible = false
	for c in _choice_box.get_children():
		c.queue_free()
	var i := 0
	for c in _choices:
		i += 1
		var b := UiTheme.button("%d.   %s" % [i, c.get("text", "")], 24)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.custom_minimum_size = Vector2(0, 64)
		b.pressed.connect(_pick.bind(c))
		_choice_box.add_child(b)
	_choice_layer.visible = true
	_layout()
	if _choice_box.get_child_count() > 0:
		(_choice_box.get_child(0) as Button).grab_focus.call_deferred()


func _pick(c: Dictionary) -> void:
	_choices = []
	_choice_layer.visible = false
	choice_made.emit(c)
	var resp = c.get("byRoute", {}).get(route, [])
	_queue.append_array(resp if resp is Array else [])
	_next()


func choosing() -> bool:
	return active and _choice_layer.visible


func choose(index: int) -> void:
	if choosing() and index >= 0 and index < _choice_box.get_child_count():
		(_choice_box.get_child(index) as Button).pressed.emit()


func skip_all() -> void:
	_queue.clear()
	_line = {}
	if not _choices.is_empty():
		_build_choices()
	else:
		_finish()


func _revealed() -> bool:
	return _line.is_empty() or _shown >= _text.get_total_character_count()


## Tap / action key: reveal the whole line first, then continue.
func advance() -> void:
	if not active or _line.is_empty():
		return
	if not _revealed():
		_shown = _text.get_total_character_count()
		return
	_next()


func _process(delta: float) -> void:
	if not active:
		return
	_blink += delta
	if choosing():
		_dim.color.a = lerpf(_dim.color.a, 0.53, 1.0 - exp(-delta * 10.0))
		return
	_dim.color.a = lerpf(_dim.color.a, 0.0, 1.0 - exp(-delta * 10.0))
	if _line.is_empty():
		return
	_shown += delta * chars_per_second
	_appear = minf(1.0, _appear + delta * 6.0)
	var total := _text.get_total_character_count()
	_text.visible_characters = mini(total, int(_shown))
	_panel.modulate.a = _appear
	_panel.position.y = _box_y() + (1.0 - _appear) * 20.0
	var prog := 1.0 if total == 0 else minf(1.0, _shown / total)
	_progress.size.x = _progress_bg.size.x * prog
	_arrow.visible = _revealed() and int(_blink * 2.5) % 2 == 0
	if _portrait_frame.visible:
		_portrait.position.y = 8 + sin(_blink * 1.7) * 1.5


func _box_y() -> float:
	return size.y - _box_h() - 18.0


func _box_h() -> float:
	return clampf(size.y * 0.27, 168.0, 230.0)


func _layout() -> void:
	if not is_inside_tree():
		return
	var w := minf(size.x - 48.0, 1180.0)
	var h := _box_h()
	_panel.size = Vector2(w, h)
	_panel.position = Vector2((size.x - w) / 2.0, _box_y())
	var tx := 32.0
	if _portrait_frame.visible:
		var ph := h - 28.0
		var pw := ph * 0.9
		_portrait_frame.position = Vector2(14, 14)
		_portrait_frame.size = Vector2(pw, ph)
		_portrait.position = Vector2(4, 8)
		_portrait.size = Vector2(pw - 8, ph - 12)
		tx = 14 + pw + 26
	var nw := maxf(170.0, UiTheme.font("bold").get_string_size(_name.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 24).x + 44)
	_name_tag.position = Vector2(tx - 6, -22)
	_name_tag.size = Vector2(nw, 44)
	_name.position = Vector2.ZERO
	_name.size = _name_tag.size
	_text.position = Vector2(tx, 34)
	_text.size = Vector2(w - tx - 40, h - 70)
	_progress_bg.position = Vector2(tx, h - 22); _progress_bg.size = Vector2(w - tx - 70, 4)
	_progress.position = _progress_bg.position; _progress.size.y = 4
	_arrow.position = Vector2(w - 44, h - 44)
	_skip.size = Vector2(0, 0)
	_skip.position = Vector2(_panel.position.x + w - 150, _panel.position.y - 58)
	var cw := minf(size.x - 80, 820.0)
	_choice_box.size = Vector2(cw, 0)
	_choice_box.position = Vector2((size.x - cw) / 2.0, size.y * 0.36)
	var head: Label = _choice_layer.get_node("Head")
	head.size = Vector2(size.x, 40)
	head.position = Vector2(0, size.y * 0.36 - 60)


func _gui_input(event: InputEvent) -> void:
	if not active or choosing():
		return
	if (event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT) or (event is InputEventScreenTouch and event.pressed):
		advance()
		accept_event()


func _unhandled_input(event: InputEvent) -> void:
	if not active:
		return
	if event.is_action_pressed("ui_accept") and not choosing():
		advance()
		get_viewport().set_input_as_handled()
	elif choosing() and event is InputEventKey and event.pressed and event.keycode >= KEY_1 and event.keycode <= KEY_9:
		choose(event.keycode - KEY_1)
		get_viewport().set_input_as_handled()
