# VHS Tape - AI CLI Some Usage Examples 
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
Set PlaybackSpeed 1.5

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

Type "ai --check"
Enter
Sleep 4s

# === SECTION 2: Simple Queries ===
Type "cls"
Enter
Type "echo === Simple Queries ==="
Enter
Sleep 1s

Type "ai qual e a capital de Portugal"
Enter
Sleep 15s

Type "ai -c e a populacao"
Enter
Sleep 15s

# === SECTION 3: New Conversation ===
Type "cls"
Enter
Type "echo === New Conversation ==="
Enter
Sleep 1s

Type "ai -n explica REST API numa frase"
Enter
Sleep 15s

# === SECTION 4: Pipe Input ===
Type "cls"
Enter
Type "echo === Pipe Input ==="
Enter
Sleep 1s

Type "echo def hello(): pass | ai melhora este codigo"
Enter
Sleep 18s

# === SECTION 5: Different Model ===
Type "cls"
Enter
Type "echo === Using Different Model ==="
Enter
Sleep 1s

Type "ai -m quick tempo em Lisboa amanha"
Enter
Sleep 18s

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
