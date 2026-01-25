# AI CLI

A versatile terminal AI assistant powered by LLMs, featuring command execution, rich markdown rendering, and context memory.

## Features

- **Conversational Memory**: Proper context retention with `-c` flag
- **Auto-Copy**: Responses automatically copied to clipboard
- **Integrated Tools**: Execute system commands (ls, cat, tree, find, git)
- **Rich Rendering**: Beautiful minimal TUI with syntax highlighting
- **Live Streaming**: Real-time response with spinner animation
- **Dynamic Models**: Easily add, switch, and manage different LLM backends

## Requirements

- **Python 3.9+**
- **llm CLI** (Simon Willison's LLM tool)

## Installation

### 1. Install LLM CLI

The AI CLI depends on Simon Willison's excellent `llm` tool:

```bash
pip install llm
```

### 2. Configure Your LLM Provider

You need at least one LLM provider configured. **Free local options are recommended for getting started.**

#### Option A: Ollama (FREE - Recommended)

Run powerful models locally on your computer at no cost:

```bash
# 1. Install Ollama from https://ollama.ai
# 2. Pull a model (examples below)

# Recommended models:
ollama pull llama3.2          # 3B - Fast, good for quick tasks
ollama pull qwen2.5-coder     # 7B - Excellent for coding
ollama pull mistral           # 7B - Great general purpose
ollama pull deepseek-r1:8b    # 8B - Strong reasoning

# 3. Install llm-ollama plugin
llm install llm-ollama

# 4. Test it
llm -m llama3.2 "Hello"
```

**Advantages**: Free, private, works offline, no API keys needed.

#### Option B: OpenAI (Paid)

```bash
llm keys set openai
# Paste your OpenAI API key

# Test it
llm -m gpt-4o-mini "Hello"
```

**Cost**: ~$0.15-$15 per 1M tokens depending on model.

#### Option C: Anthropic Claude (Paid)

```bash
llm install llm-claude-3
llm keys set claude
# Paste your Anthropic API key

# Test it
llm -m claude-3-5-sonnet-latest "Hello"
```

**Cost**: ~$3-$15 per 1M tokens depending on model.

#### Option D: Other Free Options

```bash
# Google Gemini (Free tier available)
llm install llm-gemini
llm keys set gemini

# Groq (Free tier with fast inference)
llm install llm-groq
llm keys set groq
```

See [llm documentation](https://llm.datasette.io/) for more providers.

### 3. Install AI CLI

```bash
# Clone the repository
git clone https://github.com/mediaweb-global/cli-ai.git
cd cli-ai

# Install in development mode
pip install -e .

# Verify installation
ai --version
```

## Configuration

### First Run Setup

On first run, AI CLI creates a configuration file:

- **Windows**: `%APPDATA%\ai-cli\config.json`
- **Linux/macOS**: `~/.config/ai-cli/config.json`

### Configure Models

AI CLI comes with preconfigured model aliases. Add your models:

```bash
# Interactive model management
ai model

# Add a custom model
ai model add mymodel gpt-4o "My GPT-4o model"

# Set default model
ai model set mymodel

# List all configured models
ai model list
```

### Model Configuration File

Edit `config.json` to customize models:

```json
{
  "default_model": "maverick",
  "models": {
    "maverick": {
      "model_id": "maverick",
      "description": "Llama 4 Maverick 17B - Uso geral"
    },
    "fast": {
      "model_id": "fast",
      "description": "Llama 3.3 70B - Rápido + qualidade"
    },
    "quick": {
      "model_id": "quick",
      "description": "Llama 3.1 8B - Ultra-rápido"
    },
    "qwen": {
      "model_id": "qwen",
      "description": "Qwen3 32B - Código Python/JS"
    },
    "web": {
      "model_id": "web",
      "description": "Compound - Web search + tools"
    }
  }
}
```

**Built-in Models:**
- `maverick` - Llama 4 Maverick 17B - Uso geral (default)
- `fast` - Llama 3.3 70B - Rápido + qualidade (280 tokens/s)
- `quick` - Llama 3.1 8B - Ultra-rápido (560 tokens/s)
- `qwen` - Qwen3 32B - Código Python/JS (400 tokens/s)
- `web` - Compound - Web search + tools (450 tokens/s)

## Usage

### Basic Queries (No quotes needed!)

```bash
# Simple question - NO QUOTES NEEDED
ai what is the capital of France

# Multi-word queries - NO QUOTES NEEDED  
ai explain quantum computing in simple terms

# Use specific model
ai -m code write a quicksort function
```

### System Commands (with --)

```bash
ai --help              # Show help
ai --version           # Show version
ai --config            # Show configuration
ai --models            # List available models
ai --check             # Check system status
```

### Aliases (Shortcuts)

Save typing with built-in aliases:

```bash
ai f README.md summarize   # Same as: ai file
ai e main.py               # Same as: ai explain
ai t                       # Same as: ai tree
ai s TODO                  # Same as: ai find (search)
```

### Continue Conversations

```bash
# First message
ai explain neural networks

# Continue the conversation (keeps context)
ai -c give me a code example

# Keep going
ai -c explain that in more detail
```

### File Analysis

```bash
# Analyze a file
ai file README.md summarize this file

# Explain code
ai explain src/main.py

# Pipe input
cat error.log | ai what caused this error
echo def hello pass | ai improve this code
```

### Integrated Tools

The AI can execute safe commands when needed:

```bash
# AI can list files
ai show me python files in this directory

# AI can read files
ai what does config.json contain

# AI can check git status
ai what files have changed

# AI can search for patterns
ai find all TODO comments
```

### Direct Tools (Advanced)

```bash
# Project structure
ai tree

# Search with ripgrep
ai find def main

# Interactive file finder
ai fzf
```

### Model Management

```bash
# List all available models
ai --models

# Interactive model menu
ai model

# Show current model
ai model current

# Set default model
ai model set local

# Add new model
ai model add mymodel llama3.2 "My custom model"

# Remove model
ai model remove mymodel
```

### System Commands

```bash
# Check system status
ai check            # Verifies llm installation, models, config

# View configuration
ai config           # Shows current config.json

# Disable streaming (show complete output at once)
ai --no-stream "explain this in detail"
```

## Command Reference

### Main Command

```
ai [OPTIONS] [QUERY]
```

**Options:**
- `-m, --model MODEL` - Specify model to use
- `-c, --continue` - Continue previous conversation
- `-v, --verbose` - Show detailed output
- `--no-stream` - Disable streaming (show complete output)
- `-V, --version` - Show version
- `-h, --help` - Show help message

### Commands

- `ai check` - Verify system state (llm installation, models, config)
- `ai config` - Show/edit configuration
- `ai file <path> [query]` - Analyze file(s)
- `ai explain <path>` - Explain code file
- `ai find <pattern>` - Search patterns with ripgrep
- `ai fzf` - Interactive fuzzy file finder
- `ai model` - Model management (interactive)
- `ai models` - List available models
- `ai tree` - Show directory structure

### Aliases

- `ai f` → `ai file`
- `ai e` → `ai explain`
- `ai m` → `ai models`
- `ai t` → `ai tree`
- `ai s` → `ai find`

### Model Subcommands

- `ai model list` - List all configured models
- `ai model current` - Show current default model
- `ai model set <alias>` - Set default model
- `ai model add <alias> <id> <desc>` - Add new model
- `ai model remove <alias>` - Remove model

## Features in Detail

### Auto-Copy to Clipboard

Every response is automatically copied to your clipboard for quick usage. You'll see a confirmation:

```
λ ai-cli • 2.3s ────────────────────────────────────────────────────────────────

  [AI response here]

∴ copiado para clipboard ──────────────────────────────────────────────────────
```

### Rich Terminal UI

- **Clean Layout**: Minimal 80-character width design
- **Syntax Highlighting**: Code blocks with language detection
- **Markdown Support**: Headers, lists, tables, quotes
- **Path Detection**: Automatically highlights file paths
- **Color Themes**: Cyan/blue aesthetic optimized for readability

### Context Memory

Use `-c` to maintain conversation context:

```bash
ai "I'm learning Python"          # First message
ai -c "recommend some resources"  # AI remembers you're learning Python
ai -c "what about web frameworks?" # AI knows the context
```

### System Integration

The AI can execute safe, read-only commands when helpful:

- `ls` / `dir` - List files
- `cat` / `type` - Read files
- `pwd` - Current directory
- `git status` - Git information
- `tree` - Directory structure
- `find` / `grep` - Search

**Note**: Commands are only executed when explicitly needed by the AI's reasoning. You control when tools run.

## Troubleshooting

### "llm: command not found"

Install the llm CLI tool:

```bash
pip install llm
```

### "No API key configured"

Set up your LLM provider:

```bash
# For OpenAI
llm keys set openai

# For Claude
llm install llm-claude-3
llm keys set claude

# For local models
ollama pull llama3.2
llm install llm-ollama
```

### "Model not found"

Check available models:

```bash
# List llm models
llm models

# List ai-cli configured models
ai model list
```

Then add your model:

```bash
ai model add mymodel <model-id> "Description"
ai model set mymodel
```

### Clipboard not working

**Windows**: Should work out of the box with `clip.exe`

**macOS**: Should work with `pbcopy`

**Linux**: Install `xclip` or `xsel`:

```bash
# Ubuntu/Debian
sudo apt install xclip

# Fedora
sudo dnf install xclip

# Arch
sudo pacman -S xclip
```

### Unicode characters not displaying

Make sure you're using a modern terminal:
- **Windows**: Windows Terminal (recommended)
- **macOS**: Terminal.app or iTerm2
- **Linux**: GNOME Terminal, Konsole, or Alacritty

## Optional Dependencies

Enhance functionality with these optional tools:

- **ripgrep (rg)**: Fast search for `ai find` command
  ```bash
  # Windows: winget install BurntSushi.ripgrep.MSVC
  # macOS: brew install ripgrep
  # Linux: sudo apt install ripgrep
  ```

- **fzf**: Interactive fuzzy finder for `ai fzf`
  ```bash
  # Windows: winget install fzf
  # macOS: brew install fzf
  # Linux: sudo apt install fzf
  ```

- **tree**: Directory structure visualization
  ```bash
  # Usually pre-installed on most systems
  # Windows: built-in (tree /F)
  ```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/mediaweb-global/cli-ai.git
cd cli-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Project Structure

```
cli-ai/
├── src/
│   └── ai_cli/
│       ├── __init__.py
│       ├── main.py         # CLI entry point
│       ├── config.py       # Configuration management
│       ├── llm_client.py   # LLM interaction
│       ├── render.py       # Terminal rendering
│       └── tools/          # Integrated tools
│           ├── find.py
│           ├── fzf.py
│           ├── tree.py
│           └── safe_commands.py
├── tests/
├── pyproject.toml
├── README.md
└── LICENSE
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Configuration

Configuration is stored at:
- **Windows**: `%APPDATA%\ai-cli\config.json`
- **Linux/Mac**: `~/.config/ai-cli/config.json`

