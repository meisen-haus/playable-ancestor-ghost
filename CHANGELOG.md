# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- **Common Disease Immunity** mod setting (default on); twelve **Ghostly Nature** records (`immunity` × `lev`/`ground` × `dis`/`nodis`)
- **Levitation** mod setting (default off)
- **[PLAYERS.md](PLAYERS.md)** — player-focused install, settings, and troubleshooting guide
- Mod settings (**Options → Scripts → Ancestor Ghost**): Normal Weapons Immunity, Common Disease Immunity, Levitation, Undead are friendly
- Three **Ghostly Nature** ability records (`_100` / `_50` / `_0`); Lua grants one matching the immunity setting
- **Bonebiter** birthsign (`ag_sign_bonebiter`): Wraith ability (+25 Endurance, resist shock), Grave Curse spells, Bonebiter
- OpenMW Lua: `balance.lua`, `settings.lua`, per-save `playerSection` storage, live apply on setting change
- `l10n/AncestorGhost/en.yaml` for settings UI strings

### Changed

- **Undead are friendly** uses cell-load pacify (`onActorActive` + CREATURE local script) instead of polling nearby actors
- **Levitation** default is now **off** (was on)
- **Ghost Curse** magicka cost **9** (`SPDT` flags `0`; `F_Autocalc` was forcing ~40)
- **README.md** shortened; player details moved to **PLAYERS.md**
- Race `NPCS` defaults to `ag_ghostly_nature_100_ground_dis`; Lua swaps to the variant matching mod settings
- Tomb-wraith kit moved from mod setting to **Bonebiter** birthsign at character creation

### Removed

- `activeEffects` hacks for normal-weapons immunity (replaced by spell swap)
- Stale dev-only wording from main README
- **Wraith of Sul-Senipul** mod-setting toggle (use Bonebiter birthsign instead)

## [Earlier]

- Playable **Ancestor Ghost** race, **Ghostly Nature**, **Ghost Curse**, segmented BODY meshes, equipment Lua
- See git history on `main` / `balance` for mesh pipeline and stat tuning commits
