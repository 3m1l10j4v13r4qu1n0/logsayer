from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from typer.testing import CliRunner

from logsayer.cli import app

runner = CliRunner()

HEADER = (
    "# Contrato api\n\n"
    "Fecha: 2026-09-25 · Estado: borrador\n\n"
    "## Resumen\n\n_Una línea._\n"
)


def test_layer1_doc_without_header_fails(cwd_project: Path) -> None:
    (cwd_project / "docs" / "02_technical" / "contrato.md").write_text(
        "# Contrato\n\ntexto\n", encoding="utf-8"
    )
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "header_capa1" in result.output
    assert "Fecha:" in result.output
    assert "## Resumen" in result.output


def test_layer1_doc_with_header_passes(cwd_project: Path) -> None:
    (cwd_project / "docs" / "02_technical" / "contrato.md").write_text(
        HEADER, encoding="utf-8"
    )
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "✔ header_capa1" in result.output


def test_hu_templates_are_not_judged_by_header_check(cwd_project: Path) -> None:
    """Las HUs tienen su propio template: el check no las judgea."""
    assert runner.invoke(app, ["spec", "new", "HU-01"]).exit_code == 0
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "✔ header_capa1" in result.output


def test_mixed_layers_suggests_destination(cwd_project: Path) -> None:
    (cwd_project / "docs" / "contrato.md").write_text("# x\n", encoding="utf-8")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "sugerido" in result.output
    assert "logsayer doc route" in result.output


def test_mixed_layers_suggests_layer_for_known_prefixes(cwd_project: Path) -> None:
    docs = cwd_project / "docs"
    (docs / "logbook_clandestino.md").write_text("# x\n", encoding="utf-8")
    (docs / "audit_2026-01-01.md").write_text("# x\n", encoding="utf-8")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "logbooks/" in result.output
    assert "06_audits/" in result.output


def test_state_freshness_warns_when_layer1_is_newer(cwd_project: Path) -> None:
    doc = cwd_project / "docs" / "02_technical" / "contrato.md"
    doc.write_text(HEADER, encoding="utf-8")
    state = cwd_project / "docs" / "project_state.md"
    old = time.time() - 60 * 60 * 24 * 5
    os.utime(state, (old, old))
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "! estado_al_dia" in result.output
    assert "02_technical/contrato.md" in result.output
    assert "project_state.md" in result.output


def test_state_freshness_ok_when_state_is_newer(cwd_project: Path) -> None:
    (cwd_project / "docs" / "02_technical" / "contrato.md").write_text(
        HEADER, encoding="utf-8"
    )
    doc = cwd_project / "docs" / "02_technical" / "contrato.md"
    old = time.time() - 60 * 60 * 24 * 5
    os.utime(doc, (old, old))
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "✔ estado_al_dia" in result.output


def test_state_freshness_without_state_is_not_a_failure(cwd_project: Path) -> None:
    (cwd_project / "docs" / "project_state.md").unlink()
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "estado_capa2" in result.output


def _git(root: Path, *args: str) -> None:
    subprocess.run(("git", *args), cwd=root, check=True, capture_output=True)


def test_freshness_compares_commit_and_mtime_on_one_scale(cwd_project: Path) -> None:
    """Regresión: estado commiteado y editado en disco vs HU sin versionar.

    Con solo el timestamp del commit, el estado parecía viejo frente al mtime
    de la HU nueva y el check avisaba sin razón.
    """
    _git(cwd_project, "init", "-q")
    _git(cwd_project, "config", "user.email", "t@t.t")
    _git(cwd_project, "config", "user.name", "t")
    _git(cwd_project, "add", "-A")
    _git(cwd_project, "commit", "-q", "-m", "estado inicial")

    # HU nueva sin commitear (solo mtime) y estado commiteado pero editado.
    (cwd_project / "docs" / "04_user_stories" / "HU-01").mkdir(parents=True)
    (cwd_project / "docs" / "04_user_stories" / "HU-01" / "README.md").write_text(
        "# HU-01\n", encoding="utf-8"
    )
    state = cwd_project / "docs" / "project_state.md"
    state.write_text(
        state.read_text(encoding="utf-8") + "\n- arrancando la HU-01\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "✔ estado_al_dia" in result.output, result.output
