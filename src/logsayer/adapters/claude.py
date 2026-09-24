"""Adaptador para Claude Code: subagentes por rol en `.claude/agents/` (spec §6).

Cada archivo es un subagente en formato markdown de Claude (frontmatter
`name`/`description`/`tools` + system prompt) que invoca comandos del CLI.
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