@echo off
setlocal
chcp 65001 >nul 2>&1
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $d=$MyInvocation.MyCommand.Path; if ([string]::IsNullOrEmpty($d)) { $d=(Get-Location).Path } else { $d=Split-Path -Parent $d }; $p=(Get-ChildItem -LiteralPath $d -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like '*GitHub.ps1' } | Sort-Object Length -Descending | Select-Object -First 1); if (-not $p) { Write-Host '[x] cannot find *GitHub.ps1 next to this .cmd file' -ForegroundColor Red; Start-Sleep 5; exit 2 }; & $p.FullName @args" -- %*
set "rc=%ERRORLEVEL%"
echo.
echo [exit code: %rc%]
pause
