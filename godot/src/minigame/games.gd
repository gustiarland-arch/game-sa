class_name Games
extends RefCounted
## All minigames (port of game/minigame/Games.java), same rules, scores and texts.

const INK := UiTheme.INK
const CREAM := UiTheme.CREAM
const GOLD := UiTheme.GOLD
const LAVENDER := UiTheme.LAVENDER
const PINK := UiTheme.PINK


## Every texture the minigames draw. Loaded before the first draw: a texture first loaded inside
## _draw renders as a white box on the GL compatibility renderer.
const TEXTURES := ["items/postcard.png", "items/memory_page.png", "items/letter_two_sides.png",
	"items/lantern_paper.png", "ui/icon_heart.png", "items/sandwich.png", "items/honey.png",
	"items/strawberry.png", "items/mint.png", "props/lantern_post.png", "props/lantern_off.png",
	"ui/sparkle.png", "items/cat_plush.png", "props/spark.png", "items/symbol_flower.png",
	"items/symbol_book.png", "items/symbol_star.png", "items/symbol_moon.png"]
static var _held: Array = []


static func create(id: String) -> Minigame:
	if _held.is_empty():
		for path in TEXTURES:
			_held.append(Data.tex(path))
	match id:
		"v49_echo": return MemoryEcho.new()
		"bouquet": return Bouquet.new()
		"scrapbook": return Scrapbook.new()
		"photobooth": return Photobooth.new()
		"cooking": return Cooking.new()
		"lanterns": return Lanterns.new()
		"starmap": return StarMap.new()
		"pages", "quiet_pages", "v26_night_pages": return Pages.new()
		"claw": return Claw.new()
		"fishing": return Fishing.new()
		"starcatch": return StarCatch.new()
		"ringtoss": return RingToss.new()
		"pour": return Pour.new()
		"code", "quiet_cipher", "v26_night_compass": return CodeLock.new()
	return Photobooth.new()


# ============================================================ MERANGKAI BUKET
class Bouquet extends Minigame:
	const FLOWERS := ["Mawar", "Tulip", "Melati"]
	const COLORS := [Color(.87, .40, .59), Color(.95, .76, .38), Color(.92, .94, .95)]
	var chosen := [0, 0, 0, 0]
	var pattern: Array = []
	var message := ""
	var message_t := 0.0

	func start() -> void:
		pattern = [2, 0, 1, 2] if route == "sofia" else [0, 1, 2, 0]
		for i in 4:
			chosen[i] = (pattern[i] + i + 1) % 3

	func update(dt: float) -> void:
		super.update(dt)
		if message_t > 0:
			message_t -= dt

	func _start_x() -> float:
		return x + maxf(18, (w - 4 * 138) / 2.0)

	func tap(px: float, py: float) -> void:
		if finished:
			return
		var cy := y + h * .33
		for i in 4:
			if inside(px, py, _start_x() + i * 138 + 8, cy, 118, 180):
				chosen[i] = (chosen[i] + 1) % 3
				sfx("flower_pick")
				message = "Bunga ke-%d: %s" % [i + 1, FLOWERS[chosen[i]]]
				message_t = 1.0
				return
		if inside(px, py, x + w / 2 - 120, y + 20, 240, 60):
			submit()

	func submit() -> void:
		var matches := 0
		for i in 4:
			if chosen[i] == pattern[i]:
				matches += 1
		if matches == 4:
			score = 4; finished = true; result_text = "Buket cocok! Dua tangan, satu rangkaian yang indah."; sfx("quest_complete")
		else:
			message = "%d dari 4 bunga cocok. Periksa kartu pesanan!" % matches; message_t = 2.8; sfx("soft_wrong")

	func key(i: int) -> void:
		if i == 99:
			submit()
		elif i >= 0 and i < 4:
			chosen[i] = (chosen[i] + 1) % 3; sfx("page")

	func draw() -> void:
		var hint := "Pesanan: " + " • ".join(pattern.map(func(p): return FLOWERS[p]))
		text(hint, x + 10, y + h - 22, GOLD, .83, "center", w - 20)
		var cy := y + h * .33
		for i in 4:
			var cx := _start_x() + i * 138 + 8
			panel("panel", cx, cy, 118, 180)
			rect(cx + 52, cy + 27, 12, 92, GREEN, .75)
			for petal in 6:
				var ang := petal * TAU / 6.0
				rect(cx + 50 + cos(ang) * 17, cy + 118 + sin(ang) * 17, 17, 17, COLORS[chosen[i]])
			rect(cx + 56, cy + 124, 9, 9, GOLD)
			text(FLOWERS[chosen[i]], cx, cy + 163, INK, .76, "center", 118)
		panel("button", x + w / 2 - 120, y + 20, 240, 60)
		text("Cek buket", x + w / 2 - 120, y + 62, INK, .88, "center", 240)
		text(message if message_t > 0 else "Ketuk satu bunga untuk mengganti jenisnya", x, y + 114, LAVENDER, .77, "center", w)


