class_name TouchControls
extends Control
## Floating joystick (left half of the screen), action button and sprint button (port of TouchControls.java).
## Mouse drags work too, so it can be tested on desktop.

signal action_pressed
signal pause_pressed
signal book_pressed

var vec := Vector2.ZERO
var sprint := false
var enabled := true

var _base: TextureRect
var _knob: TextureRect
var _act: TextureButton
var _run: TextureButton
var _pause: Button
var _book: Button
var _origin := Vector2.ZERO
var _finger := -2           # -2 none, -1 mouse, >=0 touch index
const RADIUS := 78.0


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_PASS
	_base = _img("ui/joy_base.png", 168)
	_knob = _img("ui/joy_knob.png", 74)
	_act = _btn("ui/btn_action.png", 112)
	_act.pressed.connect(func(): action_pressed.emit())
	_run = _btn("ui/btn_round.png", 84)
	_run.toggle_mode = true
	_run.texture_pressed = Data.tex("ui/btn_round_on.png")
	_run.toggled.connect(func(on): sprint = on)
	var run_l := UiTheme.label("Lari", 17, UiTheme.INK, "bold")
	run_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	run_l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	run_l.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	run_l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_run.add_child(run_l)
	_pause = UiTheme.button("II", 20)
	_pause.custom_minimum_size = Vector2(56, 52)
	_pause.pressed.connect(func(): pause_pressed.emit())
	add_child(_pause)
	_book = UiTheme.button("Buku", 18)
	_book.custom_minimum_size = Vector2(72, 52)
	_book.pressed.connect(func(): book_pressed.emit())
	add_child(_book)
	resized.connect(_layout)
	_layout()


func _img(path: String, s: float) -> TextureRect:
	var t := TextureRect.new()
	t.texture = Data.tex(path)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.size = Vector2(s, s)
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	t.modulate.a = 0.55
	t.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	add_child(t)
	return t


func _btn(path: String, s: float) -> TextureButton:
	var b := TextureButton.new()
	b.texture_normal = Data.tex(path)
	b.ignore_texture_size = true
	b.stretch_mode = TextureButton.STRETCH_SCALE
	b.size = Vector2(s, s)
	b.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	b.modulate.a = 0.85
	add_child(b)
	return b


func _rest() -> Vector2:
	return Vector2(130, size.y - 130)


func _layout() -> void:
	_act.position = Vector2(size.x - 150, size.y - 160)
	_run.position = Vector2(size.x - 240, size.y - 104)
	_pause.position = Vector2(size.x - 74, 16)
	_book.position = Vector2(size.x - 156, 16)
	if _finger == -2:
		_place(_rest(), Vector2.ZERO)


func _place(origin: Vector2, offset: Vector2) -> void:
	_base.position = origin - _base.size / 2
	_knob.position = origin + offset - _knob.size / 2


func _input(event: InputEvent) -> void:
	if not enabled or not visible:
		return
	var pos := Vector2.ZERO
	var idx := -3
	var pressed := false
	var moved := false
	if event is InputEventScreenTouch:
		pos = event.position; idx = event.index; pressed = event.pressed
	elif event is InputEventScreenDrag:
		pos = event.position; idx = event.index; moved = true
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and not DisplayServer.is_touchscreen_available():
		pos = event.position; idx = -1; pressed = event.pressed
	elif event is InputEventMouseMotion and _finger == -1:
		pos = event.position; idx = -1; moved = true
	else:
		return
	if moved:
		if idx == _finger:
			_drag(pos)
		return
	if pressed and _finger == -2 and pos.x < size.x * 0.45 and pos.y > size.y * 0.25:
		_finger = idx
		_origin = pos
		_base.modulate.a = 0.8; _knob.modulate.a = 0.95
		_drag(pos)
		get_viewport().set_input_as_handled()
	elif not pressed and idx == _finger:
		_finger = -2
		vec = Vector2.ZERO
		_base.modulate.a = 0.55; _knob.modulate.a = 0.55
		_place(_rest(), Vector2.ZERO)


func _drag(pos: Vector2) -> void:
	var off := (pos - _origin).limit_length(RADIUS)
	vec = off / RADIUS
	if vec.length() < 0.18:
		vec = Vector2.ZERO
	_place(_origin, off)


func reset() -> void:
	_finger = -2
	vec = Vector2.ZERO
	_place(_rest(), Vector2.ZERO)
