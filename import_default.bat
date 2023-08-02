rem @echo off
set host=
set user=
set pass=
set db=

"C:\Program Files\MariaDB 10.6\bin\mysql.exe" -h %host% -u %user% -p%pass% -D %db% < wings\sql-wings\%1
exit