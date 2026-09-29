# Ověření 2026-09-29

More Scrap Items 0.1.0 — ověření 2026-09-29
Blender 5.2.2: oba modely, zdroje BLEND, export FBX, ikony a náhled vytvořeny.
Unity 2022.3.9f1 HDRP: export AssetBundle s typovými informacemi a vestavěnými moduly.
Plugin .NET Standard 2.1: build Release, 0 chyb a 0 varování.
Lethal Company v81 / Unity 2022.3.62f2: čistý profil MoreScrapItems-Dev, místní hostitel.
AssetBundle úspěšně načten a oba předměty zaregistrovány přes LethalLib 1.2.0.
TEST_SPAWN_COMPLETE Quota mug — síťový prefab vytvořen, hodnota scrapu nastavena.
TEST_SPAWN_COMPLETE Moon frame — síťový prefab vytvořen, hodnota scrapu nastavena.
Žádná výjimka při registraci, vytvoření, zvednutí ani odložení obou předmětů.
HOLD_TEST Quota mug: held=True — skutečný herní raycast, síťový úchop, inventář a animace.
DROP_TEST Quota mug: released=True.
HOLD_TEST Moon frame: held=True — skutečný herní raycast, síťový úchop, inventář a animace.
DROP_TEST Moon frame: released=True.
Vizuální kontrola: hrnek má otvor nahoru a ucho u pravé ruky; rámeček má hory a měsíc správně nahoře a drží se u spodního rohu.
Rotace vůči hand anchoru (0,180,90) kompenzuje jeho natočení. Pozice: hrnek (0.015,0.22,-0.02), rámeček (0.18,0.24,0).
Vývojový automatický test používá běžné herní metody zvednutí a odložení; nenahrazuje skutečný test druhého multiplayer klienta.
Autor: danielsitek (https://github.com/danielsitek).
Neověřeno: připojení dalšího klienta, kompletní herní průchod/prodej a kompatibilita se všemi dalšími mody profilu lethal_01.

## Optimalizované modely 2026-09-29

- Blender zdroje: QuotaMug 606 trojúhelníků (původně 2 892), MoonFrame 310 (původně 1 868).
- Ověřeno: jeden mesh, jedna UV mapa a jeden materiál na předmět; zabalené textury a relativní existující cesty. Počátek, rotace a měřítko modelu zachované. Šířka/výška zachovaná; u rámu odstraněn přibližně 1 mm vystouplých špendlíků.
- Vizuální kontrola v Blenderu: čitelný QUOTA nápis, otevřený hrnek, správná orientace obrazu, opravené překryvy rámu.
- Unity 2022.3.9f1: úspěšný Windows AssetBundle, QuotaMug 606 / MoonFrame 310 trojúhelníků, každý jeden renderer a jeden materiál, oba atlasy 512 × 512 / BC7 / 10 mip úrovní.
- Plugin a instalační ZIP: úspěšný Release build, 0 chyb a 0 varování.
- Lethal Company v81, čistý vývojový profil: aktualizovaný AssetBundle načten a oba předměty zaregistrovány bez výjimky. Opakovaný místní test po optimalizaci: oba předměty vytvořeny, HOLD_TEST held=True a DROP_TEST released=True pro hrnek i rámeček. Vizuálně potvrzeno: hrnek má otvor nahoru a ucho u ruky; obrázek rámu je nahoře správně a úchop u spodního rohu. Textury zobrazené správně bez chybějících materiálů. Nastavení úchopu v pluginu se nezměnilo. Automatický test úchopu ve vývojovém profilu je po ověření opět vypnutý.
- Nároky: 4 760 → 916 trojúhelníků celkem, 23 → 2 renderery. AssetBundle 942 843 → 1 145 432 bajtů kvůli novým texturám. Změna FPS a celkové paměti nebyla změřena.
- Původní herní ověření výše platí pro původní geometrii. Nejde o nový test druhého multiplayer klienta ani prodeje předmětů.
