pushd %~dp0
pushd ..\LilisetteBot
set workingDirectory="%cd%"
set nssm=C:\workspace\nssm\win64\
set prefix=wings2-live
set servicename=%prefix%_LilisetteBot
FOR /F "tokens=*" %%g IN ('where python') do (SET python=%%g)
set password=%1
set sid=S-1-5-21-1280039808-388949602-1088620844-1001

net stop %servicename%
"%nssm%\nssm" remove %servicename% confirm
"%nssm%\nssm" install %servicename% "%python%"
"%nssm%\nssm" set %servicename% AppParameters "%workingDirectory%\LilisetteBot.py"
"%nssm%\nssm" set %servicename% AppDirectory "%workingDirectory%"
"%nssm%\nssm" set %servicename% AppExit Default Restart
"%nssm%\nssm" set %servicename% AppThrottle 1500
"%nssm%\nssm" set %servicename% AppStdout C:\workspace\servicelogs\%servicename%_out.txt
"%nssm%\nssm" set %servicename% AppStderr C:\workspace\servicelogs\%servicename%_err.txt
"%nssm%\nssm" set %servicename% AppRotateFiles 1
"%nssm%\nssm" set %servicename% AppRotateOnline 0
REM sets logs to rotate if service was down for over 30 seconds
"%nssm%\nssm" set %servicename% AppRotateSeconds 30
"%nssm%\nssm" set %servicename% Description %servicename%
"%nssm%\nssm" set %servicename% DisplayName "Lilisette Bot"
"%nssm%\nssm" set %servicename% ObjectName .\game "%password%"
"%nssm%\nssm" set %servicename% Start SERVICE_DELAYED_AUTO_START
"%nssm%\nssm" set %servicename% Type SERVICE_WIN32_OWN_PROCESS
net start %servicename%

REM sets permissions for "dev" account to stop/start service
sc sdset %servicename% D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;%sid%)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)

timeout /t 30

exit