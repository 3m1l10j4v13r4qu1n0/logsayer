"""Chequeo mecánico (Capa 4 — Suk Doctor): diagnóstico protocolizado y
determinístico de la salud estructural de un proyecto logsayer (spec §13.4.1).

Un bot: mismo proyecto → mismo resultado. Sin juicio: solo reglas objetivas
de estructura, estado y no mezcla de capas (regla de oro, spec §2).
"""

from __future__ import annotations

from pathlib import Path

from logsayer.core.checks import CheckResult, fail, ok
from logsayer.core.project import state_file

L1_GLOBAL = Path("docs") / "01_global"
L1_TECHNICAL = Path("docs") / "02_technical"
L1_STORIES = Path("docs") / "04_user_stories"
L5_PROCESS = Path("docs") / "03_process"
L5_AGILE = Path("docs") / "05_agile_methodology"
L4_AUDITS = Path("docs") / "06_audits"
L3_LOGBOOKS = Path("docs") / "logbooks"

LAYERED_MD_DIRS: tuple[Path, ...] = (
    L1_GLOBAL,
    L1_TECHNICAL,
    L5_PROCESS,
    L1_STORIES,
    L5_AGILE,
    L4_AUDITS,
    L3_LOGBOOKS,
)

_PHASE_HEADER = "## Fase actual del roadmap"
_DECISIONS_HEADER = "## Decisiones activas"
_HUS_HEADER = "## HUs cerradas desde la última auditoría"


def _rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def check_markers(root: Path) -> CheckResult:
    markers = ("logsayer.toml", "AGENTS.md")
    missing = [name for name in markers if not (root / name).is_file()]
    if missing:
        return fail("marcadores_raiz", "faltan: " + ", ".join(missing))
    return ok("marcadores_raiz")


def check_layered_dirs(root: Path) -> CheckResult:
    missing = [
        str(relative)
        for relative in LAYERED_MD_DIRS
        if not (root / relative).is_dir()
    ]
    if missing:
        return fail("estructura_capas", "faltan: " + ", ".join(missing))
    return ok("estructura_capas")


def check_state(root: Path) -> CheckResult:
    state = state_file(root)
    if not state.is_file():
        return fail("estado_capa2", f"no existe {_rel(root, state)}")
    text = state.read_text(encoding="utf-8")
    issues = [
        f"falta sección '{header}'"
        for header in (_PHASE_HEADER, _DECISIONS_HEADER, _HUS_HEADER)
        if header not in text
    ]
    if issues:
        return fail("estado_capa2", "; ".join(issues))
    return ok("estado_capa2")


def check_logbook_index(root: Path) -> CheckResult:
    """El índice debe listar exactamente los logbooks reales (spec §7.5)."""
    logs_dir = root / L3_LOGBOOKS
    index = logs_dir / "00_index.md"
    if not index.is_file():
        return fail("bitacora_indice", f"no existe {_rel(root, index)}")
    listed: set[str] = set()
    for line in index.read_text(encoding="utf-8").splitlines():
        if "|" in line and "logbook_" in line:
            for cell in line.split("|"):
                cell = cell.strip()
                if cell.startswith("logbook_") and cell.endswith(".md"):
                    listed.add(cell)
    real = {path.name for path in logs_dir.glob("logbook_*.md")}
    issues = []
    for name in sorted(real - listed):
        issues.append(f"no listado en el índice: {name}")
    for name in sorted(listed - real):
        issues.append(f"listado pero inexistente: {name}")
    if issues:
        return fail("bitacora_indice", "; ".join(issues))
    return ok("bitacora_indice")


def check_hu_layout(root: Path) -> CheckResult:
    stories = root / L1_STORIES
    docs = root / "docs"
    if not stories.is_dir():
        return fail("hus_ubicacion", f"no existe {_rel(root, stories)}")
    misplaced = []
    if docs.is_dir():
        for path in docs.rglob("HU-*"):
            if not path.is_dir() or str(path).startswith(str(stories)):
                continue
            misplaced.append(str(path.relative_to(docs)))
    if misplaced:
        issues = "carpetas HU-* fuera de docs/04_user_stories/: " + ", ".join(
            misplaced
        )
        return fail("hus_ubicacion", issues)
    return ok("hus_ubicacion")


def check_mixed_layers(root: Path) -> CheckResult:
    """Regla de oro (§2): cada documento vive en una sola capa."""
    docs = root / "docs"
    findings: list[tuple[str, Path]] = []
    if docs.is_dir():
        layered_prefixes = [str(root / layer) + "/" for layer in LAYERED_MD_DIRS]
        state_resolved = str(state_file(root).resolve())
        for path in docs.rglob("*.md"):
            resolver = str(path.resolve())
            if resolver.startswith(
                tuple(layered_prefixes)
            ) or resolver == state_resolved:
                continue
            if path.name.startswith("audit_"):
                findings.append(
                    ("reporte de auditoría fuera de docs/06_audits/", path)
                )
            elif path.name.startswith("logbook_"):
                findings.append(("bitácora fuera de docs/logbooks/", path))
            else:
                findings.append(("documento markdown fuera de capa", path))
    issues = [f"{label}: {_rel(root, path)}" for label, path in findings]
    if issues:
        return fail("capas_mezcladas", "\n   - " + "\n   - ".join(issues))
    return ok("capas_mezcladas")


def run_suk(root: Path) -> list[CheckResult]:
    """Corre todos los chequeos del Suk Doctor en orden de severidad."""
    return [
        check_markers(root),
        check_layered_dirs(root),
        check_state(root),
        check_logbook_index(root),
        check_hu_layout(root),
        check_mixed_layers(root),
    ]