@echo off
chcp 65001 >nul
title Wutang-mocha Wenan Dazi - Launcher

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

echo ==========================================
echo  Wutang-mocha Wenan Dazi - One-click start
echo ==========================================
echo.

REM ---- detect problematic path (Chinese / parens) and warn early ----
echo %ROOT% | findstr "(" >nul
if not errorlevel 1 goto warnpath
echo %ROOT% | findstr /R "[一-龥]" >nul
if not errorlevel 1 goto warnpath
goto nowarn

:warnpath
echo [WARN] The project path contains special characters (Chinese / parentheses).
echo        It MAY cause npm install to fail. Recommended: move to D:\wenzhang-dazi
echo.
:nowarn

REM ---- locate python ----
set "PY="
where python >nul 2>&1
if not errorlevel 1 set "PY=python"
if "%PY%"=="" if exist "%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe" set "PY=%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe"
if "%PY%"=="" goto nopython
echo [OK] python : %PY%

REM ---- locate npm ----
set "NPM="
where npm >nul 2>&1
if not errorlevel 1 set "NPM=npm"
if "%NPM%"=="" if exist "%USERPROFILE%\.workbuddy\binaries\node\versions\22.22.2\npm.cmd" set "NPM=%USERPROFILE%\.workbuddy\binaries\node\versions\22.22.2\npm.cmd"
if "%NPM%"=="" goto nonpm
echo [OK] npm    : %NPM%
echo.

REM ---- pick a FREE backend port (avoid colliding with another running service) ----
set "BPORT=8000"
:bportscan
powershell -NoProfile -Command "try{Get-NetTCPConnection -LocalPort %BPORT% -ErrorAction Stop; exit 1}catch{exit 0}" >nul 2>&1
if errorlevel 1 goto bportbusy
goto bportok
:bportbusy
set /a BPORT+=1
if %BPORT% gtr 8020 goto bportfail
goto bportscan
:bportok
echo [OK] backend port : %BPORT%
goto fportprep
:bportfail
echo [WARN] Could not find a free port 8000-8020, falling back to 8000.
set "BPORT=8000"
:fportprep

