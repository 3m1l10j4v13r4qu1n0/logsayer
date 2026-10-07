from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from logsayer.cli import app
from logsayer.core import routing

runner = CliRunner()


def test_route_prints_full_table(cwd_project: Path) -> None:
    result = runner.invoke(app, ["doc", "route"])
    assert result.exit_code == 0, result.output
    for command in (
        "logsayer inbox add",
        "logsayer doc new technical",
        "logsayer doc new global",
        "logsayer spec new",
        "logsayer audit run",
        "logsayer log add",
    ):
        assert command in result.output
    assert "Nunca: un .md suelto en docs/" in result.output
    assert "El CLI no redacta el contenido" in result.output


def test_route_markdown_table_matches_readme(cwd_project: Path) -> None:
    """El README muestra la misma tabla que el core: no pueden divergir."""
    readme = (Path(__file__).parents[1] / "README.md").read_text(encoding="utf-8")
    for route in routing.ROUTES:
        assert route.trigger in readme, route.trigger
        assert route.command in readme, route.command


def test_route_does_not_decide_global_vs_technical(cwd_project: Path) -> None:
    """El CLI propone candidatos; no elige capa. El juicio es de Mentat."""
    result = runner.invoke(app, ["doc", "route", "inbox/contrato_api.md"])
    assert result.exit_code == 0, result.output
    assert "sin decisión automática" in result.output
    assert "02_technical" in result.output
    assert "01_global" in result.output
    assert "logsayer doc new technical" in result.output
    assert "logsayer doc new global" in result.output


def test_route_candidatos_no_repiten_la_capa(cwd_project: Path) -> None:
    """Los tres candidatos de Capa 1 van al mismo nivel: en la lista corta el
    prefijo '1 — Especificación →' repetido tres veces es ruido (el mismo que
    distingue de 'Capa 4 →' y 'Capa 3 →' en la tabla completa, donde sí va)."""
    result = runner.invoke(app, ["doc", "route", "inbox/contrato_api.md"])
    assert result.exit_code == 0, result.output
    candidatos = result.output.split("Candidatos:")[1]
    assert "1 — Especificación" not in candidatos
    assert "· docs/02_technical/ — crear con: logsayer doc new technical" in candidatos


def test_route_hints_technical_tokens_without_deciding(cwd_project: Path) -> None:
    result = runner.invoke(app, ["doc", "route", "inbox/contrato_api.md"])
    assert result.exit_code == 0, result.output
    assert "pista" in result.output
    assert "no lo decide el CLI" in result.output


def test_route_plain_name_has_no_hint(cwd_project: Path) -> None:
    result = runner.invoke(app, ["doc", "route", "inbox/notas.md"])
    assert result.exit_code == 0, result.output
    assert "sin decisión automática" in result.output
    assert "pista" not in result.output


def test_route_resolves_hu_specific_to_spec_new(cwd_project: Path) -> None:
    result = runner.invoke(app, ["doc", "route", "inbox/hu-07_criterios.md"])
    assert result.exit_code == 0, result.output
    assert "logsayer spec new" in result.output
    assert "sin decisión automática" not in result.output
    assert "declara una HU" in result.output


def test_route_detects_duplicate_of_existing_layer1_doc(cwd_project: Path) -> None:
    target = cwd_project / "docs" / "02_technical" / "contrato_api.md"
    target.write_text(
        "# Contrato\n\nFecha: 2026-09-25 · Estado: vigente\n\n## Resumen\n\nx\n",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["doc", "route", "inbox/contrato_api.md"])
    assert result.exit_code == 0, result.output
    assert "Ya existe un documento con ese nombre" in result.output
    assert "02_technical/contrato_api.md" in result.output
    assert "No lo dupliques" in result.output


def test_route_non_markdown_points_to_inbox(cwd_project: Path) -> None:
    result = runner.invoke(app, ["doc", "route", "inbox/contrato.pdf"])
    assert result.exit_code == 0, result.output
    assert "logsayer inbox add" in result.output
    assert "no;" in result.output


def test_doc_new_creates_header_and_sections(cwd_project: Path) -> None:
    result = runner.invoke(app, ["doc", "new", "technical", "contrato_api"])
    assert result.exit_code == 0, result.output
    target = cwd_project / "docs" / "02_technical" / "contrato_api.md"
    text = target.read_text(encoding="utf-8")
    assert text.startswith("---\n# Tags del índice de memoria (D13)")
    assert "tags:\n  - contrato\n  - api\n---\n" in text
    assert "# Contrato api\n" in text
    assert "Fecha: " in text and "Estado: borrador" in text
    assert "## Resumen" in text
    assert "## Qué establece" in text
    assert "## Cómo se valida" in text
    assert text.endswith("\n")
    assert "## Fuente" not in text


