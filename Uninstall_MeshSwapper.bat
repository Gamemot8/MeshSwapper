@echo off
setlocal EnableExtensions
title MeshSwapper - Uninstall

echo This removes the MeshSwapper program and its shortcuts.
echo Your sets and settings stay in %LOCALAPPDATA%\MeshSwapper
echo Python is not removed.
echo.
pause

taskkill /f /im MeshSwapper.exe >nul 2>&1
rmdir /s /q "%LOCALAPPDATA%\Programs\MeshSwapper" >nul 2>&1
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\MeshSwapper.lnk" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-Item -ErrorAction SilentlyContinue (Join-Path ([Environment]::GetFolderPath('Desktop')) 'MeshSwapper.lnk')" >nul 2>&1

echo.
echo Done. To remove your sets and settings too, delete the folder
echo %LOCALAPPDATA%\MeshSwapper
echo.
pause
exit /b 0
