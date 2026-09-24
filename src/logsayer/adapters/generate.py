"""Generación de archivos de adaptador en la raíz del proyecto usuaria."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from logsayer.adapters.base import AdapterSpec
from logsayer.config import LogsayerConfig
from logsayer.core.paths import require_logsayer_root


def generate_adapters(base: Path, spec: AdapterSpec) -> tuple[Path, list[Path]]:
    """Escribe los subagentes del adaptador en la raíz logsayer de `base`.

    Devuelve (raíz del proyecto, paths generados). Requiere raíz logsayer:
    la estructura generada vive dentro de un proyecto ya scaffolded.
    """
    root = require_logsayer_root(base)
    config = LogsayerConfig.load(root / "logsayer.toml")
    env = Environment(
        loader=PackageLoader("logsayer", "templates"),
        autoescape=select_autoescape(("html", "xml")),
    )
    context = {
        "project_name": root.name,
        "audit_threshold_hus": config.audit_threshold_hus,
        "bitacora_max_lines": config.bitacora_max_lines,
        "context_threshold_percent": config.context_threshold_percent,
    }
    written: list[Path] = []
    for adapter_file in spec.files:
        rendered = env.get_template(adapter_file.template_name).render(**context)
        target = root / adapter_file.rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        written.append(target)
    return root, written