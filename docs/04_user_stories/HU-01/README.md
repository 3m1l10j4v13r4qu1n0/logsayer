# HU-01 — `logsayer init` y scaffold de la estructura de capas

> Fase 1 del roadmap (MVP). Cerrada: merge `78ad74c` en develop, tag `v0.1.0`.

## Qué hay que construir

El comando `logsayer init <project-name>` (y `init --here`) que scaffoldee, sobre un destino vacío:

- `docs/` con las 7 carpetas de capas (`01_global`, `02_technical`, `03_process`, `04_user_stories`, `05_agile_methodology`, `06_audits`, `logbooks`), cada una con `.gitkeep`.
- `docs/project_state.md` (Capa 2), `docs/logbooks/00_index.md` (Capa 3, índice vacío).
- `AGENTS.md` coordinador con los umbrales renderizados del `logsayer.toml`.
- `logsayer.toml` con los 3 umbrales definidos (spec §4): `session_close_context_threshold = 0.70`, `bitacora_max_lines = 400`, `audit_threshold_hus = 3`.

Validación de entrada: nombre requerido salvo `--here`; slug válido (`[A-Za-z0-9._-]+`); destino no vacío rechazado.

## Cómo se valida

- `pytest` cubre config (`test_config`), scaffold (`test_scaffold`) y CLI (`test_cli`): estructura completa, umbrales renderizados, rechazo de slug inválido y de destino ocupado.
- `ruff check` y `mypy --strict` pasan.
- `logsayer check` sobre un proyecto recién scaffoldeado reporta estado sano.

## Log

- `2026-09-24` — merge de fase 1 en `develop` (`78ad74c`). Bump a `v0.1.0`.