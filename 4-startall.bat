@echo off
set prefix=wings2-live
echo Starting all %prefix% services
powershell -command "&{get-service %prefix%_* | ? name -match '[\d]+$' | ? status -ne Running | start-service }"
timeout /t 3 /nobreak >nul
powershell -command "&{get-service %prefix%_* | start-service ; while((get-service %prefix%_* | ? status -ne Running).count -gt 0){'Please wait while services start:' ; get-service %prefix%_* | ? status -ne Running ; sleep 6}}"
timeout /t 10