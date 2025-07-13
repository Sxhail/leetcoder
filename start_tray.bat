@echo off
echo 🚀 LeetCode Enforcer Bot - Tray UI Launcher
echo ===========================================
echo.
echo This will start the system tray interface for manual actions.
echo The service should already be running in the background.
echo.
echo Press any key to continue...
pause >nul

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo.
echo Starting system tray UI...
python tray_ui.py

echo.
echo Tray UI has stopped.
echo Press any key to exit...
pause >nul 