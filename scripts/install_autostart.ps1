# Bot va panelni Windows yonishi bilan (login qilmasdan ham) ishga tushiradi.
# Administrator PowerShell'da:
#   powershell -ExecutionPolicy Bypass -File scripts\install_autostart.ps1
# O'chirish:
#   Unregister-ScheduledTask -TaskName "AIHelp bot","AIHelp panel" -Confirm:$false

$root = Split-Path -Parent $PSScriptRoot

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0) `
    -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$trigger = New-ScheduledTaskTrigger -AtStartup

foreach ($name in "bot", "panel") {
    $action = New-ScheduledTaskAction -Execute "$root\scripts\run_$name.bat" -WorkingDirectory $root
    Register-ScheduledTask -TaskName "AIHelp $name" -Action $action -Trigger $trigger `
        -Settings $settings -Principal $principal -Force | Out-Null
    Start-ScheduledTask -TaskName "AIHelp $name"
    Write-Host "AIHelp $name - o'rnatildi va ishga tushdi"
}
