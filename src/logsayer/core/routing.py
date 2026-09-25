"""Tabla de ruteo de Capa 1: a qué capa va un documento que llega (spec §3, §5).

Es **dato del core, no heurística**: el ruteo por nombre o extensión es juicio,
y el juicio lo tiene el subagente Mentat, no el bot (spec §2, §10). La función
de esta tabla es imprimir la regla dentro de la sesión, que es lo que el agente
no tiene a mano; no clasificar mejor.

`logsayer doc route` la imprime; con un argumento, muestra la fila que aplica.
Ninguna función escribe nada.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from logsayer.core.inbox import CONVERTIBLE_EXTENSIONS

LAYER_SPEC = "1 — Especificación"
LAYER_EXTERNAL = "fuera de docs/"

TECHNICAL_DIR = Path("docs") / "02_technical"
GLOBAL_DIR = Path("docs") / "01_global"
AUDITS_DIR = Path("docs") / "06_audits"

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")

DOC_LAYERS: dict[str, Path] = {"technical": TECHNICAL_DIR, "global": GLOBAL_DIR}


class RoutingError(Exception):
    """Error controlado del ruteo de documentos."""


@dataclass(frozen=True)
class Verdict:
    """Qué puede afirmar el CLI sobre un archivo, y hasta dónde.

    `decided` viene filled solo con señal inequívoca (extensión o HU explícita
    en el nombre). En cualquier otro caso el CLI devuelve candidatos y se
    calla: elegir la capa es juicio, y el juicio lo tiene Mentat (spec §10).
    """

    path: Path
    decided: Route | None
    candidates: tuple[Route, ...]
    reason: str
    hint: str = ""
    duplicate: Path | None = None

    @property
    def is_decided(self) -> bool:
        return self.decided is not None


@dataclass(frozen=True)
class Route:
    """Una fila de la tabla: qué entra, a dónde va y con qué comando."""

    trigger: str
    destination: str
    versioned: str
    command: str
    note: str = ""

    def as_rows(self) -> tuple[tuple[str, str], ...]:
        return (
            ("Entrada", self.trigger),
            ("Va a", self.destination),
            ("¿Se versiona?", self.versioned),
            ("Crear con", self.command),
        )


ROUTES: tuple[Route, ...] = (
    Route(
        trigger="Documento de un equipo externo, entrega, acta o informe recibido",
        destination=f"{LAYER_EXTERNAL} (bandeja `inbox/`), y su derivado en Capa 1",
        versioned="el original no; el documento derivado sí",
        command="logsayer inbox add <archivo>",
        note="El original queda como fuente no versionada; la procedencia se "
        "registra en el bloque '## Fuente' del documento derivado.",
    ),
    Route(
        trigger="Contrato transversal: API, DTOs, modelo de datos, stack",
        destination=f"{LAYER_SPEC} → {TECHNICAL_DIR}/",
        versioned="sí",
        command="logsayer doc new technical <nombre>",
    ),
    Route(
        trigger="Visión, alcance, regla de negocio o requisito global",
        destination=f"{LAYER_SPEC} → {GLOBAL_DIR}/",
        versioned="sí",
        command="logsayer doc new global <nombre>",
    ),
    Route(
        trigger="Contrato o criterio que aplica a una HU puntual",
        destination=f"{LAYER_SPEC} → {Path('docs') / '04_user_stories'}/<HU>/",
        versioned="sí",
        command="logsayer spec new <HU>",
    ),
    Route(
        trigger="Informe de auditoría sobre un documento externo",
        destination=f"Capa 4 → {AUDITS_DIR}/audit_<fecha>-<area>.md",
        versioned="sí",
        command="logsayer audit run",
        note="Es el único comando que genera un reporte de auditoría: la "
        "Decidora lo completa, el CLI solo prepara estructura y prompt (spec §10).",
    ),
    Route(
        trigger='El "por qué" o el "cómo" de lo que ya se hizo',
        destination="Capa 3 → bitácora (append-only)",
        versioned="sí",
        command='logsayer log add "…"',
        note="Nunca directo en el estado: el snapshot es el presente, no el "
        "historial (spec §2, regla de oro).",
    ),
)

NARRATIVE_NOTE = (
    "Nunca: un .md suelto en docs/. Es lo que `logsayer check` rechaza como "
    "capas_mezcladas."
)


def table_rows() -> tuple[tuple[str, ...], ...]:
    """Filas de la tabla para renderizar en Markdown."""
    header = ("Entrada", "Va a", "¿Se versiona?", "Crear con")
    return (header,) + tuple(
        (route.trigger, route.destination, route.versioned, route.command)
        for route in ROUTES
    )


def to_markdown() -> str:
    """La tabla en Markdown — la misma que la del README (spec §3)."""
    rows = table_rows()
    widths = [max(len(cell) for cell in column) for column in zip(*rows, strict=True)]

    def line(cells: tuple[str, ...]) -> str:
        padded = (cell.ljust(width) for cell, width in zip(cells, widths, strict=True))
        return "| " + " | ".join(padded) + " |"

    lines = [line(rows[0]), "|" + "|".join("-" * (w + 2) for w in widths) + "|"]
    lines.extend(line(row) for row in rows[1:])
    return "\n".join(lines)


def _markdown_files(root: Path) -> list[Path]:
    docs = root / "docs"
    if not docs.is_dir():
        return []
    return sorted(
        path
        for path in docs.rglob("*.md")
        if path.name != "project_state.md" and "logbooks" not in path.parts
    )


_TRANSVERSAL_TOKENS = (
    "contrato",
    "contract",
    "api",
    "dto",
    "modelo",
    "data",
    "stack",
    "arquitectura",
    "schema",
    "openapi",
    "swagger",
)

_HU_RE = re.compile(r"(hu|user.stor|historia|story)[-_ ]?\d+", re.IGNORECASE)

_NO_DECIDE = (
    "El nombre no dice si el documento es global o técnico. Eso lo decide "
    "Mentat; el CLI no lo clasifica."
)


def _transversal_tokens(name: str) -> tuple[str, ...]:
    return tuple(token for token in _TRANSVERSAL_TOKENS if token in name)


def _existing_document(root: Path, stem: str) -> Path | None:
    """Documento de Capa 1 que ya existe con ese nombre, si hay."""
    for path in _markdown_files(root):
        if path.stem == stem:
            return path
    return None


def resolve(root: Path, raw_path: str) -> Verdict:
    """Propone filas de la tabla; solo decide con señal inequívoca.

    Inequívoco es poco: la extensión (un PDF no es un documento de capa) y una
    HU declarada en el nombre. Todo lo demás devuelve candidatos más una pista,
    porque la capa es un juicio del subagente, no del bot (spec §2, §10).
    """
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = (root / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if candidate.suffix.lower() in CONVERTIBLE_EXTENSIONS:
        return Verdict(
            path=candidate,
            decided=ROUTES[0],
            candidates=(),
            reason=f"La extensión {candidate.suffix.lower()} no es markdown: "
            "primero va a la bandeja, y el derivado se deriva aparte.",
        )

    stem = candidate.stem.replace("_", "-").lower()
    if _HU_RE.search(stem):
        return Verdict(
            path=candidate,
            decided=ROUTES[3],
            candidates=(),
            reason="El nombre declara una HU puntual.",
        )

    existing = _existing_document(root, candidate.stem)
    if existing is not None:
        return Verdict(
            path=candidate,
            decided=None,
            candidates=(),
            reason=(
                f"Ya existe un documento con ese nombre: "
                f"{existing.relative_to(root)}. No lo dupliques: actualizá ese, "
                "o renombrá el entrante."
            ),
            duplicate=existing,
        )

    tokens = _transversal_tokens(stem)
    return Verdict(
        path=candidate,
        decided=None,
        candidates=(ROUTES[1], ROUTES[2], ROUTES[3]),
        reason=_NO_DECIDE,
        hint=(
            f"el nombre tiene términos técnicos ({', '.join(tokens)}): "
            "02_technical/ es el primer candidato, pero eso no lo decide el CLI."
            if tokens
            else ""
        ),
    )


def valid_layer(layer: str) -> str:
    if layer not in DOC_LAYERS:
        options = ", ".join(sorted(DOC_LAYERS))
        raise RoutingError(
            f"Capa desconocida: {layer!r}. Opciones: {options}. "
            "Para una HU usá 'logsayer spec new <HU>'."
        )
    return layer


def valid_name(name: str) -> str:
    if not _SLUG_RE.fullmatch(name):
        raise RoutingError(
            f"Nombre inválido: {name!r}. Usa minúsculas, números y guiones "
            "bajos (ej: contrato_api_backend)."
        )
    return name
