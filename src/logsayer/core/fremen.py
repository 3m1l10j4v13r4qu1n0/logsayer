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
from logsayer.core.checks import CheckResult, fail, ok
from logsayer.core.project import state_file
from logsayer.core.suk import L1_STORIES, L5_AGILE, L5_PROCESS


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


def run_fremen(root: Path) -> list[CheckResult]:
    return [
        check_state_documented(root),
        check_process_dirs(root),
        check_agreement(root),
        check_definition_of_ready(root),
    ]