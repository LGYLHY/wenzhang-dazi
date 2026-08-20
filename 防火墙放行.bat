@echo off
title Wenzhang Dazi - Firewall Allow

rem ============================================================
rem   Allow LAN access to Wenzhang Dazi (ports 5173 + 8000)
rem   IMPORTANT: right-click this file -> Run as administrator
rem ============================================================

echo.
echo Allowing port 5173 (frontend) for LAN access ...
netsh advfirewall firewall add rule name="WenzhangDazi 5173" dir=in action=allow protocol=TCP localport=5173

echo Allowing port 8000 (backend) for LAN access ...
netsh advfirewall firewall add rule name="WenzhangDazi 8000" dir=in action=allow protocol=TCP localport=8000

echo.
echo Done! Others on the same WiFi can now visit:
echo   http://YOUR-LAN-IP:5173
echo.
echo To check your LAN IP: run "ipconfig" and look for IPv4.
echo.
pause
