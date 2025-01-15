@echo off
chcp 65001 >nul
:: Включение RDP
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f

:: Разрешение удаленных подключений только с Network Level Authentication (NLA)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /v UserAuthentication /t REG_DWORD /d 1 /f

:: Включение брандмауэра для RDP (TCP порт 3389)
netsh advfirewall firewall add rule name="Remote Desktop" protocol=TCP dir=in localport=3389 action=allow

:: Включение службы удаленных рабочих столов
sc config TermService start= auto
net start TermService

:: Ограничение RDP-доступа для группы "Remote Desktop Users"
echo Granting RDP access to existing Remote Desktop group

:: Проверяем существование группы
net localgroup "Remote Desktop Users" >nul 2>&1
if %errorlevel% neq 0 (
    echo Группа "Remote Desktop Users" не найдена, пробую русскую версию.
    net localgroup "Пользователи удаленного рабочего стола" %USERNAME% /add
) else (
    net localgroup "Remote Desktop Users" %USERNAME% /add
)

:: Принудительное требование ввода пароля при входе
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v LimitBlankPasswordUse /t REG_DWORD /d 1 /f

:: Отключение многопользовательского режима (если нужно разрешить только 1 сессию)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fSingleSessionPerUser /t REG_DWORD /d 1 /f

echo RDP успешно настроен. Перезагрузите сервер для применения изменений.
pause
