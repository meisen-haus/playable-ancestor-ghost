#!/usr/bin/env python3
"""
Compare Ancestor Ghost creature body geometry vs vanilla Dunmer BODY slots.

Prints a slot-by-slot report: what the engine expects, what's in the blend file,
what's already exported under Meshes/ag/, and what's still Dunmer/stub in the ESP.

Run from repo root:
  blender --background tools/blender/ancestor_ghost.blend --python tools/blender/diff_body_slots.py

Optional report file:
  blender ... --python tools/blender/diff_body_slots.py -- --out tools/reports/body_slot_diff.txt
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPT_DIR = Path(__file__).resolve().parent
MOD_ROOT = SCRIPT_DIR.parents[1]
IO_SCENE_MW = MOD_ROOT / "tools" / "downloads" / "io_scene_mw"
MORROWIND = Path(r"C:/Morrowind/Data Files")
MESHES_B = MORROWIND / "Meshes/b"
AG_MESHES = MOD_ROOT / "Meshes/ag"
TEXTURE_PATH = r"ag\TX_Ghostward_tunic.tga"

if str(IO_SCENE_MW) not in sys.path:
    sys.path.insert(0, str(IO_SCENE_MW))

from es3 import nif  # noqa: E402


@dataclass
class SlotSpec:
    name: str
    part_index: int
    vanilla_mesh: str
    vanilla_tri_names: list[str]
    nif_format: str  # morpher | skinned_bip01 | simple_tri
    ghost_blend_meshes: list[str]
    dunmer_reference: str | None
    target_ag_nif: str | None
    esp_status: str
    notes: str = ""


SLOTS: list[SlotSpec] = [
    SlotSpec(
        "Head",
        0,
        "B_N_Dark Elf_M_Head_01.NIF",
        ["Tri B_N_Dark Elf_M_Head_01"],
        "morpher",
        ["ag_head_geo"],
        "Tri B_N_Dark Elf_M_Head_01",
        "ag\\ag_head.nif",
        "custom (ag_head.nif)",
        "NiGeomMorpher — use build_vanilla_head_nif.py",
    ),
    SlotSpec(
        "Hair",
        1,
        "(stub)",
        [],
        "stub",
        [],
        None,
        "ag\\ag_hair.nif",
        "invisible stub",
    ),
    SlotSpec(
        "Neck",
        2,
        "B_N_Dark Elf_M_Neck.NIF",
        ["B_N_Dark Elf_M_Neck"],
        "simple_tri",
        [],
        None,
        None,
        "vanilla Dunmer",
        "No creature neck mesh — keep Dunmer or retexture later",
    ),
    SlotSpec(
        "Chest",
        3,
        "B_N_Dark Elf_M_Skins.NIF",
        ["Tri Chest"],
        "skinned_bip01",
        ["Tri robe front", "Tri robe back"],
        "Tri Chest",
        "ag\\ag_chest.nif",
        "custom (ag_chest.nif)",
        "Join robe front+back → Tri Chest on Bip01; build_vanilla_chest_nif.py",
    ),
    SlotSpec(
        "Groin",
        4,
        "B_N_Dark Elf_M_Groin.NIF",
        ["B_N_Dark Elf_M_Groin"],
        "simple_tri",
        [],
        None,
        "ag\\ag_groin.nif",
        "vanilla Dunmer",
        "Robe may cover this — custom groin optional",
    ),
    SlotSpec(
        "Hand",
        5,
        "B_N_Dark Elf_M_Skins.NIF",
        [
            "Tri Left Hand 0",
            "Tri Left Hand 1",
            "Tri Left Hand 2",
            "Tri Right Hand 0",
            "Tri Right Hand 1",
            "Tri Right Hand 2",
        ],
        "skinned_bip01",
        ["Tri hand", "Tri hand01"],
        "Tri Left Hand 0",
        "ag\\ag_chest.nif",
        "custom (ag_chest.nif)",
        "Usually exported in same NIF as chest; build_vanilla_chest_nif.py",
    ),
    SlotSpec(
        "Wrist",
        6,
        "B_N_Dark Elf_M_Wrist.NIF",
        ["Tri B_N_Dark Elf_M_Wrist"],
        "simple_tri",
        [],
        None,
        "ag\\ag_wrist.nif",
        "vanilla Dunmer",
        "Small cuff slot — stub, retexture, or extend hand mesh",
    ),
    SlotSpec(
        "Forearm",
        7,
        "B_N_Dark Elf_M_Forearm.NIF",
        ["B_N_Dark Elf_M_Forearm"],
        "simple_tri",
        [],
        None,
        "ag\\ag_forearm.nif",
        "vanilla Dunmer",
        "Hidden under robe — often left Dunmer or stubbed",
    ),
    SlotSpec(
        "UpperArm",
        8,
        "B_N_Dark Elf_M_Upper Arm.NIF",
        ["B_N_Dark Elf_M_Upper Arm"],
        "simple_tri",
        [],
        None,
        "ag\\ag_upperarm.nif",
        "vanilla Dunmer",
        "Hidden under robe — often left Dunmer or stubbed",
    ),
    SlotSpec(
        "Foot",
        9,
        "ag\\ag_foot.nif",
        [],
        "stub",
        [],
        None,
        "ag\\ag_foot.nif",
        "invisible stub",
    ),
    SlotSpec(
        "Ankle",
        10,
        "ag\\ag_ankle.nif",
        [],
        "stub",
        [],
        None,
        "ag\\ag_ankle.nif",
        "invisible stub",
    ),
    SlotSpec(
        "Knee",
        11,
        "ag\\ag_knee.nif",
        [],
        "stub",
        [],
        None,
        "ag\\ag_knee.nif",
        "invisible stub",
    ),
    SlotSpec(
        "UpperLeg",
        12,
        "ag\\ag_upperleg.nif",
        [],
        "stub",
        [],
        None,
        "ag\\ag_upperleg.nif",
        "invisible stub",
    ),
]


def _ensure_object_mode() -> None:
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def _bounds(obj: bpy.types.Object) -> dict:
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    xs = [c.x for c in corners]
    ys = [c.y for c in corners]
    zs = [c.z for c in corners]
    center = Vector((sum(xs) / 8, sum(ys) / 8, sum(zs) / 8))
    size = Vector((max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)))
    return {
        "center": center,
        "size": size,
        "verts": len(obj.data.vertices) if obj.data else 0,
        "parent": obj.parent.name if obj.parent else None,
        "material": obj.active_material.name if obj.active_material else None,
    }


def _analyze_nif(path: Path) -> dict | None:
    if not path.is_file():
        return None
    stream = nif.NiStream()
    stream.load(path)
    tris = [shape.name for shape in stream.objects_of_type(nif.NiTriShape)]
    return {
        "size": path.stat().st_size,
        "root": stream.root.name if stream.root else None,
        "tris": tris,
        "skin_count": sum(1 for _ in stream.objects_of_type(nif.NiSkinInstance)),
        "morpher": any(True for _ in stream.objects_of_type(nif.NiGeomMorpherController)),
        "alpha": any(True for _ in stream.objects_of_type(nif.NiAlphaProperty)),
        "bip01_nodes": sum(
            1 for node in stream.objects_of_type(nif.NiNode) if node.name.startswith("Bip01")
        ),
    }


def _vanilla_path(filename: str) -> Path | None:
    if not filename or filename.startswith("ag\\") or filename == "(stub)":
        return None
    return MESHES_B / filename


def _ag_path(modl: str | None) -> Path | None:
    if not modl or not modl.lower().startswith("ag\\"):
        return None
    return AG_MESHES / modl.split("\\", 1)[1]


def _format_vector(vec: Vector) -> str:
    return f"({vec.x:+.3f}, {vec.y:+.3f}, {vec.z:+.3f})"


def _compare_centers(ghost_names: list[str], reference_name: str | None, lines: list[str]) -> None:
    if not ghost_names or not reference_name:
        return
    ref = bpy.data.objects.get(reference_name)
    if ref is None:
        lines.append(f"    reference missing in blend: {reference_name}")
        return
    ref_bounds = _bounds(ref)
    lines.append(f"    Dunmer ref '{reference_name}': center {_format_vector(ref_bounds['center'])} "
                 f"size {_format_vector(ref_bounds['size'])} verts {ref_bounds['verts']}")
    for name in ghost_names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            lines.append(f"    ghost '{name}': MISSING in blend")
            continue
        gb = _bounds(obj)
        delta = gb["center"] - ref_bounds["center"]
        lines.append(
            f"    ghost '{name}': center {_format_vector(gb['center'])} "
            f"size {_format_vector(gb['size'])} verts {gb['verts']} parent={gb['parent']} "
            f"Δcenter {_format_vector(delta)}"
        )


def _compare_nif_pair(
    vanilla: Path | None, custom: Path | None, slot_name: str, lines: list[str]
) -> None:
    v = _analyze_nif(vanilla) if vanilla else None
    c = _analyze_nif(custom) if custom else None
    if v:
        lines.append(f"    vanilla NIF: root={v['root']} tris={v['tris']} skin={v['skin_count']} "
                     f"morpher={v['morpher']} alpha={v['alpha']} bip01={v['bip01_nodes']}")
    elif vanilla:
        lines.append(f"    vanilla NIF: NOT FOUND ({vanilla})")
    if c:
        lines.append(f"    custom  NIF: root={c['root']} tris={c['tris']} skin={c['skin_count']} "
                     f"morpher={c['morpher']} alpha={c['alpha']} bip01={c['bip01_nodes']}")
    elif custom:
        lines.append(f"    custom  NIF: not exported yet ({custom.name})")
    if v and c:
        lines.append("    format diff:")
        lines.append(f"      root: {v['root']} → {c['root']}")
        lines.append(f"      morpher: {v['morpher']} → {c['morpher']}  (head=morpher, body=skinned)")
        lines.append(f"      alpha: {v['alpha']} → {c['alpha']}  (strip NiAlphaProperty on body exports)")
        missing = [t for t in v["tris"] if not any(t.lower() in ct.lower() or ct.lower() in t.lower() for ct in c["tris"])]
        if missing and slot_name not in ("Head", "Hair"):
            lines.append(f"      tri names still expected: {missing}")


def build_report() -> str:
    _ensure_object_mode()
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("Ancestor Ghost — body slot diff (creature vs Dunmer vs ESP)")
    lines.append("=" * 72)
    lines.append("")
    lines.append("Blend armatures:")
    for obj in sorted(bpy.data.objects, key=lambda o: o.name):
        if obj.type == "ARMATURE":
            lines.append(f"  {obj.name}  parent={obj.parent.name if obj.parent else None}")
    lines.append("")
    lines.append("REMAINING CUSTOM WORK (visible ghost body):")
    lines.append("  • Chest  — join Tri robe front + Tri robe back → ag_chest.nif (Tri Chest, Bip01 skin)")
    lines.append("  • Hands  — Tri hand + Tri hand01 → same NIF, Dunmer hand tri names")
    lines.append("  • Optional: groin / arm stubs if Dunmer skin shows through the robe")
    lines.append("")
    lines.append("ALREADY DONE / PLACEHOLDER:")
    lines.append("  • Head (ag_head.nif), hair stub, leg stubs, Chameleon, ESP/Lua")
    lines.append("  • Neck + upper arm chain still vanilla Dunmer in build_esp.mjs")
    lines.append("")

    for slot in SLOTS:
        lines.append("-" * 72)
        lines.append(f"{slot.name}  (BODY part index {slot.part_index})")
        lines.append(f"  ESP now: {slot.esp_status}")
        lines.append(f"  NIF format: {slot.nif_format}")
        if slot.target_ag_nif:
            lines.append(f"  Target: {slot.target_ag_nif}")
        if slot.notes:
            lines.append(f"  Note: {slot.notes}")

        vanilla = _vanilla_path(slot.vanilla_mesh)
        custom = _ag_path(slot.target_ag_nif)
        _compare_nif_pair(vanilla, custom, slot.name, lines)
        _compare_centers(slot.ghost_blend_meshes, slot.dunmer_reference, lines)

        if slot.ghost_blend_meshes:
            for name in slot.ghost_blend_meshes:
                obj = bpy.data.objects.get(name)
                if obj is None:
                    continue
                for mod in obj.modifiers:
                    if mod.type == "ARMATURE":
                        lines.append(f"    {name} armature modifier → {mod.object.name if mod.object else None}")

    lines.append("")
    lines.append("=" * 72)
    lines.append("FORMAT CHEAT SHEET")
    lines.append("=" * 72)
    lines.append("| Slot group      | Vanilla pattern              | Ghost source           |")
    lines.append("|-----------------|------------------------------|------------------------|")
    lines.append("| Head            | morpher, no Bip01 in file    | ag_head_geo            |")
    lines.append("| Chest + hands   | Bip01 root + NiSkinInstance  | robe + creature hands  |")
    lines.append("| Groin           | simple tri, no skeleton      | (optional)             |")
    lines.append("| Wrist/forearm   | simple tri                   | usually Dunmer/stub    |")
    lines.append("| Legs            | invisible stubs              | ag_*leg*.nif (done)    |")
    lines.append("")
    lines.append("Next export script to add: tools/blender/build_vanilla_chest_nif.py")
    lines.append("  (skinned export — mirror Dunmer Skins.nif, not morpher head pipeline)")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--out", type=Path, default=None, help="Write report to this file")
    # Blender passes its own args after "--"
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args(sys.argv)
    report = build_report()
    print(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
        print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
