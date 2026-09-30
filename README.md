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
- `release-inputs/`: verzovaná DLL a AssetBundle připravené pro vydání; neobsahuje herní DLL.
- `scripts/Optimize-Models.py`: znovuvytvoření modelů z původních zdrojů; přepíše ruční úpravy optimalizovaných `.blend`.
- `scripts/Export-Edited-Model.py`: export uložených ručně upravených `.blend` do herního FBX.
- `docs/`: [návod pro nový předmět](docs/new-item.md), postup úprav a výsledky ověření.

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

## Publikování na Thunderstore

Token Thunderstore Service Account týmu `danielsitek` ulož do GitHub Actions secretu `TCLI_AUTH_TOKEN`. Žádný vlastní runner ani zapnutý domácí počítač při vydání nejsou potřeba.

Před vydáním nové verze:

1. Po změně modelů vytvoř AssetBundle v Unity přes **Tools → More Scrap Items → Build models and scrap bundle**.
2. Na Windows počítači s hrou a r2modman profilem spusť `./scripts/Prepare-Release.ps1 -Version 0.1.0`. Skript nastaví verzi, sestaví plugin, zkopíruje DLL i bundle do `release-inputs/` a uloží otisky zdrojů. Vygenerovaný ZIP můžeš nejprve otestovat v r2modmanu.
3. Commitni a pushni zdroje, verzi i `release-inputs/`. Potom můžeš z libovolného počítače odeslat tag `v0.1.0` na tento commit:

```powershell
git tag v0.1.0
git push origin v0.1.0
```

Workflow `.github/workflows/publish-thunderstore.yml` běží na GitHubem provozovaném runneru. Ověří, že vydávané binární soubory odpovídají commitu a tagu, vytvoří ZIP a GitHub Release a nahraje stejný ZIP na Thunderstore. Když po přípravě změníš kód nebo Unity assety, kontrola vydání zastaví; znovu spusť přípravný skript. Stejnou verzi nelze na Thunderstore zveřejnit podruhé. Stav sleduj na kartě **Actions**.

## Nastavení a testování

Konfigurace je `BepInEx/config/danielsitek.more-scrap-items.cfg`. Při prvním spuštění plugin zkopíruje nastavení ze starého `dansi.more-scrap-items.cfg`, pokud nový soubor ještě neexistuje; starý soubor ponechá jako zálohu. Síťové názvy předmětů zůstávají stejné.

- `[Spawn]`: četnost předmětů; 0 vypne daný předmět.
- `[Holding]`: pozice a rotace vůči hernímu úchopu.
- `[Development] SpawnInShipForTesting`: jednorázové vytvoření obou předmětů u místního hostitele.
- `[Development] RunHoldingTest`: automatický test běžných herních metod zvednutí a odložení; vyžaduje zapnuté testovací vytváření předmětů.

Vývojové volby při běžném hraní nech vypnuté. Výsledky skutečně provedených kontrol a jejich omezení jsou v `docs/validation.md`.

## Git

Verzujeme vlastní zdroje, modely, Unity `.meta` soubory, nastavení projektu, zámek balíčků a připravené binární soubory modu v `release-inputs/`. Lokální a herní DLL, cache, buildy a nepoužitá ukázková scéna šablony jsou ignorované. Vlastní projekt pluginu `.csproj` se verzovat musí.

Při přesouvání Unity assetu přesuň také jeho `.meta` soubor. [GitHub repozitář](https://github.com/danielsitek/lethal-company-more-scrap-items) je nastaven jako `origin`. Licenci pro případné veřejné zveřejnění je potřeba zvolit samostatně.
