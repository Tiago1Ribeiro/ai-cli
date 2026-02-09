# AI CLI


```bash
┌─────────────────────────────────────────────────────────────┐
│  Assistente de IA versátil para terminal, alimentado por    │
│  LLMs, com execução de comandos, renderização rica de       │
│  markdown e memória de contexto.                            │
└─────────────────────────────────────────────────────────────┘
```

## Demos

### Instalação Completa
![AI CLI Installation Demo](ai-cli-demo.gif)

### Exemplos de Utilização
![AI CLI Usage Examples](ai-cli-usage.gif)

---

## Características

```bash
  FEATURE              DESCRIÇÃO
  ───────────────────  ──────────────────────────────────────────
  Memória              Retenção de contexto entre mensagens [-c]
  Clipboard            Respostas copiadas automaticamente
  Ferramentas          Executa comandos do sistema (ls, cat, git)
  Renderização         TUI minimalista com syntax highlighting
  Streaming            Resposta em tempo real com animação
  Modelos              Adiciona e alterna entre backends LLM
```

---

## Quick Start

### 1. Instalar AI CLI (Recomendado: pipx)

O **pipx** instala aplicações Python isoladamente, tornando o comando `ai`
disponível globalmente — sem necessidade de ativar ambientes virtuais.

```bash
# 1. Instalar pipx (uma vez)
python -m pip install --user pipx
python -m pipx ensurepath

# 2. Clonar o repositório
git clone https://github.com/Tiago1Ribeiro/ai-cli.git
cd ai-cli

# 3. Instalar ai-cli globalmente (modo editável)
pipx install -e .

# 4. Reiniciar o terminal e verificar
ai --version
```

```
  Porquê pipx?
  ─────────────────────────────────────────────────────
  [+] Comando `ai` disponível em qualquer directório
  [+] Sem necessidade de activar venv ou conda
  [+] Isolamento total de dependências
  [+] Modo editável: alterações em src/ reflectem-se
      imediatamente
```

<details>
<summary>[...] Alternativa: instalação manual (venv / conda)</summary>

**Opção A — venv:**

```bash
# Windows
python -m venv .venv && .venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv && source .venv/bin/activate

pip install -e .
```

**Opção B — conda:**

```bash
conda create -n ai-cli python=3.10
conda activate ai-cli
pip install -e .
```

```
  NOTA: Com estas opções, tens de activar o ambiente
        sempre que quiseres usar o comando `ai`.
```

</details>

### 2. Instalar dependência core

O `ai-cli` depende da ferramenta `llm` para gerir modelos:

```bash
# Se instalaste via pipx (recomendado)
pipx inject ai-cli llm

# Se instalaste via pip/conda
pip install llm
```

### 3. Configurar um modelo

