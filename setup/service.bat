pushd %~dp0
pushd ..\wings
set workingDirectory="%cd%"
set nssm=C:\workspace\nssm\win64\
set prefix=wings2-live
set ip=%1
set port=%2
set servicename=%prefix%_%port%
set regionName=%3
set password=%4
set sidDev=S-1-5-21-1280039808-388949602-1088620844-1001
set sidGame=S-1-5-21-1280039808-388949602-1088620844-1000

net stop %servicename%
"%nssm%\nssm" remove %servicename% confirm
"%nssm%\nssm" install %servicename% "%workingDirectory%\topaz_game_64.exe"
"%nssm%\nssm" set %servicename% AppParameters "--ip %ip% --port %port%"
"%nssm%\nssm" set %servicename% AppDirectory "%workingDirectory%"
"%nssm%\nssm" set %servicename% AppExit Default Restart
"%nssm%\nssm" set %servicename% AppThrottle 1500
"%nssm%\nssm" set %servicename% AppStdout C:\workspace\servicelogs\%servicename%_out.txt
"%nssm%\nssm" set %servicename% AppStderr C:\workspace\servicelogs\%servicename%_err.txt
"%nssm%\nssm" set %servicename% AppRotateFiles 1
"%nssm%\nssm" set %servicename% AppRotateOnline 0
REM sets logs to rotate if service was down for over 30 seconds
"%nssm%\nssm" set %servicename% AppRotateSeconds 30
"%nssm%\nssm" set %servicename% Description %regionName%
"%nssm%\nssm" set %servicename% DisplayName "%prefix% Game Server %regionName%"
"%nssm%\nssm" set %servicename% ObjectName .\game "%password%"
"%nssm%\nssm" set %servicename% Start SERVICE_DELAYED_AUTO_START
"%nssm%\nssm" set %servicename% Type SERVICE_WIN32_OWN_PROCESS
net start %servicename%

REM sets permissions for "dev" account to stop/start service
sc sdset %servicename% D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;%sidDev%)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;%sidGame%)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)

timeout /t 30

exit