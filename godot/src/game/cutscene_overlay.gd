class_name CutsceneOverlay
extends Control
## Screen-space part of the cutscene: letterbox bars, captions with chapter stills, fade and flash.

var cine: Cutscene
var _ribbon: Texture2D
var _bloom: Texture2D
var _ornament: Texture2D
var _stills := {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ribbon = Data.tex("ui/v32_cinematic_ribbon.png")
	_bloom = Data.tex("ui/v32_bloom.png")
	_ornament = Data.tex("ui/v32_scene_ornament.png")


func _draw() -> void:
	if cine == null:
		return
	var W := size.x
	var H := size.y
	if cine.bars > 0.001:
		var bh := H * 0.11 * cine.bars
		draw_rect(Rect2(0, 0, W, bh), UiTheme.INK)
		draw_rect(Rect2(0, H - bh, W, bh), UiTheme.INK)
		draw_rect(Rect2(0, bh, W, 2), Color(UiTheme.GOLD, cine.bars * 0.55))
		draw_rect(Rect2(0, H - bh - 2, W, 2), Color(UiTheme.GOLD, cine.bars * 0.36))
		if cine.active:
			var txt := "▶▶" if cine.fast else "Tahan layar untuk mempercepat"
			draw_string(UiTheme.font("body"), Vector2(W - 520, H - bh * 0.32), txt, HORIZONTAL_ALIGNMENT_RIGHT, 500, 16, Color(UiTheme.LAVENDER, 0.9))
	if cine.cap_dur > 0:
		var a := Cutscene._ease(clampf(minf(cine.cap_t * 2.0, (cine.cap_dur - cine.cap_t) * 2.0), 0, 1))
		var shift := (1.0 - a) * 16.0
		if cine.cap_art != null:
			var still: Texture2D = _stills.get(cine.cap_art)
			if still == null:
				still = Data.tex("ui/v32_cinema/%s.png" % cine.cap_art)
				_stills[cine.cap_art] = still
			if still:
				var sw := minf(W * 0.76, 940.0)
				var sh := sw * 432.0 / 768.0
				draw_texture_rect(still, Rect2((W - sw) / 2.0, H - H * 0.14 - sh, sw, sh), false, Color(1, 1, 1, a * 0.48))
		var cw := minf(700.0, W * 0.82)
		var ch := cw * 206.0 / 700.0
		if _bloom:
			draw_texture_rect(_bloom, Rect2(W / 2 - 230, H / 2 - 230, 460, 460), false, Color(1, 1, 1, a * 0.52))
		if _ribbon:
			draw_texture_rect(_ribbon, Rect2(W / 2 - cw / 2, H / 2 - ch / 2 + shift, cw, ch), false, Color(1, 1, 1, a * 0.87))
		if _ornament:
			draw_texture_rect(_ornament, Rect2(W / 2 - 382, H / 2 + 2 + shift, 124, 124), false, Color(1, 1, 1, a * 0.92))
			draw_texture_rect(_ornament, Rect2(W / 2 + 258, H / 2 + 2 + shift, 124, 124), false, Color(1, 1, 1, a * 0.72))
		var tf := UiTheme.font("title")
		var title_size := 38
		var tw := tf.get_string_size(cine.cap_title, HORIZONTAL_ALIGNMENT_LEFT, -1, title_size).x
		draw_string(tf, Vector2(W / 2 - tw / 2, H / 2 - 8 + shift), cine.cap_title, HORIZONTAL_ALIGNMENT_LEFT, -1, title_size, Color(UiTheme.CREAM, a))
		if cine.cap_sub != null:
			var bf := UiTheme.font("body")
			var sub := str(cine.cap_sub)
			var sw2 := bf.get_string_size(sub, HORIZONTAL_ALIGNMENT_LEFT, -1, 22).x
			draw_string(bf, Vector2(W / 2 - sw2 / 2, H / 2 + 32 + shift), sub, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color(UiTheme.GOLD, a))
	if cine.fade > 0.001:
		draw_rect(Rect2(0, 0, W, H), Color(cine.fade_color, cine.fade))
	if cine.flash > 0:
		draw_rect(Rect2(0, 0, W, H), Color(cine.flash_color, minf(1.0, cine.flash / maxf(0.01, cine.flash_dur))))
