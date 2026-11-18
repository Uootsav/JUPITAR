@echo off
cd /d "%~dp0"
echo DEVELOPER BUILD ONLY. End users do not run this file.
echo Requires Python 3.11, Git, CMake, Visual Studio C++ build tools, and Inno Setup 6.
echo Prefer the included GitHub Actions workflow to avoid installing these locally.
powershell.exe -NoProfile -File tools\build_windows.ps1
if errorlevel 1 echo Build failed. Review the error above.
pause
