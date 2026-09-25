"""Chequeo mecánico (Capa 4 — Suk Doctor): diagnóstico protocolizado y
determinístico de la salud estructural de un proyecto logsayer (spec §13.4.1).

Un bot: mismo proyecto → mismo resultado. Sin juicio: solo reglas objetivas
de estructura, estado y no mezcla de capas (regla de oro, spec §2).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from logsayer.config import LogsayerConfig
from logsayer.core.checks import CheckResult, fail, ok, warn
from logsayer.core.inbox import age_days, inbox_dir, is_stale, pending
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


_SUGGESTIONS: tuple[tuple[str, str], ...] = (
    ("audit_", "06_audits/"),
    ("logbook_", "logbooks/"),
    ("hu-", "04_user_stories/<HU>/"),
)


def _suggest(path: Path) -> str:
    """Destino sugerido para un documento que vive fuera de capa (F3)."""
    name = path.name.lower()
    for prefix, destination in _SUGGESTIONS:
        if name.startswith(prefix):
            return destination
    if name == "project_state.md":
        return "docs/ (Capa 2 — Estado)"
    return (
        "01_global/ si es visión o regla de negocio; 02_technical/ si es "
        "técnico. Decidilo con 'logsayer doc route'"
    )


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
    issues = [
        f"{label}: {_rel(root, path)}\n     → sugerido: docs/{_suggest(path)}"
        for label, path in findings
    ]
    if issues:
        return fail("capas_mezcladas", "\n   - ".join(issues))
    return ok("capas_mezcladas")



_HEADER_TITLE_RE = re.compile(r"^#\s+\S")
_HEADER_DATE_RE = re.compile(r"^Fecha:\s*\d{4}-\d{2}-\d{2}\s*·\s*Estado:\s*\S+")
_HEADER_SECTIONS: tuple[str, ...] = ("## Resumen",)


def check_layer1_headers(root: Path) -> CheckResult:
    """Los documentos de Capa 1 no-HU llevan el header estándar (F8).

    Solo `01_global/` y `02_technical/`: las HUs tienen su propio template
    (`hu.md.j2`) y este check no judgea HUs. Los `.md` fuera de `docs/` no se
    escanean — no son de ninguna capa.
    """
    issues: list[str] = []
    for layer in (L1_GLOBAL, L1_TECHNICAL):
        directory = root / layer
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            missing: list[str] = []
            if not lines or not _HEADER_TITLE_RE.match(lines[0]):
                missing.append("'# Título'")
            if not any(_HEADER_DATE_RE.match(line.strip()) for line in lines[:8]):
                missing.append("'Fecha: YYYY-MM-DD · Estado: <estado>'")
            missing.extend(
                f"'{section}'"
                for section in _HEADER_SECTIONS
                if section not in text
            )
            if missing:
                issues.append(f"{_rel(root, path)}: falta " + ", ".join(missing))
    if issues:
        return fail("header_capa1", "\n   - ".join(issues))
    return ok("header_capa1")


def _last_commit_ts(root: Path, rel_path: Path) -> float | None:
    """Fecha del último commit del archivo, o None si no es un repo git."""
    try:
        completed = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(rel_path)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    raw = completed.stdout.strip()
    if not raw.isdigit():
        return None
    return float(raw)


def _doc_timestamp(root: Path, path: Path) -> float:
    """Fecha de versión de un documento: último commit **o** último toque en disco.

    Se toma el mayor de los dos, y no solo el commit, porque si no la
    comparación mezclaría dos relojes: un archivo commiteado y después editado
    en el working tree seguiría fechada en su commit viejo, mientras que un
    archivo sin versionar se fecha por mtime — y el más nuevo de los dos
    parecería "futuro". Con el máximo, todo queda en la misma escala.
    """
    committed = _last_commit_ts(root, path.relative_to(root))
    modified = path.stat().st_mtime
    return modified if committed is None else max(committed, modified)


def check_state_freshness(root: Path) -> CheckResult:
    """El snapshot no puede quedar viejo sin que nadie lo note (F7).

    Mecánico y sin juicio: si un documento de Capa 1 tiene fecha de versión más
    nueva que `project_state.md`, el estado está desactualizado. La coherencia
    de *contenido* entre capas es de la Decidora (spec §10), esto solo mira
    fechas.
    """
    state = state_file(root)
    if not state.is_file():
        return ok("estado_al_dia", "sin estado que comparar")
    state_ts = _doc_timestamp(root, state)
    newer: list[str] = []
    for layer in (L1_GLOBAL, L1_TECHNICAL, L1_STORIES):
        directory = root / layer
        if not directory.is_dir():
            continue
        candidates = [path for path in directory.rglob("*.md") if path.is_file()]
        for path in sorted(candidates):
            if _doc_timestamp(root, path) > state_ts:
                newer.append(_rel(root, path))
    if newer:
        return warn(
            "estado_al_dia",
            f"Capa 1 cambió después del último estado ({len(newer)}): "
            + "; ".join(newer)
            + "\n   → actualizá docs/project_state.md al cierre de la sesión",
        )
    return ok("estado_al_dia")


def check_inbox(root: Path, config: LogsayerConfig) -> CheckResult:
    """Reporta documentos sin ubicar en `inbox/` (spec §3, §13.4.1).

    Es un `warn`, no un `fail`: una bandeja con pendientes es un proyecto sano
    con un pendiente. La bandeja ausente tampoco es un fallo — es opcional, y
    exigirla rompería `check` en todo proyecto scaffoldeado antes de la fase 6.
    """
    if not inbox_dir(root).is_dir():
        return ok("bandeja_entrada", "sin bandeja (opcional)")
    files = pending(root)
    if not files:
        return ok("bandeja_entrada", "vacía")
    listing = "\n   - ".join(_rel(root, path) for path in files)
    stale = [
        f"{_rel(root, path)} ({age_days(path)} días)"
        for path in files
        if is_stale(path, config.inbox_max_age_days)
    ]
    detail = (
        f"{len(files)} sin ubicar (umbral de aviso: "
        f"{config.inbox_max_age_days} días)\n"
        f"   - {listing}\n"
        "   siguiente: logsayer doc route <archivo>  (Mentat decide la capa)"
    )
    if stale:
        detail += "\n   envejecidos: " + "; ".join(stale)
    return warn("bandeja_entrada", detail)


def run_suk(root: Path) -> list[CheckResult]:
    """Corre todos los chequeos del Suk Doctor en orden de severidad."""
    config = LogsayerConfig.load(root / "logsayer.toml")
    return [
        check_markers(root),
        check_layered_dirs(root),
        check_state(root),
        check_logbook_index(root),
        check_hu_layout(root),
        check_mixed_layers(root),
        check_layer1_headers(root),
        check_inbox(root, config),
        check_state_freshness(root),
    ]
