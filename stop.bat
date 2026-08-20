@echo off
title Wenzhang Dazi - Stop

rem ============================================================
rem   Wenzhang Dazi - Stop
rem   Stop backend (8000) + frontend (5173), then close
rem   the two cmd windows opened by start.bat.
rem   Pure ASCII to avoid encoding issues.
rem ============================================================

echo.
echo ============================================
echo   Stopping Wenzhang Dazi services...
echo ============================================
echo.

echo [1/3] Killing backend process (port 8000) ...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo   kill PID %%p
    taskkill /F /PID %%p >nul 2>&1
)

echo [2/3] Killing frontend process (port 5173) ...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo   kill PID %%p
    taskkill /F /PID %%p >nul 2>&1
)

echo [3/3] Closing start.bat cmd windows ...
taskkill /F /FI "WINDOWTITLE eq backend-8000*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq frontend-5173*" >nul 2>&1

echo.
echo Done! Services stopped and windows closed.
echo.
pause
