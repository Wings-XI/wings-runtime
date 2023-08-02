@echo off
set prefix=wings2-live
echo Stopping all %prefix% services
powershell -command "&{get-service %prefix%_* | stop-service -NoWait}"
timeout /t 5 /nobreak >nul
powershell -command "&{while((get-service %prefix%_* | ? status -ne stopped).count -gt 0){'Please wait while services stop' ; get-service %prefix%_* | ? status -ne stopped ; sleep 6}}"
timeout /t 10