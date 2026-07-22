@echo off
setlocal
cd /d "%~dp0"

set "PY_CMD="
py -3.12 --version >nul 2>&1 && set "PY_CMD=py -3.12"
if not defined PY_CMD py -3.11 --version >nul 2>&1 && set "PY_CMD=py -3.11"
if not defined PY_CMD py -3 --version >nul 2>&1 && set "PY_CMD=py -3"
if not defined PY_CMD python --version >nul 2>&1 && set "PY_CMD=python"

if not defined PY_CMD (
  echo Python est introuvable. Installez Python 3.11 ou 3.12 depuis python.org.
  pause
  exit /b 1
)

%PY_CMD% -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
if errorlevel 1 (
  echo Operation EVO necessite Python 3.11 ou une version plus recente.
  echo Version detectee :
  %PY_CMD% --version
  pause
  exit /b 1
)

echo [1/4] Python detecte :
%PY_CMD% --version

echo [2/4] Creation de l'environnement virtuel...
if not exist ".venv\Scripts\python.exe" %PY_CMD% -m venv .venv
if errorlevel 1 (
  echo Echec de la creation de l'environnement virtuel.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat

echo [3/4] Installation des dependances...
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
if errorlevel 1 (
  echo Echec de l'installation des dependances. Verifiez votre connexion Internet.
  pause
  exit /b 1
)

echo [4/4] Configuration locale...
if not exist ".env" copy ".env.example" ".env" >nul

echo.
echo Installation terminee. Lancez maintenant run_windows.bat
pause
