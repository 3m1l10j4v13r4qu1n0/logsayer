"""Índice de memoria: capa transversal de navegación sobre `docs/` (D12).

El grafo de memoria **no es una sexta capa**: indexa las cinco para que el
agente pueda elegir qué leer primero sin leerlo todo (D14). Este módulo es la
pieza mecánica — parseo del frontmatter, nivel derivado de la ruta y
generación del artefacto `docs/00_memory_index.md`. Sin LLM y sin embeddings.

El índice es un **artefacto**: se regenera, no se edita a mano. Que la
generación sea determinista es la razón por la que `memory search` (HU-11)
puede leerlo sin volver al disco.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

DOCS_DIR = Path("docs")
INDEX_FILE = DOCS_DIR / "00_memory_index.md"

# Nivel = distancia a la especificación. El diseño (memory_architecture.md)
# fija 0/1/2 para global, technical y HUs; las capas de proceso, metodología,
# auditoría y bitácora no compiten por ser fuente de verdad de una HU, y por
# eso caen todas en el mismo nivel, el más lejano. Las rutas son relativas a
# `docs/`, que es como se reporta cada documento en el índice.
_LAYER_LEVELS: tuple[tuple[Path, int], ...] = (
    (Path("01_global"), 0),
    (Path("02_technical"), 1),
    (Path("04_user_stories"), 2),
)
_FALLBACK_LEVEL = 3
_ROOT_LEVEL = 0

_SEPARATOR = " · "
_UNKNOWN = "—"

_HU_DIR_RE = re.compile(r"^HU-\d+$")
_NUMERIC_RE = re.compile(r"^\d+$")
_FENCE = "---"
_TAGS_KEY = "tags:"
_ITEM_RE = re.compile(r"^\s*-\s*(.+?)\s*$")
_INLINE_RE = re.compile(r"^\[(.*)]$")
_HU_RE = re.compile(r"HU-\d+", re.IGNORECASE)
_STATE_RE = re.compile(
    r"^Fecha:\s*\d{4}-\d{2}-\d{2}\s*·\s*Estado:\s*(\S+)", re.MULTILINE
)
_DATE_RE = re.compile(r"^Fecha:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)
_SOURCE_HEADER = "## Fuente"

# Nombres de archivo que no aportan información: el token útil de un
# `HU-XX/README.md` es la carpeta que lo contiene, no el nombre del archivo.
_GENERIC_STEMS = frozenset(
    {"readme", "index", "indice", "doc", "documento", "notas", "nota", "borrador"}
)


@dataclass(frozen=True)
class Document:
    """Un documento indexado: identidad por ruta, metadata por header."""

    path: Path
    level: int
    state: str
    date: str
    tags: tuple[str, ...]
    declared: bool

    def row(self, width: int) -> str:
        """La línea del índice. `width` alinea la primera celda de todas."""
        cells = [
            f"nivel {self.level}",
            self.state or _UNKNOWN,
            self.date or _UNKNOWN,
        ]
        if self.tags:
            cells.append(", ".join(self.tags))
        tail = _SEPARATOR.join(cells)
        return self.path.as_posix().ljust(width) + _SEPARATOR + tail


@dataclass(frozen=True)
class IndexStatus:
    """Inventario del artefacto. No dictamina frescura: eso es `indice_al_dia`."""

    path: Path
    exists: bool
    documents: int
    declared: int
    derived: int
    generated_at: str

    def rows(self) -> tuple[tuple[str, str], ...]:
        return (
            ("artefacto", self.path.as_posix()),
            ("documentos", str(self.documents)),
            (
                "tags",
                f"{self.declared} declaradas en frontmatter, {self.derived} derivadas",
            ),
            ("generado", self.generated_at if self.exists else "—"),
        )


def index_path(root: Path) -> Path:
    return root / INDEX_FILE


def _environment() -> Environment:
    return Environment(
        loader=PackageLoader("logsayer", "templates"),
        autoescape=select_autoescape(("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def split_frontmatter(text: str) -> tuple[list[str] | None, str]:
    """Separa el bloque `---` inicial. Devuelve (bloque, cuerpo).

    Un frontmatter sin cierre es frontmatter inexistente, no un error: el
    documento se indexa igual, sin tags. Un `check` que rompiera la indexación
    por un `---` sin pareja enseñaría a la gente a no escribir frontmatter.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != _FENCE:
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() == _FENCE:
            # El cuerpo arranca en la primera línea con contenido: el frontmatter
            # es el preámbulo, y un blanco de separación no vuelve "no-título" a
            # la primera línea del documento.
            return lines[1:index], "\n".join(lines[index + 1 :]).lstrip("\n")
    return None, text


def body_text(text: str) -> str:
    """El documento sin su bloque `---` inicial (para leer el header)."""
    return split_frontmatter(text)[1]


def frontmatter_tags(text: str) -> list[str] | None:
    """Tags declaradas, o None si el documento no trae el campo.

    Contrato mínimo (D13): un solo campo, `tags`. Cualquier otra clave se
    ignora en silencio — el índice no las valida, y agregar reglas por clave
    sería inventar metadata que ningún comando consume.
    """
    block, _ = split_frontmatter(text)
    if block is None:
        return None
    for position, line in enumerate(block):
        if not line.strip().startswith(_TAGS_KEY):
            continue
        inline = _INLINE_RE.match(line.strip()[len(_TAGS_KEY) :].strip())
        if inline is not None:
            return _split_inline(inline.group(1))
        tags: list[str] = []
        for candidate in block[position + 1 :]:
            if not candidate.strip():
                continue
            if not candidate.startswith((" ", "\t")):
                break
            item = _ITEM_RE.match(candidate)
            if item is None:
                break
            tags.append(item.group(1).strip())
        return tags
    return None


