@echo off
title FCC Lookup Ver 1.67 - Debug Run
python FCC_Lookup_Ver_1.67.pyw
if errorlevel 1 (
    echo.
    echo App exited with an error. Check the message above or:
    echo   %%APPDATA%%\FCC_Lookup\error_log.txt
    echo.
    pause
)
