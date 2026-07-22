@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Environnement absent. Lancez d'abord setup_windows.bat
  pause
  exit /b 1
)

echo Reparation des comptes de demonstration...
".venv\Scripts\python.exe" -c "import sys; sys.path.insert(0, 'backend'); from database.db import init_db; init_db(force=False); print('Comptes repares avec succes.')"
if errorlevel 1 (
  echo La reparation a echoue.
  pause
  exit /b 1
)

echo.
echo Vous pouvez maintenant lancer run_windows.bat
pause
