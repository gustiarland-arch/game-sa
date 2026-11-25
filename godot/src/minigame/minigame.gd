class_name Minigame
extends RefCounted
## Base of all minigames (port of game/minigame/Minigame.java). The game code keeps the Java
## layout maths (y up, inside the work area x, y, w, h); the drawing helpers flip to Godot's y-down
## screen space, so each game reads line for line like the original.

const GREEN := Color(0.45, 0.78, 0.5)
const RED := Color(0.9, 0.45, 0.5)

var cfg: Dictionary = {}
var route := "sofia"
var x := 0.0
var y := 0.0
var w := 0.0
var h := 0.0
var t := 0.0
var finished := false
var score := 0
var result_text := ""
var screen_h := 720.0
var canvas: CanvasItem         # set while drawing


func init(config: Dictionary, r: String) -> void:
	cfg = config
	route = r
	start()


func start() -> void:
	pass


func update(dt: float) -> void:
	t += dt


func draw() -> void:
	pass


func tap(_px: float, _py: float) -> void:
	pass


func key(_index: int) -> void:
	pass


static func inside(px: float, py: float, bx: float, by: float, bw: float, bh: float) -> bool:
	return px >= bx and px <= bx + bw and py >= by and py <= by + bh


func sfx(id: String, mult := 1.0) -> void:
	Audio.sfx(id, mult)


# ------------------------------------------------------------ drawing in Java (y-up) coordinates
func rect(rx: float, ry: float, rw: float, rh: float, c: Color, a := 1.0) -> void:
	canvas.draw_rect(Rect2(rx, screen_h - ry - rh, rw, rh), Color(c, c.a * a))


func image(tex: Texture2D, ix: float, iy: float, iw: float, ih: float, a := 1.0) -> void:
	if tex:
		canvas.draw_texture_rect(tex, Rect2(ix, screen_h - iy - ih, iw, ih), false, Color(1, 1, 1, a))


func panel(kind: String, px: float, py: float, pw: float, ph: float) -> void:
	var st: StyleBoxFlat
	match kind:
		"dark": st = UiTheme.panel(Color("3a2e52"), Color("57476f"), 14, 2, 0)
		"button": st = UiTheme.panel(Color("fff3f6"), UiTheme.PINK, 14, 2, 4)
		"selected": st = UiTheme.panel(Color("ffe1ea"), UiTheme.PINK_DEEP, 14, 3, 4)
		_: st = UiTheme.panel(Color("fbf3ee"), Color("d9c6e0"), 14, 2, 0)
	st.draw(canvas.get_canvas_item(), Rect2(px, screen_h - py - ph, pw, ph))


## LibGDX text: y is the top of the line. scale 1.0 of the body font = 23 px.
func text(s: String, tx: float, ty: float, c: Color, scale := 1.0, align := "left", width := 0.0, kind := "body") -> void:
	var f := UiTheme.font(kind)
	var size := int(round((46.0 if kind == "title" else 23.0) * scale))
	var base := screen_h - ty + f.get_ascent(size) * 0.82
	var ha := HORIZONTAL_ALIGNMENT_LEFT
	if align == "center":
		ha = HORIZONTAL_ALIGNMENT_CENTER
	elif align == "right":
		ha = HORIZONTAL_ALIGNMENT_RIGHT
	if width > 0:
		canvas.draw_multiline_string(f, Vector2(tx, base), s, ha, width, size, -1, c)
	else:
		canvas.draw_string(f, Vector2(tx, base), s, ha, -1.0, size, c)


func portrait(who: String, emo: String) -> Texture2D:
	return Data.portrait(who, emo)
