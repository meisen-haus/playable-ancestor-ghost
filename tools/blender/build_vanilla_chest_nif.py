#!/usr/bin/env python3
"""
Build Meshes/ag/ag_chest.nif in vanilla *body* format (Bip01 + NiSkinInstance).

Chest + hand slots share this file (like Dunmer Skins.nif):
  - Tri Chest          <- ghost robe (Tri robe front + back)
  - Tri Right Hand 0   <- Tri hand
  - Tri Left Hand 0    <- Tri hand01

Run from repo root:
  blender --background tools/blender/ancestor_ghost.blend --python tools/blender/build_vanilla_chest_nif.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector, kdtree

SCRIPT_DIR = Path(__file__).resolve().parent
MOD_ROOT = SCRIPT_DIR.parents[1]
IO_SCENE_MW = MOD_ROOT / "tools" / "downloads" / "io_scene_mw"
MORROWIND = Path(r"C:/Morrowind/Data Files")
VANILLA_SKINS = MORROWIND / "Meshes/b/B_N_Dark Elf_M_Skins.NIF"
OUT_NIF = MOD_ROOT / "Meshes/ag/ag_chest.nif"
BACKUP_NIF = MOD_ROOT / "Meshes/ag/ag_chest.dunmer_backup.nif"
TEXTURE_PATH = r"ag\TX_Ghostward_tunic.tga"

ARMATURE = "Bip01"
ROBE_PARTS = ("Tri robe front", "Tri robe back")
HAND_RIGHT_SRC = "Tri hand"
HAND_LEFT_SRC = "Tri hand01"
REF_CHEST = "Tri Chest"
REF_HAND_R = "Tri Right Hand 0"
REF_HAND_L = "Tri Left Hand 0"

EXPORT_CHEST = "ag_chest_geo"
EXPORT_HAND_R = "ag_hand_r_geo"
EXPORT_HAND_L = "ag_hand_l_geo"

TRI_CHEST = "Tri Chest"
TRI_HAND_R = "Tri Right Hand 0"
TRI_HAND_L = "Tri Left Hand 0"

CHEST_Z_NUDGE = 4.0

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

if str(IO_SCENE_MW) not in sys.path:
    sys.path.insert(0, str(IO_SCENE_MW))

from es3 import nif  # noqa: E402
from io_scene_mw import nif_export  # noqa: E402


def _ensure_object_mode() -> None:
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def _world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    mw = obj.matrix_world
    points = [mw @ Vector(corner) for corner in obj.bound_box]
    mins = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maxs = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return mins, maxs


def _world_centroid(obj: bpy.types.Object) -> Vector:
    mw = obj.matrix_world
    center = Vector((0.0, 0.0, 0.0))
    for vert in obj.data.vertices:
        center += mw @ vert.co
    return center / len(obj.data.vertices)


def _link_for_export(obj: bpy.types.Object, armature: bpy.types.Object) -> None:
    collections = armature.users_collection
    if not collections:
        return
    for coll in list(obj.users_collection):
        coll.objects.unlink(obj)
    collections[0].objects.link(obj)


def _duplicate_unparented(name: str) -> bpy.types.Object:
    source = bpy.data.objects.get(name)
    if source is None:
        raise RuntimeError(f"Missing mesh object '{name}' in blend file.")
    world = source.matrix_world.copy()
    _ensure_object_mode()
    bpy.ops.object.select_all(action="DESELECT")
    source.select_set(True)
    bpy.context.view_layer.objects.active = source
    bpy.ops.object.duplicate()
    duplicate = bpy.context.active_object
    duplicate.parent = None
    duplicate.matrix_world = world
    return duplicate


def _apply_modifiers(obj: bpy.types.Object) -> None:
    _ensure_object_mode()
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for mod in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except RuntimeError:
            pass


def _apply_non_armature_modifiers(obj: bpy.types.Object) -> None:
    """Apply modifiers except Armature — applying creature armature destroys weight groups."""
    _ensure_object_mode()
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for mod in list(obj.modifiers):
        if mod.type == "ARMATURE":
            continue
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except RuntimeError:
            pass
    for mod in list(obj.modifiers):
        if mod.type == "ARMATURE":
            obj.modifiers.remove(mod)


def _bmesh_join(objects: list[bpy.types.Object], name: str) -> bpy.types.Object:
    bm = bmesh.new()
    for obj in objects:
        start = len(bm.verts)
        bm.from_mesh(obj.data)
        bmesh.ops.transform(bm, matrix=obj.matrix_world, verts=bm.verts[start:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    result = bpy.data.objects.new(name, mesh)
    armature = bpy.data.objects.get(ARMATURE)
    if armature is not None:
        _link_for_export(result, armature)
    else:
        bpy.context.collection.objects.link(result)
    return result


def _align_world_to_reference(mesh: bpy.types.Object, reference: bpy.types.Object) -> None:
    """Match shoulder height (max Z) and XY center in world space. No yaw rotation."""
    _ensure_object_mode()
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    _, mesh_max = _world_bounds(mesh)
    _, ref_max = _world_bounds(reference)
    mesh_center = _world_centroid(mesh)
    ref_center = _world_centroid(reference)

    offset = Vector((
        ref_center.x - mesh_center.x,
        ref_center.y - mesh_center.y,
        ref_max.z - mesh_max.z,
    ))
    for vert in mesh.data.vertices:
        vert.co += offset

    mesh.location = (0.0, 0.0, 0.0)
    mesh.rotation_euler = (0.0, 0.0, 0.0)
    mesh.scale = (1.0, 1.0, 1.0)


def _copy_weights_nearest(
    target: bpy.types.Object,
    source: bpy.types.Object,
    armature: bpy.types.Object,
) -> None:
    valid_bones = {bone.name for bone in armature.data.bones}
    target.vertex_groups.clear()

    tree = kdtree.KDTree(len(source.data.vertices))
    source_world = source.matrix_world
    for index, vert in enumerate(source.data.vertices):
        tree.insert(source_world @ vert.co, index)
    tree.balance()

    target_world = target.matrix_world
    group_cache: dict[str, bpy.types.VertexGroup] = {}
    for vert_index, vert in enumerate(target.data.vertices):
        _, source_index, _ = tree.find(target_world @ vert.co)
        for group in source.data.vertices[source_index].groups:
            name = source.vertex_groups[group.group].name
            if name not in valid_bones:
                continue
            if name not in group_cache:
                group_cache[name] = target.vertex_groups.new(name=name)
            group_cache[name].add([vert_index], group.weight, "REPLACE")

    if not target.modifiers.get("Armature"):
        mod = target.modifiers.new("Armature", "ARMATURE")
        mod.object = armature
    target.parent = armature


def _ensure_material(mesh: bpy.types.Object) -> None:
    mat = bpy.data.materials.get("ag_body")
    if mat is None:
        mat = bpy.data.materials.new("ag_body")
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


def _remap_hand_weights(mesh: bpy.types.Object, armature: bpy.types.Object, side: str) -> None:
    """Collapse creature 11-bone hand weights onto Dunmer's 4 finger bones."""
    from collections import defaultdict

    valid_bones = {bone.name for bone in armature.data.bones}
    fallback = f"Bip01 Finger21.{side}"
    per_vertex: list[defaultdict[str, float]] = [
        defaultdict(float) for _ in range(len(mesh.data.vertices))
    ]

    for vg in mesh.vertex_groups:
        target = HAND_BONE_REMAP.get(vg.name, vg.name)
        if target not in valid_bones:
            continue
        for vert in mesh.data.vertices:
            for group in vert.groups:
                if group.group == vg.index:
                    per_vertex[vert.index][target] += group.weight

    mesh.vertex_groups.clear()
    group_cache: dict[str, bpy.types.VertexGroup] = {}

    for vert_index, weights in enumerate(per_vertex):
        total = sum(weights.values())
        if total <= 0.0:
            weights[fallback] = 1.0
            total = 1.0
        for name, weight in weights.items():
            if name not in group_cache:
                group_cache[name] = mesh.vertex_groups.new(name=name)
            group_cache[name].add([vert_index], weight / total, "REPLACE")

    if not mesh.modifiers.get("Armature"):
        mod = mesh.modifiers.new("Armature", "ARMATURE")
        mod.object = armature
    mesh.parent = armature


