"""Localización de la raíz de un proyecto logsayer."""

from __future__ import annotations

from pathlib import Path

ROOT_MARKER = "logsayer.toml"


class ProjectRootError(Exception):
    """No se encontró la raíz de un proyecto logsayer."""


def find_logsayer_root(start: Path) -> Path | None:
    """Sube desde `start` buscando `logsayer.toml` (patrón estilo `.git`)."""
    current = start.resolve()
    for directory in (current, *current.parents):
        if (directory / ROOT_MARKER).is_file():
            return directory
    return None


def require_logsayer_root(start: Path) -> Path:
    root = find_logsayer_root(start)
    if root is None:
        raise ProjectRootError(
            f"No se encuentra {ROOT_MARKER} desde {start}. "
            "Corre 'logsayer init' o ejecuta dentro del proyecto."
        )
    return root