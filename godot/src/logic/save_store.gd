class_name SaveStore
extends RefCounted
## Local saves (port of logic/SaveStore.java), byte-compatible with the LibGDX build:
## user://saves/<route>_slot_0N.json + global.json, envelope {format:"olu-save", crc, payload}, CRC32 over the
## Java compact JSON of the payload, rotating .bak/.bak2 backups and atomic writes. On Android the Godot
## user:// folder is the same app files folder LibGDX used, so existing saves keep working.

const SLOTS := 2
const DIR := "user://saves/"
const SOURCES := ["", ".tmp", ".bak", ".bak2"]

static var _crc_table: PackedInt64Array = []


static func slot_path(route: String, slot: int) -> String:
	return DIR + "%s_slot_%02d.json" % [route, slot]


# ------------------------------------------------------------ Java-compatible compact JSON + CRC32
static func compact(v) -> String:
	if v == null:
		return "null"
	if v is String or v is StringName:
		return _quote(str(v))
	if v is bool:
		return "true" if v else "false"
	if v is int:
		return str(v)
	if v is float:
		if v == roundf(v) and absf(v) < 1e15:
			return str(int(v))
		return _java_double(v)
	if v is Dictionary:
		var parts := PackedStringArray()
		for k in v:
			parts.append(_quote(str(k)) + ":" + compact(v[k]))
		return "{" + ",".join(parts) + "}"
	if v is Array or v is PackedStringArray:
		var parts := PackedStringArray()
		for e in v:
			parts.append(compact(e))
		return "[" + ",".join(parts) + "]"
	return _quote(str(v))


## Double.toString for the rare non-integral value (plain notation between 1e-3 and 1e7).
static func _java_double(d: float) -> String:
	var a := absf(d)
	if a >= 1e-3 and a < 1e7:
		var s := String.num(d, 15)
		if not s.contains("."):
			s += ".0"
		return s
	var e := floori(log(a) / log(10.0))
	var m := d / pow(10.0, e)
	var ms := String.num(m, 15)
	if not ms.contains("."):
		ms += ".0"
	return ms + "E" + str(e)


static func _quote(s: String) -> String:
	var b := "\""
	for ch in s:
		match ch:
			"\"": b += "\\\""
			"\\": b += "\\\\"
			"\n": b += "\\n"
			"\r": b += "\\r"
			"\t": b += "\\t"
			_:
				if ch.unicode_at(0) < 0x20:
					b += "\\u%04x" % ch.unicode_at(0)
				else:
					b += ch
	return b + "\""


static func crc32(text: String) -> int:
	if _crc_table.is_empty():
		_crc_table.resize(256)
		for n in 256:
			var c := n
			for _k in 8:
				c = (0xEDB88320 ^ (c >> 1)) if (c & 1) else (c >> 1)
			_crc_table[n] = c
	var crc := 0xFFFFFFFF
	for byte in text.to_utf8_buffer():
		crc = _crc_table[(crc ^ byte) & 0xFF] ^ (crc >> 8)
	return crc ^ 0xFFFFFFFF


static func wrap_payload(payload: Dictionary) -> String:
	return JSON.stringify({"format": "olu-save", "crc": crc32(compact(payload)), "payload": payload}, "  ", false)


## Payload dictionary, or an error string.
static func unwrap_payload(text: String):
	var env = JSON.parse_string(text)
	if not (env is Dictionary) or env.get("format") != "olu-save":
		return "Bukan file save game ini"
	var p = env.get("payload")
	if not (p is Dictionary):
		return "Payload hilang"
	var want = env.get("crc")
	if not (want is float or want is int) or int(want) != crc32(compact(p)):
		return "Checksum tidak cocok (file rusak)"
	return p


# ------------------------------------------------------------ files
static func _read(path: String):
	if not FileAccess.file_exists(path):
		return null
	return FileAccess.get_file_as_string(path)


static func _write_atomic(path: String, content: String) -> bool:
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var tmp := path + ".tmp"
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(content)
	f.close()
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(path)
	return DirAccess.rename_absolute(tmp, path) == OK


