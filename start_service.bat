@echo off
echo 🚀 LeetCode Enforcer Bot - Service Installer
echo ============================================
echo.
echo This will install and start the LeetCode Enforcer Bot as a Windows service.
echo The service will run automatically in the background and cannot be manually stopped.
echo.
echo Scheduled checks:
echo - Morning: 9:00 AM
echo - Midday: 12:00 PM  
echo - Evening: 6:00 PM
echo.
echo Press any key to continue...
pause >nul

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo.
echo Installing Windows service...
python leetcoder_service.py install

echo.
echo Starting service...
python leetcoder_service.py start

echo.
echo ✅ Service installed and started successfully!
echo.
echo The LeetCode Enforcer Bot is now running in the background.
echo It will automatically:
echo - Check your progress at 9 AM, 12 PM, and 6 PM
echo - Block distractions when you're behind on goals
echo - Open the next Blind 75 problem to solve
echo - Unblock distractions when you meet your daily goal
echo.
echo To view service logs: C:\leetcoder_service.log
echo To stop service (admin required): python leetcoder_service.py stop
echo To uninstall service (admin required): python leetcoder_service.py uninstall
echo.
echo Press any key to exit...
pause >nul 