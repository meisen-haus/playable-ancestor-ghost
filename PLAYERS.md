# Ancestor Ghost: Player Guide

Play as a Dunmer **Ancestor Ghost**: incorporeal, tomb-bound, and unable to wear normal gear. This mod is for **OpenMW 0.51+** only (not vanilla Morrowind, not MWSE).

## Requirements

- [OpenMW](https://openmw.org/) **0.51.0 or newer**
- A legal install of **Morrowind** data files (configured in OpenMW)

## Installation

1. Download **`ancestor-ghost-<version>.zip`** from [GitHub Releases](https://github.com/meisen-haus/playable-ancestor-ghost/releases) (one file: addon, scripts, meshes, and Lua).
2. Extract the **`ancestor-ghost`** folder into your OpenMW **data path** (for example `OpenMW 0.51.0/data/ancestor-ghost/`).
3. The folder must include at minimum:
   - `ancestor_ghost.omwaddon`
   - `ancestor_ghost.omwscripts`
   - `scripts/`
   - `l10n/`
   - `Meshes/` and `Textures/` (ghost appearance)
4. Open **OpenMW Launcher**, then **Data Files**, and enable the mod folder.
5. Enable **both**:
   - `ancestor_ghost.omwaddon` (race, spells, body parts)
   - `ancestor_ghost.omwscripts` (equipment lock and mod settings)
6. In load order, place **`ancestor_ghost.omwaddon` after `Morrowind.esm`**.
7. Start the game, choose **Ancestor Ghost** at character creation, and pick a birthsign (see **Bonebiter** below for the tomb-wraith kit).

If options or equipment rules do nothing, the **scripts** file is probably not enabled.

## What you get

Every Ancestor Ghost gets the following:

- **Look:** Ghost head and robe; flesh slots hidden; Chameleon 50%.
- **Ghostly Nature:** Constant ability. Resist to normal weapons depends on the immunity setting below.
- **Resists:** Frost and poison 100% (always).
- **Magicka:** Fortify Maximum Magicka at **3× Intelligence** (similar to The Mage birthsign, with a stronger multiplier).
- **Starting spell:** **Ghost Curse** (touch, **9** magicka): drains endurance and fatigue, damages health.
- **Combat:** Hand-to-hand and Ghost Curse only. No weapons, armour, or clothing.
- **Jewelry:** Rings and amulets are allowed.

### Starting attributes

Strength 30, Intelligence 50, Willpower 50, Agility 50, Speed 50, Endurance 20, Personality 20, Luck 40.

### Skill bonuses

Destruction +15, Mysticism +10, Alteration +10, Conjuration +10.

Custom classes still add **+10** to each favored attribute at creation, same as vanilla races.

## Mod settings

Open **Options**, then **Scripts**, then **Ancestor Ghost** (from the pause menu, or the main menu while a save is loaded). Settings are **per save**. When you change something, you should see a short on-screen message and the effect applies right away.

### Normal Weapons Immunity (default: 100%)

- **100%:** Normal weapons (iron, steel, and similar) do not harm you.
- **50%:** Half damage from normal weapons.
- **None:** You can be hurt by normal weapons like a living character.

All three options use the same ability name in the spell list: **Ghostly Nature**. Only one variant is active at a time.

## Birthsign: Bonebiter

At character creation, choose the **Bonebiter** birthsign for the tomb-wraith kit (Wraith of Sul-Senipul):

- Ability **Wraith** (+25 Endurance, 100% resist shock)
- Spells **Grave Curse: Fatigue**, **Grave Curse: Strength**, and **Bonebiter**

Like vanilla birthsigns, these are granted at creation and stay on your spell list. Other birthsigns work as usual if you do not want this kit.

## Equipment you cannot use

Helmet, cuirass, greaves, boots, pauldrons, gauntlets, shirt, pants, skirt, robe, weapons (both hands), and ammunition. If you try to equip any of these, the gear is unequipped and you may see a one-time tutorial message.

## Tips

- **New character:** Pick Ancestor Ghost at creation. Existing saves need a race-change mod or a new game to use this race.
- **Testing immunity:** At **None**, test with an iron weapon or an NPC who uses one. At **100%**, you should take no damage from normal weapons.
- **After updating the mod:** Restart OpenMW and load your save so scripts and the plugin reload.

## Troubleshooting

**No Scripts → Ancestor Ghost page:** Enable `ancestor_ghost.omwscripts` and use OpenMW 0.51 or newer.

**Settings do nothing:** Enable the scripts file and restart the game after copying updated files.

**Ghost Curse costs 40 magicka:** You have an old `ancestor_ghost.omwaddon`. Replace it with the latest release build.

**Still immune at None:** Old save or old plugin. Install the latest addon and toggle the setting again.

**Wrong body or missing ghost mesh:** Install the full mod folder, including `Meshes/` and `Textures/`.

## Lore

Based on ancestral ghosts in Dunmer tombs: frost and poison immunity, ghost curse touch, and resistance to normal weapons (configurable). The playable body uses a biped rig with a ghost robe and head, not the floating creature mesh from vanilla.
