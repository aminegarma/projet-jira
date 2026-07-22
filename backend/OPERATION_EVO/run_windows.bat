@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Environnement absent. Lancez d'abord setup_windows.bat
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
cd backend
start "" http://127.0.0.1:5000/login
python app.py
pause
