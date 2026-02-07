"""Comando find - pesquisa com ripgrep ou grep."""

import shutil
import subprocess
import sys
import os

import click

from ..render import console, render_error, render_info, render_warning


def has_ripgrep() -> bool:
    """Verifica se ripgrep esta instalado."""
    return shutil.which("rg") is not None


def run_ripgrep(pattern: str, path: str, context: int, ignore_case: bool) -> None:
    """Executa ripgrep com o padrao dado."""
    cmd = ["rg", "--color=always", "--heading", "--line-number"]
    
    if context > 0:
        cmd.extend(["-C", str(context)])
    
    if ignore_case:
        cmd.append("-i")
    
    cmd.extend([pattern, path])
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode == 1:
            render_info(f"Nenhum resultado para '{pattern}'")
    except Exception as e:
        render_error(f"Erro ao executar ripgrep: {e}")


def run_grep(pattern: str, path: str, context: int, ignore_case: bool) -> None:
    """Fallback para grep em Unix."""
    cmd = ["grep", "-r", "-n", "--color=always"]
    
    if context > 0:
        cmd.extend(["-C", str(context)])
    
    if ignore_case:
        cmd.append("-i")
    
    cmd.extend([pattern, path])
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode == 1:
            render_info(f"Nenhum resultado para '{pattern}'")
    except Exception as e:
        render_error(f"Erro ao executar grep: {e}")


def run_findstr(pattern: str, path: str, ignore_case: bool) -> None:
    """Fallback para findstr no Windows."""
    cmd = ["findstr", "/S", "/N"]
    
    if ignore_case:
        cmd.append("/I")
    
    target = f"{path}\\*" if os.path.isdir(path) and not path.endswith("*") else path
    cmd.extend([pattern, target])
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode == 1:
            render_info(f"Nenhum resultado para '{pattern}'")
    except Exception as e:
        render_error(f"Erro ao executar findstr: {e}")


@click.command("find")
@click.argument("pattern")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("-c", "--context", default=0, help="Linhas de contexto (default: 0)")
@click.option("-i", "--ignore-case", is_flag=True, help="Ignora maiusculas/minusculas")
def find_cmd(pattern: str, path: str, context: int, ignore_case: bool) -> None:
    """Pesquisa padroes em ficheiros.
    
    \b
    Prioridade:
    1. ripgrep (rg) - Recomendado
    2. grep (Linux/Mac)
    3. findstr (Windows)
    """
    if has_ripgrep():
        run_ripgrep(pattern, path, context, ignore_case)
    elif sys.platform == "win32":
        render_warning("ripgrep nao encontrado. A usar findstr.")
        run_findstr(pattern, path, ignore_case)
    else:
        render_warning("ripgrep nao encontrado. A usar grep.")
        run_grep(pattern, path, context, ignore_case)

