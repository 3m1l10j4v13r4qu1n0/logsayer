from __future__ import annotations

import os
import time
from pathlib import Path

from typer.testing import CliRunner

from logsayer.cli import app

runner = CliRunner()


def _drop(root: Path, name: str) -> Path:
    """Archivo externo al proyecto, con el nombre exacto que va a tener."""
    outside = root.parent / "fuera-del-proyecto"
    outside.mkdir(exist_ok=True)
    source = outside / name
    source.write_text("# Documento externo\n", encoding="utf-8")
    return source


def test_init_creates_inbox_with_gitignore(plain_cwd: Path) -> None:
    result = runner.invoke(app, ["init", "proyecto"])
    assert result.exit_code == 0, result.output
    ignore = plain_cwd / "proyecto" / "inbox" / ".gitignore"
    assert ignore.is_file()
    assert ignore.read_text(encoding="utf-8") == "*\n!.gitignore\n"
    assert "inbox/.gitignore" in result.output


def test_init_here_adopt_creates_inbox(plain_cwd: Path) -> None:
    (plain_cwd / "AGENTS.md").write_text("# propio\n", encoding="utf-8")
    result = runner.invoke(app, ["init", "--here"])
    assert result.exit_code == 0, result.output
    assert (plain_cwd / "inbox" / ".gitignore").is_file()
    assert (plain_cwd / "AGENTS.md").read_text(encoding="utf-8") == "# propio\n"


def test_check_reports_empty_inbox_as_ok(cwd_project: Path) -> None:
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "bandeja_entrada: vacía" in result.output


def test_check_missing_inbox_is_not_a_failure(plain_cwd: Path) -> None:
    """Un proyecto previo a la fase 6 no tiene bandeja: eso no es un fallo."""
    (plain_cwd / "logsayer.toml").write_text("[logsayer]\n", encoding="utf-8")
    (plain_cwd / "AGENTS.md").write_text("# propio\n", encoding="utf-8")
    for layer in (
        "01_global",
        "02_technical",
        "03_process",
        "04_user_stories",
        "05_agile_methodology",
        "06_audits",
        "logbooks",
    ):
        (plain_cwd / "docs" / layer).mkdir(parents=True, exist_ok=True)
    (plain_cwd / "docs" / "project_state.md").write_text(
        "# Estado del proyecto — x\n\n## Fase actual del roadmap\n\nalgo\n\n"
        "## Decisiones activas\n\n- D1\n\n"
        "## HUs cerradas desde la última auditoría\n\n0\n",
        encoding="utf-8",
    )
    (plain_cwd / "docs" / "logbooks" / "00_index.md").write_text(
        "| logbook | |\n|---|---|\n", encoding="utf-8"
    )
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "bandeja_entrada: sin bandeja (opcional)" in result.output


def test_inbox_add_moves_file_in(cwd_project: Path) -> None:
    source = _drop(cwd_project, "contrato.md")
    result = runner.invoke(app, ["inbox", "add", str(source)])
    assert result.exit_code == 0, result.output
    assert (cwd_project / "inbox" / "contrato.md").is_file()
    assert not source.exists()
    assert "logsayer doc route" in result.output


def test_inbox_add_warns_on_non_markdown(cwd_project: Path) -> None:
    source = cwd_project.parent / "contrato.pdf"
    source.write_bytes(b"%PDF-1.4\n")
    result = runner.invoke(app, ["inbox", "add", str(source)])
    assert result.exit_code == 0, result.output
    assert "no es markdown" in result.output
    assert "no convierte PDF" in result.output


def test_inbox_add_rejects_file_already_staged(cwd_project: Path) -> None:
    source = _drop(cwd_project, "contrato.md")
    assert runner.invoke(app, ["inbox", "add", str(source)]).exit_code == 0
    result = runner.invoke(app, ["inbox", "add", "inbox/contrato.md"])
    assert result.exit_code != 0
    assert "ya está en la bandeja" in result.output


def test_inbox_add_missing_file(cwd_project: Path) -> None:
    result = runner.invoke(app, ["inbox", "add", "no-existe.md"])
    assert result.exit_code != 0
    assert "No existe el archivo" in result.output


def test_inbox_add_does_not_overwrite(cwd_project: Path) -> None:
    first = _drop(cwd_project, "contrato.md")
    assert runner.invoke(app, ["inbox", "add", str(first)]).exit_code == 0
    second = _drop(cwd_project, "contrato.md")
    assert runner.invoke(app, ["inbox", "add", str(second)]).exit_code == 0
    assert (cwd_project / "inbox" / "contrato.md").is_file()
    assert (cwd_project / "inbox" / "contrato-2.md").is_file()


def test_check_warns_on_pending_without_failing(cwd_project: Path) -> None:
    source = _drop(cwd_project, "contrato.md")
    assert runner.invoke(app, ["inbox", "add", str(source)]).exit_code == 0
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "! bandeja_entrada: 1 sin ubicar" in result.output
    assert "logsayer doc route <archivo>" in result.output
    assert "Estado: sano" in result.output


def test_check_reports_stale_inbox_items(cwd_project: Path) -> None:
    source = _drop(cwd_project, "viejo.md")
    assert runner.invoke(app, ["inbox", "add", str(source)]).exit_code == 0
    stale = cwd_project / "inbox" / "viejo.md"
    old = time.time() - 60 * 60 * 24 * 30
    os.utime(stale, (old, old))
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "envejecidos" in result.output
    assert "viejo.md (30 días)" in result.output


def test_check_ignores_done_items(cwd_project: Path) -> None:
    source = _drop(cwd_project, "contrato.md")
    assert runner.invoke(app, ["inbox", "add", str(source)]).exit_code == 0
    assert runner.invoke(
        app, ["doc", "new", "technical", "contrato_api", "--from", "inbox/contrato.md"]
    ).exit_code == 0
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "bandeja_entrada: vacía" in result.output


def test_inbox_without_subcommand_lists_pending(cwd_project: Path) -> None:
    source = _drop(cwd_project, "nota.md")
    assert runner.invoke(app, ["inbox", "add", str(source)]).exit_code == 0
    result = runner.invoke(app, ["inbox"])
    assert result.exit_code == 0, result.output
    assert "nota.md" in result.output
    assert "doc route" in result.output


def test_inbox_empty_says_so(cwd_project: Path) -> None:
    result = runner.invoke(app, ["inbox"])
    assert result.exit_code == 0, result.output
    assert "Bandeja vac" in result.output


def test_inbox_listing_excludes_done(cwd_project: Path) -> None:
    source = _drop(cwd_project, "nota.md")
    assert runner.invoke(app, ["inbox", "add", str(source)]).exit_code == 0
    assert runner.invoke(
        app, ["doc", "new", "global", "vision", "--from", "inbox/nota.md"]
    ).exit_code == 0
    result = runner.invoke(app, ["inbox"])
    assert result.exit_code == 0, result.output
    assert "Bandeja vac" in result.output
