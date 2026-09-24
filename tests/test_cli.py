from pathlib import Path

import pytest
from typer.testing import CliRunner

from logsayer.cli import app

runner = CliRunner()


@pytest.fixture
def cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_init_here_scaffolds_cwd(cwd: Path) -> None:
    result = runner.invoke(app, ["init", "--here"])
    assert result.exit_code == 0, result.output
    assert (cwd / "AGENTS.md").is_file()
    assert (cwd / "logsayer.toml").is_file()
    assert (cwd / "docs" / "project_state.md").is_file()
    assert (cwd / "docs" / "logbooks" / "00_index.md").is_file()


def test_init_with_name(cwd: Path) -> None:
    result = runner.invoke(app, ["init", "mi-proyecto"])
    assert result.exit_code == 0, result.output
    assert (cwd / "mi-proyecto" / "AGENTS.md").is_file()


def test_init_requires_name_or_here() -> None:
    result = runner.invoke(app, ["init"])
    assert result.exit_code != 0


def test_init_here_rejects_name(cwd: Path) -> None:
    result = runner.invoke(app, ["init", "mi-proyecto", "--here"])
    assert result.exit_code != 0


def test_init_here_adopts_non_empty_cwd(cwd: Path) -> None:
    (cwd / "algo.txt").write_text("x", encoding="utf-8")
    (cwd / "AGENTS.md").write_text("contenido propio", encoding="utf-8")
    result = runner.invoke(app, ["init", "--here"])
    assert result.exit_code == 0, result.output
    assert (cwd / "docs" / "project_state.md").is_file()
    assert (cwd / "logsayer.toml").is_file()
    assert (cwd / "AGENTS.md").read_text(encoding="utf-8") == "contenido propio"
    assert "preservados" in result.output


def test_init_rejects_non_empty_target(cwd: Path) -> None:
    occupied = cwd / "ocupado"
    occupied.mkdir()
    (occupied / "algo.txt").write_text("x", encoding="utf-8")
    result = runner.invoke(app, ["init", "ocupado"])
    assert result.exit_code != 0


def test_help_lists_role_groups() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    roles = ("mentat", "navigator", "reverend-mother", "truthsayer", "suk", "fremen")
    for role in roles:
        assert role in result.output