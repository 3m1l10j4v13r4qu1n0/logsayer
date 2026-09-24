"""Interfaz de línea de comandos de logsayer (Typer)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from logsayer.adapters.generate import generate_adapters
from logsayer.adapters.registry import AgentError, resolve_adapter
from logsayer.config import LogsayerConfig
from logsayer.core import audit, fremen, logbook, project, specs, suk
from logsayer.core.checks import CheckResult
from logsayer.core.paths import ProjectRootError, require_logsayer_root
from logsayer.core.project import project_name
from logsayer.scaffold import (
    RENDERED_FILES,
    ScaffoldError,
    resolve_target,
    scaffold,
)

app = typer.Typer(
    help="logsayer — sistema de 5 capas documentales para proyectos con agentes IA.",
    no_args_is_help=True,
)

_ROLES: tuple[tuple[str, str], ...] = (
    ("mentat", "Capa 1 — Especificacion (Mentat)."),
    ("navigator", "Capa 2 — Estado (Navegante)."),
    ("reverend-mother", "Capa 3 — Bitacora (Reverenda Madre)."),
    ("truthsayer", "Capa 4 — Verificacion semantica (Decidora)."),
    ("suk", "Capa 4 — Verificacion mecanica (Suk Doctor)."),
    ("fremen", "Capa 5 — Proceso (Fremen)."),
)

_role_typers: dict[str, typer.Typer] = {}
for _name, _help in _ROLES:
    _role_typers[_name] = typer.Typer(help=_help, no_args_is_help=True)
    app.add_typer(_role_typers[_name], name=_name)


def _register_with_alias(role: str, sub: typer.Typer, name: str) -> None:
    """Registra `sub` bajo el grupo del rol y con alias plano en la raíz (spec §5)."""
    _role_typers[role].add_typer(sub, name=name)
    app.add_typer(sub, name=name)


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
        existing = {rel for rel in RENDERED_FILES if (target / rel).is_file()}
        written = scaffold(target, name, LogsayerConfig.load(), adopt=here)
    except ScaffoldError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Scaffold listo en {target}")
    if here and existing:
        typer.echo("Modo adopt: preservados (ya existían, no se sobrescriben):")
        for rel in sorted(existing):
            typer.echo(f"  - {rel}")
    for written_path in written:
        typer.echo(f"Generado: {written_path}")


agent_typer = typer.Typer(
    help="Adaptadores por agente (Capa: coordinación multi-agente).",
    no_args_is_help=True,
)


@agent_typer.command("add")
def agent_add(
    agent: Annotated[
        str,
        typer.Argument(help="Agente destino (opencode | claude)."),
    ],
) -> None:
    """Genera subagentes por rol en la convención nativa del agente."""
    try:
        spec = resolve_adapter(agent)
        root, written = generate_adapters(Path.cwd(), spec)
    except (AgentError, ProjectRootError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    for path in written:
        typer.echo(f"Generado: {path.relative_to(root)}")


app.add_typer(agent_typer, name="agent")


spec_typer = typer.Typer(
    help="Historias de usuario (Capa 1).",
    no_args_is_help=True,
)


@spec_typer.command("new")
def spec_new(
    hu: Annotated[str, typer.Argument(help="Identificador de la HU (ej: HU-01).")],
) -> None:
    """Crea una HU con template mínimo en 04_user_stories/."""
    try:
        root = require_logsayer_root(Path.cwd())
        target = specs.create_hu(root, hu)
    except (ProjectRootError, specs.SpecError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"HU {hu} creada en {target}")


_register_with_alias("mentat", spec_typer, "spec")


state_typer = typer.Typer(
    help="Snapshot del estado del proyecto (Capa 2).",
    no_args_is_help=True,
)


@state_typer.command("show")
def state_show() -> None:
    """Imprime docs/project_state.md (lectura obligatoria al iniciar sesión)."""
    try:
        root = require_logsayer_root(Path.cwd())
        state = project.state_file(root)
    except ProjectRootError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if not state.is_file():
        raise typer.BadParameter(f"No existe {state}. Se crea con 'logsayer init'.")
    typer.echo(state.read_text(encoding="utf-8").rstrip())


_register_with_alias("navigator", state_typer, "state")


log_typer = typer.Typer(
    help="Bitácora append-only, particionada (Capa 3).",
    no_args_is_help=True,
)


@log_typer.command("add")
def log_add(
    text: Annotated[str, typer.Argument(help="Texto de la entrada de bitácora.")],
    phase: Annotated[
        str | None,
        typer.Option(
            "--fase",
            help="Fase del logbook (default: fase actual de project_state.md).",
        ),
    ] = None,
) -> None:
    """Agrega una entrada al logbook activo; particiona si supera el límite."""
    try:
        root = require_logsayer_root(Path.cwd())
        config = LogsayerConfig.load(root / "logsayer.toml")
        result = logbook.add_entry(root, text, config, phase_override=phase)
    except (ProjectRootError, logbook.LogbookError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    path = result["path"]
    assert isinstance(path, Path)
    typer.echo(f"Entrada registrada en {path.relative_to(root)}")


@log_typer.command("index")
def log_index() -> None:
    """Reconstruye docs/logbooks/00_index.md desde los archivos reales."""
    try:
        root = require_logsayer_root(Path.cwd())
        index_path = logbook.write_index(root)
    except (ProjectRootError, logbook.LogbookError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Índice actualizado en {index_path.relative_to(root)}")


_register_with_alias("reverend-mother", log_typer, "log")


audit_typer = typer.Typer(
    help="Verificación semántica spec-vs-código (Capa 4).",
    no_args_is_help=True,
)


@audit_typer.command("run")
def audit_run(
    reset_counter: Annotated[
        bool,
        typer.Option(
            "--reset-counter",
            help="Reinicia el contador de HUs en project_state.md tras la corrida.",
        ),
    ] = False,
) -> None:
    """Genera la estructura del reporte y el prompt; el resultado
    lo produce la Decidora."""
    try:
        root = require_logsayer_root(Path.cwd())
        report = audit.run_audit(root)
        if reset_counter:
            project.set_closed_hus(root, 0)
    except (ProjectRootError, audit.AuditError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Estructura y prompt generados en {report.relative_to(root)}")
    if reset_counter:
        typer.echo("Contador de HUs reiniciado a 0 en project_state.md.")
    else:
        typer.echo("Contador intacto. Al aprobar, corre de nuevo con --reset-counter.")


@audit_typer.command("status")
def audit_status() -> None:
    """Muestra el contador de HUs vs el umbral y el último reporte."""
    try:
        root = require_logsayer_root(Path.cwd())
        config = LogsayerConfig.load(root / "logsayer.toml")
        closed = project.read_closed_hus(root)
        last = audit.last_audit(root)
        threshold = config.audit_threshold_hus
    except ProjectRootError as exc:
        raise typer.BadParameter(str(exc)) from exc
    current = f"HUs cerradas desde la última auditoría: {closed}"
    typer.echo(f"{current} (umbral: {threshold})")
    if last is None:
        typer.echo("Última auditoría: ninguna reportada.")
    else:
        typer.echo(f"Última auditoría: {last.name} ({last.relative_to(root)})")
    if closed >= threshold:
        typer.echo("Estado: corresponde auditar. Ejecuta: logsayer audit run")
    else:
        missing = threshold - closed
        typer.echo(f"Estado: no corresponde auditar (faltan {missing} HUs).")


_register_with_alias("truthsayer", audit_typer, "audit")


def _render_checks(title: str, results: list[CheckResult]) -> None:
    """Imprime el reporte de chequeos y sale con código 1 si algo falló."""
    typer.echo(f"{title}\n")
    failed = 0
    for result in results:
        mark = "✔" if result.ok else "✘"
        typer.echo(f"{mark} {result.name}: {result.detail or 'OK'}")
        if not result.ok:
            failed += 1
    typer.echo()
    if failed:
        message = (
            f"Estado: {failed} chequeo(s) fallido(s). "
            "Corrige antes de continuar."
        )
        typer.echo(message)
        raise typer.Exit(code=1)
    typer.echo("Estado: sano.")


@_role_typers["suk"].command("doctor")
def suk_doctor() -> None:
    """Chequeo mecánico: estructura y no mezcla de capas (Suk Doctor)."""
    try:
        root = require_logsayer_root(Path.cwd())
        results = suk.run_suk(root)
    except ProjectRootError as exc:
        raise typer.BadParameter(str(exc)) from exc
    title = f"Suk Doctor — verificación mecánica de {project_name(root)}"
    _render_checks(title, results)


@app.command("check")
def check() -> None:
    """Alias plano de `suk doctor` (spec §5)."""
    suk_doctor()


@_role_typers["fremen"].command("verify")
def fremen_verify() -> None:
    """Chequeo de proceso: marco operativo y Definition of Ready (Fremen)."""
    try:
        root = require_logsayer_root(Path.cwd())
        results = fremen.run_fremen(root)
    except ProjectRootError as exc:
        raise typer.BadParameter(str(exc)) from exc
    title = f"Fremen — verificación de proceso de {project_name(root)}"
    _render_checks(title, results)


process_typer = typer.Typer(
    help="Chequeo de proceso (Capa 5 — Fremen).",
    no_args_is_help=True,
)


@process_typer.command("check")
def process_check() -> None:
    """Alias plano de `fremen verify` (spec §5)."""
    fremen_verify()


app.add_typer(process_typer, name="process")