@echo off
setlocal
chcp 65001 >nul 2>&1
cd /d "%~dp0"
echo.
echo === Push Qqsp zh_CN repo to GitHub ===
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0push-to-github.ps1" %*
set "rc=%ERRORLEVEL%"
echo.
echo [exit code: %rc%]
pause