"""Configuração de modelos e sistema com persistência."""

import json
import locale
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional


# =============================================================================
# PATHS DE CONFIGURAÇÃO
# =============================================================================

def get_config_dir() -> Path:
    """Obtém diretório de configuração (XDG compliant)."""
    if os.name == "nt":  # Windows
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:  # Unix/Linux/Mac
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    
    config_dir = base / "ai-cli"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Obtém caminho do ficheiro de configuração."""
    return get_config_dir() / "config.json"


# =============================================================================
# MODELOS
# =============================================================================

@dataclass(frozen=True)
class ModelConfig:
    """Configuração de um modelo LLM."""
    
    alias: str
    model_id: str
    description: str
    tokens_per_sec: Optional[int] = None
    is_custom: bool = False  # Modelo adicionado pelo utilizador
    
    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário (para JSON)."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelConfig":
        """Cria a partir de dicionário."""
        return cls(**data)


# Modelos built-in (Groq free tier recomendados)
BUILTIN_MODELS: dict[str, ModelConfig] = {
    "fast": ModelConfig(
        alias="fast",
        model_id="llama-3.3-70b-versatile",
        description="Llama 3.3 70B - Rápido + qualidade",
        tokens_per_sec=280,
    ),
    "quick": ModelConfig(
        alias="quick",
        model_id="llama-3.1-8b-instant",
        description="Llama 3.1 8B - Ultra-rápido",
        tokens_per_sec=560,
    ),
    "qwen": ModelConfig(
        alias="qwen",
        model_id="qwen2.5-coder-32b-instruct",
        description="Qwen2.5 32B - Código Python/JS",
        tokens_per_sec=200,
    ),
    "mixtral": ModelConfig(
        alias="mixtral",
        model_id="mixtral-8x7b-32768",
        description="Mixtral 8x7B - Contexto longo (32k)",
        tokens_per_sec=250,
    ),
}


# =============================================================================
# CONFIGURAÇÃO PERSISTENTE
# =============================================================================

@dataclass
class AppConfig:
    """Configuração da aplicação (persistida em JSON)."""
    
    default_model: Optional[str] = None  # None = usar default do sistema (llm)
    custom_models: dict[str, dict[str, Any]] = field(default_factory=dict)
    system_prompt: str = "Responde sempre em português de Portugal. Sê conciso e direto."
    stream_by_default: bool = True
    show_tokens: bool = False
    
    # Histórico de modelos usados (para sugestões)
    recent_models: list[str] = field(default_factory=list)
    max_recent: int = 5
    
    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "default_model": self.default_model,
            "custom_models": self.custom_models,
            "system_prompt": self.system_prompt,
            "stream_by_default": self.stream_by_default,
            "show_tokens": self.show_tokens,
            "recent_models": self.recent_models,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        """Cria a partir de dicionário."""
        # Garantir compatibilidade com versões antigas
        default_prompt = "Responde sempre em português de Portugal. Sê conciso e direto."
        
        # Migrar 'maverick' para None se estiver na config antiga
        def_model = data.get("default_model")
        if def_model == "maverick":
            def_model = None
            
        return cls(
            default_model=def_model,
            custom_models=data.get("custom_models", {}),
            system_prompt=data.get("system_prompt", default_prompt),
            stream_by_default=data.get("stream_by_default", True),
            show_tokens=data.get("show_tokens", False),
            recent_models=data.get("recent_models", []),
        )
    
    def add_to_recent(self, model: str) -> None:
        """Adiciona modelo ao histórico recente."""
        if model in self.recent_models:
            self.recent_models.remove(model)
        self.recent_models.insert(0, model)
        self.recent_models = self.recent_models[:self.max_recent]


# Configuração global (singleton)
_config: Optional[AppConfig] = None


def load_config() -> AppConfig:
    """Carrega configuração do ficheiro."""
    global _config
    
    if _config is not None:
        return _config
    
    config_file = get_config_file()
    
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            _config = AppConfig.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # Config corrupta, usar default
            _config = AppConfig()
    else:
        _config = AppConfig()
    
    return _config


def save_config(config: Optional[AppConfig] = None) -> None:
    """Guarda configuração no ficheiro."""
    global _config
    
    if config is not None:
        _config = config
    
    if _config is None:
        return
    
    config_file = get_config_file()
    
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(_config.to_dict(), f, indent=2, ensure_ascii=False)


def reset_config() -> AppConfig:
    """Reset para configuração default."""
    global _config
    _config = AppConfig()
    save_config()
    return _config


# =============================================================================
# GESTÃO DE MODELOS
# =============================================================================

def get_all_models() -> dict[str, ModelConfig]:
    """Obtém todos os modelos (built-in + custom)."""
    config = load_config()
    
    models = dict(BUILTIN_MODELS)
    
    # Adicionar modelos custom
    for alias, data in config.custom_models.items():
        try:
            models[alias] = ModelConfig.from_dict(data)
        except (KeyError, TypeError):
            # Ignorar modelos custom corruptos
            continue
    
    return models


def get_model(alias: str) -> ModelConfig:
    """Obtém configuração de um modelo pelo alias."""
    models = get_all_models()
    
    if alias not in models:
        available = ", ".join(sorted(models.keys()))
        raise ValueError(f"Modelo '{alias}' não encontrado. Disponíveis: {available}")
    
    return models[alias]


def list_models() -> list[ModelConfig]:
    """Lista todos os modelos disponíveis."""
    return list(get_all_models().values())


def get_default_model() -> Optional[str]:
    """Obtém o modelo default atual."""
    return load_config().default_model


def set_default_model(alias: str) -> None:
    """
    Define o modelo default.
    
    Args:
        alias: Alias do modelo
        
    Raises:
        ValueError: Se modelo não existe
    """
    # Validar que existe
    get_model(alias)
    
    config = load_config()
    config.default_model = alias
    config.add_to_recent(alias)
    save_config()


def add_custom_model(
    alias: str,
    model_id: str,
    description: str = "",
    tokens_per_sec: Optional[int] = None,
) -> ModelConfig:
    """
    Adiciona um modelo custom.
    
    Args:
        alias: Nome curto para o modelo
        model_id: ID real do modelo no 'llm'
        description: Descrição opcional
        tokens_per_sec: Velocidade estimada
        
    Returns:
        ModelConfig criado
        
    Raises:
        ValueError: Se alias é built-in
    """
    if alias in BUILTIN_MODELS:
        raise ValueError(f"'{alias}' é um modelo built-in e não pode ser substituído")
    
    model = ModelConfig(
        alias=alias,
        model_id=model_id,
        description=description or f"Modelo custom: {model_id}",
        tokens_per_sec=tokens_per_sec,
        is_custom=True,
    )
    
    config = load_config()
    config.custom_models[alias] = model.to_dict()
    save_config()
    
    return model


def remove_custom_model(alias: str) -> bool:
    """
    Remove um modelo custom.
    
    Returns:
        True se removido, False se não existia
    """
    config = load_config()
    
    if alias in config.custom_models:
        del config.custom_models[alias]
        
        # Se era o default, reverter para system default
        if config.default_model == alias:
            config.default_model = None
        
        # Remover do histórico
        if alias in config.recent_models:
            config.recent_models.remove(alias)
        
        save_config()
        return True
    
    return False


# =============================================================================
# DESCOBERTA DE MODELOS DO LLM
# =============================================================================

def discover_llm_models() -> list[str]:
    """
    Descobre modelos disponíveis no 'llm'.
    
    Returns:
        Lista de model IDs disponíveis
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "llm", "models", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding=locale.getpreferredencoding(False) or "utf-8",
        )
        
        if result.returncode == 0:
            models_data = json.loads(result.stdout)
            return [m.get("model_id", m.get("name", "")) for m in models_data if m]
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    
    return []


