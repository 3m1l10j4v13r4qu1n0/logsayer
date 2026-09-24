"""Interfaz de línea de comandos de logsayer (Typer)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from logsayer.config import LogsayerConfig
from logsayer.scaffold import ScaffoldError, resolve_target, scaffold

app = typer.Typer(
    help="logsayer — sistema de 5 capas documentales para proyectos con agentes IA.",
    no_args_is_help=True,
)


def _role_group(name: str, help_text: str) -> None:
    group = typer.Typer(help=help_text, no_args_is_help=True)
    app.add_typer(group, name=name)


for _name, _help in (
    ("mentat", "Capa 1 — Especificacion (Mentat). Comandos disponibles en Fase 2."),
    ("navigator", "Capa 2 — Estado (Navegante). Comandos disponibles en Fase 2."),
    ("reverend-mother", "Capa 3 — Bitacora (Reverenda Madre). Comandos en Fase 2."),
    ("truthsayer", "Capa 4 — Verificacion semantica (Decidora). Comandos en Fase 2."),
    ("suk", "Capa 4 — Verificacion mecanica (Suk Doctor). Comandos en Fase 2."),
    ("fremen", "Capa 5 — Proceso (Fremen). Comandos disponibles en Fase 2."),
):
    _role_group(_name, _help)


@app.command()
def init(
    project_name: Annotated[
        str | None,
        typer.Argument(help="Nombre del proyecto a scaffoldear."),
    ] = None,
    here: Annotated[
        bool,
        typer.Option("--here", help="Scaffoldea en el directorio actual."),
    ] = False,
) -> None:
    """Inicializa la estructura docs/ + AGENTS.md + logsayer.toml."""
    try:
        target, name = resolve_target(project_name, here, Path.cwd())
        scaffold(target, name, LogsayerConfig.load())
    except ScaffoldError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Scaffold listo en {target}")