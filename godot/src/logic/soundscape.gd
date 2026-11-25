class_name Soundscape
extends RefCounted
## Music, ambience and footstep choice per place, weather and hour (port of SoundscapePlan.java).


static func music_for(area: String, base, weather: String, indoor: bool, minute: int, quest_music = null) -> String:
	if quest_music != null and str(quest_music) != "":
		return str(quest_music)
	var rainy := weather == "rain" or weather == "hujan"
	var night := WorldClock.is_night(minute)
	var dusk := WorldClock.hour(minute) >= 16
	match area:
		"arland_room", "sofia_room": return "home_evening" if dusk or night else "home_morning"
		"cafe", "dapur", "galeri_komunitas": return "cafe_waltz"
		"perpustakaan", "ruang_dua_surat": return "library_whisper"
		"toko_bunga": return "flower_shop"
		"arcade": return "arcade_neon"
		"memory_garden": return "memory_bloom"
		"lantern_field", "rain_garden": return "lantern_glow"
		"star_path", "memory_bridge": return "star_road"
		"starfall_village": return "star_village"
		"clockwork_station", "ruang_arsip": return "archive_mystery"
		"moonlight_lake": return "lake_moon"
		"bukit_bintang": return "hill_stars"
		"eternal_garden", "hall_of_tomorrow": return "eternal_promise"
		"hutan_bisik": return "whisper_woods"
		"gua_kristal": return "crystal_echo"
	if rainy and not indoor:
		return "rain_lullaby"
	match area:
		"riverside", "dermaga": return "lake_moon" if night else "lake_breeze"
		"taman_kota": return "park_sunset" if dusk or night else "park_blossom"
		"perumahan": return "city_night" if night else "neighborhood_day"
		"plaza", "jalan_kota": return "city_night" if night else ("city_evening" if dusk else "city_morning")
	return "town" if base == null or str(base) == "" else str(base)


static func ambience_for(area: String, weather: String, indoor: bool, minute: int) -> String:
	var rainy := weather == "rain" or weather == "hujan"
	match area:
		"rain_garden": return "rain_outdoor"
		"star_path", "bukit_bintang": return "v50_highland_breeze"
		"memory_garden", "eternal_garden": return "v50_memory_air"
		"hall_of_tomorrow", "clockwork_station", "memory_bridge": return "magic_chimes"
		"moonlight_lake": return "lake_water"
		"arcade": return "arcade_hum"
		"cafe", "dapur", "galeri_komunitas": return "rain_window" if rainy else "cafe_room"
		"ruang_dua_surat": return "library_room"
		"perpustakaan", "ruang_arsip": return "rain_window" if rainy else "library_room"
		"gua_kristal": return "cave_drips"
		"lantern_field", "starfall_village": return "magic_chimes"
	if indoor:
		return "rain_window" if rainy else ""
	if rainy:
		return "rain_outdoor"
	match area:
		"riverside", "dermaga": return "lake_water"
		"hutan_bisik": return "forest_wind"
	if WorldClock.is_night(minute):
		return "night_crickets"
	match area:
		"taman_kota", "toko_bunga": return "park_birds"
		"perumahan": return "wind_leaves"
	return "birds_morning" if WorldClock.hour(minute) < 10 else "city_day"


static func footstep_for(area: String) -> String:
	match area:
		"taman_kota", "hutan_bisik", "memory_garden", "eternal_garden", "rain_garden":
			return "step_grass"
		"cafe", "dapur", "arland_room", "sofia_room", "perpustakaan", "ruang_arsip", "galeri_komunitas", "clockwork_station", "hall_of_tomorrow", "ruang_dua_surat":
			return "step_wood"
	return "step_stone"
