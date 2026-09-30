"""Adaptador para Claude Code: subagentes por rol en `.claude/agents/` (spec §6).

Cada archivo es un subagente en formato markdown de Claude (frontmatter
`name`/`description`/`tools` + system prompt) que invoca comandos del CLI.

El `tools:` es toda la superficie declarativa que Claude Code da a un subagente y
su granularidad es la herramienta, no el recurso: no hay equivalente al bloque
`permissions:` de opencode, que evalúa reglas ordenadas por acción, recurso y
efecto. El alcance por ruta queda en el prompt y en las reglas de la sesión, y
los templates lo dicen en vez de dejar que la prosa parezca una garantía. Las
reglas por recurso de `settings.json` son de sesión —alcanzarían a la sesión
principal y a los otros roles—, así que el CLI no las genera. Ver HU-14.
"""

from __future__ import annotations

from logsayer.adapters.base import AdapterFile, AdapterSpec

ROLES: tuple[str, ...] = ("mentat", "navigator", "reverend-mother", "truthsayer")

claude_spec = AdapterSpec(
    name="claude",
    files=tuple(
        AdapterFile(
            f".claude/agents/{rol}.md",
            f"adapters/claude/{rol}.md.j2",
        )
        for rol in ROLES
    ),
)