import tomllib
from pathlib import Path

import pytest

from logsayer.config import LogsayerConfig
from logsayer.core.presets import load
from logsayer.scaffold import (
    RENDERED_FILES,
    STATIC_DIRS,
    ScaffoldError,
    resolve_target,
    scaffold,
    validate_target,
)


def _scaffold(target: Path, project_name: str) -> None:
    scaffold(target, project_name, LogsayerConfig())


def test_resolve_target_plain_name(tmp_path: Path) -> None:
    target, name = resolve_target("mi-proyecto", False, tmp_path)
    assert target == tmp_path / "mi-proyecto"
    assert name == "mi-proyecto"


def test_resolve_target_here(tmp_path: Path) -> None:
    target, name = resolve_target(None, True, tmp_path)
    assert target == tmp_path
    assert name == tmp_path.name


def test_resolve_target_here_rejects_name(tmp_path: Path) -> None:
    with pytest.raises(ScaffoldError):
        resolve_target("mi-proyecto", True, tmp_path)


def test_resolve_target_requires_name_or_here(tmp_path: Path) -> None:
    with pytest.raises(ScaffoldError):
        resolve_target(None, False, tmp_path)


def test_resolve_target_rejects_invalid_slug(tmp_path: Path) -> None:
    with pytest.raises(ScaffoldError):
        resolve_target("mi proyecto!", False, tmp_path)


def test_validate_target_rejects_non_empty(tmp_path: Path) -> None:
    occupied = tmp_path / "ocupado"
    occupied.mkdir()
    (occupied / "algo.txt").write_text("x", encoding="utf-8")
    with pytest.raises(ScaffoldError):
        validate_target(occupied)


def test_validate_target_accepts_empty(tmp_path: Path) -> None:
    empty = tmp_path / "vacio"
    empty.mkdir()
    validate_target(empty)


def test_scaffold_creates_full_structure(tmp_path: Path) -> None:
    target = tmp_path / "mi-proyecto"
    _scaffold(target, "mi-proyecto")
    for directory in STATIC_DIRS:
        assert (target / "docs" / directory / ".gitkeep").is_file()
    for rel_path in RENDERED_FILES:
        assert (target / rel_path).is_file()


def test_scaffold_renders_thresholds(tmp_path: Path) -> None:
    target = tmp_path / "proyecto"
    _scaffold(target, "proyecto")
    parsed = tomllib.loads((target / "logsayer.toml").read_text(encoding="utf-8"))
    section = parsed["logsayer"]
    assert section["session_close_context_threshold"] == 0.70
    assert section["bitacora_max_lines"] == 400
    assert section["audit_threshold_hus"] == 3


def test_scaffold_project_state_contains_template(tmp_path: Path) -> None:
    target = tmp_path / "proyecto"
    _scaffold(target, "proyecto")
    content = (target / "docs" / "project_state.md").read_text(encoding="utf-8")
    assert "Estado del proyecto — proyecto" in content
    assert "HUs cerradas desde la última auditoría" in content
    assert "0" in content


def test_scaffold_agents_md_uses_config(tmp_path: Path) -> None:
    target = tmp_path / "proyecto"
    scaffold(target, "proyecto", LogsayerConfig(audit_threshold_hus=5))
    content = (target / "AGENTS.md").read_text(encoding="utf-8")
    assert ">= 5" in content


def test_scaffold_adopts_existing_target(tmp_path: Path) -> None:
    target = tmp_path / "existente"
    target.mkdir()
    (target / "algo.txt").write_text("x", encoding="utf-8")
    written = scaffold(target, "existente", LogsayerConfig(), adopt=True)
    assert "docs/project_state.md" in [str(p) for p in written]
    for directory in STATIC_DIRS:
        assert (target / "docs" / directory / ".gitkeep").is_file()
    assert (target / "algo.txt").read_text(encoding="utf-8") == "x"


def test_scaffold_adopt_keeps_existing_agents(tmp_path: Path) -> None:
    target = tmp_path / "existente"
    target.mkdir()
    (target / "AGENTS.md").write_text("contenido propio", encoding="utf-8")
    written = scaffold(target, "existente", LogsayerConfig(), adopt=True)
    assert not any(str(p) == "AGENTS.md" for p in written)
    assert (target / "AGENTS.md").read_text(encoding="utf-8") == "contenido propio"


def test_scaffold_adopt_requires_existing_target(tmp_path: Path) -> None:
    written = scaffold(tmp_path / "nuevo", "nuevo", LogsayerConfig(), adopt=True)
    assert (tmp_path / "nuevo" / "docs" / "project_state.md").is_file()
    assert any(str(p) == "docs/project_state.md" for p in written)


def test_scaffold_without_preset_writes_no_new_tables(tmp_path: Path) -> None:
    # El TOML de un proyecto sin preset tiene que salir como siempre: `[project]`
    # y `[adapters]` son del preset, y escribirlos siempre agregaría una clave
    # que ningún comando consume en un proyecto que nunca pidió un preset.
    target = tmp_path / "proyecto"
    _scaffold(target, "proyecto")
    parsed = tomllib.loads((target / "logsayer.toml").read_text(encoding="utf-8"))
    assert set(parsed) == {"logsayer"}


def test_scaffold_materializes_the_preset(tmp_path: Path) -> None:
    target = tmp_path / "proyecto"
    preset = load("minimal")
    scaffold(target, "proyecto", preset.thresholds, preset=preset)
    parsed = tomllib.loads((target / "logsayer.toml").read_text(encoding="utf-8"))
    assert parsed["project"]["preset"] == "minimal"
    assert parsed["adapters"]["enabled"] == ["claude"]
    assert parsed["logsayer"]["bitacora_max_lines"] == 800
    assert parsed["logsayer"]["audit_threshold_hus"] == 5


def test_preset_default_writes_the_same_thresholds_as_no_preset(tmp_path: Path) -> None:
    # `default` es literalmente "no sobreescribir nada": si el dataclass cambia,
    # los dos caminos tienen que seguir dando lo mismo, y por eso el test compara
    # las dos salidas y no una lista de valores.
    plain = tmp_path / "plain"
    preset_target = tmp_path / "con-preset"
    _scaffold(plain, "x")
    preset = load("default")
    scaffold(preset_target, "x", preset.thresholds, preset=preset)
    plain_toml = (plain / "logsayer.toml").read_text(encoding="utf-8")
    preset_toml = (preset_target / "logsayer.toml").read_text(encoding="utf-8")
    plain_section = tomllib.loads(plain_toml)["logsayer"]
    preset_section = tomllib.loads(preset_toml)["logsayer"]
    assert plain_section == preset_section
    assert "[project]" not in plain_toml


def test_scaffold_never_generates_adapter_files(tmp_path: Path) -> None:
    # D30: el preset declara y `agent add` ejecuta. Un `init --preset` que
    # escribiera `.claude/agents/` rompería la promesa de `init --here` de no
    # sobrescribir lo que ya está.
    target = tmp_path / "proyecto"
    preset = load("minimal")
    scaffold(target, "proyecto", preset.thresholds, preset=preset)
    for owned in (".opencode", ".claude", ".github"):
        assert not (target / owned).exists()