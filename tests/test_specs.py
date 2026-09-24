from pathlib import Path

import pytest

from logsayer.core.specs import SpecError, create_hu, valid_hu


def test_valid_hu_accepts_sequence() -> None:
    assert valid_hu("HU-01")
    assert valid_hu("HU-123")


@pytest.mark.parametrize("bad", ["hu-01", "HU", "HU-", "HU-01-", "xHU-01"])
def test_valid_hu_rejects_bad_format(bad: str) -> None:
    assert not valid_hu(bad)


def test_create_hu_writes_template(cwd_project: Path) -> None:
    target = create_hu(cwd_project, "HU-01")
    assert target == cwd_project / "docs" / "04_user_stories" / "HU-01" / "README.md"
    content = target.read_text(encoding="utf-8")
    assert "HU-01" in content
    assert "Cómo se valida" in content


def test_create_hu_rejects_invalid_identifier(cwd_project: Path) -> None:
    with pytest.raises(SpecError):
        create_hu(cwd_project, "nope")


def test_create_hu_rejects_existing(cwd_project: Path) -> None:
    create_hu(cwd_project, "HU-02")
    with pytest.raises(SpecError, match="ya existe"):
        create_hu(cwd_project, "HU-02")