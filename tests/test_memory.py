from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from logsayer.cli import app
from logsayer.core import layers, memory, suk
from logsayer.core.memory import Document

runner = CliRunner()

HEADER = (
    "# Contrato api\n\n"
    "Fecha: 2026-09-28 · Estado: vigente\n\n"
    "## Resumen\n\n_Una línea._\n"
)

FRONTMATTER = (
    "---\n"
    "# Tags del índice de memoria (D13): el CLI las scaffoldea, el Mentat ajusta.\n"
    "tags:\n"
    "  - memoria\n"
    "  - retrieval\n"
    "---\n\n"
)


def _doc(root: Path, relative: str, content: str = HEADER) -> Path:
    path = root / "docs" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _tags(*names: str) -> str:
    block = "\n".join(f"  - {name}" for name in names)
    return f"---\ntags:\n{block}\n---\n\n"


def _lines(root: Path) -> list[str]:
    return [
        line
        for line in (root / "docs" / "00_memory_index.md")
        .read_text(encoding="utf-8")
        .splitlines()
        if line and not line.startswith(("#", "<!--"))
    ]


def _rows(root: Path) -> dict[str, str]:
    return {row.split("·")[0].strip(): row for row in _lines(root)}


def _paths(root: Path) -> list[str]:
    return [row.split("·")[0].strip() for row in _lines(root)]


def test_index_has_one_line_per_document(cwd_project: Path) -> None:
    _doc(cwd_project, "01_global/mission.md")
    _doc(cwd_project, "02_technical/contrato.md")
    _doc(cwd_project, "04_user_stories/HU-01/README.md", "# HU-01\n")
    _doc(cwd_project, "logbooks/logbook_fase1_01.md", "# Logbook\n")
    runner.invoke(app, ["memory", "index"])

    assert _paths(cwd_project) == [
        "01_global/mission.md",
        "project_state.md",
        "02_technical/contrato.md",
        "04_user_stories/HU-01/README.md",
        "logbooks/00_index.md",
        "logbooks/logbook_fase1_01.md",
    ]
    assert "docs/00_memory_index.md" not in _paths(cwd_project)


def test_index_excludes_itself(cwd_project: Path) -> None:
    runner.invoke(app, ["memory", "index"])
    first = (cwd_project / "docs" / "00_memory_index.md").read_text(encoding="utf-8")
    runner.invoke(app, ["memory", "index"])
    second = (cwd_project / "docs" / "00_memory_index.md").read_text(encoding="utf-8")
    assert first == second


def test_index_is_idempotent(cwd_project: Path) -> None:
    _doc(cwd_project, "02_technical/contrato.md")
    runner.invoke(app, ["memory", "index"])
    first = (cwd_project / "docs" / "00_memory_index.md").read_text(encoding="utf-8")
    runner.invoke(app, ["memory", "index"])
    assert first == (cwd_project / "docs" / "00_memory_index.md").read_text(
        encoding="utf-8"
    )


def test_index_reports_level_state_and_date(cwd_project: Path) -> None:
    _doc(cwd_project, "01_global/mission.md")
    _doc(cwd_project, "02_technical/contrato.md")
    _doc(cwd_project, "04_user_stories/HU-02/README.md", "# HU-02\n")
    _doc(cwd_project, "03_process/merge-checklist.md", "# Merge\n")
    _doc(cwd_project, "05_agile_methodology/metodologia.md", "# Metodología\n")
    _doc(cwd_project, "06_audits/audit_2026-09-28.md", "# Auditoría\n")
    _doc(cwd_project, "logbooks/logbook_fase8_01.md", "# Logbook\n")
    runner.invoke(app, ["memory", "index"])

    rows = _rows(cwd_project)
    assert "nivel 0" in rows["01_global/mission.md"]
    assert "nivel 0" in rows["project_state.md"]
    assert "nivel 1" in rows["02_technical/contrato.md"]
    assert "nivel 2" in rows["04_user_stories/HU-02/README.md"]
    for name in (
        "03_process/merge-checklist.md",
        "05_agile_methodology/metodologia.md",
        "06_audits/audit_2026-09-28.md",
        "logbooks/logbook_fase8_01.md",
    ):
        assert "nivel 3" in rows[name], name
    assert "vigente · 2026-09-28" in rows["02_technical/contrato.md"]
    assert "— · —" in rows["03_process/merge-checklist.md"]


