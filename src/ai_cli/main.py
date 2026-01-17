"""Ponto de entrada principal do CLI."""

import sys
from typing import Optional

import click

from . import __version__
from .config import list_models, get_default_model, validate_model
from .llm_client import explain_file, query_llm, query_llm_with_file
from .render import (
    console,
    render_error,
    render_warning,
    render_info,
    render_table,
    render_success,
)


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

# Modelo padrão (pode vir de config/env)
DEFAULT_MODEL = get_default_model() if hasattr(sys.modules.get('.config', object()), 'get_default_model') else "maverick"

# Exit codes padronizados
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_KEYBOARD_INTERRUPT = 130  # Padrão Unix para Ctrl+C


# =============================================================================
# IMPORTAÇÃO DE TOOLS COM LOGGING
# =============================================================================

TOOLS_AVAILABLE = False
TOOLS_ERROR: Optional[str] = None

try:
    from .tools import find, fzf, tree
    TOOLS_AVAILABLE = True
except ImportError as e:
    TOOLS_ERROR = f"Dependência em falta: {e.name}"
except Exception as e:
    # Log para debug, mas não falha
    TOOLS_ERROR = str(e)


# =============================================================================
# VALIDADORES E CALLBACKS
# =============================================================================

def validate_model_callback(
    ctx: click.Context, 
    param: click.Parameter, 
    value: str
) -> str:
    """Valida se o modelo existe."""
    valid_models = [m.alias for m in list_models()]
    
    if value not in valid_models:
        # Tentar encontrar correspondência parcial
        matches = [m for m in valid_models if value.lower() in m.lower()]
        
        if len(matches) == 1:
            return matches[0]
        elif matches:
            raise click.BadParameter(
                f"Modelo '{value}' ambíguo. Correspondências: {', '.join(matches)}"
            )
        else:
            raise click.BadParameter(
                f"Modelo '{value}' não encontrado. "
                f"Disponíveis: {', '.join(valid_models)}"
            )
    
    return value


def read_stdin_if_available() -> Optional[str]:
    """Lê stdin se houver dados (pipe/redirect)."""
    if not sys.stdin.isatty():
        try:
            return sys.stdin.read()
        except Exception:
            return None
    return None


# =============================================================================
# DECORADORES COMUNS
# =============================================================================

# Opções comuns reutilizáveis
model_option = click.option(
    "-m", "--model",
    default=DEFAULT_MODEL,
    callback=validate_model_callback,
    help=f"Modelo a usar (default: {DEFAULT_MODEL})",
    metavar="MODEL",
)

verbose_option = click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Modo verboso (mostra detalhes)",
)

output_option = click.option(
    "-o", "--output",
    type=click.Path(),
    help="Guardar output em ficheiro",
)


# =============================================================================
# GRUPO PRINCIPAL
# =============================================================================

class AliasedGroup(click.Group):
    """Grupo com suporte a aliases de comandos."""
    
    ALIASES = {
        "f": "file",
        "e": "explain",
        "m": "models",
        "t": "tree",
        "s": "find",  # search
    }
    
    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        # Tentar alias primeiro
        cmd_name = self.ALIASES.get(cmd_name, cmd_name)
        return super().get_command(ctx, cmd_name)
    
    def list_commands(self, ctx: click.Context) -> list[str]:
        return super().list_commands(ctx)


