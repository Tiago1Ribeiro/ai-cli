# VHS Tape - AI CLI Usage Examples (Complete)
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

# === SECTION 1: Basic Commands ===
Type "echo === Basic Commands ==="
Enter
Sleep 1s

Type "ai --version"
Enter
Sleep 3s

Type "ai --models"
Enter
Sleep 5s

Type "ai --check"
Enter
Sleep 4s

# === SECTION 2: Simple Queries ===
Type "cls"
Enter
Type "echo === Simple Queries ==="
Enter
Sleep 1s

Type "ai what is the capital of Portugal"
Enter
Sleep 15s

Type "ai -c and the population"
Enter
Sleep 15s

# === SECTION 3: New Conversation ===
Type "cls"
Enter
Type "echo === New Conversation ==="
Enter
Sleep 1s

Type "ai -n explain REST API in one sentence"
Enter
Sleep 15s

# === SECTION 4: File Operations ===
Type "cls"
Enter
Type "echo === File Analysis ==="
Enter
Sleep 1s

Type "ai file pyproject.toml what are the main dependencies"
Enter
Sleep 18s

Type "ai explain src\ai_cli\config.py"
Enter
Sleep 20s

# === SECTION 5: Project Structure ===
Type "cls"
Enter
Type "echo === Project Tools ==="
Enter
Sleep 1s

Type "ai tree"
Enter
Sleep 8s

# === SECTION 6: Pipe Input ===
Type "cls"
Enter
Type "echo === Pipe Input ==="
Enter
Sleep 1s

Type "echo def hello(): pass | ai improve this code"
Enter
Sleep 18s

# === SECTION 7: Different Model ===
Type "cls"
Enter
Type "echo === Using Different Model ==="
Enter
Sleep 1s

Type "ai -m fast tell me a fun fact about Python"
Enter
Sleep 15s

# === Done ===
Type "cls"
Enter
Type "echo."
Enter
Type "echo === Demo Complete ==="
Enter
Type "echo."
Enter
Type "echo Try: ai your question here"
Enter
Sleep 3s
