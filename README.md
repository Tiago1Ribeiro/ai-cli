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
ai f README.md resume   # Igual a: ai file
ai e main.py            # Igual a: ai explain
ai t                    # Igual a: ai tree
ai s TODO               # Igual a: ai find (search)
```

### Continuar Conversações

```bash
# Primeira mensagem
ai explica redes neuronais

# Continuar a conversa (mantém contexto)
ai -c dá-me um exemplo de código

# Continuar
ai -c explica isso com mais detalhe
```

### Análise de Ficheiros

```bash
# Analisar um ficheiro
ai file README.md resume este ficheiro

# Explicar código
ai explain src/main.py

# Input via pipe
cat error.log | ai o que causou este erro
echo def hello pass | ai melhora este código
```

### Ferramentas Integradas

A IA pode executar comandos seguros quando necessário:

```bash
# A IA pode listar ficheiros
ai mostra-me ficheiros python neste diretório

# A IA pode ler ficheiros
ai o que contém o config.json

# A IA pode verificar estado do git
ai que ficheiros mudaram

# A IA pode procurar padrões
ai encontra todos os comentários TODO
```

### Ferramentas Diretas (Avançado)

```bash
# Estrutura do projeto
ai tree

# Pesquisa com ripgrep
ai find def main

# Selecionador interativo de ficheiros
ai fzf
```

### Gestão de Modelos

```bash
# Listar todos os modelos disponíveis
ai --models

# Menu interativo de modelos
ai model

# Mostrar modelo atual
ai model current

# Definir modelo padrão
ai model set local

# Adicionar novo modelo
ai model add mymodel llama3.2 "O meu modelo personalizado"

# Remover modelo
ai model remove mymodel
```

### Comandos do Sistema

```bash
# Verificar estado do sistema
ai check            # Verifica instalação do llm, modelos, config

# Ver configuração
ai config           # Mostra config.json atual

# Desativar streaming (mostrar output completo de uma vez)
ai --no-stream explica isto em detalhe
```

## Referência de Comandos

### Comando Principal

```
ai [OPÇÕES] [QUERY]
```

**Opções:**
- `-m, --model MODEL` - Especificar modelo a usar
- `-c, --continue` - Continuar conversa anterior
- `-v, --verbose` - Mostrar output detalhado
- `--no-stream` - Desativar streaming (mostrar output completo)
- `-V, --version` - Mostrar versão
- `-h, --help` - Mostrar mensagem de ajuda

### Comandos

- `ai check` - Verificar estado do sistema (instalação llm, modelos, config)
- `ai config` - Mostrar/editar configuração
- `ai file <caminho> [query]` - Analisar ficheiro(s)
- `ai explain <caminho>` - Explicar ficheiro de código
- `ai find <padrão>` - Pesquisar padrões com ripgrep
- `ai fzf` - Selecionador fuzzy interativo de ficheiros
- `ai model` - Gestão de modelos (interativo)
- `ai models` - Listar modelos disponíveis
- `ai tree` - Mostrar estrutura de diretórios

### Aliases

- `ai f` → `ai file`
- `ai e` → `ai explain`
- `ai t` → `ai tree`
- `ai s` → `ai find`

### Subcomandos de Modelo

- `ai model list` - Listar todos os modelos configurados
- `ai model current` - Mostrar modelo padrão atual
- `ai model set <alias>` - Definir modelo padrão
- `ai model add <alias> <id> <desc>` - Adicionar novo modelo
- `ai model remove <alias>` - Remover modelo

## Características em Detalhe

### Cópia Automática para Clipboard

Cada resposta é automaticamente copiada para o teu clipboard para uso rápido. Verás uma confirmação:

```
λ ai-cli • 2.3s ────────────────────────────────────────────────────────────────

  [AI response here]

