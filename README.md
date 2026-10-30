# Usage Tray for Claude

**English** · [繁體中文](#繁體中文)

A small Windows 11 tray widget that shows how much of your **claude.ai** usage (Pro / Max) you have used and how much is left, and warns you before you run out.

> **Unofficial.** This is an independent, community project. It is not made, endorsed or supported by Anthropic. "Claude" is a trademark of Anthropic.

## Features

- Tray icon with your current usage % (green / orange / red)
- Small always-on-top window: current session, weekly limit, per-product usage, reset countdowns
- Desktop alerts at 80 / 90 / 95 % (configurable), and when claude.ai warns you'll run out early
- Follows what you are using: claude.ai in a browser vs. Claude Code in a terminal / editor
- Works with Chrome, Edge, Opera, Brave, Vivaldi and Firefox
- English, 繁體中文, 简体中文, 日本語, 한국어 — picked automatically from your Windows language
- One-click install and uninstall, no admin rights needed

## How it works (and privacy)

claude.ai has no public usage API. The small browser extension reads the numbers that **Settings → Usage** shows **while you have that page open**, and sends them only to the tray program on your own PC (`127.0.0.1:47821`).

- It **never** opens pages, clicks anything or polls claude.ai by itself — numbers update when *you* open the usage page (the window has a button for that).
- It never reads passwords, cookies or your conversations.
- Nothing is sent anywhere else. No analytics, no accounts.
- The extension asks for no special permissions besides access to `claude.ai` and `127.0.0.1:47821`.

## Install

1. **[Download the ZIP](https://github.com/bejoyfans/usage-tray-for-claude/archive/refs/heads/main.zip)** and extract it (right-click → *Extract All*).
2. Double-click **`START_HERE_Install.bat`**. If Windows shows *"Windows protected your PC"*, click *More info → Run anyway*.
   Python is installed automatically if it is missing.
3. The installer opens your default browser's extensions page and copies the folder path — follow the 3 steps it prints.
4. Open claude.ai → Settings → Usage. The numbers appear in the tray.

Full guides per language: [`docs/`](docs) ([EN](docs/README.en.txt) · [繁中](docs/README.zh-TW.txt) · [简中](docs/README.zh-CN.txt) · [日本語](docs/README.ja.txt) · [한국어](docs/README.ko.txt)).

**Firefox:** unsigned add-ons can only be loaded temporarily. The installer offers a temporary install, instructions to self-sign for free on addons.mozilla.org, or using Edge/Chrome instead. See the docs.

**Chrome / Edge 142+:** if no numbers arrive, allow *Local network access* for the extension (Extensions → Details → Site settings).

## Uninstall

Tray menu → *Uninstall…*, or double-click `UNINSTALL.bat`. Then remove the extension from your browser (the uninstaller opens the page for you).

## Add a language

Copy `lang/en.json`, `lang/en.cmd` and `docs/README.en.txt` to your language code (e.g. `fr`), translate, and send a pull request. New languages show up in the tray menu automatically.

## Limitations

- Depends on the text layout of the claude.ai usage page; a redesign may break it until updated.
- Japanese / Korean page parsing is best-effort — please open an issue with a screenshot if it fails.
- Windows only (the tray program). Built with Python, pystray and Pillow.

## Support

This tool is free and always will be. If it helps you, you can buy me a coffee — it keeps the project updated when claude.ai changes.

[![Support me on Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20me-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/bejoyfans)

## License

[MIT](LICENSE)

---

## 繁體中文

Windows 11 系統匣小工具：隨時顯示你 **claude.ai**（Pro / Max）的額度用了多少、還剩多少，快用完前自動通知。

> **非官方工具。** 這是獨立的社群專案，並非 Anthropic 製作、認可或支援。「Claude」是 Anthropic 的商標。

### 功能

- 系統匣圖示直接顯示用量百分比（綠 / 橘 / 紅）
- 置頂小視窗：目前工作階段、每週額度、各產品用量、重設倒數
- 用量到 80 / 90 / 95%（可自訂）或 claude.ai 提示可能提早用完時跳出通知
- 自動切換：瀏覽器的 claude.ai 或終端機 / 編輯器的 Claude Code
- 支援 Chrome、Edge、Opera、Brave、Vivaldi、Firefox
- 英文、繁中、簡中、日文、韓文，依 Windows 語言自動切換
- 一鍵安裝、一鍵移除，不需要系統管理員權限

### 運作方式與隱私

claude.ai 沒有公開的用量 API。瀏覽器擴充功能只在**你自己打開**「設定 → 使用量」頁面時，讀取頁面上顯示的數字，並且只傳給你電腦上的小程式（`127.0.0.1:47821`）。

- **絕不會**自己開網頁、點按鈕或自動抓 claude.ai 的資料；你打開使用量頁面時數字才會更新（視窗裡有按鈕可一鍵打開）。
- 不讀取密碼、Cookie 或你的對話內容。
- 資料不會傳到任何其他地方，沒有追蹤、不需要帳號。

### 安裝

1. **[下載 ZIP](https://github.com/bejoyfans/usage-tray-for-claude/archive/refs/heads/main.zip)** 並解壓縮（右鍵 →「全部解壓縮」）。
2. 連點兩下 **`START_HERE_Install.bat`**。若出現「Windows 已保護您的電腦」，按「其他資訊」→「仍要執行」。沒有 Python 會自動安裝。
3. 安裝程式會打開你預設瀏覽器的擴充功能頁面並複製資料夾路徑，照畫面上的 3 個步驟做即可。
4. 打開 claude.ai →「設定」→「使用量」，數字就會出現在系統匣。

詳細說明見 [`docs/README.zh-TW.txt`](docs/README.zh-TW.txt)。

### 移除

系統匣選單 →「移除…」，或連點 `UNINSTALL.bat`，再到瀏覽器移除擴充功能（移除程式會幫你打開那個頁面）。

### 贊助

這個工具永久免費。如果它對你有幫助，歡迎請我喝杯咖啡，讓我能在 claude.ai 改版時持續更新。

- 國外使用者：[Ko-fi（PayPal）](https://ko-fi.com/bejoyfans)

### 授權

[MIT](LICENSE)
