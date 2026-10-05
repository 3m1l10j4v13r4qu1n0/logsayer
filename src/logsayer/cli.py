"""Interfaz de línea de comandos de logsayer (Typer)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from logsayer.adapters.generate import generate_adapters
from logsayer.adapters.registry import AgentError, resolve_adapter
from logsayer.config import LogsayerConfig
from logsayer.core import (
    audit,
    fremen,
    inbox,
    logbook,
    memory,
    project,
    routing,
    specs,
    suk,
)
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
        typer.Argument(help="Agente destino (opencode | claude | copilot)."),
    ],
) -> None:
    """Genera los roles del framework en la convención nativa del agente."""
    try:
        spec = resolve_adapter(agent)
        root, written = generate_adapters(Path.cwd(), spec)
    except (AgentError, ProjectRootError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    for path in written:
        typer.echo(f"Generado: {path.relative_to(root)}")


app.add_typer(agent_typer, name="agent")


inbox_typer = typer.Typer(
    help="Bandeja de entrada de documentos externos (punto de entrada de Capa 1).",
    no_args_is_help=False,
)


@inbox_typer.callback(invoke_without_command=True)
def inbox_list(ctx: typer.Context) -> None:
    """Sin subcomando, lista lo que está esperando ubicación."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        root = require_logsayer_root(Path.cwd())
    except ProjectRootError as exc:
        raise typer.BadParameter(str(exc)) from exc
    items = inbox.pending(root)
    if not items:
        typer.echo("Bandeja vacía: no hay documentos esperando ubicación.")
        return
    typer.echo(f"Bandeja — {len(items)} documento(s) esperando ubicación:")
    for path in items:
        typer.echo(f"  - {path.relative_to(root)}")
    typer.echo("siguiente: logsayer doc route <archivo>  (Mentat decide la capa)")