def _prepare_hand_mesh(
    source_name: str,
    reference_name: str,
    export_name: str,
    armature: bpy.types.Object,
) -> bpy.types.Object:
    """Ghost hand aligned to Dunmer bind space with remapped creature weights on Bip01."""
    reference = bpy.data.objects.get(reference_name)
    if reference is None:
        raise RuntimeError(f"Missing Dunmer reference mesh '{reference_name}'.")

    mesh = _duplicate_unparented(source_name)
    _apply_non_armature_modifiers(mesh)
    _align_world_to_reference(mesh, reference)
    side = "R" if reference_name == REF_HAND_R else "L"
    _remap_hand_weights(mesh, armature, side)

    ref_inv = reference.matrix_world.inverted()
    for vert in mesh.data.vertices:
        vert.co = ref_inv @ vert.co
    mesh.matrix_world = reference.matrix_world.copy()
    mesh.parent = armature

    mesh.name = export_name
    _ensure_material(mesh)
    _link_for_export(mesh, armature)
    return mesh


def prepare_body_meshes() -> tuple[bpy.types.Object, list[bpy.types.Object]]:
    armature = bpy.data.objects.get(ARMATURE)
    if armature is None:
        raise RuntimeError(f"Missing armature '{ARMATURE}' in blend file.")

    chest_ref = bpy.data.objects.get(REF_CHEST)
    if chest_ref is None:
        raise RuntimeError(f"Missing Dunmer reference '{REF_CHEST}'.")

    robe_parts = []
    for name in ROBE_PARTS:
        if bpy.data.objects.get(name) is None:
            raise RuntimeError(f"Missing creature robe mesh '{name}'.")
        part = _duplicate_unparented(name)
        _apply_modifiers(part)
        robe_parts.append(part)

    chest = _bmesh_join(robe_parts, EXPORT_CHEST)
    _align_world_to_reference(chest, chest_ref)
    _copy_weights_nearest(chest, chest_ref, armature)
    _ensure_material(chest)
    _link_for_export(chest, armature)

    hand_r = _prepare_hand_mesh(HAND_RIGHT_SRC, REF_HAND_R, EXPORT_HAND_R, armature)
    hand_l = _prepare_hand_mesh(HAND_LEFT_SRC, REF_HAND_L, EXPORT_HAND_L, armature)

    export_meshes = [chest, hand_r, hand_l]
    keep = {ARMATURE, EXPORT_CHEST, EXPORT_HAND_R, EXPORT_HAND_L}

    for obj in bpy.data.objects:
        hide = obj.name not in keep
        obj.hide_set(hide)
        obj.hide_render = hide
        obj.select_set(False)

    _ensure_object_mode()
    for obj in export_meshes:
        obj.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature

    print("Prepared export meshes:")
    for obj in export_meshes:
        _, maxs = _world_bounds(obj)
        print(
            f"  {obj.name}: {len(obj.data.vertices)} verts, "
            f"{len(obj.vertex_groups)} bone groups, world max Z {maxs.z:.3f}"
        )

    return armature, export_meshes


