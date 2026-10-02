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
    assert result.exit_code == 1, result.output
    assert "usá logsayer audit reset" in result.output
    assert "reiniciado" not in result.output
    state = (cwd_project / "docs" / "project_state.md").read_text(encoding="utf-8")
    assert "3" in state.split("desde la última auditoría")[1][:5]


def test_audit_status_reports_due(cwd_project: Path) -> None:
    set_closed_hus(cwd_project, 3)
    result = runner.invoke(app, ["audit", "status"])
    assert result.exit_code == 0, result.output
    assert "corresponde auditar" in result.output


def test_audit_status_reports_not_due(cwd_project: Path) -> None:
    set_closed_hus(cwd_project, 1)
    result = runner.invoke(app, ["audit", "status"])
    assert result.exit_code == 0, result.output
    assert "Restan" in result.output
    assert "2" in result.output


def test_audit_status_shows_derived_without_moving_the_threshold(
    cwd_project: Path,
) -> None:
    """El derivado se muestra como dato; el umbral sigue decidiendo con lo
    declarado (D35). El desvase se avisa, no corrige el veredicto."""
    for hu in ("HU-01", "HU-02"):
        directory = cwd_project / "docs" / "04_user_stories" / hu
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "README.md").write_text(f"# {hu}\n", encoding="utf-8")
    audits = cwd_project / "docs" / "06_audits"
    audits.mkdir(parents=True, exist_ok=True)
    (audits / "audit_2026-09-27.md").write_text(
        "# Auditoría\n\n| HU | Veredicto | Evidencia |\n| --- | --- | --- |\n"
        "| HU-01 | cumple | ev |\n",
        encoding="utf-8",
    )
    set_closed_hus(cwd_project, 0)
    result = runner.invoke(app, ["audit", "status"])
    assert result.exit_code == 0, result.output
    assert "Derivadas del disco: 1 HU(s) sin veredicto" in result.output
    assert "HU-02" in result.output
    assert "queda por debajo del derivado" in result.output
    assert "Restan" in result.output


def test_audit_via_role_group(cwd_project: Path) -> None:
    result = runner.invoke(app, ["truthsayer", "audit", "status"])
    assert result.exit_code == 0, result.output


def test_audit_reset_rejects_with_pending_verdicts(cwd_project: Path) -> None:
    audits = cwd_project / "docs" / "06_audits"
    audits.mkdir(parents=True, exist_ok=True)
    hus_dir = cwd_project / "docs" / "04_user_stories"
    (hus_dir / "HU-14").mkdir(parents=True, exist_ok=True)
    (hus_dir / "HU-14" / "README.md").write_text("# HU-14\n", encoding="utf-8")
    (hus_dir / "HU-15").mkdir(parents=True, exist_ok=True)
    (hus_dir / "HU-15" / "README.md").write_text("# HU-15\n", encoding="utf-8")
    table = (
        "# Auditoría\n\n## Alcance de la auditoría por pasada\n\n"
        "| HU | Veredicto | Evidencia | Observaciones |\n"
        "|---|---|---|---|\n"
        "| HU-14 |  |  |  |\n"
        "| HU-15 |  |  |  |\n"
    )
    (audits / "audit_2026-09-29.md").write_text(table, encoding="utf-8")
    set_closed_hus(cwd_project, 2)
    before = list(audits.glob("*"))
    result = runner.invoke(app, ["audit", "reset"])
    assert result.exit_code != 0, result.output
    out = result.output
    assert "HU-14" in out or "HU-15" in out or "pendiente" in out
    assert list(audits.glob("*")) == before


def test_audit_reset_clears_counter_when_complete(
    cwd_project: Path,
    tmp_path: Path,
) -> None:
    audits = cwd_project / "docs" / "06_audits"
    audits.mkdir(parents=True, exist_ok=True)
    content = (
        "# Auditoría\n\n## Alcance de la auditoría por pasada\n\n"
        "| HU | Veredicto | Evidencia | Observaciones |\n|---|---|---|---|\n"
        "| HU-01 | cumple | ev | o |\n"
        "| HU-02 | cumple | ev | o |\n"
    )
    (audits / "audit_2026-09-27.md").write_text(content, encoding="utf-8")
    set_closed_hus(cwd_project, 3)
    before = set(audits.glob("*"))
    result = runner.invoke(app, ["audit", "reset"])
    assert result.exit_code == 0, result.output
    assert "reiniciado" in result.output
    after = set(audits.glob("*"))
    assert after == before
    state = (cwd_project / "docs" / "project_state.md").read_text(encoding="utf-8")
    assert "0" in state.split("desde la última auditoría")[1][:5]


def test_help_lists_flat_aliases() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for alias in ("spec", "state", "log", "audit"):
        assert alias in result.output