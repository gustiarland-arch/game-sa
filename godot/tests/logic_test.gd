extends Node
## Headless logic checks for the Godot port:  godot --headless --path godot tests/logic_test.tscn
## Covers weather parity with the Java build, save schema 8 round trip, legacy save migration,
## condition checks and the full action list of every quest step resolving without unknown steps.

var fails := 0
var checks := 0


func ok(cond: bool, what: String) -> void:
	checks += 1
	if not cond:
		fails += 1
		print("GAGAL: ", what)


func _ready() -> void:
	# 1. weather parity (string from the Java WorldClock for days 1..400, first letter)
	var expect := FileAccess.get_file_as_string("res://tests/weather_java.txt").strip_edges()
	var got := ""
	for d in range(1, 401):
		got += WorldClock.weather(d)[0]
	ok(got == expect, "cuaca harian sama dengan versi Java")
	# 2. save round trip
	var p := Progress.new_game("arland", 2, Data.first_step, Data.area("arland_room"))
	p.add_flag("A"); p.add_flag("B"); p.items.append("bunga"); p.add_count("surat", 3); p.coins = 99
	p.add_history("Arland", "senang", "Halo", "plaza", 1)
	p.snapshot("PRO")
	var json := JSON.stringify(p.to_dict(true))
	var q := Progress.from_dict(JSON.parse_string(json))
	ok(q != null, "save bisa dibaca ulang")
	ok(q.to_dict(true).hash() == JSON.parse_string(json).hash() or JSON.stringify(q.to_dict(true)) == json, "save identik setelah round trip")
	ok(q.slot == 2 and q.coins == 99 and q.count("surat") == 3 and q.has_flag("B") and q.dialogue_history.size() == 1, "isi save utuh")
	ok(int(p.to_dict(false).schema) == 8, "schema 8")
	# 3. legacy save (schema 1, layout v3) migrates position only
	var old := Progress.from_dict({"schema": 1, "route": "sofia", "step": "PRO_PHONE", "area": "sofia_room", "x": 480, "y": 320})
	ok(old != null and is_equal_approx(old.x, 300.0) and is_equal_approx(old.y, 224.0) and old.coins == 12, "migrasi save lama")
	ok(Progress.from_dict({"schema": 9, "route": "sofia", "step": "x", "x": 1, "y": 1}) == null, "schema terlalu baru ditolak")
	ok(Progress.from_dict({"schema": 8, "route": "budi", "step": "x", "x": 1, "y": 1}) == null, "route tidak valid ditolak")
	# 4. conditions
	var e := QuestEngine.new(Progress.new_game("sofia", 1, Data.first_step, Data.area("sofia_room")))
	e.p.add_flag("X_SOFIA")
	ok(e.check({"flags": ["X_$RU"]}), "token $RU")
	ok(not e.check({"notFlags": ["X_SOFIA"]}), "notFlags")
	ok(e.check({"countBelow": {"k": 1}}) and not e.check({"count": {"k": 1}}), "count / countBelow")
	ok(e.check({"chapters": ["PRO"]}) and not e.check({"minChapter": "C01"}), "chapter")
	# 5. every step target in the data exists
	var missing := 0
	var walk := func(self_ref, v):
		if v is Dictionary:
			if v.get("do") == "step" and Data.step(str(v.get("id", ""))).is_empty():
				missing += 1
			for k in v:
				self_ref.call(self_ref, v[k])
		elif v is Array:
			for x in v:
				self_ref.call(self_ref, x)
	walk.call(walk, Data.quests)
	ok(missing == 0, "semua aksi step menunjuk step yang ada")
	# 6. every scene referenced by an action exists
	var scenes_missing := []
	var walk2 := func(self_ref, v):
		if v is Dictionary:
			if v.get("do") == "scene":
				var id: String = Routes.resolve(str(v.get("id", "")), "arland")
				var id2: String = Routes.resolve(str(v.get("id", "")), "sofia")
				if Data.scene(id).is_empty() and Data.scene(id2).is_empty():
					scenes_missing.append(v.get("id"))
			for k in v:
				self_ref.call(self_ref, v[k])
		elif v is Array:
			for x in v:
				self_ref.call(self_ref, x)
	walk2.call(walk2, Data.quests)
	ok(scenes_missing.is_empty(), "semua adegan yang dipanggil ada: %s" % [scenes_missing.slice(0, 5)])
	# 7. save files are byte-compatible with the LibGDX SaveStore (CRC over Java compact JSON)
	var jr = SaveStore.unwrap_payload(FileAccess.get_file_as_string("res://tests/fixtures/java_save_schema8.json"))
	ok(jr is Dictionary, "save buatan versi Java terbaca (CRC cocok): %s" % [jr if jr is String else "ok"])
	if jr is Dictionary:
		var jp := Progress.from_dict(jr)
		ok(jp != null and jp.step == "PRO_BOOK" and jp.coins == 40 and jp.has_flag("Ünicode \"kutip\"\n") and jp.dialogue_history.size() == 1, "isi save Java utuh")
		var out := OS.get_environment("SAVE_COMPAT_OUT")
		if out != "" and jp != null:
			var f: FileAccess = FileAccess.open(out, FileAccess.WRITE)
			f.store_string(SaveStore.wrap_payload(jp.to_dict(true)))
			f.close()
	# 8. slot save/load through user://
	var sp := Progress.new_game("sofia", 2, Data.first_step, Data.area("sofia_room"))
	sp.add_flag("T1")
	ok(SaveStore.save_slot(sp), "simpan slot")
	sp.add_flag("T2")
	ok(SaveStore.save_slot(sp), "simpan slot kedua kali (buat .bak)")
	var ld: Dictionary = SaveStore.load_slot("sofia", 2)
	ok(ld.status == "OK" and ld.value.has_flag("T2"), "muat slot")
	FileAccess.open(SaveStore.slot_path("sofia", 2), FileAccess.WRITE).store_string("rusak")
	ld = SaveStore.load_slot("sofia", 2)
	ok(ld.status == "RECOVERED" and ld.value.has_flag("T1"), "pulih dari .bak saat file utama rusak")
	SaveStore.delete_slot("sofia", 2)
	ok(SaveStore.load_slot("sofia", 2).status == "MISSING", "hapus slot")
	# 9. minigames: every config builds, and a correct play of the puzzle-like ones wins
	var mgs: Dictionary = Data.quests.get("minigames", {})
	var built := 0
	for id in mgs:
		for r in ["arland", "sofia"]:
			var g := Games.create(str(mgs[id].get("type", id)))
			g.init(mgs[id], r)
			g.x = 0; g.y = 0; g.w = 900; g.h = 480
			for k in 200:
				g.update(0.05)
				if k % 7 == 0:
					g.tap(450, 200)
			built += 1
	ok(built == mgs.size() * 2, "semua %d konfigurasi minigame jalan tanpa error" % mgs.size())
	var cl := Games.create("code"); cl.init(mgs.code_gua, "sofia")
	for i in cl.answer.size():
		cl.dial[i] = cl.answer[i]
	cl.check(); for k in 30: cl.update(0.05)
	ok(cl.finished and cl.score == 1, "peti kata sandi terbuka dengan jawaban benar")
	var ec := Games.create("v49_echo"); ec.init(mgs.v49_echo_plaza, "arland")
	for k in 100: ec.update(0.1)
	for st in ec.patterns.duplicate():
		for b in st: ec.choose(b)
		for k in 100: ec.update(0.1)
	ok(ec.finished and ec.score == 5, "gema kenangan selesai tanpa salah = skor 5")
	var bq := Games.create("bouquet"); bq.init({}, "sofia")
	bq.chosen = bq.pattern.duplicate(); bq.submit()
	ok(bq.finished and bq.score == 4, "buket cocok")
	# 10. puzzle: wrong resets, hint after 2 fails, right order solves
	var po := PuzzleOverlay.new()
	add_child(po)
	var solved := []
	po.open(Data.quests.puzzles.C01_SYMBOLS, "sofia", true, func(ok): solved.append(ok))
	ok(po.input("BUNGA") == "WRONG" and po.input("BUKU") == "WRONG" and po.hint_visible(), "puzzle: salah 2x memunculkan petunjuk")
	ok(po.input("BINTANG") == "CORRECT" and po.input("BUKU") == "CORRECT" and po.input("BUNGA") == "SOLVED", "puzzle: urutan route Sofia benar")
	# 11. shop purchase through the engine
	var se := QuestEngine.new(Progress.new_game("arland", 3, Data.first_step, Data.area("arland_room")), true)
	se.p.coins = 15
	ok(se.purchase("senja", "kopi_senja").begins_with("Membeli") and se.p.coins == 3 and se.p.has_item("kopi_senja"), "toko: beli kopi")
	ok(se.purchase("senja", "kukis_madu").begins_with("Koin belum cukup") and se.purchase("senja", "kopi_senja").begins_with("Barang ini sudah"), "toko: koin kurang / sudah dimiliki")
	# 12. achievements and memory book states
	var ap := Progress.new_game("sofia", 3, Data.first_step, Data.area("sofia_room"))
	ap.play_seconds = 130; ap.chapters["PRO"] = true; ap.affection = 80
	var gd := {"completed": {"arland": ["C06"], "sofia": ["C06"]}, "achievements": ["start"]}
	var ach_added := Achievements.unlock(ap, gd)
	ok(ach_added == ["chapter", "heart", "both"] and gd.achievements.size() == 4, "prestasi: hanya yang baru, tidak dicabut")
	var mbk := MemoryBook.new()
	mbk.p = ap
	mbk.g = {"routeFlags": {"arland": ["A_FLAG"]}}
	ap.add_flag("S_FLAG")
	ok(mbk.entry_state({"route": "shared", "unlock": "S_FLAG"}) == "UNLOCKED"
		and mbk.entry_state({"route": "arland", "unlock": "A_FLAG"}) == "OTHER_SIDE"
		and mbk.entry_state({"route": "arland", "unlock": "NOPE"}) == "LOCKED"
		and mbk.entry_state({"route": "sofia", "unlock": "NOPE"}) == "LOCKED", "memory book: terbuka / sisi lain / terkunci")
	mbk.free()
	# 13. romance rules
	var rp := Progress.new_game("sofia", 3, Data.first_step, Data.area("sofia_room"))
	for st in Data.steps:
		if str(Data.step(st).get("chapter", "")) == "C02":
			rp.step = st
			break
	rp.companion = true; rp.coins = 40; rp.minute = 9 * 60; rp.items.append("kopi_senja")
	var re := QuestEngine.new(rp, false)
	ok(re.romance_ready(), "romansa siap di Chapter 2 bersama pasangan")
	ok(re.give_gift("kopi_senja").begins_with("Hadiah diberikan!") and not rp.has_item("kopi_senja") and rp.affection == 4, "hadiah: item dipakai, +4 kedekatan")
	ok(re.give_gift("kopi_senja").begins_with("Kamu sudah memberi"), "hadiah: satu per hari")
	ok(re.date_block("taman", "plaza").begins_with("Datang dahulu") and re.start_date("taman", "taman_kota").begins_with("Kencan dimulai!") and rp.coins == 32, "kencan: lokasi dicek, koin dipotong")
	ok(re.start_couple_action("gandengan", "plaza").begins_with("Aksi berdua!") and rp.holding_hands
		and re.start_couple_action("gandengan", "plaza") == "Berhenti bergandengan." and re.start_couple_action("gandengan", "plaza") == "Bergandengan lagi.", "gandengan: aktif / lepas / lagi tanpa bonus ganda")
	ok(re.couple_action_actions("pelukan").size() >= 2 and re.date_actions("taman").size() >= 3, "aksi romansa menghasilkan cutscene + scene")
	print("%s: %d pemeriksaan, %d gagal" % ["SEMUA LULUS" if fails == 0 else "ADA YANG GAGAL", checks, fails])
	get_tree().quit(1 if fails > 0 else 0)
