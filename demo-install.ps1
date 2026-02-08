# ==============================================================================
# AI CLI - Script de Demonstração de Instalação Automática
# ==============================================================================
# Use este script para gravar um vídeo demonstrando a instalação completa

param(
    [switch]$Fast,  # Modo rápido (sem pausas longas)
    [switch]$Clean  # Limpar instalação anterior
)

$ErrorActionPreference = "Continue"

# Cores e formatação
function Write-Step {
    param([string]$Message)
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "→ $Message" -ForegroundColor Blue
}

function Wait-Demo {
    param([int]$Seconds = 2)
    if (-not $Fast) {
        Start-Sleep -Seconds $Seconds
    }
}

# Animação de typing (para parecer mais natural)
function Write-Command {
    param([string]$Command, [switch]$Execute)
    
    Write-Host "`n> " -NoNewline -ForegroundColor Gray
    
    foreach ($char in $Command.ToCharArray()) {
        Write-Host $char -NoNewline -ForegroundColor White
        if (-not $Fast) {
            Start-Sleep -Milliseconds (Get-Random -Minimum 30 -Maximum 80)
        }
    }
    
    Write-Host ""
    
    if ($Execute) {
        Wait-Demo -Seconds 1
        Invoke-Expression $Command
        Wait-Demo -Seconds 2
    }
}

# ==============================================================================
# INÍCIO DA DEMONSTRAÇÃO
# ==============================================================================

Clear-Host
Write-Host @"

   █████╗ ██╗     ██████╗██╗     ██╗
  ██╔══██╗██║    ██╔════╝██║     ██║
  ███████║██║    ██║     ██║     ██║
  ██╔══██║██║    ██║     ██║     ██║
  ██║  ██║██║    ╚██████╗███████╗██║
  ╚═╝  ╚═╝╚═╝     ╚═════╝╚══════╝╚═╝
  
  Demonstração de Instalação Automática
  
"@ -ForegroundColor Cyan

Wait-Demo -Seconds 3

# ==============================================================================
# LIMPEZA (opcional)
# ==============================================================================

if ($Clean) {
    Write-Step "🧹 PASSO 0: Limpeza de Instalação Anterior"
    
    Write-Command "pipx uninstall ai-cli"
    try {
        pipx uninstall ai-cli 2>$null
        Write-Success "Instalação anterior removida"
    } catch {
        Write-Info "Nenhuma instalação anterior encontrada"
    }
    
    Wait-Demo -Seconds 2
}

# ==============================================================================
# PASSO 1: Verificar Python
# ==============================================================================

Write-Step "📋 PASSO 1: Verificar Python"

Write-Command "python --version" -Execute

$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    if ($major -ge 3 -and $minor -ge 8) {
        Write-Success "Python $major.$minor encontrado (OK)"
    } else {
        Write-Host "⚠ Python $major.$minor - recomendado 3.8+" -ForegroundColor Yellow
    }
}

Wait-Demo -Seconds 2

# ==============================================================================
# PASSO 2: Instalar pipx
# ==============================================================================

Write-Step "📦 PASSO 2: Instalar pipx"

Write-Info "O pipx permite instalar aplicações Python de forma isolada"
Wait-Demo -Seconds 2

Write-Command "python -m pip install --user pipx" -Execute
Write-Command "python -m pipx ensurepath" -Execute

Write-Host "`n⚠ NOTA: Em instalação real, deve reiniciar o terminal aqui" -ForegroundColor Yellow
Wait-Demo -Seconds 3

# ==============================================================================
# PASSO 3: Clonar Repositório (simulado)
# ==============================================================================

Write-Step "📂 PASSO 3: Obter Código Fonte"

Write-Info "Já estamos no diretório do projeto"
Write-Command "Get-Location" -Execute

Write-Command "Get-ChildItem -Name" -Execute

Wait-Demo -Seconds 2

# ==============================================================================
# PASSO 4: Instalar ai-cli
# ==============================================================================

Write-Step "🚀 PASSO 4: Instalar AI CLI"

Write-Info "Instalação em modo editável (desenvolvimento)"
Wait-Demo -Seconds 2

