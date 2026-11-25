class_name WorldClock
extends RefCounted
## World clock (port of logic/WorldClock.java). Day runs 06:00 to 02:00 (26*60).
## Weather is deterministic per day number, identical to the Java build.

const DAY_START := 6 * 60
const DAY_END := 26 * 60
const CERAH := "cerah"
const BERAWAN := "berawan"
const HUJAN := "hujan"
const BERANGIN := "berangin"
const DAYS := ["Sabtu", "Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat"]


static func day_name(day: int) -> String:
	return DAYS[posmod(day - 1, 7)]


static func hhmm(minute: int) -> String:
	var m := posmod(minute, 24 * 60)
	return "%02d:%02d" % [m / 60, m % 60]


static func hour(minute: int) -> int:
	return posmod(minute, 24 * 60) / 60


## Java: long h = (day*2654435761L) ^ 0x5bd1e995L; h ^= h>>>13; h *= 0x5bd1e995L; h ^= h>>>15; floorMod(h,100)
## GDScript ints are 64-bit two's complement and wrap on overflow like Java longs; >>> is emulated with a mask.
static func weather(day: int) -> String:
	if day <= 2:
		return CERAH
	var h: int = (day * 2654435761) ^ 0x5bd1e995
	h ^= _ushr(h, 13)
	h *= 0x5bd1e995
	h ^= _ushr(h, 15)
	var r := posmod(h, 100)
	if r < 14:
		return HUJAN
	if r < 34:
		return BERAWAN
	if r < 44:
		return BERANGIN
	return CERAH


static func _ushr(v: int, n: int) -> int:
	return (v >> n) & ((1 << (64 - n)) - 1)


## Light tint [r, g, b, alpha] for a minute of the day. alpha 0 = plain daylight.
static func light(minute: int) -> Array:
	var m := float(minute)
	if m < 7 * 60:
		return _mix([1.0, 0.72, 0.55, 0.14], [1.0, 0.85, 0.7, 0.0], (m - 5 * 60) / 120.0)
	if m < 16 * 60:
		return [1.0, 1.0, 1.0, 0.0]
	if m < 18 * 60:
		return _mix([1.0, 0.78, 0.5, 0.0], [1.0, 0.6, 0.32, 0.18], (m - 16 * 60) / 120.0)
	if m < 19.5 * 60:
		return _mix([1.0, 0.6, 0.32, 0.18], [0.18, 0.2, 0.42, 0.3], (m - 18 * 60) / 90.0)
	if m < 23 * 60:
		return [0.11, 0.14, 0.32, 0.32]
	return _mix([0.11, 0.14, 0.32, 0.32], [0.06, 0.07, 0.2, 0.42], (m - 23 * 60) / 120.0)


static func is_night(minute: int) -> bool:
	var h := hour(minute)
	return h >= 19 or h < 5


static func _mix(a: Array, b: Array, t: float) -> Array:
	t = clampf(t, 0.0, 1.0)
	return [lerpf(a[0], b[0], t), lerpf(a[1], b[1], t), lerpf(a[2], b[2], t), lerpf(a[3], b[3], t)]


## "08:30" or a number of minutes -> minutes.
static func parse(o, def: int) -> int:
	if o is float or o is int:
		return int(o)
	if o is String:
		var i: int = o.find(":")
		if i > 0:
			return int(o.substr(0, i)) * 60 + int(o.substr(i + 1))
		return int(o) if o.is_valid_int() else def
	return def
