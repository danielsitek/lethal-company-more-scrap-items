"""Export saved, manually edited Art/<ItemId>.blend files to Unity FBX models.

Examples:
  blender --background --python scripts/Export-Edited-Model.py -- --project-root . --model Ringhoffer240
  blender --background --python scripts/Export-Edited-Model.py -- --project-root . --all

The script only reads .blend sources. It does not regenerate them or rebuild Unity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--project-root', type=Path, required=True)
selection = parser.add_mutually_exclusive_group(required=True)
selection.add_argument('--model', help='Item ID / Art/<ItemId>.blend filename stem')
selection.add_argument('--all', action='store_true', help='Validate and export every Art/*.blend model')
parser.add_argument('--validate-only', action='store_true', help='Check sources without writing FBX files')
parser.add_argument('--allow-bounds-change', action='store_true',
                    help='Accept changed dimensions after reviewing the Unity collider and in-game grip')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
root = args.project_root.resolve()
art_dir = root / 'Art'
models_dir = root / 'Assets/MoreScrapItems/Models'
textures_dir = root / 'Assets/MoreScrapItems/Textures'
report_path = art_dir / 'optimization-report.json'
report = json.loads(report_path.read_text(encoding='utf-8')) if report_path.is_file() else {}

if args.model:
    if Path(args.model).name != args.model or args.model in ('.', '..') or not args.model.isidentifier():
        parser.error('--model must be a plain item ID, for example Ringhoffer240')
    names = [args.model]
else:
    names = sorted(path.stem for path in art_dir.glob('*.blend'))
    if not names:
        parser.error(f'No .blend models found in {art_dir}')


def check_and_export(name):
    source = art_dir / f'{name}.blend'
    target = models_dir / f'{name}.fbx'
    if not source.is_file():
        raise RuntimeError(f'{name}: missing Blender source {source}')
    bpy.ops.wm.open_mainfile(filepath=str(source))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if len(meshes) != 1 or meshes[0].name != name:
        raise RuntimeError(f'{name}: expected one mesh object named {name}.')
    obj = meshes[0]
    mesh = obj.data
    mesh.calc_loop_triangles()
    if not mesh.loop_triangles or len(mesh.uv_layers) != 1 or len(mesh.materials) != 1:
        raise RuntimeError(f'{name}: expected triangles, one UV map, and one material.')
    if (obj.hide_render or any(abs(v) > 1e-6 for v in obj.location)
            or any(abs(v) > 1e-6 for v in obj.rotation_euler)
            or any(abs(v-1) > 1e-6 for v in obj.scale)):
        raise RuntimeError(f'{name}: keep the mesh visible at the original origin, rotation, and scale.')

    material = mesh.materials[0]
    if not material or not material.use_nodes:
        raise RuntimeError(f'{name}: expected a node-based material with one packed atlas.')
    images = [node.image for node in material.node_tree.nodes
              if node.type == 'TEX_IMAGE' and node.image]
    if len(images) != 1 or images[0].packed_file is None:
        raise RuntimeError(f'{name}: expected one packed atlas image in its material.')
    image = images[0]
    texture = Path(bpy.path.abspath(image.filepath)).resolve()
    expected_texture_id = 'MoonFrame' if name == 'MoonFramePlaced' else name
    expected_texture = (textures_dir / f'{expected_texture_id}BaseColor.png').resolve()
    if texture != expected_texture:
        raise RuntimeError(f'{name}: atlas path must be {expected_texture}, got {texture}.')
    if (not texture.is_file() or
            hashlib.sha256(image.packed_file.data).digest() != hashlib.sha256(texture.read_bytes()).digest()):
        raise RuntimeError(f'{name}: packed and external atlas differ; save both as {texture} before exporting.')
    if tuple(image.size) != (512, 512):
        raise RuntimeError(f'{name}: expected a 512x512 atlas, got {tuple(image.size)}.')

    vertices = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    low = Vector(min(v[i] for v in vertices) for i in range(3))
    high = Vector(max(v[i] for v in vertices) for i in range(3))
    if not args.allow_bounds_change:
        if name in report:
            previous = report[name]['bounds']
            if any(abs(low[i]-previous[0][i]) > .002 or abs(high[i]-previous[1][i]) > .002
                   for i in range(3)):
                raise RuntimeError(f'{name}: bounds changed; review held pose and collision, then use --allow-bounds-change.')
        elif name == 'Ringhoffer240' and abs((high.x - low.x) - .300) > .002:
            raise RuntimeError(f'{name}: expected a 0.300 m long model; use --allow-bounds-change after reviewing the size.')

    if args.validate_only:
        print(f'MANUAL_MODEL_VALID {name}: {len(mesh.loop_triangles)} triangles, dimensions={tuple(high-low)}')
        return
    if not target.parent.is_dir():
        raise RuntimeError(f'{name}: missing Unity Models directory {target.parent}')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=str(target), use_selection=True, object_types={'MESH'},
        axis_forward='-Z', axis_up='Y', apply_unit_scale=True,
        bake_space_transform=name != 'Ringhoffer240', add_leaf_bones=False,
        use_mesh_modifiers=True, mesh_smooth_type='FACE',
        path_mode='STRIP', bake_anim=False,
    )
    print(f'MANUAL_MODEL_EXPORT_COMPLETE {name}: {len(mesh.loop_triangles)} triangles -> {target}')


for model_name in names:
    check_and_export(model_name)
