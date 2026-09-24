from pathlib import Path

from logsayer.config import LogsayerConfig


def test_defaults_when_file_missing(tmp_path: Path) -> None:
    config = LogsayerConfig.load(tmp_path / "no-existe.toml")
    assert config.session_close_context_threshold == 0.70
    assert config.bitacora_max_lines == 400
    assert config.audit_threshold_hus == 3
    assert config.context_threshold_percent == 70


def test_loads_known_fields(tmp_path: Path) -> None:
    config_file = tmp_path / "logsayer.toml"
    config_file.write_text(
        "[logsayer]\n"
        "session_close_context_threshold = 0.5\n"
        "bitacora_max_lines = 60\n"
        "audit_threshold_hus = 5\n",
        encoding="utf-8",
    )
    config = LogsayerConfig.load(config_file)
    assert config.session_close_context_threshold == 0.5
    assert config.bitacora_max_lines == 60
    assert config.audit_threshold_hus == 5
    assert config.context_threshold_percent == 50


def test_missing_table_uses_defaults(tmp_path: Path) -> None:
    config_file = tmp_path / "logsayer.toml"
    config_file.write_text("version = 1\n", encoding="utf-8")
    config = LogsayerConfig.load(config_file)
    assert config.session_close_context_threshold == 0.70


def test_rejects_out_of_range_threshold(tmp_path: Path) -> None:
    config_file = tmp_path / "logsayer.toml"
    config_file.write_text(
        "[logsayer]\nsession_close_context_threshold = 1.5\n",
        encoding="utf-8",
    )
    try:
        LogsayerConfig.load(config_file)
    except ValueError:
        return
    raise AssertionError("se esperaba ValueError para umbral fuera de rango")