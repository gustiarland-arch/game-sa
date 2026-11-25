class_name Atmosphere
extends Node2D
## Time of day, weather and light for the world (port of WorldRenderer.drawAmbient, upgraded):
## a CanvasModulate tints the whole world, real 2D lights glow from lamps, crystals and the player
## at night or in caves, and rain, wind, petals, fireflies and butterflies drift over the view.

var world: World
var time := 0.0
var light := Color(1, 1, 1, 0)   # rgb tint, a = strength (WorldClock.light or the step tint)
var weather := "cerah"           # cerah / berawan / rain / berangin
var indoor := false
var realm := false
var ambient := ""
var quality := 2

var _modulate: CanvasModulate
var _lights: Array[PointLight2D] = []
var _player_light: PointLight2D
var _glow_tex: Texture2D
var _sparkle: Texture2D
var _rain: Array = []
var _target_mod := Color.WHITE
var _night := 0.0


func _ready() -> void:
	z_index = 40
	_modulate = CanvasModulate.new()
	add_child(_modulate)
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1))
	g.set_color(1, Color(1, 1, 1, 0))
	g.add_point(0.35, Color(1, 1, 1, 0.55))
	var gt := GradientTexture2D.new()
	gt.gradient = g
	gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5)
	gt.fill_to = Vector2(1.0, 0.5)
	gt.width = 256; gt.height = 256
	_glow_tex = gt
	_sparkle = Data.tex("ui/sparkle.png")
	_player_light = _make_light(Color(1, 0.92, 0.8), 1.0)
	var r := RandomNumberGenerator.new(); r.seed = 11
	for i in 220:
		_rain.append(Vector2(r.randf(), r.randf()))


func _make_light(c: Color, scale_k: float) -> PointLight2D:
	var l := PointLight2D.new()
	l.texture = _glow_tex
	l.color = c
	l.texture_scale = scale_k
	l.energy = 0
	l.blend_mode = Light2D.BLEND_MODE_ADD
	add_child(l)
	return l


## Rebuild the prop lights after an area change.
func rebuild_lights() -> void:
	for l in _lights:
		l.queue_free()
	_lights.clear()
	for spot in world.light_spots:
		var crystal: bool = spot.kind == "crystal"
		var l := _make_light(Color(0.62, 0.8, 1.0) if crystal else Color(1, 0.78, 0.48), 0.75 if crystal else 0.85)
		l.position = spot.pos if crystal else spot.foot.lerp(spot.pos, 0.35)
		l.set_meta("crystal", crystal)
		l.set_meta("head", spot.pos)
		_lights.append(l)


func dark_cave() -> bool:
	return ambient == "dark"


func _process(delta: float) -> void:
	time += delta
	var rain := weather == "rain" and not indoor
	# world tint: multiply instead of the old flat overlay, so lights can glow on top
	var tc := Color(light.r, light.g, light.b)
	var a := light.a
	if weather == "rain":
		tc = Color(0.25, 0.3, 0.42); a = 0.12 if indoor else 0.28
	elif indoor:
		a *= 0.45
	var mod := Color.WHITE.lerp(tc, clampf(a * 2.7, 0.0, 0.9))
	if weather == "berawan" and not indoor and not realm:
		mod = mod * Color(0.93, 0.94, 0.97)
	if dark_cave():
		mod = Color(0.16, 0.15, 0.24)
	_target_mod = mod
	_modulate.color = _modulate.color.lerp(_target_mod, minf(1.0, delta * 3.0))
	_night = clampf((light.a - 0.12) / 0.2, 0.0, 1.0) if not indoor else 0.0
	var lamp_on := 1.0 if (realm or dark_cave()) else maxf(pow(_night, 1.6), 0.5 if rain else 0.0)
	if indoor and not dark_cave():
		lamp_on = clampf(light.a * 2.0, 0.0, 0.6)
	for l in _lights:
		var crystal: bool = l.get_meta("crystal")
		var flick := 1.0 + 0.06 * sin(time * 2.0 + l.position.x)
		l.energy = (1.1 if crystal and dark_cave() else (0.9 if crystal else 1.05)) * (1.0 if crystal and dark_cave() else lamp_on) * flick
	_player_light.position = world.player.position + Vector2(0, -26)
	if dark_cave():
		_player_light.texture_scale = 1.9
		_player_light.energy = 1.25
	else:
		_player_light.texture_scale = 0.9
		_player_light.energy = 0.35 * _night
	queue_redraw()


func _view() -> Rect2:
	var cam := world.camera
	var vs := get_viewport_rect().size / cam.zoom
	var c := cam.get_screen_center_position()
	return Rect2(c - vs / 2, vs)


