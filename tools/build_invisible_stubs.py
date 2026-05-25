#!/usr/bin/env python3
"""
Build invisible BODY-slot stubs from vanilla Dunmer meshes.

OpenMW ignores NiMaterialProperty.alpha on skin slots — use NiAlphaProperty
(alpha test NEVER) so hidden flesh slots do not render.

Output: Meshes/ag/ag_{wrist,forearm,upperarm,neck,groin,foot,ankle,knee,upperleg,hair}.nif

Run:
  blender --background --python tools/build_invisible_stubs.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
MOD_ROOT = SCRIPT_DIR.parent
IO_SCENE_MW = MOD_ROOT / "tools" / "downloads" / "io_scene_mw"
IO_SCENE_MW_LIB = IO_SCENE_MW / "io_scene_mw" / "lib"
MORROWIND = Path(r"C:/Morrowind/Data Files")
OUT_DIR = MOD_ROOT / "Meshes/ag"

STUBS = (
    ("Meshes/b/B_N_Dark Elf_M_Wrist.NIF", "ag_wrist.nif"),
    ("Meshes/b/B_N_Dark Elf_M_Forearm.NIF", "ag_forearm.nif"),
    ("Meshes/b/B_N_Dark Elf_M_Upper Arm.NIF", "ag_upperarm.nif"),
    ("Meshes/b/B_N_Dark Elf_M_Neck.NIF", "ag_neck.nif"),
    ("Meshes/b/B_N_Dark Elf_M_Groin.NIF", "ag_groin.nif"),
    ("Meshes/b/B_N_Dark Elf_M_Foot.NIF", "ag_foot.nif"),
    ("Meshes/b/B_N_Dark Elf_M_Ankle.NIF", "ag_ankle.nif"),
    ("Meshes/b/B_N_Dark Elf_M_Knee.NIF", "ag_knee.nif"),
    ("Meshes/b/B_N_Dark Elf_M_Upper Leg.NIF", "ag_upperleg.nif"),
    ("Meshes/b/B_N_Dark Elf_M_Hair_01.NIF", "ag_hair.nif"),
)

for path in (IO_SCENE_MW_LIB, IO_SCENE_MW):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from es3 import nif  # noqa: E402


def _material_for_shape(shape: nif.NiTriShape) -> nif.NiMaterialProperty:
    for prop in shape.properties:
        if isinstance(prop, nif.NiMaterialProperty):
            return prop
    material = nif.NiMaterialProperty()
    shape.properties.append(material)
    return material


def _make_invisible_alpha() -> nif.NiAlphaProperty:
    """Reject all fragments — reliable on OpenMW body parts."""
    alpha = nif.NiAlphaProperty()
    alpha.alpha_testing = True
    alpha.test_mode = "NEVER"
    alpha.test_ref = 0
    return alpha


def _collapse_to_point(shape: nif.NiTriShape) -> None:
    """Degenerate skinned/unskinned stub geometry to a single bind point."""
    verts = np.array(shape.data.vertices, copy=True)
    if len(verts) == 0:
        return
    center = verts.mean(axis=0)
    shape.data.vertices = np.tile(center, (len(verts), 1))


def make_invisible_stub(vanilla_path: Path, out_path: Path) -> None:
    stream = nif.NiStream()
    stream.load(vanilla_path)

    for shape in stream.objects_of_type(nif.NiTriShape):
        shape.properties = [
            prop
            for prop in shape.properties
            if prop is not None and not isinstance(prop, nif.NiAlphaProperty)
        ]
        shape.properties.append(_make_invisible_alpha())
        _material_for_shape(shape).alpha = 0.0
        _collapse_to_point(shape)

    stream.save(out_path)
    print(f"  {out_path.name} ({out_path.stat().st_size} bytes, alpha test NEVER + collapsed)")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Building invisible body stubs:")
    for rel_src, out_name in STUBS:
        src = MORROWIND / rel_src
        if not src.is_file():
            raise FileNotFoundError(f"Vanilla mesh not found: {src}")
        make_invisible_stub(src, OUT_DIR / out_name)


if __name__ == "__main__":
    main()
