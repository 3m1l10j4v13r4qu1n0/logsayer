from pathlib import Path

from typer.testing import CliRunner

from logsayer.cli import app
from logsayer.core.project import set_closed_hus

runner = CliRunner()


def test_spec_new_flat_alias(cwd_project: Path) -> None:
    result = runner.invoke(app, ["spec", "new", "HU-01"])
    assert result.exit_code == 0, result.output
    assert (cwd_project / "docs" / "04_user_stories" / "HU-01" / "README.md").is_file()


def test_spec_new_via_role_group(cwd_project: Path) -> None:
    result = runner.invoke(app, ["mentat", "spec", "new", "HU-02"])
    assert result.exit_code == 0, result.output
    assert (cwd_project / "docs" / "04_user_stories" / "HU-02" / "README.md").is_file()


def test_spec_new_rejects_invalid(cwd_project: Path) -> None:
    result = runner.invoke(app, ["spec", "new", "nope"])
    assert result.exit_code != 0


def test_spec_new_requires_project_root(plain_cwd: Path) -> None:
    result = runner.invoke(app, ["spec", "new", "HU-01"])
    assert result.exit_code != 0


def test_state_show_prints_snapshot(cwd_project: Path) -> None:
    result = runner.invoke(app, ["state", "show"])
    assert result.exit_code == 0, result.output
    assert "Estado del proyecto" in result.output


def test_state_show_via_role_group(cwd_project: Path) -> None:
    result = runner.invoke(app, ["navigator", "state", "show"])
    assert result.exit_code == 0, result.output


def test_state_show_requires_project_root(plain_cwd: Path) -> None:
    result = runner.invoke(app, ["state", "show"])
    assert result.exit_code != 0


def test_log_add_flat_alias(cwd_project: Path) -> None:
    result = runner.invoke(app, ["log", "add", "Primera entrada"])
    assert result.exit_code == 0, result.output
    logbook = cwd_project / "docs" / "logbooks" / "logbook_general_01.md"
    assert logbook.is_file()
    assert "Primera entrada" in logbook.read_text(encoding="utf-8")


def test_log_add_via_role_group(cwd_project: Path) -> None:
    result = runner.invoke(app, ["reverend-mother", "log", "add", "Otra entrada"])
    assert result.exit_code == 0, result.output


def test_log_add_with_phase_flag(cwd_project: Path) -> None:
    result = runner.invoke(app, ["log", "add", "--fase", "fase-2", "Entrada p2"])
    assert result.exit_code == 0, result.output
    assert (cwd_project / "docs" / "logbooks" / "logbook_fase-2_01.md").is_file()


def test_log_index_rebuilds(cwd_project: Path) -> None:
    runner.invoke(app, ["log", "add", "A"])
    runner.invoke(app, ["log", "add", "B"])
    index = cwd_project / "docs" / "logbooks" / "00_index.md"
    index.write_text("# Bitácoras — índice\n", encoding="utf-8")
    result = runner.invoke(app, ["log", "index"])
    assert result.exit_code == 0, result.output
    content = index.read_text(encoding="utf-8")
    assert "logbook_general_01.md" in content


def test_log_requires_project_root(plain_cwd: Path) -> None:
    result = runner.invoke(app, ["log", "add", "fuera de proyecto"])
    assert result.exit_code != 0


def test_audit_run_generates_report_and_prompt(cwd_project: Path) -> None:
    result = runner.invoke(app, ["audit", "run"])
    assert result.exit_code == 0, result.output
    reports = list((cwd_project / "docs" / "06_audits").glob("audit_*.md"))
    assert reports
    assert any(not path.name.endswith(".prompt.md") for path in reports)
    assert any(path.name.endswith(".prompt.md") for path in reports)


def test_audit_run_keeps_counter_without_flag(cwd_project: Path) -> None:
    set_closed_hus(cwd_project, 2)
    runner.invoke(app, ["audit", "run"])
    state = (cwd_project / "docs" / "project_state.md").read_text(encoding="utf-8")
    assert "2" in state.split("desde la última auditoría")[1][:5]


def test_audit_run_reset_counter_flag(cwd_project: Path) -> None:
    set_closed_hus(cwd_project, 3)
    result = runner.invoke(app, ["audit", "run", "--reset-counter"])
    assert result.exit_code == 0, result.output
    assert "reiniciado" in result.output
    state = (cwd_project / "docs" / "project_state.md").read_text(encoding="utf-8")
    assert "0" in state.split("desde la última auditoría")[1][:5]


def test_audit_status_reports_due(cwd_project: Path) -> None:
    set_closed_hus(cwd_project, 3)
    result = runner.invoke(app, ["audit", "status"])
    assert result.exit_code == 0, result.output
    assert "corresponde auditar" in result.output


def test_audit_status_reports_not_due(cwd_project: Path) -> None:
    set_closed_hus(cwd_project, 1)
    result = runner.invoke(app, ["audit", "status"])
    assert result.exit_code == 0, result.output
    assert "no corresponde auditar" in result.output
    assert "2" in result.output


def test_audit_via_role_group(cwd_project: Path) -> None:
    result = runner.invoke(app, ["truthsayer", "audit", "status"])
    assert result.exit_code == 0, result.output


def test_help_lists_flat_aliases() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for alias in ("spec", "state", "log", "audit"):
        assert alias in result.output