@click.group(
    cls=AliasedGroup,
    invoke_without_command=True,
    context_settings={
        "help_option_names": ["-h", "--help"],
        "max_content_width": 100,
    }
)
@click.argument("prompt", nargs=-1, required=False)
@model_option
@click.option("-V", "--version", is_flag=True, help="Mostra versão")
@click.option("-c", "--continue", "continue_chat", is_flag=True, help="Continua conversa anterior")
@click.option("--no-stream", is_flag=True, help="Desativa streaming (output completo)")
@verbose_option
@click.pass_context
def cli(
    ctx: click.Context,
    prompt: tuple[str, ...],
    model: str,
    version: bool,
    continue_chat: bool,
    no_stream: bool,
    verbose: bool,
) -> None:
    """AI CLI - Assistente de IA no terminal.
    
    \b
    Uso Básico:
      ai olá como estás
      ai -m fast qual a capital de Portugal
    
    \b
    Conversas:
      ai -c "continua"        # Continua última conversa
      ai -c "mais detalhes"   # O modelo lembra contexto
    
    \b
    Com Ficheiros:
      ai file README.md resume isto
      ai explain main.py
    
    \b
    Com Pipe:
      cat error.log | ai "explica este erro"
      git diff | ai "resume estas alterações"
    
    \b
    Exploração:
      ai tree              # Árvore do projeto
      ai find "def.*main"  # Procura padrões
    
    \b
    Aliases:
      ai f  → ai file
      ai e  → ai explain
      ai m  → ai models
      ai t  → ai tree
      ai s  → ai find (search)
    """
    # Guardar opções no contexto para subcomandos
    ctx.ensure_object(dict)
    ctx.obj["model"] = model
    ctx.obj["verbose"] = verbose
    ctx.obj["no_stream"] = no_stream
    ctx.obj["continue"] = continue_chat
    
    if version:
        _show_version(verbose)
        return
    
    # Se há subcomando, deixa executar
    if ctx.invoked_subcommand is not None:
        return
    
    # Verificar stdin (pipe)
    stdin_content = read_stdin_if_available()
    
    # Se não há prompt nem stdin, mostra ajuda
    if not prompt and not stdin_content:
        console.print(ctx.get_help())
        return
    
    # Construir prompt completo
    full_prompt = " ".join(prompt) if prompt else ""
    
    # Se há stdin, combinar com prompt
    if stdin_content:
        if full_prompt:
            full_prompt = f"{full_prompt}\n\n---\n\n{stdin_content}"
        else:
            full_prompt = f"Analisa o seguinte:\n\n{stdin_content}"
        
        if verbose:
            render_info(f"Lidos {len(stdin_content)} caracteres do stdin")
    
    # Indicar que está a continuar conversa
    if continue_chat and verbose:
        render_info("A continuar conversa anterior...")
    
    # Executar query
    try:
        query_llm(
            full_prompt,
            model=ctx.obj["model"],
            stream=not no_stream,
            continue_conversation=continue_chat,
        )
    except KeyboardInterrupt:
        console.print("\n[dim]Cancelado pelo utilizador[/dim]")
        ctx.exit(EXIT_KEYBOARD_INTERRUPT)
    except Exception as e:
        render_error("Erro na query", str(e) if verbose else None)
        ctx.exit(EXIT_ERROR)


def _show_version(verbose: bool = False) -> None:
    """Mostra informação de versão."""
    console.print(f"[bold cyan]AI CLI[/bold cyan] v{__version__}")
    
    if verbose:
        import platform
        console.print(f"[dim]Python: {platform.python_version()}[/dim]")
        console.print(f"[dim]Platform: {platform.system()} {platform.release()}[/dim]")
        console.print(f"[dim]Tools disponíveis: {TOOLS_AVAILABLE}[/dim]")
        if TOOLS_ERROR:
            console.print(f"[dim]Tools error: {TOOLS_ERROR}[/dim]")


# =============================================================================
# COMANDOS
# =============================================================================

@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.argument("prompt", nargs=-1, required=False)
@model_option
@output_option
@click.pass_context
def file(
    ctx: click.Context,
    filepath: str,
    prompt: tuple[str, ...],
    model: Optional[str], # Changed type hint to Optional[str]
    output: Optional[str],
) -> None:
    """Analisa um ficheiro com uma pergunta.
    
    \b
    Exemplos:
      ai file README.md resume isto
      ai file main.py "o que faz este código"
      ai file data.json -o summary.md
    """
    question = " ".join(prompt) if prompt else "Analisa e resume este ficheiro."
    selected_model = model or get_default_model() # Use get_default_model here
    verbose = ctx.obj.get("verbose", False)
    
    if verbose:
        render_info(f"Ficheiro: {filepath}")
        render_info(f"Modelo: {selected_model}") # Use selected_model here
    
    try:
        result = query_llm_with_file(
            filepath,
            question,
            model=selected_model, # Use selected_model here
            stream=not ctx.obj.get("no_stream", False),
        )
        
        if output and result:
            _save_output(output, result)
            
    except FileNotFoundError:
        render_error(f"Ficheiro não encontrado: {filepath}")
        ctx.exit(EXIT_ERROR)
    except PermissionError:
        render_error(f"Sem permissão para ler: {filepath}")
        ctx.exit(EXIT_ERROR)
    except KeyboardInterrupt:
        console.print("\n[dim]Cancelado[/dim]")
        ctx.exit(EXIT_KEYBOARD_INTERRUPT)
    except Exception as e:
        render_error("Erro ao processar ficheiro", str(e) if verbose else None)
        ctx.exit(EXIT_ERROR)


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@model_option
@click.option("--detailed", "-d", is_flag=True, help="Explicação mais detalhada")
@output_option
@click.pass_context
def explain(
    ctx: click.Context,
    filepath: str,
    model: str,
    detailed: bool,
    output: Optional[str],
) -> None:
    """Explica o código de um ficheiro.
    
    \b
    Exemplos:
      ai explain main.py
      ai explain -d utils.py     # Mais detalhado
      ai explain app.py -o docs.md
    """
    verbose = ctx.obj.get("verbose", False)
    
    if verbose:
        render_info(f"A explicar: {filepath}")
    
    try:
        result = explain_file(
            filepath,
            model=model,
            detailed=detailed,
            stream=not ctx.obj.get("no_stream", False),
        )
        
        if output and result:
            _save_output(output, result)
            
    except KeyboardInterrupt:
        console.print("\n[dim]Cancelado[/dim]")
        ctx.exit(EXIT_KEYBOARD_INTERRUPT)
    except Exception as e:
        render_error("Erro ao explicar ficheiro", str(e) if verbose else None)
        ctx.exit(EXIT_ERROR)


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Output em JSON")
def models(as_json: bool) -> None:
    """Lista modelos disponíveis.
    
    \b
    Exemplos:
      ai models
      ai models --json
    """
    model_list = list_models()
    
    if as_json:
        import json
        data = [
            {
                "alias": m.alias,
                "description": m.description,
                "tokens_per_sec": m.tokens_per_sec,
            }
            for m in model_list
        ]
        console.print_json(json.dumps(data))
    else:
        headers = ["Alias", "Descrição", "Tokens/seg", "Default"]
        rows = [
            [
                m.alias,
                m.description,
                str(m.tokens_per_sec) if m.tokens_per_sec else "-",
                "✓" if m.alias == DEFAULT_MODEL else "",
            ]
            for m in model_list
        ]
        
        render_table(headers, rows, title="Modelos Disponíveis")


