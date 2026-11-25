class_name Achievements
extends RefCounted
## Offline achievements, permanent across saves (port of Achievements.java). Cosmetic only.

const ALL := [
	["start", "Langkah Pertama", "Mainkan cerita setidaknya 2 menit."],
	["chapter", "Satu Bab Bersama", "Tamatkan satu chapter utama."],
	["chapters", "Penjelajah Kenangan", "Tamatkan lima chapter di satu route."],
	["friend", "Teman Dunia Kecil", "Elus empat hewan berbeda."],
	["couple", "Hari Kita", "Selesaikan tiga jenis aksi berdua."],
	["minigames", "Main Bareng", "Mainkan tiga jenis minigame bersama."],
	["world", "Dunia yang Bergerak", "Ikuti lima jenis event dunia."],
	["moments", "Momen Kecil", "Nikmati tiga jenis momen harian."],
	["dates", "Hari yang Istimewa", "Jalani tiga kencan."],
	["heart", "Semakin Dekat", "Capai kedekatan 75."],
	["shards", "Tiga Keping Kenangan", "Kumpulkan tiga keping kenangan."],
	["both", "Dua Sisi, Satu Cerita", "Tamatkan Chapter 6 dengan Arland dan Sofia."],
]


static func _types(counts: Dictionary) -> int:
	var n := 0
	for v in counts.values():
		if v != null and int(v) > 0:
			n += 1
	return n


static func _total(counts: Dictionary) -> int:
	var n := 0
	for v in counts.values():
		if v != null and int(v) > 0:
			n += mini(1000, int(v))
	return n


## Adds newly earned ids to the global dictionary's "achievements"; returns the added ids.
static func unlock(p: Progress, g: Dictionary) -> Array:
	var mini_types := 0
	for k in p.counters:
		if str(k).begins_with("total_romgame_") and int(p.counters[k]) > 0:
			mini_types += 1
	var c: Dictionary = g.get("completed", {})
	var both: bool = c.get("arland", []).has("C06") and c.get("sofia", []).has("C06")
	var cond := [p.play_seconds >= 120, p.chapters.size() >= 1, p.chapters.size() >= 5,
		p.petted.size() >= 4, _types(p.couple_action_counts) >= 3, mini_types >= 3,
		_types(p.world_event_counts) >= 5, _types(p.moment_counts) >= 3,
		_total(p.date_counts) >= 3, p.affection >= 75, p.shards >= 3, both]
	if not (g.get("achievements") is Array):
		g["achievements"] = []
	var added := []
	for i in ALL.size():
		if cond[i] and not g.achievements.has(ALL[i][0]):
			g.achievements.append(ALL[i][0])
			added.append(ALL[i][0])
	return added


static func name_of(id: String) -> String:
	for d in ALL:
		if d[0] == id:
			return d[1]
	return id
