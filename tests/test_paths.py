from pathlib import Path

from logsayer.core.paths import find_logsayer_root


def test_find_logsayer_root_from_child(cwd_project: Path) -> None:
    sub = cwd_project / "src" / "pkg"
    sub.mkdir(parents=True)
    assert find_logsayer_root(sub) == cwd_project


def test_find_logsayer_root_none(tmp_path: Path) -> None:
    assert find_logsayer_root(tmp_path) is None