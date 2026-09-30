"""Ensure committed release binaries match the tagged source and version."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise SystemExit(message)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--tag", required=True)
args = parser.parse_args()
match = re.fullmatch(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", args.tag)
require(match is not None, "Release tag must be vMAJOR.MINOR.PATCH.")
version = ".".join(match.groups())
root = Path(__file__).resolve().parents[1]
inputs = root / "release-inputs"
manifest = json.loads((inputs / "source-hashes.json").read_text(encoding="utf-8"))
require(manifest["version"] == version, "Prepared binaries have a different version; run Prepare-Release.ps1 again.")

tracked = subprocess.check_output(
    ["git", "ls-files", "-z", "--", "Assets", "Packages", "ProjectSettings", "src", "Directory.Build.props", "global.json"],
    cwd=root,
)
source_paths = sorted(path.decode("utf-8") for path in tracked.split(b"\0") if path)
require(set(manifest["source"]) == set(source_paths), "Tracked build sources changed; run Prepare-Release.ps1 again.")
for relative in source_paths:
    blob = subprocess.check_output(
        ["git", "hash-object", "--path", relative, "--", relative], cwd=root
    ).decode("ascii").strip()
    require(blob == manifest["source"][relative], f"Build source changed: {relative}")

for name in ("MoreScrapItems.dll", "morescrapassets"):
    path = inputs / name
    require(path.is_file() and path.stat().st_size > 0, f"Prepared release input missing: {name}")
    require(digest(path) == manifest["artifacts"][name], f"Prepared release input changed: {name}")

print(f"Verified prepared binaries and {len(source_paths)} source files for {version}.")
