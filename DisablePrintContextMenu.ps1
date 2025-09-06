$progidKeys = Get-ChildItem -Path "Registry::HKEY_CLASSES_ROOT" -ErrorAction SilentlyContinue

foreach ($key in $progidKeys) {
    $printPath = "Registry::HKEY_CLASSES_ROOT\$($key.PSChildName)\shell\print"
    if (Test-Path $printPath) {
        try {
            New-ItemProperty -Path $printPath -Name "LegacyDisable" -Value "" -PropertyType String -Force | Out-Null
            Write-Host "✔ Отключено: $($key.PSChildName)"
        } catch {
            Write-Host "⚠ Ошибка: $($key.PSChildName)"
        }
    }
}