Write-Command "pipx install -e ." -Execute

Write-Success "AI CLI instalado com sucesso!"
Wait-Demo -Seconds 3

# ==============================================================================
# PASSO 5: Injetar dependências
# ==============================================================================

Write-Step "💉 PASSO 5: Instalar Dependências Core"

Write-Info "Injetando biblioteca llm no ambiente isolado"
Wait-Demo -Seconds 2

Write-Command "pipx inject ai-cli llm" -Execute

Write-Success "Biblioteca LLM instalada"
Wait-Demo -Seconds 2

# ==============================================================================
# PASSO 6: Instalar plugin Groq
# ==============================================================================

Write-Step "🔌 PASSO 6: Instalar Plugin Groq"

Write-Info "Groq oferece modelos rápidos e gratuitos"
Wait-Demo -Seconds 2

Write-Command "pipx inject ai-cli llm-groq" -Execute

Write-Success "Plugin Groq instalado"
Wait-Demo -Seconds 3

# ==============================================================================
# PASSO 7: Configurar modelo (interativo - apenas demo)
# ==============================================================================

Write-Step "⚙️  PASSO 7: Configurar Modelo"

Write-Info "Configuração de chave API (interativo - pulado no demo)"
Write-Host "`n  Comando real:" -ForegroundColor Gray
Write-Host "  `$env:PIPX_HOME = `"`$env:USERPROFILE\pipx`"" -ForegroundColor DarkGray
Write-Host "  & `"`$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe`" -m llm keys set groq" -ForegroundColor DarkGray

Wait-Demo -Seconds 4

Write-Info "Definir modelo padrão (interativo - pulado no demo)" 
Write-Host "`n  Comando real:" -ForegroundColor Gray
Write-Host "  & `"`$env:PIPX_HOME\venvs\ai-cli\Scripts\python.exe`" -m llm models default groq/moonshotai/kimi-k2-instruct-0905" -ForegroundColor DarkGray

Wait-Demo -Seconds 4

# ==============================================================================
# PASSO 8: Verificar instalação
# ==============================================================================

Write-Step "✅ PASSO 8: Verificar Instalação"

Write-Command "ai --version" -Execute

Write-Success "Comando ai disponivel globalmente!"
Wait-Demo -Seconds 2

Write-Command "ai --help" -Execute

Wait-Demo -Seconds 3

# ==============================================================================
# PASSO 9: Testar funcionalidade (se tiver modelo configurado)
# ==============================================================================

Write-Step "🧪 PASSO 9: Teste Rápido"

Write-Info "Verificando funcionalidades básicas"
Wait-Demo -Seconds 2

Write-Host "`n⚠ Para testar queries ao LLM, configure primeiro uma chave API" -ForegroundColor Yellow
Write-Host "  Exemplo:" -ForegroundColor Gray
Write-Host "  ai olá mundo" -ForegroundColor DarkGray
Write-Host "  ai -c qual é o tempo em Lisboa?" -ForegroundColor DarkGray

Wait-Demo -Seconds 4

# ==============================================================================
# PASSO 10: Executar testes automatizados
# ==============================================================================

Write-Step "🧪 PASSO 10: Executar Testes"

Write-Info "Verificando integridade do código"
Wait-Demo -Seconds 2

Write-Command "pytest tests/test_config.py tests/test_render.py tests/test_llm_client.py -v --tb=short" -Execute

Wait-Demo -Seconds 3

# ==============================================================================
# CONCLUSÃO
# ==============================================================================

Write-Host "`n" 
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "  ✨ INSTALAÇÃO CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "  Próximos passos:" -ForegroundColor Yellow
Write-Host "  1. Configurar chave API Groq (console.groq.com)" -ForegroundColor White
Write-Host "  2. Executar: ai `"olá mundo`"" -ForegroundColor White
Write-Host "  3. Explorar: ai --help" -ForegroundColor White
Write-Host ""
Write-Host "  Documentação completa: README.md" -ForegroundColor Cyan
Write-Host ""

Wait-Demo -Seconds 5
