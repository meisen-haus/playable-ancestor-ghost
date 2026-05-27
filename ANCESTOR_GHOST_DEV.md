# Ancestor Ghost Race — Developer Notes

Technical reference. See [README.md](README.md) for players and [tools/BODY_SLOTS.md](tools/BODY_SLOTS.md) for the mesh pipeline.

## File structure

```
playable-ancestor-ghost/
├── ancestor_ghost.omwaddon     # Generated plugin (node tools/build_esp.mjs)
├── ancestor_ghost.omwscripts
├── scripts/ancestor_ghost/     # Lua: settings, equip restrictions, balance
├── l10n/AncestorGhost/       # Settings UI strings (en.yaml)
├── Meshes/ag/                  # Custom + invisible stub NIFs
├── Meshes/Xbase_anim.1st.nif   # Invisible 1st-person arms (global override)
├── Textures/ag/TX_Ghostward_tunic.tga
├── tools/
│   ├── build_esp.mjs
│   ├── build_invisible_stubs.py
│   ├── build_invisible_1st_person.py
│   └── blender/
│       ├── ancestor_ghost.blend
│       ├── build_vanilla_head_nif.py
│       └── build_vanilla_chest_nif.py
└── .cursor/rules/              # Agent guidance (MCP, vendored io_scene_mw)
```

Rebuild plugin only: `node tools/build_esp.mjs` → **26 BODY** + 17 SPEL + 1 RACE + 1 BSGN.

**Releases:** publishing a GitHub release runs [`.github/workflows/release.yml`](.github/workflows/release.yml). It rebuilds `ancestor_ghost.omwaddon` and attaches **one zip** (`ancestor-ghost-<tag>.zip`) containing the full mod folder (`ancestor-ghost/`: `.omwaddon`, `.omwscripts`, `scripts/`, `l10n/`, `Meshes/`, `Textures/`, docs). Manual test: Actions → Release build → Run workflow.

## Mod settings (Options → Scripts → Ancestor Ghost)

Same pattern as [spreadable-corprus](../spreadable-corprus): `settings.lua` registers page/group from **`player.lua`** via `pcall(settings.registerPage)` / `pcall(settings.registerGroup)`. Display strings are **l10n keys** in `l10n/AncestorGhost/en.yaml`. Storage uses `storage.playerSection('SettingsAncestorGhost')` with `permanentStorage = false` (per save).

`balance.lua` is called from `player.lua` when:

1. **First `onFrame`** after the player script starts (covers save load; spell APIs need an active player).
2. **`SettingsAncestorGhost` storage changes** (`storage:subscribe`) — applies **immediately** when you change options in **Options → Scripts** (short on-screen confirmation).

Script `onLoad` also tries an early apply; the first-frame pass is the reliable one. `player_settings.readFromStorage()` is player-script-only.

| Setting | Default | Effect |
|---|---|---|
| Normal Weapons Immunity | 100% | Swaps **Ghostly Nature** resist-normal-weapons (`_*_{lev,ground}_{dis,nodis}` × 100 / 50 / 0) |
| Common Disease Immunity | on | **Ghostly Nature** includes resist common disease |
| Levitation | off | **Ghostly Nature** includes Levitate 10 |
| Undead are friendly | off | Sets **Fight** to 0 on active creatures with CREA type **Undead** (skeletons, bonewalkers, ghosts, etc.); restores AI when turned off |

**Bonebiter birthsign** (`ag_sign_bonebiter`): at character creation, grants `ag_wraith_sul`, Grave Curse spells, and **Bonebiter** (replaces the old wraith mod-setting toggle).

Player-facing install and settings: **[PLAYERS.md](PLAYERS.md)**.

**`ancestor_ghost.omwscripts` must be enabled** in the launcher (separate checkbox from the `.omwaddon`).

## Visual approach (current)

- **Head:** morpher `ag\ag_head.nif` (NPC look-at / talk).
- **Torso + hands:** rigid ghost robe + hands in `ag\ag_chest.nif`.
- **Hidden flesh:** invisible stubs (neck, groin, arms, legs, hair) via NiAlphaProperty test NEVER.
- **Look / movement:** Optional Levitate 10 and Chameleon 50% on **Ghostly Nature** (ESP; one of twelve immunity×levitate×disease variants).

**RACE flags:** `0x01` (Playable only). Do not set Beast Race (`0x02`) with biped heads.

**Clavicle:** body part index 13 omitted (vanilla Dunmer has no clavicle BODY records).

