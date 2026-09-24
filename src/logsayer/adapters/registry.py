"""Registro de adaptadores disponibles y resolución por nombre (spec §5)."""

from __future__ import annotations

from logsayer.adapters.base import AdapterSpec
from logsayer.adapters.claude import claude_spec
from logsayer.adapters.opencode import opencode_spec

REGISTRY: dict[str, AdapterSpec] = {
    "opencode": opencode_spec,
    "claude": claude_spec,
}

# Conocidos por el spec §5 pero aún sin adaptador (fase 3: solo opencode y claude).
NOT_YET_IMPLEMENTED: frozenset[str] = frozenset(
    {"copilot", "cursor", "gemini", "hermes"}
)

SUPPORTED: frozenset[str] = frozenset(REGISTRY)


class AgentError(Exception):
    """Error controlado al resolver o generar un adaptador."""


def resolve_adapter(agent: str) -> AdapterSpec:
    if agent in REGISTRY:
        return REGISTRY[agent]
    if agent in NOT_YET_IMPLEMENTED:
        raise AgentError(
            f"Adaptador {agent!r} aún no implementado. "
            "Fase 3 soporta: " + ", ".join(sorted(SUPPORTED)) + "."
        )
    raise AgentError(
        f"Agente desconocido {agent!r}. Soporta: "
        + ", ".join(sorted(SUPPORTED))
        + "."
    )