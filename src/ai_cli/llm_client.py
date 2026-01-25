"""Cliente para interagir com modelos LLM via biblioteca llm."""

import datetime
import locale
import logging
import os
import platform
import re
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterator, Optional

from .config import DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT, get_model
from .render import (
    console,
    render_error,
    render_markdown,
    render_info,
    render_warning,
)


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

# Logger
logger = logging.getLogger(__name__)

# Encoding do sistema
# Forçar UTF-8 no Windows para evitar problemas com caracteres Unicode
if sys.platform == "win32":
    SYSTEM_ENCODING = "utf-8"
else:
    SYSTEM_ENCODING = locale.getpreferredencoding(False) or "utf-8"

# Timeouts
COMMAND_TIMEOUT = 30  # segundos para comandos
LLM_TIMEOUT = 300     # 5 minutos para LLM (modelos grandes demoram)

# Limites
MAX_FILE_SIZE = 100_000  # ~100KB
MAX_RESPONSE_LENGTH = 50_000  # Limite de resposta


# =============================================================================
# TIPOS
# =============================================================================

@dataclass
class LLMResponse:
    """Resposta do modelo LLM."""
    content: str
    model: str
    tokens_used: Optional[int] = None
    duration_ms: Optional[int] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class SystemContext:
    """Contexto do sistema para o prompt."""
    os_name: str
    username: str
    cwd: str
    shell: str
    git_branch: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    @classmethod
    def current(cls) -> "SystemContext":
        """Obtém contexto atual do sistema."""
        return cls(
            os_name=platform.system(),
            username=os.getenv("USERNAME") or os.getenv("USER") or "unknown",
            cwd=os.getcwd(),
            shell=Path(os.getenv("SHELL") or os.getenv("COMSPEC") or "unknown").name,
            git_branch=_get_git_branch(),
        )


# =============================================================================
# FUNÇÕES AUXILIARES COM CACHE
# =============================================================================

@lru_cache(maxsize=1)
def _get_git_branch_cached(cwd: str) -> Optional[str]:
    """Obtém branch git atual (com cache por diretório)."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2,
            encoding=SYSTEM_ENCODING,
            errors="replace",
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    return None


def _get_git_branch() -> Optional[str]:
    """Wrapper para cache de git branch."""
    return _get_git_branch_cached(os.getcwd())


def _sanitize_for_prompt(text: str, max_length: int = 100) -> str:
    """Sanitiza texto para incluir no prompt (prevenir injection)."""
    # Remover caracteres de controlo
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    # Truncar
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    return sanitized


def _detect_file_encoding(filepath: str) -> str:
    """Detecta encoding de um ficheiro."""
    # Tentar UTF-8 primeiro (mais comum)
    encodings = ["utf-8", "utf-8-sig", SYSTEM_ENCODING, "latin-1"]
    
    for encoding in encodings:
        try:
            with open(filepath, "r", encoding=encoding) as f:
                f.read(1024)  # Ler amostra
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue
    
    return "utf-8"  # Fallback


# =============================================================================
# SYSTEM PROMPT
# =============================================================================

def get_contextualized_system_prompt(
    base_prompt: str = DEFAULT_SYSTEM_PROMPT,
    include_commands: bool = True,
) -> str:
    """
    Gera system prompt com contexto do sistema operativo.
    
    Args:
        base_prompt: Prompt base a incluir
        include_commands: Se deve incluir comandos disponíveis
    """
    ctx = SystemContext.current()
    
    # Sanitizar dados do utilizador
    safe_cwd = _sanitize_for_prompt(ctx.cwd, 200)
    safe_user = _sanitize_for_prompt(ctx.username, 50)
    
    git_info = f" (git: {ctx.git_branch})" if ctx.git_branch else ""
    
    context_section = f"""CONTEXTO: {ctx.os_name}, user {safe_user}, dir {safe_cwd}{git_info}"""

    commands_section = ""
    if include_commands:
        commands_section = """

FERRAMENTAS (usar SÓ quando pedido explicitamente ou absolutamente necessário):
Formato: [CMD: comando] - resultado aparece automaticamente.
- [CMD: ls], [CMD: cat ficheiro], [CMD: tree], [CMD: find padrão], [CMD: git status]

