class_name World
extends Node2D
## Explorable area: HD ground tiles, y-sorted props and characters, foot collision, camera,
## partner following the player's trail, doors between areas. Port of GameScreen/WorldRenderer/
## PlayerController/CompanionController (exploration part).

signal area_entered(area_id: String)
signal door_touched(door: Dictionary, old_pos: Vector2)

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
var locked := false               # dialogue / cutscene / menus own the input
var partner_mode := 2             # 0 hidden, 1 placed by the story step, 2 walking with the player
var cine: Cutscene                # set by Game; overrides the camera while active
var npcs := {}                    # town NPC id -> Actor
var npc_brain := {}               # id -> {home, radius, target, pause}
var extras: Node2D                # quest item sprites and markers
var light_spots: Array = []       # [{pos, kind: "lamp"|"crystal"}] for the atmosphere lights
var _floor: Node2D
var _sorted: Node2D
var _ground: Node2D
var _trail: Array[Vector2] = []


func _ready() -> void:
	_ground = Node2D.new(); _ground.name = "Ground"; add_child(_ground)
	_floor = Node2D.new(); _floor.name = "Floor"; add_child(_floor)
	_sorted = Node2D.new(); _sorted.name = "Sorted"; _sorted.y_sort_enabled = true; add_child(_sorted)
	extras = Node2D.new(); extras.name = "Extras"; extras.y_sort_enabled = true
	_sorted.add_child(extras)
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
		if c != player and c != partner and c != extras:
			c.queue_free()
	for c in extras.get_children():
		c.queue_free()
	npcs.clear()
	npc_brain.clear()
	_build_ground()
	_build_props()
	if player.get_parent() == null:
		_sorted.add_child(player); _sorted.add_child(partner)
	player.position = nearest_open(pos)
	player.dir = Actor.dir_of(facing)
	partner.position = nearest_open(player.position + Vector2(-26, 10))
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
	light_spots.clear()
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
		var img: String = d.image
		if img.contains("lamp") or img.contains("lantern_post") or img.contains("lantern_on") or img.contains("crystal"):
			var kind := "crystal" if img.contains("crystal") else "lamp"
			var hgt := tex.get_height() * k
			light_spots.append({"pos": Vector2(p.x, p.y - hgt * (0.82 if kind == "lamp" else 0.5)), "foot": Vector2(p.x, p.y - 8), "kind": kind})
		if d.get("layer", "sort") == "floor":
			_floor.add_child(holder)
		else:
			_sorted.add_child(holder)


func nearest_open(p: Vector2) -> Vector2:
	if not Data.blocked(area, p.x, p.y, flags):
		return p
	for r in range(4, 400, 4):
		for i in 16:
			var q := p + Vector2.from_angle(i * TAU / 16.0) * r
			if not Data.blocked(area, q.x, q.y, flags):
				return q
	return Vector2(area.spawn[0], area.spawn[1])


func can_stand(x: float, y: float) -> bool:
	return not Data.blocked(area, x, y, flags)


func add_npc(id: String, sprite: String, pos: Vector2, facing: String, wander: float) -> Actor:
	var a := Actor.new().setup(sprite)
	a.position = nearest_open(pos)
	a.dir = Actor.dir_of(facing)
	a.facing8 = [0, 2, 6, 4][a.dir]
	_sorted.add_child(a)
	npcs[id] = a
	npc_brain[id] = {"home": a.position, "radius": wander, "target": a.position, "pause": randf_range(1.0, 4.0)}
	return a


func remove_npc(id: String) -> void:
	if npcs.has(id):
		npcs[id].queue_free()
		npcs.erase(id)
		npc_brain.erase(id)


## Town NPCs stroll slowly around their scheduled spot and never walk through walls or people.
func _update_npcs(delta: float, talking_to: String) -> void:
	for id in npcs:
		var a: Actor = npcs[id]
		var b: Dictionary = npc_brain[id]
		if locked and (id == talking_to or (cine and cine.active)):
			a.walking = false
			continue
		var d: Vector2 = b.target - a.position
		if d.length() > 2.0:
			var n := a.position + d.normalized() * minf(d.length(), 46.0 * delta)
			var near_player := absf(n.x - player.position.x) < 22 and absf(n.y - player.position.y) < 16
			if Data.clear_segment(area, a.position.x, a.position.y, n.x, n.y, flags) and not near_player:
				a.position = n; a.face(d.x, d.y); a.walking = true
			else:
				b.target = a.position; b.pause = 0.55; a.walking = false
		else:
			a.walking = false
			b.pause -= delta
			if b.pause <= 0:
				b.pause = randf_range(2.0, 6.0)
				if b.radius > 0:
					for _i in 8:
						var q: Vector2 = b.home + Vector2.from_angle(randf() * TAU) * randf() * b.radius
						if can_stand(q.x, q.y):
							b.target = q
							break
				elif randf() < 0.3:
					a.dir = randi() % 4; a.facing8 = [0, 2, 6, 4][a.dir]


var talking_to := ""


func _physics_process(delta: float) -> void:
	if player == null:
		return
	door_cooldown = maxf(0.0, door_cooldown - delta)
	_update_npcs(delta, talking_to)
	var v := Vector2.ZERO if locked else Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if v == Vector2.ZERO and not locked:
		v = input_vec
	var sprint := sprint_held or Input.is_key_pressed(KEY_SHIFT)
	var len := v.length()
	if cine and cine.active:
		pass                       # cutscene moves the actors
	elif len < 0.01:
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
	if partner_mode == 2 and not (cine and cine.active):
		_follow(delta)
	var vp := get_viewport_rect().size
	if cine and cine.cam_active:
		camera.position_smoothing_enabled = false
		camera.position = cine.cam_point()
		var zc := vp.y / VIEW_H * cine.cam_zoom
		camera.zoom = Vector2(zc, zc)
		_fit_limits(vp / zc)
		return
	camera.position_smoothing_enabled = true
	camera.position = player.position + Vector2(0, -24)
	var z := vp.y / (VIEW_H * framing * (1.045 if area.get("indoor", false) else 1.0))
	camera.zoom = Vector2(z, z)
	_fit_limits(vp / z)


## Maps smaller than the view (small rooms) are centred instead of pinned to the top-left.
func _fit_limits(view: Vector2) -> void:
	var w := float(area.get("w", 960))
	var h := float(area.get("h", 640))
	camera.limit_left = int(minf(0.0, (w - view.x) / 2.0)); camera.limit_right = int(maxf(w, (w + view.x) / 2.0))
	camera.limit_top = int(minf(0.0, (h - view.y) / 2.0)); camera.limit_bottom = int(maxf(h, (h + view.y) / 2.0))


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
		place_partner_beside()


func place_partner_beside() -> void:
	partner.position = nearest_open(player.position + Vector2(-24, 8))
	_trail.clear()


func _check_doors(old: Vector2) -> void:
	if door_cooldown > 0:
		return
	var x0 := player.position.x - Data.FOOT_W / 2.0
	var foot := Rect2(x0, player.position.y - Data.FOOT_TOP, Data.FOOT_W, Data.FOOT_TOP + Data.FOOT_BOTTOM)
	for d in area.get("doors", []):
		var r: Array = d.get("rect", [])
		if r.size() >= 4 and foot.intersects(Rect2(r[0], r[1], r[2], r[3])):
			door_cooldown = 1.0
			door_touched.emit(d, old)
			return
