@echo off
setlocal
chcp 65001 >nul 2>&1
cd /d "%~dp0"
echo.
echo === Publish Qqsp zh_CN package to GitHub Releases ===
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0publish-release.ps1" %*
set "rc=%ERRORLEVEL%"
echo.
echo [exit code: %rc%]
pause