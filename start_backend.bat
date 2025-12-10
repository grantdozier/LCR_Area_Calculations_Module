@echo off
echo Starting LCR Module A Backend...
echo.

cd backend

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup first:
    echo   cd backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

call venv\Scripts\activate
echo Virtual environment activated.
echo.

echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop
echo.

python main.py

pause
