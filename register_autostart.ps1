# Registers the AdScript bot to start hidden at logon via Task Scheduler.
# Reversible: run unregister_autostart.ps1
# Usage: powershell -ExecutionPolicy Bypass -File register_autostart.ps1

$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TaskName   = "AdScriptBot"
$BotScript  = Join-Path $ProjectDir "bot.py"

$PythonW = "C:\Users\bilel\AppData\Local\Programs\Python\Python312\pythonw.exe"
if (-not (Test-Path $PythonW)) {
    $PythonW = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
}
if (-not $PythonW) { throw "pythonw.exe not found. Edit `$PythonW at the top of this script." }
if (-not (Test-Path $BotScript)) { throw "bot.py not found at $BotScript" }

$action = New-ScheduledTaskAction -Execute $PythonW -Argument "bot.py" -WorkingDirectory $ProjectDir
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero)
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Force | Out-Null

Write-Host "Registered task '$TaskName' to run at logon."
Write-Host "Python : $PythonW"
Write-Host "Script : $BotScript"
Write-Host "Log    : $(Join-Path $ProjectDir 'bot.log')"
Write-Host ""
Write-Host "Start it now without rebooting:  Start-ScheduledTask -TaskName $TaskName"
