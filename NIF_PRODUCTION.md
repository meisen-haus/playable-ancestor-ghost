# NIF production guide — Ancestor Ghost race

Background for mesh work. **Current pipeline and rebuild commands:** [tools/BODY_SLOTS.md](tools/BODY_SLOTS.md). ESP/Lua: [ANCESTOR_GHOST_DEV.md](ANCESTOR_GHOST_DEV.md).

OpenMW loads **one mesh per BODY slot** (26 BODY records today), not the creature ghost rig wholesale.

## What the engine expects

| Concept | Detail |
|--------|--------|
| **Skeleton** | Standard biped (`xbase_anim`) — Dunmer bone names, not creature ghost rig |
| **BODY records** | One `MODL` per slot; `FNAM` = `ancestor_ghost` |
| **Head slot** | Morpher NIF, no Bip01 skeleton in file; tri name must contain `Head` |
| **Body slots** | `Bip01` root + `NiSkinInstance`; tri names match vanilla (`Tri Chest`, …) |
| **Hidden flesh** | Invisible stubs: NiAlphaProperty alpha test NEVER + collapsed verts |
| **Format** | NetImmerse / Gamebryo **4.0.0.2** |

**Not valid as BODY slots:** `Meshes/r/xancestral_ghost.nif` (creature rig — must be re-segmented in Blender first).

## Shipping layout (`Meshes/ag/`)

Unisex paths (male/female share the same file):

```
ag_head.nif      morpher head
ag_chest.nif     robe + both hands (rigid Bip01 root)
ag_{neck,groin,wrist,forearm,upperarm,foot,ankle,knee,upperleg,hair}.nif   invisible stubs
```

Texture: `Textures/ag/TX_Ghostward_tunic.tga` → NIF path `ag\TX_Ghostward_tunic.tga`.

## Tools (vendored in repo)

Use `tools/downloads/io_scene_mw/` only — see `.cursor/rules/vendored-tools.mdc`. Do not install alternate exporter versions ad hoc.

Build scripts live under `tools/blender/` and `tools/build_invisible_*.py`.

## Future art directions

1. **Retexture** — same NIF layout, new materials in NifSkope or Blender.
2. **Weighted body** — replace rigid Bip01 root on chest/hands with proper spine/arm weights (see `build_vanilla_chest_nif.py` history).
3. **Full creature port** — split `xancestral_ghost.nif` to biped slots in Blender; expert rigging.

## Do not use

- Creature ghost mesh directly on player BODY slots.
- Beast Race flag (`0x02`) with biped head records.
- Empty/malformed stub NIFs (OpenMW `marker_error` yellow mesh).

## Vanilla reference paths

| Asset | Path |
|-------|------|
| Dunmer body parts | `Data Files/Meshes/b/B_N_Dark Elf_*` |
| Creature ghost | `Data Files/Meshes/r/xancestral_ghost.nif` |
