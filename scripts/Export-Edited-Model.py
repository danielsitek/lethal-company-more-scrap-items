"""Export a manually edited Art/*.blend mesh without regenerating it from Art/Source.

Run with Blender --background --python scripts/Export-Edited-Model.py --
    --project-root C:/path/to/project --model QuotaMug
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
parser.add_argument('--model', choices=('QuotaMug', 'MoonFrame', 'MoonFramePlaced'), required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
root = args.project_root.resolve()
source = root / 'Art' / (args.model + '.blend')
target = root / 'Assets' / 'MoreScrapItems' / 'Models' / (args.model + '.fbx')

bpy.ops.wm.open_mainfile(filepath=str(source))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
if len(meshes) != 1 or meshes[0].name != args.model:
    raise RuntimeError(f'{args.model}: expected one mesh object named {args.model}.')
obj = meshes[0]
mesh = obj.data
mesh.calc_loop_triangles()
if not mesh.loop_triangles or len(mesh.uv_layers) != 1 or len(mesh.materials) != 1:
    raise RuntimeError(f'{args.model}: expected triangles, one UV map, and one material.')
if obj.hide_render or any(abs(v) > 1e-6 for v in obj.location) or any(abs(v) > 1e-6 for v in obj.rotation_euler) or any(abs(v-1) > 1e-6 for v in obj.scale):
    raise RuntimeError(f'{args.model}: keep the mesh visible at the original origin, rotation, and scale.')

material = mesh.materials[0]
images = [node.image for node in material.node_tree.nodes if node.type == 'TEX_IMAGE' and node.image]
if len(images) != 1 or images[0].packed_file is None:
    raise RuntimeError(f'{args.model}: expected one packed atlas image in its material.')
image = images[0]
texture = Path(bpy.path.abspath(image.filepath)).resolve()
if not texture.is_file() or hashlib.sha256(image.packed_file.data).digest() != hashlib.sha256(texture.read_bytes()).digest():
    raise RuntimeError(f'{args.model}: packed and external atlas differ; save the texture to {texture} before exporting.')

report = json.loads((root / 'Art' / 'optimization-report.json').read_text(encoding='utf-8'))
previous = report[args.model]['bounds']
vertices = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
low = Vector(min(v[i] for v in vertices) for i in range(3))
high = Vector(max(v[i] for v in vertices) for i in range(3))
if any(abs(low[i]-previous[0][i]) > .002 or abs(high[i]-previous[1][i]) > .002 for i in range(3)):
    raise RuntimeError(f'{args.model}: bounds changed; review held pose and collision before exporting.')

bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.export_scene.fbx(
    filepath=str(target), use_selection=True, object_types={'MESH'},
    axis_forward='-Z', axis_up='Y', apply_unit_scale=True,
    bake_space_transform=True, add_leaf_bones=False,
    use_mesh_modifiers=True, mesh_smooth_type='FACE',
    path_mode='STRIP', bake_anim=False,
)
print(f'MANUAL_MODEL_EXPORT_COMPLETE {args.model}: {len(mesh.loop_triangles)} triangles -> {target}')
