import re
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
    result = runner.invoke(app, ["agent", "add", "cursor"])
    assert result.exit_code != 0
    assert "aún no implementado" in result.output
    assert not (cwd_project / ".cursor").exists()


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


# --- Copilot (HU-17, D-07) ----------------------------------------------------
#
# Copilot separa perfil e instrucción: `.github/agents/<rol>.agent.md` declara
# quién es el rol y qué herramientas tiene, y
# `.github/instructions/logsayer/<rol>.instructions.md` declara en qué rutas
# aplica. Los alias y los campos de frontmatter de abajo están verificados contra
# la documentación oficial de GitHub (D24: nada que la herramienta ignore).
COPILOT_ROLES = OPCODE_ROLES

# Alias canónicos de `tools:` en un perfil de agente de Copilot.
COPILOT_TOOL_ALIASES = frozenset(
    {"execute", "read", "edit", "search", "agent", "web", "todo"}
)

# Campos que la documentación oficial declara como ignorados, retirados o
# redundantes: escribirlos sería ruido que se lee como garantía.
COPILOT_CAMPOS_PROHIBIDOS = (
    "argument-hint:",
    "handoffs:",
    "infer:",
    "target:",
    "permissions:",
)

# Qué herramientas necesita cada rol: la Decidora escribe la tabla de
# veredictos y la Reverenda Madre solo appendea por CLI.
COPILOT_TOOLS_POR_ROL = {
    "mentat": {"read", "search", "edit", "execute"},
    "navigator": {"read", "search", "edit", "execute"},
    "reverend-mother": {"read", "search", "execute"},
    "truthsayer": {"read", "search", "edit", "execute"},
}


def _frontmatter(text: str) -> str:
    return text.split("---")[1]


def test_copilot_genera_perfiles_e_instrucciones(cwd_project: Path) -> None:
    result = runner.invoke(app, ["agent", "add", "copilot"])
    assert result.exit_code == 0, result.output
    for rol in COPILOT_ROLES:
        perfil = cwd_project / ".github" / "agents" / f"{rol}.agent.md"
        instrucciones = cwd_project / ".github" / "instructions" / "logsayer"
        instruccion = instrucciones / f"{rol}.instructions.md"
        assert perfil.is_file(), f"falta {perfil}"
        assert instruccion.is_file(), f"falta {instruccion}"


def test_copilot_no_genera_copilot_instructions_md(cwd_project: Path) -> None:
    """D37: Copilot consume `AGENTS.md` nativamente, así que un
    `.github/copilot-instructions.md` sería una segunda fuente de verdad para lo
    mismo — y dos archivos que se contradicen no los separa ningún check."""
    assert runner.invoke(app, ["agent", "add", "copilot"]).exit_code == 0
    assert not (cwd_project / ".github" / "copilot-instructions.md").exists()
    assert (cwd_project / "AGENTS.md").is_file()


def test_copilot_perfiles_declaran_solo_campos_que_copilot_usa(
    cwd_project: Path,
) -> None:
    """`description` es el único campo requerido y `tools` el que restringe la
    superficie. Todo lo demás o es opcional con default sano, o la documentación
    lo declara ignorado (`argument-hint`, `handoffs`) o retirado (`infer`)."""
    assert runner.invoke(app, ["agent", "add", "copilot"]).exit_code == 0
    for rol in COPILOT_ROLES:
        texto = (cwd_project / ".github" / "agents" / f"{rol}.agent.md").read_text(
            encoding="utf-8"
        )
        frontmatter = _frontmatter(texto)
        assert "description:" in frontmatter, rol
        assert "tools:" in frontmatter, rol
        for campo in COPILOT_CAMPOS_PROHIBIDOS:
            assert campo not in frontmatter, f"{rol} declara {campo}"


def test_copilot_usa_alias_canonicos_de_herramientas(cwd_project: Path) -> None:
    """Un alias desconocido se ignora en silencio, así que un typo deja al rol sin
    herramienta sin ningún error visible (D24)."""
    assert runner.invoke(app, ["agent", "add", "copilot"]).exit_code == 0
    for rol in COPILOT_ROLES:
        texto = (cwd_project / ".github" / "agents" / f"{rol}.agent.md").read_text(
            encoding="utf-8"
        )
        linea = next(
            linea_tools
            for linea_tools in _frontmatter(texto).splitlines()
            if linea_tools.startswith("tools:")
        )
        declarados = set(re.findall(r'"([^"]+)"', linea))
        assert declarados, f"{rol} no declara herramientas"
        assert declarados <= COPILOT_TOOL_ALIASES, f"{rol}: {declarados}"
        assert declarados == COPILOT_TOOLS_POR_ROL[rol], rol


