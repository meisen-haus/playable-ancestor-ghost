# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- Playable **Ancestor Ghost** race (`ancestor_ghost`) in `ancestor_ghost.omwaddon`
- Racial ability **Ghostly Nature**: Chameleon 50%, Resist Normal Weapons / Frost / Poison 100%
- Starting spell **Ghost Curse** (touch; drain endurance/fatigue, damage health)
- **54 BODY** records using vanilla Dunmer meshes (8 head + 8 hair variants per gender)
- OpenMW Lua (`.omwscripts`): equipment enforcement on **15 slots**, one-time tutorial message
- `tools/build_esp.mjs` to regenerate the plugin with correct OpenMW magic effect indices
- Developer docs: [ANCESTOR_GHOST_DEV.md](ANCESTOR_GHOST_DEV.md), [NIF_PRODUCTION.md](NIF_PRODUCTION.md)

### Changed

- Visual approach: Dunmer placeholder + Chameleon (replaces invisible body + VFX overlay)
- Equipment lock includes **clothing** (shirt, pants, skirt, robe), not only armour and weapons

### Removed

- Lua racial spell guard / save migration (racial effects are ESP-only)
- Race-change detection in `global.lua`
- Invisible-body / VFX-overlay approach and `tools/build_nif.mjs`