# ============================================================ SCRAPBOOK KENANGAN
class Scrapbook extends Minigame:
	const MOMENTS := ["Plaza", "Memory Garden", "Kafe Senja", "Festival"]
	const ICONS := ["items/postcard.png", "items/memory_page.png", "items/letter_two_sides.png", "items/lantern_paper.png"]
	var order := [2, 0, 3, 1]
	var selected := -1
	var moves := 0
	var message := "Susun kenangan dari paling awal ke paling akhir."

	func start() -> void:
		if route == "sofia":
			order = [1, 3, 0, 2]

	func select(pos: int) -> void:
		if selected < 0:
			selected = pos; sfx("page"); return
		if selected != pos:
			var tmp = order[selected]; order[selected] = order[pos]; order[pos] = tmp
			moves += 1; sfx("paper_fold")
		selected = -1

	func submit() -> void:
		var good := 0
		for i in 4:
			if order[i] == i:
				good += 1
		if good == 4:
			score = maxi(1, 12 - moves); finished = true; result_text = "Album tersusun! %d kali menukar halaman." % moves; sfx("quest_complete")
		else:
			message = "%d dari 4 halaman sudah benar. Coba urutkan lagi." % good; sfx("soft_wrong")

	func _sx() -> float:
		return x + maxf(20, (w - 4 * 148) / 2.0)

	func tap(px: float, py: float) -> void:
		if finished:
			return
		var by := y + h * .34
		for i in 4:
			if inside(px, py, _sx() + i * 148, by, 136, 172):
				select(i); return
		if inside(px, py, x + w / 2 - 118, y + 22, 236, 56):
			submit()

	func key(i: int) -> void:
		if i == 99:
			submit()
		elif i >= 0 and i < 4:
			select(i)

	func draw() -> void:
		text("Urutan: Plaza → Memory Garden → Kafe Senja → Festival", x, y + h - 16, GOLD, .79, "center", w)
		var by := y + h * .34
		for i in 4:
			var bx := _sx() + i * 148
			panel("selected" if selected == i else "panel", bx, by, 136, 172)
			image(Data.tex(ICONS[order[i]]), bx + 38, by + 60, 60, 76)
			text(MOMENTS[order[i]], bx + 3, by + 38, INK, .72, "center", 130)
			text(str(i + 1) + (" • dipilih" if selected == i else ""), bx + 3, by + 156, Color("c99a2e"), .7, "center", 130)
		panel("button", x + w / 2 - 118, y + 22, 236, 56)
		text("Simpan album", x + w / 2 - 118, y + 62, INK, .85, "center", 236)
		text(message, x, y + 120, LAVENDER, .75, "center", w)


# ============================================================ PHOTOBOOTH
class Photobooth extends Minigame:
	var shots := 0
	var total := 3
	var cursor := 0.0
	var dir := 1.0
	var flash := 0.0
	var cool := 0.0
	var quality: Array = []

	func start() -> void:
		total = int(cfg.get("shots", 3))

	func update(dt: float) -> void:
		super.update(dt)
		if flash > 0:
			flash -= dt
		if cool > 0:
			cool -= dt; return
		if shots >= total:
			return
		cursor += dir * dt * (0.75 + shots * 0.18)
		if cursor > 1:
			cursor = 1; dir = -1
		elif cursor < 0:
			cursor = 0; dir = 1

	func tap(_px: float, _py: float) -> void:
		if shots >= total or cool > 0:
			return
		var d := absf(cursor - 0.5)
		var q := 3 if d < 0.06 else (2 if d < 0.16 else 1)
		quality.append(q); score += q; shots += 1; flash = 0.35; cool = 0.7
		sfx("sparkle" if q == 3 else "page")
		if shots >= total:
			finished = true
			result_text = "Foto sempurna! Kalian kompak sekali." if score >= 8 else ("Fotonya manis!" if score >= 5 else "Fotonya lucu-lucu. Kenangan tetap kenangan!")

	func key(_i: int) -> void:
		tap(0, 0)

	func draw() -> void:
		var fw := 150.0
		var fh := 120.0
		var gap := 20.0
		var fx0 := x + (w - (fw * total + gap * (total - 1))) / 2
		var fy := y + h - fh - 20
		for i in total:
			var fx := fx0 + i * (fw + gap)
			panel("dark", fx - 6, fy - 6, fw + 12, fh + 12)
			if i < quality.size():
				var q: int = quality[i]
				rect(fx, fy, fw, fh, Color(1, 0.93, 0.95))
				var ta := portrait("arland", "senang" if q == 3 else ("neutral" if q == 2 else "kaget"))
				var ts := portrait("sofia", "tertawa" if q == 3 else ("senang" if q == 2 else "kaget"))
				var ph := fh - 8
				var pw := ph * (ta.get_width() / float(ta.get_height()) if ta else 0.8)
				image(ta, fx + 4, fy + 4, pw * 0.92, ph); image(ts, fx + fw - pw * 0.92 - 4, fy + 4, pw * 0.92, ph)
				text("★★★" if q == 3 else ("★★" if q == 2 else "★"), fx, fy + 22, GOLD, 0.8, "center", fw)
			else:
				text("Foto %d" % (i + 1), fx, fy + fh / 2 + 10, CREAM, 0.9, "center", fw)
		var bx := x + 60
		var bw := w - 120
		var by := y + 120
		var bh := 34.0
		rect(bx, by, bw, bh, Color(0.3, 0.25, 0.4))
		rect(bx + bw * 0.34, by, bw * 0.32, bh, GREEN, 0.55)
		rect(bx + bw * 0.44, by, bw * 0.12, bh, GOLD, 0.9)
		image(Data.tex("ui/icon_heart.png"), bx + bw * cursor - 22, by - 6, 44, 44)
		text(("Ketuk saat hati di tengah! (%d/%d)" % [shots + 1, total]) if shots < total else "Selesai!", x, by + 80, CREAM, 0.95, "center", w)
		if flash > 0:
			rect(x - 400, y - 400, w + 800, h + 800, Color.WHITE, minf(1.0, flash * 2.0))


