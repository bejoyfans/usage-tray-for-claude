@echo off
chcp 65001 >nul
setlocal EnableExtensions

set "DEST=%LOCALAPPDATA%\ClaudeUsageTray"
set "STATE=%USERPROFILE%\.claude_usage_tray"

rem If run from the install folder, copy to TEMP first so that the folder can be deleted.
if /i "%~dp0"=="%DEST%\" goto :relaunch
goto :start

:relaunch
set "TMPD=%TEMP%\cu_uninstall"
if exist "%TMPD%" rd /s /q "%TMPD%"
mkdir "%TMPD%"
copy /y "%~f0" "%TMPD%\UNINSTALL.bat" >nul
copy /y "%~dp0open_extensions.ps1" "%TMPD%\open_extensions.ps1" >nul
copy /y "%~dp0detect_lang.ps1" "%TMPD%\detect_lang.ps1" >nul
xcopy /e /i /y /q "%~dp0lang" "%TMPD%\lang" >nul
start "" "%TMPD%\UNINSTALL.bat"
exit /b

:start
cd /d "%~dp0"
if not exist "%~dp0lang\en.cmd" goto :notextracted
set "LANGID=%~1"
if defined LANGID goto :haslang
for /f "delims=" %%L in ('powershell -NoProfile -ExecutionPolicy Bypass -File detect_lang.ps1') do set "LANGID=%%L"
:haslang
if not defined LANGID set "LANGID=en"
if not exist "lang\%LANGID%.cmd" set "LANGID=en"
call "lang\%LANGID%.cmd"
title %U_TITLE%

echo.
echo %U_HEAD%
echo.
echo %U_INFO1%
echo %U_INFO2%
echo.
choice /c YN /n /m "%U_ASK%"
if errorlevel 2 goto :cancel

echo.
echo %U_S1%
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*claude_usage_tray.py*' -and $_.ProcessId -ne $PID } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>&1
timeout /t 2 >nul

echo %U_S2%
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v ClaudeUsageTray /f >nul 2>&1

echo %U_S3%
if exist "%DEST%" rd /s /q "%DEST%"
if exist "%STATE%" rd /s /q "%STATE%"

echo.
echo %U_EXT%
powershell -NoProfile -ExecutionPolicy Bypass -File open_extensions.ps1 -Mode remove -Lang %LANGID%

echo.
echo %U_PIP1%
echo %U_PIP2%
echo.
pause
exit /b 0

:cancel
echo.
echo %U_CANCEL%
timeout /t 3 >nul
exit /b 0

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