static func _write_with_backup(path: String, payload: Dictionary, progress_slot: bool) -> bool:
	var old = _read(path)
	if old != null:
		var old_payload = unwrap_payload(old)
		if old_payload is Dictionary:
			if progress_slot and float(old_payload.get("schema", 0)) > Progress.SCHEMA:
				return false          # never overwrite a save from a newer app version
			var prev = _read(path + ".bak")
			if prev != null and unwrap_payload(prev) is Dictionary:
				if not _write_atomic(path + ".bak2", prev):
					return false
			if not _write_atomic(path + ".bak", old):
				return false
	return _write_atomic(path, wrap_payload(payload))


## {value: Progress or null, status: "OK"|"MISSING"|"RECOVERED"|"CORRUPT"|"INCOMPATIBLE", error}
static func load_slot(route: String, slot: int) -> Dictionary:
	if not Routes.valid(route) or slot < 1 or slot > SLOTS:
		return {"value": null, "status": "CORRUPT", "error": "Route atau nomor slot tidak valid"}
	var path := slot_path(route, slot)
	var seen := false
	var err := ""
	for suffix in SOURCES:
		var raw = _read(path + suffix)
		if raw == null:
			continue
		seen = true
		var m = unwrap_payload(raw)
		if m is String:
			if err == "":
				err = m
			continue
		var schema := int(m.get("schema", 0))
		if schema > Progress.SCHEMA and suffix == "":
			return {"value": null, "status": "INCOMPATIBLE", "error": "Save berasal dari versi game lebih baru (schema %d)" % schema}
		var p := Progress.from_dict(m)
		if p == null or p.route != route or p.slot != slot:
			if err == "":
				err = "Isi save tidak valid"
			continue
		return {"value": p, "status": "OK" if suffix == "" else "RECOVERED", "error": err}
	return {"value": null, "status": "CORRUPT" if seen else "MISSING", "error": err}


static func save_slot(p: Progress) -> bool:
	if p == null or not Routes.valid(p.route) or p.slot < 1 or p.slot > SLOTS or p.step == "":
		return false
	var prev := p.saved_at
	p.saved_at = int(Time.get_unix_time_from_system() * 1000.0)
	var ok := _write_with_backup(slot_path(p.route, p.slot), p.to_dict(true), true)
	if not ok:
		p.saved_at = prev
	return ok


static func delete_slot(route: String, slot: int) -> void:
	for suffix in SOURCES:
		var f: String = slot_path(route, slot) + suffix
		if FileAccess.file_exists(f):
			DirAccess.remove_absolute(f)


static func load_global() -> Dictionary:
	for suffix in SOURCES:
		var raw = _read(DIR + "global.json" + suffix)
		if raw != null:
			var m = unwrap_payload(raw)
			if m is Dictionary:
				return m
	return {"schema": 2, "completed": {"arland": [], "sofia": []}, "routeFlags": {"arland": [], "sofia": []},
			"achievements": [], "lastRoute": null, "lastSlot": 0}


## Merge a slot's progress into the global record (chapters finished and flags per route) and
## unlock achievements. Returns the newly unlocked achievement ids, or null when the write failed.
static func absorb_global(p: Progress):
	var g := load_global()
	for key in ["completed", "routeFlags"]:
		if not (g.get(key) is Dictionary):
			g[key] = {"arland": [], "sofia": []}
		var have: Array = g[key].get(p.route, [])
		var src: Array = p.chapters.keys() if key == "completed" else p.flags.keys()
		for f in src:
			if not have.has(f):
				have.append(f)
		g[key][p.route] = have
	g["lastRoute"] = p.route
	g["lastSlot"] = p.slot
	var added := Achievements.unlock(p, g)
	return added if _write_with_backup(DIR + "global.json", g, false) else null


static func both_completed(chapter: String) -> bool:
	var c: Dictionary = load_global().get("completed", {})
	return c.get("arland", []).has(chapter) and c.get("sofia", []).has(chapter)
