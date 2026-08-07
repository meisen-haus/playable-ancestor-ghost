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
ag_head.nif         morpher head (NiGeomMorpherController)
ag_chest.nif        weighted ghost robe (NiSkinInstance, spine/arm bones)
ag_hand.nif         bony ghost hands (NiSkinInstance, finger bones)
ag_arms_1st.nif     reference: ghost arm mesh for future 1st-person sleeve work
ag_{neck,groin,wrist,forearm,upperarm,foot,ankle,knee,upperleg,hair}.nif   invisible stubs
```

Textures (referenced by NIFs):
- Head: `ag\TX_Ghostward_tunic.tga` (mod-bundled)
- Chest/arms: `textures\tx_ghostward_tunic.dds` (vanilla Morrowind)
- Hands: `textures\tx_licheking.dds` (vanilla Morrowind)

## Mesh provenance

The chest and hand meshes are adapted from the [Playable Creature Race Pack](https://www.nexusmods.com/morrowind/mods/45104) Ghost race assets. They are properly weighted to the standard biped skeleton (not rigid) and deform naturally during animation.

| Mesh | Source | Key properties |
|------|--------|----------------|
| `ag_chest.nif` | Creature Pack `Ghost_chest.nif` | Weighted to Bip01 Spine/Spine1/Spine2 + arm bones |
| `ag_hand.nif` | Creature Pack `Ghost_Hand.nif` (= `Lich_Hand.nif`) | Weighted to finger bones (L/R Finger0-2) |
| `ag_arms_1st.nif` | Creature Pack `Ghost_arms.nif` | 1st-person robe arms, weighted |

## Tools (vendored in repo)

Use `tools/downloads/io_scene_mw/` only — see `.cursor/rules/vendored-tools.mdc`. Do not install alternate exporter versions ad hoc.

Build scripts live under `tools/blender/` and `tools/build_invisible_*.py`.

## First-person rendering

OpenMW first-person shows:
- `Xbase_anim.1st.nif` skeleton geometry (arms — currently invisible)
- Hand body parts attached to hand bones (visible ghost hands from `ag_hand.nif`)

The `build_invisible_1st_person.py` script hides forearm/wrist/upper-arm shapes from the vanilla first-person skeleton. Hand shapes are left alone since the race's hand BODY parts take visual precedence.

Future: replace `Xbase_anim.1st.nif` arm geometry with ghost-sleeved arms from `ag_arms_1st.nif` for full visible first-person ghost arms.

## Future art directions

1. **Full first-person arms** — integrate `ag_arms_1st.nif` geometry into custom `Xbase_anim.1st.nif` for visible ghost robe sleeves.
2. **Retexture** — custom ghost-specific DDS textures to replace vanilla references.
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
| Ghost tunic texture | `Data Files/Textures/TX_Ghostward_tunic.tga` |
| Lich king texture | `Data Files/Textures/Tx_LicheKing.dds` |
