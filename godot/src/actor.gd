class_name Actor
extends Node2D
## A character standing in the world (player, partner or NPC). position = foot point in map pixels.
## Port of game/Actor.java: 24-phase walk cycle, 8-way facing for Arland/Sofia, idle breathing,
## gait bounce/sway, soft contact shadow. Sprite sheets come from characters/<id>/.

const FW := 48
const FH := 72
const DIR_DOWN := 0
const DIR_LEFT := 1
const DIR_RIGHT := 2
const DIR_UP := 3

var character := ""
var dir := DIR_DOWN
var facing8 := 0
var walking := false
var sprinting := false
var anim := 0.0
var life := 0.0
var motion_blend := 0.0
var turn_impulse := 0.0
var pose = null            # pose name or null
var pose_time := 0.0
var pose_dur := 0.0
var emote = null
var emote_time := 0.0
var alpha := 1.0
const POSES := ["sit", "wave", "give", "reach", "bow", "hold_l", "hold_r", "cheer",
		"hug", "lean", "photo", "highfive", "dance", "read", "water", "sweep"]
var _emote_sprite: Sprite2D
var style := {"cadence": 1.0, "bounce": 1.0, "sway": 1.0, "breathing": 1.0, "phase": 0.0, "scale": 1.0}

var _sprite: Sprite2D
var _shadow: Sprite2D
var _sheets := {}     # name -> {tex, cols, rows, k}

const STYLES := {
	"arland": [1.06, 1.15, .95, 1.0, .7, 1.0], "sofia": [.96, .82, .72, .85, 2.2, 1.0],
	"raka": [1.03, .74, .75, .92, 1.0, 1.03], "rini": [1.08, .86, .83, .80, 3.5, 1.0],
	"sari": [.80, .34, .36, .63, 5.0, .95], "melati": [.92, .65, .60, .80, 2.1, 1.02],
	"tigor": [.92, .53, .57, 1.0, 4.8, 1.10], "laras": [.92, .45, .45, .62, 1.7, .99],
	"dito": [1.23, 1.50, 1.19, 1.15, 2.5, .98], "wulan": [.88, .60, .55, .70, 4.2, 1.0],
}


func setup(id: String) -> Actor:
	character = id
	var s: Array = STYLES.get(id, [1.0, 1.0, 1.0, 1.0, float(abs(id.hash()) % 60) / 10.0, 1.0])
	style = {"cadence": s[0], "bounce": s[1], "sway": s[2], "breathing": s[3], "phase": s[4], "scale": s[5]}
	life = randf() * 10.0
	_shadow = Sprite2D.new()
	_shadow.texture = load("res://assets/fx/contact_shadow_v37.png") if ResourceLoader.exists("res://assets/fx/contact_shadow_v37.png") else null
	_shadow.modulate = Color(1, 1, 1, 0.9)
	add_child(_shadow)
	_sprite = Sprite2D.new()
	_sprite.centered = false
	add_child(_sprite)
	if _shadow.texture:
		_shadow.scale = Vector2(26.0 / _shadow.texture.get_width(), 10.0 / _shadow.texture.get_height())
	_emote_sprite = Sprite2D.new()
	_emote_sprite.visible = false
	_emote_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_emote_sprite)
	_update_frame()
	return self


func set_pose(p: String, seconds: float) -> void:
	pose = p; pose_time = 0.0; pose_dur = seconds


func clear_pose() -> void:
	pose = null; pose_time = 0.0; pose_dur = 0.0


func show_emote(e: String, seconds: float) -> void:
	emote = e; emote_time = seconds
	_emote_sprite.texture = Data.tex("ui/emote_%s.png" % e)


func face_to(other: Node2D) -> void:
	if other != null:
		face(other.position.x - position.x, other.position.y - position.y)


func _sheet(name: String) -> Dictionary:
	if _sheets.has(name):
		return _sheets[name]
	var out := {}
	for k in [2, 1]:
		var p := "res://assets/characters/%s/%s%s.png" % [character, name, "@2x" if k == 2 else ""]
		if ResourceLoader.exists(p):
			var t: Texture2D = load(p)
			out = {"tex": t, "k": k, "cols": t.get_width() / (FW * k), "rows": t.get_height() / (FH * k)}
			break
	_sheets[name] = out
	return out


func face(dx: float, dy: float) -> void:
	if absf(dx) + absf(dy) < 0.0001:
		return
	var nf := posmod(int(round(atan2(-dx, dy) / (PI / 4.0))), 8)
	if nf != facing8:
		turn_impulse = minf(.9, turn_impulse + .35)
	facing8 = nf
	if absf(dx) > absf(dy):
		dir = DIR_LEFT if dx < 0 else DIR_RIGHT
	elif dy != 0:
		dir = DIR_UP if dy < 0 else DIR_DOWN


func dir_name() -> String:
	return ["down", "left", "right", "up"][dir]


static func dir_of(s: String) -> int:
	return {"left": DIR_LEFT, "right": DIR_RIGHT, "up": DIR_UP}.get(s, DIR_DOWN)


