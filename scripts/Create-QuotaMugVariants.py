"""Create the QuotaMug texture variants, each with a different "ai slop" label.

Run with a Python installation that has Pillow and NumPy:
  python scripts/Create-QuotaMugVariants.py [--sheet path/to/label-sheet.png]

With --sheet, the labels are first cut out of the supplied 748x1090 sheet and
stored in Art/Source/QuotaMugLabels, so the sheet itself is not needed later.
Every stored Label<n>.png becomes QuotaMugVariant<n>BaseColor.png.

Each variant starts from QuotaMugBaseColor.png: the QUOTA print is replaced by a
label and the palette strip used by the rest of the mesh is kept intact.
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image


root = Path(__file__).resolve().parents[1]
labels_dir = root / "Art/Source/QuotaMugLabels"
textures_dir = root / "Assets/MoreScrapItems/Textures"
base_atlas_path = textures_dir / "QuotaMugBaseColor.png"

SHEET_SIZE = (748, 1090)
SHEET_BACKGROUND = np.array((245, 245, 245), dtype=float)
# Crop boxes (left, top, right, bottom) in the supplied sheet, one per variant.
LABEL_BOXES = (
    (0, 14, 190, 108),      # 1: blue 3D
    (190, 220, 380, 328),   # 2: flames
    (565, 227, 748, 328),   # 3: yellow with black outline
    (380, 336, 565, 435),   # 4: purple glow
    (190, 742, 380, 832),   # 5: green 3D
    (0, 947, 190, 1042),    # 6: red-orange with black outline
)

# The atlas wraps the mug's circumference (2π · 0.0825 m) horizontally but
# covers only 0.23 m vertically, so labels are stretched to look undistorted.
VERTICAL_STRETCH = (2 * np.pi * 0.0825) / 0.23
LABEL_WIDTH = 140             # px; with the centre below, the right edge stays clear of the handle at x = 320
LABEL_CENTER = (235, 240)     # px; the QUOTA print was centred at (256, 240)
QUOTA_BOX = (200, 207, 312, 273)  # px; the QUOTA print plus a margin, painted over with enamel


def label_path(index: int) -> Path:
    return labels_dir / f"Label{index}.png"


def stored_label_indices() -> list[int]:
    return sorted(int(path.stem.removeprefix("Label")) for path in labels_dir.glob("Label*.png"))


def atlas_path(index: int) -> Path:
    return textures_dir / f"QuotaMugVariant{index}BaseColor.png"


def cut_out(cell: np.ndarray) -> Image.Image:
    """Key out the flat sheet background and remove its tint from soft edges."""
    distance = np.abs(cell - SHEET_BACKGROUND).max(axis=2)
    alpha = np.clip((distance - 6) / 40, 0, 1)[..., None]
    color = (cell - (1 - alpha) * SHEET_BACKGROUND) / np.maximum(alpha, 1e-3)
    rgba = np.concatenate((np.clip(color, 0, 255), alpha * 255), axis=2)
    return Image.fromarray(np.round(rgba).astype(np.uint8))


def extract_labels(sheet_path: Path) -> None:
    with Image.open(sheet_path) as original:
        if original.size != SHEET_SIZE:
            raise ValueError(f"Expected the supplied {SHEET_SIZE} sheet, got {original.size}")
        sheet = np.asarray(original.convert("RGB"), dtype=float)
    labels_dir.mkdir(parents=True, exist_ok=True)
    for index, (left, top, right, bottom) in enumerate(LABEL_BOXES, start=1):
        label = cut_out(sheet[top:bottom, left:right])
        label.crop(label.getbbox()).save(label_path(index), optimize=True)


def fit_to_mug(label: Image.Image) -> Image.Image:
    height = round(label.height * LABEL_WIDTH / label.width * VERTICAL_STRETCH)
    # Resample premultiplied colour so transparent pixels do not darken the edges.
    resized = label.convert("RGBa").resize((LABEL_WIDTH, height), Image.Resampling.LANCZOS)
    return resized.convert("RGBA")


def create_atlas(base: Image.Image, label: Image.Image) -> Image.Image:
    atlas = base.convert("RGBA")
    pixels = np.asarray(base.convert("RGB")).reshape(-1, 3)
    enamel = tuple(int(c) for c in np.median(pixels, axis=0))
    atlas.paste(enamel, QUOTA_BOX)
    label = fit_to_mug(label)
    position = (LABEL_CENTER[0] - label.width // 2, LABEL_CENTER[1] - label.height // 2)
    atlas.alpha_composite(label, position)
    return atlas.convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sheet", type=Path, help="label sheet to cut the labels from")
    args = parser.parse_args()

    if args.sheet:
        extract_labels(args.sheet)
    with Image.open(base_atlas_path) as base:
        for index in stored_label_indices():
            with Image.open(label_path(index)) as label:
                create_atlas(base, label).save(atlas_path(index), optimize=True)
            print(f"Wrote {atlas_path(index).relative_to(root)}")


if __name__ == "__main__":
    main()
