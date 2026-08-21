@echo off
chcp 65001 >nul
title 文案搭子 - 一键启动

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

echo ==========================================
echo   文案搭子 · 一键启动
echo ==========================================
echo.

REM ---- 路径检查：含中文或括号会导致 npm / 启动异常 ----
powershell -NoProfile -Command "if ('%ROOT%' -match '[\u4e00-\u9fa5()]') {exit 1} else {exit 0}" >nul 2>&1
if errorlevel 1 goto badpath
goto pathok
:badpath
echo.
echo [ERROR] 项目路径包含中文或括号，会导致启动失败。
echo   当前路径：%ROOT%
echo   请先把整个文件夹移动到纯英文、无括号的路径，例如：
echo     D:\wenzhang-dazi
echo   然后再双击 start.bat。
echo.
pause
exit /b 1
:pathok

REM ---- 定位 Python（必须使用自带 chromadb 的那个 Python）----
set "PY="
if exist "%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe" set "PY=%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe"
if not "%PY%"=="" goto pyok
for /f "delims=" %%i in ('where python 2^>nul') do (
    set "PY=%%i"
    goto pyok
)
:pyok
if "%PY%"=="" goto nopython
echo [OK] python : %PY%

REM ---- 确保 Python 依赖（fastapi / uvicorn / chromadb）----
echo [PRE] 检查 Python 依赖（fastapi, uvicorn, chromadb）...
"%PY%" -c "import fastapi, uvicorn, chromadb" >nul 2>&1
if not errorlevel 1 goto pydepsok
echo       未安装，正在 pip install（约 1-3 分钟，请稍候）...
"%PY%" -m pip install -q --disable-pip-version-check -r "%ROOT%\backend\requirements.txt"
if not errorlevel 1 goto pydepsok
echo.
echo [ERROR] pip install 失败。请检查网络，或手动运行：
echo   "%PY%" -m pip install -r "%ROOT%\backend\requirements.txt"
echo.
pause
exit /b 1
:pydepsok
echo [OK] Python 依赖就绪。

REM ---- 选择一个空闲的后端端口（避免与他人已占用 8000 的服务冲突）----
set "BPORT=8000"
:bportscan
netstat -ano | findstr ":%BPORT% " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 goto bportbusy
goto bportok
:bportbusy
set /a BPORT+=1
if %BPORT% gtr 8020 goto bportfail
goto bportscan
:bportok
echo [OK] 后端端口 : %BPORT%
goto mktemp
:bportfail
echo [WARN] 8000-8020 均未空闲，回退到 8000。
set "BPORT=8000"
:mktemp

REM ---- 临时启动脚本（避免项目路径含特殊字符时 start 报错）----
set "TMP=%TEMP%\wzd-launcher-%RANDOM%"
mkdir "%TMP%" 2>nul

(
    echo @echo off
    echo chcp 65001 ^>nul
    echo cd /d "%ROOT%\backend"
    echo "%PY%" -m uvicorn app:app --host 0.0.0.0 --port %BPORT%
    echo.
    echo [backend 已停止] 按任意键关闭。
    echo pause ^>nul
) > "%TMP%\run_backend.bat"

echo [1/3] 启动后端（端口 %BPORT%）...
start "backend-%BPORT%" cmd /c "%TMP%\run_backend.bat"
echo [OK] 后端窗口已打开。

echo [2/3] 等待后端就绪（最多 30 秒）...
set "CNT=0"
:waitloop
set /a CNT+=1
timeout /t 1 /nobreak >nul
curl -s -o nul --max-time 2 "http://localhost:%BPORT%/api/health" >nul 2>&1
if not errorlevel 1 goto ready
if "%CNT%"=="30" goto beready
goto waitloop
:ready
echo [OK] 后端已就绪。
goto beready
:beready

REM ---- 前端模式：有 dist 则由后端直接托管（无需 Node / npm）；否则回退 Vite 开发模式 ----
if exist "%ROOT%\frontend\dist\index.html" goto staticmode

echo [3/3] 未检测到 frontend/dist，回退到 Vite 开发模式（需要 Node + npm）...
set "NPM="
where npm >nul 2>&1
if not errorlevel 1 set "NPM=npm"
if "%NPM%"=="" if exist "%USERPROFILE%\.workbuddy\binaries\node\versions\22.22.2\npm.cmd" set "NPM=%USERPROFILE%\.workbuddy\binaries\node\versions\22.22.2\npm.cmd"
if "%NPM%"=="" goto nonpm
echo [OK] npm    : %NPM%

set "FPORT=5173"
:fportscan
netstat -ano | findstr ":%FPORT% " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 goto fportbusy
goto fportok
:fportbusy
set /a FPORT+=1
if %FPORT% gtr 5199 goto fportfail
goto fportscan
:fportok
echo [OK] 前端端口: %FPORT%
goto mkfront
:fportfail
echo [WARN] 5173-5199 均未空闲，回退到 5173。
set "FPORT=5173"
:mkfront
(
    echo @echo off
    echo chcp 65001 ^>nul
    echo cd /d "%ROOT%\frontend"
    echo set "VITE_API_PORT=%BPORT%"
    echo call "%NPM%" run dev -- --port %FPORT%
    echo.
    echo [frontend 已停止] 按任意键关闭。
    echo pause ^>nul
) > "%TMP%\run_frontend.bat"
echo       启动前端（端口 %FPORT%）...
start "frontend-%FPORT%" cmd /c "%TMP%\run_frontend.bat"
set "SHOWPORT=%FPORT%"
echo [INFO] 等待前端就绪（最多 30 秒）...
set "FCNT=0"
:fwait
set /a FCNT+=1
timeout /t 1 /nobreak >nul
curl -s -o nul --max-time 2 "http://localhost:%FPORT%/" >nul 2>&1
if not errorlevel 1 goto fready
if "%FCNT%"=="30" goto fopen
goto fwait
:fready
echo [OK] 前端已就绪。
goto fopen

:staticmode
echo [3/3] 检测到 frontend/dist，由后端直接托管前端（无需安装 Node / npm）。
set "SHOWPORT=%BPORT%"

:fopen
echo.
echo ============================================
echo  产品已就绪！
echo  浏览器 : http://localhost:%SHOWPORT%
echo  后端   : http://localhost:%BPORT%/api/health
echo ============================================
echo.
echo 两个服务窗口正在运行，使用 stop.bat 可一键关闭。
start "" "http://localhost:%SHOWPORT%"
echo [INFO] 已尝试打开浏览器。
echo.
echo 本窗口 5 秒后关闭，服务继续在后台运行。
timeout /t 5 /nobreak >nul
exit /b 0

:nopython
echo.
echo [ERROR] 未找到 Python 3.11+。
echo   下载地址：https://www.python.org/downloads/
echo   安装时请务必勾选 "Add Python to PATH"。
echo.
pause
exit /b 1

:nonpm
echo.
echo [ERROR] 未检测到 Node.js（npm），且 frontend/dist 不存在。
echo   开发模式需要 Node；或者先在本机执行 `npm run build` 生成 dist 后，
echo   后端即可直接托管前端，无需 Node。
echo   下载 Node：https://nodejs.org/
echo.
pause
exit /b 1
