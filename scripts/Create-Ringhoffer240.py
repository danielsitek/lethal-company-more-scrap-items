"""Generate the editable tram model, 512 px atlas, FBX and transparent icon in Blender.

Run with Blender --background --python scripts/Create-Ringhoffer240.py -- --project-root .
The model is an original stylised interpretation of historic motor car 240.
"""
import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

args = argparse.ArgumentParser()
args.add_argument('--project-root', default='.')
root = Path(args.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []).project_root).resolve()
art = root / 'Art'
models = root / 'Assets/MoreScrapItems/Models'
textures = root / 'Assets/MoreScrapItems/Textures'
for path in (art, models, textures):
    path.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
palette = [
    (.56,.025,.024), (.80,.045,.035), (.92,.84,.57), (.96,.93,.79),
    (.34,.15,.055), (.66,.37,.13), (.055,.075,.075), (.15,.19,.19),
    (.21,.30,.32), (.34,.48,.51), (.72,.57,.25), (.95,.81,.39),
    (.08,.11,.11), (.68,.73,.69), (.89,.86,.74), (.43,.025,.018),
]
atlas = bpy.data.images.new('Ringhoffer240BaseColor', width=512, height=512, alpha=True)
pixels = [0.0] * (512 * 512 * 4)
for yy in range(512):
    for xx in range(512):
        # 16 padded colour chips: all graphic variation lives in the texture.
        col = min(xx // 128, 3)
        row = min(yy // 128, 3)
        color = palette[row * 4 + col]
        grain = .97 + .03 * math.sin(xx * .41 + yy * .17)
        idx = (yy * 512 + xx) * 4
        pixels[idx:idx+4] = [min(1, c * grain) for c in color] + [1.0]
atlas.pixels = pixels
atlas.filepath_raw = str(textures / 'Ringhoffer240BaseColor.png')
atlas.file_format = 'PNG'
atlas.save()
atlas.pack()
atlas.filepath = '//../Assets/MoreScrapItems/Textures/Ringhoffer240BaseColor.png'
mat = bpy.data.materials.new('Ringhoffer240Atlas')
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get('Principled BSDF')
tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
tex.image = atlas
mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value = .45

pieces = []
def finish(obj, chip):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name='UVMap')
    u = (chip % 4 + .5) / 4
    v = (chip // 4 + .5) / 4
    for loop in uv.data:
        loop.uv = (u, v)
    pieces.append(obj)
    return obj

def box(name, center, size, chip):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, chip)

def rod(name, a, b, radius, chip, vertices=6):
    a, b = Vector(a), Vector(b)
    vec = b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=vec.length, location=(a+b)/2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = vec.to_track_quat('Z','Y').to_euler()
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return finish(obj, chip)

def fleet_number(axis, fixed, z, chip=11):
    """Small block digits avoid the large triangulation cost of outline fonts."""
    segments = {'2': 'abged', '4': 'fgbc', '0': 'abcdef'}
    for i, digit in enumerate('240'):
        offset = (i-1)*.011
        for seg in segments[digit]:
            horizontal = seg in 'agd'
            p = {'a':(0,.006),'b':(.0035,.003),'c':(.0035,-.003),
                 'd':(0,-.006),'e':(-.0035,-.003),'f':(-.0035,.003),
                 'g':(0,0)}[seg]
            if axis == 'x':
                center = (offset+p[0],fixed,z+p[1]); size = (.008,.0007,.0012) if horizontal else (.0012,.0007,.007)
            else:
                center = (fixed,offset+p[0],z+p[1]); size = (.0007,.008,.0012) if horizontal else (.0007,.0012,.007)
            box('fleet number 240', center, size, chip)

# Dimensions in metres: couplers define the exact 0.300 m overall length.
box('undercarriage', (0,0,.020), (.270,.069,.018), 6)
box('lower red body', (0,0,.052), (.268,.077,.047), 0)
box('waist brass band', (0,0,.075), (.269,.079,.003), 10)
box('cream window band', (0,0,.099), (.268,.078,.045), 3)
box('roof dark edge', (0,0,.123), (.280,.088,.004), 6)
box('cream roof', (0,0,.128), (.278,.090,.009), 3)
box('roof crown', (0,0,.134), (.235,.068,.004), 14)
for side in (-1,1):
    y = side * .0395
    for x in (-.105,-.065,-.025,.025,.065,.105):
        box('side glass', (x,y,.100), (.031,.0015,.027), 9)
        box('upper reflection', (x,y + side*.001,.108), (.028,.0005,.001), 13)
    for x in (-.122,-.087,-.046,0,.046,.087,.122):
        box('wood mullion', (x,y + side*.001,.100), (.0025,.002,.043), 5)
    box('side sill', (0,y + side*.001,.081), (.264,.002,.003), 4)
    box('side header', (0,y + side*.001,.120), (.263,.002,.002), 4)
    box('ornament red', (0,y + side*.001,.057), (.16,.001,.018), 1)
    box('ornament top line', (0,y + side*.002,.068), (.157,.001,.001), 11)
    box('ornament bottom line', (0,y + side*.002,.047), (.157,.001,.001), 11)
    box('company cream strip', (0,y + side*.002,.038), (.16,.001,.008), 2)
    # Side panels and door outlines.
    for x in (-.124,-.085,.085,.124):
        box('door trim', (x,y + side*.001,.056), (.002,.002,.039), 11)
    for x in (-.125,.125):
        box('step', (x,side*.047,.018), (.020,.016,.003), 6)
    for x in (-.087,.087):
        rod('axle', (x,-.044,.014), (x,.044,.014), .002, 6)
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=.012, depth=.005, location=(x,side*.042,.014), rotation=(math.pi/2,0,0))
        finish(bpy.context.object, 6)
    box('running board', (0,side*.045,.013), (.19,.006,.004), 6)
    fleet_number('x', y+side*.002, .057)

