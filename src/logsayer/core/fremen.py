"""Chequeo de proceso (Capa 5 — Fremen): protocolo fijo de cómo se trabaja
(spec §13.5). Un bot determinístico: verifica que el marco operativo del
proyecto esté desplegado y alineado con la configuración (spec §4).

DoR y checklist de merge son reglas del equipo que viven en `docs/03_process/`
y `docs/05_agile_methodology/`; aquí solo se verifica que existan, que la
coordinación del agente no haya divergido de los umbrales, y que la Definition
of Ready se respete (toda HU en 04_user_stories lista para trabajar).
"""

from __future__ import annotations

from pathlib import Path

from logsayer.config import LogsayerConfig
from logsayer.core import memory
from logsayer.core.checks import CheckResult, fail, ok, warn
from logsayer.core.freshness import doc_timestamp
from logsayer.core.project import state_file
from logsayer.core.suk import L1_GLOBAL, L1_STORIES, L1_TECHNICAL, L5_AGILE, L5_PROCESS


def _rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def check_state_documented(root: Path) -> CheckResult:
    """El cierre de sesión deja el estado documentado: existe project_state.md."""
    state = state_file(root)
    if not state.is_file():
        return fail("estado_documentado", f"no existe {_rel(root, state)}")
    return ok("estado_documentado")


def check_process_dirs(root: Path) -> CheckResult:
    missing = [
        str(relative)
        for relative in (L5_PROCESS, L5_AGILE)
        if not (root / relative).is_dir()
    ]
    if missing:
        return fail("proceso_desplegado", "faltan: " + ", ".join(missing))
    return ok("proceso_desplegado")


def check_agreement(root: Path) -> CheckResult:
    """AGENTS.md coordinador debe reflejar los umbrales de logsayer.toml (§4)."""
    agents_md = root / "AGENTS.md"
    if not agents_md.is_file():
        return fail("acuerdo_coordinacion", f"no existe {_rel(root, agents_md)}")
    config = LogsayerConfig.load(root / "logsayer.toml")
    text = agents_md.read_text(encoding="utf-8")
    expected = {
        "contexto": f"{config.context_threshold_percent}%",
        "bitácora": f"{config.bitacora_max_lines} líneas",
        "auditoría": f">= {config.audit_threshold_hus} HUs",
    }
    diverges = [
        f"{label} ({token})"
        for label, token in expected.items()
        if token not in text
    ]
    if diverges:
        return fail(
            "acuerdo_coordinacion",
            "AGENTS.md no refleja: " + ", ".join(diverges),
        )
    return ok("acuerdo_coordinacion")


def check_definition_of_ready(root: Path) -> CheckResult:
    """Toda HU presente debe estar lista: carpeta con README (template mínimo)."""
    stories = root / L1_STORIES
    if not stories.is_dir():
        return fail("definition_of_ready", f"no existe {_rel(root, stories)}")
    not_ready = [
        path.name
        for path in sorted(stories.glob("HU-*"))
        if path.is_dir() and not (path / "README.md").is_file()
    ]
    if not_ready:
        return fail("definition_of_ready", "sin README.md: " + ", ".join(not_ready))
    return ok("definition_of_ready")


def check_index_freshness(root: Path) -> CheckResult:
    """El índice no puede estar viejo sin que nadie lo note.

    Mecánico, como `estado_al_dia`: si un documento de Capa 1 tiene fecha de
    versión más nueva que `docs/00_memory_index.md`, el retrieval va a seguir
   devolviendo candidatos de una memoria que ya no existe. Es un `warn` y
    no un `fail` (D7): un índice viejo se arregla con un comando, no es una
    estructura rota.

    El alcance es Capa 1 a propósito. `log add` anexa al logbook (Capa 3) y el
    cierre de sesión reescribe `project_state.md`: si el check los mirara, casi
    todo cierre dejaría el índice viejo y un aviso que aparece siempre deja de
    avisar. Las capas que no compiten por ser fuente de verdad de una HU (D15)
    no cambian lo que el agente tiene que leer primero.
    """
    target = memory.index_path(root)
    if not target.is_file():
        return ok("indice_al_dia", "sin índice (opcional)")
    index_ts = doc_timestamp(root, target)
    newest: tuple[float, str] | None = None
    count = 0
    for layer in (L1_GLOBAL, L1_TECHNICAL, L1_STORIES):
        directory = root / layer
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.md")):
            if not path.is_file():
                continue
            stamp = doc_timestamp(root, path)
            if stamp <= index_ts:
                continue
            count += 1
            if newest is None or stamp > newest[0]:
                newest = (stamp, _rel(root, path))
    if newest is not None:
        more = f" (+{count - 1} más)" if count > 1 else ""
        return warn(
            "indice_al_dia",
            f"Capa 1 cambió después del índice; el más nuevo es {newest[1]}{more}\n"
            "   → logsayer memory index",
        )
    return ok("indice_al_dia")


def run_fremen(root: Path) -> list[CheckResult]:
    return [
        check_state_documented(root),
        check_process_dirs(root),
        check_agreement(root),
        check_definition_of_ready(root),
        check_index_freshness(root),
    ]
