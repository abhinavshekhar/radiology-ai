$projectRoot = Split-Path -Parent $PSScriptRoot
$launcher = Join-Path $projectRoot "launch.bat"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Radiology AI.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $launcher
$Shortcut.WorkingDirectory = $projectRoot
$Shortcut.WindowStyle = 7
$Shortcut.Description = "Start Radiology AI Assistant (Docker)"
$Shortcut.IconLocation = "$env:SystemRoot\System32\imageres.dll,109"
$Shortcut.Save()

Write-Host "Desktop shortcut created:"
Write-Host "  $shortcutPath"