∴ copiado para clipboard ──────────────────────────────────────────────────────
```

### Interface Terminal Rica

- **Layout Limpo**: Design minimalista com largura de 80 caracteres
- **Syntax Highlighting**: Blocos de código com deteção de linguagem
- **Suporte Markdown**: Cabeçalhos, listas, tabelas, citações
- **Deteção de Caminhos**: Destaca automaticamente caminhos de ficheiros
- **Temas de Cor**: Estética cyan/azul otimizada para legibilidade

### Memória de Contexto

Usa `-c` para manter contexto da conversa:

```bash
ai estou a aprender Python          # Primeira mensagem
ai -c recomenda alguns recursos      # IA lembra que estás a aprender Python
ai -c e sobre web frameworks?        # IA conhece o contexto
```

### Integração com Sistema

A IA pode executar comandos seguros e só-leitura quando útil:

- `ls` / `dir` - Listar ficheiros
- `cat` / `type` - Ler ficheiros
- `pwd` - Diretório atual
- `git status` - Informação do Git
- `tree` - Estrutura de diretórios
- `find` / `grep` - Pesquisa

**Nota**: Comandos só são executados quando explicitamente necessários pelo raciocínio da IA. Tu controlas quando as ferramentas executam.

## Resolução de Problemas

### "llm: command not found"

Instala a ferramenta llm CLI:

```bash
pip install llm
```

### "No API key configured"

Configura o teu fornecedor LLM:

```bash
# Para OpenAI
llm keys set openai

# Para Claude
llm install llm-claude-3
llm keys set claude

# Para modelos locais
ollama pull llama3.2
llm install llm-ollama
```

### "Model not found"

Verifica modelos disponíveis:

```bash
# Listar modelos llm
llm models

# Listar modelos configurados do ai-cli
ai model list
```

Depois adiciona o teu modelo:

```bash
ai model add mymodel <model-id> "Descrição"
ai model set mymodel
```

### Clipboard não funciona

**Windows**: Deve funcionar automaticamente com `clip.exe`

**macOS**: Deve funcionar com `pbcopy`

**Linux**: Instala `xclip` ou `xsel`:

```bash
# Ubuntu/Debian
sudo apt install xclip

# Fedora
sudo dnf install xclip

# Arch
sudo pacman -S xclip
```

### Caracteres Unicode não aparecem

Certifica-te que estás a usar um terminal moderno:
- **Windows**: Windows Terminal (recomendado)
- **macOS**: Terminal.app ou iTerm2
- **Linux**: GNOME Terminal, Konsole ou Alacritty

## Dependências Opcionais

Melhora a funcionalidade com estas ferramentas opcionais:

- **ripgrep (rg)**: Pesquisa rápida para comando `ai find`
  ```bash
  # Windows: winget install BurntSushi.ripgrep.MSVC
  # macOS: brew install ripgrep
  # Linux: sudo apt install ripgrep
  ```

- **fzf**: Selecionador fuzzy interativo para `ai fzf`
  ```bash
  # Windows: winget install fzf
  # macOS: brew install fzf
  # Linux: sudo apt install fzf
  ```

- **tree**: Visualização de estrutura de diretórios
  ```bash
  # Geralmente pré-instalado na maioria dos sistemas
  # Windows: built-in (tree /F)
  ```

## Desenvolvimento

### Configurar Ambiente de Desenvolvimento

```bash
# Clonar repositório
git clone https://github.com/mediaweb-global/cli-ai.git
cd cli-ai

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar em modo editável com dependências de dev
pip install -e ".[dev]"

# Executar testes
pytest
```

### Estrutura do Projeto

```
cli-ai/
├── src/
│   └── ai_cli/
│       ├── __init__.py
│       ├── main.py         # Ponto de entrada CLI
│       ├── config.py       # Gestão de configuração
│       ├── llm_client.py   # Interação com LLM
│       ├── render.py       # Renderização no terminal
│       └── tools/          # Ferramentas integradas
│           ├── find.py
│           ├── fzf.py
│           ├── tree.py
│           └── safe_commands.py
├── tests/
├── pyproject.toml
├── README.md
└── LICENSE
```

## Contribuir

Contribuições são bem-vindas! Por favor:

1. Faz fork do repositório
2. Cria um branch de feature (`git checkout -b feature/funcionalidade-incrivel`)
3. Faz commit das tuas alterações (`git commit -m 'Adiciona funcionalidade incrível'`)
4. Faz push para o branch (`git push origin feature/funcionalidade-incrivel`)
5. Abre um Pull Request

## Configuração

A configuração é guardada em:
- **Windows**: `%APPDATA%\ai-cli\config.json`
- **Linux/Mac**: `~/.config/ai-cli/config.json`

