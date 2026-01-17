"""Comando tree - mostra estrutura de pastas com limites e features avançadas."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

import click
from rich.tree import Tree

from ..render import console, render_error


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

MAX_FILES_PER_DIR = 100      # Limite de ficheiros por diretório
MAX_TOTAL_ITEMS = 1000       # Limite total de items
MAX_DEPTH_SAFETY = 20        # Profundidade máxima (evitar recursão infinita)

# Pastas a ignorar por defeito
DEFAULT_IGNORE = {
    ".git", ".svn", ".hg", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".tox", ".nox", ".eggs", "*.egg-info",
    "node_modules", ".venv", "venv", "env", "dist", "build",
    ".idea", ".vscode", ".DS_Store",
}

# Ícones (emoji, fallback)
FILE_ICONS = {
    ".py": ("🐍", "[PY]"),
    ".js": ("📜", "[JS]"),
    ".ts": ("📘", "[TS]"),
    ".json": ("📋", "[JSON]"),
    ".md": ("📝", "[MD]"),
    ".txt": ("📄", "[TXT]"),
    ".yaml": ("📋", "[YML]"),
    ".yml": ("📋", "[YML]"),
    ".html": ("🌐", "[HTML]"),
    ".css": ("🎨", "[CSS]"),
    ".sh": ("🐚", "[SH]"),
}

DEFAULT_ICON = ("📄", "[FILE]")
DIR_ICON = ("📁", "[DIR]")


# =============================================================================
# TIPOS
# =============================================================================

@dataclass
class TreeStats:
    """Estatísticas da árvore."""
    directories: int = 0
    files: int = 0
    total_size: int = 0
    hidden_items: int = 0
    truncated_dirs: int = 0


@dataclass
class TreeConfig:
    """Configuração da árvore."""
    max_depth: int = 3
    show_hidden: bool = False
    show_size: bool = True
    use_emoji: bool = True
    ignore_patterns: set[str] = field(default_factory=lambda: DEFAULT_IGNORE.copy())
    respect_gitignore: bool = True
    max_files_per_dir: int = MAX_FILES_PER_DIR


# =============================================================================
# FUNÇÕES
# =============================================================================

def _supports_emoji() -> bool:
    """Verifica se terminal suporta emoji."""
    if os.name == "nt":
        return os.environ.get("WT_SESSION") is not None
    return True


def get_file_icon(suffix: str, use_emoji: bool = True) -> str:
    """Retorna ícone baseado na extensão."""
    icons = FILE_ICONS.get(suffix.lower(), DEFAULT_ICON)
    return icons[0] if use_emoji and _supports_emoji() else icons[1]


def get_dir_icon(use_emoji: bool = True) -> str:
    """Retorna ícone de diretório."""
    return DIR_ICON[0] if use_emoji and _supports_emoji() else DIR_ICON[1]


def format_size(size: int) -> str:
    """Formata tamanho em bytes."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size}{unit}" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def should_ignore(name: str, patterns: set[str]) -> bool:
    """Verifica se deve ignorar."""
    if name in patterns:
        return True
    for pattern in patterns:
        if pattern.startswith("*") and name.endswith(pattern[1:]):
            return True
    return False


