"""Renderização de markdown no terminal com Rich - Versão Otimizada e Segura."""

import os
import sys
import re
import textwrap
import subprocess
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.theme import Theme
from rich.text import Text
from rich.padding import Padding
from rich.box import ROUNDED
from rich.highlighter import RegexHighlighter


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

def _supports_unicode() -> bool:
    """Verifica se o terminal suporta Unicode de forma robusta."""
    if sys.platform == "win32":
        return (
            os.environ.get("WT_SESSION") is not None  # Windows Terminal
            or os.environ.get("ConEmuANSI") == "ON"   # ConEmu
            or os.environ.get("TERM_PROGRAM") in ("vscode", "mintty")  # VS Code, Git Bash
            or os.environ.get("MSYSTEM") is not None  # Git Bash (MSYS)
        )
    
    # Unix: verificar locale simples
    import locale
    try:
        lang, encoding = locale.getdefaultlocale()
        return encoding and "utf" in encoding.lower()
    except:
        return True


class Icons:
    """Ícones com fallback para terminais sem Unicode."""
    
    def __init__(self, use_unicode: bool = True):
        self.unicode = use_unicode
    
    @property
    def success(self) -> str: return "✓" if self.unicode else "[OK]"
    @property
    def error(self) -> str: return "✗" if self.unicode else "[X]"
    @property
    def warning(self) -> str: return "⚠" if self.unicode else "[!]"
    @property
    def info(self) -> str: return "ℹ" if self.unicode else "[i]"
    @property
    def bullet(self) -> str: return "•" if self.unicode else "*"
    @property
    def arrow(self) -> str: return "→" if self.unicode else "->"
    @property
    def thinking(self) -> str: return "🤔" if self.unicode else "[?]"
    @property
    def code(self) -> str: return "📝" if self.unicode else "[CODE]"
    
    @property
    def clipboard(self) -> str:
        # "📋" é mais seguro que "🖫"
        return "📋" if self.unicode else "[COPY]"
    
    @property
    def lambda_icon(self) -> str: return "λ" if self.unicode else ">"
    @property
    def therefore(self) -> str: return "∴" if self.unicode else "=>"


icons = Icons(_supports_unicode())


# =============================================================================
# CLIPBOARD
# =============================================================================

def copy_to_clipboard(text: str) -> bool:
    """Copia texto para o clipboard (cross-platform robusto)."""
    try:
        if sys.platform == "win32":
            # Tentar Powershell primeiro (mais fiável para encoding)
            try:
                subprocess.run(
                    ["powershell", "-Command", "Set-Clipboard", "-Value", "$input"],
                    input=text,
                    text=True,
                    encoding="utf-8",
                    check=True,
                    capture_output=True
                )
                return True
            except (FileNotFoundError, subprocess.SubprocessError):
                pass 

            # Fallback clip.exe (UTF-16LE encoding required)
            try:
                process = subprocess.Popen(["clip"], stdin=subprocess.PIPE, shell=True)
                process.communicate(input=text.encode("utf-16-le"))
                return process.returncode == 0
            except:
                return False
        
        elif sys.platform == "darwin":
            process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
            process.communicate(input=text)
            return process.returncode == 0
        
        else:
            # Linux: xclip ou xsel
            for cmd in [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]]:
                try:
                    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True)
                    process.communicate(input=text)
                    if process.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
            return False
            
    except Exception:
        return False


# =============================================================================
# TEMA
# =============================================================================

custom_theme = Theme({
    "markdown.h1": "bold bright_white",
    "markdown.h2": "bold bright_cyan",
    "markdown.h3": "bold cyan",
    "markdown.h4": "bold white",
    "markdown.code": "bold cyan on grey11",
    "markdown.code_block": "white on grey7",
    "markdown.link": "bright_blue underline",
    "markdown.link_url": "dim blue",
    "success": "bold green",
    "error": "bold red",
    "warning": "bold yellow",
    "info": "bold bright_blue",
    "dim": "dim",
    "path.path": "underline cyan",
    "divider": "bright_blue",
    "divider.text": "bold bright_white",
})