def test_index_uses_declared_tags_and_derives_the_rest(cwd_project: Path) -> None:
    _doc(cwd_project, "02_technical/motor_de_memoria.md", FRONTMATTER + HEADER)
    _doc(cwd_project, "02_technical/contrato_api.md", HEADER)
    _doc(cwd_project, "04_user_stories/HU-03/README.md", "# HU-03\n")
    runner.invoke(app, ["memory", "index"])

    rows = _rows(cwd_project)
    assert rows["02_technical/motor_de_memoria.md"].endswith("memoria, retrieval")
    assert rows["02_technical/contrato_api.md"].endswith("contrato, api")
    assert rows["04_user_stories/HU-03/README.md"].endswith("hu-03")


def test_derived_tags_ignore_generic_and_numeric_tokens(cwd_project: Path) -> None:
    _doc(cwd_project, "06_audits/audit_2026-09-28.prompt.md", "# Auditoría\n")
    _doc(cwd_project, "logbooks/00_index.md", "| a | b |\n")
    runner.invoke(app, ["memory", "index"])

    rows = _rows(cwd_project)
    assert rows["06_audits/audit_2026-09-28.prompt.md"].endswith("audit, prompt")
    assert rows["logbooks/00_index.md"].rstrip().endswith("—")


def test_hu_referenced_in_source_block_becomes_a_tag(cwd_project: Path) -> None:
    content = (
        HEADER
        + "\n## Fuente\n\n"
        + "- Origen: `docs/04_user_stories/HU-07/README.md` (recibido el 2026-09-28)\n"
    )
    _doc(cwd_project, "01_global/alcance.md", content)
    runner.invoke(app, ["memory", "index"])
    assert _rows(cwd_project)["01_global/alcance.md"].endswith("alcance, hu-07")


def test_malformed_frontmatter_still_indexes(cwd_project: Path) -> None:
    """Un `---` sin pareja no es frontmatter: se indexa igual, sin tags.

    El Suk sí lo señala, y debe: un fence colgante deja al documento sin header
    estándar, y esconder eso sería delatar la duda con el chequeo.
    """
    _doc(cwd_project, "02_technical/contrato.md", "---\ntags:\n  - huvo\n" + HEADER)
    result = runner.invoke(app, ["memory", "index"])
    assert result.exit_code == 0
    assert _rows(cwd_project)["02_technical/contrato.md"].endswith("contrato")
    check = runner.invoke(app, ["check"])
    assert check.exit_code == 1
    assert "header_capa1" in check.output


def test_index_survives_doc_new(cwd_project: Path) -> None:
    result = runner.invoke(app, ["doc", "new", "technical", "motor_de_memoria"])
    assert result.exit_code == 0
    runner.invoke(app, ["memory", "index"])
    rows = _rows(cwd_project)
    assert rows["02_technical/motor_de_memoria.md"].endswith("motor, de, memoria")


def test_index_does_not_break_checks(cwd_project: Path) -> None:
    _doc(cwd_project, "01_global/mission.md")
    runner.invoke(app, ["memory", "index"])
    check = runner.invoke(app, ["check"])
    assert check.exit_code == 0, check.output
    assert "✔ capas_mezcladas" in check.output
    assert "✔ header_capa1" in check.output
    assert runner.invoke(app, ["process", "check"]).exit_code == 0


def test_layer1_header_check_tolerates_frontmatter(cwd_project: Path) -> None:
    _doc(cwd_project, "02_technical/contrato.md", FRONTMATTER + HEADER)
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "✔ header_capa1" in result.output


