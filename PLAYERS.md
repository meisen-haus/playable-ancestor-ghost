# Ancestor Ghost — Player Guide

Play as a Dunmer **Ancestor Ghost**: incorporeal, tomb-bound, and unable to wear normal gear. This mod is for **OpenMW 0.51+** only (not vanilla Morrowind, not MWSE).

## Requirements

- [OpenMW](https://openmw.org/) **0.51.0 or newer**
- A legal install of **Morrowind** data files (configured in OpenMW)

## Installation

1. Copy this mod folder into your OpenMW **data path** (for example `OpenMW 0.51.0/data/ancestor-ghost/`).
2. The folder must include at minimum:
   - `ancestor_ghost.omwaddon`
   - `ancestor_ghost.omwscripts`
   - `scripts/`
   - `l10n/`
   - `Meshes/` and `Textures/` (ghost appearance)
3. Open **OpenMW Launcher** → **Data Files** → enable the mod folder.
4. Enable **both**:
   - `ancestor_ghost.omwaddon` (race, spells, body parts)
   - `ancestor_ghost.omwscripts` (equipment lock + mod settings)
5. In load order, place **`ancestor_ghost.omwaddon` after `Morrowind.esm`**.
6. Start the game and choose **Ancestor Ghost** at character creation.

If options or equipment rules do nothing, the **scripts** file is probably not enabled.

## What you get

### Always (every Ancestor Ghost)

| Feature | Details |
|--------|---------|
| **Look** | Ghost head and robe; flesh slots hidden; Chameleon 50% |
| **Ghostly Nature** | Constant ability (see immunity setting below for resist normal weapons) |
| **Resists** | Frost and poison 100% (always) |
| **Magicka** | Fortify Maximum Magicka — **3× Intelligence** (similar to The Mage birthsign, stronger multiplier) |
| **Starting spell** | **Ghost Curse** (touch, **9** magicka) — drain endurance/fatigue, damage health |
| **Combat** | Hand-to-hand + Ghost Curse; **no** weapons, armour, or clothing |
| **Jewelry** | Rings and amulets **are** allowed |

### Starting stats

| Attribute | Value |
|-----------|-------|
| Strength | 30 |
| Intelligence | 50 |
| Willpower | 50 |
| Agility | 50 |
| Speed | 50 |
| Endurance | 20 |
| Personality | 20 |
| Luck | 40 |

| Skill bonus | Value |
|-------------|-------|
| Destruction | +15 |
| Mysticism | +10 |
| Alteration | +10 |
| Conjuration | +10 |

Custom classes still add **+10** to each favored attribute at creation (same as vanilla races).

## Mod settings

Open **Options → Scripts → Ancestor Ghost** (from the pause menu, or the main menu while a save is loaded). Settings are **per save**. When you change something, you should see a short on-screen message and the effect applies right away.

### Wraith of Sul-Senipul (default: off)

Adds optional tomb-wraith kit:

- Ability **Wraith** (+25 Endurance, 100% resist shock)
- Spells **Grave Curse: Fatigue**, **Grave Curse: Strength**, **Bonebiter**

Turn off to remove those spells/ability from your character.

### Normal Weapons Immunity (default: 100%)

| Setting | Effect |
|---------|--------|
| **100%** | Normal weapons (iron, steel, etc.) do not harm you |
| **50%** | Half damage from normal weapons |
| **None** | You can be hurt by normal weapons like a living character |

All three use the same ability name in the spell list: **Ghostly Nature**. Only one variant is active at a time.

## Equipment you cannot use

Helmet, cuirass, greaves, boots, pauldrons, gauntlets, shirt, pants, skirt, robe, weapons (both hands), and ammunition. If you try, gear is unequipped and you may see a one-time tutorial message.

## Tips

- **New character** — Pick Ancestor Ghost at creation; existing saves need a race change mod or a new game to use this race.
- **Testing immunity** — At **None**, hit yourself or ask an NPC with an iron weapon; at **100%**, you should take no normal-weapon damage.
- **After updating the mod** — Restart OpenMW and load your save so scripts and the plugin reload.

## Troubleshooting

| Problem | What to check |
|---------|----------------|
| No **Scripts → Ancestor Ghost** page | Enable `ancestor_ghost.omwscripts`; OpenMW 0.51+ |
| Settings do nothing | Same as above; restart the game after copying files |
| Ghost Curse costs **40** magicka | Old `ancestor_ghost.omwaddon` — replace with the latest from the repo |
| Still immune at **None** | Old save or old plugin; load latest addon and toggle the setting again |
| Wrong body / missing ghost mesh | Full mod folder installed (`Meshes/`, `Textures/`) |

## Lore

Based on ancestral ghosts in Dunmer tombs: frost and poison immunity, ghost curse touch, and resistance to normal weapons (configurable). The playable body uses a biped rig with a ghost robe and head, not the floating creature mesh from vanilla.
