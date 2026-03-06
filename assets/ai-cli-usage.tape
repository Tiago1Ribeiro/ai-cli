# VHS Tape - AI CLI Usage Examples
# Usage: vhs ai-cli-usage.tape
# Prerequisites: ai-cli installed, API key configured

Output ai-cli-usage.gif

Set Theme "Catppuccin Mocha"
Set FontFamily "Cascadia Code"
Set FontSize 16
Set Width 1200
Set Height 700
Set Padding 20
Set TypingSpeed 40ms
Set PlaybackSpeed 2

# Use PowerShell on Windows
Set Shell "pwsh"

# Load API key silently and clear screen
Hide
Type "Get-Content .env | ForEach-Object { if ($_ -match '^([^#].+?)=(.+)$') { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2]) } }"
Enter
Sleep 1s
Type "Clear-Host"
Enter
Sleep 500ms
Show

Sleep 500ms

# === SECTION 1: Version & Help ===
Type "Write-Host '=== AI CLI - Usage Examples ===' -ForegroundColor Cyan"
Enter
Sleep 1s

Type "ai --version"
Enter
Sleep 2s

Type "ai --help"
Enter
Sleep 4s

# === SECTION 2: System Check ===
Type "Clear-Host"
Enter
Sleep 300ms
Type "Write-Host '=== System Check ===' -ForegroundColor Cyan"
Enter
Sleep 1s

Type "ai --check"
Enter
Sleep 3s

Type "ai --config"
Enter
Sleep 3s

# === SECTION 3: List Models ===
Type "Clear-Host"
Enter
Sleep 300ms
Type "Write-Host '=== Available Models ===' -ForegroundColor Cyan"
Enter
Sleep 1s

Type "ai --models"
Enter
Sleep 4s

# === SECTION 4: Simple Query ===
Type "Clear-Host"
Enter
Sleep 300ms
Type "Write-Host '=== Simple Query ===' -ForegroundColor Cyan"
Enter
Sleep 1s

Type "ai what is the capital of Portugal"
Enter
Sleep 15s

# === SECTION 5: Continue Conversation ===
Type "Write-Host '`n=== Continue Conversation ===' -ForegroundColor Cyan"
Enter
Sleep 1s

Type "ai -c and the population"
Enter
Sleep 15s

# === SECTION 6: File Analysis ===
Type "Clear-Host"
Enter
Sleep 300ms
Type "Write-Host '=== File Analysis ===' -ForegroundColor Cyan"
Enter
Sleep 1s

Type "ai file pyproject.toml summarize this project"
Enter
Sleep 15s

# === Done ===
Type "Clear-Host"
Enter
Sleep 300ms
Type "Write-Host '=== Demo Complete ===' -ForegroundColor Green"
Enter
Type "Write-Host 'Try it: ai your question here' -ForegroundColor Yellow"
Enter
Sleep 3s
