# VHS Tape - AI CLI Installation Demo
# Usage: vhs ai-cli-demo.tape
# Prerequisites: Python 3.9+, pipx in PATH
# Run from the ai-cli project root directory

Output ai-cli-demo.gif

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

# Clear screen
Hide
Type "Clear-Host"
Enter
Sleep 500ms
Show

Sleep 500ms

Type "Write-Host '=== AI CLI - Installation Demo ===' -ForegroundColor Cyan"
Enter
Sleep 1.5s

# Step 1: Check Python version
Type "Write-Host '`n[1/4] Checking Python...' -ForegroundColor Yellow"
Enter
Sleep 500ms

Type "python --version"
Enter
Sleep 2s

# Step 2: Install ai-cli with pipx
Type "Write-Host '`n[2/4] Installing ai-cli...' -ForegroundColor Yellow"
Enter
Sleep 500ms

Type "pipx install -e . --force"
Enter
Sleep 30s

# Step 3: Inject Groq plugin
Type "Write-Host '`n[3/4] Adding Groq LLM plugin...' -ForegroundColor Yellow"
Enter
Sleep 500ms

Type "pipx inject ai-cli llm-groq"
Enter
Sleep 20s

# Step 4: Verify installation
Type "Write-Host '`n[4/4] Verifying installation...' -ForegroundColor Yellow"
Enter
Sleep 500ms

Type "ai --version"
Enter
Sleep 2s

Type "ai --check"
Enter
Sleep 3s

# Done
Type "Write-Host '`n=== Installation Complete! ===' -ForegroundColor Green"
Enter
Sleep 2s
