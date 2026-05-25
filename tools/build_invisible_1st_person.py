#!/usr/bin/env python3
"""
Build invisible first-person arm meshes from vanilla Xbase_anim.1st.nif.

OpenMW/Morrowind draw 1st-person arms from this skeleton NIF, not BODY slots.
Ship as Meshes/Xbase_anim.1st.nif — overrides vanilla when this mod loads (all
biped races using xbase_anim; intended for Ancestor Ghost play).

Run:
  python tools/build_invisible_1st_person.py
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
VANILLA_1ST = MORROWIND / "Meshes/Xbase_anim.1st.nif"
OUT_1ST = MOD_ROOT / "Meshes/Xbase_anim.1st.nif"

# Hide Dunmer flesh in 1st person; third-person ghost uses BODY slot meshes.
INVISIBLE_TRIS = (
    "Tri Left Hand",
    "Tri Right Hand",
    "Tri Left Wrist",
    "Tri Right Wrist",
    "Tri Left Forearm",
    "Tri Right Forearm",
    "Tri Left Upper Arm",
    "Tri Right Upper Arm",
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
    alpha = nif.NiAlphaProperty()
    alpha.alpha_testing = True
    alpha.test_mode = "NEVER"
    alpha.test_ref = 0
    return alpha


def _collapse_to_point(shape: nif.NiTriShape) -> None:
    verts = np.array(shape.data.vertices, copy=True)
    if len(verts) == 0:
        return
    center = verts.mean(axis=0)
    shape.data.vertices = np.tile(center, (len(verts), 1))


def make_invisible_1st_person(vanilla_path: Path, out_path: Path) -> None:
    stream = nif.NiStream()
    stream.load(vanilla_path)

    hidden = 0
    for shape in stream.objects_of_type(nif.NiTriShape):
        if shape.name not in INVISIBLE_TRIS:
            continue
        shape.properties = [
            prop
            for prop in shape.properties
            if prop is not None and not isinstance(prop, nif.NiAlphaProperty)
        ]
        shape.properties.append(_make_invisible_alpha())
        _material_for_shape(shape).alpha = 0.0
        _collapse_to_point(shape)
        hidden += 1

    if hidden != len(INVISIBLE_TRIS):
        found = {s.name for s in stream.objects_of_type(nif.NiTriShape)}
        missing = [name for name in INVISIBLE_TRIS if name not in found]
        raise RuntimeError(f"Missing 1st-person tris: {missing}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    stream.save(out_path)
    print(
        f"Wrote {out_path} ({out_path.stat().st_size} bytes, "
        f"{hidden} invisible arm tris)"
    )


def main() -> None:
    if not VANILLA_1ST.is_file():
        raise FileNotFoundError(f"Vanilla 1st-person skeleton not found: {VANILLA_1ST}")
    make_invisible_1st_person(VANILLA_1ST, OUT_1ST)


if __name__ == "__main__":
    main()
