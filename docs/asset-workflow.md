# Úpravy a další předměty

## Úprava existujícího modelu

1. Otevři příslušný `.blend` v `Art/`. Obsahuje optimalizovaný mesh, UV mapu a zabalený texturový atlas. Zachovej střed modelu, měřítko a osy.
2. Textury jsou v `Assets/MoreScrapItems/Textures`: `QuotaMugBaseColor.png` a `MoonFrameBaseColor.png`. Horní část obsahuje nápis nebo obrázek, spodní pás obsahuje barevné vzorky pro ostatní povrchy. Při ruční úpravě atlasu zachovej rozmístění vzorků i UV mapování.
3. Exportuj model do stejného FBX v `Assets/MoreScrapItems/Models`. Export používá jednotky metrů, forward `-Z`, up `Y` a aplikovanou konverzi souřadnic. Stávající `.meta` ponech.
4. V Unity znovu sestav bundle a poté instalační ZIP podle hlavního README.
5. V čistém vývojovém profilu ověř velikost, materiály, skenování, zvednutí, úchop a odložení. Změna geometrie může vyžadovat nové hodnoty `[Holding]` a klidové rotace.

## Textury a optimalizace

| Model | Původní trojúhelníky | Optimalizované | Renderery | Materiály |
| --- | ---: | ---: | ---: | ---: |
| QuotaMug | 2 892 | 606 | 4 → 1 | 1 |
| MoonFrame | 1 868 | 310 | 19 → 1 | 1 |

Hrnek má nový profil s 24 obvodovými segmenty, zjednodušené ucho a původní nápis převedený do textury na dvou trojúhelnících. Rámeček má jednu úroveň zkosení hran; hory, měsíc, stromy a drobné špendlíky jsou v textuře. Spoje rámu a podklad jsou upravené tak, aby se plochy nepřekrývaly. Šířka, výška a počátek jsou zachované; rámeček ztratil přibližně 1 mm vystouplých špendlíků.

Oba modely mají jednu UV mapu, jeden mesh a jeden materiál HDRP/Lit. Builder používá atlas 512 × 512, sRGB, BC7 pro Windows, mipmapy, Clamp a vypnutou CPU kopii textury i meshe. Materiály jsou jednostranné; čelní obraz i štítek mají normály směrem ven. Jde o snížení geometrie a počtu rendererů; změna FPS ani celkové spotřeby paměti nebyla změřena. Obě textury s mipmapami mají dohromady přibližně 683 KiB nepočítaje režii. AssetBundle se kvůli texturám zvětšil z 942 843 na 1 145 432 bajtů.

## Obnovení z původních zdrojů

Původní modely zůstávají v `Art/Source`. Pro změnu textového nápisu nebo geometrického obrázku uprav tyto zdroje a spusť exportér:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background --python scripts/Optimize-Models.py -- --project-root .
```

Exportér znovu vytvoří `Art/QuotaMug.blend`, `Art/MoonFrame.blend`, FBX, atlasy a `Art/optimization-report.json`. Přepíše ruční změny těchto odvozených souborů. Textury generuje ortografickým vykreslením původního nápisu a obrázku bez světel a stínů. Nejde o fotografii osvětleného modelu. Editovatelné Blender modely obsahují zabalené textury a relativní cesty do repozitáře.

Po změně složitosti modelu uprav profil nebo poměr decimace v exportéru a znovu proveď build v Unity. Výsledné počty a rozměry jsou v `Builds/MoreScrapItems/asset-validation.txt`; builder ověřuje i UV mapu, jeden renderer, jeden materiál a texturu s mipmapami.

## Nový předmět

Zatím se předměty doplňují v kódu:

1. Přidej Blender zdroj do `Art/`, FBX a ikonu do `Assets/MoreScrapItems/Models` a atlas `<ID>BaseColor.png` do `Assets/MoreScrapItems/Textures`. Model má používat jeden mesh, jednu UV mapu a jeden materiál.
2. V `MoreScrapAssetBuilder.Build` přidej `MakeModel`, cestu prefabu a ikony do seznamu balíčku; rozšiř seznam validovaných prefabů, který nyní kontroluje první dva. Builder přiřadí atlas podle ID. Textura se dostane do bundle jako závislost materiálu.
3. V `Plugin.Awake` přidej registraci s jedinečným interním názvem a ID, cenou, četností a váhou.
4. V `Plugin.Register` nastav pro nový předmět odpovídající pozici v ruce, rotaci na podlaze a vlastnosti. Současné podmínky rozlišují hrnek a rámeček; další předmět nesmí automaticky zdědit nastavení rámečku.
5. Sestav a ověř nový předmět ve hře. Před multiplayer testem aktualizuj mod u všech klientů.

Budoucí katalog předmětů může tato nastavení sjednotit. V této verzi ještě není implementovaný.
