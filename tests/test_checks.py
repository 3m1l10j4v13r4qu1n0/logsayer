from pathlib import Path

from typer.testing import CliRunner

from logsayer.cli import app

runner = CliRunner()


def test_suk_doctor_healthy(cwd_project: Path) -> None:
    result = runner.invoke(app, ["suk", "doctor"])
    assert result.exit_code == 0, result.output
    assert "Estado: sano." in result.output


def test_check_flat_alias_healthy(cwd_project: Path) -> None:
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "Suk Doctor" in result.output


def test_suk_mixed_layers_audit_outside(cwd_project: Path) -> None:
    audit = cwd_project / "docs" / "audit_2026-09-24.md"
    audit.write_text("# Audit\n", encoding="utf-8")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "capas_mezcladas" in result.output


def test_suk_mixed_layers_logbook_outside(cwd_project: Path) -> None:
    logbook = cwd_project / "docs" / "logbook_general_01.md"
    logbook.write_text("# Logbook\n", encoding="utf-8")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "bitácora fuera de" in result.output


def test_suk_hu_misplaced(cwd_project: Path) -> None:
    (cwd_project / "docs" / "HU-99").mkdir()
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "hus_ubicacion" in result.output


def test_suk_state_missing_section(cwd_project: Path) -> None:
    state = cwd_project / "docs" / "project_state.md"
    content = "# Estado del proyecto — x\n\n## Fase actual del roadmap\n\nfase\n"
    state.write_text(content, encoding="utf-8")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "estado_capa2" in result.output


def test_suk_logbook_index_inconsistent(cwd_project: Path) -> None:
    logs = cwd_project / "docs" / "logbooks"
    (logs / "logbook_x_99.md").write_text("# Logbook\n", encoding="utf-8")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "bitacora_indice" in result.output


def test_suk_requires_project_root(plain_cwd: Path) -> None:
    result = runner.invoke(app, ["check"])
    assert result.exit_code != 0


def test_fremen_verify_healthy(cwd_project: Path) -> None:
    result = runner.invoke(app, ["fremen", "verify"])
    assert result.exit_code == 0, result.output
    assert "Estado: sano." in result.output


def test_process_check_flat_alias_healthy(cwd_project: Path) -> None:
    result = runner.invoke(app, ["process", "check"])
    assert result.exit_code == 0, result.output
    assert "Fremen" in result.output


def test_fremen_missing_process_dir(cwd_project: Path) -> None:
    path = cwd_project / "docs" / "03_process"
    for child in path.iterdir():
        child.unlink()
    path.rmdir()
    result = runner.invoke(app, ["process", "check"])
    assert result.exit_code == 1
    assert "proceso_desplegado" in result.output


def test_fremen_agreement_diverges(cwd_project: Path) -> None:
    agents = cwd_project / "AGENTS.md"
    reescrito = agents.read_text(encoding="utf-8").replace("70%", "80%")
    agents.write_text(reescrito, encoding="utf-8")
    result = runner.invoke(app, ["process", "check"])
    assert result.exit_code == 1
    assert "acuerdo_coordinacion" in result.output


def test_fremen_definition_of_ready(cwd_project: Path) -> None:
    (cwd_project / "docs" / "04_user_stories" / "HU-99").mkdir()
    result = runner.invoke(app, ["process", "check"])
    assert result.exit_code == 1
    assert "definition_of_ready" in result.output


def test_fremen_requires_project_root(plain_cwd: Path) -> None:
    result = runner.invoke(app, ["process", "check"])
    assert result.exit_code != 0


def test_help_lists_check_and_process(cwd_project: Path) -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "check" in result.output
    assert "process" in result.output