## Plugin (`ancestor_ghost.omwaddon`)

Built by `tools/build_esp.mjs`. Master: `Morrowind.esm`.

### RACE `ancestor_ghost` — RADT attributes

`RACE_ATTRS` in `build_esp.mjs` are **starting attribute values** (Strength → Luck), same as vanilla races. In the binary `RADT` subrecord they must be written **interleaved male/female per attribute** (`Str♂`, `Str♀`, `Int♂`, `Int♀`, …), not as two blocks of eight — OpenMW indexes `mAttributeValues` that way (`ESM::Race::RADTstruct::getAttribute` in `components/esm3/loadrace.cpp`). Block layout scrambles stats in chargen.

### SPEL: Ghostly Nature variants (Ability)

Twelve records, same display name **Ghostly Nature**: `ag_ghostly_nature_{100,50,0}_{lev,ground}_{dis,nodis}`. Shared on all: Chameleon 50, Resist Frost / Poison 100, Fortify Maximum Magicka 20. `_*_lev_*` adds Levitate 10; `_*_ground_*` omits it. `_*_dis` adds Resist Common Disease 100; `_*_nodis` omits it. Only 100% and 50% include Resist Normal Weapons at that magnitude. Chargen default on race `NPCS`: `ag_ghostly_nature_100_ground_dis`. `balance.lua` strips the other eleven and `spells:add`s the record matching all three mod settings. Wraith kit is granted via **Bonebiter** birthsign at character creation. Legacy spell IDs (including the six-variant `_lev` / `_ground` names without `_dis` / `_nodis`) are stripped on apply.

### BSGN: `ag_sign_bonebiter` (Bonebiter)

Display name **Bonebiter**. Texture `Birthsigns\Tx_birth_bonebiter.tga` (256×128, same format as vanilla birthsigns). Rebuild: `node tools/build_bonebiter_birthsign_texture.mjs` (contrast + blue bow constellation lines on `tools/source/bonebiter_birthsign.png`, then scale).

Grants at character creation: `ag_wraith_sul` (ability **Wraith**: +25 Endurance, 100% resist shock), `ag_wraith_grave_fatigue`, `ag_wraith_grave_strength`, `ag_wraith_bonebiter`. Replaces the former **Wraith of Sul-Senipul** mod-setting toggle.

### SPEL: `ag_ghost_curse` (touch spell)

Drain Endurance 5, Drain Fatigue 10, Damage Health 1–10. **Magicka cost 9** (`SPDT` cost `9`, **flags `0`**). Do not set `F_Autocalc` (`flags 0x1`) — OpenMW then ignores the cost field and recalculates ~40 like vanilla `Ghost Curse`.

### BODY records (26 total)

| Group | Count | Notes |
|---|---|---|
| Skin slots (neck → upper leg) | 20 | 10 slots × male + female → `ag\` paths |
| Head | 2 | male + female → `ag\ag_head.nif` |
| Hair | 2 | male + female → `ag\ag_hair.nif` |

Each BODY: `NAME`, `MODL`, `FNAM` (`ancestor_ghost`), `BYDT`.

## Lua (`.omwscripts`)

Requires **OpenMW 0.51+** (`core.API_REVISION >= 67`).

- `settings.lua` + `player.lua` — register mod settings page (player script only).
- `balance.lua` / `player_settings.lua` — Ghostly Nature variant from player storage.
- `undead_friendly_global.lua` — `onActorActive` + `world.activeActors`; sends `AG_PacifyUndead` / `AG_RestoreFight` (global cannot write AI fight stats in OpenMW 0.51).
- `undead_creature.lua` — CREATURE local script; zeros Fight on `AG_PacifyUndead` (OpenMW equivalent of USkele’s per-ref `mobile.fight = 0`).
- `undead_friendly_player.lua` — sends `AG_UndeadFriendlySync` to global (player scripts cannot write global storage).
- `global.lua` — unequips locked slots every 0.25 s; `onActorActive` + `AG_UndeadFriendlySync`.
- `player.lua` — `undeadFriendly.syncToGlobal()` on load / active / setting change.

Racial **Ghost Curse** comes from RACE `NPCS` in the ESP; **Ghostly Nature** variant is swapped by Lua from mod settings.

## Known limitations

- Chest/hands use rigid Bip01 root (no finger flex / run bob on robe).
- `Xbase_anim.1st.nif` affects all bipeds using that base anim when mod is loaded.
- Equipment rules require Lua; not expressible in RACE alone.
