@echo off
setlocal
title FCC Lookup Ver 1.65 - Fast Launch Build Installer
color 1F
cls

echo.
echo  ============================================
echo   FCC Lookup Ver 1.65  --  Fast Launch Build
echo  ============================================
echo.

:: ── Check Python ──────────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo  Download from: https://python.org
    pause & exit /b 1
)

:: ── Check all required files are present ──────────────────────────────────────
echo  Checking required files...
for %%F in (FCC_Lookup_Ver_1.65.pyw FCC_Lookup_Ver_1.65.spec FC_launcher_icon.ico fcc_icon.png) do (
    if not exist "%%F" (
        echo  [ERROR] Missing file: %%F
        echo  All files must be in the same folder as this batch file.
        pause & exit /b 1
    )
)
echo  All files found.
echo.

:: ── Install dependency ────────────────────────────────────────────────────────
echo  Step 1 of 3:  Installing/updating PyInstaller...
python -m pip install pyinstaller --quiet --upgrade
if errorlevel 1 (
    echo  [ERROR] pip install failed. Check your internet connection.
    pause & exit /b 1
)
echo  Dependency installed.
echo.

:: ── Build onedir app with PyInstaller ────────────────────────────────────────
echo  Step 2 of 3:  Building fast-launch onedir app ^(this takes 1-2 minutes^)...
pyinstaller FCC_Lookup_Ver_1.65.spec --clean --noconfirm
if errorlevel 1 (
    echo  [ERROR] PyInstaller build failed. See output above.
    pause & exit /b 1
)
echo  App folder built successfully.
echo.

:: ── Compile the Inno Setup installer ─────────────────────────────────────────
echo  Step 3 of 3:  Compiling Windows installer...

set ISCC=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe"       set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"

if "%ISCC%"=="" (
    echo  [NOTICE] Inno Setup not found.
    echo  Download free from: https://jrsoftware.org/isdl.php
    echo  Then run:  ISCC.exe FCC_Lookup_Ver_1.65.iss
    echo.
    echo  Your fast-launch app folder is ready at:
    echo    dist\FCC_Lookup_Ver_1.65
    echo.
    pause & exit /b 0
)

mkdir installer_output 2>nul
"%ISCC%" FCC_Lookup_Ver_1.65.iss
if errorlevel 1 (
    echo  [ERROR] Inno Setup compilation failed.
    pause & exit /b 1
)

echo.
echo  ============================================
echo   BUILD COMPLETE!
echo.
echo   Installer ready at:
echo   installer_output\FCC_Lookup_Ver_1.65_Setup.exe
echo.
echo   This version installs a fast-launch app folder.
echo   Users still launch it from one normal shortcut.
echo  ============================================
echo.
pause
