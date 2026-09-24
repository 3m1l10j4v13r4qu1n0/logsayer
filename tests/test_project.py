from pathlib import Path

from logsayer.core.project import current_phase, read_closed_hus, set_closed_hus


def test_current_phase_from_state(cwd_project: Path) -> None:
    state = cwd_project / "docs" / "project_state.md"
    phase_body = "## Fase actual del roadmap\n\nFase 2 — Comandos core\n"
    state.write_text(phase_body, encoding="utf-8")
    assert current_phase(cwd_project) == "fase-2-comandos-core"


def test_current_phase_placeholder_is_general(cwd_project: Path) -> None:
    assert current_phase(cwd_project) == "general"


def test_current_phase_without_state(tmp_path: Path) -> None:
    assert current_phase(tmp_path) == "general"


def test_read_closed_hus_defaults_to_zero(cwd_project: Path) -> None:
    assert read_closed_hus(cwd_project) == 0


def test_set_closed_hus_updates_counter(cwd_project: Path) -> None:
    set_closed_hus(cwd_project, 3)
    assert read_closed_hus(cwd_project) == 3
    state = (cwd_project / "docs" / "project_state.md").read_text(encoding="utf-8")
    assert "3" in state.split("desde la última auditoría")[1][:5]