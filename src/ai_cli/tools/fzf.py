"""Comando fzf - fuzzy finder interativo."""

import shutil
import subprocess

import click

from ..render import console, render_error, render_info, render_warning


def has_fzf() -> bool:
    """Verifica se fzf esta instalado."""
    return shutil.which("fzf") is not None


@click.command("fzf")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--preview", is_flag=True, help="Mostra preview dos ficheiros")
def fzf_cmd(path: str, preview: bool) -> None:
    """Abre fuzzy finder interativo.
    
    \b
    Exemplos:
      ai fzf
      ai fzf src --preview
      
    \b
    Nota: Requer fzf instalado.
          Instala em: https://github.com/junegunn/fzf#installation
    """
    if not has_fzf():
        render_error("fzf nao esta instalado.")
        render_info("Instala com: winget install junegunn.fzf")
        render_info("Ou visita: https://github.com/junegunn/fzf#installation")
        return
    
    # Construir comando fzf
    cmd = ["fzf", "--height=40%", "--layout=reverse", "--border"]
    
    if preview:
        # Preview com type no Windows
        cmd.extend(["--preview", "type {}"])
    
    try:
        # Listar ficheiros e passar para fzf
        if has_ripgrep():
            # Usar ripgrep para listar ficheiros (mais rápido, respeita .gitignore)
            list_cmd = ["rg", "--files", path]
        else:
            # Fallback para dir
            list_cmd = ["cmd", "/c", f"dir /s /b {path}"]
        
        list_process = subprocess.Popen(
            list_cmd,
            stdout=subprocess.PIPE,
            text=True,
        )
        
        fzf_process = subprocess.Popen(
            cmd,
            stdin=list_process.stdout,
            stdout=subprocess.PIPE,
            text=True,
        )
        
        selected, _ = fzf_process.communicate()
        
        if selected and selected.strip():
            console.print(f"\n[bold green]Selecionado:[/bold green] {selected.strip()}")
        
    except Exception as e:
        render_error(f"Erro ao executar fzf: {e}")
