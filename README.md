# AI CLI

Assistente de IA versátil para terminal, alimentado por LLMs, com execução de comandos, renderização rica de markdown e memória de contexto.

![alt text](assets\leiria_existe.png)

## Características

- **Memória de Conversação**: Retenção adequada de contexto com flag `-c`
- **Cópia Automática**: Respostas automaticamente copiadas para clipboard
- **Ferramentas Integradas**: Executa comandos do sistema (ls, cat, tree, find, git)
- **Renderização Rica**: TUI minimalista e bonita com syntax highlighting
- **Streaming em Direto**: Resposta em tempo real com animação
- **Modelos Dinâmicos**: Adiciona, alterna e gere facilmente diferentes backends LLM

## Começar (Quick Start)

Segue estes passos para instalar e configurar o AI CLI.

### 1. Instalar AI CLI (Método Recomendado: pipx)

O **pipx** instala aplicações Python isoladamente, mas torna o comando `ai` disponível globalmente. Não precisas de ativar ambientes virtuais para usar o comando.

```bash
# 1. Instalar pipx (uma vez)
python -m pip install --user pipx
python -m pipx ensurepath

# 2. Clonar o repositório
git clone https://github.com/Tiago1Ribeiro/ai-cli.git
cd ai-cli

# 3. Instalar ai-cli globalmente (modo editável para desenvolvimento)
pipx install -e .

# 4. Reinicia o terminal e verifica
ai --version
```

**Vantagens do pipx:**
- ✅ Comando `ai` disponível em qualquer pasta, qualquer terminal
- ✅ Sem necessidade de `conda activate` ou ativar venv
- ✅ Isolamento total das dependências
- ✅ Modo editável: altera o código em `src/` e as mudanças refletem-se imediatamente

### Alternativa: Instalação Manual (Para Desenvolvimento Avançado)

Se preferires controlo total sobre o ambiente:

**Opção A: Usando `venv`**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate

# Instalar
pip install -e .
```

**Opção B: Usando `conda`**
```bash
conda create -n ai-cli python=3.10
conda activate ai-cli
pip install -e .
```

**Nota**: Com esta opção, terás de ativar o ambiente sempre que quiseres usar o comando `ai`.

### 2. Instalar Dependência Core

O `ai-cli` depende da ferramenta `llm` para gerir modelos:

```bash
# Se instalaste via pipx (recomendado)
pipx inject ai-cli llm

# Se instalaste via pip/conda
pip install llm
```

### 3. Configurar Modelos (Recomendado: Free Tier)

O AI CLI usa a ferramenta `llm` para gerir modelos. Recomendamos fornecedores com **Free Tier** generoso e rápido.

#### Opção A: Groq (Recomendado - Grátis e Ultra-Rápido)
Ideal para respostas instantâneas. Modelo `llama-3.3-70b-versatile` grátis com muita quota.

1. **Obtém uma API Key grátis** em [console.groq.com](https://console.groq.com)
2. **Instala o plugin Groq:**
```bash
pipx inject ai-cli llm-groq
```

3. **Configura a API Key:**
```bash
# Windows (PowerShell)
$env:PIPX_HOME = "$env:USERPROFILE\pipx"
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm keys set groq
# Cola a tua chave quando pedido (gsk_...)

# Linux/Mac
python -m llm keys set groq
```

4. **Define o modelo padrão:**
```bash
# Windows
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models default llama-3.3-70b-versatile

# Linux/Mac
python -m llm models default llama-3.3-70b-versatile
```

5. **Testa:**
```bash
ai olá mundo
```

#### Opção B: Ollama (Local e Privado)
Se preferes rodar localmente sem internet:

1. **Instala Ollama:** [ollama.com/download](https://ollama.com/download)
2. **Faz pull de um modelo:**
```bash
ollama pull llama3.2
```

3. **Instala o plugin:**
```bash
pipx inject ai-cli llm-ollama
```

4. **Define como padrão:**
```bash
pipx inject ai-cli llm-cloudflare

# Windows
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm keys set cloudflare

