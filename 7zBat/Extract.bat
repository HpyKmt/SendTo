@echo off

rem -------------------------------------------------------------------
rem Extract Statement
rem -------------------------------------------------------------------
rem x (Extract with full paths) command
rem https://sevenzip.osdn.jp/chm/cmdline/commands/extract_full.htm
rem -------------------------------------------------------------------

rem Path to 7z.exe
set "application="C:\Program Files\7-Zip\7z.exe""

rem Get the archived file.
set /p "fp_in=Archive File: "

rem Get output folder
set /p "dir_out=Drag and Drop output folder: "

rem Get filter expression
set /p "filter=Wild Card Expression: "

rem Execute the statement
%application% x %fp_in% -o%dir_out% %filter% -r

rem in case of password encryption, password input will be prompted.
rem however, the input will not be echoed on the console.

rem Keep the console opened
pause