# ============================================================ COOKING
class Cooking extends Minigame:
	var steps: Array = []
	var idx := 0
	var needle := 0.0
	var speed := 1.1
	var zone := 0.5
	var zone_w := 0.22
	var msg_t := 0.0
	var msg := ""
	var results: Array = []
	var rng := RandomNumberGenerator.new()

	func start() -> void:
		rng.seed = 7
		steps = cfg.get("steps", [])
		if steps.is_empty():
			steps = ["Potong", "Oles", "Tata"]
		new_zone()

	func new_zone() -> void:
		zone = 0.25 + rng.randf() * 0.5; zone_w = maxf(0.12, 0.24 - idx * 0.02); speed = 0.9 + idx * 0.15

	func update(dt: float) -> void:
		super.update(dt)
		if msg_t > 0:
			msg_t -= dt
		if not finished:
			needle = (sin(t * speed * 2.6) + 1.0) / 2.0

	func tap(_px: float, _py: float) -> void:
		if finished or msg_t > 0.6:
			return
		var good := absf(needle - zone) <= zone_w / 2
		results.append(good)
		if good:
			score += 1
		sfx("sparkle" if good else "soft_wrong")
		msg = "Pas sekali!" if good else "Sedikit meleset, tidak apa-apa!"
		msg_t = 0.9
		idx += 1
		if idx >= steps.size():
			finished = true
			result_text = "Sempurna! Wangi madu ke mana-mana." if score == steps.size() else ("Enak! Sedikit berantakan, tapi enak." if score >= steps.size() / 2 else "Agak gosong... tapi dibuat bareng, jadi tetap spesial.")
		else:
			new_zone()

	func key(_i: int) -> void:
		tap(0, 0)

	func draw() -> void:
		var ly := y + h - 40
		for i in steps.size():
			var c: Color = (GREEN if results[i] else RED) if i < results.size() else (GOLD if i == idx else CREAM)
			var mark: String = ("✓ " if results[i] else "✕ ") if i < results.size() else ("▶ " if i == idx else "• ")
			text(mark + str(steps[i]), x + 40, ly - i * 34, c, 0.9)
		var icons := ["items/sandwich.png", "items/honey.png", "items/strawberry.png", "items/mint.png", "items/sandwich.png"]
		if idx < steps.size():
			image(Data.tex(icons[idx % icons.size()]), x + w - 200, y + h - 200, 140, 140)
		var gx := x + 60
		var gw := w - 120
		var gy := y + 110
		var gh := 36.0
		rect(gx, gy, gw, gh, Color(0.3, 0.25, 0.4))
		if not finished:
			rect(gx + gw * (zone - zone_w / 2), gy, gw * zone_w, gh, GREEN, 0.85)
		rect(gx + gw * needle - 3, gy - 10, 6, gh + 20, Color.WHITE)
		text("Selesai!" if finished else (msg if msg_t > 0 else "Ketuk saat jarum di zona hijau"), x, gy + 80, CREAM, 0.95, "center", w)


# ============================================================ LANTERNS (lights out)
class Lanterns extends Minigame:
	var n := 3
	var on: Array = []
	var moves := 0
	var total_moves := 0
	var board := 0
	var solved_t := -1.0
	var boards: Array = []

	func start() -> void:
		if boards.is_empty():
			for o in cfg.get("boards", []):
				if o is Array:
					boards.append(o.map(func(v): return str(v)))
			if boards.is_empty():
				boards.append(cfg.get("start", ["0", "0", "0", "0"]).map(func(v): return str(v)))
		var s: Array = boards[mini(board, boards.size() - 1)]
		n = maxi(2, int(round(sqrt(s.size()))))
		on = []
		for i in n * n:
			on.append(i < s.size() and str(s[i]).begins_with("1"))

	func cell() -> float:
		return minf((h - 120) / n, 120)

	func gx() -> float:
		return x + (w - cell() * n) / 2

	func gy() -> float:
		return y + 80

	func tap(px: float, py: float) -> void:
		if finished or solved_t >= 0:
			return
		var c := cell()
		if inside(px, py, x + w - 190, y + 10, 170, 56):
			start(); moves = 0; sfx("page"); return
		if px < gx() or py < gy():
			return
		var cx := int((px - gx()) / c)
		var cy := int((py - gy()) / c)
		if cx < 0 or cy < 0 or cx >= n or cy >= n:
			return
		for d in [Vector2i(0, 0), Vector2i(-1, 0), Vector2i(1, 0), Vector2i(0, -1), Vector2i(0, 1)]:
			toggle(cx + d.x, cy + d.y)
		moves += 1; sfx("page")
		if not on.has(false):
			solved_t = 0.8; sfx("sparkle")

	func toggle(cx: int, cy: int) -> void:
		if cx >= 0 and cy >= 0 and cx < n and cy < n:
			on[cy * n + cx] = not on[cy * n + cx]

	func key(i: int) -> void:
		if i >= 0 and i < 3:
			tap(gx() + cell() * (i + 0.5), gy() + cell() * 1.5)

	func update(dt: float) -> void:
		super.update(dt)
		if solved_t >= 0:
			solved_t -= dt
			if solved_t < 0:
				total_moves += moves; board += 1
				if board >= boards.size():
					finished = true; score = maxi(1, 60 - total_moves); result_text = "Semua lentera menyala dalam %d langkah." % total_moves
				else:
					moves = 0; start()

	func draw() -> void:
		var c := cell()
		for i in n * n:
			var cx := gx() + (i % n) * c
			var cy := gy() + (i / n) * c
			panel("dark", cx + 6, cy + 6, c - 12, c - 12)
			var tex := Data.tex("props/lantern_post.png" if on[i] else "props/lantern_off.png")
			if tex == null:
				continue
			var th := c - 26
			var tw := th * tex.get_width() / float(tex.get_height())
			if on[i]:
				rect(cx + 14, cy + 14, c - 28, c - 28, GOLD, 0.25 + 0.1 * sin(t * 3 + i))
			image(tex, cx + (c - tw) / 2, cy + 13, tw, th)
		panel("button", x + w - 190, y + 10, 170, 56)
		text("Ulang", x + w - 190, y + 48, INK, 0.9, "center", 170)
		text("Altar %d/%d   •   Langkah: %d" % [board + 1, boards.size(), moves], x + 20, y + 48, CREAM, 0.9)


