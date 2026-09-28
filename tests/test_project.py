from pathlib import Path

from typer.testing import CliRunner

from logsayer.cli import app
from logsayer.core.project import (
    current_phase,
    declared_phase,
    read_closed_hus,
    set_closed_hus,
)

runner = CliRunner()


def _declare(root: Path, value: str) -> None:
    state = root / "docs" / "project_state.md"
    text = state.read_text(encoding="utf-8")
    state.write_text(text.replace("fase: _(slug de la fase)_", f"fase: {value}"))


def test_current_phase_reads_the_declared_field(cwd_project: Path) -> None:
    _declare(cwd_project, "fase2")
    assert declared_phase(cwd_project) == "fase2"
    assert current_phase(cwd_project) == "fase2"


def test_current_phase_does_not_read_the_prose(cwd_project: Path) -> None:
    """La sección del roadmap es contexto humano: no particiona la bitácora.

    Es el incidente del 2026-09-28: la primera línea de esa sección se slugificaba
    y "Fase 6 — ingreso de documentos, cerrada y mergeada…" terminó siendo el
    nombre de un logbook que hubo que borrar.
    """
    _declare(cwd_project, "fase6")
    state = cwd_project / "docs" / "project_state.md"
    text = state.read_text(encoding="utf-8")
    marker = "## Fase actual del roadmap"
    state.write_text(
        text.replace(marker, marker + "\n\nFase 8 — memoria seleccionable"),
        encoding="utf-8",
    )
    assert current_phase(cwd_project) == "fase6"


def test_current_phase_placeholder_is_undeclared(cwd_project: Path) -> None:
    assert declared_phase(cwd_project) is None
    assert current_phase(cwd_project) == "general"


def test_current_phase_rejects_a_sentence(cwd_project: Path) -> None:
    """Una frase no es un slug: se rechaza en vez de "limpiarse" a un nombre."""
    _declare(cwd_project, "Fase 8 — memoria seleccionable")
    assert declared_phase(cwd_project) is None
    assert current_phase(cwd_project) == "general"


def test_current_phase_lowercases_the_value(cwd_project: Path) -> None:
    _declare(cwd_project, "Fase8")
    assert current_phase(cwd_project) == "fase8"


def test_current_phase_without_state(tmp_path: Path) -> None:
    assert declared_phase(tmp_path) is None
    assert current_phase(tmp_path) == "general"


def test_log_add_warns_when_the_phase_is_undeclared(cwd_project: Path) -> None:
    result = runner.invoke(app, ["log", "add", "primera entrada"])
    assert result.exit_code == 0, result.output
    assert "logbook_general_01.md" in result.output
    assert "Sin fase declarada" in result.output


def test_log_add_silences_the_warning_with_a_declared_phase(cwd_project: Path) -> None:
    _declare(cwd_project, "fase2")
    result = runner.invoke(app, ["log", "add", "primera entrada"])
    assert result.exit_code == 0, result.output
    assert "logbook_fase2_01.md" in result.output
    assert "Sin fase declarada" not in result.output


def test_log_add_never_invents_a_phase_from_prose(cwd_project: Path) -> None:
    state = cwd_project / "docs" / "project_state.md"
    marker = "## Fase actual del roadmap"
    state.write_text(
        state.read_text(encoding="utf-8").replace(
            marker, marker + "\n\nFase 8 — memoria seleccionable"
        ),
        encoding="utf-8",
    )
    result = runner.invoke(app, ["log", "add", "primera entrada"])
    assert result.exit_code == 0, result.output
    assert (cwd_project / "docs" / "logbooks" / "logbook_general_01.md").is_file()
    assert not list(
        (cwd_project / "docs" / "logbooks").glob("logbook_fase-8*")
    )
    assert "Sin fase declarada" in result.output


def test_read_closed_hus_defaults_to_zero(cwd_project: Path) -> None:
    assert read_closed_hus(cwd_project) == 0


def test_set_closed_hus_updates_counter(cwd_project: Path) -> None:
    set_closed_hus(cwd_project, 3)
    assert read_closed_hus(cwd_project) == 3
    state = (cwd_project / "docs" / "project_state.md").read_text(encoding="utf-8")
    assert "3" in state.split("desde la última auditoría")[1][:5]