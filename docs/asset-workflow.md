# Úpravy a další předměty

## Úprava existujícího modelu

1. Otevři příslušný `.blend` v `Art/`. Obsahuje optimalizovaný mesh, UV mapu a zabalený texturový atlas. Zachovej střed modelu, měřítko a osy.
2. Textury jsou v `Assets/MoreScrapItems/Textures`: `QuotaMugBaseColor.png` a `MoonFrameBaseColor.png`. Horní část obsahuje nápis nebo obrázek, spodní pás obsahuje barevné vzorky pro ostatní povrchy. Při ruční úpravě atlasu zachovej rozmístění vzorků i UV mapování.
3. Po ruční změně uloženého `.blend` spusť níže uvedený exportní příkaz. Zachová upravený mesh a přepíše odpovídající FBX v `Assets/MoreScrapItems/Models`; stávající `.meta` ponechá. Export používá jednotky metrů, forward `-Z` a up `Y`.
4. V Unity znovu sestav bundle a poté instalační ZIP podle hlavního README.
5. V čistém vývojovém profilu ověř velikost, materiály, skenování, zvednutí, úchop a odložení. Změna geometrie může vyžadovat nové hodnoty `[Holding]` a klidové rotace.

Pro upravený hrnek spusť z kořene projektu:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python scripts/Export-Edited-Model.py -- --project-root . --model QuotaMug
```

Stejný skript přijímá `MoonFrame` a `MoonFramePlaced`. Před exportem kontroluje jeden mesh, jednu UV mapu a materiál, shodu zabalené a externí textury a původní rozměry potřebné pro herní úchop. Pokud rozměry úmyslně změníš, uprav nejprve úchop a kolizi. Poté sestav Unity bundle a instalační ZIP.

`Optimize-Models.py` používá původní soubory v `Art/Source` a přepisuje optimalizované `.blend`; na ručně upravený hrnek ho nespouštěj, pokud chceš své změny zachovat.

## Textury a optimalizace

| Model | Původní trojúhelníky | Optimalizované | Renderery | Materiály |
| --- | ---: | ---: | ---: | ---: |
| QuotaMug | 2 892 | 604 | 4 → 1 | 1 |
| MoonFrame (v ruce) | 1 868 | 40 | 19 → 1 | 1 |

Hrnek má profil s 24 obvodovými segmenty a zjednodušené ucho. Cedulka je odstraněná; QUOTA je namapovaná válcovými UV přímo na tělo hrnku. Rámeček má souvislý rám s ostrými hranami bez zkosení. Hory, měsíc, stromy, špendlíky i pokosové spoje jsou v textuře. Šířka, výška a počátek držených modelů jsou zachované; rámeček ztratil přibližně 1 mm vystouplých špendlíků.

Oba modely mají jednu UV mapu, jeden mesh a jeden materiál HDRP/Lit. Builder používá atlas 512 × 512, sRGB, BC7 pro Windows, mipmapy, Clamp a vypnutou CPU kopii textury i meshe. Materiály jsou jednostranné; čelní obraz i tělo hrnku mají normály směrem ven. Jde o snížení geometrie a počtu rendererů; změna FPS ani celkové spotřeby paměti nebyla změřena. Obě textury s mipmapami mají dohromady přibližně 683 KiB nepočítaje režii. Varianta položeného rámečku nepřidává další texturu ani materiál.

## Dvě polohy rámečku

`MoonFrame.blend` je rovný model se složenou podpěrou pro držení. `MoonFramePlaced.blend` je model nakloněný o 15° dozadu s otevřenou podpěrou pro odložení; také má 40 trojúhelníků. Oba používají `MoonFrameBaseColor.png` a `MoonFrameAtlas.mat`. Při změně obrázku upravuj společný atlas. Při změně samotného rámu uprav oba meshe nebo jejich společnou funkci v exportéru.

Unity builder vytvoří třetí nativní prefab `MoonFramePlaced`. Plugin přidává `FramePresentation` až za běhu a v jediném MeshFilteru přepíná mesh podle herních stavů `isHeld`, `isPocketed` a `isHeldByEnemy`. Vždy se vykresluje jen jedna varianta. Současně se mění rozměry kolize a skenovacího boxu. Herní klidová rotace je nulová; náklon je v geometrii a obě spodní opěrné hrany leží ve stejné výšce. DLL a AssetBundle aktualizuj společně.

## Obnovení z původních zdrojů

Původní modely zůstávají v `Art/Source`. Pro změnu textového nápisu nebo geometrického obrázku uprav tyto zdroje a spusť exportér:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --python scripts/Optimize-Models.py -- --project-root .
```

Exportér znovu vytvoří `Art/QuotaMug.blend`, `Art/MoonFrame.blend`, `Art/MoonFramePlaced.blend`, FBX, atlasy a `Art/optimization-report.json`. Přepíše ruční změny těchto odvozených souborů. Textury generuje ortografickým vykreslením původního nápisu a obrázku bez světel a stínů. Nejde o fotografii osvětleného modelu. Editovatelné Blender modely obsahují zabalené textury a relativní cesty do repozitáře.

Po změně složitosti modelu uprav profil nebo poměr decimace v exportéru a znovu proveď build v Unity. Výsledné počty a rozměry jsou v `Builds/MoreScrapItems/asset-validation.txt`; builder ověřuje i UV mapu, jeden renderer, jeden materiál a texturu s mipmapami.

## Nový předmět

Stručný postup od Blenderu po test ve hře je v [návodu k přidání předmětu](new-item.md).
