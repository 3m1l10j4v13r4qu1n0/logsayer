from pathlib import Path

import pytest

from logsayer.config import LogsayerConfig
from logsayer.scaffold import scaffold


@pytest.fixture
def cwd_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    target = tmp_path / "proyecto-demo"
    scaffold(target, "proyecto-demo", LogsayerConfig())
    monkeypatch.chdir(target)
    return target


@pytest.fixture
def plain_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path