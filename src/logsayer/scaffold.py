"""Scaffold de `docs/` + `AGENTS.md` + `logsayer.toml` (Fase 1 del roadmap)."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from logsayer.config import LogsayerConfig

STATIC_DIRS: tuple[str, ...] = (
    "01_global",
    "02_technical",
    "03_process",
    "04_user_stories",
    "05_agile_methodology",
    "06_audits",
    "logbooks",
)

RENDERED_FILES: dict[str, str] = {
    "AGENTS.md": "AGENTS.md.j2",
    "logsayer.toml": "logsayer.toml.j2",
    "docs/project_state.md": "project_state.md.j2",
    "docs/logbooks/00_index.md": "00_index.md.j2",
}

_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class ScaffoldError(Exception):
    """Error controlado durante el scaffold."""


def valid_slug(name: str) -> bool:
    return bool(_SLUG_RE.fullmatch(name))


def validate_target(target: Path) -> None:
    if target.exists() and any(target.iterdir()):
        raise ScaffoldError(f"El destino no esta vacio: {target}.")


def resolve_target(
    project_name: str | None,
    here: bool,
    base: Path,
) -> tuple[Path, str]:
    if here:
        if project_name is not None:
            raise ScaffoldError("init --here no acepta nombre de proyecto.")
        return base, base.name
    if project_name is None:
        raise ScaffoldError("Falta el nombre del proyecto o la opcion --here.")
    if not valid_slug(project_name):
        raise ScaffoldError(
            f"Nombre de proyecto invalido: {project_name!r}. "
            "Usa solo letras, numeros, '.', '_' o '-'."
        )
    return base / project_name, project_name


def scaffold(
    target: Path,
    project_name: str,
    config: LogsayerConfig,
    adopt: bool = False,
) -> list[Path]:
    """Crea el árbol de capas y renderiza los documentos iniciales en `target`.

    En modo `adopt` (spec §5: `init --here` sobre un proyecto existente) no
    exige destino vacío y no sobrescribe archivos ya presentes: crea solo lo
    que falta. Devuelve los paths escritos (relativos a `target`).
    """
    if not adopt:
        validate_target(target)
    env = Environment(
        loader=PackageLoader("logsayer", "templates"),
        autoescape=select_autoescape(("html", "xml")),
    )
    target.mkdir(parents=True, exist_ok=True)
    for static in STATIC_DIRS:
        directory = target / "docs" / static
        directory.mkdir(parents=True, exist_ok=True)
        (directory / ".gitkeep").touch()

    context = {
        "project_name": project_name,
        "session_close_context_threshold": config.session_close_context_threshold,
        "context_threshold_percent": config.context_threshold_percent,
        "bitacora_max_lines": config.bitacora_max_lines,
        "audit_threshold_hus": config.audit_threshold_hus,
    }
    written: list[Path] = []
    for rel_path, template_name in RENDERED_FILES.items():
        file_path = target / rel_path
        if adopt and file_path.is_file():
            continue
        rendered = env.get_template(template_name).render(**context)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(rendered, encoding="utf-8")
        written.append(file_path.relative_to(target))
    return written