"""Renderização de markdown no terminal com Rich - Versão Melhorada."""

import os
import sys
import re  # 💡 Added re import
import textwrap
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.theme import Theme
from rich.text import Text
from rich.rule import Rule
from rich.padding import Padding


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

# Detectar se o terminal suporta Unicode (CMD antigo pode não suportar)
def _supports_unicode() -> bool:
    """Verifica se o terminal suporta Unicode."""
    if sys.platform == "win32":
        # Windows: verificar se é Windows Terminal ou ConEmu
        return (
            os.environ.get("WT_SESSION") is not None  # Windows Terminal
            or os.environ.get("ConEmuANSI") == "ON"   # ConEmu
            or os.environ.get("TERM_PROGRAM") == "vscode"  # VS Code
        )
    return True


# Ícones com fallback para ASCII
class Icons:
    """Ícones com fallback para terminais sem Unicode."""
    
    def __init__(self, use_unicode: bool = True):
        self.unicode = use_unicode
    
    @property
    def success(self) -> str:
        return "✓" if self.unicode else "[OK]"
    
    @property
    def error(self) -> str:
        return "✗" if self.unicode else "[X]"
    
    @property
    def warning(self) -> str:
        return "⚠" if self.unicode else "[!]"
    
    @property
    def info(self) -> str:
        return "ℹ" if self.unicode else "[i]"
    
    @property
    def bullet(self) -> str:
        return "•" if self.unicode else "*"
    
    @property
    def arrow(self) -> str:
        return "→" if self.unicode else "->"
    
    @property
    def thinking(self) -> str:
        return "🤔" if self.unicode else "[?]"
    
    @property
    def code(self) -> str:
        return "📝" if self.unicode else "[<>]"
    
    @property
    def clipboard(self) -> str:
        return "\U0001F5AB" if self.unicode else "[SAVE]"  # U+1F5AB as requested


# Instância global de ícones
icons = Icons(_supports_unicode())



# =============================================================================
# CLIPBOARD
# =============================================================================


# =============================================================================
# CLIPBOARD
# =============================================================================

def copy_to_clipboard(text: str) -> bool:
    """
    Copia texto para o clipboard (cross-platform).
    
    Returns:
        True se copiou com sucesso, False caso contrário
    """
    import subprocess
    
    try:
        if sys.platform == "win32":
            # Windows: usar clip.exe
            process = subprocess.Popen(
                ["clip"],
                stdin=subprocess.PIPE,
                text=True,
                encoding="utf-16-le",  # Windows clipboard encoding
            )
            process.communicate(input=text)
            return process.returncode == 0
        
        elif sys.platform == "darwin":
            # macOS: usar pbcopy
            process = subprocess.Popen(
                ["pbcopy"],
                stdin=subprocess.PIPE,
                text=True,
            )
            process.communicate(input=text)
            return process.returncode == 0
        
        else:
            # Linux: tentar xclip ou xsel
            for cmd in [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]]:
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        text=True,
                    )
                    process.communicate(input=text)
                    if process.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
            return False
    
    except Exception:
        return False


# =============================================================================
# TEMA MELHORADO
# =============================================================================

custom_theme = Theme({
    # Cabeçalhos com hierarquia visual clara
    "markdown.h1": "bold bright_white on blue",
    "markdown.h2": "bold bright_yellow",
    "markdown.h3": "bold bright_cyan",
    "markdown.h4": "bold white",
    "markdown.h5": "dim white",
    
    # Código
    "markdown.code": "bold bright_white on grey7",
    "markdown.code_block": "white on grey7",
    
    # Links
    "markdown.link": "bright_cyan underline",
    "markdown.link_url": "dim cyan",
    
    # Listas e blockquotes
    "markdown.item.bullet": "bold yellow",
    "markdown.block_quote": "dim white",
    
    # Formatação de texto
    "markdown.bold": "bold bright_white",
    "markdown.italic": "italic",
    "markdown.bold_italic": "bold magenta",  # HACK: Usado para destacar user
    "markdown.strikethrough": "strike dim",
    
    # Horizontal rule
    "markdown.hr": "dim bright_black",
    
    # Mensagens do sistema
    "success": "bold green",
    "error": "bold red",
    "warning": "bold yellow",
    "info": "bold blue",
    "dim": "dim white",
    
    # Highlighting personalizado
    "path.path": "underline cyan",
    "path.user": "bold magenta",
})

