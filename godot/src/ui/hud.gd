class_name Hud
extends Control
## Top bar: objective (left) and day, time, weather, coins and closeness (right).

var _objective: Label
var _obj_panel: PanelContainer
var _clock: Label
var _coins: Label
var _hearts: Label
var _right: PanelContainer
var _flash := 0.0

const WEATHER_ICON := {"cerah": "☀", "berawan": "☁", "hujan": "☂", "berangin": "≋"}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_obj_panel = _pill()
	_obj_panel.position = Vector2(18, 16)
	_objective = UiTheme.label("", 19, UiTheme.INK, "bold")
	_obj_panel.add_child(_objective)
	_right = _pill()
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	_right.add_child(row)
	_clock = UiTheme.label("", 18, UiTheme.INK, "bold")
	row.add_child(_clock)
	row.add_child(_sep())
	row.add_child(_icon("ui/icon_coin.png"))
	_coins = UiTheme.label("", 18, UiTheme.INK, "bold")
	row.add_child(_coins)
	row.add_child(_icon("ui/icon_heart.png"))
	_hearts = UiTheme.label("", 18, UiTheme.INK, "bold")
	row.add_child(_hearts)


func _pill() -> PanelContainer:
	var p := PanelContainer.new()
	var st := UiTheme.panel(Color(1, 0.97, 0.96, 0.92), Color("d9c6e0"), 14, 2, 8)
	st.content_margin_left = 16; st.content_margin_right = 18; st.content_margin_top = 8; st.content_margin_bottom = 9
	p.add_theme_stylebox_override("panel", st)
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(p)
	return p


func _icon(path: String) -> TextureRect:
	var t := TextureRect.new()
	t.texture = Data.tex(path)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.custom_minimum_size = Vector2(22, 22)
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	return t


func _sep() -> ColorRect:
	var c := ColorRect.new()
	c.color = Color(UiTheme.LAVENDER, 0.4)
	c.custom_minimum_size = Vector2(2, 20)
	return c


func flash_objective() -> void:
	_flash = 1.6


func refresh(engine: QuestEngine, hidden: bool) -> void:
	visible = not hidden
	var p := engine.p
	_objective.text = "✦  " + engine.objective_text()
	_clock.text = "%s %d  ·  %s  %s" % [WorldClock.day_name(p.day), p.day, WorldClock.hhmm(p.minute), WEATHER_ICON.get(engine.weather_now(), "")]
	_coins.text = str(p.coins)
	_hearts.text = str(p.affection)
	_right.reset_size()
	_right.position = Vector2(size.x - _right.size.x - 172, 16)


func _process(delta: float) -> void:
	if _flash > 0:
		_flash -= delta
		var k := clampf(_flash, 0, 1)
		_obj_panel.scale = Vector2.ONE * (1.0 + 0.05 * sin(k * PI))
		_objective.add_theme_color_override("font_color", UiTheme.INK.lerp(UiTheme.PINK_DEEP, k))
