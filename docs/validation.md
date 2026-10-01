# Ověření 2026-09-29

## Portrét Síriuse — 2026-09-30

- Výřez z dodané fotografie byl vložen do obrazové plochy společného atlasu a do ikony rámečku. Obě PNG byla vizuálně zkontrolována.
- Blender 5.2: oba `.blend` soubory mají zabalený atlas shodný s externím PNG; kontrola `Export-Edited-Model.py --all --validate-only` prošla. Geometrie obou variant zůstala na 40 trojúhelnících.
- Unity 2022.3.9f1: Windows AssetBundle byl znovu sestaven. Obě varianty mají jednu vykreslovací komponentu, jeden materiál, atlas 512 × 512 ve formátu BC7 a 10 mip úrovní.
- Plugin .NET Standard 2.1 a instalační ZIP byly sestaveny bez chyb; zobrazovaný název předmětu je `Sírius frame`, interní ID a konfigurace `MoonFrame` zůstávají stejné.
- Lethal Company v81, místní LAN hra v profilu `MoreScrapItems-Dev`: `TEST_SPAWN_COMPLETE Sírius frame`, první pokus o běžné zvednutí úspěšný (`held=True`) a odložení úspěšné (`released=True`). Při obou zvednutích `FRAME_STATE expected=held; valid=True; mesh=MoonFrame`, při obou odloženích `expected=placed; valid=True; mesh=MoonFramePlaced`. Po položení `FRAME_FLOOR gap=0,0000; rendererCount=1`.
- Vizuálně potvrzeno: portrét se v ruce vykresluje správně orientovaný, bez chybějící textury, a ikona zobrazuje Síriuse. Ve tmavém osvětlení lodi jsou detaily černé srsti méně zřetelné. Přímý pohled na přední stranu položeného rámečku a druhý multiplayer klient nebyly testovány. Testovací volby vývojového profilu byly vráceny na vypnuto. Před vydáním je třeba znovu připravit `release-inputs/` podle README.

## Ringhoffer 240 — 2026-09-30

- Jediný motorový vůz podle přiložených fotografií a [fotografií vozu 240 na Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Tram_240_(Prague)); jde o stylizovaný herní model, nikoli přesnou historickou repliku.
- Blender 5.2: `Art/Ringhoffer240.blend`, FBX, 512 × 512 atlas a průhledná ikona vytvořeny skriptem `scripts/Create-Ringhoffer240.py`. Zdroj má přesně 0,540 m na délku, jeden mesh, jednu UV mapu a jeden materiál. Zvonek WAV je původní syntéza ze `scripts/Create-RinghofferBell.py`.
- Unity 2022.3.9f1: AssetBundle znovu sestaven. Prefab má 0,54 × 0,31 × 0,20 m oproti délce rámečku 0,52 m, 2 364 importovaných trojúhelníků, jeden renderer a materiál, atlas BC7 s 10 mip úrovněmi. Builder kontroluje novou délku tramvaje.
- Plugin .NET Standard 2.1: Release build bez chyb a varování. Instalační ZIP obsahuje DLL a aktualizovaný AssetBundle. Registrace má samostatné ID 71003, konfigurovatelnou četnost a zvonek jako `dropSFX`.
- Lethal Company v81, místní hostitel v profilu MoreScrapItems-Dev: vývojový spawn, skutečný herní úchop a položení úspěšné (`GRAB_ATTEMPT held=True`, `HOLD_TEST held=True`, `DROP_TEST released=True`). Vizuálně ověřeno držení tramvaje v pravé ruce s offsetem (0,05; 0,20; −0,10), celý vůz zůstává v záběru. Po položení se přehrává `Ringhoffer240Bell` (`playing=True`) a model dosedne na podlahu (`TRAM_FLOOR gap=0,0000`). Akustická slyšitelnost nebyla nezávisle ověřena.
- 2026-10-01: výchozí i testovací pozice tramvaje snížena na (−0,05; 0,20; −0,10); nové vizuální umístění zatím čeká na ruční kontrolu ve hře.
- Neověřeno: druhý klient multiplayeru. Před vydáním znovu připravit `release-inputs/` postupem v README. Žádný release tag nebyl vytvořen.

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

## Předchozí optimalizace 2026-09-29

