class_name World
extends Node2D
## Explorable area: HD ground tiles, y-sorted props and characters, foot collision, camera,
## partner following the player's trail, doors between areas. Port of GameScreen/WorldRenderer/
## PlayerController/CompanionController (exploration part).

signal area_entered(area_id: String)

const WALK_SPEED := 112.0
const SPRINT_SPEED := 176.0
const VIEW_H := 428.0          # world units visible vertically at framing 1.0 (same as Java ExtendViewport)

var area: Dictionary = {}
var route := "sofia"
var flags := {}
var player: Actor
var partner: Actor
var camera: Camera2D
var framing := 1.2
var input_vec := Vector2.ZERO     # set by the touch joystick (HUD); keyboard is read here
var sprint_held := false
var door_cooldown := 0.0
var _floor: Node2D
var _sorted: Node2D
var _ground: Node2D
var _trail: Array[Vector2] = []


func _ready() -> void:
	_ground = Node2D.new(); _ground.name = "Ground"; add_child(_ground)
	_floor = Node2D.new(); _floor.name = "Floor"; add_child(_floor)
	_sorted = Node2D.new(); _sorted.name = "Sorted"; _sorted.y_sort_enabled = true; add_child(_sorted)
	camera = Camera2D.new(); camera.position_smoothing_enabled = true; camera.position_smoothing_speed = 7.0
	add_child(camera)


func start(route_id: String, area_id: String, pos: Vector2, facing := "down") -> void:
	route = route_id
	var me := "arland" if route == "arland" else "sofia"
	var other := "sofia" if route == "arland" else "arland"
	player = Actor.new().setup(me)
	partner = Actor.new().setup(other)
	enter_area(area_id, pos, facing)


func enter_area(area_id: String, pos: Vector2, facing := "down") -> void:
	area = Data.area(area_id)
	for n in [_ground, _floor]:
		for c in n.get_children():
			c.queue_free()
	for c in _sorted.get_children():
		if c != player and c != partner:
			c.queue_free()
	_build_ground()
	_build_props()
	if player.get_parent() == null:
		_sorted.add_child(player); _sorted.add_child(partner)
	player.position = _nearest_open(pos)
	player.dir = Actor.dir_of(facing)
	partner.position = _nearest_open(player.position + Vector2(-26, 10))
	_trail.clear()
	camera.limit_left = 0; camera.limit_top = 0
	camera.limit_right = int(area.get("w", 960)); camera.limit_bottom = int(area.get("h", 640))
	camera.position = player.position + Vector2(0, -24)
	camera.reset_smoothing()
	door_cooldown = 0.6
	area_entered.emit(area_id)


func _build_ground() -> void:
	var tiles: Array = area.get("tiles", [])
	if tiles.is_empty():
		var s := Sprite2D.new()
		s.texture = load("res://assets/" + area.get("image", ""))
		s.centered = false
		s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		if s.texture:
			s.scale = Vector2(area.w / s.texture.get_width(), area.h / s.texture.get_height())
		_ground.add_child(s)
		return
	for t in tiles:
		var s := Sprite2D.new()
		s.texture = load("res://assets/" + t.image)
		s.centered = false
		s.position = Vector2(t.x, t.y)
		s.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		if s.texture:
			s.scale = Vector2(t.w / s.texture.get_width(), t.h / s.texture.get_height())
		_ground.add_child(s)


func _build_props() -> void:
	for p in area.get("props", []):
		var d: Dictionary = Data.props.get(p.get("type", ""), {})
		if d.is_empty():
			continue
		var tex: Texture2D = load("res://assets/" + d.image) if ResourceLoader.exists("res://assets/" + d.image) else null
		if tex == null:
			continue
		var holder := Node2D.new()
		holder.position = Vector2(p.x, p.y)
		var s := Sprite2D.new()
		var k := Data.prop_scale(d)
		s.texture = tex
		s.centered = false
		s.scale = Vector2(k, k)
		s.position = Vector2(-tex.get_width() * k / 2.0, -tex.get_height() * k)
		s.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS if k < 1.0 else CanvasItem.TEXTURE_FILTER_NEAREST
		holder.add_child(s)
		if d.get("layer", "sort") == "floor":
			_floor.add_child(holder)
		else:
			_sorted.add_child(holder)