IMPORTANTE: NÃO uses ferramentas só por usar. Só quando fizer sentido."""

    return f"""És um assistente de IA versátil e útil. Respondes em português de Portugal, de forma concisa e natural.

{context_section}{commands_section}

Ajudas com programação, perguntas gerais, explicações, ideias, e qualquer outra coisa. 
Sê  direto e informativo. 

{base_prompt}"""


# =============================================================================
# EXECUÇÃO DE COMANDOS SEGUROS
# =============================================================================

# Importar uma vez no topo (lazy import para evitar circular)
_safe_commands_module = None


def _get_safe_commands():
    """Lazy import do módulo de comandos seguros."""
    global _safe_commands_module
    if _safe_commands_module is None:
        try:
            from .tools import safe_commands
            _safe_commands_module = safe_commands
        except ImportError:
            _safe_commands_module = False
    return _safe_commands_module


def execute_safe_commands(
    text: str,
    max_commands: int = 5,
    confirm: bool = False,
) -> str:
    """
    Detecta e executa comandos seguros na resposta do modelo.
    
    Args:
        text: Texto com possíveis [CMD: ...] 
        max_commands: Máximo de comandos a executar
        confirm: Se deve pedir confirmação ao utilizador
        
    Returns:
        Texto com resultados dos comandos inseridos
    """
    safe_commands = _get_safe_commands()
    if not safe_commands:
        return text
    
    # Padrão para detectar [CMD: ...]
    pattern = r'\[CMD:\s*([^\]]+)\]'
    matches = list(re.finditer(pattern, text))
    
    if not matches:
        return text
    
    # Limitar número de comandos
    if len(matches) > max_commands:
        render_warning(f"Limitado a {max_commands} comandos (encontrados {len(matches)})")
        matches = matches[:max_commands]
    
    # Confirmar se necessário
    if confirm and matches:
        cmds = [m.group(1).strip() for m in matches]
        console.print(f"[dim]Comandos a executar: {', '.join(cmds)}[/dim]")
        if not console.input("[dim]Continuar? (s/N): [/dim]").lower().startswith('s'):
            return text
    
    def replace_command(match) -> str:
        cmd_str = match.group(1).strip()
        parts = cmd_str.split(maxsplit=1)
        cmd_name = parts[0].lower()
        cmd_arg = parts[1] if len(parts) > 1 else None
        
        try:
            result = _execute_single_command(safe_commands, cmd_name, cmd_arg)
            return _format_command_result(result)
        except Exception as e:
            logger.warning(f"Erro ao executar comando '{cmd_str}': {e}")
            return f"\n**[Erro: {e}]**\n"
    
    return re.sub(pattern, replace_command, text, count=max_commands)


def _execute_single_command(safe_commands, cmd_name: str, cmd_arg: Optional[str]):
    """Executa um comando individual e retorna CommandResult."""
    if cmd_name in ["ls", "dir"]:
        return safe_commands.list_directory(cmd_arg or ".")
    elif cmd_name in ["cat", "type"]:
        if not cmd_arg:
            return safe_commands.CommandResult(success=False, error="Ficheiro não especificado")
        return safe_commands.read_file(cmd_arg)
    elif cmd_name == "pwd":
        return safe_commands.get_current_directory()
    elif cmd_name == "git":
        if cmd_arg:
            if "status" in cmd_arg:
                return safe_commands.get_git_status()
            elif "log" in cmd_arg:
                return safe_commands.get_git_log()
    elif cmd_name == "tree":
        # Executar tree command
        return _run_tree_command(cmd_arg)
    elif cmd_name in ["find", "grep", "search"]:
        if not cmd_arg:
            return safe_commands.CommandResult(success=False, error="Padrão de pesquisa não especificado")
        return _run_find_command(cmd_arg)
    
    return safe_commands.CommandResult(success=False, error=f"Comando não suportado: {cmd_name}")


def _run_tree_command(path: Optional[str]):
    """Executa tree e retorna CommandResult."""
    from .tools.safe_commands import CommandResult, run_safe_command
    
    target = path or "."
    # Usar tree simples como texto
    result = run_safe_command(["tree", "-L", "2", target] if os.name != "nt" else ["cmd", "/c", "tree", "/F", "/A", target])
    
    if result.success:
        return result
    else:
        # Fallback: usar o nosso tree.py
        try:
            from pathlib import Path
            from .tools.tree import build_tree, TreeConfig, TreeStats
            
            target_path = Path(target).resolve()
            if not target_path.is_dir():
                return CommandResult(success=False, error=f"Não é diretório: {target}")
            
            config = TreeConfig(max_depth=2, show_size=False, use_emoji=True)
            stats = TreeStats()
            
            # Simplificado: listar estrutura como texto
            lines = [f"📁 {target_path.name}/"]
            for item in sorted(target_path.iterdir()):
                if item.name.startswith("."):
                    continue
                prefix = "  📁 " if item.is_dir() else "  📄 "
                lines.append(f"{prefix}{item.name}")
            
            return CommandResult(success=True, output="\n".join(lines))
        except Exception as e:
            return CommandResult(success=False, error=str(e))


def _run_find_command(pattern: str):
    """Executa find/grep e retorna CommandResult."""
    from .tools.safe_commands import CommandResult, run_safe_command
    
    # Tentar ripgrep primeiro
    result = run_safe_command(["rg", "--no-heading", "-n", "-m", "10", pattern, "."])
    
    if result.success or "rg" in str(result.error):
        return result
    
    # Fallback para findstr (Windows)
    if os.name == "nt":
        result = run_safe_command(["findstr", "/S", "/N", "/I", pattern, "*.*"])
        return result
    
    # Fallback para grep (Unix)
    result = run_safe_command(["grep", "-r", "-n", "-I", pattern, "."])
    return result


def _format_command_result(result) -> str:
    """Formata CommandResult para inserir no texto (sem Rich tags)."""
    if hasattr(result, 'success'):
        if not result.success:
            return f"\n**Erro:** {result.error}"
        
        # Se tem output direto (pwd, git status, etc)
        if result.output:
            return f"\n```\n{result.output.strip()}\n```"
        
        # Se tem metadata com items (ls/dir) - formatação com emojis
        if result.metadata and "items" in result.metadata:
            lines = []
            for item in result.metadata["items"]:
                name = item["name"]
                if item["type"] == "dir":
                    lines.append(f"  📁 {name}/")
                else:
                    # Ícone por extensão
                    ext = name.split(".")[-1] if "." in name else ""
                    icon = _get_file_icon(ext)
                    size = item.get("size")
                    size_str = f" ({_format_size(size)})" if size else ""
                    lines.append(f"  {icon} {name}{size_str}")
            
            return "\n```\n" + "\n".join(lines) + "\n```"
    
    return "\n*(sem output)*"


def _get_file_icon(ext: str) -> str:
    """Retorna ícone baseado na extensão."""
    icons = {
        "py": "🐍", "js": "📜", "ts": "📘", "json": "📋",
        "md": "📝", "txt": "📄", "yaml": "📋", "yml": "📋",
        "toml": "⚙️", "html": "🌐", "css": "🎨", "sh": "🐚",
        "gitignore": "🙈", "license": "📜",
    }
    return icons.get(ext.lower(), "📄")


def _format_size(size: int) -> str:
    """Formata tamanho em bytes."""
    if size is None:
        return ""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


# =============================================================================
# STREAMING REAL
# =============================================================================

def _stream_subprocess_output(
    process: subprocess.Popen,
    callback: Callable[[str], None],
    timeout: Optional[float] = None,
) -> tuple[str, Optional[str]]:
    """
    Stream output de subprocess com callback para cada chunk.
    
    Returns:
        Tuple de (output_completo, erro_se_houver)
    """
    import select
    import time
    
    full_output = []
    error_output = []
    start_time = time.time()
    
    # Para Windows, usar threading
    if sys.platform == "win32":
        return _stream_windows(process, callback, timeout)
    
    # Unix: usar select para non-blocking read
    while True:
        if timeout and (time.time() - start_time) > timeout:
            process.kill()
            return "".join(full_output), "Timeout excedido"
        
        # Verificar se processo terminou
        if process.poll() is not None:
            # Ler resto do output
            if process.stdout:
                remaining = process.stdout.read()
                if remaining:
                    full_output.append(remaining)
                    callback(remaining)
            break
        
        # Ler disponível
        if process.stdout:
            try:
                ready, _, _ = select.select([process.stdout], [], [], 0.1)
                if ready:
                    chunk = process.stdout.read(1)  # Ler char a char para streaming real
                    if chunk:
                        full_output.append(chunk)
                        callback(chunk)
            except (ValueError, OSError):
                break
    
    # Ler stderr
    if process.stderr:
        error = process.stderr.read()
        if error:
            error_output.append(error)
    
    return "".join(full_output), "".join(error_output) if error_output else None


def _stream_windows(
    process: subprocess.Popen,
    callback: Callable[[str], None],
    timeout: Optional[float],
) -> tuple[str, Optional[str]]:
    """Streaming para Windows usando threading."""
    import queue
    import time
    
    output_queue: queue.Queue = queue.Queue()
    full_output = []
    error_output = []
    
    def reader(stream, q, is_error=False):
        try:
            for line in iter(stream.readline, ''):
                q.put(('error' if is_error else 'output', line))
            stream.close()
        except Exception:
            pass
        q.put(('done', None))
    
    # Iniciar threads de leitura
    stdout_thread = threading.Thread(
        target=reader, args=(process.stdout, output_queue), daemon=True
    )
    stderr_thread = threading.Thread(
        target=reader, args=(process.stderr, output_queue, True), daemon=True
    )
    
    stdout_thread.start()
    stderr_thread.start()
    
    start_time = time.time()
    done_count = 0
    
    while done_count < 2:
        if timeout and (time.time() - start_time) > timeout:
            process.kill()
            return "".join(full_output), "Timeout excedido"
        
        try:
            msg_type, content = output_queue.get(timeout=0.1)
            if msg_type == 'done':
                done_count += 1
            elif msg_type == 'output' and content:
                full_output.append(content)
                callback(content)
            elif msg_type == 'error' and content:
                error_output.append(content)
        except queue.Empty:
            continue
    
    return "".join(full_output), "".join(error_output) if error_output else None


# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def query_llm(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system_prompt: Optional[str] = None,
    stream: bool = True,
    timeout: Optional[float] = LLM_TIMEOUT,
    execute_commands: bool = True,
    continue_conversation: bool = False,
) -> Optional[LLMResponse]:
    """
    Envia uma query ao modelo LLM.
    
    Args:
        prompt: A pergunta/prompt para o modelo
        model: Alias do modelo a usar
        system_prompt: System prompt (usa DEFAULT se None)
        stream: Se True, mostra resposta em streaming
        timeout: Timeout em segundos (None = sem limite)
        execute_commands: Se deve executar [CMD: ...] na resposta
        continue_conversation: Se True, continua a conversa anterior (llm -c)
        
    Returns:
        LLMResponse com a resposta, ou None se erro crítico
    """
    import time
    start_time = time.time()
    
    # Validar prompt
    if not prompt.strip():
        render_error("Prompt vazio. Use: ai a tua pergunta aqui")
        return LLMResponse(content="", success=False, error="Prompt vazio", model=model)
    
    # Validar modelo
    try:
        model_config = get_model(model)
    except ValueError as e:
        render_error(str(e))
        return LLMResponse(content="", success=False, error=str(e), model=model)
    
    # Construir comando
    cmd = ["llm"]
    
    # Continuar conversa anterior
    if continue_conversation:
        cmd.append("-c")
        # Quando continua, não envia system prompt (já foi enviado)
    else:
        # Nova conversa - incluir system prompt
        system = system_prompt or get_contextualized_system_prompt()
        cmd.extend(["--system", system])
    
    cmd.extend(["-m", model_config.model_id, prompt])
    
    logger.debug(f"Executando: {' '.join(cmd[:4])}...")
    
    try:
        # Coletar resposta com spinner
        response_text = _query_with_spinner(cmd, timeout)
        
        if response_text is None:
            return None
        
        # Executar comandos seguros se houver
        if execute_commands and "[CMD:" in response_text:
            response_text = execute_safe_commands(response_text)
        
        # Copiar para clipboard
        from .render import copy_to_clipboard
        copied = False
        if response_text.strip():
            copied = copy_to_clipboard(response_text.strip())

        # Renderizar resposta em painel bonito
        duration_ms = int((time.time() - start_time) * 1000)
        if response_text.strip():
            render_markdown(response_text, duration=duration_ms / 1000.0, copied=copied)
        
        return LLMResponse(
            content=response_text,
            model=model_config.model_id,
            duration_ms=duration_ms,
            success=True,
        )
        
    except FileNotFoundError:
        render_error("Comando 'llm' não encontrado. Instala com: pip install llm")
        return LLMResponse(content="", success=False, error="llm não encontrado", model=model)
    except KeyboardInterrupt:
        console.print("\n[dim]Cancelado[/dim]")
        raise
    except Exception as e:
        logger.exception("Erro ao executar query")
        render_error(f"Erro inesperado: {e}")
        return LLMResponse(content="", success=False, error=str(e), model=model)


def _query_with_spinner(cmd: list[str], timeout: Optional[float]) -> Optional[str]:
    """
    Executa query com spinner (sem streaming de texto).
    Retorna o texto completo.
    """
    buffer = []
    
    # Preparar environment com UTF-8 forçado no Windows
    env = os.environ.copy()
    if sys.platform == "win32":
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding=SYSTEM_ENCODING,
        errors="replace",
        bufsize=1,  # Line buffered
        env=env,
    )
    
    try:
        # Spinner enquanto coleta output
        with console.status("[dim]A pensar...[/dim]", spinner="dots"):
            # Coletar stdout até acabar
            if process.stdout:
                for char in iter(lambda: process.stdout.read(1), ''):
                    buffer.append(char)
        
        process.wait(timeout=timeout)
        
        if process.returncode != 0 and process.stderr:
            error = process.stderr.read()
            if error:
                render_error(f"llm falhou: {error}")
                return None
        
        return "".join(buffer)
        
    except subprocess.TimeoutExpired:
        process.kill()
        render_error("Timeout - modelo demorou muito")
        return None


# =============================================================================
# FUNÇÕES DE FICHEIRO
# =============================================================================

def query_llm_with_file(
    filepath: str,
    prompt: str,
    model: str = DEFAULT_MODEL,
    stream: bool = True,
) -> Optional[LLMResponse]:
    """
    Envia conteúdo de um ficheiro ao modelo com um prompt.
    
    Args:
        filepath: Caminho para o ficheiro
        prompt: Pergunta sobre o ficheiro
        model: Alias do modelo
        stream: Se deve usar streaming
        
    Returns:
        LLMResponse com a resposta
    """
    path = Path(filepath)
    
    # Verificar existência
    if not path.exists():
        render_error(f"Ficheiro não encontrado: {filepath}")
        return None
    
    # Verificar tamanho
    file_size = path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        render_warning(f"Ficheiro grande ({file_size:,} bytes). A truncar...")
    
    # Ler ficheiro
    try:
        encoding = _detect_file_encoding(filepath)
        with open(filepath, "r", encoding=encoding, errors="replace") as f:
            content = f.read(MAX_FILE_SIZE)
    except PermissionError:
        render_error(f"Sem permissão para ler: {filepath}")
        return None
    except Exception as e:
        render_error(f"Erro ao ler ficheiro: {e}")
        return None
    
    # Detectar linguagem para syntax highlight no prompt
    extension = path.suffix.lower()
    lang_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".json": "json", ".yaml": "yaml", ".yml": "yaml",
        ".md": "markdown", ".sh": "bash", ".sql": "sql",
    }
    lang = lang_map.get(extension, "")
    
    full_prompt = f"""Ficheiro: {path.name}

```{lang}
{content}
```

{prompt}"""
    
    return query_llm(full_prompt, model=model, stream=stream)


def explain_file(
    filepath: str,
    model: str = DEFAULT_MODEL,
    detailed: bool = False,
    stream: bool = True,
) -> Optional[LLMResponse]:
    """
    Explica o código de um ficheiro.
    
    Args:
        filepath: Caminho para o ficheiro de código
        model: Alias do modelo
        detailed: Se deve dar explicação detalhada
        stream: Se deve usar streaming
        
    Returns:
        LLMResponse com a explicação
    """
    if detailed:
        prompt = """Explica este código em detalhe:
- Visão geral do que faz
- Principais funções/classes e seus propósitos
- Fluxo de execução
- Dependências importantes
- Possíveis melhorias"""
    else:
        prompt = "Explica este código de forma clara e concisa. Foca nos pontos principais."
    
    return query_llm_with_file(filepath, prompt, model=model, stream=stream)


# =============================================================================
# UTILIDADES EXPORTADAS
# =============================================================================

def clear_git_cache() -> None:
    """Limpa cache do git branch (útil após cd)."""
    _get_git_branch_cached.cache_clear()
