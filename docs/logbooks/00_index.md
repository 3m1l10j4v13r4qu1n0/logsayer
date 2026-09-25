# Bitácoras — índice

| Archivo | Fase | Rango | Decisiones clave |
|---|---|---|---|
| logbook_dogfooding_01.md | dogfooding | 1 | 2026-09-24 17:03 — Bootstrap dogfooding: init --here en modo adopt sobre el repo; HUs HU-01..05 reconstruidas desde el historial real. |
| logbook_fase1_01.md | fase1 | 1 | 2026-09-24 — Se define el schema de umbrales de `logsayer.toml` (0.70 / 400 / 3) y se inicializa el empaquetado con hatchling (Python 3.11, Typer, Jinja2). |
| logbook_fase2_01.md | fase2 | 1 | 2026-09-24 — Comandos core: `spec new` con template mínimo de HU (anti "sea of markdown") y motor único en `core/`. |
| logbook_fase3_01.md | fase3 | 1 | 2026-09-24 — Motor único + adaptadores finos (spec §6): `agent add` genera subagentes por rol (mentat, navigator, reverend-mother, truthsayer) que solo invocan al CLI, sin duplicar lógica. |
| logbook_fase4_01.md | fase4 | 1 | 2026-09-24 — Suk Doctor: verificación mecánica determinística (bot) con detección de capas mezcladas y exit code 1 ante fallas. |
| logbook_fase5_01.md | fase5 | 1 | 2026-09-24 — README público con disclaimer Dune obligatorio (spec §12) y `LICENSE` MIT. |
| logbook_fase6_01.md | fase6 | 1 | 2026-09-25 — **Fase 6: ingreso de documentos.** El feedback `feelback_usabilidad_2026-09-25.md` (un `.md` en la raíz es invisible para `logsayer check`) se toma como input de diseño, no como bug de fricción: se decide no escanear la raíz, y en su lugar agregar `inbox/` como punto de entrada declarado (D6). |
