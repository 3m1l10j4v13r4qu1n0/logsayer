# HU-05 — Documentación y publicación (README, MIT, PyPI, ejemplos)

> Fase 5 del roadmap (documentación y publicación). Cerrada: merge `d23425f` en develop, tag `v0.5.0`.

## Qué hay que construir

- `README.md` público en inglés con el one-liner de posicionamiento, las 5 capas, comandos con alias plano y el **disclaimer Dune obligatorio** (spec §12).
- `LICENSE` MIT (autor: Emilio Javier Aquino).
- `pyproject.toml` listo para PyPI: `readme`, `authors`, `keywords`, clasificadores, URLs del repo — empaquetado con hatchling.
- Caso de ejemplo real en `examples/hello-logsayer/` con la sesión documentada (salidas reales del CLI).

## Cómo se valida

- `python -m build` produce el wheel y el sdist; el `METADATA` del wheel incluye descripción larga (README), licencia y URLs.
- Instalación en venv limpio → `logsayer init` + `logsayer check` OK.
- `pytest` (89 casos), `ruff check` y `mypy --strict` pasan.

## Log

- `2026-09-24` — merge de fase 5 en `develop` (`d23425f`). Bump a `v0.5.0`.
- Pendiente: publicar en PyPI (requiere token de `3m1l10j4v13r4qu1n0`), vía `uv publish`/`twine`.