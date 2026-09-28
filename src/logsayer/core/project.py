"""Lectura de `docs/project_state.md` (Capa 2 — Navegante)."""

from __future__ import annotations

import re
from pathlib import Path

from logsayer.core.memory import split_frontmatter

STATE_PATH = Path("docs") / "project_state.md"

_HUS_HEADER = "## HUs cerradas desde la última auditoría"
_NAME_RE = re.compile(r"^# Estado del proyecto\s*—\s*(.+)$")

_PHASE_KEY = "fase:"
# El valor declarado se vuelve un nombre de archivo permanente
# (`logbook_<fase>_NN.md`), así que solo pasa un slug: letras, dígitos, punto y
# guion. Una frase es una declaración inválida, no un slug que "se limpia".
_PHASE_VALUE_RE = re.compile(r"^[a-z0-9]+(?:[-_.][a-z0-9]+)*$")


def state_file(root: Path) -> Path:
    return root / STATE_PATH


def project_name(root: Path) -> str:
    state = state_file(root)
    if not state.is_file():
        return root.name
    for line in state.read_text(encoding="utf-8").splitlines():
        match = _NAME_RE.match(line.strip())
        if match:
            return match.group(1).strip()
    return root.name


def declared_phase(root: Path) -> str | None:
    """La fase que el estado **declara** en su frontmatter, o None.

    El campo `fase` es un identificador, no una frase: se slugifica a nombre
    de archivo y por eso se valida en vez de normalizarse. Deducirlo de la prosa
    de la sección "Fase actual del roadmap" convertía cualquier frase en un
    logbook permanente —"Fase 6 — ingreso de documentos, cerrada y mergeada…"
    terminó siendo el nombre de un archivo que hubo que borrar a mano.

    None significa "no declarado", y `log add` lo dice en vez de inventar una
    partición: la fase ausente es un pendiente visible, no un default silencioso.
    """
    state = state_file(root)
    if not state.is_file():
        return None
    block, _ = split_frontmatter(state.read_text(encoding="utf-8"))
    if block is None:
        return None
    for line in block:
        candidate = line.strip()
        if not candidate.startswith(_PHASE_KEY):
            continue
        value = candidate[len(_PHASE_KEY) :].strip().strip("\"'").lower()
        if not _PHASE_VALUE_RE.match(value):
            return None
        return value
    return None


def current_phase(root: Path) -> str:
    """Slug de la fase declarada; 'general' si no hay fase declarada."""
    return declared_phase(root) or "general"


def read_closed_hus(root: Path) -> int:
    state = state_file(root)
    if not state.is_file():
        return 0
    text = state.read_text(encoding="utf-8")
    match = re.search(rf"{re.escape(_HUS_HEADER)}\s*\n+\s*(\d+)", text, re.MULTILINE)
    if match is None:
        return 0
    try:
        return int(match.group(1))
    except ValueError:
        return 0


def set_closed_hus(root: Path, value: int) -> None:
    state = state_file(root)
    text = state.read_text(encoding="utf-8")
    new_text, count = re.subn(
        rf"({re.escape(_HUS_HEADER)}\s*\n+\s*)\d+",
        lambda m: m.group(1) + str(value),
        text,
        count=1,
    )
    if count == 0:
        raise ValueError(f"No se encontró la sección '{_HUS_HEADER}' en {state}.")
    state.write_text(new_text, encoding="utf-8")