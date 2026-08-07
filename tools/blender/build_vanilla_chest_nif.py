#!/usr/bin/env python3
"""
Build body NIFs from vanilla Ancestral Ghost geometry in ancestor_ghost.blend:

  Meshes/ag/ag_chest.nif     — robe (weighted to Dunmer biped)
  Meshes/ag/ag_hand.nif      — ghost hands + vanilla Tx_LicheKing
  Meshes/ag/ag_arms_1st.nif  — robe mesh for OpenMW *.1st first-person sleeves

Geometry comes from the vanilla AncestorGhost meshes already in the blend
(Tri robe front/back, Tri hand/hand01). Skin weights are transferred from
Dunmer body-part references on Bip01. Pack slot layout (separate hand / .1st
chest) is followed as a structural reference only — no pack NIFs are shipped.

Run from repo root:
  blender --background --addons io_scene_mw tools/blender/ancestor_ghost.blend --python tools/blender/build_vanilla_chest_nif.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import bmesh
import bpy
import addon_utils
import numpy as np
from mathutils import Vector, kdtree

SCRIPT_DIR = Path(__file__).resolve().parent
MOD_ROOT = SCRIPT_DIR.parents[1]
IO_SCENE_MW = MOD_ROOT / "tools" / "downloads" / "io_scene_mw"
IO_SCENE_MW_LIB = IO_SCENE_MW / "io_scene_mw" / "lib"
MORROWIND = Path(r"C:/Morrowind/Data Files")
VANILLA_SKINS = MORROWIND / "Meshes/b/B_N_Dark Elf_M_Skins.NIF"
OUT_CHEST = MOD_ROOT / "Meshes/ag/ag_chest.nif"
OUT_HAND = MOD_ROOT / "Meshes/ag/ag_hand.nif"
OUT_ARMS_1ST = MOD_ROOT / "Meshes/ag/ag_arms_1st.nif"
TEXTURE_ROBE = r"ag\TX_Ghostward_tunic.tga"
TEXTURE_HAND = r"textures\Tx_LicheKing.dds"

# Creature-pack bind-pose + arm/finger skinning references (structural only).
# Prefer local tools/reference copies so builds don't require the pack tree.
PACK_HAND_SRC = Path(r"C:/meisen-haus/creature-pack/Data Files/meshes/b/Ghost/Ghost_Hand.nif")
PACK_CHEST_SRC = Path(r"C:/meisen-haus/creature-pack/Data Files/meshes/b/Ghost/Ghost_chest.nif")
PACK_ARMS_SRC = Path(r"C:/meisen-haus/creature-pack/Data Files/meshes/b/Ghost/Ghost_arms.nif")
HAND_SKIN_REF = MOD_ROOT / "tools" / "reference" / "ag_hand_skin_ref.nif"
CHEST_SKIN_REF = MOD_ROOT / "tools" / "reference" / "ag_chest_skin_ref.nif"
ARMS_SKIN_REF = MOD_ROOT / "tools" / "reference" / "ag_arms_1st_skin_ref.nif"

ARMATURE = "Bip01"
ROBE_PARTS = ("Tri robe front", "Tri robe back")
HAND_RIGHT_SRC = "Tri hand"
HAND_LEFT_SRC = "Tri hand01"
REF_CHEST = "Tri Chest"
REF_HAND_R = ("Tri Right Hand 0", "Tri Right Hand 1", "Tri Right Hand 2")
REF_HAND_L = ("Tri Left Hand 0", "Tri Left Hand 1", "Tri Left Hand 2")

EXPORT_CHEST = "ag_chest_geo"
EXPORT_HAND_R = "ag_hand_r_geo"
EXPORT_HAND_L = "ag_hand_l_geo"

TRI_CHEST = "Tri Chest"
TRI_HAND_R = "Tri Right Hand 0"
TRI_HAND_L = "Tri Left Hand 0"

CHEST_Z_NUDGE = 4.0

if addon_utils.enable("io_scene_mw") is None:
    for path in (IO_SCENE_MW_LIB, IO_SCENE_MW):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
elif "io_scene_mw" not in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_enable(module="io_scene_mw")

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


def _bake_armature_deformation(mesh: bpy.types.Object) -> None:
    """Bake armature-modifier pose into mesh rest coords (world = local at origin)."""
    if not any(mod.type == "ARMATURE" for mod in mesh.modifiers):
        return
    _ensure_object_mode()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = mesh.evaluated_get(depsgraph)
    eval_mw = eval_obj.matrix_world
    world_coords = [eval_mw @ v.co.copy() for v in eval_obj.data.vertices]

    for mod in list(mesh.modifiers):
        if mod.type == "ARMATURE":
            mesh.modifiers.remove(mod)
    mesh.parent = None
    mesh.location = (0.0, 0.0, 0.0)
    mesh.rotation_euler = (0.0, 0.0, 0.0)
    mesh.scale = (1.0, 1.0, 1.0)
    for vert, world in zip(mesh.data.vertices, world_coords):
        vert.co = world


def _apply_non_armature_modifiers(obj: bpy.types.Object) -> None:
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


def _join_keep_weights(objects: list[bpy.types.Object], name: str) -> bpy.types.Object:
    """Join meshes with bpy.ops.object.join so vertex groups (sleeve weights) survive."""
    _ensure_object_mode()
    # Bake world transforms into mesh data before join.
    for obj in objects:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    joined = bpy.context.active_object
    joined.name = name
    joined.data.name = name
    return joined


# Creature-robe helper / tail bones → Dunmer biped bones (sleeve chain preserved).
ROBE_WEIGHT_REMAP = {
    "Bip01 Tail": "Bip01 Spine",
    "Bip01 Tail1": "Bip01 Spine",
    "Bip01 Tail2": "Bip01 Pelvis",
    "Bip01 Tail3": "Bip01 Pelvis",
    "Bone01": "Bip01 Forearm.R",
    "Bone02": "Bip01 Forearm.R",
    "Bone04": "Bip01 Forearm.L",
    "Bone06": "Bip01 Forearm.L",
    "Bip01 Finger4.R": "Bip01 Hand.R",
    "Bip01 Finger4.L": "Bip01 Hand.L",
}


def _remap_and_filter_weights(mesh: bpy.types.Object, armature: bpy.types.Object) -> None:
    """Keep sleeve/torso biped weights; fold creature-only bones into the arm/spine chain."""
    valid = {bone.name for bone in armature.data.bones}

    # Merge remapped groups into targets.
    for src_name, dst_name in ROBE_WEIGHT_REMAP.items():
        src = mesh.vertex_groups.get(src_name)
        if src is None:
            continue
        if dst_name not in valid:
            mesh.vertex_groups.remove(src)
            continue
        dst = mesh.vertex_groups.get(dst_name) or mesh.vertex_groups.new(name=dst_name)
        for vert in mesh.data.vertices:
            try:
                w = src.weight(vert.index)
            except RuntimeError:
                continue
            if w <= 0.0:
                continue
            dst.add([vert.index], w, "ADD")
        mesh.vertex_groups.remove(src)

    # Drop anything not on the Dunmer armature.
    for group in list(mesh.vertex_groups):
        if group.name not in valid:
            mesh.vertex_groups.remove(group)

    # Normalize so shoulder→wrist influences sum to 1.
    if mesh.vertex_groups:
        bpy.context.view_layer.objects.active = mesh
        bpy.ops.object.vertex_group_normalize_all(lock_active=False)

    if not mesh.modifiers.get("Armature"):
        mod = mesh.modifiers.new("Armature", "ARMATURE")
        mod.object = armature
    mesh.parent = armature


def _align_world_to_reference(mesh: bpy.types.Object, reference: bpy.types.Object) -> Vector:
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
    return offset


def _copy_weights_nearest(
    target: bpy.types.Object,
    sources: bpy.types.Object | list[bpy.types.Object],
    armature: bpy.types.Object,
) -> None:
    """Transfer weights from one or more reference meshes (nearest world-space vert)."""
    if isinstance(sources, bpy.types.Object):
        sources = [sources]
    valid_bones = {bone.name for bone in armature.data.bones}
    target.vertex_groups.clear()

    # Flatten reference verts across all source meshes (e.g. Dunmer Hand 0/1/2).
    ref_points: list[Vector] = []
    ref_weights: list[list[tuple[str, float]]] = []
    for source in sources:
        source_world = source.matrix_world
        for vert in source.data.vertices:
            ref_points.append(source_world @ vert.co)
            weights = []
            for group in vert.groups:
                name = source.vertex_groups[group.group].name
                if name in valid_bones:
                    weights.append((name, group.weight))
            ref_weights.append(weights)

    if not ref_points:
        raise RuntimeError("Weight sources have no vertices")

    tree = kdtree.KDTree(len(ref_points))
    for index, co in enumerate(ref_points):
        tree.insert(co, index)
    tree.balance()

    target_world = target.matrix_world
    group_cache: dict[str, bpy.types.VertexGroup] = {}
    for vert_index, vert in enumerate(target.data.vertices):
        _, source_index, _ = tree.find(target_world @ vert.co)
        for name, weight in ref_weights[source_index]:
            if name not in group_cache:
                group_cache[name] = target.vertex_groups.new(name=name)
            group_cache[name].add([vert_index], weight, "REPLACE")

    if not target.modifiers.get("Armature"):
        mod = target.modifiers.new("Armature", "ARMATURE")
        mod.object = armature
    target.parent = armature


def _ensure_material(mesh: bpy.types.Object, image_path: Path) -> None:
    mat_name = f"ag_{image_path.stem}"
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        output = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(str(image_path), check_existing=True)
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    mesh.data.materials.clear()
    mesh.data.materials.append(mat)
    mesh.active_material = mat
    for poly in mesh.data.polygons:
        poly.material_index = 0


def _prepare_hand_mesh(
    source_name: str,
    export_name: str,
    weight_ref_names: tuple[str, ...],
    armature: bpy.types.Object,
    *,
    side: str,
) -> bpy.types.Object:
    """
    Vanilla ghost hand geometry, placed and skinned like a biped hand BODY part
    (same approach as creature-pack Ghost_Hand: Hand/Finger/Forearm weights at
    bind-pose hand location — not sleeve-exit + rigid root).
    """
    weight_refs = []
    for name in weight_ref_names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise RuntimeError(f"Missing Dunmer hand reference '{name}'.")
        weight_refs.append(obj)

    mesh = _duplicate_unparented(source_name)
    _bake_armature_deformation(mesh)
    _apply_non_armature_modifiers(mesh)
    # Align to the primary palm mesh (Hand 0).
    offset = _align_world_to_reference(mesh, weight_refs[0])
    print(
        f"Hand {side}: align to {weight_ref_names[0]} "
        f"offset=({offset.x:.3f}, {offset.y:.3f}, {offset.z:.3f})"
    )
    _copy_weights_nearest(mesh, weight_refs, armature)
    print(
        f"Hand {side}: weights from {', '.join(weight_ref_names)} "
        f"({len(mesh.vertex_groups)} groups)"
    )

    mesh.name = export_name
    _ensure_material(mesh, MORROWIND / "Textures/Tx_LicheKing.dds")
    _link_for_export(mesh, armature)
    return mesh


def prepare_body_meshes() -> tuple[bpy.types.Object, list[bpy.types.Object]]:
    armature = bpy.data.objects.get(ARMATURE)
    if armature is None:
        raise RuntimeError(f"Missing armature '{ARMATURE}' in blend file.")

    chest_ref = bpy.data.objects.get(REF_CHEST)
    if chest_ref is None:
        raise RuntimeError(f"Missing Dunmer reference '{REF_CHEST}'.")

    # Preserve vanilla ghost robe sleeve weights (Clavicle/UpperArm/Forearm/Hand).
    # Previous Dunmer-chest nearest transfer made sleeves billboard with the torso.
    robe_parts = []
    for name in ROBE_PARTS:
        if bpy.data.objects.get(name) is None:
            raise RuntimeError(f"Missing creature robe mesh '{name}'.")
        part = _duplicate_unparented(name)
        _bake_armature_deformation(part)
        _apply_non_armature_modifiers(part)
        robe_parts.append(part)

    chest = _join_keep_weights(robe_parts, EXPORT_CHEST)
    chest_offset = _align_world_to_reference(chest, chest_ref)
    print(f"Chest align offset: ({chest_offset.x:.3f}, {chest_offset.y:.3f}, {chest_offset.z:.3f})")
    _remap_and_filter_weights(chest, armature)
    sleeve_bones = [
        g.name for g in chest.vertex_groups
        if any(x in g.name for x in ("Forearm", "UpperArm", "Hand", "Clavicle"))
    ]
    print(
        f"Chest weights: preserved robe sleeve chain "
        f"({len(chest.vertex_groups)} groups; sleeve={sleeve_bones})"
    )
    _ensure_material(chest, MOD_ROOT / "Textures/ag/TX_Ghostward_tunic.tga")
    _link_for_export(chest, armature)

    hand_r = _prepare_hand_mesh(HAND_RIGHT_SRC, EXPORT_HAND_R, REF_HAND_R, armature, side="R")
    hand_l = _prepare_hand_mesh(HAND_LEFT_SRC, EXPORT_HAND_L, REF_HAND_L, armature, side="L")

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
            tex.file_name = TEXTURE_ROBE
            tex.pixel_data = None
            setattr(dst, slot, tex)
        else:
            setattr(dst, slot, val)
    return dst


def _set_texture_on_shape(shape: nif.NiTriShape, texture_path: str) -> None:
    shape.properties = [
        prop
        for prop in shape.properties
        if prop is not None and not isinstance(prop, (nif.NiAlphaProperty, nif.NiVertexColorProperty))
    ]
    for prop in shape.properties:
        if isinstance(prop, nif.NiTexturingProperty) and prop.base_texture and prop.base_texture.source:
            prop.base_texture.source.file_name = texture_path


def _nudge_shape_up(shape: nif.NiTriShape, amount: float) -> None:
    verts = np.array(shape.data.vertices, copy=True)
    verts[:, 2] += amount
    shape.data.vertices = verts
    print(f"  nudge {shape.name}: +Z {amount:.2f}")


def _apply_rigid_root_skin(shape: nif.NiTriShape, stream: nif.NiStream) -> None:
    """100% Bip01 root — keeps sleeve-exit hand geometry from flying to T-pose fingers."""
    if shape.skin is None or shape.skin.data is None:
        raise RuntimeError(f"{shape.name} has no NiSkinInstance for rigid-root skin.")

    bip01 = _find_node(stream, ARMATURE)
    if bip01 is None:
        raise RuntimeError(f"Missing '{ARMATURE}' root node in export.")

    num_verts = len(shape.data.vertices)
    bone_data = nif.NiSkinDataBoneData()
    bone_data.vertex_weights.resize(num_verts)
    bone_data.vertex_weights["f0"] = np.arange(num_verts, dtype=np.uint16)
    bone_data.vertex_weights["f1"] = np.ones(num_verts, dtype=np.float32)

    root_to_skin = np.array(shape.skin.data.matrix, copy=True)
    bone_data.matrix = np.linalg.inv(root_to_skin)
    bone_data.update_center_radius(shape.data.vertices, exact=True)

    shape.skin.root = bip01
    shape.skin.bones = [bip01]
    shape.skin.data.bone_data = [bone_data]
    print(f"  rigid root skin {shape.name}: 100% {bip01.name} ({num_verts} verts)")


def _find_node(stream: nif.NiStream, name: str):
    node = stream.find_object_by_name(name, nif.NiNode)
    if node is not None:
        return node
    for obj in stream.objects_of_type(nif.NiNode):
        if obj.name == name:
            return obj
    return None


def _detach_shape_tree(root: nif.NiNode, keep_names: set[str]) -> None:
    """Remove NiTriShape children (recursively under root) not in keep_names."""
    # Collect shapes to remove from the scene graph by filtering children lists.
    def prune(node: nif.NiNode) -> None:
        if not hasattr(node, "children") or node.children is None:
            return
        kept = []
        for child in node.children:
            if child is None:
                continue
            if isinstance(child, nif.NiTriShape):
                if child.name in keep_names:
                    kept.append(child)
                continue
            if isinstance(child, nif.NiNode):
                prune(child)
                kept.append(child)
            else:
                kept.append(child)
        node.children = kept

    prune(root)


def _postprocess_stream(
    stream: nif.NiStream,
    vanilla: nif.NiStream,
    *,
    keep_tris: set[str],
    texture_by_tri: dict[str, str],
    rigid_root_tris: set[str] | None = None,
    nudge_tris: set[str] | None = None,
) -> None:
    if stream.root is None:
        raise RuntimeError("Exported NIF has no root node.")
    stream.root.name = "Bip01"
    rigid_root_tris = rigid_root_tris or set()
    nudge_tris = nudge_tris or set()

    rename_map = {
        EXPORT_CHEST: TRI_CHEST,
        EXPORT_HAND_R: TRI_HAND_R,
        EXPORT_HAND_L: TRI_HAND_L,
    }
    vanilla_tris = {tri.name: tri for tri in vanilla.objects_of_type(nif.NiTriShape)}

    for shape in list(stream.objects_of_type(nif.NiTriShape)):
        shape.name = rename_map.get(shape.name, shape.name)

    _detach_shape_tree(stream.root, keep_tris)

    for shape in list(stream.objects_of_type(nif.NiTriShape)):
        if shape.name not in keep_tris:
            continue
        tex = texture_by_tri[shape.name]
        shape.properties = [
            prop
            for prop in shape.properties
            if prop is not None and not isinstance(prop, nif.NiAlphaProperty)
        ]
        _set_texture_on_shape(shape, tex)
        # Only nudge robe — hands stay aligned to biped Hand bind pose.
        if shape.name in nudge_tris:
            _nudge_shape_up(shape, CHEST_Z_NUDGE)
        if shape.name in rigid_root_tris:
            _apply_rigid_root_skin(shape, stream)

        vanilla_tri = vanilla_tris.get(shape.name)
        if vanilla_tri is None:
            continue
        for prop in vanilla_tri.properties:
            if isinstance(prop, nif.NiVertexColorProperty):
                shape.properties.append(_clone_property(prop))

    stream.sort()
    stream.merge_properties()

    # Force final texture paths (merge may have shared sources).
    for shape in stream.objects_of_type(nif.NiTriShape):
        if shape.name in texture_by_tri:
            _set_texture_on_shape(shape, texture_by_tri[shape.name])


def finalize_outputs(exported_path: Path, vanilla_path: Path) -> None:
    # Blender export keeps head/hand experiments in the temp NIF; body slots that need
    # pack-style biped bind poses are written from tools/reference skin refs instead.
    # (Hanging sleeve verts + Forearm weights = classic stretch — pack chest has
    # sleeves authored in biped arm bind pose.)
    del exported_path, vanilla_path
    _write_from_skin_ref(
        _ensure_skin_ref(PACK_CHEST_SRC, CHEST_SKIN_REF, "chest"),
        OUT_CHEST,
        texture=TEXTURE_ROBE,
        rename={},
        label="chest",
        float_torso=True,
    )
    _write_from_skin_ref(
        _ensure_skin_ref(PACK_ARMS_SRC, ARMS_SKIN_REF, "arms_1st"),
        OUT_ARMS_1ST,
        texture=TEXTURE_ROBE,
        rename={},
        label="arms_1st",
        float_torso=True,
    )
    _write_from_skin_ref(
        _ensure_skin_ref(PACK_HAND_SRC, HAND_SKIN_REF, "hand"),
        OUT_HAND,
        texture=TEXTURE_HAND,
        rename={
            "Tri Left Hand": TRI_HAND_L,
            "Tri Right Hand": TRI_HAND_R,
        },
        label="hand",
    )


def _ensure_skin_ref(pack_src: Path, ref_path: Path, label: str) -> Path:
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    if pack_src.is_file():
        shutil.copy2(pack_src, ref_path)
        print(f"Updated {label} skin ref from {pack_src}")
    if not ref_path.is_file():
        raise FileNotFoundError(
            f"Missing {label} skin reference {ref_path} "
            f"(and pack source not found at {pack_src})"
        )
    return ref_path


# Walk anim drives Bip01 Spine/Pelvis as LowerBody. Fold those into Spine1/Spine2
# so a Torso Idle blend can hold the robe while invisible legs walk.
_FLOAT_FOLD_BONES = ("Bip01 Pelvis", "Bip01 Spine")
_FLOAT_TARGET_BONES = ("Bip01 Spine1", "Bip01 Spine2")


def _float_torso_weights(shape: nif.NiTriShape) -> None:
    """Move Pelvis/Spine skin weight onto Spine1/Spine2 (Torso bone group)."""
    if shape.skin is None or shape.skin.data is None:
        return
    bones = list(shape.skin.bones)
    bone_data = list(shape.skin.data.bone_data)
    if not bones or len(bones) != len(bone_data):
        raise RuntimeError(f"{shape.name}: skin bones/data mismatch")

    name_to_idx = {b.name: i for i, b in enumerate(bones) if b is not None}
    fold_idxs = [name_to_idx[n] for n in _FLOAT_FOLD_BONES if n in name_to_idx]
    target_idxs = [name_to_idx[n] for n in _FLOAT_TARGET_BONES if n in name_to_idx]
    if not fold_idxs:
        print(f"  float weights {shape.name}: no Pelvis/Spine to fold")
        return
    if not target_idxs:
        raise RuntimeError(f"{shape.name}: missing Spine1/Spine2 for float reweight")

    num_verts = len(shape.data.vertices)
    # per-vert list of (bone_index, weight)
    per_vert: list[list[tuple[int, float]]] = [[] for _ in range(num_verts)]
    for bi, bd in enumerate(bone_data):
        for vi, w in zip(bd.vertex_weights["f0"], bd.vertex_weights["f1"]):
            per_vert[int(vi)].append((bi, float(w)))

    folded_mass = 0.0
    for vi, entries in enumerate(per_vert):
        if not entries:
            continue
        by_bone = {bi: w for bi, w in entries}
        fold = sum(by_bone.pop(bi, 0.0) for bi in fold_idxs)
        if fold <= 1e-8:
            per_vert[vi] = list(by_bone.items())
            continue
        folded_mass += fold
        t_weights = [by_bone.get(ti, 0.0) for ti in target_idxs]
        t_sum = sum(t_weights)
        if t_sum > 1e-8:
            for ti, tw in zip(target_idxs, t_weights):
                by_bone[ti] = tw + fold * (tw / t_sum)
        else:
            # No upper-spine weight yet — park on Spine1 (first target).
            by_bone[target_idxs[0]] = by_bone.get(target_idxs[0], 0.0) + fold
        # Drop near-zero; keep others.
        per_vert[vi] = [(bi, w) for bi, w in by_bone.items() if w > 1e-6]

    # Rebuild bone_data arrays; drop bones with no remaining weights.
    new_bones = []
    new_data = []
    for bi, (bone, bd) in enumerate(zip(bones, bone_data)):
        pairs = []
        for vi, entries in enumerate(per_vert):
            for ebi, w in entries:
                if ebi == bi:
                    pairs.append((vi, w))
        if not pairs and bi in fold_idxs:
            continue  # folded away
        if not pairs:
            # Keep empty non-fold bones only if they still exist elsewhere — skip empty.
            continue
        fresh = nif.NiSkinDataBoneData()
        fresh.matrix = np.array(bd.matrix, copy=True)
        fresh.vertex_weights.resize(len(pairs))
        fresh.vertex_weights["f0"] = np.array([p[0] for p in pairs], dtype=np.uint16)
        fresh.vertex_weights["f1"] = np.array([p[1] for p in pairs], dtype=np.float32)
        fresh.update_center_radius(shape.data.vertices, exact=True)
        new_bones.append(bone)
        new_data.append(fresh)

    shape.skin.bones = new_bones
    shape.skin.data.bone_data = new_data
    kept = [b.name for b in new_bones if b is not None]
    print(
        f"  float weights {shape.name}: folded Pelvis/Spine mass={folded_mass:.1f} "
        f"into Spine1/Spine2; bones={kept}"
    )


def _write_from_skin_ref(
    ref_path: Path,
    out_path: Path,
    *,
    texture: str,
    rename: dict[str, str],
    label: str,
    float_torso: bool = False,
) -> None:
    stream = nif.NiStream()
    stream.load(ref_path)
    if stream.root is not None:
        stream.root.name = "Bip01"

    for shape in stream.objects_of_type(nif.NiTriShape):
        shape.name = rename.get(shape.name, shape.name)
        _set_texture_on_shape(shape, texture)
        if float_torso:
            _float_torso_weights(shape)

    stream.sort()
    stream.merge_properties()
    for shape in stream.objects_of_type(nif.NiTriShape):
        _set_texture_on_shape(shape, texture)

    stream.save(out_path)
    bone_info = []
    for shape in stream.objects_of_type(nif.NiTriShape):
        n = len(shape.skin.bones) if shape.skin else 0
        bone_info.append(f"{shape.name}:{n}")
    print(
        f"Wrote {out_path} ({out_path.stat().st_size} bytes) "
        f"from {label} skin ref ({', '.join(bone_info)})"
    )


def _validate_skinned(path: Path, expected_tris: set[str], texture_needle: str) -> None:
    stream = nif.NiStream()
    stream.load(path)
    tri_names = {shape.name for shape in stream.objects_of_type(nif.NiTriShape)}
    data = path.read_bytes().decode("latin1", errors="ignore")
    checks = {
        "root Bip01": stream.root is not None and stream.root.name == "Bip01",
        "expected tris": expected_tris <= tri_names,
        "no extra tris": tri_names <= expected_tris,
        "NiSkinInstance": any(True for _ in stream.objects_of_type(nif.NiSkinInstance)),
        "no NiAlphaProperty": "NiAlphaProperty" not in data,
        "no morpher": "NiGeomMorpherController" not in data,
        "texture": texture_needle.lower() in data.lower(),
    }
    for shape in stream.objects_of_type(nif.NiTriShape):
        if shape.skin is None:
            checks[f"{shape.name} has skin"] = False
            continue
        n_bones = len(shape.skin.bones)
        # Chest: torso flex. Hands: pack-style finger/hand skin (many bones).
        min_bones = 2 if "Chest" in shape.name else 4
        checks[f"{shape.name} skinned"] = n_bones >= min_bones
        print(f"  {path.name} / {shape.name}: {n_bones} bones {[b.name for b in shape.skin.bones]}")

    failed = [name for name, ok in checks.items() if not ok]
    print(f"Validation {path.name}:")
    for name, ok in checks.items():
        print(f"  {'OK' if ok else 'FAIL'}: {name}")
    print(f"  tris: {sorted(tri_names)}")
    if failed:
        raise RuntimeError(f"{path.name} validation failed: {', '.join(failed)}")


def validate() -> None:
    _validate_skinned(OUT_CHEST, {TRI_CHEST}, "ghostward_tunic")
    _validate_skinned(OUT_ARMS_1ST, {TRI_CHEST}, "ghostward_tunic")
    _validate_skinned(OUT_HAND, {TRI_HAND_R, TRI_HAND_L}, "licheking")


def main() -> None:
    if not (MORROWIND / "Textures/Tx_LicheKing.dds").is_file():
        raise FileNotFoundError("Vanilla Tx_LicheKing.dds not found")
    if not (MOD_ROOT / "Textures/ag/TX_Ghostward_tunic.tga").is_file():
        raise FileNotFoundError("Missing mod tunic texture Textures/ag/TX_Ghostward_tunic.tga")

    # Body slots use pack bind-pose skin refs (sleeve/hand rooting). Geometry was
    # authored for the biped arm bind pose — Blender robe weights on hanging sleeves
    # stretch. Texture paths are rewritten to our bundled/vanilla assets.
    OUT_CHEST.parent.mkdir(parents=True, exist_ok=True)
    finalize_outputs(Path(), Path())
    validate()
    print("Wrote chest, hand, and 1st-person sleeve NIFs from skin refs.")


if __name__ == "__main__":
    main()
