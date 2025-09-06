@echo off
setlocal enabledelayedexpansion

:: ==============================
:: ls.cmd - простой аналог ls
:: ==============================
:: Опции:
::   (без аргументов)   - показать файлы и папки текущей папки (верхний уровень)
::   /s                 - рекурсивный список всех файлов и папок
::   /d                 - показать только папки
::   /f                 - показать только файлы
::   /l                 - подробный режим (дата, время, размер)
::   маска (например *.exe) - фильтровать вывод по маске (только текущая папка)
::   можно комбинировать: ls /s /l *.exe
:: ==============================

set "recurse="
set "showDirs="
set "showFiles="
set "longMode="
set "mask=*"

if "%~1"=="/?"  goto help
if "%~1"=="-h"  goto help

:parse_args
if "%~1"=="" goto run
if /i "%~1"=="/s" set "recurse=1" & shift & goto parse_args
if /i "%~1"=="/d" set "showDirs=1" & shift & goto parse_args
if /i "%~1"=="/f" set "showFiles=1" & shift & goto parse_args
if /i "%~1"=="/l" set "longMode=1" & shift & goto parse_args
set "mask=%~1"
shift
goto parse_args

:run
if defined recurse (
    echo [Рекурсивный список]
    for /r /d %%D in (*) do if not defined showFiles call :printEntry "%%D" dir
    for /r %%F in (%mask%) do if not exist "%%F\" if not defined showDirs call :printEntry "%%F" file
) else (
    echo [Текущая папка]
    :: сначала папки
    for /d %%D in (*) do if not defined showFiles call :printEntry "%%D" dir
    :: потом файлы
    for %%F in (%mask%) do if not exist "%%F\" if not defined showDirs call :printEntry "%%F" file
)
exit /b

:printEntry
set "path=%~1"
set "type=%~2"
if defined longMode (
    for %%I in ("%path%") do (
        set "size=%%~zI"
        set "date=%%~tI"
        if "%type%"=="dir" (
            echo !date!    <DIR>          \%%~nxI
        ) else (
            echo !date!    !size! bytes   %%~nxI
        )
    )
) else (
    if "%type%"=="dir" (
        echo \%~nx1
    ) else (
        echo %~nx1
    )
)
exit /b

:help
echo.
echo Использование: ls [опции] [маска]
echo.
echo   (без аргументов)   - файлы и папки текущей папки
echo   /s                 - рекурсивный список
echo   /d                 - только папки
echo   /f                 - только файлы
echo   /l                 - подробный режим (дата, время, размер)
echo   маска (например *.exe) - фильтр по имени
echo.
exit /b
