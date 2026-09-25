"""Documentos de Capa 1 — Mentat: historias de usuario y documentos transversales.

El CLI scaffoldea; el contenido lo deriva el subagente (spec §6). Ninguna
función de este módulo redacta Capa 1 a partir de un archivo externo.
"""

from __future__ import annotations

import re
from datetime import date as date_cls
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from logsayer.core import inbox
from logsayer.core.routing import DOC_LAYERS, valid_layer, valid_name

HU_DIR = Path("docs") / "04_user_stories"

HU_RE = re.compile(r"^HU-\d+$")


class SpecError(Exception):
    """Error controlado de la capa de especificación."""


def _environment() -> Environment:
    """Templates de Capa 1.

    `trim_blocks`/`lstrip_blocks` para que los condicionales de `doc.md.j2` no
    dejen líneas en blanco al renderizar; `keep_trailing_newline` porque Jinja
    se come el último newline por default y un markdown sin newline final es un
    archivo mal formado. Ninguno afecta a `hu.md.j2`, que no tiene condicionales.
    """
    return Environment(
        loader=PackageLoader("logsayer", "templates"),
        autoescape=select_autoescape(("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def valid_hu(hu: str) -> bool:
    return bool(HU_RE.fullmatch(hu))


def create_hu(root: Path, hu: str) -> Path:
    """Crea README.md de la HU desde el template mínimo (spec §10)."""
    if not valid_hu(hu):
        raise SpecError(
            f"Identificador de HU inválido: {hu!r}. Usa el formato HU-01, HU-02, ..."
        )
    target = root / HU_DIR / hu / "README.md"
    if target.exists():
        raise SpecError(f"La HU {hu} ya existe: {target}.")
    rendered = _environment().get_template("hu.md.j2").render(hu=hu)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8")
    return target


def create_doc(
    root: Path,
    layer: str,
    name: str,
    from_path: str | None = None,
) -> tuple[Path, Path | None]:
    """Crea un documento de Capa 1 (no-HU) con header estándar y bloque Fuente.

    Devuelve (documento, original archivado en `inbox/_done/`). Con `from_path`
    el original se mueve — nunca se borra — y su procedencia queda registrada en
    el documento, que pasa a ser la versión de referencia (spec §3).
    """
    valid_layer(layer)
    valid_name(name)
    target = root / DOC_LAYERS[layer] / f"{name}.md"
    if target.exists():
        raise SpecError(f"El documento ya existe: {target}.")

    source: Path | None = None
    archived: Path | None = None
    source_note: str | None = None
    source_kind = "markdown"
    if from_path is not None:
        staged, _, source_note = inbox.stage(root, from_path)
        if staged.suffix.lower() in inbox.CONVERTIBLE_EXTENSIONS:
            source_kind = "binary"
        # Se archiva antes de renderizar para que el documento registre la
        # ubicación final del original. Si el write fallara, el archivo queda en
        # `inbox/_done/`, no se pierde: se re-corre `doc new` con otro nombre.
        archived = inbox.mark_done(root, staged.name)
        source = archived

    rendered = _environment().get_template("doc.md.j2").render(
        title=name.replace("_", " ").capitalize(),
        date=date_cls.today().isoformat(),
        source=str(source.relative_to(root)) if source else None,
        source_note=source_note,
        source_kind=source_kind,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8")
    return target, archived

