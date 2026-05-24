#!/usr/bin/env python3
"""
Build invisible BODY-slot arm stubs from vanilla Dunmer meshes.

Copies wrist/forearm/upperarm NIFs unchanged, sets NiMaterialProperty.alpha = 0
so they do not render (avoids collapsed-geometry arm distortion).

Output: Meshes/ag/ag_wrist.nif, ag_forearm.nif, ag_upperarm.nif

Run:
  blender --background --python tools/build_invisible_stubs.py
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MOD_ROOT = SCRIPT_DIR.parent
IO_SCENE_MW = MOD_ROOT / "tools" / "downloads" / "io_scene_mw"
MORROWIND = Path(r"C:/Morrowind/Data Files")
OUT_DIR = MOD_ROOT / "Meshes/ag"

STUBS = (
    ("Meshes/b/B_N_Dark Elf_M_Wrist.NIF", "ag_wrist.nif"),
    ("Meshes/b/B_N_Dark Elf_M_Forearm.NIF", "ag_forearm.nif"),
    ("Meshes/b/B_N_Dark Elf_M_Upper Arm.NIF", "ag_upperarm.nif"),
)

if str(IO_SCENE_MW) not in sys.path:
    sys.path.insert(0, str(IO_SCENE_MW))

from es3 import nif  # noqa: E402


def make_invisible_stub(vanilla_path: Path, out_path: Path) -> None:
    stream = nif.NiStream()
    stream.load(vanilla_path)

    for shape in stream.objects_of_type(nif.NiTriShape):
        material = None
        for prop in shape.properties:
            if isinstance(prop, nif.NiMaterialProperty):
                material = prop
                break
        if material is None:
            material = nif.NiMaterialProperty()
            shape.properties.append(material)
        material.alpha = 0.0

    stream.save(out_path)
    print(f"  {out_path.name} ({out_path.stat().st_size} bytes, alpha=0)")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Building invisible arm stubs (alpha=0, full geometry):")
    for rel_src, out_name in STUBS:
        src = MORROWIND / rel_src
        if not src.is_file():
            raise FileNotFoundError(f"Vanilla mesh not found: {src}")
        make_invisible_stub(src, OUT_DIR / out_name)


if __name__ == "__main__":
    main()
