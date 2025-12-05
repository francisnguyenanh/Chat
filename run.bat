@echo off
echo ========================================
echo       Chat App - Starting Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install requirements
if not exist "venv\Lib\site-packages\flask\" (
    echo Installing requirements...
    pip install -r requirements.txt
    echo.
)

REM Initialize database if not exists
if not exist "chat.db" (
    echo Initializing database...
    python init_db.py
    echo.
)

REM Run the application
echo Starting Chat App...
echo.
echo ========================================
echo   Server running at http://localhost:5000
echo   Press Ctrl+C to stop
echo ========================================
echo.
python app.py

pause
