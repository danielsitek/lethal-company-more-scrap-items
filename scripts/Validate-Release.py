"""Validate a prebuilt GitHub Release ZIP before uploading it to Thunderstore."""

import argparse
import json
from pathlib import Path
import re
import struct
import tomllib
from xml.etree import ElementTree
from zipfile import ZipFile


def require(condition, message):
    if not condition:
        raise SystemExit(message)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--zip", type=Path, required=True)
parser.add_argument("--tag", required=True)
args = parser.parse_args()

match = re.fullmatch(r"v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", args.tag)
require(match is not None, "Release tag must be vMAJOR.MINOR.PATCH.")
version = ".".join(match.groups())
root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "packaging/manifest.json").read_text(encoding="utf-8"))
config = tomllib.loads((root / "thunderstore.toml").read_text(encoding="utf-8"))
readme = (root / "packaging/README.md").read_text(encoding="utf-8")
project = ElementTree.parse(root / "src/MoreScrapItems/MoreScrapItems.csproj")
plugin_source = (root / "src/MoreScrapItems/Plugin.cs").read_text(encoding="utf-8")
plugin_version = re.search(r'public const string Version = "([^"]+)";', plugin_source)

require(manifest["name"] == "MoreScrapItems", "Unexpected package name.")
require(manifest["version_number"] == version, "Manifest version does not match release tag.")
require(config["package"]["versionNumber"] == version, "Thunderstore config version does not match release tag.")
require(config["package"]["namespace"] == "danielsitek", "Unexpected Thunderstore team.")
require(config["package"]["name"] == manifest["name"], "Thunderstore package name differs from manifest.")
require(config["package"]["description"] == manifest["description"], "Thunderstore description differs from manifest.")
require(config["package"]["websiteUrl"] == manifest["website_url"], "Thunderstore website differs from manifest.")
require(project.findtext("./PropertyGroup/Version") == version, "Project version does not match release tag.")
require(plugin_version is not None and plugin_version.group(1) == version, "Plugin version does not match release tag.")
require(readme.startswith(f"# More Scrap Items {version}\n"), "Package README version does not match release tag.")
require(args.zip.name == f"MoreScrapItems-{version}.zip", "ZIP filename does not match release tag.")
require(args.zip.is_file(), "Release ZIP is missing.")

required = {
    "manifest.json",
    "README.md",
    "icon.png",
    "BepInEx/plugins/MoreScrapItems/MoreScrapItems.dll",
    "BepInEx/plugins/MoreScrapItems/morescrapassets",
}
with ZipFile(args.zip) as archive:
    names = [entry.filename for entry in archive.infolist() if not entry.is_dir()]
    require(len(names) == len(set(names)), "ZIP contains duplicate files.")
    require(required.issubset(names), "ZIP is missing required files.")
    require(set(names) <= required | {"CHANGELOG.md"}, "ZIP contains unexpected files.")
    require(archive.testzip() is None, "ZIP contains a damaged file.")
    require(json.loads(archive.read("manifest.json")) == manifest, "ZIP manifest differs from source.")
    for filename in ("README.md", "icon.png"):
        require(archive.read(filename) == (root / "packaging" / filename).read_bytes(), f"ZIP {filename} differs from source.")
    icon = archive.read("icon.png")
    require(icon[:8] == b"\x89PNG\r\n\x1a\n", "Icon is not a PNG.")
    require(struct.unpack(">II", icon[16:24]) == (256, 256), "Icon must be 256x256.")
    for filename in required - {"manifest.json", "README.md", "icon.png"}:
        require(archive.getinfo(filename).file_size > 0, f"{filename} is empty.")

print(f"Validated {args.zip.name} for Thunderstore team danielsitek.")
