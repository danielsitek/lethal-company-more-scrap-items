"""Create a Thunderstore ZIP from the committed release inputs."""

import argparse
from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--tag", required=True)
args = parser.parse_args()
match = re.fullmatch(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", args.tag)
if match is None:
    raise SystemExit("Release tag must be vMAJOR.MINOR.PATCH.")
version = ".".join(match.groups())
root = Path(__file__).resolve().parents[1]
package = root / "Builds" / f"MoreScrapItems-{version}.zip"
package.parent.mkdir(parents=True, exist_ok=True)
files = {
    "manifest.json": root / "packaging/manifest.json",
    "icon.png": root / "packaging/icon.png",
    "README.md": root / "packaging/README.md",
    "BepInEx/plugins/MoreScrapItems/MoreScrapItems.dll": root / "release-inputs/MoreScrapItems.dll",
    "BepInEx/plugins/MoreScrapItems/morescrapassets": root / "release-inputs/morescrapassets",
}

with ZipFile(package, "w") as archive:
    for name, source in files.items():
        info = ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
        info.compress_type = ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, source.read_bytes())

print(f"Package: {package}")
