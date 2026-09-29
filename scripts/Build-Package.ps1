param(
    [string]$GameManaged,
    [string]$ProfileRoot
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$bundle = Join-Path $repoRoot 'Builds/MoreScrapItems/morescrapassets'
if (-not (Test-Path -LiteralPath $bundle)) {
    throw 'Build the assets in Unity first: Tools > More Scrap Items > Build models and scrap bundle.'
}
$dotnetCommand = Get-Command dotnet -ErrorAction SilentlyContinue
$dotnetPath = if ($dotnetCommand) { $dotnetCommand.Source } else { Join-Path ([Environment]::GetFolderPath('ProgramFiles')) 'dotnet/dotnet.exe' }
if (-not (Test-Path -LiteralPath $dotnetPath)) { throw 'Install .NET SDK 8 before building the plugin.' }
$buildArgs = @('build', (Join-Path $repoRoot 'src/MoreScrapItems/MoreScrapItems.csproj'), '-c', 'Release')
if ($GameManaged) { $buildArgs += "-p:GameManaged=$GameManaged" }
if ($ProfileRoot) { $buildArgs += "-p:ProfileRoot=$ProfileRoot" }
Push-Location $repoRoot
try {
    & $dotnetPath @buildArgs
    if ($LASTEXITCODE -ne 0) { throw 'Plugin build failed.' }
    $manifest = Get-Content -LiteralPath (Join-Path $repoRoot 'packaging/manifest.json') -Raw | ConvertFrom-Json
    $stage = Join-Path $repoRoot ('Builds/staging/' + [guid]::NewGuid().ToString('N'))
    $pluginFolder = Join-Path $stage 'BepInEx/plugins/MoreScrapItems'
    New-Item -ItemType Directory -Path $pluginFolder -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $repoRoot 'src/MoreScrapItems/bin/Release/netstandard2.1/MoreScrapItems.dll') -Destination $pluginFolder
    Copy-Item -LiteralPath $bundle -Destination $pluginFolder
    foreach ($name in @('manifest.json', 'icon.png', 'README.md')) {
        Copy-Item -LiteralPath (Join-Path $repoRoot "packaging/$name") -Destination $stage
    }
    $zip = Join-Path $repoRoot ("Builds/MoreScrapItems-" + $manifest.version_number + '.zip')
    Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -Force
    Write-Output "Package: $zip"
} finally { Pop-Location }