def test_layer1_header_check_still_requires_the_header(cwd_project: Path) -> None:
    _doc(cwd_project, "02_technical/contrato.md", FRONTMATTER + "sin header\n")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "'# Título'" in result.output


def test_status_reports_inventory_without_judging_freshness(
    cwd_project: Path,
) -> None:
    _doc(cwd_project, "02_technical/motor_de_memoria.md", FRONTMATTER + HEADER)
    _doc(cwd_project, "02_technical/contrato_api.md", HEADER)

    missing = runner.invoke(app, ["memory", "status"])
    assert missing.exit_code == 0
    assert "Todavía no existe" in missing.output
    assert "logsayer memory index" in missing.output

    runner.invoke(app, ["memory", "index"])
    report = runner.invoke(app, ["memory", "status"])
    assert report.exit_code == 0
    assert "docs/00_memory_index.md" in report.output
    assert "1 declaradas en frontmatter" in report.output
    assert "3 derivadas" in report.output
    assert "viejo" not in report.output


def test_status_works_without_docs_directory(tmp_path: Path) -> None:
    report = memory.status(tmp_path)
    assert report.exists is False
    assert report.documents == 0


def test_index_command_requires_a_project(plain_cwd: Path) -> None:
    result = runner.invoke(app, ["memory", "index"])
    assert result.exit_code != 0
    assert "logsayer.toml" in result.output


def test_memory_index_has_role_alias(cwd_project: Path) -> None:
    result = runner.invoke(app, ["navigator", "memory", "index"])
    assert result.exit_code == 0, result.output
    assert "Índice actualizado" in result.output


def test_every_layer_the_checks_know_has_a_level() -> None:
    """Ninguna capa puede quedar sin nivel sin que nadie lo note.

    El set está cerrado a propósito: si `suk` gana una capa nueva y el índice no
    la conhece, el test falla acá y no en el índice de un proyecto real.
    """
    expected = {
        "01_global": 0,
        "02_technical": 1,
        "04_user_stories": 2,
        "03_process": 3,
        "05_agile_methodology": 3,
        "06_audits": 3,
        "logbooks": 3,
    }
    known = {layer.name for layer in suk.LAYERED_MD_DIRS}
    assert known == set(expected)
    for layer in suk.LAYERED_MD_DIRS:
        probe = layer.relative_to("docs") / "doc.md"
        assert memory.level_of(probe) == expected[layer.name], layer.name
    assert memory.level_of(Path("project_state.md")) == 0


def test_every_layer_is_reachable_by_capa() -> None:
    """`--capa` no puede dejar una capa fuera: el alias apunta a la taxonomía."""
    assert set(memory._LAYER_ALIASES.values()) <= set(layers.ALL)
    for layer in layers.ALL:
        assert memory.resolve_capa(layer) == layer
    assert memory.resolve_capa("04_user_stories") == layers.STORIES


def test_unknown_capa_is_rejected() -> None:
    with pytest.raises(memory.MemoryError):
        memory.resolve_capa("no-existe")


def test_index_row_round_trips_through_the_parser(cwd_project: Path) -> None:
    """`parse_index` es el otro lado de `Document.row`, y tiene que serlo exacto.

    Si el artefacto y su parser se desalinean, el retrieval deja de devolver
    lo que el índice muestra — y nada en el flujo se entera.
    """
    _doc(cwd_project, "02_technical/motor_de_memoria.md", FRONTMATTER + HEADER)
    _doc(cwd_project, "04_user_stories/HU-03/README.md", "# HU-03\n")
    _doc(cwd_project, "03_process/merge-checklist.md", "# Merge\n")
    runner.invoke(app, ["memory", "index"])

    from_disk = memory.documents(cwd_project)
    from_index = memory.load_index(cwd_project)
    assert from_index == [
        Document(
            path=item.path,
            level=item.level,
            state=item.state,
            date=item.date,
            tags=item.tags,
        )
        for item in from_disk
    ]


