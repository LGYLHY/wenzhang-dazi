@echo off
chcp 65001 >nul
title Wenzhang Dazi - Launcher

rem ============================================================
rem   文案搭子 · 一键启动（通用版，任何人 clone 后可直接用）
rem   - 自动寻找 python / npm（系统 PATH 或 WorkBuddy 内置路径）
rem   - 首次运行自动安装前端依赖
rem   用法：双击本文件，或在终端执行 start.bat
rem ============================================================

set "ROOT=%~dp0"

rem ---- 1. 定位 python ----
set "PY=python"
where python >nul 2>&1
if errorlevel 1 (
    if exist "%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe" (
        set "PY=%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe"
    ) else (
        echo [ERROR] 未找到 Python。请安装 Python 3.11+ 并勾选 "Add to PATH"。
        pause
        exit /b 1
    )
)

rem ---- 2. 定位 npm ----
set "NPM=npm"
where npm >nul 2>&1
if errorlevel 1 (
    if exist "%USERPROFILE%\.workbuddy\binaries\node\versions\22.22.2\npm.cmd" (
        set "NPM=%USERPROFILE%\.workbuddy\binaries\node\versions\22.22.2\npm.cmd"
    ) else (
        echo [ERROR] 未找到 npm。请安装 Node.js 18+ 并勾选 "Add to PATH"。
        pause
        exit /b 1
    )
)

rem ---- 3. 首次运行自动安装前端依赖 ----
if not exist "%ROOT%frontend\node_modules" (
    echo [INFO] 首次运行，安装前端依赖（约 1~2 分钟）...
    pushd "%ROOT%frontend"
    call "%NPM%" install
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
start "backend-8000" cmd /c "pushd "%ROOT%backend" && "%PY%" -m uvicorn app:app --host 0.0.0.0 --port 8000"

echo [2/3] Starting frontend (port 5173) ...
start "frontend-5173" cmd /c "pushd "%ROOT%frontend" && "%NPM%" run dev -- --host 0.0.0.0 --port 5173 --strictPort"

echo [3/3] Waiting for services to be ready ...
timeout /t 12 /nobreak >nul

rem ---- 4. 智能开浏览器：页面已开则不重复开标签 ----
rem errorlevel: 0 = 无连接 -> open; 1 = 已连接 -> skip; 2+ = 命令失败 -> open (fallback)
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
echo   LAN for others: http://你的局域网IP:5173
echo ============================================
echo.
echo To stop: double-click stop.bat
echo.
pause
