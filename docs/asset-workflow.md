# Úpravy a další předměty

## Úprava existujícího modelu

1. Otevři příslušný `.blend` v `Art/` a ulož změny do stejného zdroje. Zachovej střed modelu, měřítko a osy.
2. Exportuj vybrané modelové objekty do stejného FBX v `Assets/MoreScrapItems/Models`. Současné exporty používají jednotky metrů, forward `-Z`, up `Y` a aplikovanou konverzi souřadnic. Stávající `.meta` ponech.
3. V Unity znovu sestav bundle a poté instalační ZIP podle hlavního README.
4. V čistém vývojovém profilu ověř velikost, materiály, skenování, zvednutí, úchop a odložení. Změna geometrie může vyžadovat nové hodnoty `[Holding]` a klidové rotace.

## Textury a optimalizace

Současná verze používá barevné materiály a geometrické detaily, včetně nápisu a obrázku. Unity builder přiřazuje HDRP materiály podle názvů. Import textur do tohoto procesu zatím není implementovaný.

Další optimalizace má převést nápis a obrázek do UV textury, zjednodušit oblé části a snížit počet samostatných rendererů a materiálů. K tomu je třeba upravit také Unity builder a přiřazení textur. Samotná výměna FBX s novou texturou proto nestačí. Nároky porovnávej na více současně viditelných předmětech, ne pouze podle počtu trojúhelníků.

## Nový předmět

Zatím se předměty doplňují v kódu:

1. Přidej Blender zdroj do `Art/`, FBX a ikonu do `Assets/MoreScrapItems/Models`.
2. V `MoreScrapAssetBuilder.Build` přidej `MakeModel`, cestu prefabu a ikony do seznamu balíčku.
3. V `Plugin.Awake` přidej registraci s jedinečným interním názvem a ID, cenou, četností a váhou.
4. V `Plugin.Register` nastav pro nový předmět odpovídající pozici v ruce, rotaci na podlaze a vlastnosti. Současné podmínky rozlišují hrnek a rámeček; další předmět nesmí automaticky zdědit nastavení rámečku.
5. Sestav a ověř nový předmět ve hře. Před multiplayer testem aktualizuj mod u všech klientů.

Budoucí katalog předmětů může tato nastavení sjednotit. V této verzi ještě není implementovaný.
