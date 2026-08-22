@echo off
echo =========================================
echo  MikaRoll Windows Build Script (Phase 3)
echo =========================================

echo 1. Installing requirements...
pip install -r requirements.txt

echo.
echo 2. Installing Playwright Chromium browser...
playwright install chromium

echo.
echo 3. Building executable...
REM We need to include playwright drivers and reportlab.
REM Playwright can be bundled if we tell PyInstaller to collect its data.

pyinstaller --noconsole --onefile ^
    --name MikaRoll ^
    --icon "image/icon.ico" ^
    --collect-data tkinterdnd2 ^
    --collect-data customtkinter ^
    --collect-data reportlab ^
    --collect-data playwright ^
    --hidden-import "playwright" ^
    --hidden-import "comtypes" ^
    --hidden-import "reportlab" ^
    --hidden-import "PyPDF2" ^
    main.py

echo.
echo Build complete! You can find MikaRoll.exe in the 'dist' folder.
echo (If you encounter any issues opening the .exe, run it from the command line to see the error output)
pause
