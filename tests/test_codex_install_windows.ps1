$ErrorActionPreference = 'Stop'

$tests = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$root = Join-Path $tests ('.tmp-codex-install-' + [guid]::NewGuid().ToString('N'))
$fixture = Join-Path $root 'repo'
$source = Join-Path $fixture '.codex\skills\sample'
$destination = Join-Path $root 'profile\.codex\skills\sample'
$victim = Join-Path $root 'victim'

try {
    New-Item -ItemType Directory -Path (Join-Path $fixture 'scripts'), $source, (Split-Path $destination), $victim -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $tests '..\scripts\codex-install.bat') -Destination (Join-Path $fixture 'scripts\codex-install.bat')
    Set-Content -LiteralPath (Join-Path $source 'SKILL.md') -Value 'fixture'
    Set-Content -LiteralPath (Join-Path $victim 'keep.txt') -Value 'keep'
    New-Item -ItemType Junction -Path $destination -Target $victim | Out-Null

    $previousProfile = $env:USERPROFILE
    try {
        $env:USERPROFILE = Join-Path $root 'profile'
        $output = & (Join-Path $fixture 'scripts\codex-install.bat') --all 2>&1 | Out-String
    } finally {
        $env:USERPROFILE = $previousProfile
    }

    if ($output -notmatch 'Refusing linked destination' -or $output -notmatch '0 installed, 1 failed') { throw $output }
    if (-not (Test-Path -LiteralPath $destination) -or -not (Test-Path -LiteralPath (Join-Path $victim 'keep.txt'))) { throw 'Linked destination or target was changed' }
} finally {
    if (Test-Path -LiteralPath $destination) { [IO.Directory]::Delete($destination) }
    if (Test-Path -LiteralPath $root) {
        $resolved = (Resolve-Path -LiteralPath $root).Path
        if (-not $resolved.StartsWith($tests + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe temporary path' }
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}
