"""Carga y validación de la configuración `logsayer.toml` (tabla `[logsayer]`)."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


def raw_config(path: Path | None) -> dict[str, object]:
    """El TOML **crudo** de `path`, o `{}` si no existe.

    Los bloques que no son umbrales (`[project]`, `[adapters]`, los de los
    presets) se leen con esto: `LogsayerConfig` los ignora a propósito —su
    contrato son los umbrales (spec §4)—, así que ensuciarlo con campos que
    ningún umbral usa sería peor. Un TOML ilegible lanza `ValueError`, porque
    el fallback silencioso a `{}` haría que un check concluyera "no declarado"
    sobre un archivo que no se pudo leer: la ausencia y el fallo no son lo mismo.
    """
    if path is None or not path.is_file():
        return {}
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"No se pudo leer {path}: {exc}") from exc


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
    inbox_max_age_days: int = 14

    @property
    def context_threshold_percent(self) -> int:
        return round(self.session_close_context_threshold * 100)

    @classmethod
    def load(cls, path: Path | None = None) -> LogsayerConfig:
        """Carga `logsayer.toml`; si no existe o le falta `[logsayer]`, usa defaults."""
        section = raw_config(path).get("logsayer")
        if section is None:
            return cls()
        return cls.from_mapping(section)

    @classmethod
    def from_mapping(cls, section: object) -> LogsayerConfig:
        """Construye la config desde una tabla `[logsayer]` ya parseada.

        Existe separada de `load()` para que un preset se valide contra
        **este** contrato y no contra un segundo validador: un preset roto
        tiene que ser imposible de llevar al scaffold.
        """
        if not isinstance(section, dict):
            raise ValueError("La tabla [logsayer] debe ser un TOML table.")
        table: Mapping[str, object] = section

        threshold = _number(
            table.get("session_close_context_threshold", 0.70),
            "session_close_context_threshold",
        )
        if not 0.0 < threshold < 1.0:
            raise ValueError("session_close_context_threshold debe estar entre 0 y 1.")
        max_lines = _integer(
            table.get("bitacora_max_lines", 400),
            "bitacora_max_lines",
        )
        hus = _integer(table.get("audit_threshold_hus", 3), "audit_threshold_hus")
        inbox_age = _integer(
            table.get("inbox_max_age_days", 14),
            "inbox_max_age_days",
        )
        if inbox_age < 1:
            raise ValueError("inbox_max_age_days debe ser al menos 1.")
        return cls(
            session_close_context_threshold=threshold,
            bitacora_max_lines=max_lines,
            audit_threshold_hus=hus,
            inbox_max_age_days=inbox_age,
        )
