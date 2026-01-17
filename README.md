# AI CLI

A versatile terminal AI assistant powered by LLMs, featuring command execution, rich markdown rendering, and context memory.

## Features

- **Conversational Memory**: proper context retention with `-c` flag.
- **Auto-Copy**: Responses are automatically copied to the clipboard.
- **Integrated Tools**: The model can execute system commands (ls, cat, tree, find, git).
- **Rich Rendering**: Beautiful Markdown output with syntax highlighting and panels.
- **Live Streaming**: Real-time response generation.
- **Dynamic Models**: Easily add, switch, and manage different LLM backends.

## Installation

```bash
# Local development
pip install -e .

# Requires llm CLI installed
pip install llm
```

## Usage

### Basic Interaction

```bash
ai "hello, how are you?"        # Simple query
ai -m fast "what time is it?"   # Use specific model
ai -c "explain more"            # Continue previous conversation
```

### File Analysis

```bash
ai file README.md "summarize this"   # Analyze file
ai explain main.py                   # Explain code
cat log.txt | ai "what is this error?" # Pipe input
```

### Exploration Tools

```bash
ai tree                        # Project structure
ai find "def main"             # Search with ripgrep
ai fzf                         # Interactive fuzzy finder
```

### Model Management

```bash
ai model                       # Interactive menu
ai model list                  # List all models
ai model set fast              # Set default model
ai model add mygpt gpt-4 "Desc"# Add custom model
ai model current               # Show current model
```

## Built-in Models

| Alias | Model | Description |
|-------|-------|-------------|
| `maverick` | Llama 4 Maverick 17B | General purpose (default) |
| `fast` | Llama 3.3 70B | Fast + High Quality |
| `quick` | Llama 3.1 8B | Ultra-fast |
| `qwen` | Qwen3 32B | Python/JS Coding |
| `web` | Compound | Web search + tools |

## Main Options

```
-m, --model ALIAS    Model to use
-c, --continue       Continue previous conversation
-v, --verbose        Verbose mode
-V, --version        Show version
-h, --help           Show help
```

## Auto-Copy

Every response is automatically copied to your clipboard for quick usage.
A confirmation indicator (💾 Copied) appears at the bottom of the response panel.

## Optional Dependencies

- **ripgrep (rg)**: For `ai find` (falls back to findstr on Windows).
- **fzf**: For `ai fzf`.

## Configuration

Configuration is stored at:
- **Windows**: `%APPDATA%\ai-cli\config.json`
- **Linux/Mac**: `~/.config/ai-cli/config.json`

## License

MIT
