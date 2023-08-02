@echo off
powershell -command "&{(get-host).ui.rawui.windowsize=@{width=120;height=40};}"

set prefix=wings2-live
powershell -command "&{while((get-service %prefix%_* | ? status -ne stopped).count -gt 0){'Please wait while services stop' ; get-service %prefix%_* | ? status -ne stopped ; sleep 6}}"
set gitPath=../git/wings

REM mkdir "./wings/"
REM mklink /D "./wings/scripts" R:\

if exist "R:\" (
	robocopy /mir /NODCOPY /MT:4 /r:0 /w:0 "%gitPath%/scripts/" "./wings/scripts/" /NFL /NDL /NJS 
	
	robocopy /mir /NODCOPY /MT:4 /r:0 /w:0 "%gitPath%" "./wings" /XD "scripts" "cmake*" ".cmake*" ".vs" "build" /XF "cmake*" "*.tlog" "*.pyc" "*.log" /NFL /NDL /NJS 
) else (
	echo "scripts mount drive (R:\) not found, check ramdisk config?"
	timeout /t 600
)
timeout /t 10