# ============================================================ STAR MAP
class StarMap extends Minigame:
	const DIRS := ["utara", "timur", "selatan", "barat", "timur laut", "barat daya", "barat laut", "tenggara"]
	const POS := [Vector2(0, 1), Vector2(1, 0), Vector2(0, -1), Vector2(-1, 0), Vector2(0.72, 0.72), Vector2(-0.72, -0.72), Vector2(-0.72, 0.72), Vector2(0.72, -0.72)]
	const COLS := ["ungu", "emas", "biru", "merah muda"]
	var stars: Array = []   # [dir, colour, ring]
	var order: Array = []
	var step := 0
	var mistakes := 0
	var wrong_t := 0.0
	var done_t := -1.0
	var lit: Array = []

	func start() -> void:
		for o in cfg.get("order", []):
			if o is Array and o.size() >= 2:
				order.append([str(o[0]), str(o[1])])
		if order.is_empty():
			order = [["timur", "ungu"], ["utara", "emas"], ["barat", "biru"]]
		var r := RandomNumberGenerator.new(); r.seed = 5
		for d in DIRS.size():
			var correct = null
			for o in order:
				if o[0] == DIRS[d]:
					correct = o[1]
			var cols := COLS.duplicate()
			for i in range(cols.size() - 1, 0, -1):
				var j := r.randi_range(0, i)
				var tmp = cols[i]; cols[i] = cols[j]; cols[j] = tmp
			var c1: String = correct if correct != null else cols[0]
			var c2: String = cols[1] if cols[0] == c1 else cols[0]
			stars.append([DIRS[d], c1, "0"]); stars.append([DIRS[d], c2, "1"])

	func pos(i: int) -> Vector2:
		var s: Array = stars[i]
		var d := DIRS.find(s[0])
		var c := Vector2(x + w / 2, y + h / 2 + 10)
		var R := minf(w, h) * 0.36
		var k := 1.0 if s[2] == "0" else 0.62
		return c + POS[d] * R * k

	func col(c: String) -> Color:
		match c:
			"ungu": return Color(0.72, 0.55, 1)
			"emas": return Color(1, 0.84, 0.4)
			"biru": return Color(0.45, 0.7, 1)
		return Color(1, 0.6, 0.75)

	func tap(px: float, py: float) -> void:
		if finished or done_t >= 0:
			return
		for i in stars.size():
			if pos(i).distance_squared_to(Vector2(px, py)) < 30 * 30:
				var s: Array = stars[i]
				var want: Array = order[step]
				if s[0] == want[0] and s[1] == want[1]:
					lit.append(i); step += 1; sfx("sparkle")
					if step >= order.size():
						done_t = 1.0
				else:
					mistakes += 1; step = 0; lit.clear(); wrong_t = 0.8; sfx("soft_wrong")
				return

	func update(dt: float) -> void:
		super.update(dt)
		if wrong_t > 0:
			wrong_t -= dt
		if done_t >= 0:
			done_t -= dt
			if done_t < 0:
				finished = true; score = maxi(1, 3 - mistakes); result_text = "Rasi kecil terbentuk di langit desa."

	func draw() -> void:
		rect(x, y, w, h, Color(0.1, 0.12, 0.26))
		var c := Vector2(x + w / 2, y + h / 2 + 10)
		var R := minf(w, h) * 0.36
		var lab := ["U", "T", "S", "B"]
		for d in 4:
			text(lab[d], c.x + POS[d].x * (R + 34) - 20, c.y + POS[d].y * (R + 34) + 10, LAVENDER, 0.9, "center", 40)
		for i in range(lit.size() - 1):
			var p0 := pos(lit[i])
			var p1 := pos(lit[i + 1])
			for k in 21:
				var f := k / 20.0
				rect(lerpf(p0.x, p1.x, f) - 2, lerpf(p0.y, p1.y, f) - 2, 4, 4, GOLD, 0.9)
		var st := Data.tex("ui/sparkle.png")
		for i in stars.size():
			var p := pos(i)
			var s := 44.0 if lit.has(i) else 30 + 4 * sin(t * 2 + i)
			rect(p.x - s / 4, p.y - s / 4, s / 2, s / 2, col(stars[i][1]), 1.0 if lit.has(i) else 0.8)
			image(st, p.x - s / 2, p.y - s / 2, s, s)
		text("Belum tepat. Ulangi dari bintang pertama." if wrong_t > 0 else "Kompas: timur → utara → barat   •   Lentera: ungu → emas → biru",
				x, y + 40, RED if wrong_t > 0 else CREAM, 0.8, "center", w)


