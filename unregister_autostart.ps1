# Removes the AdScript bot autostart task.
# Usage: powershell -ExecutionPolicy Bypass -File unregister_autostart.ps1

$ErrorActionPreference = "Stop"
$TaskName = "AdScriptBot"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed task '$TaskName'."
} else {
    Write-Host "No task named '$TaskName' found."
}
