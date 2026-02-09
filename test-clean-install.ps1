# Script para testar instalacao limpa do AI CLI
# Simula uma maquina nova removendo instalacoes anteriores

Write-Host "=== AI CLI - Teste de Instalacao Limpa ===" -ForegroundColor Cyan
Write-Host ""

# Passo 1: Atualizar PATH e verificar pipx
Write-Host "[1/6] Verificando pipx..." -ForegroundColor Yellow

# Recarregar PATH da sessao
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

if (Get-Command pipx -ErrorAction SilentlyContinue) {
    Write-Host "[OK] pipx encontrado" -ForegroundColor Green
    
    # Remover instalacao anterior se existir
    Write-Host ""
    Write-Host "[2/6] Removendo instalacao anterior do ai-cli..." -ForegroundColor Yellow
    pipx uninstall ai-cli 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Instalacao anterior removida" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Nenhuma instalacao anterior encontrada" -ForegroundColor Gray
    }
} else {
    Write-Host "[ERRO] pipx nao encontrado mesmo apos recarregar PATH" -ForegroundColor Red
    exit 1
}

# Passo 2: Verificar Python
Write-Host ""
Write-Host "[3/6] Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "[OK] $pythonVersion" -ForegroundColor Green

# Passo 3: Instalar ai-cli
Write-Host ""
Write-Host "[4/6] Instalando ai-cli com pipx..." -ForegroundColor Yellow
pipx install -e .
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] ai-cli instalado" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Falha na instalacao" -ForegroundColor Red
    exit 1
}

# Passo 4: Injetar dependencias
Write-Host ""
Write-Host "[5/6] Instalando dependencias LLM..." -ForegroundColor Yellow
pipx inject ai-cli llm
pipx inject ai-cli llm-groq
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Falha ao instalar dependencias" -ForegroundColor Red
    exit 1
}

# Passo 5: Verificar instalacao
Write-Host ""
Write-Host "[6/6] Verificando instalacao..." -ForegroundColor Yellow
$aiVersion = ai --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] $aiVersion" -ForegroundColor Green
} else {
    Write-Host "[ERRO] Comando 'ai' nao encontrado" -ForegroundColor Red
    exit 1
}

# Resumo
Write-Host ""
Write-Host "=== Instalacao Concluida ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor White
Write-Host "1. Configure sua chave API: llm keys set groq" -ForegroundColor Yellow
Write-Host "2. Defina o modelo padrao: llm models default groq/moonshotai/kimi-k2-instruct-0905" -ForegroundColor Yellow
Write-Host "3. Teste o comando: ai ola mundo" -ForegroundColor Yellow
Write-Host ""
