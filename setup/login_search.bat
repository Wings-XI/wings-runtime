pushd %~dp0
pushd ..\wings
set workingDirectory="%cd%"
set nssm=C:\workspace\nssm\win64\
set prefix=wings2-live
set ip=%1
set password=%2
set sid=S-1-5-21-1280039808-388949602-1088620844-1001


set servicename=%prefix%_search
set regionName=Search
net stop %servicename%
"%nssm%\nssm" remove %servicename% confirm
"%nssm%\nssm" install %servicename% "%workingDirectory%\topaz_search_64.exe"
"%nssm%\nssm" set %servicename% AppParameters "--ip %ip%"
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
"%nssm%\nssm" set %servicename% DisplayName "%prefix% %regionName%"
"%nssm%\nssm" set %servicename% ObjectName .\game "%password%"
"%nssm%\nssm" set %servicename% Start SERVICE_DELAYED_AUTO_START
"%nssm%\nssm" set %servicename% Type SERVICE_WIN32_OWN_PROCESS
net start %servicename%

sc sdset %servicename% D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;%sid%)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)


set servicename=%prefix%_login
set regionName=Login
net stop %servicename%
"%nssm%\nssm" remove %servicename% confirm
"%nssm%\nssm" install %servicename% "%workingDirectory%\topaz_new_connect_64.exe"
"%nssm%\nssm" set %servicename% AppParameters "--ip %ip%"
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
"%nssm%\nssm" set %servicename% DisplayName "%prefix% %regionName%"
"%nssm%\nssm" set %servicename% ObjectName .\game "%password%"
"%nssm%\nssm" set %servicename% Start SERVICE_DELAYED_AUTO_START
"%nssm%\nssm" set %servicename% Type SERVICE_WIN32_OWN_PROCESS
net start %servicename%

sc sdset %servicename% D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;%sid%)S:(AU;FA;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;WD)


timeout /t 30

exit