class PathHighlighter(RegexHighlighter):
    """Realça caminhos."""
    base_style = "path."
    highlights = [
        # Caminhos genéricos (Windows/Unix)
        r"(?P<path>(?<!\w)(?:[a-zA-Z]:\\[\w\-\.\\]+|(?:\.|~)?/[\w\-\./]+|(?:\.\/)?[\w\-]+\/[\w\-\./]+))",
    ]


# =============================================================================
# CONSOLE GLOBAL
# =============================================================================

console = Console(
    theme=custom_theme,
    highlight=False,
    soft_wrap=False,
    # force_terminal removed to allow piping
)

def set_quiet_mode(quiet: bool = True) -> None:
    """Ativa modo silencioso alterando propriedade do console global."""
    console.quiet = quiet


# =============================================================================
# HELPER DE LAYOUT
# =============================================================================

def _get_content_width() -> int:
    """Calcula largura contentável segura."""
    terminal_width = console.size.width
    DEFAULT_WIDTH = 120
    MARGIN = 4
    return min(DEFAULT_WIDTH, terminal_width - MARGIN)

def _make_divider(text: str = "", style: str = "divider") -> Text:
    """Cria divisor adaptavel."""
    width = _get_content_width()
    line_char = "─" if icons.unicode else "-"
    
    if text:
        text_obj = Text.from_markup(text, style="divider.text")
        text_len = len(text_obj)
        # Linha esquerda/direita balanceada
        remaining = max(2, width - text_len - 2) # 2 spaces padding
        side_len = remaining // 2
        
        divider = Text(line_char * side_len, style=style)
        divider.append(" ")
        divider.append(text_obj)
        divider.append(" ")
        divider.append(line_char * side_len, style=style)
        return divider
    else:
        return Text(line_char * width, style=style)


def render_header(duration: float, title: Optional[str] = None) -> None:
    """Cabeçalho consistente."""
    width = _get_content_width()
    prefix = f"{icons.lambda_icon} {title or 'ai-cli'} • {duration:.1f}s "
    line_char = "─" if icons.unicode else "-"
    
    line_len = max(0, width - len(prefix))
    
    grid = Table.grid(expand=False)
    grid.add_column()
    grid.add_column()
    grid.add_row(
        Text(prefix, style="bright_blue"),
        Text(line_char * line_len, style="bright_blue")
    )
    console.print(grid)

def render_footer(copied: bool = False) -> None:
    """Rodapé consistente."""
    width = _get_content_width()
    line_char = "─" if icons.unicode else "-"
    
    if copied:
        prefix = f"{icons.therefore} copiado para clipboard "
        line_len = max(0, width - len(prefix))
        
        grid = Table.grid(expand=False)
        grid.add_column()
        grid.add_column()
        grid.add_row(
            Text(prefix, style="bright_blue"),
            Text(line_char * line_len, style="bright_blue")
        )
        console.print(grid)
    else:
        console.print(Text(line_char * width, style="bright_blue"))


# =============================================================================
# MARKDOWN & STREAMING
# =============================================================================

def _preprocess_markdown(text: str) -> str:
    """Limpeza básica sem remover fences válidas."""
    text = text.strip()
    text = textwrap.dedent(text)
    # Remover >2 newlines consecutivas
    return re.sub(r'\n{3,}', '\n\n', text)


def render_markdown(
    text: str,
    title: Optional[str] = None,
    subtitle: Optional[str] = None, # Mantido API mas opcional
    duration: float = 0.0,
    copied: bool = False,
    width: Optional[int] = None, # Mantido API
    code_theme: str = "monokai", # Mantido API
    justify: str = "left", # Mantido API
) -> None:
    """Renderiza Markdown completo."""
    clean_text = _preprocess_markdown(text)
    
    render_header(duration, title)
    console.print() 
    
    # Criar markdown
    md = Markdown(
        clean_text,
        code_theme="monokai",
        hyperlinks=True,
    )
    
    # Renderizar com padding
    c_width = _get_content_width()
    console.print(Padding(md, (0, 2)), width=c_width)
    
    console.print()
    render_footer(copied)
    console.print()


