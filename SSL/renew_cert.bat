@echo off
chcp 65001
set "DOMAIN=sms.getleads.red"

:: Переход в директорию с Certbot
cd /d D:\Certbot\bin

:: Запуск Certbot с использованием переменной %DOMAIN%
certbot certonly --webroot -w "E:\OSPanel\home\%DOMAIN%" -d %DOMAIN% --force-renewal -v

pause
