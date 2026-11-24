# v6 asset audit

`tools/v6/audit_unused_assets.py` lists files under `android/assets` that the game can never load:

- **Superseded character sheets** (rule A): the loader in `Assets.java` always prefers
  `walk_v53`, `idle_v53`, `*_8dir_v53` and `poses_v53`, so older `walk_v37/v32`, `idle_v37/v32`
  and `*_8dir_v462` sheets were dead weight. `walk.png`, `walk_plus.png` and `poses.png` are kept:
  they are the base/fallback sheets and the source art the v5.3 atlases were generated from.
- **Unreferenced files** (rule B): `maps/elevation/v50_*` (replaced by `maps/environment_v51/*`
  platforms), v2.1 UI textures (the game loads `ui/v32_*`), and five orphaned props/items.
  `ui/app_icon_512.png` is kept for the store listing.

165 files removed, listed in `deleted_assets.txt`. All of them remain in git history.
Runtime check: the desktop build loaded four outdoor maps with no missing-texture errors, and the
full CI tool suite passes. Two archived checks were pointed at the assets the game actually ships.
