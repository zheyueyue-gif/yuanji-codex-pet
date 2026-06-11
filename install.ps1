$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$codexHome = Join-Path $env:USERPROFILE ".codex"
$petDir = Join-Path $codexHome "pets\chujian"
$configPath = Join-Path $codexHome "config.toml"

New-Item -ItemType Directory -Force -Path $petDir | Out-Null
Copy-Item -LiteralPath (Join-Path $repoRoot "pet\pet.json") -Destination (Join-Path $petDir "pet.json") -Force
Copy-Item -LiteralPath (Join-Path $repoRoot "pet\spritesheet.webp") -Destination (Join-Path $petDir "spritesheet.webp") -Force

if (Test-Path -LiteralPath $configPath) {
  $text = [System.IO.File]::ReadAllText($configPath)
} else {
  New-Item -ItemType Directory -Force -Path $codexHome | Out-Null
  $text = ""
}

$selectedLine = 'selected-avatar-id = "custom:chujian"'
$pattern = '(?m)^selected-avatar-id\s*=\s*"[^"]*"\s*$'

if ($text -match $pattern) {
  $updated = [regex]::Replace($text, $pattern, $selectedLine, 1)
} elseif ($text -match '(?m)^\[desktop\]\s*$') {
  $updated = [regex]::Replace($text, '(?m)^\[desktop\]\s*$', '[desktop]' + "`r`n" + $selectedLine, 1)
} else {
  $updated = $text.TrimEnd() + "`r`n`r`n[desktop]`r`n" + $selectedLine + "`r`n"
}

[System.IO.File]::WriteAllText($configPath, $updated, [System.Text.UTF8Encoding]::new($false))

Write-Host "Installed Chujian Codex pet."
Write-Host "If Codex does not switch immediately, restart Codex or select custom:chujian in Settings -> Appearance."
