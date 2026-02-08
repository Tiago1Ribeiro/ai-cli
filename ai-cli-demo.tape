# VHS Tape File - AI CLI Installation Demo
# Usa: vhs ai-cli-demo.tape
# Output: ai-cli-demo.gif ou ai-cli-demo.mp4

# Configurações de output
Output ai-cli-demo.gif
Output ai-cli-demo.mp4

# Configurações de estilo
Set Theme "Catppuccin Mocha"
Set FontFamily "Cascadia Code"
Set FontSize 18
Set Width 1200
Set Height 800
Set Padding 20
Set TypingSpeed 50ms
Set PlaybackSpeed 1.0

# ==============================================================================
# INÍCIO
# ==============================================================================

Hide
Type "clear"
Enter
Show

Sleep 1s

Type "# AI CLI - Demonstração de Instalação"
Enter
Sleep 2s

# ==============================================================================
# PASSO 1: Verificar Python
# ==============================================================================

Type "# Passo 1: Verificar Python"
Enter
Sleep 500ms

Type "python --version"
Enter
Sleep 2s

# ==============================================================================
# PASSO 2: Instalar pipx
# ==============================================================================

Type "# Passo 2: Instalar pipx (gerenciador de apps Python)"
Enter
Sleep 500ms

Type "python -m pip install --user pipx"
Enter
Sleep 3s

Type "python -m pipx ensurepath"
Enter
Sleep 2s

Type "# [Reiniciar terminal aqui em instalação real]"
Enter
Sleep 2s

# ==============================================================================
# PASSO 3: Navegar para o projeto
# ==============================================================================

Type "# Passo 3: Clonar repositório"
Enter
Sleep 500ms

Type "git clone https://github.com/Tiago1Ribeiro/ai-cli.git"
Enter
Sleep 2s

Type "cd ai-cli"
Enter
Sleep 1s

Type "ls"
Enter
Sleep 2s

# ==============================================================================
# PASSO 4: Instalar ai-cli
# ==============================================================================

Type "# Passo 4: Instalar AI CLI globalmente"
Enter
Sleep 500ms

Type "pipx install -e ."
Enter
Sleep 4s

# ==============================================================================
# PASSO 5: Injetar dependências
# ==============================================================================

Type "# Passo 5: Instalar biblioteca LLM"
Enter
Sleep 500ms

Type "pipx inject ai-cli llm"
Enter
Sleep 3s

# ==============================================================================
# PASSO 6: Instalar plugin
# ==============================================================================

Type "# Passo 6: Instalar plugin Groq (grátis e rápido)"
Enter
Sleep 500ms

Type "pipx inject ai-cli llm-groq"
Enter
Sleep 3s

# ==============================================================================
# PASSO 7: Configurar (simulado)
# ==============================================================================

Type "# Passo 7: Configurar chave API e modelo"
Enter
Sleep 500ms

Type "# llm keys set groq"
Enter
Type "# llm models default groq/moonshotai/kimi-k2-instruct-0905"
Enter
Sleep 2s

Type "# [Configure sua chave em console.groq.com]"
Enter
Sleep 3s

# ==============================================================================
# PASSO 8: Verificar instalação
# ==============================================================================

Type "# Passo 8: Verificar instalação"
Enter
Sleep 500ms

Type "ai --version"
Enter
Sleep 2s

Type "ai --help"
Enter
Sleep 3s

# ==============================================================================
# PASSO 9: Exemplo de uso (simulado)
# ==============================================================================

Type "# Passo 9: Testar (após configurar chave)"
Enter
Sleep 500ms

Type "# ai \"olá mundo\""
Enter
Sleep 1s

Type "# ai -c \"qual é o tempo em Lisboa?\""
Enter
Sleep 2s

# ==============================================================================
# CONCLUSÃO
# ==============================================================================

Type "# ✅ Instalação concluída!"
Enter
Sleep 1s

Type "# Próximo: configure sua chave API e comece a usar"
Enter
Sleep 3s

# ==============================================================================
# FIM
# ==============================================================================

Sleep 2s
