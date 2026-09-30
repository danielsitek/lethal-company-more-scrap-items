"""Copy the current MoonFrame atlas into both Blender source files."""
import hashlib
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1]
atlas = root / "Assets/MoreScrapItems/Textures/MoonFrameBaseColor.png"
expected = hashlib.sha256(atlas.read_bytes()).digest()
atlas_data = atlas.read_bytes()

for name in ("MoonFrame", "MoonFramePlaced"):
    blend = root / "Art" / f"{name}.blend"
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    images = [node.image for material in bpy.data.materials if material.use_nodes
              for node in material.node_tree.nodes if node.type == "TEX_IMAGE" and node.image]
    if len(images) != 1:
        raise RuntimeError(f"{name}: expected exactly one atlas image")
    image = images[0]
    image.filepath = "//../Assets/MoreScrapItems/Textures/MoonFrameBaseColor.png"
    image.pack(data=atlas_data, data_len=len(atlas_data))
    if hashlib.sha256(image.packed_file.data).digest() != expected:
        raise RuntimeError(f"{name}: packed atlas differs from external PNG "
                           f"({len(image.packed_file.data)} vs {atlas.stat().st_size} bytes)")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    print(f"Packed {atlas.name} into {blend.name}")
