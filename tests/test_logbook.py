from pathlib import Path

from logsayer.config import LogsayerConfig
from logsayer.core.logbook import add_entry, write_index
from logsayer.core.project import set_closed_hus


def test_add_entry_creates_first_logbook_and_index(cwd_project: Path) -> None:
    add_entry(cwd_project, "Primera decisión", LogsayerConfig())
    logs = cwd_project / "docs" / "logbooks"
    assert (logs / "logbook_general_01.md").is_file()
    index = (logs / "00_index.md").read_text(encoding="utf-8")
    assert "logbook_general_01.md" in index
    assert "Primera decisión" in index


def test_add_entry_appends_timestamped_line(cwd_project: Path) -> None:
    add_entry(cwd_project, "Decisión A", LogsayerConfig())
    add_entry(cwd_project, "Decisión B", LogsayerConfig())
    content = (cwd_project / "docs" / "logbooks" / "logbook_general_01.md").read_text(
        encoding="utf-8"
    )
    assert content.startswith("# Logbook — general (01)")
    assert "Decisión A" in content
    assert "Decisión B" in content


def test_add_entry_with_phase_override(cwd_project: Path) -> None:
    add_entry(cwd_project, "Entrada fase 2", LogsayerConfig(), phase_override="fase-2")
    path = cwd_project / "docs" / "logbooks" / "logbook_fase-2_01.md"
    assert path.is_file()
    assert "Entrada fase 2" in path.read_text(encoding="utf-8")


def test_partition_moves_overflow_to_new_file(
    cwd_project: Path,
) -> None:
    config = LogsayerConfig(bitacora_max_lines=4)
    add_entry(cwd_project, "A", config)
    add_entry(cwd_project, "B", config)
    add_entry(cwd_project, "C", config)
    logs = cwd_project / "docs" / "logbooks"
    first = (logs / "logbook_general_01.md").read_text(encoding="utf-8")
    second = (logs / "logbook_general_02.md").read_text(encoding="utf-8")
    assert "A" in first
    assert "B" in first
    assert "C" in second
    assert "C" not in first
    index = (logs / "00_index.md").read_text(encoding="utf-8")
    assert "logbook_general_02.md" in index


def test_write_index_rebuilds_from_real_files(cwd_project: Path) -> None:
    add_entry(cwd_project, "A", LogsayerConfig())
    add_entry(cwd_project, "B", LogsayerConfig())
    index = cwd_project / "docs" / "logbooks" / "00_index.md"
    index.write_text("# Bitácoras — índice\n", encoding="utf-8")
    write_index(cwd_project)
    content = index.read_text(encoding="utf-8")
    assert "| Archivo | Fase | Rango | Decisiones clave |" in content
    assert "logbook_general_01.md" in content


def test_rejects_unknown_phase_in_index(cwd_project: Path) -> None:
    set_closed_hus(cwd_project, 9)
    add_entry(cwd_project, "Con fase", LogsayerConfig(), phase_override="alpha")
    index = (
        cwd_project / "docs" / "logbooks" / "00_index.md"
    ).read_text(encoding="utf-8")
    assert "logbook_alpha_01.md" in index