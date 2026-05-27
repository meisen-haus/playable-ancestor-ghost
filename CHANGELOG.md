# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- **[PLAYERS.md](PLAYERS.md)** — player-focused install, settings, and troubleshooting guide
- Mod settings (**Options → Scripts → Ancestor Ghost**): Wraith of Sul-Senipul, Normal Weapons Immunity, Undead are friendly
- Three **Ghostly Nature** ability records (`_100` / `_50` / `_0`); Lua grants one matching the immunity setting
- Wraith kit spells and **Wraith** ability (`ag_wraith_sul`: +25 Endurance, resist shock)
- OpenMW Lua: `balance.lua`, `settings.lua`, per-save `playerSection` storage, live apply on setting change
- `l10n/AncestorGhost/en.yaml` for settings UI strings

### Changed

- **Ghost Curse** magicka cost **9** (`SPDT` flags `0`; `F_Autocalc` was forcing ~40)
- **README.md** shortened; player details moved to **PLAYERS.md**
- Ghostly Nature no longer on race `NPCS` (Lua grants the correct variant)

### Removed

- `activeEffects` hacks for normal-weapons immunity (replaced by spell swap)
- Stale dev-only wording from main README

## [Earlier]

- Playable **Ancestor Ghost** race, **Ghostly Nature**, **Ghost Curse**, segmented BODY meshes, equipment Lua
- See git history on `main` / `balance` for mesh pipeline and stat tuning commits