def export_skinned_nif(filepath: Path) -> None:
    result = nif_export.save(
        bpy.context,
        filepath=str(filepath),
        use_selection=True,
        use_active_collection=False,
        export_animations=True,
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


def _set_texture_on_shape(shape: nif.NiTriShape) -> None:
    shape.properties = [
        prop
        for prop in shape.properties
        if prop is not None and not isinstance(prop, (nif.NiAlphaProperty, nif.NiVertexColorProperty))
    ]
    for prop in shape.properties:
        if isinstance(prop, nif.NiTexturingProperty) and prop.base_texture and prop.base_texture.source:
            prop.base_texture.source.file_name = TEXTURE_PATH


def _nudge_chest_up(shape: nif.NiTriShape, amount: float) -> None:
    verts = np.array(shape.data.vertices, copy=True)
    verts[:, 2] += amount
    shape.data.vertices = verts
    print(f"  nudge {shape.name}: +Z {amount:.2f}")


def _find_node(stream: nif.NiStream, name: str):
    node = stream.find_object_by_name(name, nif.NiNode)
    if node is not None:
        return node
    for obj in stream.objects_of_type(nif.NiNode):
        if obj.name == name:
            return obj
    return None


def _nudge_hand_to_vanilla(shape: nif.NiTriShape, vanilla_tri: nif.NiTriShape) -> None:
    """Shift hand verts to vanilla centroid; keep exported skin bind (skeleton-connected)."""
    verts = np.array(shape.data.vertices, copy=True)
    ref = np.array(vanilla_tri.data.vertices, copy=True)
    delta = ref.mean(axis=0) - verts.mean(axis=0)
    shape.data.vertices = verts + delta
    print(
        f"  nudge {shape.name}: delta {tuple(round(float(x), 2) for x in delta)}, "
        f"span {tuple(round(float(x), 2) for x in (verts.max(0) - verts.min(0)))}"
    )


def _fix_hand_skin_root(shape: nif.NiTriShape, vanilla_tri: nif.NiTriShape, stream: nif.NiStream) -> None:
    """Match hand NiSkinInstance root to vanilla without replacing bind data."""
    if shape.skin is None or vanilla_tri.skin is None or vanilla_tri.skin.root is None:
        return
    root = _find_node(stream, vanilla_tri.skin.root.name)
    if root is None:
        raise RuntimeError(f"Missing hand skin root '{vanilla_tri.skin.root.name}' in export.")
    if shape.skin.root != root:
        shape.skin.root = root
        print(f"  hand skin root {shape.name}: {root.name}")


def finalize_vanilla_chest(exported_path: Path, vanilla_path: Path, out_path: Path) -> None:
    vanilla = nif.NiStream()
    vanilla.load(vanilla_path)

    stream = nif.NiStream()
    stream.load(exported_path)

    if stream.root is None:
        raise RuntimeError("Exported NIF has no root node.")
    stream.root.name = "Bip01"

    rename_map = {
        EXPORT_CHEST: TRI_CHEST,
        EXPORT_HAND_R: TRI_HAND_R,
        EXPORT_HAND_L: TRI_HAND_L,
    }
    vanilla_tris = {tri.name: tri for tri in vanilla.objects_of_type(nif.NiTriShape)}

    tris = list(stream.objects_of_type(nif.NiTriShape))
    if len(tris) < 3:
        raise RuntimeError(
            f"Expected 3 NiTriShape blocks (chest + 2 hands), found {len(tris)}: "
            f"{[shape.name for shape in tris]}"
        )

    print("Post-process:")
    for shape in tris:
        new_name = rename_map.get(shape.name, shape.name)
        shape.name = new_name
        shape.properties = [
            prop
            for prop in shape.properties
            if prop is not None and not isinstance(prop, nif.NiAlphaProperty)
        ]
        _set_texture_on_shape(shape)

        vanilla_tri = vanilla_tris.get(new_name)
        if vanilla_tri is None:
            continue

        if new_name == TRI_CHEST:
            _nudge_chest_up(shape, CHEST_Z_NUDGE)
        elif new_name in (TRI_HAND_R, TRI_HAND_L):
            _nudge_hand_to_vanilla(shape, vanilla_tri)
            _fix_hand_skin_root(shape, vanilla_tri, stream)

        for prop in vanilla_tri.properties:
            if isinstance(prop, nif.NiVertexColorProperty):
                shape.properties.append(_clone_property(prop))

    stream.sort()
    stream.merge_properties()

    for src in stream.objects_of_type(nif.NiSourceTexture):
        src.file_name = TEXTURE_PATH

    stream.save(out_path)


def validate(out_path: Path) -> None:
    stream = nif.NiStream()
    stream.load(out_path)

    tri_names = [shape.name for shape in stream.objects_of_type(nif.NiTriShape)]
    data = out_path.read_bytes().decode("latin1", errors="ignore")
    checks = {
        "root Bip01": stream.root is not None and stream.root.name == "Bip01",
        "Tri Chest": TRI_CHEST in tri_names,
        "Tri Right Hand 0": TRI_HAND_R in tri_names,
        "Tri Left Hand 0": TRI_HAND_L in tri_names,
        "NiSkinInstance": any(True for _ in stream.objects_of_type(nif.NiSkinInstance)),
        "no NiAlphaProperty": "NiAlphaProperty" not in data,
        "no morpher": "NiGeomMorpherController" not in data,
        "texture path": "ghostward_tunic" in data.lower(),
    }
    failed = [name for name, ok in checks.items() if not ok]
    print("Validation:")
    for name, ok in checks.items():
        print(f"  {'OK' if ok else 'FAIL'}: {name}")
    print(f"  tris: {tri_names}")
    if failed:
        raise RuntimeError(f"ag_chest.nif validation failed: {', '.join(failed)}")


def main() -> None:
    if not VANILLA_SKINS.is_file():
        raise FileNotFoundError(f"Vanilla Dunmer skins not found: {VANILLA_SKINS}")
    if OUT_NIF.is_file() and not BACKUP_NIF.is_file():
        shutil.copy2(OUT_NIF, BACKUP_NIF)
        print(f"Backed up previous chest to {BACKUP_NIF}")

    prepare_body_meshes()

    temp_nif = MOD_ROOT / "Meshes/ag/_ag_chest_skinned.nif"
    temp_nif.parent.mkdir(parents=True, exist_ok=True)
    export_skinned_nif(temp_nif)
    finalize_vanilla_chest(temp_nif, VANILLA_SKINS, OUT_NIF)
    temp_nif.unlink(missing_ok=True)

    validate(OUT_NIF)
    print(f"Wrote vanilla-format chest: {OUT_NIF} ({OUT_NIF.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
