# Ancestor Ghost Race — Developer Notes

Technical reference. See [README.md](README.md) for players and [tools/BODY_SLOTS.md](tools/BODY_SLOTS.md) for the mesh pipeline.

## File structure

```
playable-ancestor-ghost/
├── ancestor_ghost.omwaddon     # Generated plugin (node tools/build_esp.mjs)
├── ancestor_ghost.omwscripts
├── scripts/ancestor_ghost/     # Lua: equip restrictions + tutorial
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

Rebuild plugin only: `node tools/build_esp.mjs` → **26 BODY** + 2 SPEL + 1 RACE (~7 KB).

## Visual approach (current)

- **Head:** morpher `ag\ag_head.nif` (NPC look-at / talk).
- **Torso + hands:** rigid ghost robe + hands in `ag\ag_chest.nif`.
- **Hidden flesh:** invisible stubs (neck, groin, arms, legs, hair) via NiAlphaProperty test NEVER.
- **Look:** Chameleon 50% on racial ability `ag_ghostly_nature` (ESP only).

**RACE flags:** `0x01` (Playable only). Do not set Beast Race (`0x02`) with biped heads.

**Clavicle:** body part index 13 omitted (vanilla Dunmer has no clavicle BODY records).

## Plugin (`ancestor_ghost.omwaddon`)

Built by `tools/build_esp.mjs`. Master: `Morrowind.esm`.

### SPEL: `ag_ghostly_nature` (Ability)

Chameleon 50, Resist Normal Weapons / Frost / Poison 100. ENAM uses OpenMW `sMagicEffectIds` indices (see `build_esp.mjs`).

### SPEL: `ag_ghost_curse` (touch spell)

Drain Endurance 5, Drain Fatigue 10, Damage Health 1–10.

### BODY records (26 total)

| Group | Count | Notes |
|---|---|---|
| Skin slots (neck → upper leg) | 20 | 10 slots × male + female → `ag\` paths |
| Head | 2 | male + female → `ag\ag_head.nif` |
| Hair | 2 | male + female → `ag\ag_hair.nif` |

Each BODY: `NAME`, `MODL`, `FNAM` (`ancestor_ghost`), `BYDT`.

## Lua (`.omwscripts`)

Requires **OpenMW 0.51+** (`core.API_REVISION >= 67`).

- `global.lua` — unequips locked slots every 0.25 s for `ancestor_ghost` race.
- `player.lua` — one-time tutorial message on equip block.

Racial spells come from RACE `NPCS` in the ESP, not Lua.

## Known limitations

- Chest/hands use rigid Bip01 root (no finger flex / run bob on robe).
- `Xbase_anim.1st.nif` affects all bipeds using that base anim when mod is loaded.
- Equipment rules require Lua; not expressible in RACE alone.
