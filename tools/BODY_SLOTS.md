# Body slots — current shipping state

All BODY records in `tools/build_esp.mjs` point at `Meshes/ag/` assets below.

| Slot | ESP path | Source | Notes |
|------|----------|--------|-------|
| Head | `ag\ag_head.nif` | `tools/blender/build_vanilla_head_nif.py` | Morpher head |
| Hair | `ag\ag_hair.nif` | `tools/build_invisible_stubs.py` | Invisible stub |
| Neck | `ag\ag_neck.nif` | `tools/build_invisible_stubs.py` | Invisible stub |
| Chest | `ag\ag_chest.nif` | Creature Pack `Ghost_chest.nif` | Weighted robe (deforms with animation) |
| Hand | `ag\ag_hand.nif` | Creature Pack `Ghost_Hand.nif` | Bony ghost hands, finger-bone weights |
| Groin | `ag\ag_groin.nif` | `tools/build_invisible_stubs.py` | Invisible stub |
| Wrist / Forearm / UpperArm | `ag\ag_*.nif` | `tools/build_invisible_stubs.py` | Invisible stubs |
| Foot / Ankle / Knee / UpperLeg | `ag\ag_*.nif` | `tools/build_invisible_stubs.py` | Invisible stubs |

1st-person: `Meshes/Xbase_anim.1st.nif` via `tools/build_invisible_1st_person.py` (hides arm shapes; hand body parts render via OpenMW attachment).

Reference asset: `Meshes/ag/ag_arms_1st.nif` — creature pack ghost arms mesh for future first-person sleeve work.

## Full mesh rebuild

From repo root (Blender 5.1+, Morrowind at `C:/Morrowind/Data Files`):

```powershell
blender --background --addons io_scene_mw tools/blender/ancestor_ghost.blend --python tools/blender/build_vanilla_head_nif.py
blender --background --python tools/build_invisible_stubs.py
blender --background --python tools/build_invisible_1st_person.py
node tools/build_esp.mjs
```

Chest and hand NIFs (`ag_chest.nif`, `ag_hand.nif`) are adapted directly from the Playable Creature Race Pack and do not require Blender rebuild.

## Dev diff report (optional)

```powershell
blender --background tools/blender/ancestor_ghost.blend --python tools/blender/diff_body_slots.py
```

## Mesh format comparison

| | Head | Chest | Hand |
|---|------|-------|------|
| Root | Part-named NiNode (no Bip01) | `Bip01` | `Bip01` |
| Deformation | `NiGeomMorpherController` | Weighted `NiSkinInstance` (spine/arm bones) | Weighted `NiSkinInstance` (finger bones) |
| Tri names | contains `Head` | `Tri Chest` | `Tri Left Hand`, `Tri Right Hand` |
| Texture | `ag\TX_Ghostward_tunic.tga` | `textures\tx_ghostward_tunic.dds` (vanilla) | `textures\tx_licheking.dds` (vanilla) |
