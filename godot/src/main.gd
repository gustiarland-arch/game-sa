extends Node
## Boot. Normal start opens the world (title/menus come in phase 3).
## Capture mode for automated QA (not used by players):
##   godot --path godot -- --shot <route> <area> <x> <y> <frames> <out.png> [x:y;x:y waypoints]

var world: World
var _shot := {}
var _frame := 0
var _wp := 0


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	world = World.new()
	add_child(world)
	var i := args.find("--shot")
	if i >= 0:
		_shot = {"route": args[i + 1], "area": args[i + 2], "x": float(args[i + 3]), "y": float(args[i + 4]),
				"frames": int(args[i + 5]), "out": args[i + 6], "wps": []}
		if args.size() > i + 7:
			for pt in args[i + 7].split(";", false):
				var xy := pt.split(":")
				_shot.wps.append(Vector2(float(xy[0]), float(xy[1])))
		world.start(_shot.route, _shot.area, Vector2(_shot.x, _shot.y))
	else:
		var a: Dictionary = Data.area("plaza")
		world.start("sofia", "plaza", Vector2(a.spawn[0], a.spawn[1]))


func _process(_delta: float) -> void:
	if _shot.is_empty():
		return
	_frame += 1
	if _wp < _shot.wps.size():
		var d: Vector2 = _shot.wps[_wp] - world.player.position
		if d.length() < 8:
			_wp += 1
			world.input_vec = Vector2.ZERO
		else:
			world.input_vec = d.normalized()
	else:
		world.input_vec = Vector2.ZERO
	if _frame == _shot.frames:
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(_shot.out)
		print("SHOT ", _shot.out, " at ", world.player.position)
		get_tree().quit()