# =============================================================================
# HIGHLIGHTER
# =============================================================================

from rich.highlighter import RegexHighlighter

class PathHighlighter(RegexHighlighter):
    """Realça caminhos e keywords."""
    base_style = "path."
    highlights = [
        # Regex para caminhos Windows e Unix
        r"(?P<path>(?<!\w)(?:[a-zA-Z]:\\[\w\-\.\\]+|(?:\.|~)?/[\w\-\./]+|(?:\.\/)?[\w\-]+\/[\w\-\./]+))",
        # Highlight específico para o user
        r"(?P<user>mediaweb\.global)",
    ]


# =============================================================================
# CONSOLE MELHORADO
# =============================================================================

# Console global com highlighter
console = Console(
    theme=custom_theme,
    highlight=False,  # Hightlight manual apenas onde necessário
)


# =============================================================================
# FUNÇÕES DE RENDERIZAÇÃO
# =============================================================================

def render_error(title: str, message: Optional[str] = None) -> None:
    """Renderiza mensagem de erro."""
    text = f"[bold red]{icons.error} {title}[/bold red]"
    if message:
        text += f"\n[white]{message}[/white]"
    console.print(Panel(text, border_style="red"))


def render_warning(message: str) -> None:
    """Renderiza aviso."""
    console.print(f"[bold yellow]{icons.warning} {message}[/bold yellow]")


def render_info(message: str) -> None:
    """Renderiza informação."""
    console.print(f"[bold blue]{icons.info} {message}[/bold blue]")


def render_success(message: str) -> None:
    """Renderiza sucesso."""
    console.print(f"[bold green]{icons.success} {message}[/bold green]")


def render_table(title: str, columns: list[str], rows: list[list[str]]) -> None:
    """Renderiza uma tabela."""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    
    for col in columns:
        table.add_column(col)
    
    for row in rows:
        table.add_row(*row)
        
    console.print(table)


def render_markdown(
    text: str,
    code_theme: str = "monokai",
    justify: str = "left",
    width: Optional[int] = None,
    subtitle: Optional[str] = None,
) -> None:
    """
    Renderiza texto markdown no terminal.
    
    Args:
        text: Texto em formato markdown
        code_theme: Tema para blocos de código
        justify: Alinhamento (left, center, right, full)
        width: Largura máxima (None = usar console width)
        subtitle: Subtítulo do painel (ex: status)
    """
    from rich.box import ROUNDED
    
    # Pré-processar texto (limpar code fences, dedent)
    clean_text = _preprocess_markdown(text)
    
    # Criar objeto Markdown
    # NOTA: Não injetamos estilos aqui para evitar artifacts
    md = Markdown(
        clean_text,
        code_theme=code_theme,
        inline_code_theme=code_theme,
        hyperlinks=True,
        justify=justify,
    )
    
    # Determinar largura
    max_width = 100
    terminal_width = console.width or 120
    panel_width = min(max_width, terminal_width - 4)
    
    # ESTRATÉGIA FINAL: Renderizar Markdown para Texto ANSI -> Aplicar Highlighter
    # Isto garante que temos estrutura Markdown mas com regex highlighting por cima
    # sem conflitos de sintaxe.
    
    # 1. Capturar output do Markdown
    with console.capture() as capture:
        console.print(md, width=panel_width)
    ansi_text = capture.get()
    
    # 2. Converter para Rich Text
    final_text = Text.from_ansi(ansi_text)
    
    # 3. Aplicar Highlighter (Caminhos e User)
    PathHighlighter().highlight(final_text)
    
    # 4. Renderizar Painel
    panel = Panel(
        final_text, # Usar o Text renderizado e realçado
        box=ROUNDED,
        border_style="blue",
        padding=(1, 2),
        width=panel_width,
        subtitle=subtitle,
        subtitle_align="right",
    )
    
    console.print(panel)


# Removido _highlight_text_content pois agora usamos PathHighlighter no texto final


