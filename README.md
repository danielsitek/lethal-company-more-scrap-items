# More Scrap Items

Mod pro Lethal Company od **danielsitek**. Přidává hrnek QUOTA a rámeček s původním obrázkem hor a měsíce.

| Předmět | Základní hodnota | Četnost | Trojúhelníky |
| --- | --- | --- | --- |
| Quota mug | 50–110 | 25 | 604 |
| Moon frame | 90–180 | 18 | 40 |

Rámeček se při odložení nakloní o 15° a vyklopí podpěru; v ruce je rovný se složenou podpěrou. Obě varianty mají 40 trojúhelníků a sdílejí texturu i materiál.

Hra může hodnotu upravit podle měsíce. Četnost je relativní váha při výběru scrapu.

## Struktura

- `Art/`: optimalizované Blender zdroje; původní modely jsou v `Art/Source`.
- `Assets/MoreScrapItems/`: FBX, ikony, materiály, prefaby a Unity nástroje.
- `Assets/HDRPDefaultResources/`: HDRP nastavení včetně zachovaných profilů šablony.
- `src/MoreScrapItems/`: BepInEx plugin.
- `packaging/`: metadata, ikona a README instalačního balíčku.
- `scripts/Build-Package.ps1`: sestavení pluginu a instalačního ZIPu.
- `scripts/Optimize-Models.py`: opakovatelný export low-poly modelů a texturových atlasů z původních zdrojů.
- `docs/`: postup úprav a výsledky ověření.

## Vývojové prostředí

Unity **2022.3.9f1**, HDRP **14.0.8**, .NET SDK **8** a Blender. Použij lokální instalaci Lethal Company a r2modman profil s BepInEx **5.4.2305**, LethalLib **1.2.0** a jeho závislostmi. Profil nejprve jednou spusť přes Start modded, aby vznikla knihovna MMHOOK.

Otevři kořen repozitáře v Unity Hubu. Unity obnoví balíčky podle `Packages/packages-lock.json`. Projekt sestavuje modelový AssetBundle; kompletní extrakce hry Project Patcherem není potřeba. Zachované balíčky patcheru jsou volitelné vývojové nástroje.

Plugin standardně hledá hru ve složce Steam v Program Files (x86) a profil `lethal_01` v aktuálním uživatelském AppData. Pro jiné cesty zkopíruj `Build.local.props.example` na `Build.local.props` a uprav `GameManaged` a `ProfileRoot`. Tento místní soubor se necommituje.

```powershell
dotnet build src/MoreScrapItems/MoreScrapItems.csproj -c Release
```

## Sestavení modu

1. V Unity vyber **Tools → More Scrap Items → Build models and scrap bundle**. Výstupem je `Builds/MoreScrapItems/morescrapassets`.
2. V PowerShellu v kořeni repozitáře spusť:

```powershell
./scripts/Build-Package.ps1
```

Výstup: `Builds/MoreScrapItems-0.1.0.zip`. Skript vyžaduje již sestavený bundle; při změně modelů ho nejprve znovu vytvoř v Unity. Sestavení nepřepisuje nainstalovaný mod a nespouští hru.

ZIP lze importovat do r2modmanu jako místní mod s autorem `danielsitek`. Při ruční instalaci zkopíruj jeho složku `BepInEx` do profilu. Po aktualizaci restartuj hru. Pro multiplayer mají všichni používat stejnou verzi modu.

## Nastavení a testování

Konfigurace je `BepInEx/config/dansi.more-scrap-items.cfg`. Interní GUID zůstává kvůli návaznosti konfigurace; autor balíčku je `danielsitek`.

- `[Spawn]`: četnost předmětů; 0 vypne daný předmět.
- `[Holding]`: pozice a rotace vůči hernímu úchopu.
- `[Development] SpawnInShipForTesting`: jednorázové vytvoření obou předmětů u místního hostitele.
- `[Development] RunHoldingTest`: automatický test běžných herních metod zvednutí a odložení; vyžaduje zapnuté testovací vytváření předmětů.

Vývojové volby při běžném hraní nech vypnuté. Výsledky skutečně provedených kontrol a jejich omezení jsou v `docs/validation.md`.

## Git

Verzujeme vlastní zdroje, modely, Unity `.meta` soubory, nastavení projektu a zámek balíčků. Lokální DLL, vytažené herní soubory, cache, buildy a nepoužitá ukázková scéna šablony jsou ignorované. Vlastní projekt pluginu `.csproj` se verzovat musí.

Při přesouvání Unity assetu přesuň také jeho `.meta` soubor. Repozitář zatím nemá GitHub remote. Licenci pro případné veřejné zveřejnění je potřeba zvolit samostatně.
