Claude 额度追踪小助手 - 说明文件（简体中文）
==========================================
Windows 11 系统托盘小程序：随时显示你 claude.ai（Pro / Max）额度用了多少、还剩多少，
快用完之前自动弹出通知。

快速开始
--------
1. 把压缩包解压到任意位置。
2. 双击  START_HERE_Install.bat（语言会按系统自动选择）。
   若出现“Windows 已保护你的电脑”，点“更多信息”→“仍要运行”。
3. 屏幕出现小窗口，系统托盘（右下角，可能藏在 ^ 箭头里，拖出来即可常驻）出现图标。
4. 第一次需要安装一次浏览器扩展。安装程序会检测默认浏览器，自动打开扩展页面，
   并把文件夹路径复制到剪贴板。按黑色窗口里的 3 个步骤操作即可（见下方“各浏览器”）。
5. 在该浏览器登录 claude.ai，一分钟内数字就会出现。

工作原理
--------
claude.ai 没有公开的额度 API。扩展只读取“设置 > 使用情况”页面上显示的数字
（不接触密码和 Cookie），并且只发送到本机 (http://127.0.0.1:47821)。它只在“你自己”打开
这个页面时才读取，绝不会自己打开网页、点击按钮或自动抓取 claude.ai 的数据。
所以每次你打开“设置 > 使用情况”，数字就会更新。快捷方式：窗口里的“打开使用量页面来更新”
按钮、托盘菜单 > 立即更新，或扩展的工具栏按钮。所有数据都保留在你的电脑上。

各浏览器
--------
Chrome  ：地址栏输入 chrome://extensions → 右上角打开“开发者模式”→
          “加载已解压的扩展程序”→ 粘贴路径 (Ctrl+V) → 选择文件夹。
Edge    ：edge://extensions → 左侧打开“开发人员模式”→“加载解压缩的扩展”→ 粘贴路径 → 选择文件夹。
Opera   ：opera://extensions →“开发者模式”→“加载已解压的扩展程序”→ 粘贴路径。
Brave   ：brave://extensions →“开发者模式”→“加载已解压的扩展程序”→ 粘贴路径。
Vivaldi ：vivaldi://extensions →“开发者模式”→“加载已解压的扩展程序”→ 粘贴路径。
其他 Chromium 内核浏览器做法相同。
文件夹位置：%LOCALAPPDATA%\ClaudeUsageTray\extension
之后请勿删除或移动。浏览器启动时若提示“停用开发者模式的扩展”，关闭提示即可。

FIREFOX
-------
Firefox 只会永久保留经 Mozilla 签名的附加组件，所以有 3 种做法；
默认浏览器是 Firefox 时，安装程序会询问你选哪一种。
 1) 临时安装（无需账号、10 秒）：about:debugging#/runtime/this-firefox →
    “临时载入附加组件…”→ 选 extension-firefox\manifest.json（路径已在剪贴板）。
    关闭 Firefox 就会消失，每次启动 Firefox 都要重做。
 2) 永久安装（免费）：到 addons.mozilla.org 注册 → 开发者中心 →“提交新附加组件”→
    选“自行分发”(On your own / unlisted) → 上传 claude-usage-bridge-firefox.xpi。
    Mozilla 几分钟内签名完成，下载签名后的 .xpi 拖进 Firefox 即可永久使用。
 3) Firefox Developer Edition / Nightly / ESR：打开 about:config，把
    xpinstall.signatures.required 设为 false，再到 about:addons > 齿轮 >
    “从文件安装附加组件…”选 .xpi。普通版 Firefox 无法这样做。
最省事的替代方案：Firefox 照常使用，另外在 Chrome 或 Edge 装一次扩展即可
（只要有一个浏览器安装就行）。

使用方法
--------
* 左键点托盘图标：显示 / 隐藏小窗口。
* 右键点图标：立即更新、显示模式、语言、开机自启、帮助、卸载、退出。
* 显示模式“自动”会根据你正在用浏览器的 claude.ai 还是 Claude Code 切换；“固定”始终显示 claude.ai。
* 会话或每周额度达到 80%、90%、95% 时会弹出通知。
* 托盘图标显示已用百分比，越满颜色越红。

语言
----
语言会按 Windows 系统自动选择，也可在托盘菜单 > 语言切换。内置英文、繁体中文、
简体中文、日文、韩文。想添加语言：复制 lang\en.json、lang\en.cmd、docs\README.en.txt
并改名为 fr.json / fr.cmd / README.fr.txt 后翻译，重新启动即可，菜单会自动列出。
强制安装程序语言：START_HERE_Install.bat ja

设置
----
文件：%USERPROFILE%\.claude_usage_tray\config.json（首次运行后生成）
  thresholds    通知阈值，默认 [80, 90, 95]
  stale_minutes  超过多少分钟没更新就提醒你，默认 60
  language      "auto" 或语言代码如 "zh-CN"
  browsers / code_apps  用来判断你在使用什么的进程名

卸载
----
任选一种：托盘菜单 >“卸载…”；或双击 UNINSTALL.bat；或运行
%LOCALAPPDATA%\ClaudeUsageTray\uninstall.bat。会停止程序、取消开机自启、删除所有文件，
并打开浏览器扩展页面，让你点“移除”Claude Usage Bridge。
（Python 与依赖包不会改动；想卸载请到 Windows 设置 > 应用。）

更新
----
解压新版后再运行一次 START_HERE_Install.bat。若扩展有更新，到浏览器扩展页面点重新加载。

常见问题
--------
* Chrome / Edge 142 及以后版本没有数字，或询问“本地网络访问”：到扩展页面 →
  Claude Usage Bridge →“详情”→“网站设置”→“本地网络访问”改为“允许”。
  （程序只连接你自己这台电脑。）
* 一直显示“暂无数据”：确认扩展已启用、该浏览器已登录 claude.ai，再点
  在该浏览器打开“设置 > 使用情况”。
* 看不到窗口：到托盘 ^ 箭头里找。
* 找不到 Python：到 python.org 安装（勾选 Add python.exe to PATH）后重新运行安装程序。
* claude.ai 改版后数字不对：页面解析可能需要更新。

说明
----
非官方工具，与 Anthropic 无关。百分比即 claude.ai 页面显示的数字；Anthropic 并未公布确切消息条数。