- Blender zdroje: QuotaMug 606 trojúhelníků (původně 2 892), MoonFrame 310 (původně 1 868).
- Ověřeno: jeden mesh, jedna UV mapa a jeden materiál na předmět; zabalené textury a relativní existující cesty. Počátek, rotace a měřítko modelu zachované. Šířka/výška zachovaná; u rámu odstraněn přibližně 1 mm vystouplých špendlíků.
- Vizuální kontrola v Blenderu: čitelný QUOTA nápis, otevřený hrnek, správná orientace obrazu, opravené překryvy rámu.
- Unity 2022.3.9f1: úspěšný Windows AssetBundle, QuotaMug 606 / MoonFrame 310 trojúhelníků, každý jeden renderer a jeden materiál, oba atlasy 512 × 512 / BC7 / 10 mip úrovní.
- Plugin a instalační ZIP: úspěšný Release build, 0 chyb a 0 varování.
- Lethal Company v81, čistý vývojový profil: aktualizovaný AssetBundle načten a oba předměty zaregistrovány bez výjimky. Opakovaný místní test po optimalizaci: oba předměty vytvořeny, HOLD_TEST held=True a DROP_TEST released=True pro hrnek i rámeček. Vizuálně potvrzeno: hrnek má otvor nahoru a ucho u ruky; obrázek rámu je nahoře správně a úchop u spodního rohu. Textury zobrazené správně bez chybějících materiálů. Nastavení úchopu v pluginu se nezměnilo. Automatický test úchopu ve vývojovém profilu je po ověření opět vypnutý.
- Nároky: 4 760 → 916 trojúhelníků celkem, 23 → 2 renderery. AssetBundle 942 843 → 1 145 432 bajtů kvůli novým texturám. Změna FPS a celkové paměti nebyla změřena.
- Původní herní ověření výše platí pro původní geometrii. Nejde o nový test druhého multiplayer klienta ani prodeje předmětů.

## Hrnek a dvě polohy rámečku 2026-09-29

- Upravené Blender modely: hrnek 604 trojúhelníků bez cedulky, QUOTA přímo na válcové UV těla; rámeček v ruce 40 trojúhelníků a položený rámeček 40. Třetí mesh sdílí rámovou texturu a materiál. Kontrola všech `.blend`: jeden mesh, jedna UV mapa, jeden materiál, relativní zabalený atlas, nezměněný počátek a osy.
- Vizuální náhled: rám má ostré hrany, pokosové spoje v textuře a varianta položená na zemi má náklon 15° dozadu s vyklopenou zadní podpěrou. Ve hře je celý nápis QUOTA vidět na hrnku při držení.
- Unity 2022.3.9f1: úspěšný Windows AssetBundle se třemi prefaby. Všechny mají jeden renderer a jeden materiál, atlas 512 × 512 v BC7 a 10 mip úrovní. Modely mají 604 / 40 / 40 trojúhelníků. Položená varianta má širší kolizní i skenovací box v hloubce.
- Plugin .NET Standard 2.1 a ZIP: Release build bez chyb a varování. AssetBundle má 1 118 896 bajtů. Instalován DLL i AssetBundle v profilech `lethal_01` a `MoreScrapItems-Dev`.
- Lethal Company v81, čistý místní vývojový profil: oba předměty vytvořeny; jejich běžné herní zvednutí i odložení uspělo. Rámeček se při prvním i druhém zvednutí přepnul na `MoonFrame`, při obou odloženích na `MoonFramePlaced`. V každém stavu zůstal jeden renderer.
- Měření skutečné polohy položeného rámečku proti podlaze po obou odloženích: mezera `0,0000 m` (před úpravou výšky byla `0,0400 m`). Po testu je `RunHoldingTest` opět vypnutý.
- Neověřeno: druhý multiplayer klient, prodej předmětu a kompatibilita s ostatními mody hlavního profilu.

## Ručně upravený hrnek 2026-09-29

- Uložený `Art/QuotaMug.blend` má upravený horní okraj a napojení ucha. Změnilo se 53 vrcholů, ale zůstalo 604 trojúhelníků, jedna UV mapa a materiál, zabalený atlas, počátek, osy a celkové rozměry. Externí PNG a zabalená textura se shodují.
- Upravený mesh byl vyexportován přímo z uloženého `.blend` do `QuotaMug.fbx` pomocí `Export-Edited-Model.py`; generátor z `Art/Source` nebyl spuštěn. Unity 2022.3.9f1 úspěšně sestavilo Windows AssetBundle. Kontrola prefabu: 604 trojúhelníků, jeden renderer, jeden materiál, atlas 512 × 512 / BC7 / 10 mip úrovní. Plugin Release a instalační ZIP sestaveny bez chyb a varování.
- Lethal Company v81, místní vývojový profil: nový hrnek se vytvořil, zvedl běžnou herní metodou (`HOLD_TEST held=True`) a odložil (`DROP_TEST released=True`). Vizuálně má otvor nahoru, ucho napojené na tělo a celý nápis QUOTA je čitelný v ruce. Rámeček zůstal funkční; po dvou odloženích mezera nad podlahou `0,0000 m`.
- DLL a AssetBundle byly aktualizovány v profilech `lethal_01` a `MoreScrapItems-Dev`. Vývojový automatický test byl po kontrole znovu vypnut. Druhý multiplayer klient nebyl testován.
