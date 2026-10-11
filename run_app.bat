@echo off
title Chemical Inventory Management System (CIMS)
echo Starting Chemical Inventory Management System...

:: Check if virtual environment exists
if exist .venv\Scripts\python.exe (
    start "" ".venv\Scripts\pythonw.exe" app.py
) else (
    python app.py
)
exit
