@echo off
title Wenzhang Dazi - Stop

rem ============================================================
rem   Wenzhang Dazi - Stop
rem   Stop backend (port range 8000-8020) + frontend (5173-5199),
rem   then close the two cmd windows opened by start.bat.
rem   Ports are dynamic in start.bat, so we scan the ranges.
rem   Pure ASCII to avoid encoding issues.
rem ============================================================

echo.
echo ============================================
echo   Stopping Wenzhang Dazi services...
echo ============================================
echo.

echo [1/3] Killing backend processes (ports 8000-8020) ...
set "P=8000"
:killb
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%P% " ^| findstr "LISTENING"') do (
    echo   kill PID %%p on port %P%
    taskkill /F /PID %%p >nul 2>&1
)
set /a P+=1
if %P% leq 8020 goto killb

echo [2/3] Killing frontend processes (ports 5173-5199) ...
set "P=5173"
:killf
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%P% " ^| findstr "LISTENING"') do (
    echo   kill PID %%p on port %P%
    taskkill /F /PID %%p >nul 2>&1
)
set /a P+=1
if %P% leq 5199 goto killf

echo [3/3] Closing start.bat cmd windows ...
taskkill /F /FI "WINDOWTITLE eq backend-*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq frontend-*" >nul 2>&1

echo.
echo Done! Services stopped and windows closed.
echo.
pause
