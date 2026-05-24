# Body slots — what remains

Head export is done (`build_vanilla_head_nif.py`). For the visible ghost body, **torso + hands** are the main custom mesh work.

## Run the diff report

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" `
  --background tools/blender/ancestor_ghost.blend `
  --python tools/blender/diff_body_slots.py

# optional file output
& "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" `
  --background tools/blender/ancestor_ghost.blend `
  --python tools/blender/diff_body_slots.py -- `
  --out tools/reports/body_slot_diff.txt
```

## Status by slot

| Slot | ESP today | Creature source in blend | Notes |
|------|-----------|--------------------------|-------|
| Head | `ag\ag_head.nif` | `ag_head_geo` | Done — morpher format |
| Hair | invisible stub | — | Done |
| **Chest** | Dunmer Skins | `Tri robe front`, `Tri robe back` | **TODO** → `ag_chest.nif` |
| **Hand** | Dunmer Skins | `Tri hand`, `Tri hand01` | **TODO** — same NIF as chest |
| Neck | Dunmer | — | No ghost mesh; keep or retexture |
| Groin | Dunmer | — | Optional if robe doesn't cover |
| Wrist / Forearm / UpperArm | vanilla Dunmer | Robe covers most of the arm; collapsed stubs caused distortion |
| Legs | invisible stubs | — | Done |

## Format difference (head vs body)

| | Head | Chest + hands |
|---|------|---------------|
| Root | `B_N_Dark Elf_M_Head_01` style | `Bip01` |
| Controller | `NiGeomMorpherController` | `NiSkinInstance` per tri |
| Tri names | contains `Head` | `Tri Chest`, `Tri Left Hand 0`… |
| Skeleton in file | none | full `Bip01` hierarchy |

Body export should follow **Dunmer Skins.nif**, not the head morpher pipeline.

## Chest + hands export

Automated builder: `tools/blender/build_vanilla_chest_nif.py`

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" `
  --background tools/blender/ancestor_ghost.blend `
  --python tools/blender/build_vanilla_chest_nif.py

node tools/build_esp.mjs
```

Output: `Meshes/ag/ag_chest.nif` (Chest + Hand BODY slots). ESP points both slots at this path.
