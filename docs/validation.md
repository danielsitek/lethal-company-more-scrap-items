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
