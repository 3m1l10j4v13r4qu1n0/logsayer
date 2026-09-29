"""El worklist de auditoría: alcance, herencia y cobertura (D20, D21)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from logsayer.core import audit
from logsayer.core.suk import check_audit_coverage

HU = "docs/04_user_stories/HU-01/README.md"
AU = "docs/06_audits"


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True
    )


def _commit(root: Path, message: str) -> None:
    _git(root, "add", "-A")
    _git(root, "commit", "-m", message)


@pytest.fixture
def repo(cwd_project: Path) -> Path:
    _git(cwd_project, "init", "-q")
    _git(cwd_project, "config", "user.email", "t@t")
    _git(cwd_project, "config", "user.name", "t")
    _commit(cwd_project, "init")
    return cwd_project


def _hu(root: Path, name: str = "HU-01") -> str:
    directory = root / "docs/04_user_stories" / name
    directory.mkdir(parents=True, exist_ok=True)
    readme = directory / "README.md"
    readme.write_text(f"# {name}\n", encoding="utf-8")
    return f"docs/04_user_stories/{name}/README.md"


def _cite(root: Path, readme: str, *paths: str) -> None:
    target = root / readme
    target.write_text(
        target.read_text(encoding="utf-8") + "\n"
        + "\n".join(f"- Cita: `{path}`" for path in paths)
        + "\n",
        encoding="utf-8",
    )


def _reports(root: Path) -> list[str]:
    """Solo reportes: los `.prompt.md` también matchean `audit_*.md`."""
    return sorted(
        path.name
        for path in (root / AU).glob("audit_*.md")
        if not path.name.endswith(".prompt.md")
    )


def _seal(root: Path, verdicts: dict[str, str], date: str = "2026-09-27") -> Path:
    """Un reporte con worklist ya opinado, para probar la herencia."""
    report = root / AU / f"audit_{date}.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(f"| {hu} | {v} | ev |" for hu, v in verdicts.items())
    report.write_text(
        f"# Auditoría {date}\n\n| HU | Veredicto | Evidencia |\n"
        f"| --- | --- | --- |\n{rows}\n",
        encoding="utf-8",
    )
    return report


class TestWorklist:
    def test_el_alcance_lo_decide_el_disco(self, repo: Path) -> None:
        for hu in ("HU-01", "HU-02", "HU-07"):
            _hu(repo, hu)
        assert audit.hu_ids(repo) == ["HU-01", "HU-02", "HU-07"]
        assert [item.hu for item in audit.hu_worklist(repo)] == [
            "HU-01",
            "HU-02",
            "HU-07",
        ]

    def test_ignora_directorios_que_no_son_hus(self, repo: Path) -> None:
        (repo / "docs/04_user_stories/template").mkdir(parents=True)
        (repo / "docs/04_user_stories/HU-1b").mkdir(parents=True)
        assert audit.hu_ids(repo) == []

    def test_cada_fila_lleva_una_hu(self, repo: Path) -> None:
        _hu(repo)
        report = audit.run_audit(repo)
        text = report.read_text(encoding="utf-8")
        assert "| HU-01 |" in text
        assert "sin cambios" not in text


class TestCitas:
    def test_resuelve_prefijo_corto(self, repo: Path) -> None:
        readme = _hu(repo)
        (repo / "src/logsayer/core").mkdir(parents=True, exist_ok=True)
        (repo / "src/logsayer/core/audit.py").write_text("x\n", encoding="utf-8")
        _cite(repo, readme, "logsayer.toml", "core/audit.py")
        cites, dead, _ = audit.cited_paths(repo, repo / readme)
        assert [p.as_posix() for p in cites] == [
            "src/logsayer/core/audit.py",
            "logsayer.toml",
        ]
        assert dead == ()

    def test_reporta_ruta_muerta_sin_adivinarla(self, repo: Path) -> None:
        readme = _hu(repo)
        _cite(repo, readme, "no_existe.md")
        cites, dead, _ = audit.cited_paths(repo, repo / readme)
        assert cites == ()
        assert dead == ("no_existe.md",)

    def test_no_sigue_las_fuentes_de_lo_que_cita(self, repo: Path) -> None:
        """Las citas son directas: seguir el grafo rompe la cota de la pasada."""
        readme = _hu(repo)
        spec = repo / "logsayer.toml"
        spec.write_text(
            spec.read_text(encoding="utf-8") + "\n## Fuente\n- `docs/00_index.md`\n",
            encoding="utf-8",
        )
        _cite(repo, readme, "logsayer.toml")
        cites, _, _ = audit.cited_paths(repo, repo / readme)
        assert [p.as_posix() for p in cites] == ["logsayer.toml"]

    def test_una_cita_ambigua_no_se_elige_al_azar(self, repo: Path) -> None:
        """Elegir el primer hit puede mandar a la Decidora al archivo
        equivocado con toda confianza: se reporta en vez de adivinar."""
        readme = _hu(repo)
        for adapter in ("opencode", "claude"):
            path = repo / f"src/logsayer/templates/adapters/{adapter}"
            path.mkdir(parents=True, exist_ok=True)
            (path / "mentat.md.j2").write_text("x\n", encoding="utf-8")
        _cite(repo, readme, "mentat.md.j2")
        cites, dead, ambiguous = audit.cited_paths(repo, repo / readme)
        assert cites == ()
        assert dead == ()
        assert ambiguous == ("mentat.md.j2",)

    def test_una_cita_ambigua_no_hereda(self, repo: Path) -> None:
        readme = _hu(repo)
        for adapter in ("opencode", "claude"):
            path = repo / f"src/logsayer/templates/adapters/{adapter}"
            path.mkdir(parents=True, exist_ok=True)
            (path / "mentat.md.j2").write_text("x\n", encoding="utf-8")
        _cite(repo, readme, "mentat.md.j2")
        _commit(repo, "hu")
        _seal(repo, {"HU-01": "cumple"})
        _commit(repo, "auditoria")
        item = audit.hu_worklist(repo)[0]
        assert not item.unchanged
        assert "ambigua" in item.reason
        assert item.ambiguous_cites == ("mentat.md.j2",)

    def test_deduplica(self, repo: Path) -> None:
        readme = _hu(repo)
        _cite(repo, readme, "logsayer.toml", "logsayer.toml")
        cites, _, _ = audit.cited_paths(repo, repo / readme)
        assert len(cites) == 1


class TestHerencia:
    def test_sin_reporte_previo_no_hereda(self, repo: Path) -> None:
        _hu(repo)
        assert all(not item.unchanged for item in audit.hu_worklist(repo))

    def test_hu_sellada_hereda(self, repo: Path) -> None:
        readme = _hu(repo)
        _cite(repo, readme, "logsayer.toml")
        _commit(repo, "hu")
        _seal(repo, {"HU-01": "cumple"})
        _commit(repo, "auditoria")
        item = audit.hu_worklist(repo)[0]
        assert item.unchanged
        assert "2026-09-27" in item.reason

    def test_readme_tocado_invalida(self, repo: Path) -> None:
        readme = _hu(repo)
        _commit(repo, "hu")
        _seal(repo, {"HU-01": "cumple"})
        _commit(repo, "auditoria")
        (repo / readme).write_text("cambio\n", encoding="utf-8")
        assert "README modificado" in audit.hu_worklist(repo)[0].reason

    def test_lo_que_cita_tocado_invalida(self, repo: Path) -> None:
        readme = _hu(repo)
        _cite(repo, readme, "logsayer.toml")
        _commit(repo, "hu")
        _seal(repo, {"HU-01": "cumple"})
        _commit(repo, "auditoria")
        (repo / "logsayer.toml").write_text("# todo nuevo\n", encoding="utf-8")
        assert "cambió lo que cita" in audit.hu_worklist(repo)[0].reason

    def test_project_state_no_invalida(self, repo: Path) -> None:
        """D21: se reescribe en cada cierre, contarlo invalidaría para siempre."""
        readme = _hu(repo)
        _cite(repo, readme, "docs/project_state.md")
        _commit(repo, "hu")
        _seal(repo, {"HU-01": "cumple"})
        _commit(repo, "auditoria")
        (repo / "docs/project_state.md").write_text("# nuevo\n", encoding="utf-8")
        assert audit.hu_worklist(repo)[0].unchanged

    def test_una_hu_nunca_auditada_no_hereda(self, repo: Path) -> None:
        _hu(repo, "HU-01")
        _hu(repo, "HU-02")
        _seal(repo, {"HU-01": "cumple"})
        _commit(repo, "auditoria")
        reasons = {item.hu: item.reason for item in audit.hu_worklist(repo)}
        assert "sin veredicto" in reasons["HU-02"]
        assert not audit.hu_worklist(repo)[1].unchanged

    def test_un_andamiaje_no_destruye_la_herencia(self, repo: Path) -> None:
        """`audit run` genera un reporte vacío: si fuera "el previo", una
        corrida sola borraría todo el trabajo de herencia anterior."""
        _hu(repo)
        _seal(repo, {"HU-01": "cumple"})
        _commit(repo, "auditoria sellada")
        audit.run_audit(repo)  # andamiaje vacío, sin veredictos
        _commit(repo, "andamiaje")
        assert audit.hu_worklist(repo)[0].unchanged

    def test_reporte_sin_worklist_no_concede_herencia(self, repo: Path) -> None:
        """Un reporte en prosa no es parseable: no hay herencia, y se dice."""
        _hu(repo)
        old = repo / AU / "audit_2026-09-27.md"
        old.parent.mkdir(parents=True, exist_ok=True)
        old.write_text("# Auditoría\n\n### HU-01 — cumple\n", encoding="utf-8")
        _commit(repo, "auditoria en prosa")
        item = audit.hu_worklist(repo)[0]
        assert not item.unchanged
        assert "worklist" in item.reason


class TestCobertura:
    def test_falta_de_veredicto_es_hueco(self, repo: Path) -> None:
        _hu(repo, "HU-01")
        _hu(repo, "HU-02")
        _seal(repo, {"HU-01": "cumple"})
        assert audit.pending_verdicts(repo) == ["HU-02"]

    def test_fila_vacia_no_cuenta(self, repo: Path) -> None:
        _hu(repo)
        _seal(repo, {"HU-01": "cumple"})
        report = repo / AU / "audit_2026-09-29.md"
        report.write_text(
            "| HU | Veredicto | Evidencia |\n| --- | --- | --- |\n"
            "| HU-01 | — | — |\n",
            encoding="utf-8",
        )
        assert audit.pending_verdicts(repo) == ["HU-01"]

    def test_sin_auditoria_no_hay_hueco(self, repo: Path) -> None:
        _hu(repo)
        assert audit.pending_verdicts(repo) == []

    def test_reporte_sin_worklist_no_se_mide(self, repo: Path) -> None:
        _hu(repo)
        old = repo / AU / "audit_2026-09-27.md"
        old.parent.mkdir(parents=True, exist_ok=True)
        old.write_text("# Auditoría\n\n### HU-01 — cumple\n", encoding="utf-8")
        assert audit.pending_verdicts(repo) == []

    def test_el_placeholder_empuja_el_veredicto(self, repo: Path) -> None:
        _hu(repo)
        _seal(repo, {"HU-01": "cumple"})
        report = repo / AU / "audit_2026-09-29.md"
        report.write_text(
            "| HU | Veredicto | Evidencia |\n| --- | --- | --- |\n"
            "| HU-01 | sin cambios | — |\n",
            encoding="utf-8",
        )
        assert audit.pending_verdicts(repo) == []


class TestCheckCobertura:
    def test_sin_auditoria_es_ok(self, repo: Path) -> None:
        _hu(repo)
        assert check_audit_coverage(repo).status == "ok"

    def test_reporte_viejo_no_se_mide(self, repo: Path) -> None:
        _hu(repo)
        old = repo / AU / "audit_2026-09-27.md"
        old.parent.mkdir(parents=True, exist_ok=True)
        old.write_text("# Auditoría\n\n### HU-01 — cumple\n", encoding="utf-8")
        result = check_audit_coverage(repo)
        assert result.status == "ok"
        assert "worklist" in result.detail

    def test_hueco_es_warn_nunca_fail(self, repo: Path) -> None:
        _hu(repo, "HU-01")
        _hu(repo, "HU-02")
        _seal(repo, {"HU-01": "cumple"})
        result = check_audit_coverage(repo)
        assert result.status == "warn"
        assert "HU-02" in result.detail

    def test_reporte_a_medio_llenar_no_rompe_el_check(self, repo: Path) -> None:
        """Es `warn` a propósito (D7): bloquear el check haría odiarlo."""
        _hu(repo, "HU-01")
        _hu(repo, "HU-02")
        audit.run_audit(repo)
        assert check_audit_coverage(repo).status == "warn"


class TestPasadaAislada:
    def test_no_escribe_reporte(self, repo: Path) -> None:
        """Un reporte con una fila se volvería "el previo" y dejaría al resto
        del alcance sin cubrir: el fallo que D14 existe para cerrar."""
        _hu(repo, "HU-01")
        _hu(repo, "HU-02")
        before = _reports(repo)
        audit.run_audit(repo, only="HU-01")
        after = _reports(repo)
        assert before == after

    def test_el_prompt_trae_una_sola_hu(self, repo: Path) -> None:
        _hu(repo, "HU-01")
        _hu(repo, "HU-02")
        prompt = audit.run_audit(repo, only="HU-01")
        text = prompt.read_text(encoding="utf-8")
        assert prompt.name.endswith(".prompt.md")
        assert "### HU-01" in text
        assert "### HU-02" not in text

    def test_hu_fuera_de_alcance_falla(self, repo: Path) -> None:
        _hu(repo, "HU-01")
        with pytest.raises(audit.AuditError):
            audit.run_audit(repo, only="HU-99")
