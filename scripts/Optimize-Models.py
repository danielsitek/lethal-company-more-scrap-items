"""Run with Blender --background --python scripts/Optimize-Models.py -- --project-root PATH.

High detail sources are kept in Art/Source. Exports keep the original axes and bounds.
"""
import argparse
import math
from pathlib import Path
import sys
import json
import bpy
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree

parser = argparse.ArgumentParser()
parser.add_argument('--project-root', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
root = args.project_root.resolve()
models = root / 'Assets/MoreScrapItems/Models'
textures = root / 'Assets/MoreScrapItems/Textures'
textures.mkdir(parents=True, exist_ok=True)
models.mkdir(parents=True, exist_ok=True)
palette = {
 'EnamelCream': (.84,.79,.65), 'EnamelTeal': (.025,.29,.31),
 'QuotaInk': (.035,.055,.05), 'WalnutWood': (.23,.105,.043),
 'Brass': (.61,.36,.11), 'IvoryMat': (.86,.81,.68),
 'NightSky': (.03,.085,.16), 'AmberMoon': (.95,.52,.18),
 'DistantMountains': (.14,.33,.39), 'NearMountains': (.04,.20,.23),
 'Snow': (.68,.79,.73), 'FrameBacking': (.12,.09,.058),
 'WalnutJoint': (.065,.025,.009)
}
swatches = list(palette)
atlas_size = 512

def bounds(obj):
 coords = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
 return Vector([min(v[i] for v in coords) for i in range(3)]), Vector([max(v[i] for v in coords) for i in range(3)])

def select(objects, active=None):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects: o.select_set(True)
 bpy.context.view_layer.objects.active = active or objects[0]

def emission(name):
 mat = bpy.data.materials.new('Bake_' + name)
 mat.use_nodes = True
 mat.node_tree.nodes.clear()
 output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
 node = mat.node_tree.nodes.new('ShaderNodeEmission')
 node.inputs['Color'].default_value = (*palette.get(name, palette['EnamelCream']), 1)
 mat.node_tree.links.new(node.outputs[0], output.inputs['Surface'])
 return mat

def quad(name, vertices, material):
 mesh = bpy.data.meshes.new(name)
 mesh.from_pydata(vertices, [], [(0,1,2,3)])
 mesh.update()
 o = bpy.data.objects.new(name, mesh)
 bpy.context.collection.objects.link(o)
 o.data.materials.append(material)
 return o

def render_atlas(name, objects, extent):
 originals = {o: list(o.data.materials) for o in objects}
 for o in objects:
  o.hide_render = False
  o.hide_set(False)
  for collection in o.users_collection: collection.hide_render = False
  for i, mat in enumerate(originals[o]): o.data.materials[i] = emission(mat.name.split('.')[0])
 scene = bpy.context.scene
 # Palette squares occupy a reserved strip below the artwork, with ample mip padding.
 patches = []
 for i, key in enumerate(swatches):
  u = (i + .5) / len(swatches)
  x = (u - .5) * extent
  z = (-.5 + .025) * extent
  w = extent / len(swatches) * .46
  h = extent * .023
  patches.append(quad('Palette_' + key, [(x-w,-.4,z-h),(x+w,-.4,z-h),(x+w,-.4,z+h),(x-w,-.4,z+h)], emission(key)))
 camera_data = bpy.data.cameras.new('AtlasCamera')
 camera = bpy.data.objects.new('AtlasCamera', camera_data)
 scene.collection.objects.link(camera)
 camera.location = (0,-1,0)
 camera.rotation_euler = (math.pi/2,0,0)
 camera_data.type = 'ORTHO'
 camera_data.ortho_scale = extent
 scene.camera = camera
 scene.render.engine = 'BLENDER_EEVEE'
 scene.render.resolution_x = scene.render.resolution_y = atlas_size
 scene.render.resolution_percentage = 100
 scene.render.image_settings.file_format = 'PNG'
 scene.render.image_settings.color_mode = 'RGB'
 scene.render.film_transparent = False
 scene.world.color = (0,0,0)
 scene.view_settings.view_transform = 'Standard'
 scene.view_settings.look = 'None'
 scene.view_settings.exposure = 0
 scene.view_settings.gamma = 1
 path = textures / (name + 'BaseColor.png')
 scene.render.filepath = str(path)
 bpy.ops.render.render(write_still=True)
 for o in patches + [camera]: bpy.data.objects.remove(o, do_unlink=True)
 for o, mats in originals.items():
  o.data.materials.clear()
  for mat in mats: o.data.materials.append(mat)
 image = bpy.data.images.load(str(path), check_existing=False)
 image.pack()
 image.filepath = '//../Assets/MoreScrapItems/Textures/' + path.name
 return image

def atlas_material(name, image):
 mat = bpy.data.materials.new(name + 'Atlas')
 mat.use_nodes = True
 bsdf = mat.node_tree.nodes.get('Principled BSDF')
 bsdf.inputs['Metallic'].default_value = .12 if name == 'QuotaMug' else 0
 bsdf.inputs['Roughness'].default_value = .35 if name == 'QuotaMug' else .7
 tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
 tex.image = image
 mat.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
 return mat

def uv_color(mesh, polygon, key):
 u = (swatches.index(key) + .5) / len(swatches)
 for loop in polygon.loop_indices: mesh.uv_layers.active.data[loop].uv = (u,.025)

def uv_project(obj, polygon, extent):
 for loop in polygon.loop_indices:
  v = obj.matrix_world @ obj.data.vertices[obj.data.loops[loop].vertex_index].co
  obj.data.uv_layers.active.data[loop].uv = (v.x/extent+.5,v.z/extent+.5)

def export(name, objects, material, original_bounds):
 for o in objects:
  o.data.materials.clear()
  o.data.materials.append(material)
  for p in o.data.polygons: p.material_index = 0
 select(objects)
 bpy.ops.object.join()
 obj = bpy.context.object
 obj.name = name
 # Unity retains a root at the original origin rather than at an arbitrary mesh centre.
 bpy.context.scene.cursor.location = (0,0,0)
 bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
 select([obj])
 bpy.ops.wm.save_as_mainfile(filepath=str(root/'Art'/f'{name}.blend'), relative_remap=False)
 bpy.ops.export_scene.fbx(filepath=str(models/f'{name}.fbx'), use_selection=True, object_types={'MESH'}, axis_forward='-Z', axis_up='Y', apply_unit_scale=True, bake_space_transform=True, add_leaf_bones=False, use_mesh_modifiers=True, mesh_smooth_type='FACE', path_mode='STRIP', bake_anim=False)
 obj.data.calc_loop_triangles()
 low, high = bounds(obj)
 # The existing held poses rely on these extents. Fail before publishing a mismatched model.
 tolerance = .002 if name == 'MoonFrame' else .0001
 if original_bounds is not None and (max(abs(low[i]-original_bounds[0][i]) for i in range(3)) > tolerance or max(abs(high[i]-original_bounds[1][i]) for i in range(3)) > tolerance):
  raise RuntimeError(f'{name}: bounds changed: {tuple(low)}, {tuple(high)}')
 return {'triangles':len(obj.data.loop_triangles),'objects':1,'materials':1,'texture':f'{atlas_size}x{atlas_size}','bounds':[list(low),list(high)]}

def scene_bounds(objects):
 pairs=[bounds(o) for o in objects]
 return (Vector([min(p[0][i] for p in pairs) for i in range(3)]), Vector([max(p[1][i] for p in pairs) for i in range(3)]))

def mug():
 name='QuotaMug'
 bpy.ops.wm.open_mainfile(filepath=str(root/'Art/Source'/f'{name}.blend'))
 originals=[o for o in bpy.context.scene.objects if o.type=='MESH']
 original_bounds=scene_bounds(originals)
 badge=next(o for o in originals if o.name.startswith('MugBadge'))
 text=next(o for o in originals if o.name.startswith('QuotaPrint'))
 body=next(o for o in originals if o.name.startswith('EnamelMugBody'))
 handle=next(o for o in originals if o.name.startswith('MugHandle'))
 # Bake ink onto an enamel background, sized for cylindrical UVs rather than a label card.
 circumference=2*math.pi*.0825
 vertical_extent=.23
 body.hide_render=handle.hide_render=badge.hide_render=True
 enamel=bpy.data.materials.new('EnamelCream')
 ink=bpy.data.materials.new('QuotaInk')
 text.data.materials.clear();text.data.materials.append(ink)
 text.matrix_world=Matrix.Translation((0,0,.05*circumference)) @ Matrix.Diagonal((1,1,circumference/vertical_extent,1)) @ text.matrix_world
 half=circumference/2
 background=quad('BakeEnamel', [(-half,-.0858,-half),(half,-.0858,-half),(half,-.0858,half),(-half,-.0858,half)],enamel)
 image=render_atlas(name, [background,text], circumference)
 body.hide_render=handle.hide_render=False
 material=atlas_material(name,image)
 body.data.calc_loop_triangles()
 kd=KDTree(len(body.data.polygons))
 for i,p in enumerate(body.data.polygons): kd.insert(p.center,i)
 kd.balance()
 profile=[(.069,-.0975),(.079,-.0895),(.086,.0805),(.09,.0905),(.089,.0975),(.082,.0975),(.08,.0885),(.072,-.0705),(.061,-.0795)]
 segments=24
 vertices=[(r*math.cos(2*math.pi*i/segments),r*math.sin(2*math.pi*i/segments),z) for r,z in profile for i in range(segments)]
 faces=[]
 for j in range(len(profile)-1):
  for i in range(segments):
   n=(i+1)%segments
   faces.append((j*segments+i,j*segments+n,(j+1)*segments+n,(j+1)*segments+i))
 vertices.extend([(0,0,profile[0][1]),(0,0,profile[-1][1])])
 for i in range(segments):
  n=(i+1)%segments
  faces.append((len(vertices)-2,n,i))
  faces.append((len(vertices)-1,(len(profile)-1)*segments+i,(len(profile)-1)*segments+n))
 mesh=bpy.data.meshes.new('LowPolyMugBody')
 mesh.from_pydata(vertices,[],faces)
 mesh.update()
 mesh.uv_layers.new(name='UVMap')
 low_body=bpy.data.objects.new('LowPolyMugBody',mesh)
 bpy.context.collection.objects.link(low_body)
 for p in mesh.polygons:
  _,idx,_=kd.find(p.center)
  key=body.data.materials[body.data.polygons[idx].material_index].name.split('.')[0]
  uv_color(mesh,p,key)
  if p.index//segments==1:
   angles=[math.atan2(mesh.vertices[mesh.loops[loop].vertex_index].co.y,mesh.vertices[mesh.loops[loop].vertex_index].co.x) for loop in p.loop_indices]
   us=[(.375+(angle+math.pi/2)/(2*math.pi))%1 for angle in angles]
   if max(us)-min(us)>.5:us=[u+1 if u<.5 else u for u in us]
   for loop,u in zip(p.loop_indices,us):
    z=mesh.vertices[mesh.loops[loop].vertex_index].co.z
    mesh.uv_layers.active.data[loop].uv=(u,z/vertical_extent+.55)
  p.use_smooth=p.index<(len(profile)-1)*segments
 # Mark transitions across the lip and base instead of smoothing through the entire cup.
 select([low_body])
 bpy.ops.object.mode_set(mode='EDIT')
 bpy.ops.mesh.select_all(action='SELECT')
 bpy.ops.mesh.normals_make_consistent(inside=False)
 bpy.ops.object.mode_set(mode='OBJECT')
 select([handle])
 hb=bounds(handle)
 modifier=handle.modifiers.new('Reduce handle segments','DECIMATE')
 modifier.ratio=.30
 bpy.ops.object.modifier_apply(modifier=modifier.name)
 # Decimation may move extreme vertices slightly; retain the exact gameplay bounds.
 lb=bounds(handle)
 for v in handle.data.vertices:
  for i in range(3): v.co[i]=hb[0][i]+(v.co[i]-lb[0][i])/(lb[1][i]-lb[0][i])*(hb[1][i]-hb[0][i])
 if not handle.data.uv_layers: handle.data.uv_layers.new(name='UVMap')
 for p in handle.data.polygons: uv_color(handle.data,p,'EnamelCream')
 bpy.data.objects.remove(body,do_unlink=True)
 bpy.data.objects.remove(text,do_unlink=True)
 bpy.data.objects.remove(badge,do_unlink=True)
 bpy.data.objects.remove(background,do_unlink=True)
 return export(name,[low_body,handle],material,original_bounds)

def box(name, lo, hi, color, material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(lo+hi)/2)
 obj=bpy.context.object;obj.name=name;obj.dimensions=hi-lo
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 while obj.data.uv_layers:obj.data.uv_layers.remove(obj.data.uv_layers[0])
 obj.data.uv_layers.new(name='UVMap');obj.data.materials.append(material)
 for p in obj.data.polygons:uv_color(obj.data,p,color)
 return obj

def frame_mesh(material):
 # Continuous square-edged border. Rail joints are pixels, not separate overlapping rails.
 outer=[(-.186,-.14),(.186,-.14),(.186,.14),(-.186,.14)]
 inner=[(-.158,-.112),(.158,-.112),(.158,.112),(-.158,.112)]
 vertices=[(x,-.0155,z) for x,z in outer]+[(x,-.0155,z) for x,z in inner]+[(x,-.0095,z) for x,z in inner]+[(x,.0155,z) for x,z in outer]
 faces=[]
 for i in range(4):
  j=(i+1)%4
  faces.append((i,j,4+j,4+i))
 for i in range(4):
  j=(i+1)%4
  faces.append((4+i,4+j,8+j,8+i))
 faces.append((8,9,10,11))
 faces.append((15,14,13,12))
 for i in range(4):
  j=(i+1)%4
  faces.append((i,12+i,12+j,j))
 mesh=bpy.data.meshes.new('ContinuousFrame');mesh.from_pydata(vertices,[],faces);mesh.update()
 mesh.uv_layers.new(name='UVMap');mesh.materials.append(material)
 obj=bpy.data.objects.new('ContinuousFrame',mesh);bpy.context.collection.objects.link(obj)
 for p in mesh.polygons:
  if p.index<4 or p.index==8:uv_project(obj,p,.4)
  else:uv_color(mesh,p,'FrameBacking' if p.index==9 else 'WalnutWood')
 select([obj]);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
 return obj

def frame():
 name='MoonFrame'
 bpy.ops.wm.open_mainfile(filepath=str(root/'Art/Source'/f'{name}.blend'))
 originals=[o for o in bpy.context.scene.objects if o.type=='MESH']
 original_bounds=scene_bounds(originals)
 wood=bpy.data.materials.new('WalnutWood');joint=bpy.data.materials.new('WalnutJoint')
 helpers=[quad('SquareCornerBake',[(-.186,.04,-.14),(.186,.04,-.14),(.186,.04,.14),(-.186,.04,.14)],wood)]
 for sx in (-1,1):
  for sz in (-1,1):
   a=Vector((sx*.158,-.022,sz*.112));b=Vector((sx*.186,-.022,sz*.14))
   perpendicular=Vector((-(b-a).z,0,(b-a).x)).normalized()*.00045
   helpers.append(quad('BakedMitreJoint',[a-perpendicular,b-perpendicular,b+perpendicular,a+perpendicular],joint))
 image=render_atlas(name,originals+helpers,.4)
 material=atlas_material(name,image)
 for o in originals+helpers:bpy.data.objects.remove(o,do_unlink=True)
 body=frame_mesh(material)
 folded=box('FoldedStand',Vector((-.027,.016,-.135)),Vector((.027,.03,.055)),'WalnutWood',material)
 held=export(name,[body,folded],material,original_bounds)
 # Make a second native mesh with the same atlas and origin; both feet meet z=-0.14.
 held_obj=bpy.context.object
 bpy.data.objects.remove(held_obj,do_unlink=True)
 body=frame_mesh(material)
 tilt=Matrix.Rotation(math.radians(-15),4,'X')
 for v in body.data.vertices:v.co=tilt@v.co
 body.data.update()
 dz=-.14-bounds(body)[0].z
 for v in body.data.vertices:v.co.z+=dz
 hinge=tilt@Vector((0,.023,.055));hinge.z+=dz
 height=hinge.z+.14
 reach=math.sqrt(.19**2-height**2)
 foot=Vector((0,hinge.y+reach,-.14))
 vertices=[]
 for center in (foot,hinge):
  vertices.extend([(center.x+x,center.y+y,center.z) for x,y in [(-.027,-.007),(.027,-.007),(.027,.007),(-.027,.007)]])
 faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 mesh=bpy.data.meshes.new('OpenKickstand');mesh.from_pydata(vertices,[],faces);mesh.update();mesh.uv_layers.new(name='UVMap');mesh.materials.append(material)
 stand=bpy.data.objects.new('OpenKickstand',mesh);bpy.context.collection.objects.link(stand)
 for p in mesh.polygons:uv_color(mesh,p,'WalnutWood')
 placed=export('MoonFramePlaced',[body,stand],material,None)
 placed['backward_tilt_degrees']=15
 placed['floor_z']=-.14
 return held,placed

report={'QuotaMug':mug()}
report['MoonFrame'],report['MoonFramePlaced']=frame()
(root/'Art/optimization-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('OPTIMIZATION_COMPLETE',json.dumps(report))
