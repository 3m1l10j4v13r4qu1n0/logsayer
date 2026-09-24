"""Carga y validación de la configuración `logsayer.toml` (tabla `[logsayer]`)."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


def _number(value: object, field: str) -> float:
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field} debe ser un numero.")
    return float(value)


def _integer(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} debe ser un entero.")
    return value


@dataclass(frozen=True)
class LogsayerConfig:
    """Umbrales de configuración del framework (sección 4 de la spec maestra)."""

    session_close_context_threshold: float = 0.70
    bitacora_max_lines: int = 400
    audit_threshold_hus: int = 3

    @property
    def context_threshold_percent(self) -> int:
        return round(self.session_close_context_threshold * 100)

    @classmethod
    def load(cls, path: Path | None = None) -> LogsayerConfig:
        """Carga `logsayer.toml`; si no existe o le falta `[logsayer]`, usa defaults."""
        if path is None or not path.is_file():
            return cls()
        with path.open("rb") as fh:
            data = tomllib.load(fh)
        section = data.get("logsayer")
        if section is None:
            return cls()
        if not isinstance(section, dict):
            raise ValueError("La tabla [logsayer] debe ser un TOML table.")

        threshold = _number(
            section.get("session_close_context_threshold", 0.70),
            "session_close_context_threshold",
        )
        if not 0.0 < threshold < 1.0:
            raise ValueError("session_close_context_threshold debe estar entre 0 y 1.")
        max_lines = _integer(
            section.get("bitacora_max_lines", 400),
            "bitacora_max_lines",
        )
        hus = _integer(section.get("audit_threshold_hus", 3), "audit_threshold_hus")
        return cls(
            session_close_context_threshold=threshold,
            bitacora_max_lines=max_lines,
            audit_threshold_hus=hus,
        )