def test_copilot_truthsayer_declara_edit_y_reverend_mother_no(
    cwd_project: Path,
) -> None:
    """La Decidora escribe la tabla de veredictos: sin `edit` declara que no
    puede. La Reverenda Madre sí se declara sin `edit`, porque su única escritura
    es `logsayer log add` (D40)."""
    assert runner.invoke(app, ["agent", "add", "copilot"]).exit_code == 0
    truthsayer = (
        cwd_project / ".github" / "agents" / "truthsayer.agent.md"
    ).read_text(encoding="utf-8")
    reverend = (
        cwd_project / ".github" / "agents" / "reverend-mother.agent.md"
    ).read_text(encoding="utf-8")
    assert '"edit"' in _frontmatter(truthsayer)
    assert '"edit"' not in _frontmatter(reverend)


def test_copilot_instrucciones_declaran_applyto_y_excluyen_code_review(
    cwd_project: Path,
) -> None:
    """`applyTo` es lo que hace que las reglas de un rol no lleguen a los
    archivos de los otros; `excludeAgent: "code-review"` saca el prompt de un
    contexto donde el rol no existe (D39)."""
    assert runner.invoke(app, ["agent", "add", "copilot"]).exit_code == 0
    for rol in COPILOT_ROLES:
        texto = (
            cwd_project
            / ".github"
            / "instructions"
            / "logsayer"
            / f"{rol}.instructions.md"
        ).read_text(encoding="utf-8")
        frontmatter = _frontmatter(texto)
        assert 'excludeAgent: "code-review"' in frontmatter, rol
        apply_to = re.search(r'applyTo:\s*"([^"]+)"', frontmatter)
        assert apply_to, f"{rol} no declara applyTo"
        assert apply_to.group(1).startswith("docs/"), rol


def test_copilot_applyto_cubre_la_capa_de_cada_rol(cwd_project: Path) -> None:
    """Cada rol se inyecta donde tiene algo que hacer, y en ningún otro lado."""
    assert runner.invoke(app, ["agent", "add", "copilot"]).exit_code == 0

    def apply_to(rol: str) -> str:
        texto = (
            cwd_project
            / ".github"
            / "instructions"
            / "logsayer"
            / f"{rol}.instructions.md"
        ).read_text(encoding="utf-8")
        return re.search(r'applyTo:\s*"([^"]+)"', texto).group(1)  # type: ignore[union-attr]

    capas = {
        "mentat": ("docs/01_global", "docs/02_technical", "docs/04_user_stories"),
        "navigator": ("docs/project_state.md",),
        "reverend-mother": ("docs/logbooks/",),
        "truthsayer": ("docs/06_audits/",),
    }
    for rol, esperadas in capas.items():
        patrones = apply_to(rol).split(",")
        for esperada in esperadas:
            assert any(esperada in patron for patron in patrones), (rol, esperada)
        # ninguna otra capa se filtra en el patrón de este rol
        for otro, propias in capas.items():
            if otro == rol:
                continue
            ajenas = [c for c in propias if c not in esperadas]
            assert not [c for c in ajenas if c in apply_to(rol)], (rol, otro)


def test_copilot_renderiza_los_umbrales_del_toml(cwd_project: Path) -> None:
    assert runner.invoke(app, ["agent", "add", "copilot"]).exit_code == 0
    truthsayer = (
        cwd_project / ".github" / "agents" / "truthsayer.agent.md"
    ).read_text(encoding="utf-8")
    assert ">= 3" in truthsayer
    reverend = (
        cwd_project / ".github" / "agents" / "reverend-mother.agent.md"
    ).read_text(encoding="utf-8")
    assert "400 líneas" in reverend


def test_copilot_esta_en_el_registro_y_no_en_pendientes() -> None:
    from logsayer.adapters.registry import NOT_YET_IMPLEMENTED, REGISTRY

    assert "copilot" in REGISTRY
    assert "copilot" not in NOT_YET_IMPLEMENTED
    assert REGISTRY["copilot"].name == "copilot"


def test_los_tres_adaptadores_invocan_los_mismos_comandos_de_mentat(
    cwd_project: Path,
) -> None:
    """HU-17 agrega el tercer adaptador: la paridad de comandos del rol es lo que
    hace comparables las tres superficies declarativas, que no pueden ser iguales
    porque las herramientas no lo permiten (D24)."""
    for agente in ("opencode", "claude", "copilot"):
        assert runner.invoke(app, ["agent", "add", agente]).exit_code == 0
    contenidos = {
        "opencode": (cwd_project / ".opencode" / "agents" / "mentat.md").read_text(
            encoding="utf-8"
        ),
        "claude": (cwd_project / ".claude" / "agents" / "mentat.md").read_text(
            encoding="utf-8"
        ),
        "copilot": (cwd_project / ".github" / "agents" / "mentat.agent.md").read_text(
            encoding="utf-8"
        ),
    }
    for comando in COMANDOS_DE_MENTAT:
        for agente, contenido in contenidos.items():
            assert comando in contenido, (agente, comando)