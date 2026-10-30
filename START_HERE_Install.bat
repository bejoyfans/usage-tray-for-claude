@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
if not exist "%~dp0lang\en.cmd" goto :notextracted
if not exist "%~dp0claude_usage_tray.py" goto :notextracted

set "DEST=%LOCALAPPDATA%\ClaudeUsageTray"
set "STATE=%USERPROFILE%\.claude_usage_tray"

rem ---------- language: automatic, or force it with  START_HERE_Install.bat ja ----------
set "LANGID=%~1"
if defined LANGID goto :haslang
for /f "delims=" %%L in ('powershell -NoProfile -ExecutionPolicy Bypass -File detect_lang.ps1') do set "LANGID=%%L"
:haslang
if not defined LANGID set "LANGID=en"
if not exist "lang\%LANGID%.cmd" set "LANGID=en"
call "lang\%LANGID%.cmd"
title %M_TITLE%

echo.
echo %M_HEAD%
echo.

rem ---------- 1. find Python 3.9+ ----------
set "PY="
call :findpy py
if not defined PY call :findpy python
if not defined PY goto :installpy
goto :havepy

:findpy
%1 -c "import sys;sys.exit(0 if sys.version_info>=(3,9) else 1)" >nul 2>&1
if not errorlevel 1 set "PY=%1"
exit /b

:installpy
echo %M_PYINST%
winget install -e --id Python.Python.3.12 --scope user --silent --accept-package-agreements --accept-source-agreements
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PY goto :nopy
goto :havepy

:nopy
echo.
echo %M_NOPY1%
echo %M_NOPY2%
echo %M_NOPY3%
echo.
pause
exit /b 1

:havepy
"%PY%" -c "import sys;print(sys.executable)" > "%TEMP%\cu_py.txt"
set /p PYEXE=<"%TEMP%\cu_py.txt"
del "%TEMP%\cu_py.txt" >nul 2>&1
set "PYW=%PYEXE:python.exe=pythonw.exe%"
if not exist "%PYW%" set "PYW=%PYEXE%"
echo %M_PYOK%

rem ---------- 2. packages ----------
echo %M_PIP%
"%PYEXE%" -m pip install --disable-pip-version-check -q pystray pillow
if errorlevel 1 goto :piperr

rem ---------- 3. copy everything to a permanent place ----------
echo %M_COPY%
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*claude_usage_tray.py*' -and $_.ProcessId -ne $PID } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>&1
if not exist "%DEST%" mkdir "%DEST%"
copy /y "%~dp0claude_usage_tray.py" "%DEST%\claude_usage_tray.py" >nul
xcopy /e /i /y /q "%~dp0extension" "%DEST%\extension" >nul
xcopy /e /i /y /q "%~dp0extension-firefox" "%DEST%\extension-firefox" >nul
copy /y "%~dp0claude-usage-bridge-firefox.xpi" "%DEST%\claude-usage-bridge-firefox.xpi" >nul
xcopy /e /i /y /q "%~dp0lang" "%DEST%\lang" >nul
xcopy /e /i /y /q "%~dp0docs" "%DEST%\docs" >nul
copy /y "%~dp0open_extensions.ps1" "%DEST%\open_extensions.ps1" >nul
copy /y "%~dp0detect_lang.ps1" "%DEST%\detect_lang.ps1" >nul
copy /y "%~dp0UNINSTALL.bat" "%DEST%\uninstall.bat" >nul
copy /y "%~dp0docs\README.en.txt" "%DEST%\README.txt" >nul
if exist "%~dp0docs\README.%LANGID%.txt" copy /y "%~dp0docs\README.%LANGID%.txt" "%DEST%\README.txt" >nul

rem start with Windows
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v ClaudeUsageTray /t REG_SZ /d "\"%PYW%\" \"%DEST%\claude_usage_tray.py\"" /f >nul

rem ---------- 4. launch ----------
echo %M_LAUNCH%
start "" "%PYW%" "%DEST%\claude_usage_tray.py" --show

if exist "%STATE%\ext_done.txt" goto :done

rem ---------- first time only: browser extension ----------
if not exist "%STATE%" mkdir "%STATE%"
powershell -NoProfile -ExecutionPolicy Bypass -File "%DEST%\open_extensions.ps1" -Mode install -ExtPath "%DEST%\extension" -FirefoxPath "%DEST%\extension-firefox" -FirefoxXpi "%DEST%\claude-usage-bridge-firefox.xpi" -Lang %LANGID%
echo %M_EXTWAIT%
echo.
pause
echo done> "%STATE%\ext_done.txt"

:done
echo.
echo %M_DONE1%
echo %M_DONE2%
echo %M_DONE3%
echo %M_README% %DEST%\README.txt
timeout /t 8 >nul
exit /b 0

:piperr
echo.
echo %M_PIPERR%
echo.
pause
exit /b 1

:notextracted
echo.
echo  Please extract - unzip - the whole ZIP first, then run this file from the extracted folder.
echo  請先把整個壓縮檔解壓縮，再從解壓縮後的資料夾執行這個檔案。
echo  请先把整个压缩包解压，再从解压后的文件夹运行这个文件。
echo  先に ZIP をすべて展開し、展開したフォルダーからこのファイルを実行してください。
echo  먼저 ZIP 전체를 압축 해제한 뒤, 압축을 푼 폴더에서 이 파일을 실행하세요.
echo.
pause
exit /b 1