def test_search_ranks_the_document_that_declares_the_tag(cwd_project: Path) -> None:
    """El criterio de validación del diseño: gana el que declara la tag."""
    _doc(cwd_project, "02_technical/motor_de_memoria.md", FRONTMATTER + HEADER)
    _doc(cwd_project, "02_technical/contrato_api.md", HEADER)
    _doc(cwd_project, "06_audits/audit_2026-09-28.md", "# Auditoría\n")
    runner.invoke(app, ["memory", "index"])

    hits = memory.search(cwd_project, "motor de memoria")
    assert [hit.document.path.as_posix() for hit in hits] == [
        "02_technical/motor_de_memoria.md"
    ]
    assert hits[0].matched == ("memoria",)
    assert hits[0].score == memory._EXACT


def test_search_breaks_ties_by_level_then_path(cwd_project: Path) -> None:
    """A igual puntaje, primero lo más cercano a la especificación.

    Es el mismo orden con el que se lee el índice: los dos artefactos tienen que
    leerse como las mismas capas.
    """
    _doc(cwd_project, "01_global/memoria.md", HEADER)
    _doc(cwd_project, "06_audits/memoria.md", "# Memoria\n")
    _doc(cwd_project, "04_user_stories/HU-01/memoria.md", "# Memoria\n")
    runner.invoke(app, ["memory", "index"])

    hits = memory.search(cwd_project, "memoria")
    assert [(hit.document.level, hit.document.path.as_posix()) for hit in hits] == [
        (0, "01_global/memoria.md"),
        (2, "04_user_stories/HU-01/memoria.md"),
        (3, "06_audits/memoria.md"),
    ]


def test_search_prefers_an_exact_match_over_a_prefix(cwd_project: Path) -> None:
    _doc(cwd_project, "02_technical/contrato.md", _tags("mem") + HEADER)
    _doc(cwd_project, "02_technical/arquitectura.md", _tags("memoria") + HEADER)
    runner.invoke(app, ["memory", "index"])

    hits = memory.search(cwd_project, "memoria")
    assert [hit.document.path.as_posix() for hit in hits] == [
        "02_technical/arquitectura.md",
        "02_technical/contrato.md",
    ]


def test_search_tolerates_accents_and_case(cwd_project: Path) -> None:
    _doc(cwd_project, "06_audits/auditoria_2026-09-28.md", "# Auditoría\n")
    runner.invoke(app, ["memory", "index"])

    for query in ("Auditoría", "auditoria"):
        assert [
            hit.document.path.as_posix() for hit in memory.search(cwd_project, query)
        ] == ["06_audits/auditoria_2026-09-28.md"]


def test_search_ignores_stopwords_and_repeated_tokens(cwd_project: Path) -> None:
    """Sin stopwords, "de" puntúa como "memoria" y el ranking no significa nada."""
    _doc(cwd_project, "02_technical/memoria.md", _tags("de") + HEADER)
    _doc(cwd_project, "02_technical/arquitectura.md", _tags("memoria") + HEADER)
    runner.invoke(app, ["memory", "index"])

    hits = memory.search(cwd_project, "de la memoria")
    assert [hit.document.path.as_posix() for hit in hits] == [
        "02_technical/arquitectura.md"
    ]
    assert memory.query_tokens("memoria memoria") == ("memoria",)


def test_search_never_crosses_the_capa_filter(cwd_project: Path) -> None:
    _doc(cwd_project, "02_technical/memoria.md", _tags("memoria") + HEADER)
    _doc(cwd_project, "04_user_stories/HU-04/memoria.md", "# Memoria\n")
    _doc(cwd_project, "project_state.md", HEADER)
    runner.invoke(app, ["memory", "index"])

    hits = memory.search(cwd_project, "memoria", capa="technical")
    assert [hit.document.path.as_posix() for hit in hits] == [
        "02_technical/memoria.md"
    ]
    assert memory.search(cwd_project, "hu-04", capa="stories")