func _nearest_open(p: Vector2) -> Vector2:
	if not Data.blocked(area, p.x, p.y, flags):
		return p
	for r in range(4, 400, 4):
		for i in 16:
			var q := p + Vector2.from_angle(i * TAU / 16.0) * r
			if not Data.blocked(area, q.x, q.y, flags):
				return q
	return Vector2(area.spawn[0], area.spawn[1])


func _physics_process(delta: float) -> void:
	if player == null:
		return
	door_cooldown = maxf(0.0, door_cooldown - delta)
	var v := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if v == Vector2.ZERO:
		v = input_vec
	var sprint := sprint_held or Input.is_key_pressed(KEY_SHIFT)
	var len := v.length()
	if len < 0.01:
		player.walking = false
	else:
		var dirv := v / len
		var spd := (SPRINT_SPEED if sprint else WALK_SPEED) * maxf(0.45, minf(1.0, len)) * delta
		var o := player.position
		var nx := o.x + dirv.x * spd
		if Data.clear_segment(area, o.x, o.y, nx, o.y, flags):
			player.position.x = nx
		var ny := player.position.y + dirv.y * spd
		if Data.clear_segment(area, player.position.x, o.y, player.position.x, ny, flags):
			player.position.y = ny
		player.face(dirv.x, dirv.y)
		player.sprinting = sprint
		player.walking = (player.position - o).length() > 0.01
		if player.walking and (_trail.is_empty() or _trail[-1].distance_to(player.position) > 6):
			_trail.append(player.position)
			if _trail.size() > 80:
				_trail.pop_front()
		_check_doors(o)
	_follow(delta)
	camera.position = player.position + Vector2(0, -24)
	var vp := get_viewport_rect().size
	var z := vp.y / (VIEW_H * framing * (1.045 if area.get("indoor", false) else 1.0))
	camera.zoom = Vector2(z, z)


## Partner walks along the player's trail and stops at a comfortable distance.
func _follow(delta: float) -> void:
	var target := partner.position
	while _trail.size() > 0 and _trail[0].distance_to(player.position) > 34:
		target = _trail[0]
		if partner.position.distance_to(_trail[0]) < 6:
			_trail.pop_front()
		else:
			break
	var d := target - partner.position
	var dist_player := partner.position.distance_to(player.position)
	if d.length() > 2 and dist_player > 30:
		var spd := (SPRINT_SPEED if player.sprinting else WALK_SPEED) * (1.08 if dist_player > 70 else 0.96) * delta
		var step := d.normalized() * minf(spd, d.length())
		partner.position += step
		partner.face(step.x, step.y)
		partner.walking = true
		partner.sprinting = player.sprinting
	else:
		partner.walking = false
		if dist_player < 80:
			partner.face(player.position.x - partner.position.x, player.position.y - partner.position.y)
	if dist_player > 240:      # fell far behind (e.g. after a scene): catch up next to the player
		partner.position = _nearest_open(player.position + Vector2(-24, 8))
		_trail.clear()


func _check_doors(old: Vector2) -> void:
	if door_cooldown > 0:
		return
	for d in area.get("doors", []):
		var r: Array = d.get("rect", [])
		if r.size() < 4:
			continue
		if Rect2(r[0], r[1], r[2], r[3]).grow(4).has_point(player.position):
			door_cooldown = 1.0
			var to: String = d.get("to", "")
			if Data.maps.has(to):
				enter_area(to, Vector2(d.get("tx", 0), d.get("ty", 0)), d.get("dir", "down"))
			return
