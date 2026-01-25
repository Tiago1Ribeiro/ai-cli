# AI CLI

Assistente de IA versátil para terminal, alimentado por LLMs, com execução de comandos, renderização rica de markdown e memória de contexto.

![alt text](image.png)

## Características

- **Memória de Conversação**: Retenção adequada de contexto com flag `-c`
- **Cópia Automática**: Respostas automaticamente copiadas para clipboard
- **Ferramentas Integradas**: Executa comandos do sistema (ls, cat, tree, find, git)
- **Renderização Rica**: TUI minimalista e bonita com syntax highlighting
- **Streaming em Direto**: Resposta em tempo real com animação
- **Modelos Dinâmicos**: Adiciona, alterna e gere facilmente diferentes backends LLM

## Requisitos

- **Python 3.9+**
- **llm CLI** (ferramenta LLM de Simon Willison)

## Instalação

### 1. Instalar LLM CLI

O AI CLI depende da excelente ferramenta `llm` de Simon Willison:

```bash
pip install llm
```

### 2. Configurar o Fornecedor de LLM

Precisas de pelo menos um fornecedor de LLM configurado. **Opções locais gratuitas são recomendadas para começar.**

#### Opção A: Ollama (GRÁTIS - Recomendado)

Executa modelos poderosos localmente no teu computador sem custos:

```bash
# 1. Instalar Ollama de https://ollama.ai
# 2. Fazer pull de um modelo (exemplos abaixo)

# Modelos recomendados:
ollama pull llama3.2          # 3B - Rápido, bom para tarefas rápidas
ollama pull qwen2.5-coder     # 7B - Excelente para código
ollama pull mistral           # 7B - Ótimo para uso geral
ollama pull deepseek-r1:8b    # 8B - Raciocínio forte

# 3. Instalar plugin llm-ollama
llm install llm-ollama

# 4. Testar
llm -m llama3.2 "Olá"
```

**Vantagens**: Grátis, privado, funciona offline, não precisa de API keys.

#### Opção B: OpenAI (Pago)

```bash
llm keys set openai
# Cola a tua OpenAI API key

# Testar
llm -m gpt-4o-mini "Olá"
```

**Custo**: ~$0.15-$15 por 1M tokens dependendo do modelo.

#### Opção C: Anthropic Claude (Pago)

```bash
llm install llm-claude-3
llm keys set claude
# Cola a tua Anthropic API key

# Testar
llm -m claude-3-5-sonnet-latest "Olá"
```

**Custo**: ~$3-$15 por 1M tokens dependendo do modelo.

#### Opção D: Outras Opções Grátis

```bash
# Google Gemini (Tier gratuito disponível)
llm install llm-gemini
llm keys set gemini

# Groq (Tier gratuito com inferência rápida)
llm install llm-groq
llm keys set groq
```

Vê a [documentação llm](https://llm.datasette.io/) para mais fornecedores.

### 3. Instalar AI CLI

```bash
# Clonar o repositório
git clone https://github.com/mediaweb-global/cli-ai.git
cd cli-ai

# Instalar em modo de desenvolvimento
pip install -e .

# Verificar instalação
ai --version
```

## Configuração

### Configuração Inicial

Na primeira execução, AI CLI cria um ficheiro de configuração:

- **Windows**: `%APPDATA%\ai-cli\config.json`
- **Linux/macOS**: `~/.config/ai-cli/config.json`

### Configurar Modelos

AI CLI vem com aliases de modelos pré-configurados. Adiciona os teus modelos:

```bash
# Gestão interativa de modelos
ai model

# Adicionar um modelo personalizado
ai model add mymodel gpt-4o "O meu modelo GPT-4o"

# Definir modelo padrão
ai model set mymodel

# Listar todos os modelos configurados
ai model list
```

### Ficheiro de Configuração de Modelos

Edita `config.json` para personalizar modelos:

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

**Modelos Incluídos:**
- `maverick` - Llama 4 Maverick 17B - Uso geral (padrão)
- `fast` - Llama 3.3 70B - Rápido + qualidade (280 tokens/s)
- `quick` - Llama 3.1 8B - Ultra-rápido (560 tokens/s)
- `qwen` - Qwen3 32B - Código Python/JS (400 tokens/s)
- `web` - Compound - Web search + tools (450 tokens/s)

## Uso

### Queries Básicas (Sem aspas!)

```bash
# Pergunta simples - SEM ASPAS
ai qual é a capital de França

# Queries multi-palavra - SEM ASPAS
ai explica computação quântica em termos simples

# Usar modelo específico
ai -m code escreve uma função quicksort
```

### Comandos do Sistema (com --)

```bash
ai --help              # Mostrar ajuda
ai --version           # Mostrar versão
ai --config            # Mostrar configuração
ai --models            # Listar modelos disponíveis
ai --check             # Verificar estado do sistema
```

### Aliases (Atalhos)

Poupa tempo com aliases integrados:

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

