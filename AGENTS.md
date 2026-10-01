# Agent guide

Start with [README.md](README.md) for the project layout, setup, builds, and release process.

- [docs/new-item.md](docs/new-item.md): add another scrap item.
- [docs/asset-workflow.md](docs/asset-workflow.md): edit Blender models, export FBX, and rebuild Unity assets.
- [docs/release.md](docs/release.md): prepare, publish, verify, and retry a release.
- [docs/validation.md](docs/validation.md): completed checks and their limits.
- [packaging/README.md](packaging/README.md): player-facing mod description, installation, and configuration.
- `src/MoreScrapItems/`: BepInEx plugin; `Assets/MoreScrapItems/`: Unity assets and bundle tools; `Art/`: Blender sources.
- `.github/workflows/publish-thunderstore.yml` and `scripts/Prepare-Release.ps1`: tag-triggered publishing and its Windows preparation step.

Keep Unity `.meta` files with their assets. Do not commit local game libraries, caches, or builds. After changing models or textures, rebuild the AssetBundle in Unity. Before tagging a release, rerun `Prepare-Release.ps1` and commit the updated `release-inputs/` alongside the sources. Do not create a release tag unless requested.
