# More Scrap Items 0.1.0

More Scrap Items adds two original scrap finds to **Lethal Company**: a QUOTA mug and a framed picture of mountains beneath the moon. Pick them up, scan them, and bring them back to meet the quota. The picture frame stands at an angle when placed on the floor, with its support leg extended; it folds flat while held.

## Items

| Item | Base value | Default spawn weight |
| --- | ---: | ---: |
| QUOTA mug | 50–110 | 25 |
| Moon frame | 90–180 | 18 |

The game may adjust scrap values for the current moon. Spawn weights control how often each item is selected relative to other scrap.

## Installation

In **r2modman**, select Lethal Company, search for **MoreScrapItems** by **danielsitek**, and install it. The mod manager will also install the listed BepInEx and LethalLib dependencies. Launch the game with **Start modded**.

For manual installation, install BepInEx and LethalLib first, then extract this package into your game or mod profile folder. The plugin files should end up in `BepInEx/plugins/MoreScrapItems/`. Restart the game after updating the mod. Everyone in a multiplayer lobby should use the same mod version.

## Configuration

After the first launch, edit `BepInEx/config/danielsitek.more-scrap-items.cfg` in your mod profile:

- `[Spawn]` — `QuotaMugRarity` and `MoonFrameRarity` set each item's relative spawn weight. Set a value to `0` to disable that item.
- `[Holding]` — adjust each item's position and rotation in the player's hand. The default poses are ready to use.

The `[Development]` options are for local testing and should stay disabled during normal play.
