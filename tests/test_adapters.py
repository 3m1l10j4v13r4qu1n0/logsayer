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


# Los comandos que HU-07 nombraba y que la auditoría del 2026-09-29 dejó a
# HU-07 en `parcial` por estar declarados solo en un lado.
COMANDOS_DE_MENTAT = ("logsayer spec new", "logsayer doc new", "logsayer doc route")


def test_mentat_opencode_declara_los_comandos_como_shell_allow(
    cwd_project: Path,
) -> None:
    """El bloque `permissions:` de opencode es un evaluador ordenado: el allow
    tiene que preceder al `ask` general, o la excepción se lo come. Por eso el
    test mira el orden, no solo la presencia."""
    assert runner.invoke(app, ["agent", "add", "opencode"]).exit_code == 0
    content = (cwd_project / ".opencode" / "agents" / "mentat.md").read_text(
        encoding="utf-8"
    )
    posiciones = []
    for comando in COMANDOS_DE_MENTAT:
        regla = f'resource: "{comando}*"'
        assert f'action: shell\n    {regla}\n    effect: allow' in content
        posiciones.append(content.index(regla))
    shell_ask = content.index('resource: "*"\n    effect: ask')
    assert max(posiciones) < shell_ask, "el allow tiene que preceder al ask"
    edit_deny = content.index('resource: "*"\n    effect: deny')
    assert edit_deny < shell_ask, "el deny de edit tiene que preceder al shell"


def test_mentat_claude_declara_la_superficie_y_su_excepcion(cwd_project: Path) -> None:
    """En Claude Code la superficie declarada es el allowlist `tools:`, de
    granularidad por herramienta. El template no escribe reglas por recurso
    porque las de `settings.json` son de sesión: no acotarían al subagente
    (D24, HU-14)."""
    assert runner.invoke(app, ["agent", "add", "claude"]).exit_code == 0
    content = (cwd_project / ".claude" / "agents" / "mentat.md").read_text(
        encoding="utf-8"
    )
    frontmatter = content.split("---")[1]
    assert "tools: Read, Grep, Glob, Write, Edit, Bash" in frontmatter
    assert "permissions" not in frontmatter, "el frontmatter no declara permisos"
    assert "## Permisos: qué es declaración y qué es instrucción" in content
    assert "la herramienta**, no la ruta" in content


def test_los_dos_adaptadores_invocan_los_mismos_comandos_de_mentat(
    cwd_project: Path,
) -> None:
    """HU-07 nombraba `doc route*` y `doc new*` en los dos `mentat.md.j2`. La
    superficie declarativa no se puede igualar entre herramientas (D24), pero los
    comandos que el rol tiene que poder correr sí: si uno deja de invocarlos,
    el otro no debería seguir declarando que puede."""
    runner.invoke(app, ["agent", "add", "opencode"])
    runner.invoke(app, ["agent", "add", "claude"])
    opencode = (cwd_project / ".opencode" / "agents" / "mentat.md").read_text(
        encoding="utf-8"
    )
    claude = (cwd_project / ".claude" / "agents" / "mentat.md").read_text(
        encoding="utf-8"
    )
    for comando in COMANDOS_DE_MENTAT:
        assert comando in opencode, comando
        assert comando in claude, comando