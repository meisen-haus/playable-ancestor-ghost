# NIF production guide — Ancestor Ghost race

Background for mesh work. **Current pipeline and rebuild commands:** [tools/BODY_SLOTS.md](tools/BODY_SLOTS.md). ESP/Lua: [ANCESTOR_GHOST_DEV.md](ANCESTOR_GHOST_DEV.md).

OpenMW loads **one mesh per BODY slot** (30 BODY records today: 26 third-person + 4 first-person `*.1st`), not the creature ghost rig wholesale.

## What the engine expects

| Concept | Detail |
|--------|--------|
| **Skeleton** | Standard biped (`xbase_anim`) — Dunmer bone names, not creature ghost rig |
| **BODY records** | One `MODL` per slot; `FNAM` = `ancestor_ghost` |
| **Head slot** | Morpher NIF, no Bip01 skeleton in file; tri name must contain `Head` |
| **Body slots** | `Bip01` root + `NiSkinInstance`; tri names match vanilla (`Tri Chest`, …) |
| **First person** | BODY IDs ending in `.1st` override the matching part in 1st person |
| **Hidden flesh** | Invisible stubs: NiAlphaProperty alpha test NEVER + collapsed verts |
| **Format** | NetImmerse / Gamebryo **4.0.0.2** |

**Not valid as BODY slots:** `Meshes/r/xancestral_ghost.nif` (creature rig — must be re-segmented in Blender first).

## Shipping layout (`Meshes/ag/`)

Unisex paths (male/female share the same file):

```
ag_head.nif         morpher head (NiGeomMorpherController)
ag_chest.nif        weighted ghost robe (skin ref + float reweight → Spine1/Spine2)
ag_hand.nif         ghost hands + vanilla Tx_LicheKing
ag_arms_1st.nif     optional arms-only ref (1st person uses full ag_chest.nif)
ag_{neck,groin,wrist,forearm,upperarm,foot,ankle,knee,upperleg,hair}.nif   invisible stubs
```

Textures:
- Head / chest / sleeves: `ag\TX_Ghostward_tunic.tga` (mod-bundled)
- Hands: `textures\Tx_LicheKing.dds` (vanilla Morrowind)

## Provenance

Body NIFs use creature-pack **bind-pose skinning references** under `tools/reference/` (chest/arms/hand), with textures rewritten to our bundled tunic TGA and vanilla `Tx_LicheKing.dds`. Hanging vanilla-robe verts + biped Forearm weights caused classic sleeve stretch; the pack meshes are authored in biped arm bind pose so sleeves follow shoulder→wrist. Chest/arms builds also **fold Pelvis/Spine weights into Spine1/Spine2** so a Torso IdleSpell blend can float the robe while invisible legs walk. Head remains Blender-built from vanilla morpher geometry. Pack BODY layout (separate Hand, Chest `*.1st`) is also followed.

## Tools (vendored in repo)

Use `tools/downloads/io_scene_mw/` only — see `.cursor/rules/vendored-tools.mdc`. Do not install alternate exporter versions ad hoc.

Build scripts live under `tools/blender/` and `tools/build_invisible_*.py`.

## First-person rendering

OpenMW first-person shows:
- `Xbase_anim.1st.nif` skeleton (Dunmer wrist/forearm/upper-arm tris hidden)
- BODY `ag_chest_*.1st` → `ag_chest.nif` (full robe torso for look-down immersion)
- BODY `ag_hand_*.1st` → `ag_hand.nif` (bony hands)

## Future art directions

1. **Retexture** — custom ghost-specific DDS if desired beyond the bundled tunic TGA.
2. **Weight paint polish** — hand sleeve-exit placement still relies on nearest-bone transfer from Dunmer T-pose refs.
3. **Full creature port** — alternate segmentations of `xancestral_ghost.nif` if art direction changes.

## Do not use

- Creature ghost mesh directly on player BODY slots.
- Beast Race flag (`0x02`) with biped head records.
- Empty/malformed stub NIFs (OpenMW `marker_error` yellow mesh).

## Vanilla reference paths

| Asset | Path |
|-------|------|
| Dunmer body parts | `Data Files/Meshes/b/B_N_Dark Elf_*` |
| Creature ghost | `Data Files/Meshes/r/AncestorGhost.nif`, `XAncestorGhost.nif` |
| Ghost tunic texture | `Data Files/Textures/TX_Ghostward_tunic.tga` (bundled as `Textures/ag/`) |
| Lich king texture | `Data Files/Textures/Tx_LicheKing.dds` |