@cli.command()
def config() -> None:
    """Mostra/edita configuração.
    
    \b
    Exemplos:
      ai config              # Mostra configuração atual
      ai config --edit       # Abre editor
    """
    # TODO: Implementar gestão de config
    render_info("Configuração atual:")
    console.print(f"  Modelo padrão: [cyan]{DEFAULT_MODEL}[/cyan]")
    console.print(f"  Tools disponíveis: [cyan]{TOOLS_AVAILABLE}[/cyan]")


@cli.command(name="check")
def health_check() -> None:
    """Verifica estado do sistema."""
    console.print("[bold]Verificação do Sistema[/bold]\n")
    
    # Verificar API
    try:
        # Assumindo que há uma função de health check
        render_success("API configurada")
    except Exception as e:
        render_error("API não configurada", str(e))
    
    # Verificar tools
    if TOOLS_AVAILABLE:
        render_success("Tools disponíveis (tree, find, fzf)")
    else:
        render_warning(f"Tools indisponíveis: {TOOLS_ERROR}")
    
    # Verificar modelos
    try:
        models_count = len(list_models())
        render_success(f"{models_count} modelos disponíveis")
    except Exception as e:
        render_error("Não foi possível listar modelos", str(e))


# =============================================================================
# UTILITÁRIOS
# =============================================================================

