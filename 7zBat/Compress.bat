@echo off

echo ---------------------
echo Compress File
echo ---------------------

rem Path to 7z.exe
set "application="C:\Program Files\7-Zip\7z.exe""

rem Get the archived file.
set /p "dir_in=Input Folder: "

cd %dir_in%
echo CWD: %dir_in%

set /p "dir_out=Output Folder: "
set /p "fn=Output File name: "
set "fp_out=%dir_out%\%fn%"
echo OUT: %fp_out%

set /p "wld_crd=Wild Card(.*): "

set /p "arc_type=Archive Type:"

set /p "pwd=Password: "
echo DBG %pwd%

rem Execute the statement
%application% a %fp_out% %wld_crd% -t%arc_type% -r -p%pwd% -mhe

pause