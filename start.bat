@echo off
chcp 65001 >nul
title Wenzhang Dazi - Launcher

rem ============================================================
rem   Wenzhang Dazi · one-click launcher (universal)
rem   - auto-detect python / npm (system PATH or WorkBuddy built-in)
rem   - auto npm install on first run
rem   - launch backend + frontend, then open browser
rem   Double-click this file, or run: start.bat
rem ============================================================

set "ROOT=%~dp0"

rem ---- 1. locate python ----
set "PY=python"
where python >nul 2>&1
if errorlevel 1 (
    if exist "%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe" (
        set "PY=%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe"
    ) else (
        echo [ERROR] Python not found. Install Python 3.11+ and tick "Add to PATH".
        pause
        exit /b 1
    )
)

rem ---- 2. locate npm ----
set "NPM=npm"
where npm >nul 2>&1
if errorlevel 1 (
    if exist "%USERPROFILE%\.workbuddy\binaries\node\versions\22.22.2\npm.cmd" (
        set "NPM=%USERPROFILE%\.workbuddy\binaries\node\versions\22.22.2\npm.cmd"
    ) else (
        echo [ERROR] npm not found. Install Node.js 18+ and tick "Add to PATH".
        pause
        exit /b 1
    )
)

echo [OK] python : %PY%
echo [OK] npm    : %NPM%

rem ---- 3. first-run frontend install ----
if not exist "%ROOT%frontend\node_modules" (
    echo [INFO] First run: installing frontend deps (about 1-2 min)...
    pushd "%ROOT%frontend"
    call "%NPM%" install
    if errorlevel 1 (
        echo [ERROR] npm install failed. Check network / Node install.
        popd
        pause
        exit /b 1
    )
    popd
)

echo.
echo ============================================
echo   Wenzhang Dazi is starting...
echo   Backend  : http://localhost:8000
echo   Frontend : http://localhost:5173
echo ============================================
echo.

echo [1/3] Starting backend (port 8000) ...
start "backend-8000" /D "%ROOT%backend" cmd /c ""%PY%" -m uvicorn app:app --host 0.0.0.0 --port 8000"

echo [2/3] Starting frontend (port 5173) ...
start "frontend-5173" /D "%ROOT%frontend" cmd /c ""%NPM%" run dev -- --host 0.0.0.0 --port 5173 --strictPort"

echo [3/3] Waiting for backend to be ready ...
set "BOK=0"
for /L %%i in (1,1,25) do (
    curl -s -o nul "http://localhost:8000/api/health" 2>nul
    if not errorlevel 1 (
        set "BOK=1"
        goto :fe
    )
    timeout /t 1 /nobreak >nul
)
:fe
timeout /t 5 /nobreak >nul
if "%BOK%"=="1" ( echo [OK] Backend is up. ) else ( echo [WARN] Backend did not respond - check the "backend-8000" window. )

rem ---- 4. smart-open browser (don't duplicate tab) ----
rem errorlevel: 0 = no connection -> open; 1 = already open -> skip; 2+ = cmd failed -> open (fallback)
powershell -NoProfile -Command "try { if (Get-NetTCPConnection -LocalPort 5173 -State Established -ErrorAction Stop) { exit 1 } else { exit 0 } } catch { exit 2 }" >nul 2>&1
if errorlevel 2 goto open
if errorlevel 1 goto skip
:open
echo Opening browser...
start "" "http://localhost:5173"
goto done
:skip
echo.
echo A page is already open - just press F5 in that tab.
:done

echo.
echo ============================================
echo   URL: http://localhost:5173
echo   LAN for others: http://YOUR-LAN-IP:5173
echo ============================================
echo.
echo To stop: double-click stop.bat
echo.
pause
