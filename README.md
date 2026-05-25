# Ancestor Ghost Race

An OpenMW mod that adds the **Ancestor Ghost** as a fully playable race.

## Description

The Dunmer believe that the spirits of the dead linger in the mortal world — the strongest among them endure as Ancestor Ghosts, bound to protect the tombs of their kin. This mod lets you play as one.

Ancestor Ghosts are incorporeal undead. They **cannot equip weapons, armour, or clothing**; they fight with bare hands and **Ghost Curse** — the touch spell used by the creatures in Dunmer tombs. Visually they use a **ghost head and robe** on a hidden Dunmer rig (Chameleon 50% for extra translucency). Mesh pipeline: [tools/BODY_SLOTS.md](tools/BODY_SLOTS.md).

Racial effects from **Ghostly Nature** (constant ability):

- Chameleon 50%
- Resist Normal Weapons 100%
- Resist Frost 100%
- Resist Poison 100%

## Race traits

| Trait | Value |
|---|---|
| **Racial ability** | Ghostly Nature (constant) |
| Chameleon | 50% |
| Resist Normal Weapons | 100% |
| Resist Frost | 100% |
| Resist Poison | 100% |
| **Starting spell** | Ghost Curse (touch) |
| Ghost Curse effects | Drain Endurance 5 for 30s, Drain Fatigue 10 for 30s, Damage Health 1–10 |

### Attribute bonuses

| Attribute | Value |
|---|---|
| Strength | 30 |
| Intelligence | 65 |
| Willpower | 30 |
| Agility | 50 |
| Speed | 60 |
| Endurance | 20 |
| Personality | 20 |
| Luck | 40 |

### Skill bonuses

| Skill | Bonus |
|---|---|
| Conjuration | +10 |
| Mysticism | +10 |
| Unarmored | +10 |
| Hand-to-hand | +10 |

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
3. Open **OpenMW Launcher** → **Data Files** → enable the folder.
4. Enable **`ancestor_ghost.omwaddon`** after `Morrowind.esm`.
5. Launch the game and select **Ancestor Ghost** at character creation.

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
