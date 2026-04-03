# Memory Check Script
Write-Host "=== Memory Usage Report ===" -ForegroundColor Cyan

# Get memory info
$os = Get-CimInstance Win32_OperatingSystem
$totalGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$usedGB = $totalGB - $freeGB
$usagePercent = [math]::Round(($usedGB / $totalGB) * 100, 2)

Write-Host "`nTotal Memory: $totalGB GB"
Write-Host "Used: $usedGB GB"
Write-Host "Available: $freeGB GB"
$color = if($usagePercent -gt 80){"Red"} elseif($usagePercent -gt 70){"Yellow"} else{"Green"}
Write-Host "Usage: $usagePercent %" -ForegroundColor $color

Write-Host "`n=== Top Memory Processes ===" -ForegroundColor Cyan

# Get top processes
$processes = Get-Process | Sort-Object WS -Descending | Select-Object -First 15
foreach ($p in $processes) {
    $memMB = [math]::Round($p.WS / 1MB, 2)
    Write-Host ($p.Name.PadRight(30) + $memMB.ToString().PadLeft(8) + " MB")
}

Write-Host "`n=== Anomaly Detection ===" -ForegroundColor Cyan

# Check for high memory processes
$highMem = $processes | Where-Object { $_.WS / 1MB -gt 500 }
if ($highMem) {
    Write-Host "WARNING: Processes using >500MB:" -ForegroundColor Yellow
    foreach ($p in $highMem) {
        Write-Host ("  " + $p.Name + ": " + [math]::Round($p.WS/1MB,2) + " MB")
    }
} else {
    Write-Host "No single process using >500MB" -ForegroundColor Green
}

# Overall usage check
if ($usagePercent -gt 85) {
    Write-Host "`nWARNING: Memory usage >85%, consider checking" -ForegroundColor Red
} elseif ($usagePercent -gt 70) {
    Write-Host "`nNOTICE: Memory usage >70%, elevated level" -ForegroundColor Yellow
} else {
    Write-Host "`nOK: Memory usage normal" -ForegroundColor Green
}

Write-Host "`n=== Suggestions ===" -ForegroundColor Cyan
Write-Host "1. If memory usage >80%, close unnecessary programs"
Write-Host "2. Check for unknown processes"
Write-Host "3. Use Task Manager for details"
Write-Host "4. Restart to free memory"