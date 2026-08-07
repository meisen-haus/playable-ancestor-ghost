# Skinning references (`tools/reference/`)

Bind-pose NIF copies used by `tools/blender/build_vanilla_chest_nif.py` when writing shipping body meshes. Builds rewrite textures to our tunic TGA / vanilla `Tx_LicheKing.dds`, fold chest Pelvis/Spine weights into Spine1/Spine2 for the idle-float Lua blend, and write `Meshes/ag/ag_*.nif`.

| File | Role |
|------|------|
| `ag_chest_skin_ref.nif` | Robe + sleeve skin (Clavicle→Hand) |
| `ag_arms_1st_skin_ref.nif` | Optional arms-only skin ref |
| `ag_hand_skin_ref.nif` | Bony hands (Hand/Finger/Forearm) |

## Provenance

These refs match the **Playable Creature Race Pack** (Nexus) ghost body layout (`Ghost_chest.nif`, `Ghost_arms.nif`, `Ghost_Hand.nif`) — used as a **structural / bind-pose skinning reference** only. Shipping textures and HEAD mesh are ours / vanilla; we do not redistribute the pack as a dependency.

If the pack is installed locally at `C:/meisen-haus/creature-pack/...`, the chest builder refreshes these files from that tree on each run. Otherwise the committed copies here are enough to rebuild.
