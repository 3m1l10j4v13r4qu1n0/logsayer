# HU-02 — Comandos core (spec, log, audit) con alias plano

> Fase 2 del roadmap (comandos core). Cerrada: merge `eae09ec` en develop, tag `v0.2.0`.

## Qué hay que construir

- `logsayer spec new <hu>` — crea la carpeta `04_user_stories/HU-XX/` con un template mínimo de HU (spec §10, sin documentos de cientos de líneas).
- `logsayer log add "…"` — append en el logbook activo (`docs/logbooks/logbook_<fase>_NN.md`); si supera `bitacora_max_lines`, particiona en `NN+1`.
- `logsayer log index` — reconstruye `docs/logbooks/00_index.md` desde los archivos reales.
- `logsayer audit run` — genera la estructura del reporte + prompt semántico en `06_audits/` (el juicio lo produce la Decidora; ver riesgo §10).
- `logsayer audit status` — contador de HUs vs umbral y último reporte.
- Registro de los comandos bajo el grupo de rol (`mentat spec new`, `navigator state show`, `reverend-mother log add`, `truthsayer audit run`) Y con alias plano en la raíz (`spec new`, `state show`, `log add`, `audit run`).

## Cómo se valida

- `pytest` cubre specs (`test_specs`), logbook con partición (`test_logbook`), audit (`test_audit`) y los alias por CLI (`test_cli_commands`).
- `ruff check` y `mypy --strict` pasan.

## Log

- `2026-09-24` — merge de fase 2 en `develop` (`eae09ec`). Bump de versión a `0.2.0` (`b193158`).