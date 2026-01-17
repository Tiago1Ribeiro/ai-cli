# 🤖 AI CLI

Assistente de IA versátil no terminal com modelos LLM, execução de comandos e renderização markdown.

## ✨ Features

- 🗣️ **Conversas com memória** - `ai -c` continua última conversa
- 📋 **Cópia automática** - Respostas copiadas para clipboard
- 🔧 **Ferramentas integradas** - O modelo pode executar comandos (ls, cat, tree, find, git)
- 🎨 **Renderização rica** - Markdown com cores, emojis e syntax highlighting
- ⚡ **Streaming** - Respostas em tempo real
- 🔄 **Modelos dinâmicos** - Adiciona e troca modelos facilmente

## 📦 Instalação

```bash
# Desenvolvimento local
pip install -e .

# Requer llm CLI instalado
pip install llm
```

## 🚀 Uso

### Básico
```bash
ai olá como estás              # Pergunta simples
ai -m fast que horas são       # Usar modelo específico
ai -c explica melhor           # Continuar conversa anterior
```

### Ficheiros
```bash
ai file README.md resume isto  # Analisar ficheiro
ai explain main.py             # Explicar código
cat log.txt | ai "que erro é?" # Via pipe
```

### Ferramentas
```bash
ai tree                        # Estrutura de pastas
ai find "def main"             # Pesquisa com ripgrep
ai fzf                         # Fuzzy finder interativo
```

### Gestão de Modelos
```bash
ai model                       # Menu interativo
ai model list                  # Listar todos
ai model set fast              # Definir default
ai model add meu gpt-4 "Desc"  # Adicionar custom
ai model current               # Ver atual
```

## 🤖 Modelos Built-in

| Alias | Modelo | Descrição |
|-------|--------|-----------|
| `maverick` | Llama 4 Maverick 17B | Uso geral (padrão) |
| `fast` | Llama 3.3 70B | Rápido + qualidade |
| `quick` | Llama 3.1 8B | Ultra-rápido |
| `qwen` | Qwen3 32B | Código Python/JS |
| `web` | Compound | Web search + tools |

## 🔧 Opções Principais

```
-m, --model ALIAS    Modelo a usar
-c, --continue       Continuar conversa anterior
-v, --verbose        Modo verbose
-V, --version        Versão
-h, --help           Ajuda
```

## 📋 Auto-Copy

Todas as respostas são **automaticamente copiadas** para o clipboard.
Após cada resposta verás: `📋 Copiado`

## 🔌 Dependências Opcionais

- **ripgrep (rg)** - Para `ai find` (fallback para findstr)
- **fzf** - Para `ai fzf`

## 📁 Configuração

Configuração guardada em:
- **Windows**: `%APPDATA%\ai-cli\config.json`
- **Linux/Mac**: `~/.config/ai-cli/config.json`

## 📜 Licença

MIT
