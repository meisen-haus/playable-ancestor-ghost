#!/usr/bin/env python3
"""
Structural diff: creature Ancestor Ghost (Bip01.001) vs playable Dunmer export (Bip01).

Explains why hand/arm pipelines fail and what the engine actually expects.

Run:
  blender --background tools/blender/ancestor_ghost.blend \\
    --python tools/blender/diff_creature_vs_playable.py

Optional report file:
  blender ... --python tools/blender/diff_creature_vs_playable.py -- \\
    --out tools/reports/creature_vs_playable.txt
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPT_DIR = Path(__file__).resolve().parent
MOD_ROOT = SCRIPT_DIR.parents[1]
IO_SCENE_MW = MOD_ROOT / "tools" / "downloads" / "io_scene_mw"
MORROWIND = Path(r"C:/Morrowind/Data Files")
VANILLA_SKINS = MORROWIND / "Meshes/b/B_N_Dark Elf_M_Skins.NIF"
AG_CHEST = MOD_ROOT / "Meshes/ag/ag_chest.nif"

if str(IO_SCENE_MW) not in sys.path:
    sys.path.insert(0, str(IO_SCENE_MW))

from es3 import nif  # noqa: E402

CREATURE_ARM = "Bip01.001"
PLAYABLE_ARM = "Bip01"

CREATURE_HANDS = ("Tri hand", "Tri hand01")
CREATURE_ROBE = ("Tri robe front", "Tri robe back")
DUNMER_HAND_R = "Tri Right Hand 0"
DUNMER_HAND_L = "Tri Left Hand 0"
DUNMER_CHEST = "Tri Chest"

HAND_BONE_REMAP = {
    "Bip01 Hand.R": "Bip01 Finger21.R",
    "Bip01 Finger01.R": "Bip01 Finger11.R",
    "Bip01 Finger02.R": "Bip01 Finger1.R",
    "Bip01 Finger11.R": "Bip01 Finger11.R",
    "Bip01 Finger12.R": "Bip01 Finger1.R",
    "Bip01 Finger21.R": "Bip01 Finger21.R",
    "Bip01 Finger22.R": "Bip01 Finger2.R",
    "Bip01 Finger31.R": "Bip01 Finger21.R",
    "Bip01 Finger32.R": "Bip01 Finger2.R",
    "Bip01 Finger41.R": "Bip01 Finger21.R",
    "Bip01 Finger42.R": "Bip01 Finger2.R",
    "Bip01 Hand.L": "Bip01 Finger21.L",
    "Bip01 Finger01.L": "Bip01 Finger11.L",
    "Bip01 Finger02.L": "Bip01 Finger1.L",
    "Bip01 Finger11.L": "Bip01 Finger11.L",
    "Bip01 Finger12.L": "Bip01 Finger1.L",
    "Bip01 Finger21.L": "Bip01 Finger21.L",
    "Bip01 Finger22.L": "Bip01 Finger2.L",
    "Bip01 Finger31.L": "Bip01 Finger21.L",
    "Bip01 Finger32.L": "Bip01 Finger2.L",
    "Bip01 Finger41.L": "Bip01 Finger21.L",
    "Bip01 Finger42.L": "Bip01 Finger2.L",
}


def _world_centroid(obj: bpy.types.Object) -> Vector:
    mw = obj.matrix_world
    center = Vector((0.0, 0.0, 0.0))
    for vert in obj.data.vertices:
        center += mw @ vert.co
    return center / len(obj.data.vertices)


def _vertex_group_summary(obj: bpy.types.Object) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for vert in obj.data.vertices:
        for group in vert.groups:
            counts[obj.vertex_groups[group.group].name] += 1
    return dict(sorted(counts.items()))


def _bone_head_delta(bname: str) -> tuple[bool, bool, float | None]:
    arm0 = bpy.data.objects.get(PLAYABLE_ARM)
    arm1 = bpy.data.objects.get(CREATURE_ARM)
    if arm0 is None or arm1 is None:
        return False, False, None
    b0 = arm0.data.bones.get(bname)
    b1 = arm1.data.bones.get(bname)
    if b0 is None or b1 is None:
        return b0 is not None, b1 is not None, None
    p0 = arm0.matrix_world @ b0.head_local
    p1 = arm1.matrix_world @ b1.head_local
    return True, True, (p0 - p1).length


def _nif_tri_stats(path: Path) -> dict[str, dict]:
    if not path.is_file():
        return {}
    stream = nif.NiStream()
    stream.load(path)
    out: dict[str, dict] = {}
    import numpy as np

    for tri in stream.objects_of_type(nif.NiTriShape):
        verts = np.array(tri.data.vertices)
        entry: dict = {
            "verts": len(verts),
            "center": tuple(round(float(x), 2) for x in verts.mean(axis=0)),
            "span": tuple(round(float(x), 2) for x in (verts.max(axis=0) - verts.min(axis=0))),
        }
        if tri.skin:
            entry["skin_root"] = tri.skin.root.name if tri.skin.root else None
            entry["bones"] = [b.name for b in tri.skin.bones if b]
        out[tri.name] = entry
    return out


def _section(lines: list[str], title: str) -> None:
    lines.append("")
    lines.append("=" * 72)
    lines.append(title)
    lines.append("=" * 72)


def build_report() -> str:
    lines: list[str] = []
    lines.append("CREATURE vs PLAYABLE — Ancestor Ghost body port diff")
    lines.append(f"Blend: {SCRIPT_DIR / 'ancestor_ghost.blend'}")

    _section(lines, "1. RIG: Bip01 (playable) vs Bip01.001 (creature)")
    arm0 = bpy.data.objects.get(PLAYABLE_ARM)
    arm1 = bpy.data.objects.get(CREATURE_ARM)
    if arm0 and arm1:
        b0 = {b.name for b in arm0.data.bones}
        b1 = {b.name for b in arm1.data.bones}
        only_creature = sorted(b1 - b0)
        lines.append(f"Shared bones: {len(b0 & b1)}")
        lines.append(f"Creature-only bones ({len(only_creature)}): {', '.join(only_creature[:12])}")
        if len(only_creature) > 12:
            lines.append(f"  ... and {len(only_creature) - 12} more (tail, feet, extra finger chains)")

        lines.append("")
        lines.append("Hand/finger rest-pose delta (world space, same bone name on both rigs):")
        for bname in (
            "Bip01 Hand.R",
            "Bip01 Finger01.R",
            "Bip01 Finger11.R",
            "Bip01 Finger1.R",
            "Bip01 Finger21.R",
        ):
            on0, on1, delta = _bone_head_delta(bname)
            if on0 and on1 and delta is not None:
                lines.append(f"  {bname}: {delta:.4f} units")
            elif on1 and not on0:
                lines.append(f"  {bname}: creature-only (different naming on Bip01)")

        lines.append("")
        lines.append("Creature finger naming vs Dunmer hand skin bones:")
        lines.append("  Creature weights: Hand + Finger01/02/11/12/21/22/31/32/41/42 (11 groups)")
        lines.append("  Dunmer Hand 0 skin: Finger1, Finger11, Finger2, Finger21 only (4 bones, NO Hand)")
        lines.append("  Dunmer also has Hand 1 + Hand 2 tris per side (not in ag_chest export)")

    _section(lines, "2. MESH INVENTORY (blend file)")
    rows = [
        ("Creature robe", CREATURE_ROBE, CREATURE_ARM),
        ("Creature hands", CREATURE_HANDS, CREATURE_ARM),
        ("Dunmer chest ref", (DUNMER_CHEST,), PLAYABLE_ARM),
        ("Dunmer hand ref", (DUNMER_HAND_R, DUNMER_HAND_L), PLAYABLE_ARM),
    ]
    for label, names, arm_name in rows:
        lines.append(f"\n{label} (armature {arm_name}):")
        for name in names:
            obj = bpy.data.objects.get(name)
            if obj is None:
                lines.append(f"  MISSING {name}")
                continue
            mod_arm = next((m.object.name for m in obj.modifiers if m.type == "ARMATURE"), None)
            lines.append(
                f"  {name}: {len(obj.data.vertices)} verts, "
                f"{len(obj.vertex_groups)} vgroups, modifier arm={mod_arm}"
            )

    _section(lines, "3. WEIGHT SYSTEM COMPARISON")
    for side, creature, dunmer in (
        ("RIGHT", "Tri hand", DUNMER_HAND_R),
        ("LEFT", "Tri hand01", DUNMER_HAND_L),
    ):
        lines.append(f"\n{side} hand:")
        c_obj = bpy.data.objects.get(creature)
        d_obj = bpy.data.objects.get(dunmer)
        if c_obj:
            lines.append(f"  Creature {creature}:")
            for gn, count in _vertex_group_summary(c_obj).items():
                mapped = HAND_BONE_REMAP.get(gn, gn)
                lines.append(f"    {gn} ({count} verts) -> {mapped}")
        if d_obj:
            lines.append(f"  Dunmer {dunmer}:")
            for gn, count in _vertex_group_summary(d_obj).items():
                lines.append(f"    {gn} ({count} verts)")

    _section(lines, "4. WORLD ALIGNMENT (before export)")
    for creature, dunmer in (("Tri hand", DUNMER_HAND_R), ("Tri hand01", DUNMER_HAND_L)):
        c = bpy.data.objects.get(creature)
        d = bpy.data.objects.get(dunmer)
        if c and d:
            cc, dc = _world_centroid(c), _world_centroid(d)
            lines.append(f"  {creature} centroid {tuple(round(x, 3) for x in cc)}")
            lines.append(f"  {dunmer} centroid {tuple(round(x, 3) for x in dc)}")
            lines.append(f"  delta {tuple(round(x, 3) for x in (dc - cc))}")

    _section(lines, "5. NIF BIND SPACE — vanilla Skins vs ag_chest.nif")
    vanilla = _nif_tri_stats(VANILLA_SKINS)
    exported = _nif_tri_stats(AG_CHEST)
    for tri_name in (DUNMER_CHEST, DUNMER_HAND_R, DUNMER_HAND_L):
        lines.append(f"\n{tri_name}:")
        for label, data in (("vanilla", vanilla.get(tri_name)), ("ag_chest", exported.get(tri_name))):
            if not data:
                lines.append(f"  {label}: (missing)")
                continue
            lines.append(
                f"  {label}: {data['verts']} verts, center {data['center']}, span {data['span']}"
            )
            if "bones" in data:
                lines.append(f"    skin root {data.get('skin_root')}, bones {data['bones']}")

    _section(lines, "6. WHY EACH PIPELINE BEHAVES THE WAY IT DOES")
    lines.append(
        "STRETCHED HANDS (creature weights on Bip01, early exports):\n"
        "  - Mesh WAS skinned; vertices followed bones at runtime.\n"
        "  - Creature finger bones (Finger02/12/22...) don't exist on Bip01 -> spikes to origin.\n"
        "  - Even after name remap, bind matrices differ (~0.55u on shared hand bones).\n"
        "  - Result: wrong pose but SKELETON-CONNECTED."
    )
    lines.append("")
    lines.append(
        "CURRENT GRAFT (static mesh + copy vanilla NiSkinInstance + bbox-fit):\n"
        "  - _apply_modifiers BAKES Bip01.001 armature -> destroys 11 weight groups.\n"
        "  - Weights stripped; vanilla skin pasted with nearest-vertex on reshaped mesh.\n"
        "  - Vert positions forced into vanilla bbox (+ 1.5x scale) -> looks placed but\n"
        "    weight/bind relationship is wrong -> invisible, inside body, or rubbery."
    )
    lines.append("")
    lines.append(
        "APPLY-ARMATURE TRAP:\n"
        "  _apply_modifiers() on creature hands collapses all 11 groups to 1 (Finger21).\n"
        "  Never apply the creature armature modifier when preserving weights."
    )

    _section(lines, "7. RECOMMENDED FIX (hands + arms)")
    lines.append(
        "HANDS:\n"
        "  1. Duplicate Tri hand/hand01; REMOVE Bip01.001 armature mod (do not apply).\n"
        "  2. World-align to Dunmer Tri * Hand 0 reference.\n"
        "  3. Remap 11 creature groups -> 4 Dunmer finger bones (see HAND_BONE_REMAP).\n"
        "  4. Transform verts into Dunmer hand bind space (ref.matrix_world).\n"
        "  5. Export SKINNED on Bip01 — no NIF vertex graft.\n"
        "  6. Post-process: rename tris, texture, ensure skin root = UpperArm only."
    )
    lines.append("")
    lines.append(
        "ARMS (hide Dunmer flesh, keep skeleton):\n"
        "  - Use full vanilla wrist/forearm/upperarm NIF copies with alpha=0\n"
        "    (tools/build_invisible_stubs.py). Do NOT collapse geometry to a point.\n"
        "  - ESP must point Wrist/Forearm/UpperArm at ag\\ag_*.nif stubs.\n"
        "  - Alternative later: extend ghost robe mesh in chest NIF to cover arms."
    )
    lines.append("")
    lines.append(
        "NOT RECOMMENDED:\n"
        "  - NIF skin graft with bbox-fit / centroid-fit on hand verts\n"
        "  - Applying creature armature before weight remap\n"
        "  - Pointing arm slots at vanilla Dunmer paths (visible flesh)"
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []

    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, help="Write report to this file")
    args = parser.parse_args(argv)

    report = build_report()
    print(report)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