def _preprocess_markdown(text: str) -> str:
    """Pré-processa markdown para melhor renderização."""
    text = text.strip()
    
    # 1. Procurar e extrair conteúdo de blocos de código se existirem
    # Procura pelo PRIMEIRO ``` e ÚLTIMO ```
    fence_pattern = r'```(?:\w+)?\s*\n(.*?)\n```'
    # Usar findall para ver se há múltiplas ocorrências ou apenas envolvente
    matches = list(re.finditer(fence_pattern, text, re.DOTALL))
    
    if matches:
        # Se o texto inteiro parece ser um bloco (o match cobre a maior parte)
        first_match = matches[0]
        # Se começa perto do início e acaba perto do fim
        if first_match.start() < 10 and len(text) - first_match.end() < 10:
             text = first_match.group(1)
    
    # 2. Remover inline code wrapping envolvente (`...`)
    if text.startswith("`") and text.endswith("`") and not text.startswith("```"):
         # Verificar se não é apenas um code span no meio
         if text.count("`") == 2:
             text = text[1:-1]
    
    # 3. Remover indentação comum (fixes "4 spaces indent = code block")
    text = textwrap.dedent(text)

    lines = text.split('\n')
    processed_lines = []
    
    in_code_block = False
    consecutive_empty = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detectar blocos de código (``` ou ~~~)
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            consecutive_empty = 0
            processed_lines.append(line)
            continue
        
        if in_code_block:
            # Dentro de bloco de código: preservar exatamente
            processed_lines.append(line)
            consecutive_empty = 0
        else:
            # Fora de bloco de código
            if not stripped:
                consecutive_empty += 1
                # Máximo de 2 linhas vazias consecutivas
                if consecutive_empty <= 2:
                    processed_lines.append(line)
            else:
                consecutive_empty = 0
                processed_lines.append(line)
    
    # Remover linhas vazias no início e fim
    while processed_lines and not processed_lines[0].strip():
        processed_lines.pop(0)
    while processed_lines and not processed_lines[-1].strip():
        processed_lines.pop()
    
    return '\n'.join(processed_lines)


# =============================================================================
# RENDERIZAÇÃO DE CÓDIGO
# =============================================================================

def render_code(
    code: str,
    language: str = "python",
    theme: str = "monokai",
    line_numbers: bool = False,
    title: Optional[str] = None,
    highlight_lines: Optional[set[int]] = None,
) -> None:
    """
    Renderiza código com syntax highlighting.
    
    Args:
        code: Código fonte
        language: Linguagem de programação
        theme: Tema de cores
        line_numbers: Mostrar números de linha
        title: Título opcional para o bloco
        highlight_lines: Linhas a destacar
    """
    # Limpar código
    code = code.strip()
    
    syntax = Syntax(
        code,
        language,
        theme=theme,
        line_numbers=line_numbers,
        word_wrap=True,
        padding=(0, 1),  # Pequeno padding horizontal
        highlight_lines=highlight_lines,
    )
    
    if title:
        panel = Panel(
            syntax,
            title=f"{icons.code} {title}",
            title_align="left",
            border_style="bright_black",
            padding=(0, 0),
        )
        console.print(panel)
    else:
        console.print(syntax)


# =============================================================================
# MENSAGENS DO SISTEMA
# =============================================================================

def render_error(message: str, details: Optional[str] = None) -> None:
    """Renderiza mensagem de erro."""
    console.print(f"[error]{icons.error}[/error] [bold]{message}[/bold]")
    if details:
        console.print(f"  [dim]{details}[/dim]")


def render_success(message: str) -> None:
    """Renderiza mensagem de sucesso."""
    console.print(f"[success]{icons.success}[/success] {message}")


def render_warning(message: str) -> None:
    """Renderiza aviso."""
    console.print(f"[warning]{icons.warning}[/warning] {message}")


def render_info(message: str) -> None:
    """Renderiza informação."""
    console.print(f"[info]{icons.info}[/info] {message}")


def render_debug(message: str) -> None:
    """Renderiza mensagem de debug (dim)."""
    console.print(f"[dim]DEBUG: {message}[/dim]")


# =============================================================================
# COMPONENTES VISUAIS
# =============================================================================

def render_panel(
    content: str,
    title: str = "",
    subtitle: str = "",
    border_style: str = "blue",
    padding: tuple[int, int] = (1, 2),
) -> None:
    """Renderiza conteúdo num painel."""
    panel = Panel(
        content,
        title=title if title else None,
        subtitle=subtitle if subtitle else None,
        border_style=border_style,
        padding=padding,
    )
    console.print(panel)


def render_rule(title: str = "", style: str = "bright_black") -> None:
    """Renderiza linha horizontal (regra)."""
    console.print(Rule(title=title, style=style))


def render_table(
    headers: list[str],
    rows: list[list[str]],
    title: str = "",
    show_lines: bool = False,
    row_styles: Optional[list[str]] = None,
) -> None:
    """
    Renderiza uma tabela.
    
    Args:
        headers: Cabeçalhos das colunas
        rows: Linhas de dados
        title: Título da tabela
        show_lines: Mostrar linhas entre rows
        row_styles: Estilos alternados para linhas
    """
    table = Table(
        title=title if title else None,
        show_header=True,
        header_style="bold magenta",
        show_lines=show_lines,
        row_styles=row_styles or ["", "dim"],  # Alternância de cores
        border_style="bright_black",
        padding=(0, 1),
    )
    
    for header in headers:
        table.add_column(header, overflow="fold")
    
    for row in rows:
        table.add_row(*row)
    
    console.print(table)


# =============================================================================
# STREAMING
# =============================================================================

class StreamingRenderer:
    """Renderizador para output em streaming."""
    
    def __init__(self):
        self.buffer = ""
        self._in_code_block = False
        self._code_buffer = ""
        self._code_lang = ""
    
    def write(self, text: str) -> None:
        """Escreve texto em modo streaming."""
        for char in text:
            self.buffer += char
            
            # Detectar início/fim de bloco de código
            if self.buffer.endswith("```"):
                if self._in_code_block:
                    # Fim do bloco
                    self._in_code_block = False
                    # Renderizar código acumulado
                    if self._code_buffer.strip():
                        render_code(self._code_buffer, self._code_lang or "text")
                    self._code_buffer = ""
                    self._code_lang = ""
                else:
                    # Início do bloco
                    self._in_code_block = True
                    # Imprimir buffer anterior
                    console.print(self.buffer[:-3], end="")
                self.buffer = ""
            elif self._in_code_block:
                if not self._code_lang and char == '\n':
                    # Primeira linha é a linguagem
                    self._code_lang = self.buffer.strip()
                    self.buffer = ""
                elif self._code_lang:
                    self._code_buffer += char
                    self.buffer = ""
            elif not self._in_code_block and len(self.buffer) > 100:
                # Flush periódico para texto normal
                console.print(self.buffer, end="")
                self.buffer = ""
    
    def flush(self) -> None:
        """Flush do buffer restante."""
        if self.buffer:
            console.print(self.buffer, end="")
            self.buffer = ""
        console.print()  # Nova linha final


def render_streaming(text: str, end: str = "") -> None:
    """Renderiza texto em modo streaming (sem newline)."""
    console.print(text, end=end, highlight=False)


def clear_line() -> None:
    """Limpa a linha atual."""
    console.print("\r" + " " * console.width + "\r", end="")


# =============================================================================
# UTILIDADES
# =============================================================================

def get_terminal_size() -> tuple[int, int]:
    """Retorna (largura, altura) do terminal."""
    try:
        size = os.get_terminal_size()
        return (size.columns, size.lines)
    except OSError:
        return (80, 24)


def supports_color() -> bool:
    """Verifica se o terminal suporta cores."""
    return console.is_terminal and not console.no_color


def set_quiet_mode(quiet: bool = True) -> None:
    """Ativa/desativa modo silencioso."""
    global console
    if quiet:
        console = create_console(no_color=True)


# =============================================================================
# EXEMPLO/TESTE
# =============================================================================

if __name__ == "__main__":
    # Teste das funcionalidades
    render_rule("Teste do Renderizador Markdown")
    
    render_success("Módulo carregado com sucesso!")
    render_warning("Isto é um aviso")
    render_error("Isto é um erro", "Com detalhes adicionais")
    render_info("Informação útil")
    
    print()
    render_rule("Markdown")
    
    test_md = """
# Título Principal

Este é um **texto em negrito** e *itálico*.

## Código

Código inline: `print("Hello")`

```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

## Lista
- Item 1
- Item 2
  - Sub-item

> Isto é um blockquote

[Link exemplo](https://github.com)
"""
    
    render_markdown(test_md)
    
    render_rule("Tabela")
    render_table(
        headers=["Nome", "Valor", "Status"],
        rows=[
            ["Config A", "123", "✓"],
            ["Config B", "456", "✗"],
            ["Config C", "789", "⚠"],
        ],
        title="Configurações",
    )
