# 🎥 Guia para Gravar Demo de Instalação

## Método 1: Gravar com Windows Terminal + OBS Studio (Recomendado)

### Preparação
1. **Instalar OBS Studio**: https://obsproject.com/
2. **Configurar Windows Terminal**:
   - Abrir Windows Terminal
   - Settings → Appearance → Theme: Dark
   - Aumentar tamanho da fonte para 14-16pt (Settings → Defaults → Appearance)
   - Ativar Acrylic transparency para visual moderno

3. **Configurar OBS**:
   - Scene: "Terminal Demo"
   - Source: Display Capture (ou Window Capture do terminal)
   - Resolução recomendada: 1920x1080 ou 1280x720
   - FPS: 30
   - Formato de saída: MP4 (H.264)

### Gravar
```powershell
# No Windows Terminal
cd C:\Projectos\ai-cli

# Executar script de demonstração
.\demo-install.ps1

# OU modo rápido (sem pausas longas)
.\demo-install.ps1 -Fast

# OU com limpeza prévia
.\demo-install.ps1 -Clean
```

---

## Método 2: Gravar com VHS (Terminal Animator) - Automático

**VHS** gera vídeos/GIFs de terminal de forma totalmente automática.

### Instalação VHS
```powershell
# Instalar via Scoop (Windows)
scoop install vhs

# OU baixar binário: https://github.com/charmbracelet/vhs/releases
```

### Criar arquivo de tape (ai-cli-demo.tape)
(Já criarei este arquivo a seguir)

### Gravar
```powershell
vhs ai-cli-demo.tape
```

Saída: `ai-cli-demo.gif` ou `ai-cli-demo.mp4`

---

## Método 3: Asciinema (Para Web)

Grava sessão de terminal que pode ser reproduzida no browser.

```powershell
# Instalar
pip install asciinema

# Gravar
asciinema rec ai-cli-install.cast

# Durante gravação, executar:
.\demo-install.ps1 -Fast

# Parar: Ctrl+D

# Upload (opcional)
asciinema upload ai-cli-install.cast

# Converter para GIF (requer agg)
pip install asciinema-agg
agg ai-cli-install.cast ai-cli-install.gif
```

---

## Método 4: PowerShell Transcript (Texto Simples)

Para documentação textual:

```powershell
# Iniciar transcrição
Start-Transcript -Path "install-demo-transcript.txt"

# Executar script
.\demo-install.ps1

# Parar
Stop-Transcript
```

---

## 🎬 Dicas de Produção

### Antes de Gravar
- [ ] Fechar aplicações desnecessárias
- [ ] Limpar histórico do terminal (`Clear-History`)
- [ ] Aumentar tamanho da fonte do terminal
- [ ] Desativar notificações (Windows: Focus Assist)
- [ ] Garantir boa iluminação se for screencast com webcam

### Durante a Gravação
- [ ] Usar o script `demo-install.ps1` para consistência
- [ ] Narrar se for tutorial (opcional)
- [ ] Deixar pausas para leitura (já incluídas no script)
- [ ] Mostrar resultado final funcionando

### Pós-Produção (Opcional)
- Adicionar música de fundo
- Legendas em pontos-chave
- Zoom em comandos importantes
- Cortar erros/tempos mortos

---

## 📊 Estrutura do Vídeo (Sugerida)

| Tempo | Conteúdo |
|-------|----------|
| 0:00 - 0:10 | Intro/Título (AI CLI) |
| 0:10 - 0:30 | Verificar Python |
| 0:30 - 1:00 | Instalar pipx |
| 1:00 - 2:00 | Instalar ai-cli com pipx |
| 2:00 - 2:30 | Injetar dependências (llm) |
| 2:30 - 3:00 | Instalar plugin Groq |
| 3:00 - 4:00 | Configurar chave API |
| 4:00 - 4:30 | Testar comando `ai` |
| 4:30 - 5:00 | Exemplo de uso |
| 5:00 - 5:15 | Conclusão/CTA |

**Duração total**: ~5 minutos

---

## 🚀 Quick Start

```powershell
# Executar AGORA (gravando com OBS ou similar)
cd C:\Projectos\ai-cli
.\demo-install.ps1

# Mais rápido (para vídeos curtos)
.\demo-install.ps1 -Fast
```

---

## 📤 Onde Publicar

- **GitHub README**: Adicionar GIF animado
- **YouTube**: Tutorial completo
- **Twitter/X**: Clip de 30seg mostrando instalação
- **LinkedIn**: Demonstração profissional
- **Dev.to / Medium**: Artigo com vídeo embebido
