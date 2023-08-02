@echo off
pushd c:\workspace
echo Starting backup of workspace directory
duplicacy\duplicacy_win_x64.exe backup 
timeout /t 60