# ============================================================ PAGES (urutkan kenangan)
class Pages extends Minigame:
	var correct: Array = []
	var deck: Array = []
	var placed: Array = []
	var wrong_t := 0.0
	var done_t := -1.0
	var mistakes := 0

	func start() -> void:
		correct = cfg.get("pages", [])
		if correct.is_empty():
			correct = ["Satu", "Dua", "Tiga"]
		deck = correct.duplicate()
		var r := RandomNumberGenerator.new(); r.seed = 3
		for i in range(deck.size() - 1, 0, -1):
			var j := r.randi_range(0, i)
			var tmp = deck[i]; deck[i] = deck[j]; deck[j] = tmp
		if deck == correct and deck.size() > 1:
			deck.reverse()

	func cw() -> float:
		return (w - 60) / 3.0

	func rows() -> int:
		return (correct.size() + 2) / 3

	func card_y(i: int) -> float:
		return y + 20 + (rows() - 1 - i / 3) * 62

	func tap(px: float, py: float) -> void:
		if finished or done_t >= 0:
			return
		for i in deck.size():
			var bx := x + 20 + (i % 3) * (cw() + 10)
			if inside(px, py, bx, card_y(i), cw(), 54):
				var p = deck[i]
				if p == correct[placed.size()]:
					placed.append(p); deck.remove_at(i); sfx("page")
					if placed.size() == correct.size():
						done_t = 0.8; sfx("sparkle")
				else:
					wrong_t = 0.7; mistakes += 1; sfx("soft_wrong")
				return

	func update(dt: float) -> void:
		super.update(dt)
		if wrong_t > 0:
			wrong_t -= dt
		if done_t >= 0:
			done_t -= dt
			if done_t < 0:
				finished = true; score = maxi(1, 6 - mistakes); result_text = "Semua halaman kembali ke tempatnya."

	func draw() -> void:
		var sy := y + h - 56
		for i in correct.size():
			var sx := x + 20 + (i % 3) * (cw() + 10)
			var syy := sy - (i / 3) * 48
			panel("dark", sx, syy, cw(), 44)
			text("%d. %s" % [i + 1, placed[i] if i < placed.size() else "..."], sx + 14, syy + 32, GOLD if i < placed.size() else LAVENDER, 0.72, "left", cw() - 20)
		var off := sin(wrong_t * 50) * 6 if wrong_t > 0 else 0.0
		for i in deck.size():
			var bx := x + 20 + (i % 3) * (cw() + 10) + off
			var by := card_y(i)
			panel("button", bx, by, cw(), 54)
			text(str(deck[i]), bx + 8, by + 38, INK, 0.74, "center", cw() - 16)
		text("Pilih halaman berikutnya sesuai urutan kenangan", x, y + 30 + rows() * 62 + 34, CREAM, 0.85, "center", w)


# ============================================================ CLAW
class Claw extends Minigame:
	var claw_x := 0.1
	var dir := 1.0
	var drop := -1.0
	var plush_x := 0.5
	var won := false

	func start() -> void:
		plush_x = 0.2 + randf() * 0.6

	func update(dt: float) -> void:
		super.update(dt)
		if finished:
			return
		if drop < 0:
			claw_x += dir * dt * 0.55
			if claw_x > 0.95:
				claw_x = 0.95; dir = -1
			if claw_x < 0.05:
				claw_x = 0.05; dir = 1
		else:
			drop += dt
			if drop > 1.3:
				finished = true; score = 1 if won else 0
				result_text = "Dapat boneka!" if won else "Bonekanya lepas... coba lagi lain kali."

	func tap(_px: float, _py: float) -> void:
		if drop >= 0 or finished:
			return
		drop = 0; won = absf(claw_x - plush_x) < 0.06; sfx("sparkle" if won else "page")

	func key(_i: int) -> void:
		tap(0, 0)

	func draw() -> void:
		var bx := x + 60
		var bw := w - 120
		var top := y + h - 30
		var floor_y := y + 70
		rect(bx, floor_y, bw, top - floor_y, Color(0.8, 0.92, 0.98), 0.35)
		var cxp := bx + bw * claw_x
		var depth := 0.0 if drop < 0 else minf(1.0, drop / 0.6) * (top - floor_y - 70)
		if drop > 0.6 and won:
			depth = (top - floor_y - 70) * maxf(0, 1.0 - (drop - 0.6) / 0.7)
		rect(cxp - 2, top - 20 - depth, 4, 20 + depth, INK)
		rect(cxp - 18, top - 34 - depth, 36, 14, LAVENDER)
		var pyy := top - 34 - depth - 44 if (won and drop > 0.6) else floor_y
		image(Data.tex("items/cat_plush.png"), bx + bw * plush_x - 28, pyy, 56, 56)
		text("Ketuk saat capit tepat di atas boneka" if drop < 0 else ("Kena!" if won else "..."), x, y + 50, CREAM, 0.9, "center", w)


# ============================================================ FISHING
class Fishing extends Minigame:
	const NAMES := ["Ikan Mas", "Nila", "Mujair", "Lele", "Gurami", "Koi Danau", "Ikan Pelangi", "Ikan Bintang"]
	const WEIGHT := [22, 20, 18, 14, 11, 8, 5, 2]
	var phase := 0
	var wait := 0.0
	var bite := 0.0
	var fish := 0.5
	var fdir := 1.0
	var fspeed := 0.5
	var hook_w := 0.18
	var species := 0

	func start() -> void:
		var r := randf() * 100
		var acc := 0.0
		for i in NAMES.size():
			acc += WEIGHT[i]
			if r <= acc:
				species = i
				break
		fspeed = 0.45 + species * 0.12; hook_w = maxf(0.1, 0.22 - species * 0.015)
		wait = 1.2 + randf() * 2.2

	func update(dt: float) -> void:
		super.update(dt)
		if finished:
			return
		if phase == 0:
			wait -= dt
			if wait <= 0:
				phase = 1; bite = 0.9; sfx("page")
		elif phase == 1:
			bite -= dt
			if bite <= 0:
				phase = 0; wait = 1.0 + randf() * 2.0
		else:
			fish += fdir * fspeed * dt * (1.0 + 0.4 * sin(t * 3.0))
			if fish > 0.97:
				fish = 0.97; fdir = -1
			if fish < 0.03:
				fish = 0.03; fdir = 1
			if randf() < dt * 0.8:
				fdir = -fdir

	func tap(_px: float, _py: float) -> void:
		if finished:
			return
		if phase == 0:
			sfx("soft_wrong"); wait += 0.6; return
		if phase == 1:
			phase = 2; return
		var good := absf(fish - 0.5) < hook_w / 2
		finished = true; score = species + 1 if good else 0
		sfx("sparkle" if good else "soft_wrong")
		result_text = ("Dapat %s!%s" % [NAMES[species], " Langka sekali!" if species >= 6 else ""]) if good else "Ikannya lepas. Sabar, coba lagi."

	func key(_i: int) -> void:
		tap(0, 0)

	func draw() -> void:
		rect(x, y, w, h * 0.55, Color(0.35, 0.6, 0.78))
		for i in 18:
			var wx := x + fmod(i * 0.37 + t * 0.03, 1.0) * w
			rect(wx, y + 30 + (i * 41) % int(h * 0.5), 18, 2, Color.WHITE, 0.4)
		var bx := x + w / 2
		var by := y + h * 0.42 + (sin(t * 30) * 6 if phase == 1 else sin(t * 2) * 3)
		rect(bx - 1, by + 16, 2, h * 0.55 - (by - y) + 40, INK, 0.8)
		rect(bx - 8, by, 16, 16, RED); rect(bx - 8, by + 8, 16, 8, Color.WHITE)
		if phase == 2:
			var gx := x + 60
			var gw := w - 120
			var gy := y + h * 0.62
			var gh := 34.0
			rect(gx, gy, gw, gh, Color(0.3, 0.25, 0.4))
			rect(gx + gw * (0.5 - hook_w / 2), gy, gw * hook_w, gh, GREEN, 0.85)
			rect(gx + gw * fish - 14, gy + 6, 28, gh - 12, GOLD)
		var msg: String = ["Tunggu pelampungnya bergerak...", "Ada yang menarik! KETUK sekarang!", "Ketuk saat ikan (kuning) di zona hijau!"][phase]
		text(msg, x, y + h - 20, GOLD if phase == 1 else CREAM, 1.0, "center", w)


