Claude Usage Tray - README (English)
====================================
A small Windows 11 tray program that shows how much of your claude.ai quota
(Pro / Max) you have used and how much is left, and warns you before it runs out.

QUICK START
-----------
1. Unzip the package anywhere.
2. Double-click  START_HERE_Install.bat  (the language is chosen automatically).
   If Windows shows "Windows protected your PC", click "More info" -> "Run anyway".
3. A small window appears and an icon is added to the tray (bottom right; it may
   be hidden under the ^ arrow - drag it onto the taskbar to keep it visible).
4. Once, install the browser extension. The installer detects your default browser,
   opens its extensions page and copies the folder path to the clipboard.
   Follow the 3 steps printed in the black window (see "BROWSERS" below).
5. Sign in to claude.ai in that browser. Numbers appear within a minute.

HOW IT WORKS
------------
claude.ai has no public quota API. The extension reads the numbers that
Settings > Usage shows on the page (it never touches passwords or cookies) and
sends them only to this PC (http://127.0.0.1:47821). It works only while YOU have
that page open: it never opens pages, clicks anything or polls claude.ai by itself.
So the numbers update whenever you open Settings > Usage. Shortcuts: the
"Open usage page to update" button in the window, tray menu > Update now, or the
extension's toolbar button. Everything stays on your computer.

BROWSERS
--------
Chrome  : chrome://extensions -> turn on "Developer mode" (top right) ->
          "Load unpacked" -> paste the folder path (Ctrl+V) -> Select Folder.
Edge    : edge://extensions -> turn on "Developer mode" (left side) ->
          "Load unpacked" -> paste the path -> Select Folder.
Opera   : opera://extensions -> "Developer mode" -> "Load unpacked" -> paste path.
Brave   : brave://extensions -> "Developer mode" -> "Load unpacked" -> paste path.
Vivaldi : vivaldi://extensions -> "Developer mode" -> "Load unpacked" -> paste path.
Other Chromium browsers work the same way.
The folder is   %LOCALAPPDATA%\ClaudeUsageTray\extension
Do not delete or move it afterwards. Browsers may show a "disable developer mode
extensions" notice at start-up: just dismiss it.

FIREFOX
-------
Firefox only keeps add-ons that are signed by Mozilla, so there are 3 options.
The installer asks which one you want when Firefox is your default browser.
 1) Temporary (no account, 10 seconds): about:debugging#/runtime/this-firefox ->
    "Load Temporary Add-on..." -> pick  extension-firefox\manifest.json
    (path is on the clipboard). It is removed when Firefox closes and must be
    repeated every time Firefox starts.
 2) Permanent, free: sign up at addons.mozilla.org, then Developer Hub ->
    "Submit a New Add-on" -> "On your own" (unlisted) -> upload
    claude-usage-bridge-firefox.xpi. Mozilla signs it within minutes; download the
    signed .xpi and drag it into Firefox. Signed add-ons stay permanently.
 3) Firefox Developer Edition / Nightly / ESR: open about:config, set
    xpinstall.signatures.required to false, then install the .xpi from
    about:addons > gear icon > "Install Add-on From File...". Normal Firefox
    release cannot do this.
Easiest alternative: keep Firefox as it is and install the extension in Chrome or
Edge as well. It only needs to be installed in one browser.

USING IT
--------
* Left-click the tray icon: show / hide the small window.
* Right-click the tray icon: Update now, Display mode, Language, Start with
  Windows, Help, Uninstall, Quit.
* Display mode "auto" follows what you are doing (claude.ai in a browser vs
  Claude Code); "fixed" always shows claude.ai.
* Alerts pop up at 80%, 90% and 95% of the session or weekly limit.
* The tray icon shows the percent used and changes colour as it fills.

LANGUAGE
--------
The language follows Windows automatically. Change it in the tray menu >
Language. English, Traditional Chinese, Simplified Chinese, Japanese and Korean are
included. To add a language, copy lang\en.json, lang\en.cmd and docs\README.en.txt
to new names such as fr.json / fr.cmd / README.fr.txt, translate them, and restart.
It appears in the menu automatically. To force the installer language:
START_HERE_Install.bat ja

SETTINGS
--------
File: %USERPROFILE%\.claude_usage_tray\config.json  (created on first run)
  thresholds    alert levels, default [80, 90, 95]
  stale_minutes  after this many minutes the window reminds you to update, default 60
  language      "auto" or a code such as "en"
  browsers / code_apps  process names used to detect what you are using

UNINSTALL
---------
Any of these: tray menu > Uninstall...; or double-click UNINSTALL.bat; or run
%LOCALAPPDATA%\ClaudeUsageTray\uninstall.bat. It stops the program, removes
auto-start and all files, and opens your browser's extensions page so you can
click Remove on "Claude Usage Bridge". (Python and its packages are left alone;
remove them in Windows Settings > Apps if you want.)

UPDATING
--------
Unzip the new version and run START_HERE_Install.bat again. Reload the extension
in the browser's extensions page if the extension changed.

TROUBLESHOOTING
---------------
* Chrome / Edge 142 or newer show no data, or ask about "local network": open the
  extensions page -> Claude Usage Bridge -> Details -> Site settings ->
  "Local network access" -> Allow. (The program only talks to this PC.)
* "No data yet": check that the extension is enabled and you are signed in to
  claude.ai in that browser, then open Settings > Usage in it.
* Window does not appear: look under the ^ arrow in the tray.
* Python not found: install it from python.org (tick "Add python.exe to PATH") and
  run the installer again.
* Numbers wrong after a claude.ai redesign: the page text parser may need updating.

NOTES
-----
Unofficial tool, not affiliated with Anthropic. The percentages are exactly what
claude.ai shows; Anthropic does not publish absolute message counts.
