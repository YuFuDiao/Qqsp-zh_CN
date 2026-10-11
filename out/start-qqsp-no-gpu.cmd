@echo off
rem Launcher for Qqsp with GPU acceleration disabled (fix for freeze after ~1h play).
rem If still freezing, change the flag below to: --disable-gpu-compositing
set "QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu"
start "" "%~dp0Qqsp.exe" %*
