"""Set package and plugin versions from a release tag in a temporary checkout."""

import argparse
import json
from pathlib import Path
import re


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--tag", required=True)
args = parser.parse_args()
match = re.fullmatch(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", args.tag)
if match is None:
    raise SystemExit("Release tag must be vMAJOR.MINOR.PATCH.")
version = ".".join(match.groups())
root = Path(__file__).resolve().parents[1]


def replace_once(filename, pattern, replacement):
    path = root / filename
    content = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, lambda _: replacement, content, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"Version marker missing in {filename}.")
    path.write_text(updated, encoding="utf-8", newline="\n")


manifest_path = root / "packaging/manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version_number"] = version
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")

replace_once("thunderstore.toml", r'^versionNumber = "[^"]+"$', f'versionNumber = "{version}"')
replace_once("src/MoreScrapItems/MoreScrapItems.csproj", r'<Version>[^<]+</Version>', f'<Version>{version}</Version>')
replace_once("src/MoreScrapItems/Plugin.cs", r'public const string Version = "[^"]+";', f'public const string Version = "{version}";')
replace_once("packaging/README.md", r'^# More Scrap Items [^\n]+', f'# More Scrap Items {version}')
print(f"Set release version to {version} in the build checkout.")
