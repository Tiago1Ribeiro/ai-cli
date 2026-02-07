"""Comando fzf - fuzzy finder interativo."""

import shutil
import subprocess
import sys
import os

import click

from ..render import console, render_error, render_info, render_warning


def has_fzf() -> bool:
    """Verifica se fzf esta instalado."""
    return shutil.which("fzf") is not None


def has_ripgrep() -> bool:
    """Verifica se ripgrep esta instalado."""
    return shutil.which("rg") is not None


@click.command("fzf")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--preview", is_flag=True, help="Mostra preview dos ficheiros")
def fzf_cmd(path: str, preview: bool) -> None:
    """Abre fuzzy finder interativo.
    
    \b
    Exemplos:
      ai fzf
      ai fzf src --preview
    """
    if not has_fzf():
        render_error("fzf nao esta instalado.")
        return
    
    # Construir comando fzf
    cmd = ["fzf", "--height=80%", "--layout=reverse", "--border"]
    
    if preview:
        preview_cmd = "type {}" if sys.platform == "win32" else "cat {}"
        if shutil.which("bat"):
            preview_cmd = "bat --style=numbers --color=always {}"
        cmd.extend(["--preview", preview_cmd])
    
    try:
        # Listar ficheiros
        if has_ripgrep():
            list_cmd = ["rg", "--files", path]
        elif sys.platform == "win32":
            list_cmd = ["cmd", "/c", f"dir /s /b {path}"]
        else:
            list_cmd = ["find", path, "-type", "f"]
        
        list_process = subprocess.Popen(
            list_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        fzf_process = subprocess.Popen(
            cmd,
            stdin=list_process.stdout,
            stdout=subprocess.PIPE,
            text=True,
        )
        
        # Fechar stdout do list_process para permitir SIGPIPE
        if list_process.stdout:
            list_process.stdout.close()
        
        selected, _ = fzf_process.communicate()
        list_process.wait()
        
        if selected and selected.strip():
            console.print(f"\n[bold green]Selecionado:[/bold green] {selected.strip()}")
        
    except Exception as e:
        render_error(f"Erro ao executar fzf: {e}")
