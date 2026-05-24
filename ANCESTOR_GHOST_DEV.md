# Ancestor Ghost Race — Developer Notes

Technical reference. See [README.md](README.md) for players and [NIF_PRODUCTION.md](NIF_PRODUCTION.md) for mesh authoring.

## File structure

```
ancestor-ghost/
├── ancestor_ghost.omwaddon     # Generated plugin (run build_esp.mjs)
├── ancestor_ghost.omwscripts   # Lua manifest (LOAD / GLOBAL / PLAYER)
├── scripts/ancestor_ghost/
│   ├── content_register.lua    # LOAD: OpenMW API revision guard
│   ├── global.lua              # GLOBAL: equipment slot enforcement
│   └── player.lua              # PLAYER: one-time equip-block tutorial
├── tools/
│   └── build_esp.mjs           # Builds ancestor_ghost.omwaddon
├── README.md
├── ANCESTOR_GHOST_DEV.md
├── NIF_PRODUCTION.md
└── CHANGELOG.md
```

Rebuild the plugin:

```bash
node tools/build_esp.mjs
```

Output: **57 content records** (2 SPEL + 54 BODY + 1 RACE), ~7 KB.

---

## Visual approach (current)

- **Body:** vanilla Dunmer meshes on all BODY records (`DUNMER_SKIN`, `HEAD_VARIANTS` in `build_esp.mjs`).
- **Look:** Chameleon 50% on racial ability `ag_ghostly_nature` (ESP only — no Lua spell logic).
- **Not used:** custom NIFs or creature-mesh VFX overlay.
- **Deferred:** custom segmented ghost meshes — see [NIF_PRODUCTION.md](NIF_PRODUCTION.md).

**RACE flags:** `0x01` (Playable only). Do not set Beast Race (`0x02`) with Dunmer biped heads — causes char-gen animation / `Attribute 'Empty{}'` errors.

**Clavicle:** body part index 13 omitted (vanilla Dunmer has no clavicle BODY records).

---

## Plugin (`ancestor_ghost.omwaddon`)

Built by `tools/build_esp.mjs`. Master: `Morrowind.esm`.

### SPEL: `ag_ghostly_nature` (Ability, SPDT type 1)

| Effect | OpenMW ENAM index | Magnitude |
|---|---|---|
| Chameleon | 40 | 50 |
| Resist Normal Weapons | 98 | 100 |
| Resist Frost | 91 | 100 |
| Resist Poison | 97 | 100 |

ENAM uses **OpenMW `sMagicEffectIds` indices** (see comments in `build_esp.mjs`), not legacy CS effect numbers.

### SPEL: `ag_ghost_curse` (Spell, touch, SPDT flags `0x0001`)

| Effect | Attribute | Magnitude | Duration |
|---|---|---|---|
| Drain Attribute | Endurance | 5 | 30s |
| Drain Fatigue | — | 10 | 30s |
| Damage Health | — | 1–10 | instant |

### RACE: `ancestor_ghost`

| Subrecord | Content |
|---|---|
| NAME | `ancestor_ghost` |
| FNAM | `Ancestor Ghost` |
| RADT | Attributes, skills, height/weight, flags `0x01` |
| NPCS | `ag_ghostly_nature`, `ag_ghost_curse` |
| DESC | Race description text |

No `INDX` / inline body list on RACE — body parts are separate **BODY** records with `FNAM = ancestor_ghost`.

### BODY records (54 total)

| Group | Count | Notes |
|---|---|---|
| Skin (neck → upper leg) | 20 | 10 slots × male + female; vanilla Dunmer `MODL` paths |
| Head variants | 16 | 8 male + 8 female |
| Hair variants | 16 | 8 male + 8 female |
| Clavicle | 0 | omitted |

Each BODY: `NAME`, `MODL`, `FNAM` (`ancestor_ghost`), `BYDT` (part index, gender flag, type skin).

---

## Lua (`.omwscripts`)

Requires **OpenMW 0.51+** (`core.API_REVISION >= 67`).

### `content_register.lua` (LOAD)

Fails fast if API revision is too old. No `openmw.content` registration needed for a RACE-only mod.

### `global.lua` (GLOBAL)

Polls `world.players` every **0.25 s**. For `race == ancestor_ghost`, unequips any item in locked slots and sends `AG_EquipBlocked` to the player.

**Locked `EQUIPMENT_SLOT` values:**

`Helmet`, `Cuirass`, `Greaves`, `Boots`, `LeftPauldron`, `RightPauldron`, `LeftGauntlet`, `RightGauntlet`, `Shirt`, `Pants`, `Skirt`, `Robe`, `CarriedLeft`, `CarriedRight`, `Ammunition`.

Use `CarriedLeft` / `CarriedRight` for shield and weapons — there is no `WeaponOneHand` in OpenMW Lua.

**Allowed:** rings, amulets, belt (not in locked list).

### `player.lua` (PLAYER)

Shows a **one-time** `ui.showMessage` when `AG_EquipBlocked` fires. Flag stored in `storage.playerSection('AncestorGhost')` key `ag_tutorial_shown`.

**Racial spells are not applied in Lua** — only via RACE `NPCS` in the ESP at character creation.

---

## Known limitations

- Placeholder appearance (Dunmer + Chameleon), not the tomb ghost creature model.
- Equipment rules require Lua; not expressible in the RACE record alone.

---

## Debugging notes (historical)

| Symptom | Cause |
|---|---|
| `Unknown subrecord RACE/INDX` | Invalid Skyrim-style body list on RACE — use separate BODY records |
| Char-gen yellow box | Head/hair need real biped NIFs with geometry |
| `Attribute 'Empty{}' not found` | Wrong ENAM effect indices or Beast flag + biped heads |
| `marker_error` yellow mesh | Invalid / empty custom NIF on a BODY slot |
| `Key not found: WeaponOneHand` | Invalid Lua equipment slot name |

Vanilla `lookoutScript` / `fallingScript` warnings come from `Morrowind.esm`, not this mod.
