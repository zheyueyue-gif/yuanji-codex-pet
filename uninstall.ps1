$ErrorActionPreference = "Stop"

$codexHome = Join-Path $env:USERPROFILE ".codex"
$petDir = Join-Path $codexHome "pets\chujian"
$configPath = Join-Path $codexHome "config.toml"

if (Test-Path -LiteralPath $petDir) {
  Remove-Item -LiteralPath $petDir -Recurse -Force
}

if (Test-Path -LiteralPath $configPath) {
  $text = [System.IO.File]::ReadAllText($configPath)
  $updated = [regex]::Replace($text, '(?m)^selected-avatar-id\s*=\s*"custom:chujian"\s*$', 'selected-avatar-id = "seedy"', 1)
  [System.IO.File]::WriteAllText($configPath, $updated, [System.Text.UTF8Encoding]::new($false))
}

Write-Host "Uninstalled Chujian Codex pet."