# Linux/Mac
python -m llm keys set cloudflare
# Linux/Mac
python -m llm models default llama3.2
```

#### Opção C: Cloudflare Workers AI (Grátis)
```bash
llm install llm-cloudflare
llm keys set cloudflare
# Segue as instruções do plugin
```

### 4. Testar

Agora que tens um modelo padrão definido no `llm`, o `ai` vai usá-lo automaticamente:

```bash
ai olá mundo
```

### 🏃 Quick Reference - Mudar de Modelo

```bash
# Usar modelo diferente uma vez
ai -m llama-3.1-8b-instant pergunta rápida

# Mudar modelo default permanentemente (Windows)
$env:PIPX_HOME = "$env:USERPROFILE\pipx"
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models default llama-3.3-70b-versatile

# Ver modelos disponíveis
ai --models

# Menu interativo
ai model
```

**💡 Dica:** Se instalaste com pipx e precisas de executar comandos `llm` diretamente, usa:
```bash
# Windows
$env:PIPX_HOME = "$env:USERPROFILE\pipx"
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm [comando]

# Exemplo: Listar modelos
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models list
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

Edita `config.json` para personalizar modelos ou aliases de conveniência:

```json
{
  "default_model": null, 
  "models": {
    "fast": {
      "model_id": "llama-3.3-70b-versatile",
      "description": "Llama 3.3 70B via Groq - Rápido e inteligente"
    },
    "quick": {
      "model_id": "llama-3.1-8b-instant",
      "description": "Llama 3.1 8B via Groq - Ultra-rápido"
    },
    "local": {
      "model_id": "llama3.2",
      "description": "Llama 3.2 local via Ollama"
    }
  }
}
```

**Nota**: Se `default_model` for null, o AI CLI usa o modelo padrão definido globalmente no `llm` (vê comando na secção Troubleshooting).

**Modelos Groq Populares (gratuitos):**
- `llama-3.3-70b-versatile` - Mais inteligente
- `llama-3.1-8b-instant` - Mais rápido
- `mixtral-8x7b-32768` - Contexto longo
- `gemma2-9b-it` - Eficiente

## Uso

### Queries Básicas (Sem aspas!)

```bash
# Pergunta simples - SEM ASPAS
ai qual é a capital de França

# Queries multi-palavra - SEM ASPAS
ai explica computação quântica em termos simples
```

### Mudar de Modelo

Tens 3 formas de mudar de modelo:

#### 1. Temporariamente (apenas para esta query)
```bash
# Usar flag -m com qualquer modelo instalado no llm
ai -m llama-3.1-8b-instant pergunta rápida

# Usar alias configurado no ai-cli
ai -m fast explica isto em detalhe
ai -m quick resposta rápida
```

#### 2. Mudar o modelo default do sistema (llm)
Este é usado por todas as apps que usam `llm`, incluindo o `ai-cli`:

```bash
# Windows PowerShell
$env:PIPX_HOME = "$env:USERPROFILE\pipx"
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models default llama-3.3-70b-versatile

# Linux/Mac
python -m llm models default llama-3.3-70b-versatile
```

#### 3. Usar o menu interativo (mais fácil)
```bash
ai model               # Menu interativo - escolhe modelo
ai model set fast      # Define 'fast' como default (alias do ai-cli)
ai model current       # Ver modelo atual
```

**Recomendação:** Usa a Opção 2 (default do llm) para um modelo "global", e a flag `-m` quando precisares de outro temporariamente.

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

### Gestão de Modelos Avançada

```bash
# Ver todos os aliases configurados no ai-cli
ai --models

# Menu interativo completo (adicionar/remover/configurar)
ai model

# Adicionar novo alias
ai model add myfast llama-3.1-8b-instant "Meu modelo rápido"

# Remover alias
ai model remove myfast

# Listar modelos reais instalados no llm
# Windows:
$env:PIPX_HOME = "$env:USERPROFILE\pipx"
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models list

# Linux/Mac:
python -m llm models list
```

**Nota sobre Aliases vs Modelos:**
- **Aliases** (`fast`, `quick`, etc.) são atalhos configurados no `ai-cli` (ficheiro `config.json`)
- **Modelos** (`llama-3.3-70b-versatile`, etc.) são os IDs reais instalados no `llm`
- Podes usar ambos com a flag `-m`

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

### "ai: command not found" (após instalar com pipx)