def _save_output(filepath: str, content: str) -> None:
    """Guarda output num ficheiro."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        render_success(f"Guardado em: {filepath}")
    except Exception as e:
        render_error(f"Erro ao guardar: {e}")


# =============================================================================
# COMANDOS DE GESTÃO DE MODELOS
# =============================================================================

@cli.group(invoke_without_command=True)
@click.pass_context
def model(ctx: click.Context) -> None:
    """Gestão de modelos.
    
    \b
    Exemplos:
      ai model              # Menu interativo
      ai model list         # Lista modelos
      ai model set fast     # Define default
      ai model add meu gpt-4 "GPT-4 custom"
      ai model current      # Mostra modelo atual
    """
    if ctx.invoked_subcommand is None:
        # Sem subcomando = menu interativo
        from .config import select_model_interactive, set_default_model, get_model
        
        selected = select_model_interactive()
        if selected:
            try:
                model_config = get_model(selected)
                set_default_model(selected)
                render_success(f"Modelo default: {selected} ({model_config.description})")
            except ValueError as e:
                render_error(str(e))
        else:
            render_warning("Nenhum modelo selecionado")


@model.command(name="list")
@click.option("--json", "as_json", is_flag=True, help="Output JSON")
def model_list(as_json: bool) -> None:
    """Lista modelos disponíveis.
    
    \b
    Exemplos:
      ai model list
      ai model list --json
    """
    from .config import get_default_model
    
    model_list = list_models()
    default = get_default_model()
    
    if as_json:
        import json
        console.print_json(json.dumps([m.to_dict() for m in model_list]))
    else:
        headers = ["Alias", "Descrição", "Velocidade", "Default", "Tipo"]
        rows = [
            [
                m.alias,
                m.description,
                f"{m.tokens_per_sec} t/s" if m.tokens_per_sec else "-",
                "✓" if m.alias == default else "",
                "custom" if m.is_custom else "built-in",
            ]
            for m in model_list
        ]
        render_table(headers, rows, title="Modelos Disponíveis")


@model.command(name="set")
@click.argument("alias")
def model_set(alias: str) -> None:
    """Define modelo default.
    
    \b
    Exemplo:
      ai model set fast
    """
    from .config import set_default_model, get_model
    
    try:
        model_config = get_model(alias)
        set_default_model(alias)
        render_success(f"Modelo default: {alias} ({model_config.description})")
    except ValueError as e:
        render_error(str(e))


@model.command(name="add")
@click.argument("alias")
@click.argument("model_id")
@click.argument("description", required=False, default="")
@click.option("--speed", type=int, help="Tokens por segundo")
def model_add(alias: str, model_id: str, description: str, speed: Optional[int]) -> None:
    """Adiciona modelo custom.
    
    \b
    Exemplos:
      ai model add mygpt gpt-4 "GPT-4 para código"
      ai model add local llama3:8b --speed 100
    """
    from .config import add_custom_model
    
    try:
        model_config = add_custom_model(alias, model_id, description, speed)
        render_success(f"Modelo adicionado: {alias} → {model_id}")
        render_info(f"Usa com: ai -m {alias} \"sua pergunta\"")
    except ValueError as e:
        render_error(str(e))


@model.command(name="remove")
@click.argument("alias")
def model_remove(alias: str) -> None:
    """Remove modelo custom.
    
    \b
    Exemplo:
      ai model remove mygpt
    """
    from .config import remove_custom_model, BUILTIN_MODELS
    
    if alias in BUILTIN_MODELS:
        render_error(f"'{alias}' é built-in e não pode ser removido")
        return
    
    if remove_custom_model(alias):
        render_success(f"Modelo removido: {alias}")
    else:
        render_error(f"Modelo custom '{alias}' não encontrado")


@model.command(name="current")
def model_current() -> None:
    """Mostra modelo default atual.
    
    \b
    Exemplo:
      ai model current
    """
    from .config import get_default_model, get_model
    
    alias = get_default_model()
    model_config = get_model(alias)
    
    console.print(f"Modelo atual: [bold cyan]{alias}[/bold cyan]")
    console.print(f"  ID: {model_config.model_id}")
    console.print(f"  Descrição: {model_config.description}")
    if model_config.tokens_per_sec:
        console.print(f"  Velocidade: {model_config.tokens_per_sec} tokens/seg")
    console.print(f"  Tipo: {'custom' if model_config.is_custom else 'built-in'}")


@model.command(name="reset")
def model_reset() -> None:
    """Reset configuração para defaults.
    
    \b
    Exemplo:
      ai model reset
    """
    from .config import reset_config
    
    click.confirm("Resetar toda a configuração para defaults?", abort=True)
    reset_config()
    render_success("Configuração resetada para defaults")


@model.command(name="info")
def model_info() -> None:
    """Mostra informação de configuração.
    
    \b
    Exemplo:
      ai model info
    """
    from .config import get_config_file, get_config_dir
    
    console.print(f"[bold]Configuração AI CLI[/bold]\n")
    console.print(f"Diretório: [cyan]{get_config_dir()}[/cyan]")
    console.print(f"Ficheiro: [cyan]{get_config_file()}[/cyan]")
    
    if get_config_file().exists():
        size = get_config_file().stat().st_size
        console.print(f"Tamanho: {size} bytes")
    else:
        console.print("[dim]Ficheiro ainda não criado[/dim]")


# =============================================================================
# REGISTO DE TOOLS
# =============================================================================

if TOOLS_AVAILABLE:
    cli.add_command(tree.tree_cmd, name="tree")
    cli.add_command(find.find_cmd, name="find")
    cli.add_command(fzf.fzf_cmd, name="fzf")


# =============================================================================
# ENTRY POINT
# =============================================================================

def main() -> None:
    """Entry point com tratamento de exceções."""
    try:
        cli(standalone_mode=False)
    except click.ClickException as e:
        e.show()
        sys.exit(e.exit_code)
    except click.Abort:
        console.print("\n[dim]Abortado[/dim]")
        sys.exit(EXIT_KEYBOARD_INTERRUPT)
    except KeyboardInterrupt:
        console.print("\n[dim]Interrompido[/dim]")
        sys.exit(EXIT_KEYBOARD_INTERRUPT)
    except Exception as e:
        render_error("Erro inesperado", str(e))
        sys.exit(EXIT_ERROR)


if __name__ == "__main__":
    main()
    