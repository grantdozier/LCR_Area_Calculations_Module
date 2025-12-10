@echo off
echo Starting LCR Module A Frontend...
echo.

cd frontend

if not exist node_modules (
    echo ERROR: Node modules not found!
    echo Please run setup first:
    echo   cd frontend
    echo   npm install
    pause
    exit /b 1
)

echo Starting Vite development server...
echo Frontend will open at http://localhost:3000
echo Press Ctrl+C to stop
echo.

npm run dev

pause