O AI CLI usa a ferramenta [llm](https://llm.datasette.io/) para gerir modelos.
Recomendamos fornecedores com **Free Tier** generoso.

#### Groq (Recomendado — Grátis e ultra-rápido)

Modelo `groq/moonshotai/kimi-k2-instruct-0905`.

```bash
# 1. Obtém API Key grátis em https://console.groq.com

# 2. Instalar o plugin Groq
pipx inject ai-cli llm-groq

# 3. Configurar a API Key
#    Windows (PowerShell):
$env:PIPX_HOME = "$env:USERPROFILE\pipx"
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm keys set groq

#    Linux/Mac:
python -m llm keys set groq

# 4. Definir modelo padrão
#    Windows:
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models default groq/moonshotai/kimi-k2-instruct-0905

#    Linux/Mac:
python -m llm models default groq/moonshotai/kimi-k2-instruct-0905
```

<details>
<summary>[...] Outras opções de modelo (Ollama, Cloudflare, OpenAI)</summary>

#### Ollama (Local e privado)

```bash
# 1. Instalar: https://ollama.com/download
ollama pull llama3.2

# 2. Instalar plugin
pipx inject ai-cli llm-ollama

# 3. Definir como padrão
#    Windows:
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models default llama3.2

#    Linux/Mac:
python -m llm models default llama3.2
```

#### Cloudflare Workers AI (Grátis)

```bash
pipx inject ai-cli llm-cloudflare

# Windows:
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm keys set cloudflare

# Linux/Mac:
python -m llm keys set cloudflare
```

#### OpenAI (Pago)

```bash
pipx inject ai-cli openai

# Windows:
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm keys set openai

# Linux/Mac:
python -m llm keys set openai
```

</details>

### 4. Testar

```bash
ai olá mundo
```

---

## Uso

### Queries básicas

```bash
# Pergunta simples — sem aspas
ai qual é a capital de França

# Queries multi-palavra
ai explica computação quântica em termos simples
```

### Continuar conversações

```bash
ai explica redes neuronais            # primeira mensagem
ai -c dá-me um exemplo de código      # mantém contexto
ai -c explica isso com mais detalhe   # continua a conversa
```

### Análise de ficheiros

```bash
ai file README.md resume este ficheiro
ai explain src/main.py

# Input via pipe
cat error.log | ai o que causou este erro
echo "def hello pass" | ai melhora este código
```

### Ferramentas integradas

A IA executa comandos seguros (só-leitura) quando necessário:

```bash
ai mostra-me ficheiros python neste directório
ai o que contém o config.json
ai que ficheiros mudaram                # git status
ai encontra todos os comentários TODO
```

### Mudar de modelo

```bash
# Temporariamente (só esta query)
ai -m groq/llama-3.1-8b-instant pergunta rápida
ai -m fast explica isto em detalhe

# Menu interactivo
ai model

# Ver modelos disponíveis
ai --models
```

### Aliases

```bash
  ALIAS    COMANDO        DESCRIÇÃO
  ───────  ─────────────  ──────────────────────
  ai f     ai file        Analisar ficheiro
  ai e     ai explain     Explicar código
  ai t     ai tree        Estrutura de directórios
  ai s     ai find        Pesquisar padrões
```

---

## Referência de Comandos

```bash
SYNOPSIS
    ai [OPÇÕES] [QUERY]

OPÇÕES
    -m, --model MODEL     Especificar modelo a usar
    -c, --continue        Continuar conversa anterior
    -v, --verbose         Output detalhado
        --no-stream       Desactivar streaming
    -V, --version         Mostrar versão
    -h, --help            Mostrar ajuda

COMANDOS
    ai check              Verificar estado do sistema
    ai config             Mostrar/editar configuração
    ai file <path> [q]    Analisar ficheiro(s)
    ai explain <path>     Explicar ficheiro de código
    ai find <padrão>      Pesquisar com ripgrep
    ai fzf                Seleccionador fuzzy interactivo
    ai model              Gestão de modelos (interactivo)
    ai models             Listar modelos disponíveis
    ai tree               Mostrar estrutura de directórios
```

<details>
<summary>[...] Subcomandos de modelo</summary>

```bash
  SUBCOMANDO                          DESCRIÇÃO
  ────────────────────────────────    ─────────────────────────────
  ai model list                      Listar modelos configurados
  ai model current                   Mostrar modelo padrão actual
  ai model set <alias>               Definir modelo padrão
  ai model add <alias> <id> <desc>   Adicionar novo modelo
  ai model remove <alias>            Remover modelo
```

</details>

---

## Configuração

Na primeira execução, o AI CLI cria um ficheiro de configuração:

```bash
  SISTEMA       CAMINHO
  ────────────  ──────────────────────────────────
  Windows       %APPDATA%\ai-cli\config.json
  Linux/macOS   ~/.config/ai-cli/config.json
```

<details>
<summary>[...] Exemplo de config.json</summary>

```json
{
  "default_model": null,
  "models": {
    "fast": {
      "model_id": "groq/moonshotai/kimi-k2-instruct-0905",
      "description": "Kimi K2 via Groq - Rápido e inteligente"
    },
    "quick": {
      "model_id": "groq/llama-3.1-8b-instant",
      "description": "Llama 3.1 8B via Groq - Ultra-rápido"
    },
    "local": {
      "model_id": "llama3.2",
      "description": "Llama 3.2 local via Ollama"
    }
  }
}
```

Se `default_model` for `null`, o AI CLI usa o modelo padrão definido
globalmente no `llm`.

```bash
  Modelos Groq populares (gratuitos):
  ─────────────────────────────────────────────
  groq/moonshotai/kimi-k2-instruct-0905   -- mais inteligente
  groq/llama-3.1-8b-instant      -- mais rápido
  groq/llama-3.3-70b-versatile   -- modelo versátil
  groq/qwen/qwen3-32b            -- propósito geral
```

</details>

<details>
<summary>[...] Gestão de modelos avançada</summary>

```bash
# Ver todos os aliases configurados
ai --models

# Menu interactivo completo
ai model

# Adicionar novo alias
ai model add myfast groq/llama-3.1-8b-instant "Meu modelo rápido"

# Remover alias
ai model remove myfast

# Mudar default permanentemente
# Windows:
$env:PIPX_HOME = "$env:USERPROFILE\pipx"
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models default groq/moonshotai/kimi-k2-instruct-0905

# Linux/Mac:
python -m llm models default groq/moonshotai/kimi-k2-instruct-0905

# Listar modelos reais instalados no llm
# Windows:
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models list

# Linux/Mac:
python -m llm models list
```

```bash
  NOTA: Aliases vs Modelos
  ──────────────────────────────────────────────────
  Aliases  (fast, quick)                 -> atalhos no config.json do ai-cli
  Modelos  (groq/moonshotai/kimi-k2-instruct-0905)     -> IDs reais instalados no llm
  Ambos funcionam com a flag -m.
```

</details>

---

## Resolução de Problemas

<details>
<summary>[err] ai: command not found (após pipx)</summary>

1. **Fecha e reabre o terminal** (ou reinicia o sistema).
2. Verifica se o PATH foi actualizado:
   ```bash
   # Windows PowerShell
   $env:PATH
   # Deve conter: C:\Users\TeuUser\.local\bin
   ```
3. Se não funcionar, usa o caminho completo temporariamente:
   ```bash
   C:\Users\TeuUser\.local\bin\ai.exe --help
   ```

</details>

<details>
<summary>[err] llm: command not found</summary>

```bash
# Se usaste pipx
pipx inject ai-cli llm

# Se usaste pip
pip install llm
```

</details>

<details>
<summary>[err] No API key configured / Unknown model</summary>

Setup rápido com Groq:

```bash
pipx inject ai-cli llm-groq

# Windows:
$env:PIPX_HOME = "$env:USERPROFILE\pipx"
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm keys set groq
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models default groq/moonshotai/kimi-k2-instruct-0905

# Linux/Mac:
python -m llm keys set groq
python -m llm models default groq/moonshotai/kimi-k2-instruct-0905

ai olá
```

</details>

<details>
<summary>[err] Clipboard não funciona</summary>

```bash
  SISTEMA    SOLUÇÃO
  ─────────  ─────────────────────────────────────
  Windows    Funciona automaticamente (clip.exe)
  macOS      Funciona automaticamente (pbcopy)
  Linux      Instalar xclip:
               sudo apt install xclip      # Debian/Ubuntu
               sudo dnf install xclip      # Fedora
               sudo pacman -S xclip        # Arch
```

</details>

<details>
<summary>[err] Caracteres Unicode não aparecem</summary>

Usa um terminal moderno:

```bash
  SISTEMA    TERMINAL RECOMENDADO
  ─────────  ──────────────────────────────
  Windows    Windows Terminal
  macOS      Terminal.app ou iTerm2
  Linux      GNOME Terminal, Konsole, Alacritty
```

</details>

<details>
<summary>[?] Perguntas frequentes sobre modelos</summary>

```bash
Q: Diferença entre `ai -m fast` e `ai -m groq/moonshotai/kimi-k2-instruct-0905`?
A: `fast` é um alias que aponta para o mesmo modelo. Ambos funcionam.

Q: Como sei que modelo está a ser usado?
A: `ai model current` ou verifica o cabeçalho da resposta.

Q: Posso ter vários modelos instalados?
A: Sim. Instala vários plugins e muda entre eles com `-m`.

Q: Como adiciono um modelo sem alias?
A: Usa directamente:
     ai -m groq/llama-3.3-70b-versatile tua pergunta
   Ou cria alias:
     ai model add mix groq/llama-3.3-70b-versatile "Versatile"
     ai -m mix tua pergunta

Q: Como vejo os modelos Groq disponíveis?
A: Depois de instalar llm-groq:
     # Linux/Mac
     python -m llm models list | grep -i groq
     # Windows
     & "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models list | Select-String "groq"
```

</details>

---

## Dependências Opcionais

<details>
<summary>[...] Ferramentas que melhoram a experiência</summary>

```bash
  FERRAMENTA    PARA QUÊ                      INSTALAÇÃO
  ────────────  ────────────────────────────   ──────────────────────────
  ripgrep (rg)  Pesquisa rápida (ai find)      winget/brew/apt install ripgrep
  fzf           Seleccionador fuzzy (ai fzf)   winget/brew/apt install fzf
  tree          Estrutura de directórios        Geralmente pré-instalado
```

</details>

---

## Desenvolvimento

<details>
<summary>[...] Configurar ambiente de desenvolvimento</summary>

**Método recomendado (pipx):**

```bash
git clone https://github.com/Tiago1Ribeiro/ai-cli.git
cd ai-cli
pipx install -e .
pipx inject ai-cli llm pytest pytest-cov
ai --version
```

**Método tradicional (venv):**

```bash
git clone https://github.com/Tiago1Ribeiro/ai-cli.git
cd ai-cli
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

</details>

<details>
<summary>[...] Estrutura do projecto</summary>

```bash
ai-cli/
├── src/
│   └── ai_cli/
│       ├── __init__.py
│       ├── main.py              # Ponto de entrada CLI
│       ├── config.py            # Gestão de configuração
│       ├── llm_client.py        # Interacção com LLM
│       ├── render.py            # Renderização no terminal
│       └── tools/               # Ferramentas integradas
│           ├── find.py
│           ├── fzf.py
│           ├── tree.py
│           └── safe_commands.py
├── tests/
├── pyproject.toml
├── README.md
└── LICENSE
```

</details>

<details>
<summary>[...] Actualizar / Desinstalar</summary>

```bash
# Actualizar (pipx)
cd ai-cli && git pull && pipx reinstall ai-cli

# Actualizar (pip)
cd ai-cli && git pull && pip install -e . --upgrade

# Desinstalar
pipx uninstall ai-cli    # ou: pip uninstall ai-cli
```

</details>

---

## Contribuir

Contribuições são bem-vindas:

```bash
1.  Fork do repositório
2.  git checkout -b feature/funcionalidade-incrivel
3.  git commit -m 'Adiciona funcionalidade incrível'
4.  git push origin feature/funcionalidade-incrivel
5.  Abrir Pull Request
```

---

```bash
ai-cli -- feito para o terminal
```