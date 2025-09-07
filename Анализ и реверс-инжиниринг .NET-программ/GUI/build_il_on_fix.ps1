# build_il_on_fix_v3.ps1
# Улучшенное исправление всех случаев '/on' в IL коде
# Обрабатывает структуры данных, поля, типы и методы

param(
    [string]$src = "C.il",
    [string]$out = "Laitis-rebuilt.exe",
    [string]$ilasm = "C:\Windows\Microsoft.NET\Framework\v4.0.30319\ilasm.exe",
    [int]$maxTries = 30,
    [int]$timeout = 300
)

$log = "errors.log"
$ErrorActionPreference = "Stop"

Write-Host "=== build_il_on_fix_v3.ps1 (улучшенное исправление '/on') ===" -ForegroundColor Green
Write-Host "Source: $src"
Write-Host "ILAsm:  $ilasm"
Write-Host "Output: $out"
Write-Host "Max tries: $maxTries, Timeout: $timeout sec"
Write-Host "-----------------------------------------------"

$start = Get-Date
$tries = 0

function Apply-Enhanced-On-Patch([string]$text) {
    $totalRepl = 0
    $originalText = $text
    
    Write-Host "Применяю расширенные исправления для '/on'..." -ForegroundColor Yellow
    
    # 1. Исправление полей структур: 'Ln/on'::field_name
    $pattern1 = "(?<!')\b([\w\.\-\+<>/]+/on)(?=::[\w_]+)"
    $text = [regex]::Replace($text, $pattern1, {
        param($match)
        $script:totalRepl++
        return "'" + $match.Groups[1].Value + "'"
    }, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    
    # 2. Исправление типов значений: valuetype 'Ln/on'
    $pattern2 = "(?<=valuetype\s+)(?<!')\b([\w\.\-\+<>/]+/on)\b(?!\w)"
    $text = [regex]::Replace($text, $pattern2, {
        param($match)
        $script:totalRepl++
        return "'" + $match.Groups[1].Value + "'"
    }, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    
    # 3. Исправление объявлений классов: beforefieldinit 'on'
    $pattern3 = "(?<=\.class\b[^\r\n]*\bbeforefieldinit\s+)(?<!')(\bon\b)(?!\w)"
    $text = [regex]::Replace($text, $pattern3, {
        param($match)
        $script:totalRepl++
        return "'" + $match.Groups[1].Value + "'"
    }, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    
    # 4. Исправление загрузки адресов полей: ldflda ... 'Ln/on'::field
    $pattern4 = "(?<=ldflda\s+[^\r\n]*?\s)(?<!')\b([\w\.\-\+<>/]+/on)(?=::)"
    $text = [regex]::Replace($text, $pattern4, {
        param($match)
        $script:totalRepl++
        return "'" + $match.Groups[1].Value + "'"
    }, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    
    # 5. Исправление ldfld инструкций: ldfld type 'Ln/on'::field
    $pattern5 = "(?<=ldfld\s+[^\r\n]*?\s)(?<!')\b([\w\.\-\+<>/]+/on)(?=::)"
    $text = [regex]::Replace($text, $pattern5, {
        param($match)
        $script:totalRepl++
        return "'" + $match.Groups[1].Value + "'"
    }, [System.Text.RegularExpressions.RegexOptions)::IgnoreCase)
    
    # 6. Исправление stfld инструкций: stfld type 'Ln/on'::field  
    $pattern6 = "(?<=stfld\s+[^\r\n]*?\s)(?<!')\b([\w\.\-\+<>/]+/on)(?=::)"
    $text = [regex]::Replace($text, $pattern6, {
        param($match)
        $script:totalRepl++
        return "'" + $match.Groups[1].Value + "'"
    }, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    
    # 7. Исправление generic параметров: <valuetype 'Ln/on'>
    $pattern7 = "(?<=<[^>]*?valuetype\s+)(?<!')\b([\w\.\-\+<>/]+/on)\b(?=[^>]*?>)"
    $text = [regex]::Replace($text, $pattern7, {
        param($match)
        $script:totalRepl++
        return "'" + $match.Groups[1].Value + "'"
    }, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    
    # 8. Исправление call инструкций с generic типами
    $pattern8 = "(?<=call\s+[^\r\n]*?<[^>]*?)(?<!')\b([\w\.\-\+<>/]+/on)\b(?=[^>]*?>)"
    $text = [regex]::Replace($text, $pattern8, {
        param($match)
        $script:totalRepl++
        return "'" + $match.Groups[1].Value + "'"
    }, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    
    # 9. Исправление locals init объявлений
    $pattern9 = "(?<=\.locals\s+init\s*\([^)]*?)(?<!')\b([\w\.\-\+<>/]+/on)\b"
    $text = [regex]::Replace($text, $pattern9, {
        param($match)
        $script:totalRepl++
        return "'" + $match.Groups[1].Value + "'"
    }, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    
    Write-Host "Применено $totalRepl исправлений" -ForegroundColor Cyan
    return @($text, $totalRepl)
}

function Create-Diagnostic-Report([string]$filePath, [int]$attempt) {
    $diagFile = "diagnostics_try$attempt.txt"
    
    Write-Host "Создаю диагностический отчёт..." -ForegroundColor Yellow
    
    $report = @()
    $report += "=== ДИАГНОСТИЧЕСКИЙ ОТЧЁТ (попытка $attempt) ==="
    $report += "Время: $(Get-Date)"
    $report += "Файл: $filePath"
    $report += ""
    
    # Поиск всех строк с '/on'
    $lines = Get-Content -Path $filePath -Encoding Default
    $lineNum = 0
    $foundLines = @()
    
    foreach ($line in $lines) {
        $lineNum++
        if ($line -match "/on") {
            $foundLines += [PSCustomObject]@{
                LineNumber = $lineNum
                Content = $line.Trim()
            }
        }
    }
    
    $report += "Найдено строк с '/on': $($foundLines.Count)"
    $report += ""
    
    foreach ($found in $foundLines) {
        $report += "Строка $($found.LineNumber): $($found.Content)"
    }
    
    $report += ""
    $report += "=== КОНТЕКСТ ОШИБОК ИЗ ЛОГА ==="
    
    if (Test-Path $log) {
        $errorLines = Get-Content -Path $log | Where-Object { $_ -match "(error|warning|fail)" }
        foreach ($errorLine in $errorLines) {
            $report += $errorLine
        }
    }
    
    $report | Out-File -FilePath $diagFile -Encoding UTF8
    Write-Host "Диагностический отчёт сохранён: $diagFile" -ForegroundColor Green
    return $diagFile
}

# Проверка существования файлов
if (-not (Test-Path $src)) {
    Write-Host "ОШИБКА: Исходный файл не найден: $src" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $ilasm)) {
    Write-Host "ОШИБКА: ILAsm не найден: $ilasm" -ForegroundColor Red
    exit 2
}

# Основной цикл
while ($tries -lt $maxTries) {
    $tries++
    Write-Host "`n--- Попытка #$tries ---" -ForegroundColor Magenta
    
    # Создание резервной копии
    $backup = "$src.bak$tries"
    Copy-Item -Path $src -Destination $backup -Force
    Write-Host "Резервная копия: $backup"
    
    # Запуск ilasm
    Write-Host "Запуск ILAsm..." -ForegroundColor Yellow
    $process = Start-Process -FilePath $ilasm -ArgumentList "$src", "/exe", "/output=$out" -Wait -PassThru -RedirectStandardOutput "$log.stdout" -RedirectStandardError "$log.stderr"
    
    # Объединение вывода
    $stdout = if (Test-Path "$log.stdout") { Get-Content "$log.stdout" } else { @() }
    $stderr = if (Test-Path "$log.stderr") { Get-Content "$log.stderr" } else { @() }
    $combined = $stdout + $stderr
    $combined | Out-File -FilePath $log -Encoding UTF8
    
    # Проверка результата
    $isFailure = $combined -match "\*\*\*\*\* FAILURE \*\*\*\*\*"
    
    if (-not $isFailure -and $process.ExitCode -eq 0) {
        Write-Host "✅ Сборка успешно завершена: $out" -ForegroundColor Green
        
        # Удаление временных файлов
        Remove-Item -Path "$log.stdout" -ErrorAction SilentlyContinue
        Remove-Item -Path "$log.stderr" -ErrorAction SilentlyContinue
        
        exit 0
    }
    
    Write-Host "❌ Обнаружена ошибка сборки. Применяю исправления..." -ForegroundColor Red
    
    # Создание диагностического отчёта
    $diagFile = Create-Diagnostic-Report -filePath $src -attempt $tries
    
    # Чтение и исправление файла
    try {
        $originalContent = Get-Content -Path $src -Raw -Encoding Default
        $result = Apply-Enhanced-On-Patch $originalContent
        $fixedContent = $result[0]
        $replacements = $result[1]
        
        if ($replacements -eq 0) {
            Write-Host "⚠️  Исправления не найдены. Проверьте диагностический отчёт: $diagFile" -ForegroundColor Yellow
            break
        }
        
        # Создание файла различий
        $patchFile = "patch_try$tries.diff"
        $originalLines = $originalContent -split "`r?`n"
        $fixedLines = $fixedContent -split "`r?`n"
        
        $diff = Compare-Object -ReferenceObject $originalLines -DifferenceObject $fixedLines -IncludeEqual
        $diffReport = @()
        $diffReport += "=== ПАТЧ (попытка $tries) ==="
        $diffReport += "Применено исправлений: $replacements"
        $diffReport += ""
        
        foreach ($line in $diff) {
            switch ($line.SideIndicator) {
                "<=" { $diffReport += "- $($line.InputObject)" }
                "=>" { $diffReport += "+ $($line.InputObject)" }
            }
        }
        
        $diffReport | Out-File -FilePath $patchFile -Encoding UTF8
        Write-Host "Файл различий: $patchFile" -ForegroundColor Cyan
        
        # Сохранение исправленного файла
        $fixedContent | Set-Content -Path $src -Encoding Default
        Write-Host "Исправленный файл сохранён" -ForegroundColor Green
        
    } catch {
        Write-Host "ОШИБКА при обработке файла: $_" -ForegroundColor Red
        break
    }
    
    # Проверка таймаута
    $elapsed = (Get-Date) - $start
    if ($elapsed.TotalSeconds -ge $timeout) {
        Write-Host "⛔ Достигнут таймаут ($timeout сек). Завершение работы." -ForegroundColor Red
        break
    }
    
    # Удаление временных файлов
    Remove-Item -Path "$log.stdout" -ErrorAction SilentlyContinue
    Remove-Item -Path "$log.stderr" -ErrorAction SilentlyContinue
}

Write-Host "`n=== ЗАВЕРШЕНИЕ РАБОТЫ ===" -ForegroundColor Magenta
Write-Host "Выполнено попыток: $tries из $maxTries"
Write-Host "Время работы: $((Get-Date) - $start)"
Write-Host "`nПроверьте файлы:"
Write-Host " - $log (лог ошибок)"
Write-Host " - patch_try*.diff (файлы различий)"
Write-Host " - diagnostics_try*.txt (диагностические отчёты)"
Write-Host " - $src.bak* (резервные копии)"

exit 1