func _draw() -> void:
	if world == null:
		return
	var v := _view()
	var L := v.position.x
	var T := v.position.y
	var W := v.size.x
	var H := v.size.y
	var rain := weather == "rain" and not indoor
	var night := light.a >= 0.2 and not rain and not indoor
	# sun or moon halo
	if not indoor and not realm and not dark_cave():
		var halo := 230.0 if night else 260.0
		var hp := Vector2(L + W * (0.82 if night else 0.18), T + H * 0.2)
		var hc := Color(0.72, 0.78, 1, 0.12 if rain else 0.18) if night else Color(1, 0.78, 0.54, 0.14 if rain else 0.22)
		draw_texture_rect(_glow_tex, Rect2(hp - Vector2(halo, halo) / 2, Vector2(halo, halo)), false, hc)
	# area ambience particles
	if ambient != "" and ambient != "dark" and not rain:
		var n := 28 if quality == 2 else 16
		for i in n:
			var fx := fmod(i * 0.6180339 + time * (0.012 + (i % 5) * 0.004), 1.0) * W
			var fy := fposmod(i * 0.3819 + (time * 0.03 if ambient == "petals" else -sin(time * 0.3 + i) * 0.02), 1.0) * H
			var pt := Vector2(L + fx, T + fy)
			if ambient == "petals":
				draw_rect(Rect2(pt, Vector2(4, 3)), Color(1, 0.78, 0.86, 0.85))
			elif ambient == "fireflies":
				var al := 0.3 + 0.7 * maxf(0, sin(time * 2 + i))
				draw_texture_rect(_glow_tex, Rect2(pt - Vector2(9, 9), Vector2(18, 18)), false, Color(1, 0.95, 0.55, al * 0.8))
				draw_rect(Rect2(pt - Vector2(1, 1), Vector2(2.5, 2.5)), Color(1, 1, 0.7, al))
			elif _sparkle:
				var al := 0.3 + 0.6 * maxf(0, sin(time * 1.5 + i * 2))
				draw_texture_rect(_sparkle, Rect2(pt - Vector2(3, 3), Vector2(7, 7)), false, Color(1, 0.96, 0.85, al))
	# rain: slanted streaks and splash rings near the bottom of the view
	if rain:
		draw_rect(v, Color(0.2, 0.26, 0.38, 0.1))
		for i in _rain.size():
			var r: Vector2 = _rain[i]
			var fx := fmod(r.x + time * 0.05, 1.0) * (W + 60) - 30
			var fy := fposmod(r.y + time * (1.1 + (i % 4) * 0.15), 1.0) * (H + 40) - 20
			var p0 := Vector2(L + fx, T + fy)
			var near := i % 3 == 0
			draw_line(p0, p0 + (Vector2(-3.5, 17) if near else Vector2(-2.2, 11)), Color(0.88, 0.93, 1, 0.75 if near else 0.5), 1.6 if near else 1.1)
		for i in 18:
			var k := fmod(time * 1.7 + i * 0.37, 1.0)
			var c := Vector2(L + fmod(i * 0.618 + floor(time * 1.7 + i * 0.37) * 0.29, 1.0) * W, T + H * (0.35 + fmod(i * 0.41, 0.6)))
			draw_arc(c, 2 + k * 7, 0, TAU, 12, Color(0.85, 0.92, 1, 0.35 * (1 - k)), 1.0)
	# butterflies on sunny outdoor days
	if not indoor and not rain and not night and not realm and not dark_cave():
		for i in (7 if quality == 2 else 4):
			var bx := fposmod(i * 0.618 + sin(time * 0.11 + i) * 0.18, 1.0) * W
			var by := fposmod(i * 0.37 + cos(time * 0.09 + i * 2) * 0.15, 1.0) * H
			var flap := absf(sin(time * 14.0 + i)) * 2.6 + 0.8
			var bc := Color(1, 0.85, 0.4, 0.95) if i % 2 == 0 else Color(0.95, 0.75, 0.95, 0.95)
			draw_rect(Rect2(L + bx - flap - 0.5, T + by, flap, 2.4), bc)
			draw_rect(Rect2(L + bx + 0.5, T + by, flap, 2.4), bc)
	# windy days: leaves and petals carried sideways
	if weather == "berangin" and not indoor and not realm:
		for i in (35 if quality == 2 else 22):
			var fx := fmod(i * 0.618 + time * (0.09 + (i % 4) * 0.02), 1.0) * (W + 40) - 20
			var fy := fposmod(i * 0.37 + sin(time * 1.3 + i) * 0.03, 1.0) * H
			var lc := Color(1, 0.78, 0.86, 0.9) if i % 3 == 0 else Color(0.55, 0.75, 0.4, 0.9)
			draw_set_transform(Vector2(L + fx, T + fy), sin(time * 4 + i) * 0.8)
			draw_rect(Rect2(-2, -1, 4, 2.4), lc)
			draw_set_transform(Vector2.ZERO)
	# warm bloom over lamps when they are lit
	for l in _lights:
		var head: Vector2 = l.get_meta("head")
		if l.energy > 0.05 and v.grow(60).has_point(head):
			var s := 44.0 + sin(time * 2.0 + head.x) * 3.0
			var crystal: bool = l.get_meta("crystal")
			draw_texture_rect(_glow_tex, Rect2(head - Vector2(s, s) / 2, Vector2(s, s)), false,
				Color(0.7, 0.85, 1, 0.5 * minf(1, l.energy)) if crystal else Color(1, 0.88, 0.6, 0.55 * minf(1, l.energy)))
