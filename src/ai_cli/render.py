"""Renderização de markdown no terminal com Rich - Versão TUI Melhorada."""

import os
import sys
import shutil
import re
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
        return "🖫" if self.unicode else "[SAVE]"
    
    @property
    def lambda_icon(self) -> str:
        return "λ" if self.unicode else ">"
    
    @property
    def therefore(self) -> str:
        return "∴" if self.unicode else "=>"


# Instância global de ícones
icons = Icons(_supports_unicode())


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
# TEMA MELHORADO PARA TUI
# =============================================================================

custom_theme = Theme({
    # Cabeçalhos com hierarquia visual clara
    "markdown.h1": "bold bright_white",
    "markdown.h2": "bold bright_cyan",
    "markdown.h3": "bold cyan",
    "markdown.h4": "bold white",
    "markdown.h5": "white",
    "markdown.h6": "dim white",
    
    # Código
    "markdown.code": "bold cyan on grey11",
    "markdown.code_block": "white on grey7",
    
    # Links
    "markdown.link": "bright_blue underline",
    "markdown.link_url": "dim blue",
    
    # Listas e blockquotes
    "markdown.item.bullet": "bright_yellow",
    "markdown.item.number": "bright_yellow",
    "markdown.block_quote": "italic dim cyan",
    
    # Formatação de texto
    "markdown.bold": "bold white",
    "markdown.italic": "italic bright_white",
    "markdown.bold_italic": "bold italic bright_white",
    "markdown.strikethrough": "strike dim",
    
    # Horizontal rule
    "markdown.hr": "bright_black",
    
    # Mensagens do sistema
    "success": "bold green",
    "error": "bold red",
    "warning": "bold yellow",
    "info": "bold bright_blue",
    "dim": "dim",
    
    # Highlighting personalizado
    "path.path": "underline cyan",
    "path.user": "bold magenta",
    
    # Linhas decorativas
    "divider": "bright_blue",
    "divider.text": "bold bright_white",
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

# Forçar UTF-8 no Windows CMD para evitar erros de encoding
if sys.platform == "win32":
    # Configurar stdout/stderr para UTF-8
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        # Python < 3.7 ou streams que não suportam reconfigure
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Console global com highlighter
console = Console(
    theme=custom_theme,
    highlight=False,  # Highlight manual apenas onde necessário
    force_terminal=True,
)


# =============================================================================
# LINHAS DECORATIVAS
# =============================================================================

def _make_divider(text: str = "", style: str = "divider") -> Text:
    """
    Cria uma linha decorativa curta estilo: ─── Texto ───
    
    Args:
        text: Texto a exibir (opcional)
        style: Estilo da linha
    
    Returns:
        Text formatado
    """
    if icons.unicode:
        line_char = "─"
    else:
        line_char = "-"
    
    if text:
        # Com texto: ────── Text ──────
        # Minimalist: linhas do tamanho da linha vazia (12 chars)
        left_line = line_char * 12
        right_line = line_char * 12
        divider = Text()
        divider.append(left_line, style=style)
        divider.append(" ", style=style)
        divider.append(Text.from_markup(text, style="divider.text"))
        divider.append(" ", style=style)
        divider.append(right_line, style=style)
    else:
        # Sem texto: apenas linha curta (12 chars)
        divider = Text(line_char * 12, style=style)
    
    return divider


def render_divider(text: str = "", style: str = "divider") -> None:
    """Renderiza uma linha decorativa curta com indentação."""
    divider = _make_divider(text, style)
    # Adicionar padding (0 top/bottom, 2 left/right) para alinhar com o texto
    console.print(Padding(divider, (0, 2)))


# =============================================================================
# FUNÇÕES DE RENDERIZAÇÃO PRINCIPAIS
# =============================================================================

def render_header(duration: float) -> None:
    """Renderiza o cabeçalho com duração e linha decorativa."""
    # Calcular quantos chars cabem
    prefix = f"{icons.lambda_icon} ai-cli • {duration:.1f}s "
    max_line_width = 80
    line_length = max(0, max_line_width - len(prefix))
    
    grid = Table.grid(expand=False)
    grid.add_column()
    grid.add_column()
    grid.add_row(
        Text(prefix, style="bright_blue"),
        Text("─" * line_length if icons.unicode else "-" * line_length, style="bright_blue")
    )
    console.print(grid)


def render_footer(copied: bool = False) -> None:
    """Renderiza o rodapé com feedback de clipboard."""
    max_line_width = 80
    
    if copied:
        prefix = f"{icons.therefore} copiado para clipboard "
        line_length = max(0, max_line_width - len(prefix))
        
        grid = Table.grid(expand=False)
        grid.add_column()
        grid.add_column()
        grid.add_row(
            Text(prefix, style="bright_blue"),
            Text("─" * line_length if icons.unicode else "-" * line_length, style="bright_blue")
        )
    else:
        # Minimalist closing line
        grid = Table.grid(expand=False)
        grid.add_column()
        grid.add_row(
            Text("─" * max_line_width if icons.unicode else "-" * max_line_width, style="bright_blue")
        )
        
    console.print(grid)


def render_markdown(
    text: str,
    code_theme: str = "monokai",
    justify: str = "left",
    width: Optional[int] = None,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    duration: float = 0.0,
    copied: bool = False,
) -> None:
    """Renderiza texto markdown no terminal com linhas decorativas."""
    
    clean_text = _preprocess_markdown(text)
    
    md = Markdown(
        clean_text,
        code_theme=code_theme,
        inline_code_theme=code_theme,
        hyperlinks=True,
        justify=justify,
    )
    
    # Obter largura real do terminal
    terminal_width = console.size.width
    
    # Constantes
    DEFAULT_WIDTH = 120
    MARGIN = 4
    
    # Decidir largura do conteúdo
    if width:
        content_width = min(width, terminal_width - MARGIN)
    else:
        content_width = min(DEFAULT_WIDTH, terminal_width - MARGIN)
    
    # Linha superior
    render_header(duration)
    
    console.print()  # Espaço
    
    # Renderizar markdown com highlighting
    with console.capture() as capture:
        console.print(md, width=content_width)
    
    final_text = Text.from_ansi(capture.get())
    PathHighlighter().highlight(final_text)
    
    # Adicionar padding
    padded = Padding(final_text, (0, 2))
    console.print(padded)
    
    console.print()  # Espaço
    
    # Linha inferior
    render_footer(copied)
    
    console.print()  # Espaço extra


def render_code(
    code: str,
    language: str = "python",
    theme: str = "monokai",
    line_numbers: bool = False,
    title: Optional[str] = None,
    highlight_lines: Optional[set[int]] = None,
) -> None:
    """Renderiza código com syntax highlighting entre linhas decorativas."""
    
    # Limpar código
    code = code.strip()
    
    syntax = Syntax(
        code,
        language,
        theme=theme,
        line_numbers=line_numbers,
        word_wrap=True,
        padding=(0, 1),
        highlight_lines=highlight_lines,
    )
    
    # Linha superior
    if title:
        render_divider(f"{icons.code} {title}", style="bright_blue")
    else:
        render_divider(f"{icons.code} {language}", style="bright_blue")
    
    console.print()  # Espaço
    
    # Código com padding
    console.print(Padding(syntax, (0, 2)))
    
    console.print()  # Espaço
    
    # Linha inferior
    render_divider(style="bright_blue")
    console.print()


def _preprocess_markdown(text: str) -> str:
    """Pré-processa markdown para melhor renderização."""
    text = text.strip()
    
    # 1. Procurar e extrair conteúdo de blocos de código se existirem
    fence_pattern = r'```(?:\w+)?\s*\n(.*?)\n```'
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
    """Renderiza conteúdo num painel (mantido para compatibilidade)."""
    from rich.box import ROUNDED
    
    panel = Panel(
        content,
        title=title if title else None,
        subtitle=subtitle if subtitle else None,
        border_style=border_style,
        padding=padding,
        box=ROUNDED,
    )
    console.print(panel)


def render_rule(title: str = "", style: str = "bright_black", align: str = "center") -> None:
    """Renderiza linha horizontal full-width (regua tradicional)."""
    if title:
        console.print(Rule(title, style=style, align=align))
    else:
        console.print(Rule(style=style))


def render_table(
    headers: list[str],
    rows: list[list[str]],
    title: str = "",
    show_lines: bool = False,
    row_styles: Optional[list[str]] = None,
) -> None:
    """Renderiza uma tabela entre linhas decorativas."""
    
    # Linha superior com título
    if title:
        render_divider(f"📊 {title}", style="bright_blue")
    else:
        render_divider(style="bright_blue")
    
    console.print()  # Espaço
    
    table = Table(
        show_header=True,
        header_style="bold bright_cyan",
        show_lines=show_lines,
        row_styles=row_styles or ["", "dim"],
        border_style="bright_black",
        padding=(0, 1),
        box=None,  # Sem bordas externas
    )
    
    for header in headers:
        table.add_column(header, overflow="fold")
    
    for row in rows:
        table.add_row(*row)
    
    console.print(Padding(table, (0, 2)))
    
    console.print()  # Espaço
    
    # Linha inferior
    render_divider(style="bright_blue")
    console.print()


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
        console = Console(theme=custom_theme, no_color=True, highlight=False)


# =============================================================================
# EXEMPLO/TESTE
# =============================================================================

if __name__ == "__main__":
    # Mostra a largura atual
    term_w, term_h = get_terminal_size()
    
    render_rule("🎨 Teste do Renderizador TUI Melhorado", style="bold bright_blue")
    
    console.print(f"[dim]Terminal: {term_w}×{term_h} | Unicode: {icons.unicode}[/dim]\n")
    
    # Teste de mensagens do sistema
    render_success("Módulo carregado com sucesso!")
    render_warning("Isto é um aviso")
    render_error("Isto é um erro", "Com detalhes adicionais")
    render_info("Informação útil")
    render_debug("Mensagem de debug")
    
    console.print()
    
    # Teste de markdown
    test_md = """
# 📘 Título Principal

Este é um **texto em negrito** e *itálico*. Também temos ***negrito e itálico***.

## 💻 Código

Código inline: `print("Hello")` funciona bem.

```python
def hello(name: str) -> str:
    '''Função de exemplo'''
    return f"Hello, {name}!"

# Uso
print(hello("Mundo"))
```

## 📝 Lista e Citação

- Item 1 com **negrito**
- Item 2 com *itálico*
  - Sub-item A
  - Sub-item B
- Item 3

> Isto é um blockquote importante
> com múltiplas linhas

## 🔗 Links

Veja mais em [GitHub](https://github.com) ou [Rich](https://rich.readthedocs.io)

---

Caminho exemplo: `/home/user/projeto/arquivo.py` ou `C:\\Users\\mediaweb.global\\Documents`
"""
    
    render_markdown(test_md, title="Demonstração de Markdown", subtitle="v2.0")
    
    # Teste de código standalone
    test_code = """
class Example:
    def __init__(self, value: int):
        self.value = value
    
    def display(self):
        print(f"Value: {self.value}")

example = Example(42)
example.display()
"""
    
    render_code(test_code, language="python", title="Exemplo de Classe", line_numbers=True)
    
    # Teste de tabela
    render_table(
        headers=["Nome", "Tipo", "Status", "Valor"],
        rows=[
            ["Config A", "String", "✓ Ativo", "123"],
            ["Config B", "Integer", "✗ Inativo", "456"],
            ["Config C", "Boolean", "⚠ Aviso", "True"],
            ["Config D", "Float", "✓ Ativo", "3.14"],
        ],
        title="Tabela de Configurações",
        show_lines=False,
    )
    
    # Teste final adaptável
    test_adaptive = """
# 🚀 Teste Adaptável

Este texto se **adapta automaticamente** à largura do terminal.

## Características

- Layout responsivo
- Syntax highlighting
- Ícones contextuais
- Estilos consistentes

```bash
# Comandos de exemplo
git clone https://github.com/user/repo.git
cd repo
pip install -r requirements.txt
```

### Conclusão

O layout usa linhas horizontais ao invés de caixas, mantendo um visual **limpo e profissional**.
"""
    
    render_markdown(
        test_adaptive,
        title="Teste de Responsividade",
        subtitle=f"Terminal: {term_w}×{term_h}"
    )
    
    render_rule("✨ Fim dos Testes", style="bold green")