def _split_inline(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _source_block(text: str) -> str:
    """El bloque `## Fuente` y nada más: leer prosa libre es juicio."""
    lines = body_text(text).splitlines()
    for position, line in enumerate(lines):
        if line.strip() == _SOURCE_HEADER:
            block = []
            for candidate in lines[position + 1 :]:
                if candidate.strip().startswith("##"):
                    break
                block.append(candidate)
            return "\n".join(block)
    return ""


def _dedupe(values: list[str]) -> tuple[str, ...]:
    seen: dict[str, None] = {}
    for value in values:
        token = value.strip().lower()
        if token:
            seen.setdefault(token, None)
    return tuple(seen)


def derive_tags(relative: Path, text: str) -> tuple[str, ...]:
    """Tags derivadas del nombre, sin intervención de LLM.

    Tres fuentes, todas mecánicas: la carpeta `HU-XX/` que contiene el
    documento (en este framework la identidad de un documento es su ruta, no
    su nombre de archivo), los tokens `snake_case` del stem, y la HU citada en
    `## Fuente`. Es el piso del índice: si nadie escribe frontmatter, el
    documento igual queda clasificable.
    """
    tags: list[str] = []
    for part in relative.parts:
        if _HU_DIR_RE.fullmatch(part):
            tags.append(part.lower())
    for token in _tokens(relative.stem):
        if token in _GENERIC_STEMS:
            continue
        tags.append(token)
    tags.extend(_HU_RE.findall(_source_block(text)))
    return _dedupe(tags)


def _tokens(stem: str) -> list[str]:
    """Tokens `snake_case` de un nombre de archivo, sin los numéricos.

    Se parta por `_`, `-` y `.` para que `audit_2026-09-24.prompt` dé
    `audit` y `prompt` en vez de un `24.prompt` que no es una palabra.
    """
    return [
        token
        for token in re.split(r"[_\-.]", stem.lower())
        if token and not _NUMERIC_RE.match(token)
    ]


def level_of(relative: Path) -> int:
    """Nivel derivado de la ruta, no declarado en el documento (D13)."""
    if relative == Path("project_state.md"):
        return _ROOT_LEVEL
    for layer, level in _LAYER_LEVELS:
        if relative.parts[: len(layer.parts)] == layer.parts:
            return level
    return _FALLBACK_LEVEL


def _state_and_date(text: str) -> tuple[str, str]:
    """Estado y fecha del header estándar. Vacíos si el documento no lo tiene.

    Solo se mira la forma que prescribe `doc.md.j2` y valida `header_capa1`:
    un header no estándar no se interpreta, se reporta como ausente.
    """
    body = body_text(text)
    state = _STATE_RE.search(body)
    date = _DATE_RE.search(body)
    return (
        state.group(1) if state is not None else "",
        date.group(1) if date is not None else "",
    )


def document(root: Path, path: Path) -> Document:
    """Metadata de un documento de `docs/`, lista para el índice."""
    relative = path.relative_to(root / DOCS_DIR)
    text = path.read_text(encoding="utf-8")
    declared = frontmatter_tags(text)
    tags = _dedupe(declared) if declared is not None else derive_tags(relative, text)
    state, date = _state_and_date(text)
    return Document(
        path=relative,
        level=level_of(relative),
        state=state,
        date=date,
        tags=tags,
        declared=declared is not None,
    )


def documents(root: Path) -> list[Document]:
    """Todos los documentos de `docs/`, ordenados por (nivel, ruta).

    El índice se excluye a sí mismo: incluirlo haría que regenerar cambiara el
    contenido del índice.
    """
    docs = root / DOCS_DIR
    if not docs.is_dir():
        return []
    index = index_path(root).resolve()
    found: list[Document] = []
    for path in docs.rglob("*.md"):
        if not path.is_file() or path.resolve() == index:
            continue
        found.append(document(root, path))
    return sorted(found, key=lambda item: (item.level, item.path.as_posix()))


def render_index(root: Path) -> tuple[Path, int]:
    """Regenera `docs/00_memory_index.md`. Devuelve (ruta, documentos)."""
    entries = documents(root)
    width = max(
        (len(item.path.as_posix()) for item in entries),
        default=0,
    )
    lines = [item.row(width) for item in entries]
    content = _environment().get_template("memory_index.md.j2").render(lines=lines)
    target = index_path(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target, len(entries)


def status(root: Path) -> IndexStatus:
    """Qué hay en el índice ahora, sin juzgar si está viejo."""
    entries = documents(root)
    target = index_path(root)
    exists = target.is_file()
    generated = (
        datetime.fromtimestamp(target.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        if exists
        else ""
    )
    return IndexStatus(
        path=target.relative_to(root),
        exists=exists,
        documents=len(entries),
        declared=sum(1 for item in entries if item.declared),
        derived=sum(1 for item in entries if not item.declared),
        generated_at=generated,
    )
