# HU-04 — Validación mecánica (Suk Doctor) y de proceso (Fremen)

> Fase 4 del roadmap (validación). Cerrada: merge `c5fdf66` en develop, tag `v0.4.0`.

## Qué hay que construir

- `logsayer suk doctor` (alias `logsayer check`) — chequeo mecánico determinístico (bot, spec §2): marca de raíz, estructura completa de capas, estado de Capa 2 presente, índice de bitácora, ubicación de las HUs, y **detección de capas mezcladas** (un documento en la capa equivocada). Exit code 1 si algo falla.
- `logsayer fremen verify` (alias `logsayer process check`) — chequeo de proceso: estado documentado, proceso desplegado, acuerdo de coordinación y Definition of Ready.

Ambos comparten el mismo motor de chequeos (`core/checks.py`) y renderización (`_render_checks` en `cli.py`).

## Cómo se valida

- `pytest` cubre `checks` (`test_checks`), `suk` y `fremen` (`test_cli_commands`): sano con estructura correcta, falla con capas mezcladas o ausentes, exit code 1.
- `ruff check` y `mypy --strict` pasan.

## Log

- `2026-09-24` — merge de fase 4 en `develop` (`c5fdf66`). Bump a `v0.4.0`.