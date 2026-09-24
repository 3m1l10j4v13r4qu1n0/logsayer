"""Auditoría spec-vs-código (Capa 4 — Decidora de Verdad).

El CLI genera la estructura del reporte y el prompt; el resultado lo produce el
subagente que ejecuta la auditoría (spec §10: no prometer resultado determinístico).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from logsayer.core.project import project_name, read_closed_hus

AUDITS_DIR = Path("docs") / "06_audits"


class AuditError(Exception):
    """Error controlado de auditoría."""


def _render(template: str, **context: object) -> str:
    env = Environment(
        loader=PackageLoader("logsayer", "templates"),
        autoescape=select_autoescape(("html", "xml")),
    )
    return env.get_template(template).render(**context)


def _next_report_path(root: Path, date: str) -> Path:
    audits_dir = root / AUDITS_DIR
    audits_dir.mkdir(parents=True, exist_ok=True)
    counter = 0
    while True:
        suffix = "" if counter == 0 else f"-{counter}"
        candidate = audits_dir / f"audit_{date}{suffix}.md"
        if not candidate.exists():
            return candidate
        counter += 1


def last_audit(root: Path) -> Path | None:
    audits_dir = root / AUDITS_DIR
    if not audits_dir.is_dir():
        return None
    reports = [
        path
        for path in audits_dir.glob("audit_*.md")
        if not path.name.endswith(".prompt.md")
    ]
    if not reports:
        return None
    return max(reports)


def run_audit(root: Path) -> Path:
    """Genera el reporte y el prompt de auditoría para la Decidora."""
    date = datetime.now().strftime("%Y-%m-%d")
    report = _next_report_path(root, date)
    name = project_name(root)
    closed = read_closed_hus(root)
    report.write_text(
        _render(
            "audit_report.md.j2",
            date=date,
            project_name=name,
            closed_hus=closed,
        )
    )
    prompt = report.with_suffix(".prompt.md")
    prompt.write_text(
        _render(
            "audit_prompt.md.j2",
            date=date,
            project_name=name,
            closed_hus=closed,
            report_name=report.name,
        )
    )
    return report