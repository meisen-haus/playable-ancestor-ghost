# Vanilla-format head export (`ag_head.nif`)

Morrowind **Head** BODY slots use a different NIF layout than chest/legs:

| Head slot | Chest / leg slots |
|-----------|-------------------|
| Root `NiNode` named after the part (`ag_head_m_01`) | Root `NiNode` = `Bip01` skeleton |
| **No skeleton** in the file | Full `Bip01` + `NiSkinInstance` |
| **`NiGeomMorpherController`** + `NiMorphData` | Weighted skinning only |
| Tri name contains **`Head`** (`Tri ag_head_m_01`) | Tri name contains slot (`Tri Chest`) |

The automated builder lives at `tools/blender/build_vanilla_head_nif.py`.

## Prerequisites

1. **Blender 4.2+** with [io_scene_mw](https://github.com/Greatness7/io_scene_mw) enabled  
   (a copy is in `tools/downloads/io_scene_mw/` — install via *Edit → Preferences → Add-ons → Install*).
2. **`tools/blender/ancestor_ghost.blend`** containing:
   - Joined ghost geometry as `ag_head_geo`
   - Dunmer reference mesh `Tri B_N_Dark Elf_M_Head_01` (import the vanilla head NIF once for alignment)
3. **Vanilla Dunmer head** at  
   `C:/Morrowind/Data Files/Meshes/b/B_N_Dark Elf_M_Head_01.NIF`
4. **Texture** at `Textures/ag/TX_Ghostward_tunic.tga`

## One-command build

From the repo root:

```powershell
& "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" `
  --background tools/blender/ancestor_ghost.blend `
  --python tools/blender/build_vanilla_head_nif.py
```

Output: `Meshes/ag/ag_head.nif`  
Previous skinned export (if any) is saved to `Meshes/ag/ag_head.skinned_backup.nif`.

## What the script does

1. Joins `ag_head_geo*` meshes, removes armature modifiers, aligns to `Tri B_N_Dark Elf_M_Head_01`.
2. Parents mesh under empty root `ag_head_m_01`; renames tri to **`Tri ag_head_m_01`**.
3. Exports a **static** mesh NIF (no skeleton) via io_scene_mw.
4. Post-processes with the es3 library:
   - Adds **basis-only** `NiMorphData` + `NiGeomMorpherController`
   - Copies **NiTextKeyExtraData** + **NiVertexColorProperty** from the vanilla Dunmer head
   - **Rotates -90° Z** in Blender to match Dunmer head forward (ghost rig offset)
   - Sets texture path to `ag\TX_Ghostward_tunic.tga`
   - Strips `NiAlphaProperty` / `NiSkinInstance`

## Manual fallback (NifSkope)

If the script fails, use NifSkope 2.0 (MW 4.0.0.2):

1. Open `B_N_Dark Elf_M_Head_01.NIF` → **Save As** `Meshes/ag/ag_head.nif`.
2. Rename root node → `ag_head_m_01`; tri shape → `Tri ag_head_m_01`.
3. Export ghost geometry from Blender as **OBJ** (no armature), aligned to the Dunmer head.
4. In NifSkope: replace the tri shape vertices / swap the mesh block (keep `NiGeomMorpherController`, `NiMorphData`, text keys).
5. Update **NiSourceTexture** → `ag\TX_Ghostward_tunic.tga`.
6. Remove any **NiAlphaProperty** blocks.

## Test in OpenMW

1. ESP already points at `ag\ag_head.nif` — no rebuild needed unless you changed paths.
2. Restart OpenMW, load char gen or your save.
3. **`luap`** → `debug.toggleRenderMode(debug.RENDER_MODE.Wireframe)` — you should see head wireframe at the neck.
4. If still missing, temporarily set `HEAD_VARIANTS` to the Dunmer head path in `build_esp.mjs` to confirm slot wiring.

## Notes

- **Face sliders** won't morph the ghost hood (basis-only morpher). That is fine for a single fixed ghost face.
- **Neck** stays a separate BODY slot (`B_N_Dark Elf_M_Neck.NIF`) — do not merge neck into the head NIF.
- Char-gen expects **1 head + 1 hair** per gender (`build_esp.mjs` already enforces this).
