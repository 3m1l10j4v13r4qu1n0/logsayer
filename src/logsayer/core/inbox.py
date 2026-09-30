"""Bandeja de entrada (`inbox/`): punto de entrada de Capa 1, no una capa.

Vive en la raíz, **fuera de `docs/`** (spec §3): cualquier `.md` adentro de
`docs/` que no pertenezca a una capa dispara `capas_mezcladas`, así que una
bandeja adentro se autovería. No se versiona — su `.gitignore` propio lo declara
sin tocar el del proyecto — y su única salida es entrar a Capa 1.

El módulo mueve archivos y nombra; el contenido lo deriva el subagente Mentat
(spec §6). Borrar lo que el usuario dejó nunca es responsabilidad del CLI.
"""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

INBOX_DIR = Path("inbox")
DONE_SUBDIR = "_done"
GITIGNORE_NAME = ".gitignore"

_GITIGNORE_BODY = "*\n!.gitignore\n"

CONVERTIBLE_EXTENSIONS: frozenset[str] = frozenset(
    {".pdf", ".docx", ".doc", ".odt", ".rtf", ".pptx", ".xlsx", ".epub"}
)


class InboxError(Exception):
    """Error controlado de la bandeja de entrada."""


def inbox_dir(root: Path) -> Path:
    return root / INBOX_DIR


def done_dir(root: Path) -> Path:
    return inbox_dir(root) / DONE_SUBDIR


def ensure_inbox(root: Path) -> Path:
    """Crea `inbox/` con su `.gitignore` si no existe. Idempotente.

    El `.gitignore` va adentro de la bandeja y no en la raíz del proyecto: el
    default "lo que entra no se versiona" se expresa sin que el CLI toque un
    archivo del usuario.
    """
    directory = inbox_dir(root)
    directory.mkdir(parents=True, exist_ok=True)
    ignore = directory / GITIGNORE_NAME
    if not ignore.exists():
        ignore.write_text(_GITIGNORE_BODY, encoding="utf-8")
    return directory


def _resolve_source(root: Path, raw: str) -> Path:
    """Resuelve el path de entrada: absoluto, o relativo a la raíz del proyecto."""
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = (root / candidate).resolve()
    else:
        candidate = candidate.resolve()
    if not candidate.exists():
        raise InboxError(f"No existe el archivo: {candidate}.")
    if not candidate.is_file():
        raise InboxError(f"No es un archivo: {candidate}.")
    return candidate


def _unique_target(directory: Path, name: str) -> Path:
    """Evita pisar: `contrato.pdf`, `contrato-2.pdf`, ..."""
    candidate = directory / name
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2
    while True:
        candidate = directory / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _conversion_warning(path: Path) -> str | None:
    if path.suffix.lower() in CONVERTIBLE_EXTENSIONS:
        return (
            f"{path.name} no es markdown. Convertilo antes de derivarlo "
            "(el CLI no convierte PDF ni docx); el documento derivado va en "
            "Capa 1 y este archivo queda en la bandeja."
        )
    return None


def stage(root: Path, raw_path: str) -> tuple[Path, bool, str | None]:
    """Deja el archivo en `inbox/`. Devuelve (ruta, lo movió, aviso).

    Tolera que ya esté en la bandeja: ese es el flujo normal de `check` →
    `doc route` → `doc new --from inbox/<archivo>`, así que re-ingresar un
    archivo ya bandeado no es un error, es lo esperado.
    """
    source = _resolve_source(root, raw_path)
    if source.is_relative_to(inbox_dir(root).resolve()):
        return source, False, _conversion_warning(source)
    ensure_inbox(root)
    target = _unique_target(inbox_dir(root), source.name)
    shutil.move(str(source), str(target))
    return target, True, _conversion_warning(target)


def add(root: Path, raw_path: str) -> tuple[Path, str | None]:
    """Mueve el archivo señalado a `inbox/`. Devuelve (destino, aviso).

    Es el único punto del framework que toca un archivo del usuario, y solo
    uno: el que el humano le señaló explícitamente. A diferencia de `stage`, acá
    un archivo que ya está en la bandeja es un error: lo que el usuario quiere
    en ese caso es decidir su capa, no re-ingresarlo.
    """
    source = _resolve_source(root, raw_path)
    if source.is_relative_to(inbox_dir(root).resolve()):
        raise InboxError(
            f"{source.name} ya está en la bandeja. "
            "Usá 'logsayer doc route' para decidir su capa."
        )
    ensure_inbox(root)
    target = _unique_target(inbox_dir(root), source.name)
    shutil.move(str(source), str(target))
    return target, _conversion_warning(target)


def pending(root: Path) -> list[Path]:
    """Archivos esperando ubicación, excluyendo `inbox/_done/`."""
    directory = inbox_dir(root)
    if not directory.is_dir():
        return []
    files = [path for path in directory.iterdir() if path.is_file()]
    return sorted(
        path for path in files if path.name not in (GITIGNORE_NAME,)
    )


def mark_done(root: Path, name: str) -> Path:
    """Mueve un archivo ya procesado a `inbox/_done/` (spec §3)."""
    source = inbox_dir(root) / name
    if not source.is_file():
        others = ", ".join(path.name for path in pending(root))
        raise InboxError(
            f"{name} no está en la bandeja. Pendientes: {others or 'ninguno'}."
        )
    done = done_dir(root)
    done.mkdir(parents=True, exist_ok=True)
    target = _unique_target(done, name)
    shutil.move(str(source), str(target))
    return target


def age_days(path: Path, now: datetime | None = None) -> int:
    """Antigüedad en días del archivo, por mtime."""
    reference = now or datetime.now(UTC)
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    return max(0, (reference - modified).days)


def is_stale(path: Path, max_age_days: int, now: datetime | None = None) -> bool:
    return age_days(path, now) > max_age_days
