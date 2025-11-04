@echo off
echo ====================================
echo Worker Stress Analysis - Web Server
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv311\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv311
    echo Then install dependencies: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv311\Scripts\activate.bat

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo ERROR: Flask not installed!
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Start the application
echo.
echo Starting Flask application...
echo.
echo Dashboard will be available at: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
