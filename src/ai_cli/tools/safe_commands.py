"""Comandos seguros (read-only) que o LLM pode executar."""

import logging
import mimetypes
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURAÇÃO DE SEGURANÇA
# =============================================================================

class SecurityLevel(Enum):
    """Níveis de segurança para comandos."""
    STRICT = "strict"      # Só dentro do CWD
    NORMAL = "normal"      # Paths relativos ok
    RELAXED = "relaxed"    # Qualquer path (perigoso)


# Configuração global
SECURITY_LEVEL = SecurityLevel.STRICT
COMMAND_TIMEOUT = 5  # segundos
MAX_FILE_SIZE = 1_000_000  # 1MB
MAX_LINES = 100

# Extensões seguras para leitura
SAFE_TEXT_EXTENSIONS = {
    ".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".conf", ".sh", ".bash", ".zsh",
    ".html", ".css", ".xml", ".sql", ".r", ".rs", ".go", ".java",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".pl",
    ".lua", ".vim", ".dockerfile", ".makefile", ".gitignore",
}

# Paths bloqueados (nunca ler)
BLOCKED_PATHS = {
    "/etc/passwd", "/etc/shadow", "/etc/hosts",
    "~/.ssh", "~/.aws", "~/.config",
    ".env", ".env.local", ".env.production",
    "secrets.json", "credentials.json",
}


# =============================================================================
# TIPOS
# =============================================================================

@dataclass
class CommandResult:
    """Resultado de um comando seguro."""
    success: bool
    output: str = ""
    error: Optional[str] = None
    truncated: bool = False
    metadata: dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "truncated": self.truncated,
            **self.metadata,
        }


# =============================================================================
# VALIDAÇÃO DE SEGURANÇA
# =============================================================================

def _normalize_path(path: str) -> Path:
    """Normaliza e resolve path."""
    return Path(path).expanduser().resolve()


def _is_path_safe(path: str, base_dir: Optional[Path] = None) -> tuple[bool, str]:
    """
    Verifica se path é seguro para aceder.
    
    Returns:
        Tuple de (é_seguro, razão_se_não)
    """
    try:
        normalized = _normalize_path(path)
        base = base_dir or Path.cwd()
        
        # Verificar paths bloqueados
        path_str = str(normalized).lower()
        for blocked in BLOCKED_PATHS:
            blocked_expanded = str(Path(blocked).expanduser()).lower()
            if path_str == blocked_expanded or path_str.startswith(blocked_expanded):
                return False, f"Path bloqueado por segurança: {blocked}"
        
        # Verificar nível de segurança
        if SECURITY_LEVEL == SecurityLevel.STRICT:
            # Deve estar dentro do CWD
            try:
                normalized.relative_to(base)
            except ValueError:
                return False, "Path fora do diretório atual (modo strict)"
        
        elif SECURITY_LEVEL == SecurityLevel.NORMAL:
            # Não permitir paths absolutos perigosos
            dangerous_prefixes = ["/etc", "/root", "/var", "/usr", "/bin", "/sbin"]
            for prefix in dangerous_prefixes:
                if path_str.startswith(prefix):
                    return False, f"Path de sistema não permitido: {prefix}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Erro ao validar path: {e}"


def _is_text_file(filepath: Path) -> bool:
    """Verifica se ficheiro é texto (não binário)."""
    # Verificar por extensão primeiro
    if filepath.suffix.lower() in SAFE_TEXT_EXTENSIONS:
        return True
    
    # Verificar por mimetype
    mime_type, _ = mimetypes.guess_type(str(filepath))
    if mime_type and mime_type.startswith("text/"):
        return True
    
    # Verificar primeiros bytes
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(1024)
            # Se tem null bytes, provavelmente é binário
            if b"\x00" in chunk:
                return False
            # Tentar decodificar como UTF-8
            try:
                chunk.decode("utf-8")
                return True
            except UnicodeDecodeError:
                return False
    except Exception:
        return False


# =============================================================================
# COMANDOS SEGUROS
# =============================================================================