def test_doc_new_from_stages_and_archives_original(cwd_project: Path) -> None:
    outside = cwd_project.parent / "contrato.md"
    outside.write_text("# Contrato\n", encoding="utf-8")
    result = runner.invoke(
        app, ["doc", "new", "technical", "contrato_api", "--from", str(outside)]
    )
    assert result.exit_code == 0, result.output
    archived = cwd_project / "inbox" / "_done" / "contrato.md"
    assert archived.is_file()
    assert not outside.exists()
    text = (cwd_project / "docs" / "02_technical" / "contrato_api.md").read_text(
        encoding="utf-8"
    )
    assert "## Fuente" in text
    assert "`inbox/_done/contrato.md`" in text
    fuente = text.split("## Fuente")[1].split("## Qué establece")[0]
    assert "no se versiona" not in fuente


def test_doc_new_from_accepts_file_already_in_inbox(cwd_project: Path) -> None:
    outside = cwd_project.parent / "contrato.md"
    outside.write_text("# Contrato\n", encoding="utf-8")
    assert runner.invoke(app, ["inbox", "add", str(outside)]).exit_code == 0
    result = runner.invoke(
        app, ["doc", "new", "technical", "contrato_api", "--from", "inbox/contrato.md"]
    )
    assert result.exit_code == 0, result.output
    assert (cwd_project / "inbox" / "_done" / "contrato.md").is_file()


def test_doc_new_from_binary_keeps_conversion_note(cwd_project: Path) -> None:
    outside = cwd_project.parent / "acta.pdf"
    outside.write_bytes(b"%PDF-1.4\n")
    result = runner.invoke(
        app, ["doc", "new", "technical", "acta_reunion", "--from", str(outside)]
    )
    assert result.exit_code == 0, result.output
    text = (cwd_project / "docs" / "02_technical" / "acta_reunion.md").read_text(
        encoding="utf-8"
    )
    assert "Nota:" in text
    assert "no es markdown" in text
    assert "quedó archivado en `inbox/_done/`" in text


def test_doc_new_from_binary_warns_on_stdout(cwd_project: Path) -> None:
    """El aviso tenía que salir por stdout además de quedar en el documento:
    el que lo lee después es la Decidora, y quien lo pidió es el humano que
    acaba de tipear el comando (spec §3, D25, HU-14)."""
    outside = cwd_project.parent / "acta.pdf"
    outside.write_bytes(b"%PDF-1.4\n")
    result = runner.invoke(
        app, ["doc", "new", "technical", "acta_reunion", "--from", str(outside)]
    )
    assert result.exit_code == 0, result.output
    assert "Aviso: acta.pdf no es markdown" in result.output


def test_doc_new_from_markdown_does_not_warn(cwd_project: Path) -> None:
    """El aviso es del original no markdown: colgarlo a un `.md` sería ruido
    permanente, y un aviso que aparece siempre deja de avisar (D7)."""
    outside = cwd_project.parent / "contrato.md"
    outside.write_text("# Contrato\n", encoding="utf-8")
    result = runner.invoke(
        app, ["doc", "new", "technical", "contrato_api", "--from", str(outside)]
    )
    assert result.exit_code == 0, result.output
    assert "Aviso:" not in result.output


def test_doc_new_rejects_hu_layer(cwd_project: Path) -> None:
    result = runner.invoke(app, ["doc", "new", "hu", "HU-09"])
    assert result.exit_code != 0
    assert "logsayer spec new" in result.output


def test_doc_new_rejects_bad_name(cwd_project: Path) -> None:
    result = runner.invoke(app, ["doc", "new", "technical", "Mal Nombre"])
    assert result.exit_code != 0
    assert "Nombre inválido" in result.output


def test_doc_new_rejects_existing(cwd_project: Path) -> None:
    primero = runner.invoke(app, ["doc", "new", "technical", "contrato_api"])
    assert primero.exit_code == 0, primero.output
    result = runner.invoke(app, ["doc", "new", "technical", "contrato_api"])
    assert result.exit_code != 0
    assert "ya existe" in result.output


def test_doc_new_missing_from_file_errors_cleanly(cwd_project: Path) -> None:
    result = runner.invoke(
        app, ["doc", "new", "technical", "contrato_api", "--from", "no-existe.md"]
    )
    assert result.exit_code != 0
    assert "No existe el archivo" in result.output
    assert not (cwd_project / "docs" / "02_technical" / "contrato_api.md").exists()


def test_doc_role_alias_equivalent(cwd_project: Path) -> None:
    result = runner.invoke(app, ["mentat", "doc", "route"])
    assert result.exit_code == 0, result.output
    assert "logsayer spec new" in result.output


def test_help_lists_inbox_and_doc(cwd_project: Path) -> None:
    result = runner.invoke(app, ["--help"])
    assert "inbox" in result.output
    assert "doc" in result.output
