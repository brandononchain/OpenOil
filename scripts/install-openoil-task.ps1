# Registers OpenOil to start at boot, after MetaTrader has time to open.
# Run in an elevated PowerShell on the same Windows machine as the terminal:
#   powershell -ExecutionPolicy Bypass -File scripts\install-openoil-task.ps1 -WorkDir C:\Users\Administrator\OpenOil-main

param(
    [string]$WorkDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$python = (Get-Command python -ErrorAction Stop).Source
$action = New-ScheduledTaskAction -Execute $python -Argument "-m openoil.main" -WorkingDirectory $WorkDir
$trigger = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = "PT90S"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Days 365)
Register-ScheduledTask -TaskName "OpenOil" -Action $action -Trigger $trigger -Settings $settings -User $env:USERNAME -RunLevel Highest -Force | Out-Null
Write-Output "Scheduled task OpenOil registered."
Write-Output "Python: $python"
Write-Output "Folder: $WorkDir"
Write-Output "It starts 90 seconds after boot. Open MetaTrader first, or start the terminal from its own startup task."
Write-Output "Railway cannot reach 127.0.0.1:22346. Leave this task on the VPS."