REM ---- pick a FREE frontend port (avoid showing someone else's project on 5173) ----
set "FPORT=5173"
:fportscan
powershell -NoProfile -Command "try{Get-NetTCPConnection -LocalPort %FPORT% -ErrorAction Stop; exit 1}catch{exit 0}" >nul 2>&1
if errorlevel 1 goto fportbusy
goto fportok
:fportbusy
set /a FPORT+=1
if %FPORT% gtr 5199 goto fportfail
goto fportscan
:fportok
echo [OK] frontend port: %FPORT%
goto mktemp
:fportfail
echo [WARN] Could not find a free port 5173-5199, falling back to 5173.
set "FPORT=5173"
:mktemp

REM ---- create temp helper scripts so 'start' never sees the project path with parens ----
set "TMP=%TEMP%\wzd-launcher-%RANDOM%"
mkdir "%TMP%" 2>nul
if not exist "%TMP%" goto tmpfail

REM Use a SAFE cache dir (no parens) so npm never writes inside the project path
set "NPM_CONFIG_CACHE=%TEMP%\npm-cache-wzd"
set "NPM_CONFIG_TMP=%TEMP%\npm-tmp-wzd"

(
    echo @echo off
    echo chcp 65001 ^>nul
    echo cd /d "%ROOT%\backend"
    echo "%PY%" -m uvicorn app:app --host 0.0.0.0 --port %BPORT%
    echo.
    echo [backend stopped] Press any key to close.
    echo pause ^>nul
) > "%TMP%\run_backend.bat"

(
    echo @echo off
    echo chcp 65001 ^>nul
    echo cd /d "%ROOT%\frontend"
    echo set "VITE_API_PORT=%BPORT%"
    echo call "%NPM%" run dev -- --port %FPORT%
    echo.
    echo [frontend stopped] Press any key to close.
    echo pause ^>nul
) > "%TMP%\run_frontend.bat"

(
    echo @echo off
    echo chcp 65001 ^>nul
    echo cd /d "%ROOT%\frontend"
    echo call "%NPM%" install --no-audit --no-fund
) > "%TMP%\do_install.bat"

echo [1/4] Starting backend (port %BPORT%) ...
start "backend-%BPORT%" cmd /c "%TMP%\run_backend.bat"
echo [OK] backend window opened.

echo [2/4] Preparing frontend ...
if exist "%ROOT%\frontend\node_modules" goto have_modules
echo       First run: installing frontend deps (1-3 min) ...
echo.
call "%TMP%\do_install.bat"
if not errorlevel 1 goto install_ok
echo.
echo [WARN] npm install with default registry failed.
echo        Retrying with China mirror (npmmirror.com) ...
(
    echo @echo off
    echo chcp 65001 ^>nul
    echo cd /d "%ROOT%\frontend"
    echo call "%NPM%" install --no-audit --no-fund --registry=https://registry.npmmirror.com
) > "%TMP%\do_install.bat"
call "%TMP%\do_install.bat"
if not errorlevel 1 goto install_ok
echo.
echo [ERROR] npm install failed. Please try:
echo   1. Switch to a different network (e.g. mobile hotspot)
echo   2. Move project to a simple path like D:\wenzhang-dazi
echo   3. Check Node.js version (need 18+): node -v
echo.
pause
exit /b 1

:install_ok
echo [OK] npm install done.
:have_modules

echo [3/4] Starting frontend (port %FPORT%) ...
start "frontend-%FPORT%" cmd /c "%TMP%\run_frontend.bat"
echo [OK] frontend window opened.

echo.
echo [4/4] Waiting for backend to be ready (max 30s) ...
set "CNT=0"
:waitloop
set /a CNT+=1
timeout /t 2 /nobreak >nul
powershell -NoProfile -Command "$ErrorActionPreference='SilentlyContinue'; try{$r=Invoke-WebRequest -Uri 'http://localhost:%BPORT%/api/health' -UseBasicParsing -TimeoutSec 2; if($r.StatusCode -eq 200){exit 0}else{exit 1}}catch{exit 1}" >nul 2>&1
if not errorlevel 1 goto ready
if "%CNT%"=="15" goto fe
goto waitloop
:ready
echo [OK] Backend is up.
goto showurls
:fe
echo [WARN] Backend did not respond after 30s. Check the "backend-%BPORT%" window.

:showurls
echo.
echo ============================================
echo  Product is ready!
echo  Browser :  http://localhost:%FPORT%
echo  Backend :  http://localhost:%BPORT%/api/health
echo ============================================
echo.
echo Two service windows are running. Use stop.bat to close them.

REM ---- wait for frontend to be ready, then open browser ----
echo [INFO] Waiting for frontend to be ready (up to 40s) ...
set "FCNT=0"
:fwait
set /a FCNT+=1
timeout /t 1 /nobreak >nul
powershell -NoProfile -Command "$ErrorActionPreference='SilentlyContinue'; try{$r=Invoke-WebRequest -Uri 'http://localhost:%FPORT%/' -UseBasicParsing -TimeoutSec 2; if($r.StatusCode -eq 200){exit 0}else{exit 1}}catch{exit 1}" >nul 2>&1
if not errorlevel 1 goto fready
if "%FCNT%"=="40" goto fnotready
goto fwait
:fready
echo [OK] Frontend is up.
goto fopen
:fnotready
echo [WARN] Frontend did not respond after 40s.
echo        Check the "frontend-%FPORT%" window - it should show "Local: http://localhost:%FPORT%/".
echo        Browser will still open; if the page fails, wait 10s then press F5.
:fopen
start "" "http://localhost:%FPORT%"
echo [INFO] Browser opened: http://localhost:%FPORT%

echo.
echo This window will close in 5s. Services keep running.
timeout /t 5 /nobreak >nul
exit /b 0

:nopython
echo.
echo [ERROR] Python 3.11+ not found.
echo   Download: https://www.python.org/downloads/
echo   IMPORTANT: Check "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:nonpm
echo.
echo [ERROR] Node.js (npm) not found.
echo   Download: https://nodejs.org/
echo.
pause
exit /b 1

:tmpfail
echo.
echo [ERROR] Cannot create temp directory: %TMP%
pause
exit /b 1