def validate_model_exists(model_id: str) -> bool:
    """Verifica se modelo existe no 'llm'."""
    available = discover_llm_models()
    return not available or model_id in available  # Se falhar descoberta, assume válido


# =============================================================================
# SELEÇÃO INTERATIVA
# =============================================================================

def select_model_interactive() -> Optional[str]:
    """
    Apresenta menu interativo para selecionar modelo.
    
    Returns:
        Alias do modelo selecionado, ou None se cancelado
    """
    try:
        from rich.console import Console
        from rich.prompt import Prompt
        from rich.table import Table
    except ImportError:
        return _select_model_simple()
    
    console = Console()
    models = get_all_models()
    config = load_config()
    
    # Criar tabela
    table = Table(title="Modelos Disponíveis", show_header=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Alias", style="cyan")
    table.add_column("Descrição")
    table.add_column("Velocidade", justify="right")
    table.add_column("", width=3)  # Indicador de default
    
    # Ordenar: recentes primeiro, depois alfabético
    sorted_aliases = sorted(models.keys(), key=lambda x: (
        x not in config.recent_models,
        config.recent_models.index(x) if x in config.recent_models else 999,
        x
    ))
    
    for i, alias in enumerate(sorted_aliases, 1):
        model = models[alias]
        speed = f"{model.tokens_per_sec} t/s" if model.tokens_per_sec else "-"
        is_default = "✓" if alias == config.default_model else ""
        custom_tag = "[dim](custom)[/dim]" if model.is_custom else ""
        
        table.add_row(
            str(i),
            alias,
            f"{model.description} {custom_tag}",
            speed,
            is_default,
        )
    
    console.print(table)
    console.print()
    
    # Prompt para seleção
    choice = Prompt.ask(
        "Escolhe modelo (número ou alias)",
        default=config.default_model,
    )
    
    # Interpretar escolha
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(sorted_aliases):
            return sorted_aliases[idx]
    elif choice in models:
        return choice
    
    return None


def _select_model_simple() -> Optional[str]:
    """Seleção simples sem Rich."""
    models = get_all_models()
    config = load_config()
    
    print("\nModelos disponíveis:")
    aliases = sorted(models.keys())
    
    for i, alias in enumerate(aliases, 1):
        model = models[alias]
        default_marker = " (default)" if alias == config.default_model else ""
        print(f"  {i}. {alias} - {model.description}{default_marker}")
    
    print()
    try:
        choice = input(f"Escolhe (1-{len(aliases)}) ou alias [{config.default_model}]: ").strip()
    except (KeyboardInterrupt, EOFError):
        return None
    
    if not choice:
        return config.default_model
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(aliases):
            return aliases[idx]
    elif choice in models:
        return choice
    
    return None


# =============================================================================
# SYSTEM PROMPT
# =============================================================================

DEFAULT_SYSTEM_PROMPT = "Responde sempre em português de Portugal. Sê conciso e direto."


def get_system_prompt() -> str:
    """Obtém system prompt configurado."""
    return load_config().system_prompt


def set_system_prompt(prompt: str) -> None:
    """Define system prompt."""
    config = load_config()
    config.system_prompt = prompt
    save_config()


# =============================================================================
# COMPATIBILIDADE
# =============================================================================

# Para compatibilidade com código existente
DEFAULT_MODEL = get_default_model()
MODELS = BUILTIN_MODELS  # Para acesso direto se necessário


def validate_model(alias: str) -> bool:
    """Verifica se alias é válido."""
    try:
        get_model(alias)
        return True
    except ValueError:
        return False
