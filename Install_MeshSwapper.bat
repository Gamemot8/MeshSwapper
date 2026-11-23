@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title MeshSwapper - Install or Repair

set "INSTALL=%LOCALAPPDATA%\Programs\MeshSwapper"
set "WORK=%TEMP%\MeshSwapper_build"
set "RAW=https://raw.githubusercontent.com/Gamemot8/MeshSwapper/main"
set "BROKEN=0"

echo ============================================================
echo   MeshSwapper - one-click install / repair
echo ============================================================
echo.
echo  - Installs for your Windows user only, no admin rights needed
echo  - Needs an internet connection the first time
echo  - Python 3.9 is installed automatically if it is missing
echo  - Something broken? Just run this file again, it repairs everything
echo  - Your sets and settings are kept
echo.

rem --- close MeshSwapper if it is running
taskkill /f /im MeshSwapper.exe >nul 2>&1

rem --- 1) get the program files: next to this file, otherwise from GitHub
if exist "%WORK%" rmdir /s /q "%WORK%"
mkdir "%WORK%" >nul 2>&1
if not exist "%~dp0meshswapper.pyw" goto download_source
if not exist "%~dp0meshswapper.ico" goto download_source
echo [1/5] Using the files next to this installer ...
copy /y "%~dp0meshswapper.pyw" "%WORK%\meshswapper.pyw" >nul
copy /y "%~dp0meshswapper.ico" "%WORK%\meshswapper.ico" >nul
goto have_source

:download_source
echo [1/5] Downloading MeshSwapper from GitHub ...
call :fetch "%RAW%/meshswapper.pyw" "%WORK%\meshswapper.pyw"
if errorlevel 1 goto download_failed
call :fetch "%RAW%/meshswapper.ico" "%WORK%\meshswapper.ico"
if errorlevel 1 goto download_failed

:have_source
echo.
echo [2/5] Checking Python ...

rem --- 2) use an existing Python, but only if it really works
set "PY=py -3.9"
%PY% -c "import encodings, tkinter, ensurepip" >nul 2>&1
if not errorlevel 1 goto have_python
set "PY=py"
%PY% -c "import encodings, tkinter, ensurepip" >nul 2>&1
if not errorlevel 1 goto have_python

rem --- check a Python that this installer put there earlier
set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
if not exist "%PYEXE%" goto need_install
"%PYEXE%" -c "import encodings, tkinter, ensurepip" >nul 2>&1
if not errorlevel 1 goto use_local
echo An earlier Python installation is broken and will be repaired ...
set "BROKEN=1"

:need_install
echo.
echo Python is being downloaded and installed now ...
taskkill /f /im python-3.9.13-amd64.exe >nul 2>&1
timeout /t 2 /nobreak >nul
set "PYSETUP=%TEMP%\python-setup-%RANDOM%.exe"
set "PYURL=https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe"

echo [Download 1/2] with curl ...
curl.exe -L -f --retry 3 --progress-bar -o "%PYSETUP%" "%PYURL%"
if errorlevel 1 del "%PYSETUP%" >nul 2>&1
call :bigger "%PYSETUP%" 20000000
if "%BIG%"=="1" goto do_install

echo [Download 2/2] with PowerShell ...
powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest '%PYURL%' -OutFile '%PYSETUP%'"
if errorlevel 1 del "%PYSETUP%" >nul 2>&1
call :bigger "%PYSETUP%" 20000000
if "%BIG%"=="1" goto do_install

echo Direct download does not work. Trying winget ...
winget install -e --id Python.Python.3.9 --scope user --silent --accept-package-agreements --accept-source-agreements
goto verify_install

:do_install
if "%BROKEN%"=="1" (
    echo Removing the broken Python installation ...
    start /wait "" "%PYSETUP%" /uninstall /quiet
    rmdir /s /q "%LOCALAPPDATA%\Programs\Python\Python39" >nul 2>&1
)
echo.
echo Installing Python 3.9. A window with a progress bar appears, you do not have to click anything.
echo Please wait until it continues by itself, about 1 to 3 minutes ...
start /wait "" "%PYSETUP%" /passive InstallAllUsers=0 PrependPath=1 Include_launcher=0 Include_test=0 Include_doc=0 Shortcuts=0
del "%PYSETUP%" >nul 2>&1

:verify_install
if not exist "%PYEXE%" goto install_failed
"%PYEXE%" -c "import encodings, tkinter, ensurepip" >nul 2>&1
if errorlevel 1 goto install_failed
goto use_local

:install_failed
echo.
echo The automatic Python installation did not work.
echo Please install Python 3.9 by hand: https://www.python.org/downloads/release/python-3913/
echo Tick "Add python.exe to PATH", then run this file again.
goto failed

:use_local
set PY="%PYEXE%"

:have_python
echo Using:
%PY% --version
echo.
echo [3/5] Installing numpy and pyinstaller, the first time takes a while ...
%PY% -m pip install --disable-pip-version-check numpy pyinstaller
if errorlevel 1 goto failed

echo.
echo [4/5] Building MeshSwapper, this takes a few minutes ...
pushd "%WORK%"
%PY% -m PyInstaller --noconfirm --clean --onedir --noupx --windowed --icon "meshswapper.ico" --name MeshSwapper meshswapper.pyw
set "BUILD_ERR=%errorlevel%"
popd
if not "%BUILD_ERR%"=="0" goto failed

echo.
echo [5/5] Installing MeshSwapper and creating shortcuts ...
if exist "%INSTALL%" rmdir /s /q "%INSTALL%"
xcopy /e /i /y /q "%WORK%\dist\MeshSwapper" "%INSTALL%" >nul
if errorlevel 1 goto failed
powershell -NoProfile -Command "$s=New-Object -ComObject WScript.Shell; foreach($p in @([Environment]::GetFolderPath('Desktop'), (Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'))){ $l=$s.CreateShortcut((Join-Path $p 'MeshSwapper.lnk')); $l.TargetPath='%INSTALL%\MeshSwapper.exe'; $l.WorkingDirectory='%INSTALL%'; $l.IconLocation='%INSTALL%\MeshSwapper.exe'; $l.Save() }" >nul 2>&1
rmdir /s /q "%WORK%" >nul 2>&1

echo.
echo ============================================================
echo   Done! MeshSwapper is installed.
echo ============================================================
echo A shortcut is on your Desktop and in the Start menu.
echo Starting MeshSwapper now ...
start "" "%INSTALL%\MeshSwapper.exe"
echo.
pause
exit /b 0

:download_failed
echo.
echo Could not download the program files from GitHub.
echo Check your internet connection, or download the whole repository as a ZIP, unzip it
echo and run this file from the unzipped folder.
goto failed

:fetch
rem usage: call :fetch URL FILE   (curl first, PowerShell as backup)
del "%~2" >nul 2>&1
curl.exe -L -f --retry 3 -s -o "%~2" "%~1" >nul 2>&1
call :bigger "%~2" 1000
if "%BIG%"=="1" exit /b 0
del "%~2" >nul 2>&1
powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest '%~1' -OutFile '%~2'" >nul 2>&1
call :bigger "%~2" 1000
if "%BIG%"=="1" exit /b 0
exit /b 1

:bigger
rem usage: call :bigger FILE MINBYTES   -> BIG=1 when the file exists and is bigger
set "BIG=0"
if not exist "%~1" exit /b
for %%F in ("%~1") do if %%~zF GTR %~2 set "BIG=1"
exit /b

:failed
echo.
echo That did not work. Read the message above, for example no internet connection,
echo and just run this file again.
pause
exit /b 1