# ============================================================ HUJAN BINTANG
class StarCatch extends Minigame:
	var stars: Array = []    # {x, y, v, gold}
	var basket := 0.5
	var target := 0.5
	var spawn := 0.0
	var time := 20.0
	var caught := 0
	var missed := 0

	func start() -> void:
		time = float(cfg.get("seconds", 20))

	func update(dt: float) -> void:
		super.update(dt)
		if finished:
			return
		time -= dt
		if time <= 0:
			finished = true; score = caught
			result_text = ("Hujan bintang milikmu! %d bintang." % caught) if caught >= 25 else (("Tangkapan bagus: %d bintang." % caught) if caught >= 15 else "%d bintang tertangkap. Lumayan!" % caught)
			return
		var d := target - basket
		basket += signf(d) * minf(absf(d), dt * 1.6)
		spawn -= dt
		if spawn <= 0:
			stars.append({"x": 0.05 + randf() * 0.9, "y": 1.0, "v": 0.32 + randf() * 0.25 + (20.0 - time) * 0.012, "gold": randf() < 0.12})
			spawn = 0.45 + randf() * 0.35
		for i in range(stars.size() - 1, -1, -1):
			var s: Dictionary = stars[i]
			s.y -= s.v * dt
			if s.y < 0.1 and s.y > 0.02 and absf(s.x - basket) < 0.08:
				caught += 3 if s.gold else 1; sfx("sparkle" if s.gold else "page"); stars.remove_at(i)
			elif s.y < 0:
				missed += 1; stars.remove_at(i)

	func tap(px: float, _py: float) -> void:
		if w > 0:
			target = clampf((px - x - 40) / (w - 80), 0.04, 0.96)

	func key(i: int) -> void:
		target = clampf(basket - 0.25 if i == 0 else (basket + 0.25 if i == 2 else basket), 0.04, 0.96)

	func draw() -> void:
		var bx := x + 40
		var bw := w - 80
		var by := y + 30
		var bh := h - 70
		rect(bx, by, bw, bh, Color(0.12, 0.14, 0.32))
		for i in 26:
			rect(bx + fmod(i * 0.618, 1.0) * bw, by + fmod(i * 0.377 + 0.2, 1.0) * bh, 2, 2, Color.WHITE, 0.25 + 0.25 * sin(t * 2 + i))
		var st := Data.tex("props/spark.png")
		for s in stars:
			var sz := 38.0 if s.gold else 28.0
			image(st, bx + bw * s.x - sz / 2, by + bh * s.y - sz / 2, sz, sz)
			if s.gold:
				rect(bx + bw * s.x - 3, by + bh * s.y - 3, 6, 6, GOLD)
		var cx := bx + bw * basket
		rect(cx - bw * 0.08, by + 6, bw * 0.16, 22, LAVENDER); rect(cx - bw * 0.08, by + 24, bw * 0.16, 5, GOLD)
		text("Bintang: %d   Waktu: %d" % [caught, int(ceil(maxf(0, time)))], x, y + h - 6, CREAM, 0.95, "center", w)
		text("Ketuk kiri/kanan layar untuk menggeser keranjang (tombol 1 / 3)", x, y + 22, LAVENDER, 0.7, "center", w)


