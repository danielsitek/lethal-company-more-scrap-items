# Vydání nové verze

Postup spouštěj v PowerShellu z kořene repozitáře. Nahraď `0.1.1` novým číslem verze; již vydanou verzi na Thunderstore nelze publikovat znovu. GitHub Actions potřebuje secret `TCLI_AUTH_TOKEN` s tokenem Service Account týmu `danielsitek`.

1. Dokonči změny a zkontroluj metadata v `packaging/manifest.json`, `thunderstore.toml` a hráčský popis v `packaging/README.md`. Pokud se změnily modely, textury nebo jiné Unity assety, v Unity zvol **Tools → More Scrap Items → Build models and scrap bundle**.
2. Na Windows s nainstalovanou hrou a profilem r2modman připrav binárky a ZIP:

   ```powershell
   $Version = "0.1.1"
   ./scripts/Prepare-Release.ps1 -Version $Version
   ```

   Skript nastaví verzi, sestaví plugin, zkopíruje DLL a AssetBundle do `release-inputs/` a zapíše kontrolní hashe. ZIP v `Builds/` lze před vydáním vyzkoušet jako lokální mod v r2modman.

3. Zkontroluj změny, commitni zdroje **spolu s** `release-inputs/` a pushni commit na `main`. Teprve pak vytvoř a pushni tag na tomto commitu:

   ```powershell
   git status --short
   git add -A
   git diff --cached --name-only
   git diff --cached --check
   git commit -m "Prepare release v$Version"
   git push origin main
   git tag "v$Version"
   git push origin "v$Version"
   ```

   Před commitem v seznamu staged souborů ověř, že neobsahuje místní herní knihovny, cache ani buildy.

4. Na GitHubu v **Actions → Build and publish More Scrap Items** ověř úspěch všech kroků. Workflow zkontroluje shodu binárek se zdroji, vytvoří ZIP, GitHub Release a publikuje stejný ZIP na Thunderstore. Ověř také ZIP v GitHub Release a stránku verze na Thunderstore.

## Když publikace selže

- Pokud se změnily zdroje nebo Unity assety po přípravě, znovu sestav AssetBundle podle potřeby a spusť `Prepare-Release.ps1` před vytvořením tagu.
- Pokud selže pouze publikační krok po vytvoření GitHub Release, oprav workflow na `main`. V Actions spusť **Build and publish More Scrap Items → Run workflow**, vyber `main` a do `release_tag` zadej existující tag (např. `v0.1.0`). Ruční běh načte zdroje z tagu a znovu použije existující GitHub Release i ZIP. Tag neposouvej.
- Než běh zopakuješ, zkontroluj, zda se verze už na Thunderstore nepublikovala; stejnou verzi nelze nahrát dvakrát.
