from pathlib import Path

from typer.testing import CliRunner

from logsayer.cli import app

runner = CliRunner()

OPCODE_ROLES = ("mentat", "navigator", "reverend-mother", "truthsayer")
CLAUDE_ROLES = OPCODE_ROLES


def test_agent_add_opencode_generates_subagents(cwd_project: Path) -> None:
    result = runner.invoke(app, ["agent", "add", "opencode"])
    assert result.exit_code == 0, result.output
    for rol in OPCODE_ROLES:
        path = cwd_project / ".opencode" / "agents" / f"{rol}.md"
        assert path.is_file(), f"falta {path}"
        content = path.read_text(encoding="utf-8")
        assert "mode: subagent" in content
        assert "Capa" in content


def test_agent_add_claude_generates_subagents(cwd_project: Path) -> None:
    result = runner.invoke(app, ["agent", "add", "claude"])
    assert result.exit_code == 0, result.output
    for rol in CLAUDE_ROLES:
        path = cwd_project / ".claude" / "agents" / f"{rol}.md"
        assert path.is_file(), f"falta {path}"
        content = path.read_text(encoding="utf-8")
        assert f"name: {rol}" in content
        assert "description:" in content


def test_agent_add_known_but_not_implemented(cwd_project: Path) -> None:
    result = runner.invoke(app, ["agent", "add", "copilot"])
    assert result.exit_code != 0
    assert "aún no implementado" in result.output
    assert not (cwd_project / ".copilot").exists()


def test_agent_add_unknown_agent(cwd_project: Path) -> None:
    result = runner.invoke(app, ["agent", "add", "windsurf"])
    assert result.exit_code != 0
    assert "Agente desconocido" in result.output


def test_agent_add_requires_project_root(plain_cwd: Path) -> None:
    result = runner.invoke(app, ["agent", "add", "opencode"])
    assert result.exit_code != 0


def test_agent_add_renders_config_into_templates(cwd_project: Path) -> None:
    runner.invoke(app, ["agent", "add", "opencode"])
    content = (cwd_project / ".opencode" / "agents" / "truthsayer.md").read_text(
        encoding="utf-8"
    )
    assert ">= 3" in content
    content = (cwd_project / ".opencode" / "agents" / "reverend-mother.md").read_text(
        encoding="utf-8"
    )
    assert "400 líneas" in content


def test_agent_add_is_idempotent(cwd_project: Path) -> None:
    first = runner.invoke(app, ["agent", "add", "claude"])
    second = runner.invoke(app, ["agent", "add", "claude"])
    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    content = (cwd_project / ".claude" / "agents" / "mentat.md").read_text(
        encoding="utf-8"
    )
    assert content.count("name: mentat") == 1


def test_help_lists_agent(cwd_project: Path) -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "agent" in result.output