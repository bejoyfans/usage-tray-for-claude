# Detects the default browser and opens its extensions page (or, for Firefox, guides through the options).
#   -Mode install   copy the extension folder path to the clipboard and print the steps for that browser
#   -Mode remove    open the extensions page and tell the user to remove Claude Usage Bridge
# All texts come from lang\<code>.json ("ps" section).
param(
    [ValidateSet('install', 'remove')][string]$Mode = 'install',
    [string]$ExtPath = '',        # extension folder for Chrome-family browsers
    [string]$FirefoxPath = '',    # extension-firefox folder (contains manifest.json)
    [string]$FirefoxXpi = '',     # claude-usage-bridge-firefox.xpi
    [string]$Lang = 'en'
)

$ErrorActionPreference = 'SilentlyContinue'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

# ---------- texts ----------
function Load-Strings([string]$code) {
    $f = Join-Path $PSScriptRoot "lang\$code.json"
    if (Test-Path -LiteralPath $f) {
        return (Get-Content -LiteralPath $f -Raw -Encoding UTF8 | ConvertFrom-Json).ps
    }
    return $null
}
$S = Load-Strings $Lang
$E = Load-Strings 'en'
function T([string]$k, [hashtable]$a = @{}) {
    $v = $null
    if ($S -and $S.PSObject.Properties[$k]) { $v = $S.$k }
    if (-not $v -and $E -and $E.PSObject.Properties[$k]) { $v = $E.$k }
    if (-not $v) { return $k }
    foreach ($name in $a.Keys) { $v = $v.Replace('{' + $name + '}', [string]$a[$name]) }
    return $v
}

# ---------- browsers ----------
$Browsers = @{
    chrome  = @{ Name = 'Google Chrome';  Url = 'chrome://extensions';  Side = 'right'; Load = 'chrome' }
    edge    = @{ Name = 'Microsoft Edge'; Url = 'edge://extensions';    Side = 'left';  Load = 'edge' }
    opera   = @{ Name = 'Opera';          Url = 'opera://extensions';   Side = 'right'; Load = 'chrome' }
    brave   = @{ Name = 'Brave';          Url = 'brave://extensions';   Side = 'right'; Load = 'chrome' }
    vivaldi = @{ Name = 'Vivaldi';        Url = 'vivaldi://extensions'; Side = 'right'; Load = 'chrome' }
}

function Get-AppPath([string]$exe) {
    foreach ($root in 'HKLM:', 'HKCU:') {
        $p = (Get-ItemProperty -LiteralPath "$root\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\$exe").'(default)'
        if ($p) { return $p.Trim('"') }
    }
    return $null
}

function Get-ProgIdExe([string]$prog) {
    $cmd = (Get-ItemProperty -LiteralPath "Registry::HKEY_CLASSES_ROOT\$prog\shell\open\command").'(default)'
    if ($cmd -match '^\s*"([^"]+)"') { return $Matches[1] }
    if ($cmd -match '^\s*(\S+)') { return $Matches[1] }
    return $null
}

# 1. Windows default browser
$prog = (Get-ItemProperty -LiteralPath 'HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice').ProgId
$key = $null
switch -Wildcard ($prog) {
    'ChromeHTML*'  { $key = 'chrome' }
    'MSEdgeHTM*'   { $key = 'edge' }
    'BraveHTML*'   { $key = 'brave' }
    'Opera*'       { $key = 'opera' }
    'VivaldiHTM*'  { $key = 'vivaldi' }
    'FirefoxURL*'  { $key = 'firefox' }
}
$exe = $null
if ($key) { $exe = Get-ProgIdExe $prog }
$wasFirefox = ($key -eq 'firefox')

Write-Host ''

# 2. Firefox
if ($wasFirefox -and $exe -and (Test-Path -LiteralPath $exe)) {
    if ($Mode -eq 'remove') {
        Start-Process -FilePath $exe -ArgumentList 'about:addons'
        Write-Host (T 'ff_remove')
        Write-Host ''
        exit 0
    }
    Write-Host (T 'ff_detected') -ForegroundColor Green
    Write-Host (T 'ff_rule')
    Write-Host (T 'ff_opt1')
    Write-Host (T 'ff_opt2')
    Write-Host (T 'ff_opt3')
    $ans = Read-Host (T 'ff_prompt')
    $choice = 3
    if ($ans) {
        $a = $ans.Trim()
        if ($a -eq '1') { $choice = 1 } elseif ($a -eq '2') { $choice = 2 }
    }
    if ($choice -eq 1) {
        $manifest = Join-Path $FirefoxPath 'manifest.json'
        Set-Clipboard -Value $manifest
        Start-Process -FilePath $exe -ArgumentList 'about:debugging#/runtime/this-firefox'
        Write-Host ''
        Write-Host (T 'ff_temp1')
        Write-Host (T 'ff_temp2')
        Write-Host (T 'path_copied' @{ path = $manifest })
        Write-Host (T 'ff_temp3')
        Write-Host ''
        exit 0
    }
    if ($choice -eq 2) {
        Set-Clipboard -Value $FirefoxXpi
        Start-Process -FilePath $exe -ArgumentList 'https://addons.mozilla.org/developers/addon/submit/distribution'
        Write-Host ''
        Write-Host (T 'ff_perm1')
        Write-Host (T 'path_copied' @{ path = $FirefoxXpi })
        Write-Host (T 'ff_perm2')
        Write-Host (T 'ff_perm3')
        Write-Host (T 'ff_perm4')
        Write-Host ''
        exit 0
    }
    Write-Host (T 'ff_other')
    $exe = $null    # fall through to Chrome / Edge below
}

# 3. Chrome-family default browser, or fall back to an installed Chrome / Edge
if ($key -eq 'firefox' -or -not $exe -or -not (Test-Path -LiteralPath $exe)) {
    $key = $null
    $exe = $null
    foreach ($pair in @(@('chrome', 'chrome.exe'), @('edge', 'msedge.exe'))) {
        $p = Get-AppPath $pair[1]
        if ($p -and (Test-Path -LiteralPath $p)) { $key = $pair[0]; $exe = $p; break }
    }
}

if (-not $key -or -not $exe) {
    Write-Host (T 'no_browser') -ForegroundColor Yellow
    if ($Mode -eq 'install' -and $ExtPath) {
        Set-Clipboard -Value $ExtPath
        Write-Host (T 'path_only' @{ path = $ExtPath })
    }
    exit 0
}

$b = $Browsers[$key]
if ($wasFirefox) {
    Write-Host (T 'ff_fallback' @{ name = $b.Name }) -ForegroundColor Yellow
} else {
    Write-Host (T 'detected' @{ name = $b.Name }) -ForegroundColor Green
}

Start-Process -FilePath $exe -ArgumentList $b.Url

Write-Host ''
Write-Host ' ------------------------------------------------------------'
if ($Mode -eq 'install') {
    if ($ExtPath) { Set-Clipboard -Value $ExtPath }
    Write-Host (T 'install_title')
    Write-Host (T 'install_intro' @{ name = $b.Name })
    if ($b.Side -eq 'left') { Write-Host (T 'step_toggle_left') } else { Write-Host (T 'step_toggle_right') }
    if ($b.Load -eq 'edge') { Write-Host (T 'step_load_edge') } else { Write-Host (T 'step_load_chrome') }
    Write-Host (T 'step_path')
    Write-Host (T 'path_copied' @{ path = $ExtPath })
} else {
    Write-Host (T 'remove_msg' @{ name = $b.Name })
}
Write-Host ' ------------------------------------------------------------'
Write-Host ''