def test_search_reads_the_artifact_and_not_the_disk(cwd_project: Path) -> None:
    """El retriever no regenera: ve lo que el índice dice, vieja o no.

    Si leyera los archivos, `indice_al_dia` no detectaría nada y el artefacto
    sería decorativo. La consecuencia honesta es que hay que reindexar para que
    un documento nuevo sea encontrable — y para eso está el check.
    """
    _doc(cwd_project, "02_technical/memoria.md", _tags("memoria") + HEADER)
    runner.invoke(app, ["memory", "index"])
    _doc(cwd_project, "02_technical/retrieval.md", _tags("retrieval") + HEADER)

    assert not memory.search(cwd_project, "retrieval")
    runner.invoke(app, ["memory", "index"])
    assert memory.search(cwd_project, "retrieval")


def test_search_needs_the_index(cwd_project: Path) -> None:
    with pytest.raises(memory.MemoryError) as excinfo:
        memory.search(cwd_project, "memoria")
    assert "logsayer memory index" in str(excinfo.value)


def test_search_query_of_only_stopwords_returns_nothing(cwd_project: Path) -> None:
    _doc(cwd_project, "01_global/mision.md", HEADER)
    runner.invoke(app, ["memory", "index"])
    assert memory.search(cwd_project, "de la y el") == []


def test_search_limit_zero_returns_everything(cwd_project: Path) -> None:
    for name in ("a", "b", "c"):
        _doc(cwd_project, f"06_audits/audit_{name}.md", "# A\n")
    runner.invoke(app, ["memory", "index"])
    assert len(memory.search(cwd_project, "audit", limit=0)) == 3
    assert len(memory.search(cwd_project, "audit", limit=2)) == 2


def test_search_command_lists_ranked_candidates(cwd_project: Path) -> None:
    _doc(cwd_project, "02_technical/motor_de_memoria.md", FRONTMATTER + HEADER)
    _doc(cwd_project, "02_technical/contrato_api.md", HEADER)
    runner.invoke(app, ["memory", "index"])

    result = runner.invoke(app, ["memory", "search", "motor de memoria"])
    assert result.exit_code == 0, result.output
    assert "1 de" in result.output
    assert "02_technical/motor_de_memoria.md" in result.output
    assert "02_technical/contrato_api.md" not in result.output


def test_search_command_reports_no_match(cwd_project: Path) -> None:
    runner.invoke(app, ["memory", "index"])
    result = runner.invoke(app, ["memory", "search", "nada de esto existe"])
    assert result.exit_code == 0, result.output
    assert "Sin coincidencias" in result.output
    assert "fremen verify" in result.output


def test_search_command_rejects_unknown_capa(cwd_project: Path) -> None:
    runner.invoke(app, ["memory", "index"])
    result = runner.invoke(app, ["memory", "search", "memoria", "--capa", "nada"])
    assert result.exit_code != 0
    assert "Capa desconocida" in result.output


def test_search_command_requires_a_project(plain_cwd: Path) -> None:
    result = runner.invoke(app, ["memory", "search", "memoria"])
    assert result.exit_code != 0
    assert "logsayer.toml" in result.output


def test_search_has_role_alias(cwd_project: Path) -> None:
    _doc(cwd_project, "01_global/mision.md", HEADER)
    runner.invoke(app, ["memory", "index"])
    result = runner.invoke(app, ["navigator", "memory", "search", "mision"])
    assert result.exit_code == 0, result.output
    assert "01_global/mision.md" in result.output


def test_search_matches_hyphenated_tags(cwd_project: Path) -> None:
    """`hu-04` es una tag del índice y también la consulta más natural.

    Partir la consulta por guion convertía la búsqueda de una HU en dos
    tokens que no matcheaban nada.
    """
    _doc(cwd_project, "04_user_stories/HU-04/README.md", "# HU-04\n")
    runner.invoke(app, ["memory", "index"])
    assert memory.query_tokens("HU-04") == ("hu-04",)
    assert [
        hit.document.path.as_posix()
        for hit in memory.search(cwd_project, "hu-04", capa="stories")
    ] == ["04_user_stories/HU-04/README.md"]
