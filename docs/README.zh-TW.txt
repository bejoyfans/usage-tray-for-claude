Claude 額度追蹤小幫手 - 說明檔（繁體中文）
==========================================
Windows 11 系統匣小程式：隨時顯示你 claude.ai（Pro / Max）額度用了多少、還剩多少，
快用完之前自動跳通知。

快速開始
--------
1. 把壓縮檔解壓縮到任何位置。
2. 連點兩下  START_HERE_Install.bat（語言會自動依系統選擇）。
   若出現「Windows 已保護您的電腦」，按「其他資訊」→「仍要執行」。
3. 螢幕會出現小視窗，系統匣（右下角，可能藏在 ^ 箭頭裡，拖出來即可常駐）出現圖示。
4. 第一次要安裝一次瀏覽器擴充功能。安裝程式會偵測你的預設瀏覽器，自動打開擴充功能頁面，
   並把資料夾路徑複製到剪貼簿。照黑色視窗裡的 3 個步驟做即可（見下方「各瀏覽器」）。
5. 在該瀏覽器登入 claude.ai，一分鐘內數字就會出現。

運作原理
--------
claude.ai 沒有公開的額度 API。擴充功能只讀取「設定 > 使用量」頁面上顯示的數字
（不碰密碼與 Cookie），並且只傳給本機 (http://127.0.0.1:47821)。它只在「你自己」打開
這個頁面時才讀取，絕不會自己開網頁、點按鈕或自動去抓 claude.ai 的資料。
所以每次你打開「設定 > 使用量」，數字就會更新。捷徑：視窗裡的「開啟使用量頁面來更新」
按鈕、系統匣選單 > 立即更新，或擴充功能的工具列按鈕。所有資料都留在你的電腦。

各瀏覽器
--------
Chrome  ：網址列輸入 chrome://extensions → 右上角開啟「開發人員模式」→
          「載入未封裝項目」→ 貼上路徑 (Ctrl+V) → 選擇資料夾。
Edge    ：edge://extensions → 左側開啟「開發人員模式」→「載入解壓縮」→ 貼上路徑 → 選擇資料夾。
Opera   ：opera://extensions →「開發人員模式」→「載入已解壓縮的擴充功能」→ 貼上路徑。
Brave   ：brave://extensions →「開發人員模式」→「載入未封裝項目」→ 貼上路徑。
Vivaldi ：vivaldi://extensions →「開發人員模式」→「載入未封裝項目」→ 貼上路徑。
其他 Chromium 系瀏覽器做法相同。
資料夾位置：%LOCALAPPDATA%\ClaudeUsageTray\extension
之後請勿刪除或搬移。瀏覽器啟動時若提示「停用開發人員模式擴充功能」，按關閉即可。

FIREFOX
-------
Firefox 只會永久保留經 Mozilla 簽署的附加元件，所以有 3 種做法；
預設瀏覽器是 Firefox 時，安裝程式會問你要哪一種。
 1) 暫時安裝（免帳號、10 秒）：about:debugging#/runtime/this-firefox →
    「載入暫時性附加元件…」→ 選 extension-firefox\manifest.json（路徑已在剪貼簿）。
    關閉 Firefox 就會消失，每次開 Firefox 都要重做。
 2) 永久安裝（免費）：到 addons.mozilla.org 註冊 → 開發者中心 →「提交新附加元件」→
    選「自行發布」(On your own / unlisted) → 上傳 claude-usage-bridge-firefox.xpi。
    Mozilla 幾分鐘內簽署完成，下載簽署後的 .xpi 拖進 Firefox 即可永久使用。
 3) Firefox Developer Edition / Nightly / ESR：開 about:config，把
    xpinstall.signatures.required 設為 false，再到 about:addons > 齒輪 >
    「從檔案安裝附加元件…」選 .xpi。一般版 Firefox 無法這樣做。
最省事的替代方案：Firefox 照用，另外在 Chrome 或 Edge 裝一次擴充功能就好
（只要有一個瀏覽器安裝即可）。

使用方式
--------
* 左鍵點系統匣圖示：顯示 / 隱藏小視窗。
* 右鍵點圖示：立即更新、顯示模式、語言、開機自動啟動、說明、移除、結束。
* 顯示模式「自動」會依你正在用的是瀏覽器的 claude.ai 或 Claude Code 切換；「固定」永遠顯示 claude.ai。
* 工作階段或每週額度到 80%、90%、95% 時會跳出通知。
* 系統匣圖示顯示已用百分比，越滿顏色越紅。

語言
----
語言會自動依 Windows 系統選擇，也可在系統匣選單 > 語言切換。內建英文、繁體中文、
簡體中文、日文、韓文。想新增語言：複製 lang\en.json、lang\en.cmd、docs\README.en.txt
並改名成 fr.json / fr.cmd / README.fr.txt 後翻譯，重新啟動即可，選單會自動列出。
強制安裝程式語言：START_HERE_Install.bat ja

設定
----
檔案：%USERPROFILE%\.claude_usage_tray\config.json（第一次執行後產生）
  thresholds    通知門檻，預設 [80, 90, 95]
  stale_minutes  超過幾分鐘沒更新就提醒你，預設 60
  language      "auto" 或語言代碼如 "zh-TW"
  browsers / code_apps  用來判斷你在使用什麼的程式名稱

移除
----
任選一種：系統匣選單 >「移除…」；或連點 UNINSTALL.bat；或執行
%LOCALAPPDATA%\ClaudeUsageTray\uninstall.bat。會停止程式、取消開機啟動、刪除所有檔案，
並打開瀏覽器擴充功能頁面讓你按「移除」Claude Usage Bridge。
（Python 與套件不會動；想移除請到 Windows 設定 > 應用程式。）

更新
----
解壓縮新版後再執行一次 START_HERE_Install.bat。若擴充功能有更新，到瀏覽器擴充功能頁面按重新載入。

疑難排解
--------
* Chrome / Edge 142 以後版本沒數字，或詢問「區域網路存取」：到擴充功能頁 →
  Claude Usage Bridge →「詳細資料」→「網站設定」→「區域網路存取」改為「允許」。
  （程式只連到你自己這台電腦。）
* 一直顯示「尚無資料」：確認擴充功能已啟用、該瀏覽器已登入 claude.ai，再按
  在該瀏覽器打開「設定 > 使用量」。
* 看不到視窗：到系統匣 ^ 箭頭裡找。
* 找不到 Python：到 python.org 安裝（勾選 Add python.exe to PATH）後重跑安裝程式。
* claude.ai 改版後數字不對：頁面解析可能需要更新。

注意
----
非官方工具，與 Anthropic 無關。百分比就是 claude.ai 頁面顯示的數字；Anthropic 並未公布確切訊息則數。