# ============================================================ LEMPAR GELANG
class RingToss extends Minigame:
	var throws_left := 5
	var hits := 0
	var bottle := 0
	var power := 0.0
	var dir := 1.0
	var anim := -1.0
	var last_hit := false
	const ZONE := [0.25, 0.5, 0.75]

	func start() -> void:
		throws_left = int(cfg.get("throws", 5)); bottle = randi() % 3

	func update(dt: float) -> void:
		super.update(dt)
		if finished:
			return
		if anim >= 0:
			anim += dt
			if anim > 0.9:
				anim = -1
				if throws_left <= 0:
					finished = true; score = hits
					result_text = ("Jago! %d gelang masuk." % hits) if hits >= 4 else (("%d gelang masuk. Dapat hadiah!" % hits) if hits >= 2 else "%d gelang masuk. Masih dapat hadiah hiburan!" % hits)
				else:
					bottle = randi() % 3
			return
		power += dir * dt * (0.8 + (5 - throws_left) * 0.1)
		if power > 1:
			power = 1; dir = -1
		elif power < 0:
			power = 0; dir = 1

	func tap(_px: float, _py: float) -> void:
		if finished or anim >= 0 or throws_left <= 0:
			return
		last_hit = absf(power - ZONE[bottle]) < 0.07
		if last_hit:
			hits += 1
		throws_left -= 1; anim = 0; sfx("sparkle" if last_hit else "soft_wrong")

	func key(_i: int) -> void:
		tap(0, 0)

	func draw() -> void:
		var bx := x + 60
		var bw := w - 120
		var gy := y + 70
		for i in 3:
			var cx: float = bx + bw * ZONE[i]
			rect(cx - 14, gy + 70, 28, 90, Color(0.55, 0.85, 0.7) if i == bottle else Color(0.5, 0.6, 0.7), 1.0 if i == bottle else 0.5)
			rect(cx - 6, gy + 160, 12, 26, GREEN if i == bottle else LAVENDER, 0.8)
		rect(bx, gy, bw, 30, Color(0.3, 0.25, 0.4))
		rect(bx + bw * (ZONE[bottle] - 0.07), gy, bw * 0.14, 30, GREEN, 0.8)
		rect(bx + bw * power - 4, gy - 6, 8, 42, GOLD)
		if anim >= 0:
			text("Masuk!" if last_hit else "Meleset!", x, y + h - 60, GOLD if last_hit else CREAM, 0.5, "center", w, "title")
		text("Gelang: %d   Masuk: %d   (ketuk saat garis emas di zona hijau)" % [throws_left, hits], x, y + h - 8, CREAM, 0.85, "center", w)


# ============================================================ TUANG TEH
class Pour extends Minigame:
	var cups := 3
	var cup := 0
	var fill := 0.0
	var speed := 0.35
	var line := 0.7
	var pouring := true
	var pause := -1.0
	var total := 0
	var marks: Array = []

	func start() -> void:
		cups = int(cfg.get("cups", 3)); next()

	func next() -> void:
		fill = 0; line = 0.6 + randf() * 0.25; speed = 0.35 + cup * 0.12; pouring = true

	func update(dt: float) -> void:
		super.update(dt)
		if finished:
			return
		if pause >= 0:
			pause += dt
			if pause > 0.8:
				pause = -1; cup += 1
				if cup >= cups:
					finished = true; score = total
					result_text = "Tuangan sempurna, seperti barista!" if total >= cups * 3 - 1 else ("Tehnya pas dan hangat." if total >= cups * 2 else "Agak tumpah sedikit, tapi tetap enak.")
				else:
					next()
			return
		if pouring:
			fill += dt * speed
			if fill >= 1.0:
				fill = 1.0; stop()

	func stop() -> void:
		pouring = false
		var d := absf(fill - line)
		var q := 3 if d < 0.03 else (2 if d < 0.08 else 1)
		marks.append(q); total += q; pause = 0; sfx("sparkle" if q == 3 else "page")

	func tap(_px: float, _py: float) -> void:
		if not finished and pouring and pause < 0:
			stop()

	func key(_i: int) -> void:
		tap(0, 0)

	func draw() -> void:
		var cw := 140.0
		var ch := 200.0
		var cx := x + (w - cw) / 2
		var cy := y + 50
		var tea := Color(0.78, 0.5, 0.25)
		rect(cx - 8, cy - 8, cw + 16, ch + 16, CREAM, 0.9)
		rect(cx, cy, cw, ch, Color(0.95, 0.95, 0.98))
		rect(cx, cy, cw, ch * fill, tea)
		rect(cx - 16, cy + ch * line - 2, cw + 32, 4, RED)
		if pouring:
			rect(cx + cw / 2 - 4, cy + ch * fill, 8, ch * (1.0 - fill) + 40, tea, 0.9)
		var sb := ""
		for i in cups:
			sb += (["★ ", "★★ ", "★★★ "][marks[i] - 1]) if i < marks.size() else "○ "
		text("Gelas %d/%d   %s" % [mini(cups, cup + 1), cups, sb], x, y + h - 8, GOLD, 0.9, "center", w)
		text("Ketuk untuk berhenti menuang tepat di garis merah", x, y + 24, CREAM, 0.8, "center", w)


# ============================================================ PETI KATA SANDI
class CodeLock extends Minigame:
	const ICONS := ["items/symbol_flower.png", "items/symbol_book.png", "items/symbol_star.png", "items/symbol_moon.png"]
	const NAMES := ["Bunga", "Buku", "Bintang", "Bulan"]
	var dial: Array = []
	var answer: Array = []
	var tries := 0
	var shake := 0.0
	var ok_t := -1.0
	var msg := ""

	func start() -> void:
		answer = cfg.get("answer", [0, 1, 2]).map(func(v): return int(v))
		dial = []
		for _i in answer.size():
			dial.append(0)

	func dial_x(i: int) -> float:
		var dw := 130.0
		var gap := 26.0
		var tot := dial.size() * dw + (dial.size() - 1) * gap
		return x + (w - tot) / 2 + i * (dw + gap)

	func update(dt: float) -> void:
		super.update(dt)
		if shake > 0:
			shake -= dt
		if ok_t >= 0:
			ok_t += dt
			if ok_t > 1.1:
				finished = true; score = 1; result_text = "Klik! Peti terbuka."

	func tap(px: float, py: float) -> void:
		if finished or ok_t >= 0:
			return
		var dy := y + h * 0.42
		for i in dial.size():
			if inside(px, py, dial_x(i), dy, 130, 150):
				dial[i] = (dial[i] + 1) % ICONS.size(); sfx("page"); return
		if inside(px, py, x + w / 2 - 110, y + 40, 220, 70):
			check()

	func key(i: int) -> void:
		if i >= 0 and i < dial.size():
			dial[i] = (dial[i] + 1) % ICONS.size(); sfx("page")
		else:
			check()

	func check() -> void:
		if dial == answer:
			ok_t = 0; sfx("sparkle"); msg = "Benar!"
		else:
			tries += 1; shake = 0.4; sfx("soft_wrong")
			msg = "Belum tepat. Petunjuknya terukir di batu-batu sekitar sini." if tries >= 3 else "Belum tepat."

	func draw() -> void:
		var dy := y + h * 0.42
		var off := sin(shake * 60) * 6 if shake > 0 else 0.0
		text(str(cfg.get("hint", "Putar simbol, lalu tekan Buka.")), x, y + h - 20, LAVENDER, 0.8, "center", w)
		for i in dial.size():
			var dx := dial_x(i) + off
			rect(dx, dy, 130, 150, GREEN if ok_t >= 0 else Color(0.32, 0.26, 0.44))
			rect(dx + 6, dy + 6, 118, 138, Color(0.96, 0.92, 0.86))
			image(Data.tex(ICONS[dial[i]]), dx + 33, dy + 46, 64, 64)
			text(NAMES[dial[i]], dx, dy + 36, INK, 0.75, "center", 130)
			text("▲ ketuk", dx, dy + 172, CREAM, 0.7, "center", 130)
		rect(x + w / 2 - 110, y + 40, 220, 70, PINK)
		text("Buka", x + w / 2 - 110, y + 88, CREAM, 1.0, "center", 220)
		if msg != "":
			text(msg, x, y + 150, GOLD if ok_t >= 0 else CREAM, 0.85, "center", w)


