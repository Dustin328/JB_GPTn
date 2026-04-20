@echo off
setlocal

REM Build script for creating a Windows .exe of JailbrokeGPT backend + embedded frontend

cd /d "%~dp0"

if not exist "..\frontend\package.json" (
  echo [ERROR] Could not find frontend folder relative to backend.
  exit /b 1
)

if not exist "venv\Scripts\python.exe" (
  echo [ERROR] Python virtual environment not found at backend\venv.
  echo Create it first: python -m venv venv
  exit /b 1
)

echo [1/4] Building frontend into backend\frontend_dist ...
cd /d "..\frontend"
call npm install || exit /b 1
call npm run build:backend || exit /b 1

echo [2/4] Installing PyInstaller ...
cd /d "..\backend"
call venv\Scripts\activate.bat
python -m pip install --upgrade pip || exit /b 1
python -m pip install pyinstaller || exit /b 1

echo [3/4] Building EXE ...
pyinstaller --clean --onefile --name JailbrokeGPTBackend --add-data "frontend_dist;frontend_dist" app.py || exit /b 1

echo [4/4] Done.
echo EXE created at: backend\dist\JailbrokeGPTBackend.exe

echo.
echo Notes:
echo - Copy backend\.env next to the EXE before running.
echo - MySQL must be installed/running on the target machine.
echo - First launch can take time while model files are downloaded.

endlocal
