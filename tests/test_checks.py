from pathlib import Path

from typer.testing import CliRunner

from logsayer import __version__
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


def _index(root: Path) -> Path:
    assert runner.invoke(app, ["memory", "index"]).exit_code == 0
    return root / "docs" / "00_memory_index.md"


def test_fremen_index_absent_is_optional(cwd_project: Path) -> None:
    """Un proyecto scaffoldeado antes de la fase 8 no tiene índice: no es un fallo."""
    result = runner.invoke(app, ["fremen", "verify"])
    assert result.exit_code == 0, result.output
    assert "✔ indice_al_dia" in result.output
    assert "sin índice" in result.output


def test_fremen_index_fresh_after_regenerating(cwd_project: Path) -> None:
    _index(cwd_project)
    result = runner.invoke(app, ["fremen", "verify"])
    assert "✔ indice_al_dia" in result.output


def test_fremen_index_stale_names_the_newest_document(cwd_project: Path) -> None:
    _index(cwd_project)
    nuevo = cwd_project / "docs" / "02_technical" / "contrato.md"
    nuevo.write_text("# Contrato\n", encoding="utf-8")

    result = runner.invoke(app, ["fremen", "verify"])
    assert result.exit_code == 0, result.output
    assert "! indice_al_dia" in result.output
    assert "docs/02_technical/contrato.md" in result.output
    assert "logsayer memory index" in result.output


def test_fremen_index_ignores_the_logbook_and_the_state(cwd_project: Path) -> None:
    """El aviso que aparece en todo cierre de sesión no avisa de nada (D7).

    `log add` anexa al logbook y el cierre reescribe `project_state.md`: si el
    check los mirara, reindexar sería un paso obligatorio de cada sesión.
    """
    _index(cwd_project)
    runner.invoke(app, ["log", "add", "entrada de bitácora", "--fase", "fase2"])
    state = cwd_project / "docs" / "project_state.md"
    state.write_text(
        state.read_text(encoding="utf-8") + "\nUna línea más.\n", encoding="utf-8"
    )

    result = runner.invoke(app, ["fremen", "verify"])
    assert "✔ indice_al_dia" in result.output, result.output


def test_help_lists_check_and_process(cwd_project: Path) -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "check" in result.output
    assert "process" in result.output


def _declare(root: Path, toml: str) -> None:
    (root / "logsayer.toml").write_text(toml, encoding="utf-8")


def test_preset_known_is_ok_when_declared_and_shipped(cwd_project: Path) -> None:
    _declare(cwd_project, '[project]\npreset = "minimal"\n')
    result = runner.invoke(app, ["check"])
    assert "✔ preset_conocido" in result.output, result.output


def test_preset_known_warns_when_the_snapshot_points_to_a_missing_preset(
    cwd_project: Path,
) -> None:
    # El fallo real de un snapshot: el preset dejó de distribuirse y el TOML
    # sigue apuntando a él.
    _declare(cwd_project, '[project]\npreset = "estricto"\n')
    result = runner.invoke(app, ["check"])
    assert "! preset_conocido" in result.output, result.output
    assert "estricto" in result.output
    assert __version__ in result.output


def test_preset_known_is_ok_without_a_declared_preset(cwd_project: Path) -> None:
    # Un proyecto scaffoldeado antes de la fase 7 no declara nada, y eso no es
    # un pendiente: el aviso tiene que ser para el snapshot roto, no por todos.
    result = runner.invoke(app, ["check"])
    assert "✔ preset_conocido" in result.output, result.output


def test_declared_adapters_warns_before_agent_add_runs(cwd_project: Path) -> None:
    _declare(cwd_project, '[adapters]\nenabled = ["claude"]\n')
    result = runner.invoke(app, ["check"])
    assert "! adaptadores_declarados" in result.output, result.output
    assert "agent add claude" in result.output


def test_declared_adapters_is_ok_after_agent_add(cwd_project: Path) -> None:
    _declare(cwd_project, '[adapters]\nenabled = ["claude"]\n')
    runner.invoke(app, ["agent", "add", "claude"])
    result = runner.invoke(app, ["check"])
    assert "✔ adaptadores_declarados" in result.output, result.output


def test_declared_adapters_warns_on_a_name_without_adapter(cwd_project: Path) -> None:
    _declare(cwd_project, '[adapters]\nenabled = ["hermes"]\n')
    result = runner.invoke(app, ["check"])
    assert "! adaptadores_declarados" in result.output, result.output
    assert "hermes" in result.output


def test_declared_adapters_stays_quiet_with_a_partial_set(cwd_project: Path) -> None:
    # Se mide contra el conjunto entero y no archivo por archivo (D41): quien
    # escribió uno a mano ya ejecutó la parte, y un archivo borrado a conciencia
    # no es un pendiente.
    _declare(cwd_project, '[adapters]\nenabled = ["claude"]\n')
    runner.invoke(app, ["agent", "add", "claude"])
    (cwd_project / ".claude" / "agents" / "truthsayer.md").unlink()
    result = runner.invoke(app, ["check"])
    assert "✔ adaptadores_declarados" in result.output, result.output


def test_declared_adapters_is_ok_without_declarations(cwd_project: Path) -> None:
    result = runner.invoke(app, ["check"])
    assert "✔ adaptadores_declarados" in result.output, result.output


def test_declared_adapters_warns_on_a_malformed_list(cwd_project: Path) -> None:
    _declare(cwd_project, '[adapters]\nenabled = "claude"\n')
    result = runner.invoke(app, ["check"])
    assert "! adaptadores_declarados" in result.output, result.output


def test_both_checks_stay_ok_on_a_fresh_project(cwd_project: Path) -> None:
    # La batería entera depende de esto: los dos checks nuevos no pueden avisar
    # en un proyecto scaffoldeado que no pidió preset.
    result = runner.invoke(app, ["check"])
    assert "Estado: sano." in result.output, result.output