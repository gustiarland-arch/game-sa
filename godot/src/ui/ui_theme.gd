class_name UiTheme
extends RefCounted
## Shared colours, fonts and panel styles for the HD interface (same palette as the LibGDX Ui class).

const INK := Color("3b3049")
const INK_SOFT := Color("6a5a80")
const CREAM := Color("fbf3ee")
const PINK := Color("e89cb4")
const PINK_DEEP := Color("c4567e")
const LAVENDER := Color("9b8ab8")
const GOLD := Color("ffd678")
const BG := Color("2c2240")
const NPC_TAG := Color(0.36, 0.58, 0.5)

static var _fonts := {}


static func font(kind := "body") -> Font:
	if _fonts.has(kind):
		return _fonts[kind]
	var path: String = {"body": "res://fonts/Inter-Medium.otf", "bold": "res://fonts/Inter-Bold.otf",
			"title": "res://fonts/InterDisplay-Bold.otf"}.get(kind, "res://fonts/Inter-Medium.otf")
	var f: Font = load(path)
	_fonts[kind] = f
	return f


static func panel(bg := CREAM, border := Color(0.84, 0.74, 0.86), radius := 18, border_w := 3, shadow := 14) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = border
	s.set_border_width_all(border_w)
	s.set_corner_radius_all(radius)
	s.shadow_color = Color(0.1, 0.05, 0.15, 0.35)
	s.shadow_size = shadow
	s.shadow_offset = Vector2(0, 5)
	s.anti_aliasing = true
	return s


static func label(text: String, size: int, color: Color, kind := "body") -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font(kind))
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	return l


static func button(text: String, size := 22, accent := false) -> Button:
	var b := Button.new()
	b.text = text
	b.focus_mode = Control.FOCUS_ALL
	b.add_theme_font_override("font", font("bold"))
	b.add_theme_font_size_override("font_size", size)
	var base := PINK_DEEP if accent else Color(1, 0.98, 0.97)
	var fg := Color.WHITE if accent else INK
	b.add_theme_color_override("font_color", fg)
	b.add_theme_color_override("font_hover_color", fg)
	b.add_theme_color_override("font_pressed_color", fg)
	b.add_theme_color_override("font_focus_color", fg)
	var n := panel(base, PINK if not accent else Color("a8456a"), 14, 2, 6)
	n.content_margin_left = 18; n.content_margin_right = 18; n.content_margin_top = 10; n.content_margin_bottom = 10
	var h := n.duplicate(); h.bg_color = base.lightened(0.06); h.border_color = PINK_DEEP
	var pr := n.duplicate(); pr.bg_color = base.darkened(0.08); pr.shadow_size = 2
	var f := h.duplicate(); f.set_border_width_all(3)
	b.add_theme_stylebox_override("normal", n)
	b.add_theme_stylebox_override("hover", h)
	b.add_theme_stylebox_override("pressed", pr)
	b.add_theme_stylebox_override("focus", f)
	return b
