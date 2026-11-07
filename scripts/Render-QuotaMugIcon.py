"""Render the inventory icon from the saved mug mesh and one shipped print variant.

Run in Blender:
  blender --background --python scripts/Render-QuotaMugIcon.py -- --project-root .
"""
import argparse
from pathlib import Path
import sys

import bpy
from mathutils import Vector


parser = argparse.ArgumentParser()
parser.add_argument('--project-root', type=Path, required=True)
parser.add_argument('--variant', type=int, default=1, choices=range(1, 7))
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
root = args.project_root.resolve()
source = root / 'Art/QuotaMug.blend'
texture = root / f'Assets/MoreScrapItems/Textures/QuotaMugVariant{args.variant}BaseColor.png'
output = root / 'Assets/MoreScrapItems/Models/QuotaMugIcon.png'
package_icon = root / 'packaging/icon.png'

bpy.ops.wm.open_mainfile(filepath=str(source))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
if len(meshes) != 1 or meshes[0].name != 'QuotaMug':
    raise RuntimeError('Expected the saved QuotaMug mesh.')
material = meshes[0].data.materials[0]
image_nodes = [node for node in material.node_tree.nodes if node.type == 'TEX_IMAGE']
if len(image_nodes) != 1 or not texture.is_file():
    raise RuntimeError('Expected one image texture node and an existing variant atlas.')
image_nodes[0].image = bpy.data.images.load(str(texture), check_existing=False)

scene = bpy.context.scene
world = bpy.data.worlds.new('QuotaMugIconWorld')
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.42, .46, .49, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .8

bpy.ops.object.light_add(type='AREA', location=(-.32, -.40, .45))
bpy.context.object.data.energy = 85
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = .36

bpy.ops.object.camera_add(location=(.39, -.55, .30))
camera = bpy.context.object
camera.rotation_euler = (Vector((.025, 0, 0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = .33
scene.camera = camera

scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.view_settings.view_transform = 'Standard'
scene.render.resolution_x = scene.render.resolution_y = 512
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = str(output)
bpy.ops.render.render(write_still=True)
icon = bpy.data.images.load(str(output), check_existing=False)
icon.scale(256, 256)
icon.filepath_raw = str(package_icon)
icon.file_format = 'PNG'
icon.save()
print(f'QUOTA_MUG_ICON_COMPLETE variant={args.variant} output={output} package={package_icon}')