@inbox_typer.command("add")
def inbox_add(
    path: Annotated[
        str,
        typer.Argument(help="Archivo a mover a inbox/ (ej: ~/Downloads/contrato.pdf)."),
    ],
) -> None:
    """Mueve un documento externo a inbox/ y deja constancia del próximo paso."""
    try:
        root = require_logsayer_root(Path.cwd())
        target, warning = inbox.add(root, path)
    except (ProjectRootError, inbox.InboxError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Movido a {target.relative_to(root)}")
    if warning:
        typer.echo(f"Aviso: {warning}")
    typer.echo("Siguiente: logsayer doc route " + str(target.relative_to(root)))


app.add_typer(inbox_typer, name="inbox")


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


doc_typer = typer.Typer(
    help="Documentos de Capa 1 transversales (no-HU): ruteo y creación.",
    no_args_is_help=True,
)


@doc_typer.command("route")
def doc_route(
    path: Annotated[
        str | None,
        typer.Argument(help="Archivo a rutear. Sin argumento, imprime la tabla."),
    ] = None,
) -> None:
    """Imprime a qué capa va un documento. No escribe nada (spec §3)."""
    if path is None:
        typer.echo("¿Dónde va mi documento?\n")
        typer.echo(routing.to_markdown())
        typer.echo(f"\n{routing.NARRATIVE_NOTE}")
        typer.echo(
            "\nEl CLI no redacta el contenido: elige la capa y creá el documento "
            "con el comando de la fila."
        )
        return
    try:
        root = require_logsayer_root(Path.cwd())
        verdict = routing.resolve(root, path)
    except (ProjectRootError, routing.RoutingError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    if verdict.is_decided:
        assert verdict.decided is not None
        route = verdict.decided
        typer.echo(f"→ capa:      {route.destination}")
        typer.echo(f"→ versión:   {route.versioned}")
        typer.echo(f"→ crear:     {route.command}")
        if route.note:
            typer.echo(f"→ nota:      {route.note}")
        typer.echo(f"→ por qué:   {verdict.reason}")
        return
    if verdict.duplicate is not None:
        typer.echo(f"→ sin destino: {verdict.reason}")
        return
    typer.echo(f"→ sin decisión automática. {verdict.reason}")
    if verdict.hint:
        typer.echo(f"→ pista:      {verdict.hint}")
    typer.echo("\nCandidatos:")
    for route in verdict.candidates:
        typer.echo(f"  · {route.destination} — crear con: {route.command}")
    typer.echo(
        "\nElegí la fila que corresponde y creá el documento con ese comando. "
        "Si ninguna aplica, la fila es 'El por qué o el cómo de lo que ya se "
        "hizo' (bitácora)."
    )


@doc_typer.command("new")
def doc_new(
    layer: Annotated[
        str,
        typer.Argument(help="Capa 1 de destino: global | technical."),
    ],
    name: Annotated[
        str,
        typer.Argument(help="Nombre del documento en snake_case (ej: contrato_api)."),
    ],
    from_path: Annotated[
        str | None,
        typer.Option(
            "--from",
            help="Documento de origen; se archiva en inbox/_done/ y queda su "
            "procedencia en el bloque '## Fuente'.",
        ),
    ] = None,
) -> None:
    """Crea un documento de Capa 1 con header estándar. Para HUs: spec new."""
    try:
        root = require_logsayer_root(Path.cwd())
        created = specs.create_doc(root, layer, name, from_path)
    except (
        ProjectRootError,
        inbox.InboxError,
        routing.RoutingError,
        specs.SpecError,
    ) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Documento creado en {created.target.relative_to(root)}")
    if created.archived is not None:
        typer.echo(f"Origen archivado en {created.archived.relative_to(root)}")
        if created.notice is not None:
            typer.echo(f"Aviso: {created.notice}")
        typer.echo(
            "El contenido lo deriva el subagente Mentat: "
            "el CLI solo lo scaffoldeó."
        )


_register_with_alias("mentat", doc_typer, "doc")


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


memory_typer = typer.Typer(
    help="Índice de memoria: navegación transversal sobre docs/ (no es una capa).",
    no_args_is_help=True,
)


@memory_typer.command("index")
def memory_index() -> None:
    """Regenera docs/00_memory_index.md desde los documentos reales."""
    try:
        root = require_logsayer_root(Path.cwd())
        index, count = memory.render_index(root)
    except ProjectRootError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(
        f"Índice actualizado en {index.relative_to(root)} ({count} documentos)"
    )


@memory_typer.command("status")
def memory_status() -> None:
    """Inventario del índice: qué indexa, cuántas tags y cuándo se generó."""
    try:
        root = require_logsayer_root(Path.cwd())
        report = memory.status(root)
    except ProjectRootError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo("Índice de memoria")
    for label, value in report.rows():
        typer.echo(f"  {label}: {value}")
    if report.exists:
        typer.echo("\nRegenerar con: logsayer memory index")
    else:
        typer.echo("\nTodavía no existe. Generalo con: logsayer memory index")


@memory_typer.command("search")
def memory_search(
    query: Annotated[str, typer.Argument(help="Consulta sobre las tags del índice.")],
    capa: Annotated[
        str | None,
        typer.Option(
            "--capa",
            help="Filtra por capa (global, technical, stories, audits, logbooks, …).",
        ),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", help="Máximo de candidatos a listar (0 = todos)."),
    ] = memory.DEFAULT_LIMIT,
) -> None:
    """Candidatos ordenados: qué leer primero, no qué es auditable."""
    try:
        root = require_logsayer_root(Path.cwd())
        hits = memory.search(root, query, capa=capa, limit=limit)
        total = len(memory.load_index(root))
    except (ProjectRootError, memory.MemoryError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    if not hits:
        typer.echo(f"Sin coincidencias para {query!r} en el índice de memoria.")
        typer.echo("\nEl índice puede estar viejo: logsayer fremen verify")
        return
    width = max(len(hit.document.path.as_posix()) for hit in hits)
    typer.echo(f"{len(hits)} de {total} documentos · {query!r}")
    for position, hit in enumerate(hits, start=1):
        typer.echo(f"  {position}. {hit.row(width)}")


_register_with_alias("navigator", memory_typer, "memory")


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
            help="Fase del logbook (default: campo 'fase' de project_state.md).",
        ),
    ] = None,
) -> None:
    """Agrega una entrada al logbook activo; particiona si supera el límite."""
    try:
        root = require_logsayer_root(Path.cwd())
        config = LogsayerConfig.load(root / "logsayer.toml")
        undeclared = phase is None and project.declared_phase(root) is None
        result = logbook.add_entry(root, text, config, phase_override=phase)
    except (ProjectRootError, logbook.LogbookError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    path = result["path"]
    assert isinstance(path, Path)
    typer.echo(f"Entrada registrada en {path.relative_to(root)}")
    if undeclared:
        typer.echo(
            "\n! Sin fase declarada en docs/project_state.md: la entrada cayó en "
            "'general'.\n  Declarala en el frontmatter (campo 'fase:') o pasá "
            "--fase para no partir la bitácora."
        )


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
            help="[DEPRECATED] No resetea desde audit run. Usá 'logsayer audit reset'.",
            callback=lambda v: v,
        ),
    ] = False,
    only: Annotated[
        str | None,
        typer.Option(
            "--hu",
            help="Emite el brief de una sola pasada (HU-07).",
        ),
    ] = None,
) -> None:
    """Genera la estructura del reporte y el prompt; el resultado
    lo produce la Decidora."""
    try:
        root = require_logsayer_root(Path.cwd())
        if reset_counter:
            typer.echo(
                "--reset-counter ya no resetea: usá logsayer audit reset",
                err=True,
            )
            raise typer.Exit(code=1)
        artifact = audit.run_audit(root, only=only)
    except (ProjectRootError, audit.AuditError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    where = artifact.relative_to(root)
    if only is not None:
        typer.echo(f"Brief de la pasada {only} generado en {where}")
        typer.echo("El alcance no cambia: es el input de repetir una fila.")
        return
    typer.echo(f"Estructura y prompt generados en {where}")
    typer.echo("Contador intacto. Al aprobar, corre logsayer audit reset.")


@audit_typer.command("status")
def audit_status() -> None:
    """Muestra el contador de HUs vs el umbral y el último reporte."""
    try:
        root = require_logsayer_root(Path.cwd())
        config = LogsayerConfig.load(root / "logsayer.toml")
        closed = project.read_closed_hus(root)
        last = audit.last_audit(root)
        derived = audit.derived_closed_hus(root)
        threshold = config.audit_threshold_hus
    except (ProjectRootError, OSError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(
        f"HUs cerradas desde la última auditoría: {closed} (umbral: {threshold})"
    )
    if last is None:
        typer.echo("Última auditoría: ninguna")
    else:
        typer.echo(f"Última auditoría: {last.relative_to(root)}")
    if derived is None:
        typer.echo("Derivadas del disco: no se mide (sin auditoría sellada).")
    else:
        where = derived.source.relative_to(root)
        listing = ", ".join(derived.hus) if derived.hus else "ninguna"
        typer.echo(
            f"Derivadas del disco: {derived.count} HU(s) sin veredicto en "
            f"{where} ({listing})"
        )
        if closed < derived.count:
            typer.echo(
                "! El contador declarado queda por debajo del derivado: es el "
                "número que decide si toca auditar, así que el desvase retrasa "
                "la auditoría. Corregilo en docs/project_state.md."
            )
    if closed >= threshold:
        typer.echo("Estado: corresponde auditar. Ejecuta: logsayer audit run")
    else:
        missing = threshold - closed
        typer.echo(f"Estado: en pausa. Restan {missing} HUs para proponer auditoría.")


@audit_typer.command("reset")
def audit_reset() -> None:
    """Reinicia el contador de HUs (no corrige reportes ni genera artefactos)."""
    try:
        root = require_logsayer_root(Path.cwd())
        pending = audit.pending_verdicts(root)
    except ProjectRootError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if pending:
        listing = ", ".join(pending)
        raise typer.BadParameter(
            f"Hay HUs con veredicto pendiente: {listing}. "
            "Completalas antes de resetear."
        )
    project.set_closed_hus(root, 0)
    typer.echo("Contador de HUs reiniciado a 0 en docs/project_state.md.")


_register_with_alias("truthsayer", audit_typer, "audit")


def _render_checks(title: str, results: list[CheckResult]) -> None:
    """Imprime el reporte de chequeos y sale con código 1 si algo falló.

    Los `warn` se muestran pero no alteran el exit code: son pendientes, no
    fallas.
    """
    typer.echo(f"{title}\n")
    failed = 0
    warned = 0
    for result in results:
        typer.echo(f"{result.mark} {result.name}: {result.detail or 'OK'}")
        if result.status == "fail":
            failed += 1
        elif result.status == "warn":
            warned += 1
    typer.echo()
    if failed:
        message = (
            f"Estado: {failed} chequeo(s) fallido(s). "
            "Corrige antes de continuar."
        )
        typer.echo(message)
        raise typer.Exit(code=1)
    if warned:
        typer.echo(
            f"Estado: sano con {warned} chequeo(s) en aviso. "
            "No bloquea, pero atendelos."
        )
        return
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