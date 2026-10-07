"""Auditoría spec-vs-código (Capa 4 — Decidora de Verdad).

El CLI genera la estructura del reporte y el prompt; el resultado lo produce el
subagente que ejecuta la auditoría (spec §10: no prometer resultado
determinístico).

El alcance de la auditoría lo decide el disco, no el agente: `hu_worklist`
enumera `docs/04_user_stories/HU-*/` y el reporte se scaffoldea con una fila
por HU. La Decidora llena celdas, no decide cuáles filas existen. Es la
traducción mecánica de D14 —"el retrieval elige qué leer primero, nunca qué es
auditable"— a un artefacto que se puede diffear sin LLM.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from logsayer.core.freshness import doc_timestamp
from logsayer.core.layers import STORIES
from logsayer.core.project import project_name, read_closed_hus

AUDITS_DIR = Path("docs") / "06_audits"
HU_DIR = Path("docs") / STORIES

# Rutas que toda pasada recibe, más allá de lo que la HU cite. Sin base fija,
# una HU sin citas arrancaría ciega; con base fija, la extracción de citas es
# una mejora y no un requisito (D20).
BASE_FILES: tuple[Path, ...] = (
    Path("docs") / "01_global" / "mission.md",
    Path("docs") / "project_state.md",
)

# Raíces contra las que se resuelve una ruta citada. Una HU escribe
# `core/memory.py`, no `src/logsayer/core/memory.py`: el prefijo es lo que el
# autor se ahorra de repetir. Sin este catálogo, la extracción marcaría como
# muerta casi toda cita real.
CITATION_ROOTS: tuple[str, ...] = (
    "",
    "docs/",
    "src/logsayer/",
    "src/logsayer/adapters/",
    "src/logsayer/templates/",
    "src/logsayer/templates/adapters/opencode/",
    "src/logsayer/templates/adapters/claude/",
    "inbox/_done/",
)

# Citas que no cuentan como cambio. `project_state.md` se reescribe en cada
# cierre de sesión: es ritual de coordinación, no requisito, y contarlo
# invalidaría para siempre el veredicto de toda HU que lo menciona. Es el mismo
# error que D19 corrige para `indice_al_dia`.
NON_SPEC_CITATIONS: frozenset[str] = frozenset({"docs/project_state.md"})

# Solo rutas con extensión y prefijo de archivo. "la spec de memoria" es
# interpretación, no parsing (D20).
_CITED_RE = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|toml|j2))`")
_HU_RE = re.compile(r"^HU-\d+$")
_EMPTY = "—"
_ROW_RE = re.compile(r"^\|\s*(HU-\d+)\s*\|\s*([^|]*?)\s*\|")
_REPORT_DATE_RE = re.compile(r"^audit_(\d{4}-\d{2}-\d{2})")


class AuditError(Exception):
    """Error controlado de auditoría."""


@dataclass(frozen=True)
class HuItem:
    """Una HU del alcance: qué hay que leer y si su veredicto sigue en pie.

    `readme` y `cites` son relativas a la raíz del proyecto: una ruta absoluta
    ata el prompt a la máquina donde se generó, y la Decidora no necesita saber
    dónde está el repo para leer un archivo.
    """

    hu: str
    readme: Path
    cites: tuple[Path, ...]
    dead_cites: tuple[str, ...]
    ambiguous_cites: tuple[str, ...]
    unchanged: bool
    reason: str
    has_readme: bool = True

    @property
    def verdict_cell(self) -> str:
        """Veredicto prellenado por el CLI, si la HU puede heredarse."""
        return _EMPTY if not self.unchanged else "sin cambios"

    def row(self) -> str:
        return f"| {self.hu} | {self.verdict_cell} | {_EMPTY} |"

    def brief(self) -> list[str]:
        """Input de una pasada, como lo ve la Decidora."""
        if not self.has_readme:
            return [
                f"No hay README en `{self.readme.parent.as_posix()}/`: esta HU "
                "no tiene spec que auditar. Anotá la falta en el reporte.",
            ]
        base = [path.as_posix() for path in (*BASE_FILES, self.readme)]
        lines = [f"Base fija: {', '.join(f'`{path}`' for path in base)}"]
        if self.cites:
            cited = ", ".join(f"`{path.as_posix()}`" for path in self.cites)
            lines.append(f"Rutas citadas: {cited}")
        else:
            lines.append(
                "Rutas citadas: ninguna (puede ser correcto o una HU mal "
                "escrita; la pasada corre igual con la base fija)"
            )
        if self.dead_cites:
            lines.append(
                "Rutas citadas que NO existen en disco: "
                + ", ".join(f"`{path}`" for path in self.dead_cites)
            )
        if self.ambiguous_cites:
            lines.append(
                "Rutas citadas ambiguas (resuelven a más de un archivo, "
                "alcanzá la que corresponda): "
                + ", ".join(f"`{path}`" for path in self.ambiguous_cites)
            )
        if self.reason and not self.unchanged:
            lines.append(f"Pendiente: {self.reason}.")
        return lines


def _render(template: str, **context: object) -> str:
    env = Environment(
        loader=PackageLoader("logsayer", "templates"),
        autoescape=select_autoescape(("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env.get_template(template).render(**context)


def _next_report_path(root: Path, date: str) -> Path:
    audits_dir = root / AUDITS_DIR
    audits_dir.mkdir(parents=True, exist_ok=True)
    counter = 0
    while True:
        suffix = "" if counter == 0 else f"-{counter}"
        candidate = audits_dir / f"audit_{date}{suffix}.md"
        if not candidate.exists():
            return candidate
        counter += 1


def _report_date(path: Path) -> str:
    match = _REPORT_DATE_RE.match(path.name)
    return match.group(1) if match else path.stem


def last_audit(root: Path) -> Path | None:
    return _latest(root, sealed_only=False)


def sealed_audit(root: Path) -> Path | None:
    """El reporte más reciente que tiene veredictos, si hay alguno.

    Distinguir esto de `last_audit` no es un detalle: `audit run` scaffoldea un
    reporte vacío, y si esevuclo fuera "el previo", una sola corrida borraría
    toda la herencia que el trabajo anterior había ganado. Un andamiaje no
    dice nada sobre la cobertura, así que no sella. El reporte más reciente
    sigue siendo el que se mide; el que sella es el más reciente con opinión.
    """
    return _latest(root, sealed_only=True)


def _latest(root: Path, *, sealed_only: bool) -> Path | None:
    audits_dir = root / AUDITS_DIR
    if not audits_dir.is_dir():
        return None
    reports = sorted(
        (
            path
            for path in audits_dir.glob("audit_*.md")
            if not path.name.endswith(".prompt.md")
        ),
        reverse=True,
    )
    for report in reports:
        if not sealed_only:
            return report
        text = report.read_text(encoding="utf-8")
        if has_worklist(text) and parse_verdicts(text):
            return report
    return None


def hu_ids(root: Path) -> list[str]:
    """Las HUs del disco, ordenadas. El alcance no se deduce: se cuenta."""
    stories = root / HU_DIR
    if not stories.is_dir():
        return []
    return sorted(
        path.name
        for path in stories.glob("HU-*")
        if path.is_dir() and _HU_RE.fullmatch(path.name)
    )


def cited_paths(
    root: Path, readme: Path
) -> tuple[tuple[Path, ...], tuple[str, ...], tuple[str, ...]]:
    """Rutas que la HU nombra entre backticks: (resueltas, muertas, ambiguas).

    Solo dependencias directas. Los `## Fuente` de los docs citados no se
    siguen: si se sigieran, el contexto volvería a crecer con el grafo y la
    pasada perdería su cota (D20).

    Una cita que resuelve a más de un archivo no se elige al azar. `mentat.md.j2`
    existe en `adapters/opencode/` y en `adapters/claude/`, y elegir el primero
    puede mandar a la Decidora a auditar el archivo equivocado con toda
    confianza. Se reporta como ambigua y no se resuelve.

    Una HU sin README no tiene nada que extraer y no es un error de la auditoría:
    el directorio existe y por eso está en el alcance, con su hueco adentro.
    """
    if not readme.is_file():
        return (), (), ()
    text = readme.read_text(encoding="utf-8")
    resolved: list[Path] = []
    dead: list[str] = []
    ambiguous: list[str] = []
    for cited in sorted(set(_CITED_RE.findall(text))):
        hits = [
            Path(f"{prefix}{cited}")
            for prefix in CITATION_ROOTS
            if (root / f"{prefix}{cited}").exists()
        ]
        if not hits:
            dead.append(cited)
        elif len(hits) > 1:
            ambiguous.append(cited)
        else:
            resolved.append(hits[0])
    return tuple(resolved), tuple(dead), tuple(ambiguous)


@dataclass(frozen=True)
class _Seal:
    """Lo que un reporte previo sella: qué cubrió y hasta cuándo.

    Un reporte sin worklist no sella nada (covered vacío, sello `None`): los
    anteriores a la fase 9 listan las HUs en prosa, y leer prosa para decidir
    qué está cubierto es exactamente el parsing que la fase 9 evita. Sin
    herencia y a re-auditar: la respuesta conservadora ante un artefacto de
    formato desconocido.
    """

    covered: frozenset[str] = frozenset()
    ts: float | None = None
    date: str | None = None
    source: Path | None = None


def _seal_of(root: Path, report: Path | None) -> _Seal:
    if report is None or not report.is_file():
        return _Seal()
    text = report.read_text(encoding="utf-8")
    if not has_worklist(text):
        return _Seal()
    return _Seal(
        covered=frozenset(parse_verdicts(text)),
        ts=doc_timestamp(root, report),
        date=_report_date(report),
        source=report,
    )


def parse_verdicts(text: str) -> dict[str, str]:
    """Filas de la tabla de ítems que ya tienen veredicto.

    Es el inverso exacto de `HuItem.row()`: el CLI escribe la tabla y la relee
    igual, así que el check mide cobertura real y no formato Kerberos.
    """
    verdicts: dict[str, str] = {}
    for line in text.splitlines():
        match = _ROW_RE.match(line)
        if match and match.group(2) not in ("", _EMPTY):
            verdicts[match.group(1)] = match.group(2)
    return verdicts


def has_worklist(text: str) -> bool:
    """Si el reporte trae la tabla de ítems que el CLI scaffoldea.

    Los reportes anteriores a la fase 9 no la tienen: la Decidora escribía una
    lista con viñetas. Medirlos con la métrica de cobertura daría un hueco
    falso, así que un reporte sin worklist no se mide.
    """
    return any(_ROW_RE.match(line) for line in text.splitlines())


def hu_worklist(root: Path, report: Path | None = None) -> list[HuItem]:
    """El alcance de la auditoría: una fila por HU del disco (D20).

    "Sin cambios" es una herencia condicionada, no un atajo: solo se concede si
    la HU ya fue auditada, su README es anterior al reporte que selló, y ninguna
    ruta que cita cambió desde entonces. `project_state.md` queda fuera de la
    comparación (D21).
    """
    seal = _seal_of(root, report if report is not None else sealed_audit(root))
    return [_item_for(root, hu, seal) for hu in hu_ids(root)]


def _item_for(root: Path, hu: str, seal: _Seal) -> HuItem:
    readme = Path(*HU_DIR.parts, hu, "README.md")
    if not (root / readme).is_file():
        readme = Path(*HU_DIR.parts, f"{hu}.md")
    cites, dead, ambiguous = cited_paths(root, root / readme)
    cites = tuple(path for path in cites if path != readme)
    has_readme = (root / readme).is_file()
    unchanged, reason = _may_inherit(root, hu, readme, cites, dead, ambiguous, seal)
    return HuItem(
        hu=hu,
        readme=readme,
        cites=cites,
        dead_cites=dead,
        ambiguous_cites=ambiguous,
        unchanged=unchanged,
        reason=reason,
        has_readme=has_readme,
    )


def _may_inherit(
    root: Path,
    hu: str,
    readme: Path,
    cites: tuple[Path, ...],
    dead_cites: tuple[str, ...],
    ambiguous_cites: tuple[str, ...],
    seal: _Seal,
) -> tuple[bool, str]:
    if hu not in seal.covered:
        if last_audit(root) is None:
            return False, "nunca auditada"
        if seal.source is None:
            return False, "ningún reporte previo selló worklist, sin herencia"
        return False, "sin veredicto en el reporte que selló"
    if seal.ts is None or not (root / readme).is_file():
        return False, "el directorio de la HU no tiene README"
    if doc_timestamp(root, root / readme) > seal.ts:
        return False, "README modificado desde el reporte previo"
    if dead_cites:
        listed = ", ".join(dead_cites)
        return False, f"cita una ruta que no existe: {listed}"
    if ambiguous_cites:
        listed = ", ".join(ambiguous_cites)
        return False, f"cita una ruta ambigua: {listed}"
    touched = [
        path
        for path in cites
        if path.as_posix() not in NON_SPEC_CITATIONS
        and doc_timestamp(root, root / path) > seal.ts
    ]
    if touched:
        listed = ", ".join(path.as_posix() for path in touched)
        return False, f"cambió lo que cita: {listed}"
    return True, f"sin cambios desde el reporte del {seal.date}"


def pending_verdicts(root: Path, report: Path | None = None) -> list[str]:
    """HUs del alcance cuya fila sigue vacía en el reporte.

    Lo que el check de cobertura mide: si el disco tiene N HUs y el reporte
    tiene N filas con veredicto. Un hueco acá es una auditoría que pasó por
    omisión (D14).

    Devuelve `[]` si el reporte no trae worklist: no se mide cobertura con una
    métrica que el artefacto no adoptó.
    """
    target = report if report is not None else last_audit(root)
    if target is None or not target.is_file():
        return []
    text = target.read_text(encoding="utf-8")
    if not has_worklist(text):
        return []
    covered = parse_verdicts(text)
    return [hu for hu in hu_ids(root) if hu not in covered]


@dataclass(frozen=True)
class DerivedCounter:
    """Las HUs que el disco tiene y el reporte que selló no opinó.

    Es el reverso de `read_closed_hus()`, que lee un número que alguien
    escribió a mano. El derivado no mira el estado: cuenta los directorios
    `HU-*` sin veredicto en el reporte sellado, así que el desfase entre lo
    declarado y lo real es medible sin que nadie lo afirme.
    """

    hus: tuple[str, ...]
    source: Path

    @property
    def count(self) -> int:
        return len(self.hus)


def derived_closed_hus(root: Path) -> DerivedCounter | None:
    """Contador de HUs derivado del disco, o `None` si no se puede derivar.

    `None` no es "cero": es la ausencia del denominador. Sin un reporte con
    worklist no hay auditoría de la que "desde" medir, y un reporte en prosa
    —los anteriores a la fase 9— no dice cuáles HUs cubrió sin parsear prosa,
    que es justo lo que la tabla de alcance evita. Ante esa falta de dato la
    respuesta no es "todas las HUs están sin auditar" sino "no se mide": la
    alternativa daría un aviso permanente en todo proyecto con HUs que nunca
    se auditó, y un aviso permanente no avisa.
    """
    report = sealed_audit(root)
    if report is None:
        return None
    covered = parse_verdicts(report.read_text(encoding="utf-8"))
    return DerivedCounter(
        hus=tuple(hu for hu in hu_ids(root) if hu not in covered),
        source=report,
    )


def run_audit(root: Path, only: str | None = None) -> Path:
    """Genera el reporte y el prompt de auditoría para la Decidora.

    Devuelve el artefacto principal: el reporte en la corrida completa, el
    prompt de la pasada en la repetida.

    `only` emite el brief de una sola HU, que es como se repite una pasada que
    falló. No escribe reporte a propósito: un reporte con una fila se volvería
    el "reporte previo" y dejaría al resto del alcance sin cubrir, que es
    exactamente el fallo que D14 cierra. Un brief es un artefacto desechable,
    no un estado.
    """
    date = datetime.now().strftime("%Y-%m-%d")
    if only is not None:
        item = hu_ids_item(root, only)
        current = last_audit(root)
        return _write_prompt(
            root,
            date,
            f"audit_{date}-{only.lower()}",
            [item],
            report_name=current.name if current is not None else None,
            single=True,
        )

    previous = last_audit(root)
    report = _next_report_path(root, date)
    items = hu_worklist(root, sealed_audit(root))
    report.write_text(
        _render(
            "audit_report.md.j2",
            date=date,
            project_name=project_name(root),
            closed_hus=read_closed_hus(root),
            items=items,
            previous=_report_date(previous) if previous else None,
        )
    )
    _write_prompt(root, date, report.stem, items, report_name=report.name)
    return report


def hu_ids_item(root: Path, hu: str) -> HuItem:
    """El ítem de una HU puntual, para repetir una pasada aislada."""
    if hu not in hu_ids(root):
        raise AuditError(
            f"La HU {hu} no está en el alcance de {HU_DIR.as_posix()}/."
        )
    return _item_for(root, hu, _seal_of(root, sealed_audit(root)))


def _write_prompt(
    root: Path,
    date: str,
    stem: str,
    items: list[HuItem],
    report_name: str | None = None,
    single: bool = False,
) -> Path:
    audits_dir = root / AUDITS_DIR
    audits_dir.mkdir(parents=True, exist_ok=True)
    prompt = audits_dir / f"{stem}.prompt.md"
    prompt.write_text(
        _render(
            "audit_prompt.md.j2",
            date=date,
            project_name=project_name(root),
            items=items,
            report_name=report_name,
            single=single,
        )
    )
    return prompt
