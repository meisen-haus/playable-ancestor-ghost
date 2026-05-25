# Body slots — current shipping state

All BODY records in `tools/build_esp.mjs` point at `Meshes/ag/` assets below.

| Slot | ESP path | Builder |
|------|----------|---------|
| Head | `ag\ag_head.nif` | `tools/blender/build_vanilla_head_nif.py` (morpher) |
| Hair | `ag\ag_hair.nif` | `tools/build_invisible_stubs.py` |
| Neck | `ag\ag_neck.nif` | `tools/build_invisible_stubs.py` |
| Chest, Hand | `ag\ag_chest.nif` | `tools/blender/build_vanilla_chest_nif.py` (rigid Bip01 root) |
| Groin | `ag\ag_groin.nif` | `tools/build_invisible_stubs.py` |
| Wrist / Forearm / UpperArm | `ag\ag_*.nif` | `tools/build_invisible_stubs.py` |
| Foot / Ankle / Knee / UpperLeg | `ag\ag_*.nif` | `tools/build_invisible_stubs.py` |

1st-person arms: `Meshes/Xbase_anim.1st.nif` via `tools/build_invisible_1st_person.py`.

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

## Head vs chest format

| | Head | Chest + hands |
|---|------|---------------|
| Root | Part-named NiNode (no Bip01 skeleton) | `Bip01` |
| Deformation | `NiGeomMorpherController` | Rigid `NiSkinInstance` (100% Bip01) |
| Tri names | contains `Head` | `Tri Chest`, `Tri Right Hand 0`, … |