# ============================================================ MEMORY ECHO (v4.9)
class MemoryEcho extends Minigame:
	const SYMBOLS := ["Bunga", "Buku", "Bintang", "Bulan"]
	const ICONS := ["items/symbol_flower.png", "items/symbol_book.png", "items/symbol_star.png", "items/symbol_moon.png"]
	var patterns: Array = []
	var stage := 0
	var index := 0
	var errors := 0
	var preview_time := 0.0
	var preview := false
	var feedback := ""

	func start() -> void:
		var raw = cfg.get("patterns", {}).get(route)
		patterns = []
		if raw is Array:
			for st in raw:
				if st is Array:
					patterns.append(st.map(func(v): return clampi(int(v), 0, 3)))
		if patterns.is_empty():
			patterns = [[0, 1], [2, 3]]
		stage = 0; index = 0; errors = 0
		begin_preview()

	func begin_preview() -> void:
		preview = true; preview_time = 0; index = 0
		feedback = "Amati cahaya yang menyala, lalu ulangi urutannya."

	func update(dt: float) -> void:
		super.update(dt)
		if preview:
			preview_time += clampf(dt, 0, 0.1)
			if preview_time >= patterns[stage].size() * 0.8 + 0.7:
				preview = false; feedback = "Giliranmu: pilih simbol sesuai urutan."

	func lit_index() -> int:
		if not preview or preview_time < 0.3:
			return -1
		var tt := preview_time - 0.3
		var n := int(tt / 0.8)
		if n < 0 or n >= patterns[stage].size() or fmod(tt, 0.8) > 0.56:
			return -1
		return patterns[stage][n]

	func btn_size() -> float:
		return minf(138.0, (w - 90.0) / 4.0)

	func btn_x(n: int) -> float:
		var size := btn_size()
		var gap := minf(26.0, (w - size * 4) / 5.0)
		return x + (w - 4 * size - 3 * gap) / 2 + n * (size + gap)

	func choose(button: int) -> void:
		if finished or preview or button < 0 or button > 3:
			return
		if patterns[stage][index] != button:
			errors += 1; sfx("soft_wrong", 0.6)
			feedback = "Belum tepat. Coba dengarkan urutannya lagi."
			begin_preview()
			return
		sfx("page", 0.5)
		index += 1
		if index == patterns[stage].size():
			stage += 1
			if stage >= patterns.size():
				finished = true; score = maxi(1, 5 - errors)
				result_text = "Semua gema selaras! Kenangan baru terbuka." if errors == 0 else "Gema tersambung! Kalian menemukan ritme kenangan."
				sfx("sparkle", 0.7)
			else:
				begin_preview()
		else:
			feedback = "Bagus! %d/%d nada." % [index, patterns[stage].size()]

	func tap(px: float, py: float) -> void:
		var size := btn_size()
		var by := y + h * 0.36
		for i in 4:
			if inside(px, py, btn_x(i), by, size, size + 15):
				choose(i); return

	func key(i: int) -> void:
		choose(i)

	func draw() -> void:
		text("TAHAP %d/%d  •  %s" % [mini(stage + 1, patterns.size()), patterns.size(), "DENGARKAN" if preview else "ULANGI"], x, y + h - 28, GOLD, 0.95, "center", w)
		text(feedback, x, y + h - 85, CREAM, 0.78, "center", w)
		var size := btn_size()
		var by := y + h * 0.36
		var lit := lit_index()
		for i in 4:
			var bx := btn_x(i)
			rect(bx, by, size, size + 15, GOLD if lit == i else Color(.34, .28, .45))
			rect(bx + 5, by + 5, size - 10, size + 5, Color(.95, .92, .90))
			image(Data.tex(ICONS[i]), bx + (size - 66) / 2, by + 38, 66, 66)
			text("%d. %s" % [i + 1, SYMBOLS[i]], bx, by + 23, INK, 0.65, "center", size)
		text("Perhatikan setiap cahaya. Tunggu sampai giliranmu." if preview else "Ketuk simbol atau gunakan tombol 1–4.", x, y + 75, LAVENDER, 0.72, "center", w)
		if errors > 0:
			text("Mengulang: %d" % errors, x, y + 37, GOLD, 0.65, "center", w)