def run_safe_command(
    cmd: list[str],
    cwd: Optional[str] = None,
    timeout: int = COMMAND_TIMEOUT,
) -> CommandResult:
    """Executa comando seguro e retorna output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        
        return CommandResult(
            success=result.returncode == 0,
            output=result.stdout,
            error=result.stderr if result.returncode != 0 else None,
        )
        
    except subprocess.TimeoutExpired:
        return CommandResult(
            success=False,
            error=f"Comando expirou após {timeout}s",
        )
    except FileNotFoundError:
        return CommandResult(
            success=False,
            error=f"Comando não encontrado: {cmd[0]}",
        )
    except Exception as e:
        return CommandResult(success=False, error=str(e))


def list_directory(path: str = ".") -> CommandResult:
    """Lista conteúdo de um diretório."""
    # Validar segurança
    is_safe, reason = _is_path_safe(path)
    if not is_safe:
        return CommandResult(success=False, error=reason)
    
    try:
        p = _normalize_path(path)
        
        if not p.exists():
            return CommandResult(success=False, error=f"Caminho não existe: {path}")
        
        if not p.is_dir():
            return CommandResult(success=False, error=f"Não é um diretório: {path}")
        
        items = []
        for item in sorted(p.iterdir()):
            try:
                items.append({
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                })
            except (PermissionError, OSError):
                continue
        
        return CommandResult(
            success=True,
            output="",  # Será formatado pelo LLM client
            metadata={"items": items, "path": str(p)},
        )
        
    except Exception as e:
        return CommandResult(success=False, error=str(e))


def read_file(filepath: str, max_lines: int = MAX_LINES) -> CommandResult:
    """Lê conteúdo de um ficheiro de texto."""
    # Validar segurança
    is_safe, reason = _is_path_safe(filepath)
    if not is_safe:
        return CommandResult(success=False, error=reason)
    
    try:
        p = _normalize_path(filepath)
        
        if not p.exists():
            return CommandResult(success=False, error=f"Ficheiro não existe: {filepath}")
        
        if not p.is_file():
            return CommandResult(success=False, error=f"Não é um ficheiro: {filepath}")
        
        # Verificar tamanho
        file_size = p.stat().st_size
        if file_size > MAX_FILE_SIZE:
            return CommandResult(success=False, error=f"Ficheiro muito grande (>1MB)")
        
        # Verificar se é texto
        if not _is_text_file(p):
            return CommandResult(success=False, error="Ficheiro binário não pode ser lido")
        
        # Ler ficheiro
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(max_lines)]
            lines = [l for l in lines if l]  # Remover vazias
        
        content = "".join(lines)
        truncated = len(lines) >= max_lines
        
        return CommandResult(
            success=True,
            output=content,
            truncated=truncated,
            metadata={"filepath": str(p), "lines_read": len(lines)},
        )
        
    except Exception as e:
        return CommandResult(success=False, error=str(e))


def get_git_status() -> CommandResult:
    """Obtém status do git."""
    if not _git_available():
        return CommandResult(success=False, error="Git não está instalado")
    
    return run_safe_command(["git", "status", "--short", "--branch"])


def get_git_log(n: int = 5) -> CommandResult:
    """Obtém últimos N commits."""
    if not _git_available():
        return CommandResult(success=False, error="Git não está instalado")
    
    n = max(1, min(n, 50))  # Entre 1 e 50
    return run_safe_command(["git", "log", f"-{n}", "--oneline"])


def get_current_directory() -> CommandResult:
    """Obtém diretório atual."""
    return CommandResult(success=True, output=os.getcwd())


# =============================================================================
# AUXILIARES
# =============================================================================

@lru_cache(maxsize=1)
def _git_available() -> bool:
    """Verifica se git está instalado."""
    try:
        subprocess.run(["git", "--version"], capture_output=True, timeout=2)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# =============================================================================
# REGISTRY DE COMANDOS
# =============================================================================

SAFE_COMMANDS = {
    "ls": list_directory,
    "dir": list_directory,
    "cat": read_file,
    "type": read_file,
    "pwd": get_current_directory,
    "git_status": get_git_status,
    "git_log": get_git_log,
}
