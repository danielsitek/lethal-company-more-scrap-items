param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$')]
    [string]$Version,
    [string]$GameManaged,
    [string]$ProfileRoot
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$bundle = Join-Path $root 'Builds/MoreScrapItems/morescrapassets'
if (-not (Test-Path -LiteralPath $bundle)) { throw 'Build the Unity AssetBundle before preparing a release.' }
$bundleTime = (Get-Item -LiteralPath $bundle).LastWriteTimeUtc
Push-Location $root
try {
    $unityAssets = & git ls-files -z -- Assets/MoreScrapItems
    if ($LASTEXITCODE -ne 0) { throw 'Could not list Unity assets.' }
    foreach ($relative in $unityAssets.Split([char]0, [StringSplitOptions]::RemoveEmptyEntries)) {
        if ((Get-Item -LiteralPath (Join-Path $root $relative)).LastWriteTimeUtc -gt $bundleTime) {
            throw "Unity asset changed after the bundle was built: $relative"
        }
    }
} finally { Pop-Location }

function Replace-One([string]$relative, [string]$pattern, [string]$replacement) {
    $path = Join-Path $root $relative
    $content = [IO.File]::ReadAllText($path)
    $regex = [regex]::new($pattern, [Text.RegularExpressions.RegexOptions]::Multiline)
    if ($regex.Matches($content).Count -ne 1) { throw "Version marker missing or ambiguous in $relative" }
    $updated = $regex.Replace($content, [Text.RegularExpressions.MatchEvaluator]{ param($match) $replacement }, 1)
    [IO.File]::WriteAllText($path, $updated, [Text.UTF8Encoding]::new($false))
}

Replace-One 'src/MoreScrapItems/Plugin.cs' 'public const string Version = "[^"]+";' "public const string Version = `"$Version`";"
Replace-One 'src/MoreScrapItems/MoreScrapItems.csproj' '<Version>[^<]+</Version>' "<Version>$Version</Version>"
Replace-One 'thunderstore.toml' '^versionNumber = "[^"]+"$' "versionNumber = `"$Version`""
Replace-One 'packaging/README.md' '^# More Scrap Items [^\r\n]+' "# More Scrap Items $Version"

$manifestPath = Join-Path $root 'packaging/manifest.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$manifest.version_number = $Version
[IO.File]::WriteAllText($manifestPath, (($manifest | ConvertTo-Json -Depth 5) + "`n"), [Text.UTF8Encoding]::new($false))

$buildOptions = @{}
if ($GameManaged) { $buildOptions.GameManaged = $GameManaged }
if ($ProfileRoot) { $buildOptions.ProfileRoot = $ProfileRoot }
& (Join-Path $PSScriptRoot 'Build-Package.ps1') @buildOptions

$dll = Join-Path $root 'src/MoreScrapItems/bin/Release/netstandard2.1/MoreScrapItems.dll'
$dllVersion = [Reflection.AssemblyName]::GetAssemblyName($dll).Version
if ($dllVersion.Major -ne [int]($Version.Split('.')[0]) -or
    $dllVersion.Minor -ne [int]($Version.Split('.')[1]) -or
    $dllVersion.Build -ne [int]($Version.Split('.')[2])) {
    throw "Built DLL version $dllVersion does not match $Version."
}

$inputs = Join-Path $root 'release-inputs'
New-Item -ItemType Directory -Path $inputs -Force | Out-Null
Copy-Item -LiteralPath $dll -Destination (Join-Path $inputs 'MoreScrapItems.dll') -Force
Copy-Item -LiteralPath $bundle -Destination (Join-Path $inputs 'morescrapassets') -Force

Push-Location $root
try {
    $tracked = & git ls-files -z -- Assets Packages ProjectSettings src Directory.Build.props global.json
    if ($LASTEXITCODE -ne 0) { throw 'Could not list tracked build sources.' }
    $source = [ordered]@{}
    foreach ($relative in ($tracked.Split([char]0, [StringSplitOptions]::RemoveEmptyEntries) | Sort-Object)) {
        $source[$relative] = (& git hash-object --path $relative -- $relative).Trim()
        if ($LASTEXITCODE -ne 0) { throw "Could not hash build source: $relative" }
    }
    $artifacts = [ordered]@{}
    foreach ($name in @('MoreScrapItems.dll', 'morescrapassets')) {
        $artifacts[$name] = (Get-FileHash -LiteralPath (Join-Path $inputs $name) -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $record = [ordered]@{ version = $Version; source = $source; artifacts = $artifacts }
    [IO.File]::WriteAllText((Join-Path $inputs 'source-hashes.json'), (($record | ConvertTo-Json -Depth 5) + "`n"), [Text.UTF8Encoding]::new($false))
} finally { Pop-Location }

Write-Output "Prepared release inputs for v$Version. Commit release-inputs and the updated version files before tagging."
