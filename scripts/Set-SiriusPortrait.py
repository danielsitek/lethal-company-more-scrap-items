"""Crop Sirius's supplied photo and place it in the MoonFrame atlas.

Run with a Python installation that has Pillow and NumPy:
  python scripts/Set-SiriusPortrait.py path/to/photo.jpg

The cropped source is kept in Art/Source so Optimize-Models.py can restore it.
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("photo", type=Path)
args = parser.parse_args()

source_path = root / "Art/Source/SiriusPortrait.png"
atlas_path = root / "Assets/MoreScrapItems/Textures/MoonFrameBaseColor.png"
icon_path = root / "Assets/MoreScrapItems/Models/MoonFrameIcon.png"

with Image.open(args.photo) as original:
    photo = ImageOps.exif_transpose(original).convert("RGB")
    if photo.size != (2880, 3840):
        raise ValueError(f"Expected the supplied 2880x3840 photo, got {photo.size}")
    # Coordinates were chosen on the displayed 1368x1824 preview.
    crop = tuple(round(value * 2880 / 1368) for value in (70, 755, 1240, 1567))
    portrait = photo.crop(crop).resize((366, 254), Image.Resampling.LANCZOS)
    portrait.save(source_path, optimize=True)

with Image.open(atlas_path) as original:
    atlas = original.convert("RGB")
    if atlas.size != (512, 512):
        raise ValueError(f"Expected a 512x512 atlas, got {atlas.size}")
    atlas.paste(portrait, (73, 129))
    atlas.save(atlas_path, optimize=True)

# The icon is an existing rendered frame. Project the same photo onto its
# four-corner picture plane, leaving the surrounding frame and alpha intact.
quad = ((104, 135), (400, 184), (400, 387), (104, 338))
src = ((0, 0), (366, 0), (366, 254), (0, 254))
rows = []
values = []
for (x, y), (u, v) in zip(quad, src):
    rows.extend(((x, y, 1, 0, 0, 0, -u*x, -u*y),
                 (0, 0, 0, x, y, 1, -v*x, -v*y)))
    values.extend((u, v))
coefficients = np.linalg.solve(np.array(rows, dtype=float), np.array(values, dtype=float))
with Image.open(icon_path) as original:
    icon = original.convert("RGBA")
    warped = portrait.transform(icon.size, Image.Transform.PERSPECTIVE,
                                tuple(coefficients), Image.Resampling.BICUBIC)
    from PIL import ImageDraw
    mask = Image.new("L", icon.size, 0)
    ImageDraw.Draw(mask).polygon(quad, fill=255)
    icon.paste(warped, (0, 0), mask)
    icon.save(icon_path, optimize=True)

print(f"Updated {source_path}, {atlas_path}, and {icon_path}")
