# build_il_on_fix.ps1
$src = "C.il"
$out = "Laitis-rebuilt.exe"
$ilasm = "C:\Windows\Microsoft.NET\Framework\v4.0.30319\ilasm.exe"
$log = "errors.log"
$maxTries = 50
$timeout = 300   # seconds

Write-Host "Start build_il_on_fix.ps1 (focus: 'on')"
$start = Get-Date
$tries = 0

function Apply-On-Patch([string]$text) {
    # 1) Quote occurrences like:  Ln/on::field  =>  'Ln/on'::field
    $text = [regex]::Replace($text,
        '([^\s:]+/on)::',
        { param($m) "'" + $m.Groups[1].Value + "'::" })

    # 2) Quote ".class ... beforefieldinit on" -> ".class ... beforefieldinit 'on'"
    $text = [regex]::Replace($text,
        '(\.class\b[^\r\n]*?\bbeforefieldinit\s+)(on)\b',
        { param($m) $m.Groups[1].Value + "'" + $m.Groups[2].Value + "'" },
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)

    return $text
}

while ($tries -lt $maxTries) {
    $tries++
    Write-Host "`n=== Attempt #$tries ==="

    # backup
    $backup = "$src.bak$tries"
    Copy-Item -Path $src -Destination $backup -Force
    Write-Host "Backup saved: $backup"

    # run ilasm and capture output
    & $ilasm $src /exe /output=$out 2>&1 | Tee-Object -FilePath $log

    # if no FAILURE — success
    if (-not (Select-String -SimpleMatch "***** FAILURE *****" -Path $log -Quiet)) {
        Write-Host "✅ Build succeeded: $out"
        exit 0
    }

    Write-Host "❌ FAILURE detected, trying apply 'on' fixes..."

    # read original file as single string (use Default encoding to match original)
    $orig = Get-Content -Path $src -Raw -Encoding Default

    # apply targeted patch
    $fixed = Apply-On-Patch $orig

    if ($orig -eq $fixed) {
        Write-Host "ℹ️  No replacements were made for pattern 'on' (nothing to change)."
        # save diagnostics: lines with "/on" and some context
        $diagFile = "diagnostics_try$tries.txt"
        Select-String -Path $src -Pattern "/on" -SimpleMatch -Context 3,3 | Out-File $diagFile -Encoding UTF8
        Write-Host "Diagnostics saved to: $diagFile"
        Write-Host "I stop here so you can inspect diagnostics. If you want, paste diagnostics_try$tries.txt here."
        exit 1
    }
    else {
        # save diff so we see what changed
        $origLines = $orig -split "`r?`n"
        $fixedLines = $fixed -split "`r?`n"
        $diff = Compare-Object -ReferenceObject $origLines -DifferenceObject $fixedLines -SyncWindow 0
        $patchFile = "patch_try$tries.diff"
        $diff | Out-File $patchFile -Encoding UTF8
        Write-Host "Patch applied, diff written to: $patchFile"

        # write fixed content (UTF8)
        $fixed | Set-Content -Path $src -Encoding UTF8

        Write-Host "Re-running ilasm..."
    }

    # timeout
    if (((Get-Date) - $start).TotalSeconds -ge $timeout) {
        Write-Host "⛔ Timeout ($timeout seconds) reached. Stopping."
        break
    }
}

Write-Host "Finished loop. See $log, patch_try*.diff and diagnostics_try*.txt"
exit 1
