# NIF production guide — Ancestor Ghost race

How to add custom body meshes. See [ANCESTOR_GHOST_DEV.md](ANCESTOR_GHOST_DEV.md) for ESP/Lua and [README.md](README.md) for installation.

The playable race does **not** use one creature NIF on the player. OpenMW loads **one rigged mesh per body slot** via **BODY** records in `ancestor_ghost.omwaddon` (54 records today, all pointing at Dunmer paths).

A useful reference mod is a **playable skeleton race** that ships segmented `Meshes/Skeleton/*.nif` files and matching BODY records — same pattern this mod will follow for ghost parts.

---

## What the engine expects

| Concept | Detail |
|--------|--------|
| **Skeleton** | Standard biped (`xbase_anim` / `base_anim`) — same as Dunmer, not the creature ghost rig |
| **BODY records** | One `MODL` per slot; `FNAM` = `ancestor_ghost` |
| **Per-slot NIF** | Head, hair, neck, chest, groin, hand, wrist, forearm, upper arm, foot, ankle, knee, upper leg |
| **Rigging** | Vertex weights on the biped bone hierarchy (use Dunmer parts as templates) |
| **Format** | NetImmerse / Gamebryo **4.0.0.2** (Morrowind) |

**Not valid as BODY slots:** `Meshes/r/xancestral_ghost.nif`, `XAncestorGhost.nif` (creature rig; needs re-segmentation in Blender).

**Not valid for visible body:** empty or malformed stub NIFs (OpenMW shows `marker_error`).

---

## Tiers of work

### Tier 1 — No custom NIFs (shipping today)

- `build_esp.mjs` → `DUNMER_SKIN`, `HEAD_VARIANTS`
- Chameleon 50% on `ag_ghostly_nature`

### Tier 2 — Retexture Dunmer (recommended first art step)

| Tool | Purpose |
|------|---------|
| **NifSkope** | Materials, texture paths, alpha |
| **Image editor** | Ghostly DDS/PNG |

1. Copy Dunmer NIFs + textures to `Meshes/ag/`.
2. Edit in NifSkope; point `build_esp.mjs` paths at `ag\\...`.
3. `node tools/build_esp.mjs` → test char gen and in-game.

### Tier 3 — Custom rigged parts (skeleton-mod quality)

| Tool | Purpose |
|------|---------|
| **Blender** | Model/edit; skin to biped bones |
| **Blender NIF tools** (e.g. [Greatness7’s](https://www.nexusmods.com/morrowind/mods/42407)) | Export MW 4.0.0.2 + `NiSkinInstance` |
| **NifSkope** | QA: bounds, materials, compare to `B_N_Dark Elf_*` |

~**22 skin NIFs** (11 slots × 2 genders) + head/hair variants. Optional: `*_Hands.1st.nif`, `unsplit_*` for char-gen preview.

### Tier 4 — Port vanilla creature ghost

Import `xancestral_ghost.nif` in Blender, split to biped slots, re-weight — expert rigging only.

---

## Wiring meshes into the mod

```
Meshes/ag/
  ag_chest_m.nif
  ag_head_m_01.nif
  …
  textures/
```

In `tools/build_esp.mjs`:

```javascript
Chest: { m: 'ag\\ag_chest_m.nif', f: 'ag\\ag_chest_f.nif' },
```

```bash
node tools/build_esp.mjs
```

---

## Comparison: skeleton race mod vs this mod

| Topic | Typical skeleton race mod | Ancestor Ghost (now) |
|-------|---------------------------|----------------------|
| Meshes | Custom per-slot NIFs | Vanilla Dunmer |
| BODY records | ~22 | 54 (Dunmer + variants) |
| Lua | Often MWSE (e.g. undead pacify) | OpenMW equip enforcement only |
| ESP | Hand-built `.esp` | Generated `.omwaddon` |
| Racial effects | ESP `NPCS` | ESP `NPCS` (same pattern) |

---

## Roadmap

1. **Done** — Dunmer + Chameleon + ESP racial spells.
2. Retexture one chest + one head → `Meshes/ag/`.
3. Full custom slot set (one gender, then both).
4. Optional: 1st-person hands, custom VO, OpenMW undead-faction script (MWSE features need a new design on OpenMW).

---

## Do not use

- Lua `animation.addVfx` with the creature ghost mesh (creature rig; does not animate with the player).
- Beast Race flag on `ancestor_ghost` with biped head records.

---

## Vanilla asset paths (GOG-style layout)

| Asset | Path |
|-------|------|
| Dunmer body parts | `Data Files/Meshes/b/B_N_Dark Elf_*` |
| Creature ghost | `Data Files/Meshes/r/xancestral_ghost.nif`, `XAncestorGhost.nif` |

OpenMW docs: [openmw.readthedocs.io](https://openmw.readthedocs.io/)