Depois de executar `pipx ensurepath`, precisas de:
1. **Fechar e reabrir o terminal** (ou reiniciar o sistema)
2. Verificar se o PATH foi atualizado:
   ```bash
   # Windows PowerShell
   $env:PATH
   
   # Deve conter algo como:
   # C:\Users\TeuUser\.local\bin
   # C:\Users\TeuUser\AppData\Roaming\Python\Python3XX\Scripts
   ```

Se ainda não funcionar:
```bash
# Usar caminho completo temporariamente (Windows)
C:\Users\TeuUser\.local\bin\ai.exe --help

# Ou executar via Python
python -m pipx run ai --help
```

### "llm: command not found"

### "llm: command not found"

Instala a ferramenta llm CLI:

```bash
# Se usaste pipx (recomendado)
pipx inject ai-cli llm

# Se usaste pip
pip install llm
```

### "No API key configured" ou "Unknown model"

**Setup Rápido - Groq (Recomendado):**

```bash
# 1. Instalar plugin
pipx inject ai-cli llm-groq

# 2. Configurar chave (obter em console.groq.com)
# Windows PowerShell:
$env:PIPX_HOME = "$env:USERPROFILE\pipx"
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm keys set groq

# 3. Definir modelo default
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models default llama-3.3-70b-versatile

# 4. Testar
ai olá
```

**Outras opções:**

```bash
# Para OpenAI (pago)
pipx inject ai-cli openai
# Windows: & "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm keys set openai
# Linux/Mac: python -m llm keys set openai

# Para Ollama (local/grátis)
ollama pull llama3.2
pipx inject ai-cli llm-ollama
# Windows: & "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models default llama3.2
```

### Listar modelos disponíveis

```bash
# Modelos configurados no ai-cli (aliases)
ai --models

# Modelos reais instalados no llm
# Windows:
$env:PIPX_HOME = "$env:USERPROFILE\pipx"
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models list

# Linux/Mac:
python -m llm models list
```

### Perguntas Frequentes - Modelos

**Q: Qual a diferença entre `ai -m fast` e `ai -m llama-3.3-70b-versatile`?**
A: `fast` é um alias (atalho) configurado no `ai-cli` que aponta para `llama-3.3-70b-versatile`. Podes usar qualquer um.

**Q: Como sei que modelo está a ser usado?**
A: Usa `ai model current` ou verifica o cabeçalho da resposta (mostra duração e modelo).

**Q: Posso ter vários modelos instalados?**
A: Sim! Instala vários plugins (`llm-groq`, `llm-ollama`, etc.) e muda entre eles com `-m` ou alterando o default.

**Q: Como adiciono um modelo que não está nos aliases?**
A: Dois métodos:
```bash
# Método 1: Usar diretamente o ID do llm
ai -m mixtral-8x7b-32768 tua pergunta

# Método 2: Criar alias
ai model add mix mixtral-8x7b-32768 "Mixtral rápido"
ai -m mix tua pergunta
```

**Q: Onde vejo todos os modelos Groq disponíveis?**
A: Depois de instalar `llm-groq`:
```bash
# Windows:
& "$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe" -m llm models list | Select-String "groq"

# Linux/Mac:
python -m llm models list | grep -i groq
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

## Gestão da Instalação

### Atualizar o AI CLI
```bash
# Se instalaste com pipx
cd ai-cli
git pull
pipx reinstall ai-cli

# Se instalaste com pip (no venv/conda)
cd ai-cli
git pull
pip install -e . --upgrade
```

### Desinstalar
```bash
# Se instalaste com pipx
pipx uninstall ai-cli

# Se instalaste com pip
pip uninstall ai-cli
```

### Listar aplicações instaladas via pipx
```bash
pipx list
```

## Desenvolvimento

### Configurar Ambiente de Desenvolvimento

**Método Recomendado (pipx):**
```bash
# Clonar repositório
git clone https://github.com/mediaweb-global/cli-ai.git
cd cli-ai

# Instalar em modo editável global
pipx install -e .
pipx inject ai-cli llm pytest pytest-cov

# O comando 'ai' está agora disponível globalmente
# e qualquer alteração no código em src/ tem efeito imediato
ai --version
```

**Método Tradicional (venv):**
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

