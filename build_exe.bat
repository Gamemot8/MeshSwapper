@echo off
setlocal
cd /d "%~dp0"
title MeshSwapper - EXE bauen

if not exist "meshswapper.pyw" (
    echo meshswapper.pyw liegt nicht neben dieser Datei.
    echo Lege build_exe.bat, meshswapper.pyw und meshswapper.ico in denselben Ordner.
    pause
    exit /b 1
)
if not exist "meshswapper.ico" (
    echo meshswapper.ico fehlt. Lege sie neben diese Datei.
    pause
    exit /b 1
)

set "BROKEN=0"

rem --- 1) Vorhandenes Python (py-Launcher) nutzen, aber nur wenn es wirklich funktioniert ---
set "PY=py -3.9"
%PY% -c "import encodings, tkinter, ensurepip" >nul 2>&1
if not errorlevel 1 goto have_python
set "PY=py"
%PY% -c "import encodings, tkinter, ensurepip" >nul 2>&1
if not errorlevel 1 goto have_python

rem --- 2) Von diesem Skript frueher installiertes Python pruefen ---
set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
if not exist "%PYEXE%" goto need_install
"%PYEXE%" -c "import encodings, tkinter, ensurepip" >nul 2>&1
if not errorlevel 1 goto use_local
echo Eine fruehere Python-Installation ist kaputt/unvollstaendig und wird repariert ...
set "BROKEN=1"

:need_install
echo ============================================================
echo  Python wird jetzt automatisch geholt und installiert
echo ============================================================
rem Haengende Python-Installer von frueheren Versuchen beenden (sie sperren sonst Datei und Installation)
taskkill /f /im python-3.9.13-amd64.exe >nul 2>&1
taskkill /f /im python-setup-*.exe >nul 2>&1
timeout /t 2 /nobreak >nul
set "PYSETUP=%TEMP%\python-setup-%RANDOM%.exe"
set "PYURL=https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe"
del "%TEMP%\python-3.9.13-amd64.exe" >nul 2>&1

echo.
echo [Download 1/2] Mit curl ...
curl.exe -L -f --retry 3 --progress-bar -o "%PYSETUP%" "%PYURL%"
if errorlevel 1 del "%PYSETUP%" >nul 2>&1
call :check_setup
if "%SETUP_OK%"=="1" goto do_install

echo.
echo [Download 2/2] Mit PowerShell ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest '%PYURL%' -OutFile '%PYSETUP%'"
if errorlevel 1 del "%PYSETUP%" >nul 2>&1
call :check_setup
if "%SETUP_OK%"=="1" goto do_install

echo.
echo Direkt-Download klappt nicht. Versuche winget ...
winget install -e --id Python.Python.3.9 --scope user --silent --accept-package-agreements --accept-source-agreements
goto verify_install

:do_install
if "%BROKEN%"=="1" (
    echo Entferne kaputte Python-Installation ...
    start /wait "" "%PYSETUP%" /uninstall /quiet
    rmdir /s /q "%LOCALAPPDATA%\Programs\Python\Python39" >nul 2>&1
)
echo.
echo Installiere Python 3.9 - ein Fenster mit Balken erscheint, du musst nichts anklicken.
echo Bitte warten, bis es von selbst weitergeht (ca. 1-3 Minuten) ...
start /wait "" "%PYSETUP%" /passive InstallAllUsers=0 PrependPath=1 Include_launcher=0 Include_test=0 Include_doc=0 Shortcuts=0
del "%PYSETUP%" >nul 2>&1

:verify_install
if not exist "%PYEXE%" goto install_failed
"%PYEXE%" -c "import encodings, tkinter, ensurepip" >nul 2>&1
if errorlevel 1 goto install_failed
goto use_local

:install_failed
echo.
echo Die automatische Python-Installation hat nicht geklappt.
echo Bitte installiere Python 3.9 einmal von Hand: https://www.python.org/downloads/release/python-3913/
echo ^(Haken bei "Add python.exe to PATH"^) und starte diese Datei danach nochmal.
goto failed

:use_local
set PY="%PYEXE%"

:have_python
echo.
echo Benutze:
%PY% --version
echo.
echo [1/3] Installiere numpy und pyinstaller (nur beim ersten Mal lange) ...
%PY% -m pip install numpy pyinstaller
if errorlevel 1 goto failed

echo.
echo [2/3] Baue MeshSwapper.exe (das dauert ein paar Minuten) ...
%PY% -m PyInstaller --noconfirm --clean --onedir --noupx --windowed --icon "meshswapper.ico" --name MeshSwapper meshswapper.pyw
if errorlevel 1 goto failed

echo.
echo [3/3] Kopiere das Programm in diesen Ordner ...
if exist "%~dp0MeshSwapper" rmdir /s /q "%~dp0MeshSwapper"
xcopy /e /i /y /q "dist\MeshSwapper" "%~dp0MeshSwapper" >nul
if errorlevel 1 goto failed

echo.
echo Fertig! Der Ordner "MeshSwapper" liegt jetzt neben dieser Datei.
echo Starte das Programm mit MeshSwapper\MeshSwapper.exe (Doppelklick, kein Konsolenfenster).
echo Du kannst den ganzen Ordner "MeshSwapper" verschieben, aber nicht die EXE allein aus ihm herausnehmen.
echo Die Ordner "build" und "dist" und die Datei MeshSwapper.spec darfst du loeschen.
explorer /select,"%~dp0MeshSwapper\MeshSwapper.exe"
pause
exit /b 0

:check_setup
set "SETUP_OK=0"
if not exist "%PYSETUP%" exit /b
for %%F in ("%PYSETUP%") do if %%~zF GTR 20000000 set "SETUP_OK=1"
exit /b

:failed
echo.
echo Das hat nicht geklappt. Lies die Meldung oben (z. B. keine Internetverbindung)
echo und versuche es noch einmal.
pause
exit /b 1
