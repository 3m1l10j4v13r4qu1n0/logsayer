from pathlib import Path

import pytest

from logsayer.config import LogsayerConfig
from logsayer.core import presets as presets_module
from logsayer.core.presets import PresetError, available, load

SHIPPED = ("default", "minimal")


def test_available_are_the_two_shipped_ones() -> None:
    assert available() == SHIPPED


def test_default_overrides_nothing() -> None:
    preset = load("default")
    assert preset.thresholds == LogsayerConfig()
    assert preset.enabled == ()


def test_minimal_is_looser_and_declares_one_adapter() -> None:
    preset = load("minimal")
    assert preset.thresholds == LogsayerConfig(
        session_close_context_threshold=0.85,
        bitacora_max_lines=800,
        audit_threshold_hus=5,
        inbox_max_age_days=30,
    )
    assert preset.enabled == ("claude",)


@pytest.mark.parametrize("name", SHIPPED)
def test_every_shipped_preset_validates_against_the_project_config(name: str) -> None:
    # El preset se valida con el mismo `LogsayerConfig` que lee el TOML del
    # proyecto: un preset roto tiene que ser imposible de llevar al scaffold.
    assert isinstance(load(name).thresholds, LogsayerConfig)


def test_unknown_preset_names_the_available_ones() -> None:
    with pytest.raises(PresetError) as exc:
        load("estricto")
    message = str(exc.value)
    assert "estricto" in message
    assert "default" in message and "minimal" in message


def _fake_package(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Apunta el lector de presets a un directorio temporal del test."""
    root = tmp_path / "presets"
    root.mkdir()
    monkeypatch.setattr(presets_module, "files", lambda package: tmp_path)
    return root


def test_invalid_threshold_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _fake_package(tmp_path, monkeypatch)
    (root / "roto.toml").write_text(
        "[logsayer]\naudit_threshold_hus = 'tres'\n", encoding="utf-8"
    )
    with pytest.raises(PresetError) as exc:
        load("roto")
    assert "umbrales invalidos" in str(exc.value)


def test_unparsable_preset_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _fake_package(tmp_path, monkeypatch)
    (root / "roto.toml").write_text("esto no es toml = = =\n", encoding="utf-8")
    with pytest.raises(PresetError):
        load("roto")


def test_enabled_must_be_a_list_of_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _fake_package(tmp_path, monkeypatch)
    (root / "roto.toml").write_text(
        "[adapters]\nenabled = 'claude'\n", encoding="utf-8"
    )
    with pytest.raises(PresetError) as exc:
        load("roto")
    assert "lista de texto" in str(exc.value)


def test_unknown_adapter_in_a_preset_is_not_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # El juicio de si el nombre existe es del check `adaptadores_declarados`:
    # el preset no puede saber qué adaptadores tendrá la versión futura.
    root = _fake_package(tmp_path, monkeypatch)
    (root / "futuro.toml").write_text(
        "[adapters]\nenabled = ['hermes']\n", encoding="utf-8"
    )
    assert load("futuro").enabled == ("hermes",)


def test_empty_package_reports_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_package(tmp_path, monkeypatch)
    assert available() == ()
    with pytest.raises(PresetError) as exc:
        load("minimal")
    assert "ninguno" in str(exc.value)
