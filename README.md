# Ancestor Ghost Race

An OpenMW mod that adds the **Ancestor Ghost** as a fully playable race.

## Description

The Dunmer believe that the spirits of the dead linger in the mortal world — the strongest among them endure as Ancestor Ghosts, bound to protect the tombs of their kin. This mod lets you play as one.

Ancestor Ghosts are incorporeal undead. They **cannot equip weapons, armour, or clothing**; they fight with bare hands and **Ghost Curse** — the touch spell used by the creatures in Dunmer tombs. Visually they use a **ghost head and robe** on a hidden Dunmer rig (Chameleon 50% for extra translucency). Mesh pipeline: [tools/BODY_SLOTS.md](tools/BODY_SLOTS.md).

Racial effects from **Ghostly Nature** (constant ability):

- Chameleon 50%
- Resist Normal Weapons 100% (default; configurable in Scripts)
- Resist Frost 100%
- Resist Poison 100%
- Fortify Maximum Magicka 3× Intelligence (same mechanic as The Mage birthsign, but +2.0 multiplier like The Atronach instead of +0.5)

## Race traits

| Trait | Value |
|---|---|
| **Racial ability** | Ghostly Nature (constant) |
| Chameleon | 50% |
| Resist Normal Weapons | 100% |
| Resist Frost | 100% |
| Resist Poison | 100% |
| Fortify Maximum Magicka | 3× INT |
| **Starting spell** | Ghost Curse (touch, **9** magicka) |
| Ghost Curse effects | Drain Endurance 5 for 30s, Drain Fatigue 10 for 30s, Damage Health 1–10 |

### Starting attributes

Values in the race record are **starting attributes** (same scheme as vanilla races), not +N bonuses on top of 40. Custom classes still add **+10** to each favored attribute at character creation.

| Attribute | Value |
|---|---|
| Strength | 30 |
| Intelligence | 50 |
| Willpower | 50 |
| Agility | 50 |
| Speed | 50 |
| Endurance | 20 |
| Personality | 20 |
| Luck | 40 |

### Skill bonuses

| Skill | Bonus |
|---|---|
| Destruction | +15 |
| Mysticism | +10 |
| Alteration | +10 |
| Conjuration | +10 |

### Mod settings

Under **Options → Scripts → Ancestor Ghost** (changes apply when you toggle them; short on-screen confirmation):

- **Wraith of Sul-Senipul** (default off) — optional Grave Curse spells, Bonebiter, and Wraith ability.
- **Normal Weapons Immunity** (default 100%) — 100%, 50%, or none; swaps which **Ghostly Nature** ability you have (three ESP records, one active at a time).

**How to verify in-game (Ancestor Ghost character):**

| Setting | What to check |
|---|---|
| Wraith of Sul-Senipul **on** | Magic menu gains **Wraith** (ability), **Grave Curse: Fatigue/Strength**, **Bonebiter** |
| Wraith **off** | Those entries are removed |
| Normal Weapons **None** | **Ghostly Nature** ability without resist normal weapons; iron weapons hurt |
| Normal Weapons **50%** / **100%** | **Ghostly Nature** with that resist; test damage from a normal weapon |

### Equipment restriction

Locked slots (enforced by Lua every 0.25s): helmet, cuirass, greaves, boots, pauldrons, gauntlets, shirt, pants, skirt, robe, both hands, ammunition. **Rings and amulets** are allowed.

## Documentation

| Doc | Audience |
|---|---|
| [README.md](README.md) | Players — install and traits |
| [ANCESTOR_GHOST_DEV.md](ANCESTOR_GHOST_DEV.md) | Developers — ESP, Lua, build |
| [NIF_PRODUCTION.md](NIF_PRODUCTION.md) | Artists — custom body NIFs |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

## Installation

**Requires OpenMW 0.51 or newer.**

1. Install [OpenMW](https://openmw.org/) 0.51+ with a standard Morrowind data setup.
2. Place this folder on your OpenMW **data path** (e.g. `OpenMW 0.51.0/data/ancestor-ghost/`) so it contains:
   - `ancestor_ghost.omwscripts`
   - `ancestor_ghost.omwaddon`
   - `scripts/`
   - `l10n/`
3. Open **OpenMW Launcher** → **Data Files** → enable the folder.
4. Enable **`ancestor_ghost.omwaddon`** and **`ancestor_ghost.omwscripts`** (both are required; the addon is the race, the scripts file is Lua).
5. Put **`ancestor_ghost.omwaddon`** after `Morrowind.esm` in load order.
6. Launch the game. Mod options are under **Options → Scripts → Ancestor Ghost** (pause menu or main menu with a save loaded). Settings are per save; changes apply when you toggle them (you should see a short confirmation message).
7. Select **Ancestor Ghost** at character creation.

To rebuild the plugin after editing `tools/build_esp.mjs`:

```bash
node tools/build_esp.mjs
```

## Lore notes

Based on the Ancestor Ghost creature in Dunmer tombs: resistances and Ghost Curse match vanilla creature behavior. The player uses **segmented biped BODY slots** (ghost head/robe + invisible flesh stubs), not the floating creature mesh (`xancestral_ghost.nif`).

## Requirements

| Requirement | Details |
|---|---|
| **OpenMW** | 0.51.0 or newer (Lua API revision 67+) |
| **Morrowind data** | Base game assets installed and configured |
| **MWSE** | Not required |
| **Original engine** | Not supported — OpenMW only |

## License

[MIT License](LICENSE)
