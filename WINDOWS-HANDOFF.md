# Dočasné: dokončení variant potisku hrnku na Windows

> Tento soubor po dokončení smaž a smazání commitni.

Větev `feature/quota-mug-variants` přidává 6 variant potisku „ai slop“ pro Quota mug. Textury, builder, plugin i dokumentace jsou commitnuté. Vznikly na Macu bez Unity a .NET, proto chybí build, `.meta` soubory a test ve hře.

## 1. Unity build

1. `git pull` a přepni na `feature/quota-mug-variants`.
2. Otevři projekt v Unity 2022.3.9f1 a spusť **Tools → More Scrap Items → Build models and scrap bundle**.
3. Zkontroluj `Builds/MoreScrapItems/asset-validation.txt`. Musí obsahovat řádky `QuotaMugVariant1`–`QuotaMugVariant6` s rozměrem textury 512x512 a mipmapami. Pokud vznikne `more-scrap-build-error.txt`, oprav chybu.
4. Commitni nově vygenerované soubory:
   - `Assets/MoreScrapItems/Textures/QuotaMugVariant{1..6}BaseColor.png.meta`
   - `Assets/MoreScrapItems/Materials/QuotaMugVariant{1..6}.mat` a jejich `.meta`
   - případné změny `QuotaMugAtlas.mat` a dalších materiálů po refaktoringu builderu; nečekané změny nejdřív prohlédni.

## 2. Plugin a balíček

1. `dotnet build src/MoreScrapItems/MoreScrapItems.csproj -c Release` musí projít bez chyb a varování. Kód nebyl kompilován; nové soubory jsou `src/MoreScrapItems/MaterialVariant.cs` a metoda `LoadMaterialVariants` v `Plugin.cs`.
2. `./scripts/Build-Package.ps1` a ZIP importuj do profilu **MoreScrapItems-Dev**.

## 3. Test ve hře

- Postupuj podle [docs/spawn-testing.md](docs/spawn-testing.md). `SpawnInShipForTesting` vytvoří jen jeden hrnek. Další varianty uvidíš po několika spuštěních nebo u přirozeně spawnutých hrnků na měsících.
- Ověř:
  - nápis je čitelný v ruce i na zemi, není zdeformovaný a nezasahuje pod ucho;
  - v logu nejsou výjimky o chybějících materiálech (`Missing QuotaMug material variants`);
  - v multiplayeru vidí oba hráči na stejném hrnku stejný nápis.
- Po testu vrať `SpawnInShipForTesting = false`.
- Výsledek zapiš do `docs/validation.md`, sekce „Varianty potisku hrnku 2026-11-03“, a odstraň řádek „Neověřeno…“.

## 4. Otevřená rozhodnutí

- Nápis QUOTA už na spawnutém hrnku nikdy není. Ikona v inventáři ho ale pořád ukazuje a předmět se dál jmenuje „Quota mug“. Rozhodni, zda vrátit QUOTA jako 7. variantu, nebo změnit ikonu či název.
- Po načtení uložené hry může hrnek na lodi změnit potisk, protože varianta závisí na `NetworkObjectId`. Pokud to vadí, je potřeba variantu ukládat a synchronizovat.

## 5. Dokončení

1. Smaž zdrojový obrázek `BFDAE9D2-4FA1-49F8-8C05-4E2C88AB02E9.png`, pokud ho máš lokálně. Nikdy nebyl commitnutý.
2. Smaž tento soubor, commitni a otevři PR do `main`.
3. `release-inputs/` aktualizuj až při přípravě vydání (`Prepare-Release.ps1`).
