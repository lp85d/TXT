# Установка SSH-сервера и настройка
Write-Host "Установка и настройка SSH-сервера..." -ForegroundColor Green

# Установка OpenSSH Server, если он не установлен
if (-not (Get-WindowsCapability -Online | Where-Object { $_.Name -eq "OpenSSH.Server~~~~0.0.1.0" }).State -eq "Installed") {
    Add-WindowsCapability -Online -Name "OpenSSH.Server~~~~0.0.1.0"
    Write-Host "OpenSSH Server установлен."
}

# Запуск службы SSH и установка её в автозапуск
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
Write-Host "Служба SSH запущена и настроена на автозапуск."

# Открытие порта 22 в брандмауэре
Write-Host "Открытие порта 22 в брандмауэре..." -ForegroundColor Green
New-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -DisplayName "OpenSSH Server (TCP-In)" -Protocol TCP -LocalPort 22 -Action Allow -Direction Inbound
Write-Host "Порт 22 открыт."

# Проверка статуса SSH-сервера
Write-Host "Проверка статуса SSH-сервера..." -ForegroundColor Green
if ((Get-Service sshd).Status -eq "Running") {
    Write-Host "SSH-сервер успешно настроен и запущен!" -ForegroundColor Green
} else {
    Write-Host "Не удалось запустить SSH-сервер. Проверьте настройки вручную." -ForegroundColor Red
}
