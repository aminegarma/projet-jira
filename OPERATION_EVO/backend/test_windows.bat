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
set FLASK_ENV=test
set DISABLE_EMAIL_WORKER=true
python -m compileall -q .
if errorlevel 1 (
  echo Echec de la verification syntaxique.
  pause
  exit /b 1
)
python -m unittest discover -s tests -p "test_*.py" -v
if errorlevel 1 (
  echo Au moins un test a echoue.
  pause
  exit /b 1
)
echo.
echo Toutes les verifications ont reussi.
pause
