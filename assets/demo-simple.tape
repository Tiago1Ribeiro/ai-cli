# VHS Tape - AI CLI Quick Overview
# Usage: vhs demo-simple.tape
# A short demo showing ai-cli is installed and working

Output demo-simple.gif

Set Theme "Catppuccin Mocha"
Set FontFamily "Cascadia Code"
Set FontSize 18
Set Width 1200
Set Height 600
Set Padding 20
Set TypingSpeed 50ms
Set PlaybackSpeed 2

# Use PowerShell on Windows
Set Shell "pwsh"

Hide
Type "Clear-Host"
Enter
Sleep 500ms
Show

Sleep 500ms

Type "Write-Host '=== AI CLI - Quick Overview ===' -ForegroundColor Cyan"
Enter
Sleep 1s

# Show version
Type "ai --version"
Enter
Sleep 2s

# Show help (brief)
Type "ai --help"
Enter
Sleep 4s

# System check
Type "ai --check"
Enter
Sleep 3s

# Done
Type "Write-Host '`nReady to use: ai your question here' -ForegroundColor Green"
Enter
Sleep 2s