func _process(delta: float) -> void:
	var dt := clampf(delta, 0.0, 0.08)
	life += dt
	motion_blend = clampf(motion_blend + ((1.0 if walking else 0.0) - motion_blend) * (1.0 - exp(-dt * (12.0 if walking else 9.5))), 0, 1)
	turn_impulse = maxf(0.0, turn_impulse - dt * 3.8)
	if walking:
		anim = fmod(anim + dt * (32.0 if sprinting else 24.0) * style.cadence, 24.0)
	if emote_time > 0:
		emote_time -= dt
		if emote_time <= 0:
			emote = null
	if pose != null:
		pose_time += dt
		if walking and pose != "hold_l" and pose != "hold_r":
			clear_pose()
		elif pose_dur > 0 and pose_time >= pose_dur:
			clear_pose()
	_update_frame()


func _update_frame() -> void:
	var eight := character == "arland" or character == "sofia"
	var vdir8: int = facing8 if (facing8 & 1) == 1 else [0, 2, 6, 4][dir]
	var sh: Dictionary
	var row: int
	var col: int
	if eight:
		sh = _sheet("walk_8dir_v53" if walking else "idle_8dir_v53")
		row = vdir8
	else:
		sh = _sheet("walk_v53" if walking else "idle_v53")
		row = dir
	if sh.is_empty():
		sh = _sheet("walk")
		row = dir
	if sh.is_empty():
		return
	col = posmod(int(anim) if walking else int((life + style.phase) * 3.0), sh.cols)
	var pi: int = POSES.find(pose) if pose != null else -1
	if pi >= 0:
		var ps := _sheet("poses_v53")
		if ps.is_empty():
			ps = _sheet("poses")
		if not ps.is_empty() and pi < ps.rows:
			var anim_pose: bool = pose in ["wave", "cheer", "hug", "lean", "photo", "highfive", "dance", "read", "water", "sweep"] or (pose in ["hold_l", "hold_r"] and walking)
			var f := (int((anim if walking else pose_time) * 4.0) & 1) if anim_pose else 0
			sh = ps; row = pi; col = clampi(dir, 0, 3) * 2 + f
	var k: int = sh.k
	_sprite.texture = sh.tex
	_sprite.region_enabled = true
	_sprite.region_rect = Rect2(col * FW * k, mini(row, sh.rows - 1) * FH * k, FW * k, FH * k)
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS if k == 2 else CanvasItem.TEXTURE_FILTER_NEAREST
	var sc: float = style.scale / k
	# gait: two steps per cycle, bounce + side sway (same numbers as the Java build)
	var lift := 0.0
	var dx := 0.0
	var gait := sin(anim * PI / 6.0)
	if walking:
		lift += absf(gait) * (2.2 if sprinting else 1.4) * motion_blend * style.bounce
		dx += gait * (-0.8 if dir == DIR_LEFT else 0.8 if dir == DIR_RIGHT else 0.0) * motion_blend * style.sway
		dx += (-1.6 if facing8 in [1, 3] else 1.6 if facing8 in [5, 7] else 0.0) * motion_blend
	else:
		lift += maxf(0.0, sin((life + style.phase) * 2.12 * style.breathing)) * .65 * style.bounce
	if pose != null and pi < 0:     # procedural gestures
		var t := pose_time
		match pose:
			"laugh": lift = absf(sin(t * 12.0)) * 2.5
			"surprised": lift = sin(t / 0.35 * PI) * 7.0 if t < 0.35 else 0.0
			"jump": lift = absf(sin(t * 6.0)) * 8.0
			"nod": lift = -absf(sin(t * 9.0)) * 1.5
			"shake": dx = sin(t * 30.0) * 1.5 * maxf(0.0, 1.0 - t)
			"shy": dx = sin(t * 3.5) * 0.85; lift = -1.0
			"excited": lift = absf(sin(t * 11.0)) * 4.8
			"ponder": dx = sin(t * 1.9) * 0.7; lift = sin(t * 2.2) * 0.45
	if pose == null:
		dx += sin(life * 5.0 + style.phase) * turn_impulse * 1.5
	_sprite.scale = Vector2(sc, sc)
	_sprite.position = Vector2(-FW * style.scale / 2.0 + dx, -FH * style.scale - lift + 1)
	if _shadow.texture:
		var sk := 1.0 - minf(0.4, lift / 20.0)
		_shadow.scale = Vector2(26.0 * sk / _shadow.texture.get_width(), 10.0 / _shadow.texture.get_height())
		_shadow.position = Vector2(0, 0)
	modulate.a = alpha
	_emote_sprite.visible = emote != null and _emote_sprite.texture != null
	if _emote_sprite.visible:
		var pop := minf(1.0, (1.8 - emote_time) * 6.0)
		var tw := _emote_sprite.texture.get_width()
		_emote_sprite.scale = Vector2(22.0 / tw, 22.0 / tw) * pop
		_emote_sprite.position = Vector2(0, -FH * style.scale - 12 - lift)
