#!/usr/bin/env python3
"""
Build Meshes/ag/ag_head.nif in vanilla *head* format (NiGeomMorpher, no Bip01 skeleton).

Requires:
  - Blender 4.x with io_scene_mw enabled (or on PYTHONPATH)
  - tools/blender/ancestor_ghost.blend with ag_head_geo + Dunmer head reference
  - Vanilla Dunmer head at MORROWIND/Data Files/Meshes/b/B_N_Dark Elf_M_Head_01.NIF

Run from repo root:
  blender --background tools/blender/ancestor_ghost.blend --python tools/blender/build_vanilla_head_nif.py
"""

from __future__ import annotations

import math
import shutil
import sys
from pathlib import Path

import bpy

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
MOD_ROOT = SCRIPT_DIR.parents[1]
IO_SCENE_MW = MOD_ROOT / "tools" / "downloads" / "io_scene_mw"
MORROWIND = Path(r"C:/Morrowind/Data Files")
VANILLA_HEAD = MORROWIND / "Meshes/b/B_N_Dark Elf_M_Head_01.NIF"
OUT_NIF = MOD_ROOT / "Meshes/ag/ag_head.nif"
BACKUP_NIF = MOD_ROOT / "Meshes/ag/ag_head.skinned_backup.nif"
TEXTURE_PATH = r"ag\TX_Ghostward_tunic.tga"

ROOT_NAME = "ag_head_m_01"
TRI_NAME = "Tri ag_head_m_01"

if str(IO_SCENE_MW) not in sys.path:
    sys.path.insert(0, str(IO_SCENE_MW))

from es3 import nif  # noqa: E402
from es3.nif import NiFloatData  # noqa: E402
from io_scene_mw import nif_export  # noqa: E402


def _mesh_objects(prefix: str) -> list[bpy.types.Object]:
    return sorted(
        (o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(prefix)),
        key=lambda o: o.name,
    )


def _apply_modifiers(obj: bpy.types.Object) -> None:
    bpy.context.view_layer.objects.active = obj
    for mod in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except RuntimeError:
            pass


def _join_meshes(objects: list[bpy.types.Object]) -> bpy.types.Object:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    return bpy.context.view_layer.objects.active


def _vertex_centroid(obj: bpy.types.Object):
    from mathutils import Vector

    verts = obj.data.vertices
    if not verts:
        return Vector((0.0, 0.0, 0.0))
    center = Vector((0.0, 0.0, 0.0))
    for vert in verts:
        center += vert.co
    return center / len(verts)


