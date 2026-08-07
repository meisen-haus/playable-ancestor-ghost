# Skinning references (`tools/reference/`)

**Not shipped in the mod zip.** Release builds use the committed `Meshes/ag/*.nif` files; the GitHub release workflow only rebuilds `ancestor_ghost.omwaddon`.

Optional local NIF copies here are used only when re-running:

```powershell
blender --background --addons io_scene_mw tools/blender/ancestor_ghost.blend --python tools/blender/build_vanilla_chest_nif.py
```

That script prefers a local install of **[Playable Creature Race Pack](https://www.nexusmods.com/morrowind/mods/45104)** by **[PsychoGherkin](https://www.nexusmods.com/profile/PsychoGherkin)** (see paths in `build_vanilla_chest_nif.py`), copies bind-pose ghosts into this folder, rewrites textures, applies the float reweight, and writes `Meshes/ag/`. The `*_skin_ref.nif` files are **gitignored** so pack geometry is not committed.

| Local file (gitignored) | Role |
|-------------------------|------|
| `ag_chest_skin_ref.nif` | Robe + sleeve skin (Clavicle→Hand) |
| `ag_arms_1st_skin_ref.nif` | Optional arms-only skin ref |
| `ag_hand_skin_ref.nif` | Bony hands (Hand/Finger/Forearm) |

## Provenance / credit

Bind-pose skinning and BODY slot layout were informed by **[Playable Creature Race Pack](https://www.nexusmods.com/morrowind/mods/45104)** by **[PsychoGherkin](https://www.nexusmods.com/profile/PsychoGherkin)** — specifically the ghost meshes (`Ghost_chest.nif`, `Ghost_arms.nif`, `Ghost_Hand.nif`) — as a **structural reference** only. This mod does not depend on or redistribute that pack. Shipping tunic TGA, head mesh, and Lua idle-float are ours / vanilla.
