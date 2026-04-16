@echo off
echo ========================================
echo  FedSecure - Privacy-Preserving IDS
echo  Setup Script (Windows)
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/5] Installing dependencies...
pip install -r requirements.txt

echo [3/5] Running database migrations...
python manage.py migrate

echo [4/5] Seeding demo data...
python manage.py seed_data

echo [5/5] Starting server...
echo.
echo ========================================
echo  FedSecure is running!
echo  Open: http://127.0.0.1:8000/
echo  Admin: admin / admin123
echo  Analyst: analyst / analyst123
echo ========================================
echo.
python manage.py runserver
pause