def _align_to_reference(mesh: bpy.types.Object, reference: bpy.types.Object) -> None:
    """Bake ghost head position/orientation into morpher NIF space."""
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh

    # Drop leftover object rotation from the skinned export.
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    mesh.location = reference.matrix_world.translation
    mesh.rotation_euler = (0.0, 0.0, 0.0)
    mesh.scale = (1.0, 1.0, 1.0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Ghost hood was authored 90° off Dunmer head forward in Blender Z.
    mesh.rotation_euler[2] += math.radians(-90.0)
    bpy.ops.object.transform_apply(rotation=True)

    offset = _vertex_centroid(reference) - _vertex_centroid(mesh)
    for vert in mesh.data.vertices:
        vert.co += offset

    mesh.location = (0.0, 0.0, 0.0)
    mesh.rotation_euler = (0.0, 0.0, 0.0)
    mesh.scale = (1.0, 1.0, 1.0)


def _yaw_delta_deg(vertices, reference_vertices) -> float:
    import numpy as np

    center = vertices.mean(axis=0)
    ref_center = reference_vertices.mean(axis=0)
    rel = vertices - center
    ref_rel = reference_vertices - ref_center

    def forward(points):
        xz = points[:, [0, 2]]
        index = int(np.argmax(np.linalg.norm(xz, axis=1)))
        direction = xz[index]
        norm = np.linalg.norm(direction)
        return direction / norm if norm > 1e-6 else np.array([0.0, 1.0])

    ghost = forward(rel)
    vanilla = forward(ref_rel)
    return math.degrees(
        math.atan2(
            ghost[0] * vanilla[1] - ghost[1] * vanilla[0],
            ghost[0] * vanilla[0] + ghost[1] * vanilla[1],
        )
    )


def _ensure_material(mesh: bpy.types.Object) -> None:
    mat = bpy.data.materials.new("ag_head")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(
        str(MOD_ROOT / "Textures/ag/TX_Ghostward_tunic.tga"),
        check_existing=True,
    )
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    mesh.data.materials.clear()
    mesh.data.materials.append(mat)
    mesh.active_material = mat
    for poly in mesh.data.polygons:
        poly.material_index = 0


def prepare_head_mesh() -> tuple[bpy.types.Object, bpy.types.Object]:
    parts = _mesh_objects("ag_head_geo")
    if not parts:
        raise RuntimeError("No mesh named ag_head_geo* found in the blend file.")

    mesh = parts[0] if len(parts) == 1 else _join_meshes(parts)
    mesh.name = TRI_NAME

    reference = bpy.data.objects.get("Tri B_N_Dark Elf_M_Head_01")
    if reference is None:
        raise RuntimeError(
            "Missing reference object 'Tri B_N_Dark Elf_M_Head_01'. "
            "Import the Dunmer head NIF into the blend file first."
        )

    if mesh.parent:
        mesh.parent = None
    _apply_modifiers(mesh)
    _align_to_reference(mesh, reference)
    _ensure_material(mesh)

    # Vanilla heads: root NiNode + child NiTriShape at identity transforms.
    root = bpy.data.objects.new(ROOT_NAME, None)
    bpy.context.collection.objects.link(root)
    from mathutils import Matrix

    mesh.parent = root
    mesh.matrix_local = Matrix.Identity(4)

    for obj in bpy.data.objects:
        obj.hide_set(obj not in {root, mesh})
        obj.hide_render = obj.hide_get()
        obj.select_set(False)

    root.select_set(True)
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = root
    return root, mesh


def export_static_nif(filepath: Path) -> None:
    result = nif_export.save(
        bpy.context,
        filepath=str(filepath),
        use_selection=True,
        use_active_collection=False,
        export_animations=False,
        preserve_root_tranforms=False,
        preserve_material_names=True,
        strip_numeric_suffixes=True,
        create_switch_nodes=False,
        randomize_animations=False,
        extract_keyframe_data=False,
        vertex_precision=0.001,
    )
    if result != {"FINISHED"}:
        raise RuntimeError(f"NIF export failed: {result}")


def _clone_extra_data(src):
    """Shallow-clone NiExtraData blocks (safe for text keys)."""
    cls = type(src)
    dst = cls()
    for slot in getattr(cls, "__slots__", ()):
        setattr(dst, slot, getattr(src, slot))
    if hasattr(src, "keys") and hasattr(dst, "keys"):
        import numpy as np

        dst.keys = src.keys.copy() if len(src.keys) else np.zeros(0, dtype=src.keys.dtype)
    return dst


def _clone_property(src):
    cls = type(src)
    dst = cls()
    for slot in getattr(cls, "__slots__", ()):
        val = getattr(src, slot)
        if slot == "source" and val is not None:
            tex = nif.NiSourceTexture()
            tex.file_name = TEXTURE_PATH
            tex.pixel_data = None
            setattr(dst, slot, tex)
        else:
            setattr(dst, slot, val)
    return dst


def finalize_vanilla_head(static_path: Path, vanilla_path: Path, out_path: Path) -> None:
    import numpy as np

    vanilla = nif.NiStream()
    vanilla.load(vanilla_path)

    stream = nif.NiStream()
    stream.load(static_path)

    root = stream.root
    if root is None:
        raise RuntimeError("Exported NIF has no root node.")
    root.name = ROOT_NAME

    tri = stream.find_object_by_name(TRI_NAME, nif.NiTriShape)
    if tri is None:
        tri = next(stream.objects_of_type(nif.NiTriShape), None)
    if tri is None:
        raise RuntimeError("Exported NIF has no NiTriShape.")

    tris = list(stream.objects_of_type(nif.NiTriShape))
    for i, shape in enumerate(tris):
        shape.name = TRI_NAME if i == 0 else f"{TRI_NAME} {i}"
        shape.skin = None
        shape.properties = [
            p for p in shape.properties
            if p is not None and not isinstance(p, nif.NiAlphaProperty)
        ]
    tri = tris[0]

    vanilla_root = vanilla.root
    vanilla_tri = vanilla.find_object_by_name("Tri B_N_Dark Elf_M_Head_01", nif.NiTriShape)
    if vanilla_tri is None:
        vanilla_tri = next(vanilla.objects_of_type(nif.NiTriShape))

    # Snap position to vanilla Dunmer head morpher space.
    vanilla_verts = np.array(vanilla_tri.data.vertices, copy=True)
    vertices = np.array(tri.data.vertices, copy=True)
    vertices += vanilla_verts.mean(axis=0) - vertices.mean(axis=0)
    print(f"  heading check: {_yaw_delta_deg(vertices, vanilla_verts):+.1f}° vs Dunmer head")

    # Basis-only morpher (static ghost head; char-gen sliders won't morph this mesh).
    morph = nif.NiMorphData(relative_targets=1)
    basis = nif.NiMorphDataMorphTarget()
    basis.key_type = NiFloatData.KeyType.LIN_KEY
    basis.keys = np.empty((0, basis.key_size), dtype=np.float32)
    basis.vertices = vertices.copy()
    morph.targets = [basis]
    tri.data.vertices = vertices

    controller = nif.NiGeomMorpherController()
    controller.active = True
    controller.flags = 0x0008 | (nif.NiTimeController.CycleType.CLAMP << 1)
    controller.frequency = 1.0
    controller.phase = 0.0
    controller.start_time = 0.0
    controller.stop_time = 1.0
    controller.target = tri
    controller.data = morph
    tri.controllers.clear()
    tri.controllers.appendleft(controller)

    # Copy text keys + vertex colors from vanilla Dunmer head.
    root.extra_datas.clear()
    for ed in vanilla_root.extra_datas:
        if isinstance(ed, nif.NiTextKeyExtraData):
            root.extra_datas.append(_clone_extra_data(ed))

    tri.properties = [p for p in tri.properties if p is not None and not isinstance(p, nif.NiVertexColorProperty)]
    for prop in vanilla_tri.properties:
        if isinstance(prop, nif.NiVertexColorProperty):
            tri.properties.append(_clone_property(prop))
        elif isinstance(prop, nif.NiTexturingProperty):
            tex = _clone_property(prop)
            if tex.base_texture and tex.base_texture.source:
                tex.base_texture.source.file_name = TEXTURE_PATH
            tri.properties.append(tex)

    # Ensure texture path even if exporter rewrote materials.
    for prop in tri.properties:
        if isinstance(prop, nif.NiTexturingProperty) and prop.base_texture and prop.base_texture.source:
            prop.base_texture.source.file_name = TEXTURE_PATH

    stream.sort()
    stream.merge_properties()

    # Re-apply MW-style path after merge_properties (it lowercases/sanitizes paths).
    for src in stream.objects_of_type(nif.NiSourceTexture):
        src.file_name = TEXTURE_PATH

    stream.save(out_path)


def validate(out_path: Path) -> None:
    data = out_path.read_bytes().decode("latin1", errors="ignore")
    checks = {
        "NiGeomMorpherController": "NiGeomMorpherController" in data,
        "NiMorphData": "NiMorphData" in data,
        "no Bip01 root": data.find("NiNode") < data.find("Bip01") or "Bip01 Pelvis" not in data,
        "Tri contains Head": "Tri ag_head_m_01" in data,
        "no NiSkinInstance": "NiSkinInstance" not in data,
        "no NiAlphaProperty": "NiAlphaProperty" not in data,
        "texture path": "ghostward_tunic" in data.lower(),
    }
    failed = [name for name, ok in checks.items() if not ok]
    print("Validation:")
    for name, ok in checks.items():
        print(f"  {'OK' if ok else 'FAIL'}: {name}")
    if failed:
        raise RuntimeError(f"ag_head.nif validation failed: {', '.join(failed)}")


def main() -> None:
    if not VANILLA_HEAD.is_file():
        raise FileNotFoundError(f"Vanilla head not found: {VANILLA_HEAD}")
    if OUT_NIF.is_file() and not BACKUP_NIF.is_file():
        shutil.copy2(OUT_NIF, BACKUP_NIF)
        print(f"Backed up previous head to {BACKUP_NIF}")

    prepare_head_mesh()

    temp_nif = MOD_ROOT / "Meshes/ag/_ag_head_static.nif"
    temp_nif.parent.mkdir(parents=True, exist_ok=True)
    export_static_nif(temp_nif)
    finalize_vanilla_head(temp_nif, VANILLA_HEAD, OUT_NIF)
    temp_nif.unlink(missing_ok=True)

    validate(OUT_NIF)
    print(f"Wrote vanilla-format head: {OUT_NIF} ({OUT_NIF.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
