"""Lectura de `docs/project_state.md` (Capa 2 — Navegante)."""

from __future__ import annotations

import re
from pathlib import Path

STATE_PATH = Path("docs") / "project_state.md"

_PHASE_HEADER = "## Fase actual del roadmap"
_HUS_HEADER = "## HUs cerradas desde la última auditoría"
_NAME_RE = re.compile(r"^# Estado del proyecto\s*—\s*(.+)$")

_PLACEHOLDER = ("_(", "_(definir", "placeholder")


def state_file(root: Path) -> Path:
    return root / STATE_PATH


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "general"


def project_name(root: Path) -> str:
    state = state_file(root)
    if not state.is_file():
        return root.name
    for line in state.read_text(encoding="utf-8").splitlines():
        match = _NAME_RE.match(line.strip())
        if match:
            return match.group(1).strip()
    return root.name


def current_phase(root: Path) -> str:
    """Slug de la fase actual; 'general' si está en blanco/placeholder o no existe."""
    state = state_file(root)
    if not state.is_file():
        return "general"
    lines = state.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.strip() == _PHASE_HEADER:
            for candidate in lines[index + 1 :]:
                stripped = candidate.strip()
                if not stripped:
                    continue
                if stripped.startswith("##"):
                    return "general"
                lowered = stripped.lower()
                if not any(token in lowered for token in _PLACEHOLDER):
                    return _slug(stripped)
                return "general"
            return "general"
    return "general"


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