# VHS Tape - AI CLI Real Installation Demo
# Usage: vhs ai-cli-demo.tape
# Prerequisites: pipx in PATH, .env with GROQ_API_KEY

Output ai-cli-demo.gif
Output ai-cli-demo.mp4

Set Theme "Catppuccin Mocha"
Set FontFamily "Cascadia Code"
Set FontSize 16
Set Width 1200
Set Height 800
Set Padding 20
Set TypingSpeed 40ms
Set PlaybackSpeed 2.0

# Clear screen
Hide
Type "cls"
Enter
Show

Sleep 1s

Type "echo === AI CLI - Real Installation Demo ==="
Enter
Sleep 2s

# Step 1: Uninstall existing installation
Type "echo."
Enter
Type "echo [1/6] Removing previous ai-cli installation..."
Enter
Sleep 500ms

Type "pipx uninstall ai-cli"
Enter
Sleep 15s

# Step 2: Fresh install from source (llm is included as dependency)
Type "echo."
Enter
Type "echo [2/6] Installing ai-cli from source..."
Enter
Sleep 500ms

Type "pipx install -e ."
Enter
Sleep 60s

# Step 3: Inject Groq plugin into ai-cli virtualenv
Type "echo."
Enter
Type "echo [3/6] Adding Groq LLM plugin..."
Enter
Sleep 500ms

Type "pipx inject ai-cli llm-groq"
Enter
Sleep 30s

# Step 4: Load API key from .env file
Type "echo."
Enter
Type "echo [4/6] Loading API key from .env file..."
Enter
Sleep 500ms

Type "for /f %a in (.env) do set %a"
Enter
Sleep 5s

Type "if defined GROQ_API_KEY echo [OK] GROQ_API_KEY is set"
Enter
Sleep 2s

# Step 5: Set default model
Type "echo."
Enter
Type "echo [5/6] Setting default LLM model..."
Enter
Sleep 500ms

Type "llm models default groq/moonshotai/kimi-k2-instruct-0905"
Enter
Sleep 5s

# Step 6: Verify installation
Type "echo."
Enter
Type "echo [6/6] Verifying installation..."
Enter
Sleep 500ms

Type "ai --version"
Enter
Sleep 3s

Type "ai --help"
Enter
Sleep 5s

# Real LLM test
Type "echo."
Enter
Type "echo === Testing with a real LLM call ==="
Enter
Sleep 1s

Type "ai ola mundo"
Enter
Sleep 30s

# Done
Type "echo."
Enter
Type "echo === Done - ai-cli installed and working ==="
Enter
Sleep 3s
