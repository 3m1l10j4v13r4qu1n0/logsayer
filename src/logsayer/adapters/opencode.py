"""Adaptador para opencode: subagentes por rol en `.opencode/agents/` (spec §6).

Cada archivo es un agente en formato markdown de opencode (frontmatter
`description`/`mode`/`permissions` + system prompt) que invoca comandos del CLI.
"""

from __future__ import annotations

from logsayer.adapters.base import AdapterFile, AdapterSpec

ROLES: tuple[str, ...] = ("mentat", "navigator", "reverend-mother", "truthsayer")

opencode_spec = AdapterSpec(
    name="opencode",
    files=tuple(
        AdapterFile(
            f".opencode/agents/{rol}.md",
            f"adapters/opencode/{rol}.md.j2",
        )
        for rol in ROLES
    ),
)