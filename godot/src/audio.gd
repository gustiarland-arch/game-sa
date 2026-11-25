extends Node
## Music with crossfade and one-shot sound effects (simple port of AudioManager; the full
## time-of-day soundscape comes with the day/night phase). Autoload name: Audio.

var music_volume := 0.7
var sfx_volume := 0.9
var _music_id := ""
var _bgm: AudioStreamPlayer
var _old: AudioStreamPlayer
var _cache := {}


func _ready() -> void:
	_bgm = AudioStreamPlayer.new(); add_child(_bgm)
	_old = AudioStreamPlayer.new(); add_child(_old)


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
	if id == _music_id or id == "":
		return
	var s := _stream(["res://assets/audio/music/%s.ogg" % id, "res://assets/audio/music/%s_theme.ogg" % id])
	if s == null:
		return
	_music_id = id
	_old.stream = _bgm.stream
	_old.volume_db = _bgm.volume_db
	if _bgm.playing:
		_old.play(_bgm.get_playback_position())
	if s is AudioStreamOggVorbis:
		s.loop = true
	_bgm.stream = s
	_bgm.volume_db = -60
	_bgm.play()
	var tw := create_tween().set_parallel()
	tw.tween_property(_bgm, "volume_db", linear_to_db(music_volume), 1.2)
	tw.tween_property(_old, "volume_db", -60.0, 1.2)
	tw.chain().tween_callback(_old.stop)


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
