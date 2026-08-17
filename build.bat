@echo off
echo Installing requirements...
pip install -r requirements.txt

echo.
echo Building executable...
REM --noconsole prevents the command prompt from appearing behind the GUI
REM --onefile creates a single executable
pyinstaller --noconsole --onefile --collect-data tkinterdnd2 --name UniversalConverter main.py

echo.
echo Build complete! You can find your .exe in the 'dist' folder.
pause
