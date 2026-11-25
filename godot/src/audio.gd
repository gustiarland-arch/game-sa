extends Node
## Two looping streams (music and ambience) with crossfades, dialogue ducking, and one-shot sound
## effects (port of AudioManager.java). Autoload name: Audio.

var music_volume := 0.7
var ambience_volume := 0.8
var sfx_volume := 0.9
var _cache := {}
var _bus := {}            # "music"/"ambience" -> {id, active, outgoing, in, out, env}
var _duck := false
var _duck_level := 1.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for name in ["music", "ambience"]:
		_bus[name] = {"id": "", "active": null, "outgoing": null, "in": 0.0, "out": 0.0, "env": name == "ambience"}


func _stream(paths: Array) -> AudioStream:
	for p in paths:
		if _cache.has(p):
			return _cache[p]
		if ResourceLoader.exists(p):
			var s: AudioStream = load(p)
			_cache[p] = s
			return s
	return null


func music(id: String) -> void:
	if id == "":
		return
	_change("music", id, _stream(["res://assets/audio/music/%s.ogg" % id, "res://assets/audio/music/%s_theme.ogg" % id]))


## Empty id fades the ambience out.
func ambience(id: String) -> void:
	_change("ambience", id, _stream(["res://assets/audio/ambience/%s.ogg" % id]) if id != "" else null)


func current_music() -> String:
	return _bus.music.id


func current_ambience() -> String:
	return _bus.ambience.id


func duck(speech: bool) -> void:
	_duck = speech


func _change(name: String, id: String, s: AudioStream) -> void:
	var b: Dictionary = _bus[name]
	if id == b.id:
		return
	if s == null and id != "":
		return      # keep the old stream when the new one is missing
	_drop(b.outgoing)
	b.outgoing = b.active
	b.out = b.in
	b.active = null
	b.in = 0.0
	b.id = id
	if s == null:
		return
	if s is AudioStreamOggVorbis:
		s.loop = true
	var pl := AudioStreamPlayer.new()
	pl.stream = s
	pl.volume_db = -80
	add_child(pl)
	pl.play()
	b.active = pl


func _drop(pl) -> void:
	if pl != null and is_instance_valid(pl):
		pl.stop()
		pl.queue_free()


func _process(dt: float) -> void:
	_duck_level += ((0.62 if _duck else 1.0) - _duck_level) * minf(1.0, dt * 3.0)
	_advance(_bus.music, dt, music_volume * _duck_level)
	_advance(_bus.ambience, dt, ambience_volume * 0.55 * (0.8 + 0.2 * _duck_level))


func _advance(b: Dictionary, dt: float, level: float) -> void:
	var rate := 0.45 if b.env else 0.75
	if b.active != null:
		b.in = minf(1.0, b.in + dt * rate)
		b.active.volume_db = linear_to_db(maxf(0.0001, minf(1.0, level * b.in)))
	if b.outgoing != null:
		b.out -= dt * rate
		if b.out <= 0:
			_drop(b.outgoing)
			b.outgoing = null
		else:
			b.outgoing.volume_db = linear_to_db(maxf(0.0001, minf(1.0, level * b.out)))


func sfx(id: String, mult := 1.0) -> void:
	var s := _stream(["res://assets/audio/sfx/%s.wav" % id, "res://assets/audio/sfx/%s.ogg" % id])
	if s == null or mult <= 0:
		return
	var p := AudioStreamPlayer.new()
	p.stream = s
	p.volume_db = linear_to_db(clampf(sfx_volume * mult, 0.001, 1.0))
	add_child(p)
	p.finished.connect(p.queue_free)
	p.play()
