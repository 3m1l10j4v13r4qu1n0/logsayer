# HU-03 — Adaptadores multi-agente (opencode y claude)

> Fase 3 del roadmap (adaptadores). Cerrada: merge `196d9eb` en develop, tag `v0.3.0`.

## Qué hay que construir

`logsayer agent add <opencode|claude>` que genere, en la convención nativa de cada herramienta, subagentes por rol (mentat, navigator, reverend-mother, truthsayer) como **wrappers finos**: archivos que invocan al CLI (`logsayer log add "…"`, etc.), sin duplicar lógica del framework (spec §6 y §10 — todo el juicio vive en `logsayer/core/`).

- opencode → `.opencode/agents/<rol>.md`
- claude → `.claude/agents/<rol>.md`

Registro por agente en un registry desacoplado (`adapters/registry.py`) para permitir sumar agentes nuevos sin tocar el motor. La convención estándar (`AGENTS.md`) queda como el punto de coordinación universal (spec §6).

## Cómo se valida

- `pytest` cubre los adapters (`test_adapters`): registro por nombre, generación de archivos en la ruta nativa, falla controlada para agentes desconocidos.
- `ruff check` y `mypy --strict` pasan.

## Log

- `2026-09-24` — merge de fase 3 en `develop` (`196d9eb`), poblando primero los entornos propios (opencode y Claude Code), resto por demanda (spec §9).