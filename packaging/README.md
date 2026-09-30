# More Scrap Items 0.1.0

More Scrap Items adds three original scrap finds to **Lethal Company**: a QUOTA mug, a framed portrait of Sírius the dog, and a small Ringhoffer 240 tram model. Pick them up, scan them, and bring them back to meet the quota. The picture frame stands at an angle when placed on the floor, with its support leg extended; it folds flat while held. The tram rings when dropped.

## Items

| Item | Base value | Default spawn weight |
| --- | ---: | ---: |
| QUOTA mug | 50–110 | 25 |
| Sírius frame | 90–180 | 18 |
| Ringhoffer 240 tram | 110–220 | 12 |

The game may adjust scrap values for the current moon. Spawn weights control how often each item is selected relative to other scrap.

## Installation

In **r2modman**, select Lethal Company, search for **MoreScrapItems** by **danielsitek**, and install it. The mod manager will also install the listed BepInEx and LethalLib dependencies. Launch the game with **Start modded**.

For manual installation, install BepInEx and LethalLib first, then extract this package into your game or mod profile folder. The plugin files should end up in `BepInEx/plugins/MoreScrapItems/`. Restart the game after updating the mod. Everyone in a multiplayer lobby should use the same mod version.

## Configuration

After the first launch, edit `BepInEx/config/danielsitek.more-scrap-items.cfg` in your mod profile:

- `[Spawn]` — `QuotaMugRarity`, `MoonFrameRarity`, and `Ringhoffer240Rarity` set each item's relative spawn weight. Set a value to `0` to disable that item.
- `[Holding]` — adjust each item's position and rotation in the player's hand. The default poses are ready to use.

The `[Development]` options are for local testing and should stay disabled during normal play.