class StreamingRenderer:
    """Streaming robusto que lida com code blocks parciais."""
    def __init__(self):
        self.buffer = ""
        self.in_code_block = False
        self.code_lang = ""
        self.code_buffer = ""
    
    def write(self, text: str) -> None:
        # Acumular no buffer principal
        self.buffer += text
        
        # Processar apenas se tivermos uma quebra de linha ou o buffer estiver grande
        while '\n' in self.buffer:
            line, rest = self.buffer.split('\n', 1)
            self._process_line(line + '\n')
            self.buffer = rest
            
    def _process_line(self, line: str) -> None:
        stripped = line.strip()
        
        # Simples detecção de inicio/fim de bloco
        if stripped.startswith('```'):
            if self.in_code_block:
                # Fechando bloco
                self.in_code_block = False
                if self.code_buffer:
                    render_code(self.code_buffer, self.code_lang)
                    self.code_buffer = ""
                    self.code_lang = ""
            else:
                # Abrindo bloco
                self.in_code_block = True
                self.code_lang = stripped.lstrip('`').strip()
            return

        if self.in_code_block:
            self.code_buffer += line
        else:
            # Texto normal
            console.print(line, end="")
    
    def flush(self) -> None:
        """Força output do que sobrou."""
        if self.buffer:
            if self.in_code_block:
                self.code_buffer += self.buffer
                # Tentar renderizar o que temos como código
                render_code(self.code_buffer, self.code_lang)
            else:
                console.print(self.buffer, end="")
        console.print() 


def render_code(code: str, language: str = "text", title: Optional[str] = None, **kwargs) -> None:
    """Renderiza bloco de código isolado."""
    syntax = Syntax(
        code.strip(),
        language or "text",
        theme="monokai",
        line_numbers=False,
        word_wrap=True,
        padding=(0, 0),
    )
    console.print(Padding(syntax, (0, 2)))


# =============================================================================
# MENSAGENS E UTILS
# =============================================================================

def render_error(message: str, details: Optional[str] = None) -> None:
    console.print(f"[error]{icons.error}[/error] [bold]{message}[/bold]")
    if details:
        console.print(f"  [dim]{details}[/dim]")

def render_success(message: str) -> None:
    console.print(f"[success]{icons.success}[/success] {message}")

def render_warning(message: str) -> None:
    console.print(f"[warning]{icons.warning}[/warning] {message}")

def render_info(message: str) -> None:
    console.print(f"[info]{icons.info}[/info] {message}")

def render_panel(content: str, title: str = "", border_style: str = "blue") -> None:
    console.print(Panel(content, title=title, border_style=border_style, box=ROUNDED))

def render_divider(text: str = "", style: str = "divider") -> None:
    div = _make_divider(text, style)
    console.print(Padding(div, (0, 2)))

def render_table(
    headers: list[str],
    rows: list[list[str]],
    title: str = "",
    show_lines: bool = False,
    row_styles: Optional[list[str]] = None,
) -> None:
    """Renderiza uma tabela."""
    if title:
        render_divider(f"📊 {title}", style="bright_blue")
        console.print()
    
    table = Table(
        show_header=True,
        header_style="bold bright_cyan",
        show_lines=show_lines,
        row_styles=row_styles or ["", "dim"],
        border_style="bright_black",
        padding=(0, 1),
        box=None,
    )
    
    for header in headers:
        table.add_column(header, overflow="fold")
    
    for row in rows:
        table.add_row(*row)
    
    console.print(Padding(table, (0, 2)))
    console.print()
    
    if title:
        render_divider(style="bright_blue")
        console.print()

if __name__ == "__main__":
    # Teste rápido
    render_success("Módulo render atualizado!")