for end in (-1,1):
    x = end*.134
    for y in (-.023,0,.023):
        box('end glass', (x,y,.103), (.0015,.019,.025), 9)
    for y in (-.035,-.012,.012,.035):
        box('end wooden mullion', (x+end*.001,y,.101), (.002,.0025,.042), 5)
    box('end sill', (x+end*.001,0,.080), (.002,.076,.003), 4)
    box('end bumper', (end*.140,0,.020), (.006,.079,.005), 6)
    box('coupler', (end*.147,0,.017), (.006,.014,.004), 6)
    rod('headlight bezel', (end*.135,0,.055), (end*.139,0,.055), .009, 10, 12)
    rod('headlight lens', (end*.139,0,.055), (end*.140,0,.055), .006, 14, 12)
    fleet_number('y', end*.139, .072)

# A compact diamond pantograph stays visible while the 30 cm model remains hand-sized.
for y in (-.020,.020):
    rod('pantograph lower', (-.034,y,.139), (-.008,y,.173), .0017, 6)
    rod('pantograph upper', (-.008,y,.173), (.015,y,.143), .0017, 6)
    rod('pantograph brace', (-.034,y,.139), (.015,y,.143), .0011, 10)
rod('pantograph collector', (-.013,-.029,.174), (-.013,.029,.174), .0018, 6)
box('route board', (0,0,.140), (.095,.006,.009), 0)

bpy.ops.object.select_all(action='DESELECT')
for obj in pieces:
    obj.select_set(True)
bpy.context.view_layer.objects.active = pieces[0]
bpy.ops.object.convert(target='MESH')
bpy.ops.object.join()
tram = bpy.context.object
tram.name = 'Ringhoffer240'
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
assert len([o for o in bpy.data.objects if o.type == 'MESH']) == 1
assert len(tram.data.uv_layers) == 1 and len(tram.data.materials) == 1
assert abs((max(v.co.x for v in tram.data.vertices)-min(v.co.x for v in tram.data.vertices))-.300) < .0001
bpy.ops.wm.save_as_mainfile(filepath=str(art / 'Ringhoffer240.blend'))
bpy.ops.export_scene.fbx(filepath=str(models / 'Ringhoffer240.fbx'), use_selection=True,
    object_types={'MESH'}, axis_forward='-Z', axis_up='Y', apply_unit_scale=True,
    add_leaf_bones=False, bake_anim=False, path_mode='STRIP')

# Render an icon from the actual asset, with alpha and no backdrop.
world = bpy.data.worlds.new('IconWorld')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.35,.39,.42,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .65
bpy.ops.object.light_add(type='AREA', location=(-.20,-.24,.35))
bpy.context.object.data.energy = 30
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = .30
bpy.ops.object.camera_add(location=(.42,-.42,.29))
camera = bpy.context.object
direction = Vector((0,0,.085))-camera.location
camera.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = .35
bpy.context.scene.camera = camera
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.view_settings.view_transform = 'Standard'
scene.render.resolution_x = 256
scene.render.resolution_y = 256
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = str(models / 'Ringhoffer240Icon.png')
bpy.ops.render.render(write_still=True)
print('RINGHOFFER_COMPLETE tris=', len(tram.data.polygons) * 2, 'dimensions=', tuple(tram.dimensions))
