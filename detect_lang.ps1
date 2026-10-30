# Prints the language code to use (the name of a file in the lang folder), based on the Windows display language.
# Add a language by adding lang\<code>.cmd, lang\<code>.json and docs\README.<code>.txt (for example fr or pt-BR).
$ErrorActionPreference = 'SilentlyContinue'
$dir = Join-Path $PSScriptRoot 'lang'
$name = (Get-UICulture).Name
$cands = @()
if ($name -match '^zh') {
    if ($name -match '^zh-(TW|HK|MO)' -or $name -match 'Hant') { $cands += 'zh-TW' } else { $cands += 'zh-CN' }
} elseif ($name) {
    $cands += $name
    $cands += $name.Split('-')[0]
}
$code = 'en'
foreach ($c in $cands) {
    if ($c -and (Test-Path -LiteralPath (Join-Path $dir "$c.cmd"))) { $code = $c; break }
}
Write-Output $code
