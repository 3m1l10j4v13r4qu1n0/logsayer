"""Bitácora append-only (Capa 3 — Reverenda Madre) con partición automática."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from logsayer.config import LogsayerConfig
from logsayer.core.project import current_phase

LOGBOOK_DIR = "docs/logbooks"
INDEX_FILE = "00_index.md"

LOGBOOK_RE = re.compile(r"^logbook_(?P<phase>.+?)_(?P<seq>\d+)\.md$")


class LogbookError(Exception):
    """Error controlado de bitácora."""


def _logs_dir(root: Path) -> Path:
    return root / LOGBOOK_DIR


def _logbooks(root: Path) -> list[tuple[str, int, Path]]:
    """Devuelve [(fase, seq, path)] ordenado por (fase, seq)."""
    logs_dir = _logs_dir(root)
    if not logs_dir.is_dir():
        return []
    found: list[tuple[str, int, Path]] = []
    for path in logs_dir.glob("logbook_*.md"):
        match = LOGBOOK_RE.match(path.name)
        if match:
            found.append((match.group("phase"), int(match.group("seq")), path))
    return sorted(found, key=lambda item: (item[0], item[1]))


def _header(phase: str, seq: int) -> str:
    return f"# Logbook — {phase} ({seq:02d})\n\n"


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def _append_line(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        line = "\n" + line
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def _first_entry_text(path: Path) -> str:
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped.startswith("- "):
            return stripped[2:].strip()
    return "—"


def add_entry(
    root: Path,
    text: str,
    config: LogsayerConfig,
    phase_override: str | None = None,
) -> dict[str, object]:
    """Append de una entrada; particiona al archivo siguiente si el activo
    supera el límite."""
    phase = phase_override or current_phase(root)
    logs_dir = _logs_dir(root)
    logs_dir.mkdir(parents=True, exist_ok=True)

    phase_books = [item for item in _logbooks(root) if item[0] == phase]
    if phase_books:
        seq, active = phase_books[-1][1], phase_books[-1][2]
    else:
        seq, active = 1, logs_dir / f"logbook_{phase}_01.md"

    if active.is_file() and _line_count(active) >= config.bitacora_max_lines:
        seq += 1
        active = logs_dir / f"logbook_{phase}_{seq:02d}.md"
        active.write_text(_header(phase, seq), encoding="utf-8")
    elif not active.is_file():
        active.write_text(_header(phase, seq), encoding="utf-8")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    _append_line(active, f"- {timestamp} — {text}")
    write_index(root)
    return {"phase": phase, "seq": seq, "path": active}


def _index_header() -> str:
    env = Environment(
        loader=PackageLoader("logsayer", "templates"),
        autoescape=select_autoescape(("html", "xml")),
    )
    return env.get_template("00_index.md.j2").render()


def write_index(root: Path) -> Path:
    """Reconstruye 00_index.md desde los logbooks reales (mecánico, determinístico)."""
    logs_dir = _logs_dir(root)
    logs_dir.mkdir(parents=True, exist_ok=True)
    header = _index_header().rstrip("\n")
    rows = [
        f"| {path.name} | {phase} | {seq} | {_first_entry_text(path)} |"
        for phase, seq, path in _logbooks(root)
    ]
    content = header + ("\n" + "\n".join(rows) if rows else "") + "\n"
    index = logs_dir / INDEX_FILE
    index.write_text(content, encoding="utf-8")
    return index