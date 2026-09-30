"""Fecha de versión de un documento: `git log -1` o mtime, el que sea mayor.

Vive aparte porque lo consumen dos chequeos de capas distintas: `estado_al_dia`
(Suk, Capa 4) e `indice_al_dia` (Fremen, Capa 5). La comparación tiene que ser
la misma en los dos o los dos checks miden cosas diferentes.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def last_commit_ts(root: Path, rel_path: Path) -> float | None:
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


def doc_timestamp(root: Path, path: Path) -> float:
    """Último commit **o** último toque en disco, el que sea más nuevo.

    Se toma el mayor de los dos, y no solo el commit, porque si no la
    comparación mezclaría dos relojes: un archivo commiteado y después editado
    en el working tree seguiría fechada en su commit viejo, mientras que un
    archivo sin versionar se fecha por mtime — y el más nuevo de los dos
    parecería "futuro". Con el máximo, todo queda en la misma escala.
    """
    committed = last_commit_ts(root, path.relative_to(root))
    modified = path.stat().st_mtime
    return modified if committed is None else max(committed, modified)
