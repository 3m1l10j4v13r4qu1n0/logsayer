"""Historias de usuario (Capa 1 — Mentat): creación con template mínimo."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

HU_DIR = Path("docs") / "04_user_stories"

HU_RE = re.compile(r"^HU-\d+$")


class SpecError(Exception):
    """Error controlado de la capa de especificación."""


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
    env = Environment(
        loader=PackageLoader("logsayer", "templates"),
        autoescape=select_autoescape(("html", "xml")),
    )
    rendered = env.get_template("hu.md.j2").render(hu=hu)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8")
    return target