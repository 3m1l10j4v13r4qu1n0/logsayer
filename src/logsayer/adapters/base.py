"""Contrato declarativo de los adaptadores por agente (spec §6)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AdapterFile:
    """Archivo a generar para un adaptador: path relativo + template a renderizar."""

    rel_path: str
    template_name: str


@dataclass(frozen=True)
class AdapterSpec:
    """Definición completa de lo que genera un adaptador de agente."""

    name: str
    files: tuple[AdapterFile, ...]