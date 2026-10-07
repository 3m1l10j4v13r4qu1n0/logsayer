"""Presets de proyecto (`init --preset <nombre>`, fase 7 — spec §4).

Los presets son **datos, no código**: TOML dentro del paquete, leído con
`importlib.resources` y no importado. Agregar un preset es agregar un archivo.

El preset es un **snapshot, no una herencia viva**: `init` copia los valores al
`logsayer.toml` del proyecto y el preset deja de existir para ese proyecto, así
que no hay que resolver "qué pasa si el preset cambia en la próxima versión". El
precio —que actualizar logsayer no actualiza los umbrales de un proyecto ya
scaffoldeado— se paga con el check `preset_conocido`, que avisa cuando el nombre
declarado ya no existe en el paquete instalado.

La precedencia son dos escalones y no tres: el preset elige, y cada clave que
declara pisa el default del dataclass mientras las que omite caen al default.
No hay un escalón intermedio porque `init` no expone banderas de umbral.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from importlib.resources import files
from importlib.resources.abc import Traversable

from logsayer.config import LogsayerConfig

_SUFFIX = ".toml"


class PresetError(Exception):
    """Error controlado al resolver o cargar un preset."""


@dataclass(frozen=True)
class Preset:
    """Un preset ya validado: umbrales resueltos + adaptadores declarados.

    `enabled` es una **declaración**, no una ejecución: los archivos los escribe
    `agent add`, porque `generate_adapters()` pisa lo que encuentra sin preguntar
    y `init --here` no puede romper su promesa de no sobrescribir (D30).
    """

    name: str
    thresholds: LogsayerConfig
    enabled: tuple[str, ...]


def _preset_dir() -> Traversable:
    return files("logsayer") / "presets"


def available() -> tuple[str, ...]:
    """Nombres de los presets empaquetados, ordenados."""
    directory = _preset_dir()
    if not directory.is_dir():  # pragma: no cover - instalación sin los datos
        return ()
    names = (
        item.name[: -len(_SUFFIX)]
        for item in directory.iterdir()
        if item.name.endswith(_SUFFIX) and item.is_file()
    )
    return tuple(sorted(names))


def _read_enabled(data: dict[str, object], name: str) -> tuple[str, ...]:
    section = data.get("adapters")
    if section is None:
        return ()
    if not isinstance(section, dict):
        raise PresetError(f"[adapters] del preset {name!r} debe ser un TOML table.")
    raw = section.get("enabled", [])
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise PresetError(
            f"[adapters] enabled del preset {name!r} debe ser una lista de texto."
        )
    # Un nombre desconocido NO es un error del preset: el diseño lo deja pasar
    # a propósito y avisa el check `adaptadores_declarados`, que es donde vive el
    # juicio. Un preset no puede saber qué adaptadores tendrá la versión futura.
    return tuple(raw)


def load(name: str) -> Preset:
    """Carga el preset `name` del paquete, con sus umbrales ya validados.

    Los umbrales se validan contra el mismo `LogsayerConfig` que lee el
    `logsayer.toml` del proyecto, así que un preset roto no puede llegar al
    scaffold. Los adaptadores se validan solo como lista de texto: si el nombre
    existe o no es cosa del check (spec §4, D13).
    """
    resource = _preset_dir() / f"{name}{_SUFFIX}"
    if not resource.is_file():
        raise PresetError(
            f"Preset desconocido: {name!r}. Disponibles: "
            + (", ".join(available()) or "ninguno")
            + "."
        )
    try:
        data = tomllib.loads(resource.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise PresetError(f"El preset {name!r} no se pudo leer: {exc}") from exc
    try:
        thresholds = LogsayerConfig.from_mapping(data.get("logsayer", {}))
    except ValueError as exc:
        raise PresetError(
            f"El preset {name!r} tiene umbrales invalidos: {exc}"
        ) from exc
    return Preset(
        name=name,
        thresholds=thresholds,
        enabled=_read_enabled(data, name),
    )