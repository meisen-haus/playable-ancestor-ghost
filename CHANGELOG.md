# Changelog

All notable changes to this project are documented here.

## [Unreleased]

## [0.3.0]

### Added

- Soft **idle float** (`scripts/ancestor_ghost/idle_pose.lua`): third-person `idlespell` on torso + arms when unready so the robe does not bounce with walk; first person keeps default lower arms so magic-ready stays distinct
- Separate **Hand** BODY meshes (`ag_hand.nif`) and first-person Chest/Hand `*.1st` BODY records

### Changed

- **Chest** rebuilt as weighted robe (`ag_chest.nif`): sleeve chain Clavicle→Hand; Pelvis/Spine weights folded to Spine1/Spine2 for Torso float
- **Hands** use pack-style finger/hand skin + vanilla `Tx_LicheKing.dds`; tunic remains `ag\TX_Ghostward_tunic.tga`
- First-person immersion: full chest mesh when looking down; Dunmer arm tris still hidden in `Xbase_anim.1st.nif`
- ESP BODY layout updated (`tools/build_esp.mjs`): Hand slots + four `.1st` records
- Docs: PLAYERS / DEV / NIF / BODY_SLOTS updated for mesh pipeline, idle float, and provenance
- Ghostly Nature **Levitate** magnitude **30**; in-game settings copy simplified (also on this branch)

### Credits

- Body slot layout and bind-pose skinning informed by **[Playable Creature Race Pack](https://www.nexusmods.com/morrowind/mods/45104)** by **[Sheogorath101](https://www.nexusmods.com/morrowind/users/620544)** as a structural reference — not redistributed; shipping textures and head are separate

## [0.2.0]

### Added

- **Common Disease Immunity** mod setting (default on); twelve **Ghostly Nature** records (`immunity` × `lev`/`ground` × `dis`/`nodis`)
- **Levitation** mod setting (default off)
- **[PLAYERS.md](PLAYERS.md)** — player-focused install, settings, and troubleshooting guide
- Mod settings (**Options → Scripts → Ancestor Ghost**): Normal Weapons Immunity, Common Disease Immunity, Levitation, Undead are friendly
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
- See git history on `main` for mesh pipeline and stat tuning commits
