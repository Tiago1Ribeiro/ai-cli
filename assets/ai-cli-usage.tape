# VHS Tape - AI CLI Usage Examples
# Usage: vhs ai-cli-usage.tape

Output ai-cli-usage.gif
Output ai-cli-usage.mp4

Set Theme "Catppuccin Mocha"
Set FontFamily "Cascadia Code"
Set FontSize 16
Set Width 1200
Set Height 800
Set Padding 20
Set TypingSpeed 50ms
Set PlaybackSpeed 2.5

# Load API key silently
Hide
Type "for /f %a in (.env) do set %a"
Enter
Sleep 2s
Type "cls"
Enter
Show

Sleep 500ms

# --- Version ---
Type "ai --version"
Enter
Sleep 3s

# --- Models ---
Type "ai --models"
Enter
Sleep 5s

# --- Health Check ---
Type "ai --check"
Enter
Sleep 4s

# --- Real query ---
Type "ai what is the capital of Portugal"
Enter
Sleep 15s

# --- Continue conversation ---
Type "ai -c and Spain"
Enter
Sleep 15s

# --- File analysis ---
Type "ai file pyproject.toml summarize this"
Enter
Sleep 20s

# --- Done ---
Type "echo."
Enter
Type "echo Done."
Enter
Sleep 2s
