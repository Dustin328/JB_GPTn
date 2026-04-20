@echo off
echo ================================================
echo JailbrokeGPT Quick Start Guide
echo ================================================
echo.
echo This script will help you set up JailbrokeGPT
echo.
echo Prerequisites:
echo - MySQL installed and running
echo - Python 3.9+ installed
echo - Node.js 18+ installed
echo.
pause

:menu
cls
echo ================================================
echo JailbrokeGPT Setup Menu
echo ================================================
echo.
echo 1. Setup Backend (first time only)
echo 2. Start Backend Server
echo 3. Setup Frontend (first time only)
echo 4. Start Frontend Server
echo 5. Initialize Database
echo 6. Exit
echo.
set /p choice=Enter your choice (1-6): 

if "%choice%"=="1" goto setup_backend
if "%choice%"=="2" goto start_backend
if "%choice%"=="3" goto setup_frontend
if "%choice%"=="4" goto start_frontend
if "%choice%"=="5" goto init_database
if "%choice%"=="6" goto end
goto menu

:setup_backend
echo.
echo ================================================
echo Setting up Backend...
echo ================================================
cd backend
echo Creating virtual environment...
python -m venv venv
echo Installing dependencies (this may take 10-15 minutes)...
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo.
echo Backend setup complete!
echo.
echo Next steps:
echo 1. Edit backend\.env with your MySQL credentials
echo 2. Run option 5 to initialize database
echo 3. Run option 2 to start backend server
echo.
pause
goto menu

:start_backend
echo.
echo ================================================
echo Starting Backend Server...
echo ================================================
cd backend
call venv\Scripts\activate.bat
python app.py
pause
goto menu

:setup_frontend
echo.
echo ================================================
echo Setting up Frontend...
echo ================================================
cd frontend
echo Installing Node dependencies...
npm install
echo.
echo Frontend setup complete!
echo Run option 4 to start the frontend server.
echo.
pause
goto menu

:start_frontend
echo.
echo ================================================
echo Starting Frontend Server...
echo ================================================
cd frontend
npm run dev
pause
goto menu

:init_database
echo.
echo ================================================
echo Initializing Database...
echo ================================================
echo Make sure MySQL is running!
echo.
cd backend
call venv\Scripts\activate.bat
python init_db.py
echo.
pause
goto menu

:end
echo.
echo Goodbye!
exit
