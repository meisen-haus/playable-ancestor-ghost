# Body slots — current shipping state

All BODY records in `tools/build_esp.mjs` point at `Meshes/ag/` assets below.

| Slot | ESP path | Source | Notes |
|------|----------|--------|-------|
| Head | `ag\ag_head.nif` | `tools/blender/build_vanilla_head_nif.py` | Morpher head |
| Hair | `ag\ag_hair.nif` | `tools/build_invisible_stubs.py` | Invisible stub |
| Neck | `ag\ag_neck.nif` | `tools/build_invisible_stubs.py` | Invisible stub |
| Chest | `ag\ag_chest.nif` | skin ref + `build_vanilla_chest_nif.py` | Pack bind-pose robe; Pelvis/Spine folded → Spine1/Spine2 (float); sleeve chain to Hand; tunic TGA |
| Hand | `ag\ag_hand.nif` | same builder + `tools/reference/ag_hand_skin_ref.nif` | Pack-style Hand/Finger/Forearm bind pose + `Tx_LicheKing.dds` |
| Groin | `ag\ag_groin.nif` | `tools/build_invisible_stubs.py` | Invisible stub |
| Wrist / Forearm / UpperArm | `ag\ag_*.nif` | `tools/build_invisible_stubs.py` | Invisible stubs |
| Foot / Ankle / Knee / UpperLeg | `ag\ag_*.nif` | `tools/build_invisible_stubs.py` | Invisible stubs |

1st-person:
- `Meshes/Xbase_anim.1st.nif` via `tools/build_invisible_1st_person.py` (hides Dunmer wrist/forearm/upper-arm shapes)
- BODY `ag_chest_{m,f}.1st` → `ag\ag_chest.nif` (full robe torso when looking down)
- BODY `ag_hand_{m,f}.1st` → `ag\ag_hand.nif` (bony hands)

Slot layout (separate Hand BODY, Chest `*.1st` sleeves) and bind-pose skinning follow the **Playable Creature Race Pack** as a structural reference (`tools/reference/`). Shipping chest/hand NIFs are written from those skin refs with our textures + float reweight; head is Blender-built from vanilla morpher geometry. See [tools/reference/README.md](reference/README.md).

## Full mesh rebuild

From repo root (Blender 5.1+, Morrowind at `C:/Morrowind/Data Files`):

```powershell
blender --background --addons io_scene_mw tools/blender/ancestor_ghost.blend --python tools/blender/build_vanilla_chest_nif.py
blender --background --addons io_scene_mw tools/blender/ancestor_ghost.blend --python tools/blender/build_vanilla_head_nif.py
blender --background --python tools/build_invisible_stubs.py
blender --background --python tools/build_invisible_1st_person.py
node tools/build_esp.mjs
```

## Dev diff report (optional)

```powershell
blender --background tools/blender/ancestor_ghost.blend --python tools/blender/diff_body_slots.py
```

## Mesh format comparison

| | Head | Chest / arms_1st | Hand |
|---|------|------------------|------|
| Root | Part-named NiNode (no Bip01) | `Bip01` | `Bip01` |
| Deformation | `NiGeomMorpherController` | Weighted `NiSkinInstance` (Dunmer nearest transfer) | Hand-bone skin |
| Tri names | contains `Head` | `Tri Chest` | `Tri Left Hand 0`, `Tri Right Hand 0` |
| Texture | `ag\TX_Ghostward_tunic.tga` | `ag\TX_Ghostward_tunic.tga` | `textures\Tx_LicheKing.dds` (vanilla) |
