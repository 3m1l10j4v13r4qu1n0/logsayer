"""Adaptadores por agente: wrappers finos que llaman al motor único (spec §6).

Cada adaptador solo traduce la convención de archivos nativa de una
herramienta (opencode, Claude Code, ...) e invoca comandos del CLI.
"""

from logsayer.adapters.base import AdapterFile, AdapterSpec
from logsayer.adapters.registry import REGISTRY

__all__ = ["AdapterFile", "AdapterSpec", "REGISTRY"]