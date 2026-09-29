# More Scrap Items 0.1.0

Autor: **danielsitek** — https://github.com/danielsitek

Dva původní scrap předměty: smaltovaný hrnek QUOTA a dřevěný rámeček s obrázkem hor a měsíce. Základní hodnoty jsou 50–110 a 90–180; hra je může upravit podle měsíce.

## Instalace

Importuj ZIP jako místní mod do r2modmanu s autorem `danielsitek`, nebo zkopíruj jeho složku `BepInEx` do profilu. Vyžaduje BepInEx 5.4.2305 a LethalLib 1.2.0 včetně závislostí. Spusť Start modded; po aktualizaci restartuj hru. V multiplayeru mají všichni používat stejnou verzi modu.

## Konfigurace

Soubor: `BepInEx/config/danielsitek.more-scrap-items.cfg`. Existující nastavení ze starého souboru se při prvním spuštění zkopíruje.

- `[Spawn]`: relativní četnost předmětů; 0 předmět vypne.
- `[Holding]`: posun a natočení v ruce. Výchozí nastavení bylo vizuálně ověřené ve hře.
- `[Development]`: pomocné testy. Při běžném hraní ponech obě volby vypnuté.

Modely, materiály, ikony a krátké zvuky jsou vlastní. Balíček neobsahuje vytažené herní modely. V Lethal Company v81 bylo ověřeno načtení, vytvoření, zvednutí, držení a odložení obou předmětů na místním hostiteli. Další multiplayer klient, prodej a kombinace se všemi dalšími mody zatím nejsou ověřené.
