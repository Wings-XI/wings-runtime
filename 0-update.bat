@echo off

pushd c:\workspace\wings\git\wings
echo "Pull the live branch (git pull --rebase), resolving any issues"
start "git bash" /wait "C:\Program Files\Git\git-bash.exe"

pushd build
echo "Build the RelWithDebInfo, then close Visual Studio"
start "Release" /wait "64\topaz.sln"

echo "Build the Debug, then close Visual Studio"
start "Debug" /wait "64-Tracy\topaz.sln"

pause