def load_gitignore(directory: Path) -> set[str]:
    """Carrega .gitignore se existir."""
    gitignore = directory / ".gitignore"
    patterns = set()
    
    if gitignore.exists():
        try:
            with open(gitignore, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.add(line.rstrip("/"))
        except Exception:
            pass
    
    return patterns


def build_tree(
    path: Path,
    config: TreeConfig,
    stats: TreeStats,
    current_depth: int = 0,
) -> Optional[Tree]:
    """Constrói árvore Rich."""
    if current_depth >= config.max_depth or current_depth >= MAX_DEPTH_SAFETY:
        return None
    
    dir_icon = get_dir_icon(config.use_emoji)
    tree = Tree(f"[bold green]{dir_icon} {path.name}/[/bold green]" if current_depth == 0 
                else f"[bold blue]{dir_icon} {path.name}/[/bold blue]")
    
    # Carregar gitignore
    ignore = config.ignore_patterns.copy()
    if config.respect_gitignore:
        ignore.update(load_gitignore(path))
    
    try:
        entries = list(path.iterdir())
    except PermissionError:
        tree.add("[red]⚠ Sem permissão[/red]")
        return tree
    except Exception:
        return tree
    
    # Ordenar e filtrar
    entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))
    visible = []
    
    for entry in entries:
        if not config.show_hidden and entry.name.startswith("."):
            stats.hidden_items += 1
            continue
        if should_ignore(entry.name, ignore):
            stats.hidden_items += 1
            continue
        visible.append(entry)
    
    # Truncar se necessário
    truncated = len(visible) > config.max_files_per_dir
    if truncated:
        stats.truncated_dirs += 1
        visible = visible[:config.max_files_per_dir]
    
    # Adicionar entries
    for entry in visible:
        if entry.is_dir():
            stats.directories += 1
            subtree = build_tree(entry, config, stats, current_depth + 1)
            if subtree:
                tree.add(subtree)
            else:
                tree.add(f"[dim blue]{get_dir_icon(config.use_emoji)} {entry.name}/...[/dim blue]")
        else:
            stats.files += 1
            try:
                size = entry.stat().st_size
                stats.total_size += size
                icon = get_file_icon(entry.suffix, config.use_emoji)
                size_str = f" [dim]({format_size(size)})[/dim]" if config.show_size else ""
                tree.add(f"{icon} {entry.name}{size_str}")
            except Exception:
                icon = get_file_icon(entry.suffix, config.use_emoji)
                tree.add(f"{icon} {entry.name}")
    
    if truncated:
        remaining = len(entries) - config.max_files_per_dir
        tree.add(f"[dim]... e mais {remaining} items[/dim]")
    
    return tree


# =============================================================================
# COMANDO CLI
# =============================================================================

@click.command("tree")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("-d", "--depth", default=3, help="Profundidade máxima (default: 3)")
@click.option("-a", "--all", "show_all", is_flag=True, help="Mostra ficheiros ocultos")
@click.option("-s", "--size/--no-size", default=True, help="Mostra tamanhos")
@click.option("--no-emoji", is_flag=True, help="Desativa emojis")
@click.option("--json", "as_json", is_flag=True, help="Output JSON")
def tree_cmd(
    path: str,
    depth: int,
    show_all: bool,
    size: bool,
    no_emoji: bool,
    as_json: bool,
) -> None:
    """Mostra estrutura de pastas.
    
    \b
    Exemplos:
      ai tree
      ai tree src -d 2
      ai tree --json > tree.json
    """
    target = Path(path).resolve()
    
    if not target.is_dir():
        render_error(f"'{path}' não é um diretório")
        return
    
    config = TreeConfig(
        max_depth=min(depth, MAX_DEPTH_SAFETY),
        show_hidden=show_all,
        show_size=size,
        use_emoji=not no_emoji,
        ignore_patterns=set() if show_all else DEFAULT_IGNORE.copy(),
        respect_gitignore=not show_all,
    )
    
    stats = TreeStats()
    
    if as_json:
        # JSON output
        def dir_to_dict(p: Path, d: int = 0) -> dict:
            if d >= config.max_depth:
                return {"name": p.name, "type": "dir", "truncated": True}
            
            result = {"name": p.name, "type": "dir", "children": []}
            try:
                for e in sorted(p.iterdir()):
                    if not config.show_hidden and e.name.startswith("."):
                        continue
                    if should_ignore(e.name, config.ignore_patterns):
                        continue
                    
                    if e.is_dir():
                        result["children"].append(dir_to_dict(e, d + 1))
                    else:
                        result["children"].append({
                            "name": e.name,
                            "type": "file",
                            "size": e.stat().st_size if size else None,
                        })
            except Exception:
                result["error"] = "permission denied"
            
            return result
        
        print(json.dumps(dir_to_dict(target), indent=2, ensure_ascii=False))
    
    else:
        # Rich tree
        tree = build_tree(target, config, stats)
        
        if tree:
            console.print(tree)
            console.print()
            
            # Estatísticas
            parts = [
                f"[cyan]{stats.directories}[/cyan] diretórios",
                f"[cyan]{stats.files}[/cyan] ficheiros",
            ]
            
            if stats.total_size > 0:
                parts.append(f"[cyan]{format_size(stats.total_size)}[/cyan] total")
            
            if stats.hidden_items > 0:
                parts.append(f"[dim]{stats.hidden_items} ocultos[/dim]")
            
            if stats.truncated_dirs > 0:
                parts.append(f"[yellow]{stats.truncated_dirs} truncados[/yellow]")
            
            console.print(" | ".join(parts))
