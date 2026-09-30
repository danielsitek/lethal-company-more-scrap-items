# Nový model (scrap předmět)

Příklad používá ID `CopperBell`. Stejné ID použij ve všech názvech souborů i v kódu.

## 1. Připrav soubory

| Co | Kam |
| --- | --- |
| Blender zdroj | `Art/CopperBell.blend` |
| FBX | `Assets/MoreScrapItems/Models/CopperBell.fbx` |
| Atlas 512 × 512 | `Assets/MoreScrapItems/Textures/CopperBellBaseColor.png` |
| Průhledná ikona | `Assets/MoreScrapItems/Models/CopperBellIcon.png` |

Model má mít jeden mesh pojmenovaný `CopperBell`, jednu UV mapu a jeden materiál s atlasem zabaleným do `.blend`. Externí atlas musí být shodný se zabaleným a mít jméno `CopperBellBaseColor.png`. FBX vyexportuj přes `scripts/Export-Edited-Model.py -- --project-root . --model CopperBell`; skript rozpozná nový model podle názvu `.blend`. Unity `.meta` soubory ponech v repozitáři.

## 2. Přidej model do Unity

V `Assets/MoreScrapItems/Editor/MoreScrapAssetBuilder.cs`:

- Přidej `MakeModel("CopperBell", 1.0f)`; měřítko uprav podle výsledku ve hře.
- Do `paths` vlož prefab mezi prefaby a ikonu mezi ikony.
- Rozšiř validaci na všechny prefaby v poli `paths` (aktuálně `paths.Take(4)`), včetně nového předmětu.

## 3. Zaregistruj předmět

V `src/MoreScrapItems/Plugin.cs` přidej v `Awake` četnost a volání `Register` s unikátním `itemId`, názvem, cenou a váhou. V `Register` nastav vlastní úchop, polohu po odložení a další vlastnosti; současný kód jinak novému ID přidělí některé hodnoty rámečku. Pro jiný vzhled po odložení doplň variantu podle `MoonFrame`.

## 4. Sestav a ověř

1. V Unity spusť **Tools → More Scrap Items → Build models and scrap bundle** a zkontroluj `Builds/MoreScrapItems/asset-validation.txt`.
2. Spusť `./scripts/Build-Package.ps1` a ZIP importuj do testovacího profilu r2modman.
3. Ve hře ověř texturu, ikonu, skenování, zvednutí, natočení v ruce a polohu na zemi. Pro místní test můžeš zapnout `[Development] SpawnInShipForTesting`; potom jej vypni.

Podrobnosti jsou v [postupu pro assety](asset-workflow.md). V multiplayeru musí mít všichni stejnou verzi DLL i AssetBundle.

Pro veřejné vydání po testu spusť `./scripts/Prepare-Release.ps1 -Version X.Y.Z`, commitni změny včetně `release-inputs/` a odešli tag `vX.Y.Z`. Celý postup je v [README projektu](../README.md#publikování-na-thunderstore).
